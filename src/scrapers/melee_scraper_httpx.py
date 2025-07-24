import re
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, quote

from bs4 import BeautifulSoup
import httpx

from src.scrapers.base_scraper import BaseScraper
from config.settings import settings
from src.utils.card_utils import normalize_card_name

logger = logging.getLogger(__name__)

class MeleeScraper(BaseScraper):
    """Async scraper for Melee.gg using httpx authentication."""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.cookies = None

    async def __aenter__(self):
        """Async context manager entry with authentication."""
        await super().__aenter__()
        # Get cookies using httpx
        self.cookies = await self._login_and_get_cookies()
        if not self.cookies:
            logger.error("Failed to authenticate with Melee.gg. Scraper will not run.")
        return self

    async def _login_and_get_cookies(self) -> Optional[Dict[str, str]]:
        """Login to Melee.gg using httpx and return session cookies."""
        if not settings.MELEE_EMAIL or not settings.MELEE_PASSWORD:
            logger.error("Melee email or password not set in .env file.")
            return None

        logger.info("Authenticating with Melee.gg via httpx...")
        
        try:
            # Get main page to establish session
            logger.info("Getting main page...")
            main_resp = await self.client.get(f"{settings.MELEE_BASE_URL}/")
            
            # Get login page to get CSRF token
            logger.info("Getting login page...")
            login_resp = await self.client.get(f"{settings.MELEE_BASE_URL}/Auth/Login")
            login_soup = BeautifulSoup(login_resp.text, 'html.parser')
            
            # Find CSRF token
            csrf_input = login_soup.find('input', {'name': '__RequestVerificationToken'})
            if not csrf_input:
                logger.error("Could not find CSRF token")
                return None
            
            csrf_token = csrf_input.get('value')
            logger.info(f"Found CSRF token: {csrf_token[:20]}...")
            
            # Submit login form
            logger.info("Submitting login form...")
            login_data = {
                '__RequestVerificationToken': csrf_token,
                'Email': settings.MELEE_EMAIL,
                'Password': settings.MELEE_PASSWORD,
                'RememberMe': 'false'
            }
            
            login_post_resp = await self.client.post(
                f"{settings.MELEE_BASE_URL}/Auth/Login",
                data=login_data,
                follow_redirects=True
            )
            
            # Check if login was successful
            if login_post_resp.status_code == 200:
                # Look for user-specific elements
                if 'Log Out' in login_post_resp.text or 'user-avatar' in login_post_resp.text:
                    logger.info(f"Login successful! Got {len(self.client.cookies)} cookies")
                    # Convert cookies to dict
                    return {name: value for name, value in self.client.cookies.items()}
                else:
                    logger.error("Login failed - no user session detected")
                    return None
            else:
                logger.error(f"Login failed with status: {login_post_resp.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"An error occurred during httpx login: {e}")
            return None

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        if not self.cookies:
            logger.error("Cannot scrape without authentication cookies.")
            return []

        search_url = f"{settings.MELEE_BASE_URL}/Tournament/Search"
        params = {
            "format": self.format_name.capitalize(),
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }
        
        query_string = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        search_results_url = f"{search_url}?{query_string}"
        
        content = await self._fetch_url(search_results_url)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        tournament_links = soup.select('a[href^="/Tournament/View/"]')
        
        if not tournament_links:
            logger.info(f"No Melee tournaments found for {self.format_name}")
            return []

        tasks = [self._scrape_tournament_details(urljoin(settings.MELEE_BASE_URL, link['href'])) for link in tournament_links[:10]] # Limite pour le test
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [res for res in results if res and isinstance(res, dict)]

    async def _scrape_tournament_details(self, tournament_url: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Scraping details for: {tournament_url}")
        content = await self._fetch_url(f"{tournament_url}/Standings")
        if not content: return None

        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('h1')
        date_elem = soup.find('span', class_='tournament-date')
        
        tournament_data = {
            "source": "melee", "format": self.format_name,
            "name": title.text.strip() if title else "Unknown Tournament",
            "date": self._parse_date(date_elem.text.strip() if date_elem else ""),
            "url": tournament_url, "decklists": []
        }
        
        standings_table = soup.find('table')
        if standings_table:
            rows = standings_table.find_all('tr')[1:]
            deck_tasks = []
            for row in rows[:32]: # Top 32
                cells = row.find_all('td')
                if len(cells) >= 3:
                    player_name = cells[1].text.strip()
                    decklist_link_tag = cells[1].find('a', href=re.compile(r'/Decklist/View/\d+'))
                    if decklist_link_tag:
                        decklist_url = urljoin(settings.MELEE_BASE_URL, decklist_link_tag['href'])
                        deck_tasks.append(self._scrape_decklist(decklist_url, player_name))
            
            decklist_results = await asyncio.gather(*deck_tasks, return_exceptions=True)
            tournament_data['decklists'] = [d for d in decklist_results if d and isinstance(d, dict)]

        return tournament_data if tournament_data['decklists'] else None

    async def _scrape_decklist(self, decklist_url: str, player_name: str) -> Optional[Dict[str, Any]]:
        content = await self._fetch_url(decklist_url)
        if not content: return None
        
        soup = BeautifulSoup(content, 'html.parser')
        mainboard, sideboard = [], []
        
        deck_container = soup.find('div', class_='decklist-cards')
        if not deck_container: return None

        current_list = mainboard
        for card_line in deck_container.find_all(['h5', 'div']):
            text = card_line.text.strip()
            if 'Sideboard' in text:
                current_list = sideboard
                continue
            
            match = re.match(r'^(\d+)\s+(.+)', text)
            if match:
                quantity = int(match.group(1))
                card_name = normalize_card_name(match.group(2))
                current_list.append({"quantity": quantity, "name": card_name})
        
        if mainboard:
            return {"player": player_name, "mainboard": mainboard, "sideboard": sideboard}
        return None

    def _parse_date(self, date_str: str) -> str:
        try:
            for fmt in ["%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except: pass
        return datetime.now().strftime("%Y-%m-%d")