#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melee.gg Tournament Scraper - Robust Version
Enhanced version with better error handling, retry logic, and complete decklist parsing
"""

import re
import json
import logging
import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import hashlib
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MeleeSettings:
    """Configuration for Melee scraping"""
    BASE_URL = "https://melee.gg"
    REQUEST_TIMEOUT = 60  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    MAX_TOURNAMENTS_PER_REQUEST = 100  # For pagination
    
    # Format mappings (Melee format names to our standard names)
    FORMAT_MAPPINGS = {
        "standard": ["Standard", "Type 2"],
        "modern": ["Modern"],
        "legacy": ["Legacy"],
        "vintage": ["Vintage", "Type 1"],
        "pioneer": ["Pioneer"],
        "pauper": ["Pauper"],
        "commander": ["Commander", "EDH", "cEDH", "Duel Commander"],
        "limited": ["Limited", "Draft", "Sealed", "Cube"]
    }
    
    # Tournament type patterns
    TOURNAMENT_TYPES = {
        "rcq": ["RCQ", "Regional Championship Qualifier"],
        "championship": ["Championship", "Champs", "RC"],
        "qualifier": ["Qualifier", "PTQ", "MCQ"],
        "challenge": ["Challenge"],
        "league": ["League"],
        "fnm": ["FNM", "Friday Night Magic"],
        "prerelease": ["Prerelease", "Pre-release"],
        "other": []
    }


@dataclass 
class DeckCard:
    """Represents a card in a deck"""
    quantity: int
    name: str


@dataclass
class Decklist:
    """Represents a complete decklist"""
    player: str
    rank: int
    deck_name: str = "Unknown"
    mainboard: List[DeckCard] = field(default_factory=list)
    sideboard: List[DeckCard] = field(default_factory=list)
    commander: Optional[str] = None


@dataclass
class Tournament:
    """Represents a tournament"""
    id: str
    name: str
    date: datetime
    format: str
    tournament_type: str
    organization: str
    url: str
    player_count: int = 0
    decklists: List[Decklist] = field(default_factory=list)


class AuthenticationManager:
    """Handles Melee authentication with session management"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.cookies = {}
        self.last_auth_time = None
        self.session_duration = timedelta(hours=2)  # Assume 2 hour session
        
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        if not self.cookies or not self.last_auth_time:
            return False
        
        # Check if session might have expired
        if datetime.now() - self.last_auth_time > self.session_duration:
            logger.info("Session might have expired, re-authenticating...")
            return False
            
        return True
    
    def authenticate(self, base_url: str) -> bool:
        """Authenticate with Melee.gg"""
        logger.info("Authenticating with Melee.gg...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        with httpx.Client(headers=headers, follow_redirects=True, timeout=30) as client:
            try:
                # Get main page
                client.get(base_url)
                
                # Get login page
                login_response = client.get(f"{base_url}/Account/SignIn")
                
                # Extract CSRF token
                soup = BeautifulSoup(login_response.text, 'html.parser')
                token_input = soup.find('input', {'name': '__RequestVerificationToken'})
                if not token_input:
                    logger.error("Could not find CSRF token")
                    return False
                
                csrf_token = token_input.get('value')
                logger.debug(f"Found CSRF token: {csrf_token[:20]}...")
                
                # Submit login
                form_data = {
                    'Email': self.email,
                    'Password': self.password,
                    '__RequestVerificationToken': csrf_token
                }
                
                login_submit = client.post(
                    f"{base_url}/Account/SignInPassword",
                    data=form_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': f'{base_url}/Account/SignIn'
                    }
                )
                
                # Check if login was successful
                if login_submit.status_code == 200 and len(client.cookies) > 0:
                    # Verify we're actually logged in by checking for auth cookies
                    auth_cookie_found = any('auth' in name.lower() for name in client.cookies.keys())
                    
                    if auth_cookie_found:
                        logger.info("✅ Authentication successful")
                        self.cookies = dict(client.cookies)
                        self.last_auth_time = datetime.now()
                        return True
                    else:
                        logger.warning("Login appeared successful but no auth cookies found")
                        
                logger.error(f"❌ Authentication failed - Status: {login_submit.status_code}")
                return False
                
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return False


class TournamentTypeDetector:
    """Detect tournament types from names"""
    
    @staticmethod
    def detect_type(name: str) -> str:
        """Detect tournament type from name"""
        name_lower = name.lower()
        
        for type_name, patterns in MeleeSettings.TOURNAMENT_TYPES.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    return type_name
        
        return "other"


