import re
import logging
import asyncio
# import requests  # Not available in container, using httpx instead
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from src.scrapers.base_scraper import BaseScraper
from config.settings import settings
from src.utils.card_utils import normalize_card_name

logger = logging.getLogger(__name__)

class MeleeScraper(BaseScraper):
    """Melee scraper using the working approach from show_melee_tournaments_july.py"""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.base_url = settings.MELEE_BASE_URL
        self.authenticated = False
        self.auth_cookies = {}

    async def __aenter__(self):
        """Async context manager entry with authentication."""
        await super().__aenter__()
        # Authenticate using requests (sync)
        self._authenticate()
        return self

    def _authenticate(self):
        """Authenticate with Melee using httpx sync client."""
        if not settings.MELEE_EMAIL or not settings.MELEE_PASSWORD:
            logger.error("Melee credentials not set in .env")
            return
            
        logger.info("Authenticating with Melee.gg...")
        
        # Use httpx sync client for auth
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        with httpx.Client(headers=headers, follow_redirects=True) as sync_client:
            try:
                # Get main page
                main_response = sync_client.get(self.base_url)
                
                # Get login page
                login_response = sync_client.get(f"{self.base_url}/Account/SignIn")
                
                soup = BeautifulSoup(login_response.text, 'html.parser')
                token_input = soup.find('input', {'name': '__RequestVerificationToken'})
                if not token_input:
                    logger.error("Could not find CSRF token")
                    return
                    
                csrf_token = token_input.get('value')
                logger.info(f"Found CSRF token: {csrf_token[:20]}...")
                
                # Submit login
                form_data = {
                    'Email': settings.MELEE_EMAIL,
                    'Password': settings.MELEE_PASSWORD,
                    '__RequestVerificationToken': csrf_token
                }
                
                login_submit = sync_client.post(
                    f"{self.base_url}/Account/SignInPassword",
                    data=form_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': f'{self.base_url}/Account/SignIn'
                    }
                )
                
                if login_submit.status_code == 200 and len(sync_client.cookies) > 0:
                    logger.info("✅ Authentication successful")
                    self.authenticated = True
                    # Store cookies for async client
                    for name, value in sync_client.cookies.items():
                        self.auth_cookies[name] = value
                        self.client.cookies.set(name, value)
                else:
                    logger.error("❌ Authentication failed")
                    
            except Exception as e:
                logger.error(f"Authentication error: {e}")

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape tournaments using the working SearchResults endpoint."""
        if not self.authenticated:
            logger.error("Not authenticated")
            return []
            
        logger.info(f"Searching Melee tournaments for {self.format_name}")
        
        # Update headers for AJAX request
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': f'{self.base_url}/Tournament/Search'
        })
        
        # Search payload (proven to work)
        search_payload = {
            "draw": "1",
            "start": "0", 
            "length": "1000",  # Get many tournaments
            "search[value]": "",
            "search[regex]": "false"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/Tournament/SearchResults",
                data=search_payload
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}")
                return []
            
            data = response.json()
            
            if not isinstance(data, list):
                logger.error(f"Unexpected response format: {type(data)}")
                return []
            
            logger.info(f"Found {len(data)} tournaments from API")
            
            # Filter and process tournaments
            tournaments = []
            
            for tournament in data:
                # Check if it's a Magic tournament
                game_desc = tournament.get('gameDescription', '')
                if 'magic' not in game_desc.lower():
                    continue
                
                # Parse date
                start_date_str = tournament.get('startDate', '')
                if not start_date_str:
                    continue
                    
                try:
                    # Remove timezone and parse
                    start_date_str = start_date_str.replace('Z', '').split('T')[0]
                    tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    
                    # Check if within our date range
                    if not (start_date <= tournament_date <= end_date):
                        continue
                        
                except Exception:
                    continue
                
                tournament_id = tournament.get('id')
                if not tournament_id:
                    continue
                
                tournament_info = {
                    "source": "melee",
                    "format": self.format_name,
                    "name": tournament.get('name', 'Unknown Tournament'),
                    "date": start_date_str,
                    "url": f"{self.base_url}/Tournament/{tournament_id}",
                    "tournament_id": str(tournament_id),
                    "organization": tournament.get('organizationName', 'N/A'),
                    "decklists": []
                }
                
                # Get decklists for this tournament
                decklists = await self._get_tournament_decklists(tournament_id)
                tournament_info['decklists'] = decklists
                
                if decklists:  # Only add tournaments with decklists
                    tournaments.append(tournament_info)
                    logger.info(f"Added tournament: {tournament_info['name']} with {len(decklists)} decks")
            
            return tournaments
            
        except Exception as e:
            logger.error(f"Error searching tournaments: {e}")
            return []

    async def _get_tournament_decklists(self, tournament_id: str) -> List[Dict[str, Any]]:
        """Get tournament decklists by scraping the tournament page."""
        # For now, return empty list - this would need to be implemented
        # to scrape the actual tournament standings and decklists
        return []

    def _parse_date(self, date_str: str) -> str:
        """Parse Melee date format."""
        try:
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            return date_str
        except:
            return datetime.now().strftime("%Y-%m-%d")