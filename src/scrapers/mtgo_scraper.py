"""
Fixed MTGO scraper that extracts data from window.MTGO.decklists.data.
"""
import re
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper
from config.settings import settings
from src.utils.card_utils import normalize_card_name

logger = logging.getLogger(__name__)

class MTGOScraper(BaseScraper):
    """Updated async scraper for new MTGO website."""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.base_url = "https://www.mtgo.com"
        self.format_mapping = {
            "standard": "standard",
            "modern": "modern", 
            "legacy": "legacy",
            "vintage": "vintage",
            "pioneer": "pioneer",
            "pauper": "pauper"
        }

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape tournaments from new MTGO site."""
        format_slug = self.format_mapping.get(self.format_name.lower())
        if not format_slug:
            logger.error(f"Format not supported: {self.format_name}")
            return []

        tournaments = []
        
        # Step 1: Get the decklists page
        decklists_url = f"{self.base_url}/decklists"
        logger.info(f"Fetching decklists page: {decklists_url}")
        
        content = await self._fetch_url(decklists_url)
        if not content:
            logger.error("Failed to fetch decklists page")
            return []
        
        # Step 2: Parse to find tournament links
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all decklist links for our format
        all_links = soup.find_all('a', href=re.compile(f'/decklist/{format_slug}'))
        tournament_links = []
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # Extract date from href
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', href)
            if date_match:
                try:
                    link_date = datetime(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3))
                    )
                    if start_date <= link_date <= end_date:
                        full_url = urljoin(self.base_url, href)
                        tournament_links.append((full_url, link_text, link_date.strftime('%Y-%m-%d')))
                except ValueError:
                    pass
        
        logger.info(f"Found {len(tournament_links)} tournament links for date range")
        
        # Step 3: Process each tournament
        for url, title, date_str in tournament_links:
            tournament_data = await self._scrape_tournament_page(url, title, date_str)
            if tournament_data:
                tournaments.append(tournament_data)
        
        logger.info(f"Successfully scraped {len(tournaments)} tournaments for {self.format_name}")
        return tournaments

    async def _scrape_tournament_page(self, url: str, title: str, date_str: str) -> Optional[Dict[str, Any]]:
        """Scrape a single tournament page."""
        logger.debug(f"Scraping tournament: {url}")
        
        content = await self._get_cached_or_fetch(url, cache_hours=48)
        if not content:
            return None
        
        # Extract data from window.MTGO.decklists.data
        decklists = self._extract_mtgo_data(content)
        if not decklists:
            logger.warning(f"No decklists found in {url}")
            return None
        
        tournament_data = {
            "source": "mtgo",
            "format": self.format_name,
            "name": self._clean_tournament_name(title),
            "date": date_str,
            "url": url,
            "decklists": decklists
        }
        
        logger.info(f"Found {len(decklists)} decklists in {title}")
        return tournament_data

    def _extract_mtgo_data(self, content: str) -> List[Dict[str, Any]]:
        """Extract deck data from window.MTGO.decklists.data."""
        decklists = []
        
        # Find window.MTGO.decklists.data assignment
        match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
        if not match:
            logger.debug("Could not find window.MTGO.decklists.data")
            return []
        
        try:
            # Parse the JSON data
            data = json.loads(match.group(1))
            
            # Extract decklists array
            if 'decklists' not in data:
                logger.debug("No 'decklists' key in data")
                return []
            
            for deck_data in data['decklists']:
                parsed_deck = self._parse_mtgo_deck(deck_data)
                if parsed_deck:
                    decklists.append(parsed_deck)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MTGO JSON data: {e}")
        except Exception as e:
            logger.error(f"Error extracting MTGO data: {e}")
        
        return decklists

    def _parse_mtgo_deck(self, deck_data: Dict) -> Optional[Dict[str, Any]]:
        """Parse a single deck from MTGO data format."""
        try:
            player_name = deck_data.get('player', 'Unknown')
            
            # Parse mainboard
            mainboard = []
            for card in deck_data.get('main_deck', []):
                if card.get('sideboard') == 'false':
                    mainboard.append({
                        "quantity": int(card.get('qty', 1)),
                        "name": normalize_card_name(card.get('card_attributes', {}).get('card_name', ''))
                    })
            
            # Parse sideboard
            sideboard = []
            for card in deck_data.get('sideboard_deck', []):
                sideboard.append({
                    "quantity": int(card.get('qty', 1)),
                    "name": normalize_card_name(card.get('card_attributes', {}).get('card_name', ''))
                })
            
            # Get wins/losses
            wins_data = deck_data.get('wins', {})
            wins = wins_data.get('wins') if isinstance(wins_data, dict) else None
            losses = wins_data.get('losses') if isinstance(wins_data, dict) else None
            
            if mainboard:
                return {
                    "player": player_name,
                    "mainboard": mainboard,
                    "sideboard": sideboard,
                    "wins": int(wins) if wins else None,
                    "losses": int(losses) if losses else None
                }
        
        except Exception as e:
            logger.debug(f"Error parsing MTGO deck: {e}")
        
        return None

    def _clean_tournament_name(self, name: str) -> str:
        """Clean tournament name."""
        # Remove dates from the name
        name = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{1,2}\s*\d{4}', '', name)
        name = re.sub(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip() or f"{self.format_name.title()} Tournament"