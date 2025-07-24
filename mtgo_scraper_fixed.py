"""
Fixed MTGO scraper that properly extracts JavaScript data.
"""
import re
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from src.scrapers.base_scraper_async import BaseScraper
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
        
        # Find all decklist links
        all_links = soup.find_all('a', href=re.compile('/decklist/'))
        tournament_links = []
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # Check if it's our format and within date range
            if format_slug in href.lower():
                # Extract date from link text or href
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
                            tournament_links.append((full_url, link_text))
                    except ValueError:
                        pass
        
        logger.info(f"Found {len(tournament_links)} tournament links for date range")
        
        # Step 3: Process each tournament
        for url, title in tournament_links:
            tournament_data = await self._scrape_tournament_page(url, title)
            if tournament_data:
                tournaments.append(tournament_data)
        
        logger.info(f"Successfully scraped {len(tournaments)} tournaments for {self.format_name}")
        return tournaments

    async def _scrape_tournament_page(self, url: str, title: str) -> Optional[Dict[str, Any]]:
        """Scrape a single tournament page."""
        logger.debug(f"Scraping tournament: {url}")
        
        content = await self._get_cached_or_fetch(url, cache_hours=48)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract date
        date_str = self._extract_date(soup, title, url)
        
        tournament_data = {
            "source": "mtgo",
            "format": self.format_name,
            "name": self._clean_tournament_name(title),
            "date": date_str,
            "url": url,
            "decklists": []
        }
        
        # Find and parse JavaScript data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for the main data object (usually the longest script with player data)
                if '"player"' in script.string and '{' in script.string:
                    decklists = self._extract_decklists_from_script(script.string)
                    if decklists:
                        tournament_data['decklists'] = decklists
                        break
        
        logger.info(f"Found {len(tournament_data['decklists'])} decklists in {title}")
        
        return tournament_data if tournament_data['decklists'] else None

    def _extract_decklists_from_script(self, script_content: str) -> List[Dict[str, Any]]:
        """Extract decklists from JavaScript content."""
        decklists = []
        
        try:
            # Method 1: Try to find JSON array of decks
            # Look for patterns like: [{...player data...}, {...}]
            json_match = re.search(r'\[(\{[^[\]]*"player"[^[\]]*\}(?:,\s*\{[^[\]]*\})*)\]', script_content)
            if json_match:
                json_str = '[' + json_match.group(1) + ']'
                try:
                    data = json.loads(json_str)
                    for deck in data:
                        parsed = self._parse_deck_object(deck)
                        if parsed:
                            decklists.append(parsed)
                    return decklists
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Extract individual deck objects
            # Pattern to find objects with player, mainboard, sideboard
            deck_pattern = r'\{[^{}]*"player"\s*:\s*"([^"]+)"[^{}]*"mainboard"\s*:\s*\[([^\]]+)\][^{}]*"sideboard"\s*:\s*\[([^\]]+)\][^{}]*\}'
            
            for match in re.finditer(deck_pattern, script_content):
                player_name = match.group(1)
                mainboard_str = match.group(2)
                sideboard_str = match.group(3)
                
                mainboard = self._parse_card_array(mainboard_str)
                sideboard = self._parse_card_array(sideboard_str)
                
                if mainboard:
                    decklists.append({
                        "player": player_name,
                        "mainboard": mainboard,
                        "sideboard": sideboard
                    })
            
            # Method 3: Look for structured data with clear separators
            if not decklists:
                # Find all player entries
                player_pattern = r'"player"\s*:\s*"([^"]+)"'
                players = re.findall(player_pattern, script_content)
                
                if players:
                    logger.debug(f"Found {len(players)} players, attempting alternate parsing")
                    # This is a fallback - we found players but couldn't parse full decks
                    # You might need to implement more specific parsing based on actual page structure
        
        except Exception as e:
            logger.error(f"Error extracting decklists from script: {e}")
        
        return decklists

    def _parse_deck_object(self, deck_data: Dict) -> Optional[Dict[str, Any]]:
        """Parse a deck object from JSON data."""
        try:
            player_name = deck_data.get('player', 'Unknown')
            
            mainboard = []
            for card in deck_data.get('mainboard', []):
                if isinstance(card, dict):
                    mainboard.append({
                        "quantity": card.get('quantity', 1),
                        "name": normalize_card_name(card.get('name', ''))
                    })
            
            sideboard = []
            for card in deck_data.get('sideboard', []):
                if isinstance(card, dict):
                    sideboard.append({
                        "quantity": card.get('quantity', 1),
                        "name": normalize_card_name(card.get('name', ''))
                    })
            
            if mainboard:
                return {
                    "player": player_name,
                    "mainboard": mainboard,
                    "sideboard": sideboard,
                    "wins": deck_data.get('wins'),
                    "losses": deck_data.get('losses')
                }
        except Exception as e:
            logger.debug(f"Error parsing deck object: {e}")
        
        return None

    def _parse_card_array(self, cards_str: str) -> List[Dict[str, Any]]:
        """Parse a string representation of a card array."""
        cards = []
        
        try:
            # Pattern for card objects: {"quantity": X, "name": "Card Name"}
            card_pattern = r'\{\s*"quantity"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"\s*\}'
            
            for match in re.finditer(card_pattern, cards_str):
                quantity = int(match.group(1))
                name = normalize_card_name(match.group(2))
                cards.append({"quantity": quantity, "name": name})
        
        except Exception as e:
            logger.debug(f"Error parsing card array: {e}")
        
        return cards

    def _extract_date(self, soup, title: str, url: str) -> str:
        """Extract date from various sources."""
        # Method 1: From URL
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', url)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        
        # Method 2: From title
        date_match = re.search(r'(\w+)\s*(\d{1,2})\s*(\d{4})', title)
        if date_match:
            try:
                month_name = date_match.group(1)
                day = date_match.group(2)
                year = date_match.group(3)
                # Convert month name to number
                month = datetime.strptime(month_name, '%B').month
                return f"{year}-{str(month).zfill(2)}-{day.zfill(2)}"
            except:
                pass
        
        # Default: today
        return datetime.now().strftime('%Y-%m-%d')

    def _clean_tournament_name(self, name: str) -> str:
        """Clean tournament name."""
        # Remove dates
        name = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{1,2}\s*\d{4}', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()