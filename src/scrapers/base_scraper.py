# src/scrapers/base_scraper.py - VERSION ASYNC

import asyncio
import time
import json
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import httpx
from config.settings import settings
from src.utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for all scrapers with async support."""

    def __init__(self, format_name: str):
        self.format_name = format_name
        self.source_name = self.__class__.__name__.replace("Scraper", "").lower()
        
        # Use async client
        self.client = None
        self._semaphore = None
        
        self.cache = CacheManager()
        self.raw_data_path = settings.DATA_DIR / "raw" / self.source_name / self.format_name
        self.raw_data_path.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        """Async context manager entry."""
        # Configure rate limiting based on source
        rate_limit = settings.MTGO_RATE_LIMIT if self.source_name == 'mtgo' else settings.MELEE_RATE_LIMIT
        self._semaphore = asyncio.Semaphore(rate_limit)
        
        # Create async client with retry
        transport = httpx.AsyncHTTPTransport(retries=3)
        self.client = httpx.AsyncClient(
            transport=transport,
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=rate_limit * 2)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL with rate limiting and error handling."""
        async with self._semaphore:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    logger.warning(f"Client error fetching {url}: {e.response.status_code}")
                else:
                    logger.error(f"Server error fetching {url}: {e}")
                return None
            except httpx.RequestError as e:
                logger.error(f"Network error fetching {url}: {e}")
                return None

    async def _get_cached_or_fetch(self, url: str, cache_hours: int = 24) -> Optional[str]:
        """Get from cache or fetch with async support."""
        cache_key = f"{self.source_name}:{hashlib.md5(url.encode()).hexdigest()}"
        
        # Try cache first (sync operation is fine for Redis)
        cached_content = self.cache.get(cache_key)
        if cached_content:
            return cached_content
        
        # Fetch async
        content = await self._fetch_url(url)
        if content:
            self.cache.set(cache_key, content, ttl=cache_hours * 3600)
        return content

    async def _save_raw_data(self, data: Dict[str, Any], filename_prefix: str):
        """Save data asynchronously using aiofiles."""
        import aiofiles
        filepath = self.raw_data_path / f"{filename_prefix}.json"
        
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    @abstractmethod
    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape tournaments asynchronously."""
        pass

    async def run(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Run scraper asynchronously."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Scraping {self.source_name} for {self.format_name} from {start_date.date()} to {end_date.date()}")
        
        async with self:
            tournaments = await self.scrape_tournaments(start_date, end_date)
        
        # Save all tournaments concurrently
        save_tasks = []
        for tournament in tournaments:
            filename = f"{tournament.get('date', 'nodate')}_{tournament.get('name', 'noname').replace(' ', '_').lower()}"
            save_tasks.append(self._save_raw_data(tournament, filename))
        
        await asyncio.gather(*save_tasks)
        
        logger.info(f"Scraped and saved {len(tournaments)} tournaments from {self.source_name}")
        return tournaments

    @staticmethod
    def run_sync(scraper_class, format_name: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Helper method to run async scraper from sync code."""
        async def _run():
            scraper = scraper_class(format_name)
            return await scraper.run(days_back)
        
        return asyncio.run(_run())


# Example of updated MTGO scraper with async support
class AsyncMTGOScraper(BaseScraper):
    """Async version of MTGO scraper for better performance."""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.base_url = settings.MTGO_BASE_URL
        self.format_urls = {
            "modern": "modern-league", "legacy": "legacy-league",
            "vintage": "vintage-league", "pioneer": "pioneer-league",
            "pauper": "pauper-league", "standard": "standard-league"
        }

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape tournaments concurrently."""
        format_slug = self.format_urls.get(self.format_name.lower())
        if not format_slug:
            logger.error(f"Format not supported by MTGO Scraper: {self.format_name}")
            return []

        # Generate all URLs to fetch
        urls_to_fetch = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            tournament_url = f"{self.base_url}/en/articles/archive/mtgo-standings/{format_slug}-{date_str}"
            urls_to_fetch.append((tournament_url, date_str))
            current_date += timedelta(days=1)

        # Fetch all URLs concurrently
        tasks = []
        for url, date_str in urls_to_fetch:
            task = self._fetch_and_parse_tournament(url, date_str)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        tournaments = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error during scraping: {result}")
            elif result is not None:
                tournaments.append(result)
        
        return tournaments

    async def _fetch_and_parse_tournament(self, url: str, date_str: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse a single tournament page."""
        content = await self._get_cached_or_fetch(url, cache_hours=48)
        
        if not content or "No results found" in content or "page-not-found" in content:
            return None
        
        # Parse in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._parse_tournament_page_sync, 
            content, 
            date_str, 
            url
        )

    def _parse_tournament_page_sync(self, content: str, date_str: str, url: str) -> Optional[Dict[str, Any]]:
        """Synchronous parsing logic (same as before)."""
        from bs4 import BeautifulSoup
        import re
        from src.utils.card_utils import normalize_card_name
        
        soup = BeautifulSoup(content, 'html.parser')
        title_elem = soup.find('h1')
        if not title_elem or "league" not in title_elem.text.lower():
            return None

        tournament_data = {
            "source": self.source_name,
            "format": self.format_name,
            "name": title_elem.text.strip(),
            "date": date_str,
            "url": url,
            "decklists": []
        }

        decklist_sections = soup.find_all('div', class_='deck-list-text')
        for section in decklist_sections:
            player_elem = section.find_previous('h4')
            if not player_elem:
                continue
            
            player_name = re.sub(r'\s*\(\d+-\d+\)\s*', '', player_elem.text).strip()
            
            mainboard, sideboard = self._parse_decklist_section(section)
            
            if mainboard:
                tournament_data["decklists"].append({
                    "player": player_name,
                    "mainboard": mainboard,
                    "sideboard": sideboard
                })
        
        return tournament_data if tournament_data["decklists"] else None

    def _parse_decklist_section(self, section):
        """Parse decklist section (same implementation as before)."""
        from src.utils.card_utils import normalize_card_name
        import re
        
        mainboard, sideboard = [], []
        current_list = mainboard
        
        lines = section.get_text(strip=True, separator='\n').split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower() == 'sideboard':
                current_list = sideboard
                continue
            
            match = re.match(r'^(\d+)\s+(.+)', line)
            if match:
                quantity = int(match.group(1))
                card_name = normalize_card_name(match.group(2).strip())
                current_list.append({"quantity": quantity, "name": card_name})
        
        return mainboard, sideboard