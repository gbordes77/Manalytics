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
    """Abstract base class for all scrapers, using httpx with retries."""

    def __init__(self, format_name: str):
        self.format_name = format_name
        self.source_name = self.__class__.__name__.replace("Scraper", "").lower()
        
        retries = 3
        transport = httpx.HTTPTransport(retries=retries)
        self.client = httpx.Client(transport=transport, timeout=30.0, follow_redirects=True)
        
        self.cache = CacheManager()
        self.raw_data_path = settings.DATA_DIR / "raw" / self.source_name / self.format_name
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.last_request_time = 0

    def _rate_limit(self):
        rate = settings.MTGO_RATE_LIMIT if self.source_name == 'mtgo' else settings.MELEE_RATE_LIMIT
        elapsed = time.time() - self.last_request_time
        wait_time = (1 / rate) - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def _fetch_url(self, url: str) -> Optional[str]:
        self._rate_limit()
        try:
            response = self.client.get(url)
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

    def _get_cached_or_fetch(self, url: str, cache_hours: int = 24) -> Optional[str]:
        cache_key = f"{self.source_name}:{hashlib.md5(url.encode()).hexdigest()}"
        cached_content = self.cache.get(cache_key)
        if cached_content:
            return cached_content
        
        content = self._fetch_url(url)
        if content:
            self.cache.set(cache_key, content, ttl=cache_hours * 3600)
        return content

    def _save_raw_data(self, data: Dict[str, Any], filename_prefix: str):
        filepath = self.raw_data_path / f"{filename_prefix}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @abstractmethod
    def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        pass

    def run(self, days_back: int = 7) -> List[Dict[str, Any]]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Scraping {self.source_name} for {self.format_name} from {start_date.date()} to {end_date.date()}")
        tournaments = self.scrape_tournaments(start_date, end_date)
        
        for tournament in tournaments:
            filename = f"{tournament.get('date', 'nodate')}_{tournament.get('name', 'noname').replace(' ', '_').lower()}"
            self._save_raw_data(tournament, filename)
        
        logger.info(f"Scraped and saved {len(tournaments)} tournaments from {self.source_name}")
        return tournaments