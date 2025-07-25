#!/usr/bin/env python3
"""
Enhanced Melee Scraper - Final version with decklist extraction
Based on working scraper but adds decklist fetching capability
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MeleeScraperEnhanced:
    """Enhanced Melee scraper that fetches tournament data AND decklists"""
    
    def __init__(self):
        self.base_url = "https://melee.gg"
        self.session = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/128.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            timeout=30.0,
            follow_redirects=True
        )
        self.authenticated = False
        self.csrf_token = None
        self.cookie_file = Path("api_credentials/melee_cookies.json")
        self.cred_file = Path("api_credentials/melee_login.json")
    
    def ensure_authenticated(self) -> bool:
        """Ensure we are authenticated, using cookies if valid"""
        
        # Check if we have valid cookies
        if self._cookies_valid():
            self._load_cookies()
            self.authenticated = True
            logger.info("✅ Using valid cookies")
            return True
        
        # Otherwise authenticate
        return self._authenticate()
    
    def _cookies_valid(self) -> bool:
        """Check if stored cookies are still valid"""
        if not self.cookie_file.exists():
            return False
        
        try:
            with open(self.cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Check timestamp (21 days validity)
            timestamp = cookie_data.get('_timestamp', 0)
            age_days = (time.time() - timestamp) / 86400
            
            return age_days < 21
        except:
            return False
    
    def _load_cookies(self):
        """Load cookies from file"""
        with open(self.cookie_file, 'r') as f:
            cookie_data = json.load(f)
        
        for name, value in cookie_data['cookies'].items():
            self.session.cookies.set(name, value)
        
        self.csrf_token = cookie_data['cookies'].get('__RequestVerificationToken')
    
    def _save_cookies(self):
        """Save cookies to file"""
        cookie_data = {
            'cookies': {},
            '_timestamp': time.time()
        }
        
        for name, value in self.session.cookies.items():
            cookie_data['cookies'][name] = value
        
        self.cookie_file.parent.mkdir(exist_ok=True)
        with open(self.cookie_file, 'w') as f:
            json.dump(cookie_data, f, indent=2)
    
    def _authenticate(self) -> bool:
        """Authenticate with Melee"""
        if not self.cred_file.exists():
            logger.error("Credentials file not found")
            return False
        
        with open(self.cred_file) as f:
            creds = json.load(f)
        
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
            
            # Submit login
            login_data = {
                'Email': creds['login'],
                'Password': creds['mdp'],
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
                self._save_cookies()
                return True
            else:
                logger.error(f"❌ Authentication failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def search_tournaments(self, start_date: datetime, end_date: datetime, format_filter: str = "Standard") -> List[Dict]:
        """Search tournaments and enrich with decklist data"""
        
        if not self.ensure_authenticated():
            logger.error("Not authenticated")
            return []
        
        logger.info(f"🔍 Searching {format_filter} tournaments from {start_date.date()} to {end_date.date()}")
        
        # Use the working Decklist search endpoint
        search_url = f"{self.base_url}/Decklist/DecklistSearch"
        
        all_results = []
        draw = 1
        start = 0
        has_more = True
        
        while has_more and start < 500:  # Limit to prevent infinite loop
            payload = self._build_decklist_search_payload(start_date, end_date, draw, start)
            
            # Add format filter
            if format_filter:
                payload["columns[3][search][value]"] = format_filter
            
            # Add CSRF token
            payload["__RequestVerificationToken"] = self.csrf_token
            
            try:
                response = self.session.post(
                    search_url,
                    data=payload,
                    headers={
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Referer': f'{self.base_url}/Decklist/Search'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Search failed: {response.status_code}")
                    break
                
                data = response.json()
                
                # DataTables format
                if 'data' in data:
                    results = data['data']
                    all_results.extend(results)
                    
                    # Check if there are more results
                    total = data.get('recordsTotal', 0)
                    has_more = (start + len(results)) < total
                    
                    logger.info(f"📊 Fetched {len(results)} results (total so far: {len(all_results)})")
                else:
                    logger.warning("No 'data' field in response")
                    break
                
                draw += 1
                start += 50
                
                # Rate limit
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error searching: {e}")
                break
        
        # Group by tournament
        tournaments = self._group_by_tournament(all_results)
        
        # Enrich with decklists (limit for now)
        enriched_tournaments = []
        
        for tournament in tournaments[:5]:  # Limit to 5 tournaments for testing
            logger.info(f"🏆 Enriching tournament: {tournament['name']}")
            enriched = self._enrich_tournament_with_decklists(tournament)
            enriched_tournaments.append(enriched)
        
        return enriched_tournaments
    
    def _build_decklist_search_payload(self, start_date: datetime, end_date: datetime, draw: int, start: int) -> Dict:
        """Build the working payload for decklist search"""
        date_filter = f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}"
        
        return {
            "draw": str(draw),
            "columns[0][data]": "DecklistName",
            "columns[0][name]": "DecklistName",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "Game",
            "columns[1][name]": "Game",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "MagicTheGathering",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "FormatId",
            "columns[2][name]": "FormatId",
            "columns[2][searchable]": "true",
            "columns[2][orderable]": "false",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "FormatName",
            "columns[3][name]": "FormatName",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "OwnerDisplayName",
            "columns[4][name]": "OwnerDisplayName",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "columns[5][data]": "TournamentName",
            "columns[5][name]": "TournamentName",
            "columns[5][searchable]": "true",
            "columns[5][orderable]": "true",
            "columns[5][search][value]": "",
            "columns[5][search][regex]": "false",
            "columns[6][data]": "SortDate",
            "columns[6][name]": "SortDate",
            "columns[6][searchable]": "true",
            "columns[6][orderable]": "true",
            "columns[6][search][value]": date_filter,
            "columns[6][search][regex]": "false",
            "columns[7][data]": "TeamRank",
            "columns[7][name]": "TeamRank",
            "columns[7][searchable]": "false",
            "columns[7][orderable]": "true",
            "columns[7][search][value]": "",
            "columns[7][search][regex]": "false",
            "columns[8][data]": "TeamMatchWins",
            "columns[8][name]": "TeamMatchWins",
            "columns[8][searchable]": "false",
            "columns[8][orderable]": "false",
            "columns[8][search][value]": "",
            "columns[8][search][regex]": "false",
            "columns[9][data]": "OrganizationName",
            "columns[9][name]": "OrganizationName",
            "columns[9][searchable]": "true",
            "columns[9][orderable]": "true",
            "columns[9][search][value]": "",
            "columns[9][search][regex]": "false",
            "columns[10][data]": "Records",
            "columns[10][name]": "Records",
            "columns[10][searchable]": "true",
            "columns[10][orderable]": "false",
            "columns[10][search][value]": "",
            "columns[10][search][regex]": "false",
            "columns[11][data]": "Archetypes",
            "columns[11][name]": "Archetypes",
            "columns[11][searchable]": "true",
            "columns[11][orderable]": "false",
            "columns[11][search][value]": "",
            "columns[11][search][regex]": "false",
            "columns[12][data]": "TournamentTags",
            "columns[12][name]": "TournamentTags",
            "columns[12][searchable]": "true",
            "columns[12][orderable]": "false",
            "columns[12][search][value]": "",
            "columns[12][search][regex]": "false",
            "columns[13][data]": "LeaderName",
            "columns[13][name]": "LeaderName",
            "columns[13][searchable]": "true",
            "columns[13][orderable]": "false",
            "columns[13][search][value]": "",
            "columns[13][search][regex]": "false",
            "columns[14][data]": "SecondaryName",
            "columns[14][name]": "SecondaryName",
            "columns[14][searchable]": "true",
            "columns[14][orderable]": "false",
            "columns[14][search][value]": "",
            "columns[14][search][regex]": "false",
            "order[0][column]": "6",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": "50",
            "search[value]": "",
            "search[regex]": "false"
        }
    
    def _group_by_tournament(self, results: List[Dict]) -> List[Dict]:
        """Group deck results by tournament"""
        tournaments = {}
        
        for result in results:
            tournament_id = result.get('TournamentId')
            if not tournament_id:
                continue
            
            if tournament_id not in tournaments:
                tournaments[tournament_id] = {
                    'tournament_id': tournament_id,
                    'name': result.get('TournamentName', 'Unknown'),
                    'date': result.get('SortDate', ''),
                    'organization': result.get('OrganizationName', ''),
                    'format': result.get('FormatName', ''),
                    'decks': []
                }
            
            # Add deck info
            deck_info = {
                'deck_id': result.get('DecklistId'),
                'player': result.get('OwnerDisplayName', 'Unknown'),
                'deck_name': result.get('DecklistName', ''),
                'rank': result.get('TeamRank', 999),
                'wins': result.get('TeamMatchWins', 0)
            }
            
            tournaments[tournament_id]['decks'].append(deck_info)
        
        return list(tournaments.values())
    
    def _enrich_tournament_with_decklists(self, tournament: Dict) -> Dict:
        """Enrich tournament with actual decklist data"""
        
        enriched_decks = []
        decks_to_fetch = tournament['decks'][:10]  # Limit to 10 decks
        
        for deck_info in decks_to_fetch:
            deck_id = deck_info.get('deck_id')
            if not deck_id:
                continue
            
            # Fetch deck details
            deck_details = self._get_deck_details(deck_id)
            
            if deck_details:
                # Merge info
                enriched_deck = {
                    **deck_info,
                    'mainboard': deck_details.get('mainboard', []),
                    'sideboard': deck_details.get('sideboard', [])
                }
                enriched_decks.append(enriched_deck)
            else:
                # Keep basic info even if details fail
                enriched_decks.append(deck_info)
            
            # Rate limit
            time.sleep(0.3)
        
        tournament['decklists'] = enriched_decks
        del tournament['decks']  # Remove old field
        
        return tournament
    
    def _get_deck_details(self, deck_id: str) -> Optional[Dict]:
        """Get detailed deck information"""
        try:
            url = f"{self.base_url}/Decklist/View/{deck_id}"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find deck text
            deck_text = soup.select_one("pre#decklist-text, .decklist-text, .deck-list")
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
                        "name": card_name,
                        "quantity": count
                    })
            
            return {
                "mainboard": mainboard,
                "sideboard": sideboard
            }
            
        except Exception as e:
            logger.debug(f"Error getting deck {deck_id}: {e}")
            return None


def test_enhanced_scraper():
    """Test the enhanced scraper"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = MeleeScraperEnhanced()
    
    # Test with 3 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    tournaments = scraper.search_tournaments(start_date, end_date, "Standard")
    
    print(f"\n✅ Found {len(tournaments)} tournaments")
    
    if tournaments:
        # Show first tournament
        first = tournaments[0]
        print(f"\n🏆 {first['name']}")
        print(f"   Date: {first['date']}")
        print(f"   Format: {first['format']}")
        print(f"   Decklists: {len(first.get('decklists', []))}")
        
        # Check if we got actual deck data
        if first.get('decklists'):
            first_deck = first['decklists'][0]
            print(f"\n🃏 First deck:")
            print(f"   Player: {first_deck.get('player', 'Unknown')}")
            print(f"   Deck: {first_deck.get('deck_name', 'Unknown')}")
            
            mainboard = first_deck.get('mainboard', [])
            sideboard = first_deck.get('sideboard', [])
            
            print(f"   Mainboard: {len(mainboard)} unique cards")
            print(f"   Sideboard: {len(sideboard)} unique cards")
            
            if mainboard:
                print("\n   Sample cards:")
                for card in mainboard[:3]:
                    print(f"     - {card['quantity']}x {card['name']}")
        
        # Save output
        output_file = Path("melee_enhanced_test_final.json")
        with open(output_file, 'w') as f:
            json.dump(tournaments[0], f, indent=2)
        
        print(f"\n💾 Saved to {output_file}")

if __name__ == "__main__":
    test_enhanced_scraper()