class FormatDetector:
    """Enhanced format detection for Melee tournaments"""
    
    @staticmethod
    def detect_format(game_desc: str, tournament_name: str = "") -> Optional[str]:
        """Detect format from game description and tournament name"""
        combined = f"{game_desc} {tournament_name}".lower()
        
        # Check each format mapping
        for our_format, melee_formats in MeleeSettings.FORMAT_MAPPINGS.items():
            for melee_format in melee_formats:
                if melee_format.lower() in combined:
                    return our_format
        
        # Special handling for Limited formats
        if any(word in combined for word in ["draft", "sealed", "cube"]):
            return "limited"
            
        return None
    
    @staticmethod
    def matches_filter(tournament_format: str, filter_format: str) -> bool:
        """Check if tournament format matches the filter"""
        if not filter_format or filter_format.lower() == "all":
            return True
        return tournament_format.lower() == filter_format.lower()


class DecklistParser:
    """Parse decklists from Melee tournament pages"""
    
    @staticmethod
    async def parse_tournament_page(client: httpx.AsyncClient, tournament_url: str) -> Tuple[List[Decklist], int]:
        """Parse tournament page for decklists and player count"""
        try:
            response = await client.get(tournament_url)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch tournament page: {response.status_code}")
                return [], 0
            
            soup = BeautifulSoup(response.text, 'html.parser')
            decklists = []
            
            # Find standings/decklists section
            # Try multiple selectors as Melee's HTML can vary
            selectors = [
                "div.tournament-standings",
                "div.standings-container", 
                "table.standings",
                "div.decklist-container",
                "div[id*='standings']"
            ]
            
            standings_section = None
            for selector in selectors:
                standings_section = soup.select_one(selector)
                if standings_section:
                    break
            
            if not standings_section:
                # Try to find any table with player data
                tables = soup.find_all('table')
                for table in tables:
                    headers = [th.text.strip().lower() for th in table.find_all('th')]
                    if any(word in ' '.join(headers) for word in ['player', 'rank', 'standing']):
                        standings_section = table
                        break
            
            if not standings_section:
                logger.debug("No standings section found on tournament page")
                return [], 0
            
            # Extract player count
            player_count = DecklistParser._extract_player_count(soup)
            
            # Parse standings rows
            rows = standings_section.find_all('tr')[1:]  # Skip header
            
            for idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                # Extract player name and rank
                rank = idx + 1
                player_name = None
                deck_link = None
                
                # Look for player name and deck link
                for cell in cells:
                    # Check for player name
                    if not player_name:
                        text = cell.get_text(strip=True)
                        if text and not text.isdigit() and len(text) > 2:
                            player_name = text
                    
                    # Check for deck link
                    link = cell.find('a', href=True)
                    if link and 'deck' in link['href'].lower():
                        deck_link = urljoin(tournament_url, link['href'])
                
                if player_name and deck_link:
                    # Fetch and parse decklist
                    decklist = await DecklistParser._parse_decklist(client, deck_link, player_name, rank)
                    if decklist:
                        decklists.append(decklist)
            
            logger.info(f"Parsed {len(decklists)} decklists from tournament")
            return decklists, player_count
            
        except Exception as e:
            logger.error(f"Error parsing tournament page: {e}")
            return [], 0
    
    @staticmethod
    def _extract_player_count(soup: BeautifulSoup) -> int:
        """Extract player count from tournament page"""
        # Look for player count in various places
        patterns = [
            r'(\d+)\s*players?',
            r'players?:\s*(\d+)',
            r'entries?:\s*(\d+)',
            r'participants?:\s*(\d+)'
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    @staticmethod
    async def _parse_decklist(client: httpx.AsyncClient, deck_url: str, 
                            player_name: str, rank: int) -> Optional[Decklist]:
        """Parse individual decklist page"""
        try:
            response = await client.get(deck_url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            decklist = Decklist(
                player=player_name,
                rank=rank
            )
            
            # Extract deck name if available
            deck_name_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile('deck.*name'))
            if deck_name_elem:
                decklist.deck_name = deck_name_elem.get_text(strip=True)
            
            # Parse mainboard
            mainboard_section = soup.find(['div', 'section'], class_=re.compile('main|deck'))
            if mainboard_section:
                decklist.mainboard = DecklistParser._parse_cards(mainboard_section)
            
            # Parse sideboard
            sideboard_section = soup.find(['div', 'section'], class_=re.compile('side'))
            if sideboard_section:
                decklist.sideboard = DecklistParser._parse_cards(sideboard_section)
            
            # Parse commander if applicable
            commander_section = soup.find(['div', 'section'], class_=re.compile('commander'))
            if commander_section:
                commander_text = commander_section.get_text(strip=True)
                # Extract card name from commander section
                match = re.search(r'(\d+)\s+(.+)', commander_text)
                if match:
                    decklist.commander = match.group(2).strip()
            
            # Validate decklist has cards
            if not decklist.mainboard:
                logger.debug(f"No mainboard cards found for {player_name}")
                return None
            
            return decklist
            
        except Exception as e:
            logger.error(f"Error parsing decklist: {e}")
            return None
    
    @staticmethod
    def _parse_cards(section) -> List[DeckCard]:
        """Parse cards from a deck section"""
        cards = []
        
        # Look for card entries
        card_entries = section.find_all(['div', 'li', 'p'], class_=re.compile('card|entry'))
        
        if not card_entries:
            # Try parsing raw text
            text = section.get_text()
            lines = text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse "quantity card name" format
                match = re.match(r'^(\d+)\s+(.+)$', line)
                if match:
                    quantity = int(match.group(1))
                    name = match.group(2).strip()
                    cards.append(DeckCard(quantity=quantity, name=name))
        else:
            # Parse structured entries
            for entry in card_entries:
                text = entry.get_text(strip=True)
                match = re.match(r'^(\d+)\s+(.+)$', text)
                if match:
                    quantity = int(match.group(1))
                    name = match.group(2).strip()
                    cards.append(DeckCard(quantity=quantity, name=name))
        
        return cards


class TournamentTracker:
    """Track processed tournaments to avoid duplicates"""
    
    def __init__(self, tracker_file: str = "data/raw/melee/.processed_tournaments.json"):
        self.tracker_file = Path(tracker_file)
        self.processed: Set[str] = set()
        self.load()
    
    def load(self):
        """Load processed tournament IDs"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    self.processed = set(data.get('processed', []))
                logger.info(f"Loaded {len(self.processed)} processed tournaments")
            except Exception as e:
                logger.error(f"Error loading tracker file: {e}")
    
    def save(self):
        """Save processed tournament IDs"""
        try:
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_file, 'w') as f:
                json.dump({'processed': list(self.processed)}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracker file: {e}")
    
    def is_processed(self, tournament_id: str) -> bool:
        """Check if tournament was already processed"""
        return tournament_id in self.processed
    
    def mark_processed(self, tournament_id: str):
        """Mark tournament as processed"""
        self.processed.add(tournament_id)
        self.save()


class MeleeScraperRobust:
    """Robust Melee.gg scraper with retry logic and complete functionality"""
    
    def __init__(self, email: str, password: str):
        self.auth_manager = AuthenticationManager(email, password)
        self.tracker = TournamentTracker()
        self.base_url = MeleeSettings.BASE_URL
        self.client = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        # Authenticate first
        if not self.auth_manager.authenticate(self.base_url):
            raise Exception("Failed to authenticate with Melee.gg")
        
        # Create async client with auth cookies
        self.client = httpx.AsyncClient(
            cookies=self.auth_manager.cookies,
            timeout=MeleeSettings.REQUEST_TIMEOUT,
            follow_redirects=True
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def scrape_tournaments(self, format_filter: str = None, 
                               start_date: datetime = None,
                               end_date: datetime = None,
                               skip_processed: bool = True,
                               limit: int = None) -> List[Tournament]:
        """Scrape tournaments with enhanced filtering and error handling"""
        
        if not self.auth_manager.is_authenticated():
            logger.info("Re-authenticating...")
            if not self.auth_manager.authenticate(self.base_url):
                logger.error("Re-authentication failed")
                return []
        
        # Update client cookies
        self.client.cookies.update(self.auth_manager.cookies)
        
        # Default date range
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        logger.info(f"Searching Melee tournaments from {start_date.date()} to {end_date.date()}")
        if format_filter:
            logger.info(f"Filtering for format: {format_filter}")
        
        tournaments = []
        offset = 0
        total_found = 0
        
        while True:
            # Search tournaments with pagination
            batch = await self._search_tournaments_batch(offset)
            
            if not batch:
                break
            
            total_found += len(batch)
            
            # Process each tournament
            for tournament_data in batch:
                try:
                    tournament = await self._process_tournament(
                        tournament_data, 
                        format_filter,
                        start_date,
                        end_date,
                        skip_processed
                    )
                    
                    if tournament:
                        tournaments.append(tournament)
                        
                        # Check limit
                        if limit and len(tournaments) >= limit:
                            logger.info(f"Reached limit of {limit} tournaments")
                            return tournaments
                        
                except Exception as e:
                    logger.error(f"Error processing tournament: {e}")
                    continue
            
            # Check if we should continue pagination
            if len(batch) < MeleeSettings.MAX_TOURNAMENTS_PER_REQUEST:
                break
            
            offset += len(batch)
            
            # Brief delay between requests
            await asyncio.sleep(1)
        
        logger.info(f"Found {total_found} tournaments total, scraped {len(tournaments)} with decklists")
        return tournaments
    
    async def _search_tournaments_batch(self, offset: int) -> List[Dict[str, Any]]:
        """Search for tournaments with retry logic"""
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': f'{self.base_url}/Tournament/Search'
        }
        
        search_payload = {
            "draw": "1",
            "start": str(offset),
            "length": str(MeleeSettings.MAX_TOURNAMENTS_PER_REQUEST),
            "search[value]": "",
            "search[regex]": "false"
        }
        
        for attempt in range(MeleeSettings.MAX_RETRIES):
            try:
                response = await self.client.post(
                    f"{self.base_url}/Tournament/SearchResults",
                    data=search_payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        return data
                    else:
                        logger.error(f"Unexpected response format: {type(data)}")
                        return []
                else:
                    logger.warning(f"Search failed with status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Search request error (attempt {attempt + 1}): {e}")
            
            if attempt < MeleeSettings.MAX_RETRIES - 1:
                await asyncio.sleep(MeleeSettings.RETRY_DELAY)
        
        return []
    
    async def _process_tournament(self, tournament_data: Dict[str, Any],
                                format_filter: str,
                                start_date: datetime,
                                end_date: datetime,
                                skip_processed: bool) -> Optional[Tournament]:
        """Process a single tournament"""
        
        # Check if it's a Magic tournament
        game_desc = tournament_data.get('gameDescription', '')
        if 'magic' not in game_desc.lower():
            return None
        
        # Extract tournament info
        tournament_id = str(tournament_data.get('id', ''))
        if not tournament_id:
            return None
        
        # Skip if already processed
        if skip_processed and self.tracker.is_processed(tournament_id):
            logger.debug(f"Skipping already processed tournament: {tournament_id}")
            return None
        
        # Parse date
        start_date_str = tournament_data.get('startDate', '')
        if not start_date_str:
            return None
        
        try:
            # Parse date
            if 'T' in start_date_str:
                start_date_str = start_date_str.replace('Z', '').split('T')[0]
            tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            tournament_date = tournament_date.replace(tzinfo=timezone.utc)
            
            # Check date range
            if not (start_date <= tournament_date <= end_date):
                return None
                
        except Exception as e:
            logger.debug(f"Error parsing date: {e}")
            return None
        
        # Detect format
        tournament_name = tournament_data.get('name', 'Unknown')
        detected_format = FormatDetector.detect_format(game_desc, tournament_name)
        
        if not detected_format:
            logger.debug(f"Could not detect format for: {tournament_name}")
            return None
        
        # Check format filter
        if format_filter and not FormatDetector.matches_filter(detected_format, format_filter):
            return None
        
        # Detect tournament type
        tournament_type = TournamentTypeDetector.detect_type(tournament_name)
        
        # Create tournament object
        tournament = Tournament(
            id=tournament_id,
            name=tournament_name,
            date=tournament_date,
            format=detected_format,
            tournament_type=tournament_type,
            organization=tournament_data.get('organizationName', 'Unknown'),
            url=f"{self.base_url}/Tournament/{tournament_id}"
        )
        
        # Get decklists
        logger.info(f"Processing: {tournament_name} ({detected_format}/{tournament_type})")
        
        decklists, player_count = await DecklistParser.parse_tournament_page(
            self.client, 
            tournament.url
        )
        
        tournament.decklists = decklists
        tournament.player_count = player_count
        
        # Only return tournaments with decklists
        if decklists:
            # Mark as processed
            self.tracker.mark_processed(tournament_id)
            logger.info(f"✅ Scraped {len(decklists)} decks from {tournament_name}")
            return tournament
        else:
            logger.debug(f"No decklists found for {tournament_name}")
            return None


async def main():
    """Test the scraper"""
    # Load credentials
    from pathlib import Path
    import json
    
    creds_file = Path("api_credentials/melee_login.json")
    if not creds_file.exists():
        logger.error("Credentials file not found")
        return
    
    with open(creds_file) as f:
        creds_raw = json.load(f)
        # Handle different credential formats
        creds = {
            'email': creds_raw.get('email', creds_raw.get('login')),
            'password': creds_raw.get('password', creds_raw.get('mdp'))
        }
    
    # Test scraping
    async with MeleeScraperRobust(creds['email'], creds['password']) as scraper:
        tournaments = await scraper.scrape_tournaments(
            format_filter="standard",
            start_date=datetime.now() - timedelta(days=7),
            limit=5
        )
        
        logger.info(f"Found {len(tournaments)} tournaments")
        
        for t in tournaments:
            logger.info(f"{t.date.date()} - {t.name} ({t.format}/{t.tournament_type}) - {len(t.decklists)} decks")


if __name__ == "__main__":
    asyncio.run(main())