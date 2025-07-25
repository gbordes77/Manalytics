#!/usr/bin/env python3
"""
Enhanced Melee Scraper v2 - Using documented API endpoints
Includes authentication and full data extraction
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MeleeScraperV2:
    """Enhanced Melee scraper with standings and decklist extraction"""
    
    def __init__(self):
        self.base_url = "https://melee.gg"
        self.session = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/128.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            timeout=30.0,
            follow_redirects=True
        )
        self.authenticated = False
        self.csrf_token = None
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with Melee using cookie-based auth"""
        try:
            # Get login page
            login_page = self.session.get(f"{self.base_url}/Account/SignIn")
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Extract CSRF token
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            if not token_input:
                logger.error("Could not find CSRF token")
                return False
            
            self.csrf_token = token_input.get('value')
            logger.info(f"Found CSRF token: {self.csrf_token[:20]}...")
            
            # Submit login
            login_data = {
                'Email': email,
                'Password': password,
                '__RequestVerificationToken': self.csrf_token
            }
            
            login_response = self.session.post(
                f"{self.base_url}/Account/SignInPassword",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f'{self.base_url}/Account/SignIn',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            
            if login_response.status_code == 200:
                logger.info("✅ Authentication successful")
                self.authenticated = True
                return True
            else:
                logger.error(f"❌ Authentication failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def search_tournaments(self, start_date: datetime, end_date: datetime, format_filter: str = "") -> List[Dict]:
        """Search tournaments using the documented API"""
        
        # Build DataTables payload
        payload = {
            "draw": "1",
            "start": "0",
            "length": "100",  # Get more results
            "order[0][column]": "2",
            "order[0][dir]": "desc",
            "startDate": start_date.strftime("%Y-%m-%d") + "T00:00:00.000Z",
            "endDate": end_date.strftime("%Y-%m-%d") + "T23:59:59.999Z"
        }
        
        # Add column definitions
        columns = ["ID", "Name", "StartDate", "Status", "Format", "OrganizationName", "Decklists"]
        for i, col in enumerate(columns):
            payload[f"columns[{i}][data]"] = col
            payload[f"columns[{i}][name]"] = col
            payload[f"columns[{i}][searchable]"] = "true"
            payload[f"columns[{i}][orderable]"] = "true"
            payload[f"columns[{i}][search][value]"] = ""
            payload[f"columns[{i}][search][regex]"] = "false"
        
        # Add format filter if specified
        if format_filter:
            payload["columns[4][search][value]"] = format_filter
        
        try:
            response = self.session.post(
                f"{self.base_url}/Tournament/SearchResults",
                data=payload,
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': f'{self.base_url}/Tournament/Search'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Response type: {type(data)}")
                
                # DataTables response format
                if isinstance(data, dict):
                    if 'data' in data:
                        tournaments = data['data']
                        logger.info(f"Found {len(tournaments)} tournaments in 'data' field")
                        return tournaments
                    else:
                        logger.warning(f"Dict response but no 'data' field: {list(data.keys())}")
                        return []
                elif isinstance(data, list):
                    logger.info(f"Direct list response with {len(data)} tournaments")
                    # Filter for Magic tournaments
                    magic_tournaments = []
                    for t in data:
                        # Check if it's a Magic tournament
                        game = t.get('game', '').lower()
                        format_name = t.get('formatName', '').lower()
                        
                        if 'magic' in game or any(fmt in format_name for fmt in ['standard', 'modern', 'legacy', 'pioneer']):
                            magic_tournaments.append(t)
                    
                    logger.info(f"Filtered to {len(magic_tournaments)} Magic tournaments")
                    return magic_tournaments
                else:
                    logger.warning(f"Unexpected response format: {type(data)}")
                    return []
            else:
                logger.error(f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching tournaments: {e}")
            return []
    
    def get_round_standings(self, round_id: str) -> Dict:
        """Get standings for a specific round"""
        
        payload = {
            "draw": "1",
            "start": "0",
            "length": "1000",  # Get all standings
            "roundId": round_id
        }
        
        # Add column definitions
        columns = ["Rank", "Player", "Decklists", "MatchRecord", "GameRecord", 
                  "Points", "OpponentMatchWinPercentage", "TeamGameWinPercentage", 
                  "OpponentGameWinPercentage"]
        
        for i, col in enumerate(columns):
            payload[f"columns[{i}][data]"] = col
            payload[f"columns[{i}][name]"] = col
            payload[f"columns[{i}][searchable]"] = "false"
            payload[f"columns[{i}][orderable]"] = "true"
        
        try:
            response = self.session.post(
                f"{self.base_url}/Standing/GetRoundStandings",
                data=payload,
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get standings: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            return {}
    
    def get_decklist_details(self, deck_id: str) -> Optional[Dict]:
        """Get detailed decklist information"""
        try:
            # Try API endpoint first
            api_response = self.session.get(
                f"{self.base_url}/Decklist/GetDecklistDetails",
                params={"deckId": deck_id},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            
            if api_response.status_code == 200:
                try:
                    return api_response.json()
                except:
                    pass
            
            # Fallback to HTML parsing
            html_response = self.session.get(f"{self.base_url}/Decklist/View/{deck_id}")
            
            if html_response.status_code != 200:
                return None
            
            soup = BeautifulSoup(html_response.text, 'html.parser')
            
            # Parse deck from HTML
            deck_text = soup.select_one("pre#decklist-text, .decklist-text")
            if not deck_text:
                return None
            
            # Parse cards
            lines = deck_text.text.strip().split('\n')
            mainboard = []
            sideboard = []
            current_section = mainboard
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower() in ["sideboard", "companion"]:
                    current_section = sideboard
                    continue
                
                # Parse "X Card Name"
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    count = int(parts[0])
                    card_name = parts[1]
                    current_section.append({
                        "Count": count,
                        "CardName": card_name
                    })
            
            # Extract metadata
            player_elem = soup.select_one(".player-name, a[href*='/Player/']")
            player_name = player_elem.text.strip() if player_elem else "Unknown"
            
            return {
                "DeckId": deck_id,
                "Player": player_name,
                "Mainboard": mainboard,
                "Sideboard": sideboard
            }
            
        except Exception as e:
            logger.error(f"Error getting decklist {deck_id}: {e}")
            return None
    
    def scrape_tournament_complete(self, tournament_id: str) -> Dict:
        """Scrape complete tournament data including standings and decklists"""
        
        result = {
            "tournament_id": tournament_id,
            "standings": [],
            "decklists": []
        }
        
        try:
            # Get tournament page to find round IDs
            tournament_page = self.session.get(f"{self.base_url}/Tournament/View/{tournament_id}")
            soup = BeautifulSoup(tournament_page.text, 'html.parser')
            
            # Extract tournament name
            title_elem = soup.select_one("h1, .tournament-title")
            result["name"] = title_elem.text.strip() if title_elem else f"Tournament {tournament_id}"
            
            # Find final round standings
            # This would need adjustment based on actual HTML structure
            round_links = soup.select("a[href*='roundId=']")
            
            if round_links:
                # Get last round (final standings)
                last_round_url = round_links[-1].get('href', '')
                if 'roundId=' in last_round_url:
                    round_id = last_round_url.split('roundId=')[-1].split('&')[0]
                    standings_data = self.get_round_standings(round_id)
                    
                    if 'data' in standings_data:
                        result["standings"] = standings_data['data']
            
            # Extract deck IDs from standings or page
            deck_ids = set()
            
            # From standings
            for standing in result["standings"]:
                if "Decklists" in standing and standing["Decklists"]:
                    # Parse deck ID from HTML link
                    if 'href="/Decklist/View/' in str(standing["Decklists"]):
                        deck_id = str(standing["Decklists"]).split('/Decklist/View/')[-1].split('"')[0]
                        deck_ids.add(deck_id)
            
            # From page links
            deck_links = soup.select("a[href*='/Decklist/View/']")
            for link in deck_links:
                deck_id = link['href'].split('/')[-1]
                deck_ids.add(deck_id)
            
            # Fetch decklists (limit for testing)
            logger.info(f"Found {len(deck_ids)} unique decks")
            
            for i, deck_id in enumerate(list(deck_ids)[:20]):  # Limit to 20 for testing
                deck_data = self.get_decklist_details(deck_id)
                if deck_data:
                    result["decklists"].append(deck_data)
                
                # Rate limiting
                if i < len(deck_ids) - 1:
                    asyncio.sleep(0.5)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping tournament {tournament_id}: {e}")
            return result


# Test function
def test_enhanced_scraper():
    """Test the enhanced scraper"""
    
    logging.basicConfig(level=logging.INFO)
    
    # Load credentials
    creds_file = Path("api_credentials/melee_login.json")
    if not creds_file.exists():
        print("❌ Credentials file not found")
        return
    
    with open(creds_file) as f:
        creds = json.load(f)
    
    scraper = MeleeScraperV2()
    
    # Authenticate
    if not scraper.authenticate(creds["login"], creds["mdp"]):
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    
    # Search tournaments
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"\n🔍 Searching tournaments from {start_date.date()} to {end_date.date()}")
    tournaments = scraper.search_tournaments(start_date, end_date, "Standard")
    
    print(f"📊 Found {len(tournaments)} tournaments")
    
    if tournaments:
        # Test with first tournament
        first_tournament = tournaments[0]
        tournament_id = first_tournament.get('ID') or first_tournament.get('id')
        
        print(f"\n🏆 Testing tournament: {first_tournament.get('Name', 'Unknown')}")
        print(f"   ID: {tournament_id}")
        
        # Scrape complete data
        complete_data = scraper.scrape_tournament_complete(tournament_id)
        
        print(f"\n📈 Results:")
        print(f"   Standings: {len(complete_data['standings'])} players")
        print(f"   Decklists: {len(complete_data['decklists'])} decks")
        
        # Save sample
        with open("melee_enhanced_test.json", "w") as f:
            json.dump(complete_data, f, indent=2)
        
        print("\n✅ Test complete! Check melee_enhanced_test.json")

if __name__ == "__main__":
    test_enhanced_scraper()