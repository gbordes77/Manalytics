"""
Melee.gg scraper using API authentication instead of Selenium.
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import quote, urljoin

from src.scrapers.base_scraper_async import BaseScraper
from config.settings import settings
from src.utils.card_utils import normalize_card_name

logger = logging.getLogger(__name__)

class MeleeScraper(BaseScraper):
    """Scraper for Melee.gg using direct API calls."""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.api_base = "https://melee.gg/api/v1"
        self.web_base = "https://melee.gg"
        self.auth_token = None
        self.format_mapping = {
            "standard": 1,
            "modern": 3,
            "legacy": 4,
            "vintage": 5,
            "pioneer": 7,
            "pauper": 8
        }

    async def __aenter__(self):
        """Async context manager entry with authentication."""
        await super().__aenter__()
        await self._authenticate()
        return self

    async def _authenticate(self):
        """Authenticate using email/password to get JWT token."""
        if not settings.MELEE_EMAIL or not settings.MELEE_PASSWORD:
            logger.error("Melee credentials not set in environment")
            return
        
        logger.info("Authenticating with Melee.gg...")
        
        # Login endpoint
        login_url = f"{self.web_base}/api/auth/login"
        
        try:
            response = await self.client.post(
                login_url,
                json={
                    "email": settings.MELEE_EMAIL,
                    "password": settings.MELEE_PASSWORD
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Origin": self.web_base,
                    "Referer": f"{self.web_base}/auth/login"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token') or data.get('access_token')
                
                if self.auth_token:
                    # Update client headers with auth token
                    self.client.headers.update({
                        "Authorization": f"Bearer {self.auth_token}",
                        "X-Auth-Token": self.auth_token
                    })
                    logger.info("Successfully authenticated with Melee.gg")
                else:
                    logger.error("No token in authentication response")
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Error during authentication: {e}")

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Search and scrape Melee tournaments via API."""
        if not self.auth_token:
            logger.error("Not authenticated, skipping Melee scraping")
            return []
        
        format_id = self.format_mapping.get(self.format_name.lower())
        if not format_id:
            logger.error(f"Format not supported by Melee: {self.format_name}")
            return []
        
        logger.info(f"Searching Melee tournaments for {self.format_name}...")
        
        # Search tournaments via API
        search_params = {
            "formatId": format_id,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "page": 1,
            "pageSize": 50,
            "sortBy": "date",
            "sortOrder": "desc"
        }
        
        tournaments = []
        page = 1
        
        while True:
            search_params["page"] = page
            results = await self._search_tournaments(search_params)
            
            if not results:
                break
            
            # Process each tournament
            tasks = []
            for tournament_data in results:
                tournament_id = tournament_data.get('id')
                if tournament_id:
                    tasks.append(self._get_tournament_details(tournament_id))
            
            # Fetch all tournament details in parallel
            tournament_details = await asyncio.gather(*tasks, return_exceptions=True)
            
            for detail in tournament_details:
                if isinstance(detail, Exception):
                    logger.error(f"Error fetching tournament: {detail}")
                elif detail:
                    tournaments.append(detail)
            
            # Check if more pages
            if len(results) < search_params["pageSize"]:
                break
            
            page += 1
            
            # Limit to prevent too many requests
            if page > 5:
                logger.info("Limiting to 5 pages of results")
                break
        
        logger.info(f"Found {len(tournaments)} Melee tournaments")
        return tournaments

    async def _search_tournaments(self, params: Dict) -> List[Dict]:
        """Search tournaments via API."""
        search_url = f"{self.api_base}/tournaments/search"
        
        try:
            response = await self.client.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # Handle paginated response
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    logger.warning(f"Unexpected search response format: {type(data)}")
                    return []
            else:
                logger.error(f"Search failed: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error searching tournaments: {e}")
            return []

    async def _get_tournament_details(self, tournament_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed tournament info including standings and decklists."""
        try:
            # Get tournament info
            info_url = f"{self.api_base}/tournaments/{tournament_id}"
            response = await self.client.get(info_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to get tournament {tournament_id}: {response.status_code}")
                return None
            
            tournament_info = response.json()
            
            # Get standings/decklists
            standings_url = f"{self.api_base}/tournaments/{tournament_id}/standings"
            standings_response = await self.client.get(standings_url)
            
            if standings_response.status_code != 200:
                logger.warning(f"Failed to get standings for {tournament_id}")
                standings = []
            else:
                standings_data = standings_response.json()
                standings = standings_data.get('data', standings_data) if isinstance(standings_data, dict) else standings_data
            
            # Parse tournament data
            tournament_data = {
                "source": "melee",
                "format": self.format_name,
                "name": tournament_info.get('name', 'Unknown Tournament'),
                "date": self._parse_date(tournament_info.get('startDate')),
                "url": f"{self.web_base}/tournament/{tournament_id}",
                "decklists": []
            }
            
            # Process standings to extract decklists
            for standing in standings[:32]:  # Top 32
                player_data = await self._get_player_decklist(tournament_id, standing)
                if player_data:
                    tournament_data['decklists'].append(player_data)
            
            return tournament_data if tournament_data['decklists'] else None
        
        except Exception as e:
            logger.error(f"Error getting tournament details: {e}")
            return None

    async def _get_player_decklist(self, tournament_id: str, standing: Dict) -> Optional[Dict]:
        """Get a player's decklist from standings."""
        try:
            player_id = standing.get('playerId') or standing.get('userId')
            player_name = standing.get('playerName') or standing.get('name') or 'Unknown'
            
            # Try to get decklist
            decklist_url = f"{self.api_base}/tournaments/{tournament_id}/players/{player_id}/decklist"
            
            response = await self.client.get(decklist_url)
            
            if response.status_code != 200:
                # Fallback: try alternate endpoint
                decklist_url = f"{self.api_base}/decklists/tournament/{tournament_id}/player/{player_id}"
                response = await self.client.get(decklist_url)
            
            if response.status_code == 200:
                decklist_data = response.json()
                
                # Parse the decklist
                mainboard = []
                sideboard = []
                
                # Handle different response formats
                if 'mainboard' in decklist_data:
                    # Direct format
                    mainboard = self._parse_card_list(decklist_data.get('mainboard', []))
                    sideboard = self._parse_card_list(decklist_data.get('sideboard', []))
                elif 'decklist' in decklist_data:
                    # Nested format
                    deck = decklist_data['decklist']
                    mainboard = self._parse_card_list(deck.get('mainboard', []))
                    sideboard = self._parse_card_list(deck.get('sideboard', []))
                elif 'cards' in decklist_data:
                    # All cards together
                    cards = decklist_data['cards']
                    for card in cards:
                        parsed = self._parse_card_entry(card)
                        if parsed:
                            if card.get('sideboard', False):
                                sideboard.append(parsed)
                            else:
                                mainboard.append(parsed)
                
                if mainboard:
                    return {
                        "player": player_name,
                        "mainboard": mainboard,
                        "sideboard": sideboard,
                        "wins": standing.get('wins'),
                        "losses": standing.get('losses'),
                        "position": standing.get('rank') or standing.get('position')
                    }
            
            return None
        
        except Exception as e:
            logger.debug(f"Error getting player decklist: {e}")
            return None

    def _parse_card_list(self, cards: List) -> List[Dict]:
        """Parse a list of cards from API response."""
        parsed = []
        
        for card in cards:
            parsed_card = self._parse_card_entry(card)
            if parsed_card:
                parsed.append(parsed_card)
        
        return parsed

    def _parse_card_entry(self, card: Any) -> Optional[Dict]:
        """Parse a single card entry from various formats."""
        try:
            # Handle different card formats
            if isinstance(card, dict):
                quantity = card.get('quantity', 1)
                name = card.get('name') or card.get('cardName')
            elif isinstance(card, str):
                # String format like "4 Lightning Bolt"
                parts = card.split(' ', 1)
                if len(parts) == 2 and parts[0].isdigit():
                    quantity = int(parts[0])
                    name = parts[1]
                else:
                    quantity = 1
                    name = card
            else:
                return None
            
            if name:
                return {
                    "quantity": quantity,
                    "name": normalize_card_name(name)
                }
        
        except Exception as e:
            logger.debug(f"Error parsing card entry: {e}")
        
        return None

    def _parse_date(self, date_str: Any) -> str:
        """Parse date from various formats."""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # ISO format
            if isinstance(date_str, str) and 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            
            # Other string formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(date_str), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        except Exception as e:
            logger.debug(f"Error parsing date: {e}")
        
        return datetime.now().strftime('%Y-%m-%d')