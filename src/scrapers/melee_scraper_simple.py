import re
import logging
import asyncio
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
    """Simple Melee scraper without authentication for public tournaments."""

    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.base_url = settings.MELEE_BASE_URL

    async def scrape_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape tournaments using the public API."""
        logger.info(f"Searching Melee tournaments for {self.format_name} from {start_date} to {end_date}")
        
        # Tournament Search payload (DataTables format)
        search_payload = {
            "draw": "1",
            "columns[0][data]": "ID",
            "columns[1][data]": "Name",
            "columns[2][data]": "StartDate",
            "columns[3][data]": "Status",
            "columns[4][data]": "Format",
            "columns[5][data]": "OrganizationName",
            "columns[6][data]": "Decklists",
            "order[0][column]": "2",
            "order[0][dir]": "desc",
            "start": "0",
            "length": "25",
            "startDate": f"{start_date}T00:00:00.000Z",
            "endDate": f"{end_date}T23:59:59.999Z"
        }
        
        try:
            # POST request to Tournament Search
            response = await self.client.post(
                f"{self.base_url}/Tournament/Search",
                data=search_payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}")
                return []
            
            data = response.json()
            
            # Check if we got the expected response format
            if not isinstance(data, dict) or 'data' not in data:
                logger.error(f"Unexpected response format: {type(data)}")
                return []
            
            tournaments_data = data.get('data', [])
            logger.info(f"Found {len(tournaments_data)} tournaments")
            
            # Filter by format and process tournaments
            tournaments = []
            for tournament in tournaments_data:
                # Check format
                tournament_format = tournament.get('Format', '').lower()
                if self.format_name.lower() not in tournament_format.lower():
                    continue
                
                tournament_id = tournament.get('ID')
                if not tournament_id:
                    continue
                
                tournament_info = {
                    "source": "melee",
                    "format": self.format_name,
                    "name": tournament.get('Name', 'Unknown Tournament'),
                    "date": self._parse_date(tournament.get('StartDate', '')),
                    "url": f"{self.base_url}/Tournament/View/{tournament_id}",
                    "tournament_id": tournament_id,
                    "decklists": []
                }
                
                # Get standings/decklists for this tournament
                decklists = await self._get_tournament_decklists(tournament_id)
                tournament_info['decklists'] = decklists
                
                if decklists:  # Only add tournaments with decklists
                    tournaments.append(tournament_info)
            
            return tournaments
            
        except Exception as e:
            logger.error(f"Error searching tournaments: {e}")
            return []

    async def _get_tournament_decklists(self, tournament_id: str) -> List[Dict[str, Any]]:
        """Get decklists from tournament standings."""
        logger.info(f"Getting decklists for tournament {tournament_id}")
        
        # Round Standings payload
        standings_payload = {
            "draw": "1",
            "columns[0][data]": "Rank",
            "columns[1][data]": "Player",
            "columns[2][data]": "Decklists",
            "columns[3][data]": "MatchRecord",
            "columns[4][data]": "GameRecord",
            "columns[5][data]": "Points",
            "columns[6][data]": "OpponentMatchWinPercentage",
            "columns[7][data]": "TeamGameWinPercentage",
            "columns[8][data]": "OpponentGameWinPercentage",
            "start": "{start}",
            "length": "25",
            "roundId": "{roundId}"
        }
        
        decklists = []
        
        try:
            # First, get the tournament page to find the latest round
            tournament_resp = await self.client.get(f"{self.base_url}/Tournament/View/{tournament_id}")
            if tournament_resp.status_code != 200:
                return []
            
            soup = BeautifulSoup(tournament_resp.text, 'html.parser')
            
            # Find round selector or standings section
            # This is simplified - you may need to parse the actual round structure
            
            # For now, try to get standings from the public API
            standings_resp = await self.client.post(
                f"{self.base_url}/Round/GetRoundStandings",
                data={
                    "tournamentId": tournament_id,
                    "roundNumber": "0"  # 0 often means final standings
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            if standings_resp.status_code == 200:
                standings_data = standings_resp.json()
                
                # Process each player in standings
                for standing in standings_data.get('data', [])[:32]:  # Top 32
                    player_name = standing.get('Player', 'Unknown')
                    decklist_id = standing.get('DecklistId')
                    
                    if decklist_id:
                        # Get the actual decklist
                        decklist = await self._get_decklist_details(decklist_id, player_name)
                        if decklist:
                            decklists.append(decklist)
            
            return decklists
            
        except Exception as e:
            logger.error(f"Error getting tournament decklists: {e}")
            return []

    async def _get_decklist_details(self, decklist_id: str, player_name: str) -> Optional[Dict[str, Any]]:
        """Get decklist details from the public view."""
        try:
            # Get decklist page
            decklist_resp = await self.client.get(f"{self.base_url}/Decklist/View/{decklist_id}")
            if decklist_resp.status_code != 200:
                return None
            
            soup = BeautifulSoup(decklist_resp.text, 'html.parser')
            
            mainboard = []
            sideboard = []
            
            # Parse decklist - this depends on the HTML structure
            decklist_container = soup.find('div', class_='decklist-visual')
            if not decklist_container:
                return None
            
            current_list = mainboard
            for section in decklist_container.find_all('div', class_='deck-section'):
                # Check if this is sideboard
                header = section.find('h4', class_='deck-section-title')
                if header and 'Sideboard' in header.text:
                    current_list = sideboard
                
                # Parse cards
                for card_div in section.find_all('div', class_='card-line'):
                    card_text = card_div.text.strip()
                    match = re.match(r'^(\d+)\s+(.+)$', card_text)
                    if match:
                        quantity = int(match.group(1))
                        card_name = normalize_card_name(match.group(2))
                        current_list.append({"quantity": quantity, "name": card_name})
            
            if mainboard:
                return {
                    "player": player_name,
                    "mainboard": mainboard,
                    "sideboard": sideboard
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting decklist details: {e}")
            return None

    def _parse_date(self, date_str: str) -> str:
        """Parse Melee date format."""
        try:
            # Handle ISO format with timezone
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            return date_str
        except:
            return datetime.now().strftime("%Y-%m-%d")