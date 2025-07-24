#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melee.gg Tournament Scraper - Complete Version
Integrates all functionality from the original scraper with enhanced robustness
"""

import re
import json
import logging
import asyncio
import httpx
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import hashlib
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import time
import os
from dateutil import parser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Configuration ====================

class MtgMeleeConstants:
    """Constants from original scraper"""
    COOKIE_FILE = "melee_cookies.json"
    CRED_FILE = "api_credentials/melee_login.json"
    COOKIE_MAX_AGE_DAYS = 1
    
    TOURNAMENT_LIST_PAGE = "https://melee.gg/Tournament/SearchTournamentResults"
    TOURNAMENT_PAGE = "https://melee.gg/Tournament/View/{tournamentId}"
    ROUND_PAGE = "https://melee.gg/Tournament/GetStandings/{tournamentId}"
    DECK_PAGE = "https://melee.gg/Decklist/View/{deckId}"
    
    # API endpoints
    ROUND_PAGE_PARAMETERS = "draw=1&start={start}&length=25&tournamentId={tournamentId}&roundId={roundId}"
    
    # Minimum thresholds
    Min_number_of_valid_decklists = 8
    VALID_DECKLIST_THRESHOLD = 0.65
    
    @staticmethod
    def format_url(template, **kwargs):
        return template.format(**kwargs)
    
    @staticmethod
    def build_magic_payload(start_date, end_date, length=500, draw=1, start=0):
        """Build search payload for tournaments"""
        return {
            "draw": str(draw),
            "columns[0][data]": "TournamentStartDate",
            "columns[0][searchable]": "false",
            "columns[0][orderable]": "true",
            "order[0][column]": "0",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "showOnlyMyDecklists": "false",
            "gameId": "1",  # Magic: The Gathering
            "dateMin": start_date.strftime("%Y-%m-%d"),
            "dateMax": end_date.strftime("%Y-%m-%d")
        }


class MtgMeleeAnalyzerSettings:
    """Settings from original analyzer"""
    ValidFormats = ["Standard", "Modern", "Pioneer", "Legacy", "Vintage", "Pauper", "Commander", "Premodern"]
    PlayersLoadedForAnalysis = 25
    DecksLoadedForAnalysis = 16
    BlacklistedTerms = ["Team "]


# ==================== Data Classes ====================

@dataclass
class DeckItem:
    """Card in a deck"""
    card_name: str
    count: int


@dataclass
class Standing:
    """Player standing information"""
    player: str
    rank: int
    points: int
    wins: int
    losses: int
    draws: int
    omwp: float  # Opponent Match Win Percentage
    gwp: float   # Game Win Percentage
    ogwp: float  # Opponent Game Win Percentage


@dataclass
class RoundItem:
    """Single match in a round"""
    player1: str
    player2: str
    result: str


@dataclass
class Round:
    """Tournament round"""
    round_name: str
    matches: List[RoundItem]


@dataclass
class MtgMeleeDeckInfo:
    """Complete deck information"""
    date: Optional[datetime]
    deck_uri: str
    player: str
    format: str
    mainboard: List[DeckItem]
    sideboard: List[DeckItem]
    result: Optional[str] = None
    rounds: Optional[List['MtgMeleeRoundInfo']] = None


@dataclass
class MtgMeleeRoundInfo:
    """Round information for a player"""
    round_name: str
    match: RoundItem


@dataclass
class MtgMeleePlayerDeck:
    """Player's deck reference"""
    deck_id: str
    format: str
    uri: str
    tournament_decklists: Optional[Any] = None


@dataclass
class MtgMeleePlayerInfo:
    """Complete player information"""
    username: str
    player_name: str
    result: str
    standing: Standing
    decks: Optional[List[MtgMeleePlayerDeck]] = None
    nb_of_oppo: int = 0


@dataclass
class melee_extract_decklist:
    """Extracted decklist data"""
    date: datetime
    TournamentId: int
    Valid: bool
    OwnerDisplayName: str
    OwnerUsername: str
    Guid: str
    DecklistName: str
    decklists: List[Dict]
    decklists_formats: str


@dataclass
class MtgMeleeTournamentInfo:
    """Tournament information"""
    tournament_id: int
    uri: str
    date: datetime
    organizer: str
    name: str
    decklists: Dict[str, Dict[str, melee_extract_decklist]]
    formats: str
    statut: str


@dataclass
class MtgMeleeTournament:
    """Tournament for processing"""
    uri: str
    date: datetime
    name: str
    formats: str
    json_file: str
    decklists: Dict = field(default_factory=dict)
    deck_offset: int = -1
    expected_decks: int = 1
    fix_behavior: str = "None"
    excluded_rounds: Optional[List[str]] = None


@dataclass
class CacheItem:
    """Cached tournament data"""
    tournament: MtgMeleeTournament
    decks: List[MtgMeleeDeckInfo]
    standings: Optional[List[Standing]] = None
    rounds: Optional[List[Round]] = None


# ==================== Helper Classes ====================

class CardNameNormalizer:
    """Normalize card names"""
    _replacements = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if not cls._initialized:
            cls._replacements = {
                # Add any specific card name normalizations here
            }
            cls._initialized = True
    
    @classmethod
    def normalize(cls, name: str) -> str:
        """Normalize a card name"""
        if not cls._initialized:
            cls.initialize()
        
        # Basic normalization
        name = name.strip()
        
        # Apply replacements
        if name in cls._replacements:
            return cls._replacements[name]
        
        # Handle split cards
        if "//" in name:
            parts = [part.strip() for part in name.split("//")]
            name = " // ".join(parts)
        
        return name


class FilenameGenerator:
    """Generate tournament filenames"""
    
    @staticmethod
    def generate_file_name(tournament_id, tournament_name, tournament_date, 
                          tournament_format, valid_formats, seat=-1):
        """Generate standardized filename"""
        name = tournament_name
        
        # Add format if not in name
        if tournament_format.lower() not in name.lower():
            name += f" ({tournament_format})"
        
        # Shorten other format names
        for other_format in valid_formats:
            if other_format.lower() != tournament_format.lower() and other_format.lower() in name.lower():
                name = name.replace(other_format, other_format[:3], 1)
        
        # Add seat number if multi-seat tournament
        if seat >= 0:
            name += f" (Seat {seat + 1})"
        
        # Create slug
        slug = SlugGenerator.generate_slug(name.strip())
        date_str = tournament_date.strftime('%Y-%m-%d')
        
        return f"{slug}-{tournament_id}-{date_str}.json"


class SlugGenerator:
    """Generate URL-safe slugs"""
    
    @staticmethod
    def generate_slug(text):
        """Convert text to URL-safe slug"""
        # Remove special characters
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces with hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remove leading/trailing hyphens
        return slug.strip('-')


# ==================== Authentication Manager ====================

class MtgMeleeAuthManager:
    """Enhanced authentication with cookie persistence"""
    
    def __init__(self):
        self.session = None
        self.cookies = {}
        self.last_auth_time = None
        
    def get_client(self, load_cookies: bool = True) -> requests.Session:
        """Get authenticated session"""
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            })
        
        if load_cookies:
            cookies_valid = self._cookies_valid()
            if cookies_valid:
                self._load_cookies()
            else:
                self._refresh_cookies()
        
        return self.session
    
    def _cookies_valid(self) -> bool:
        """Check if saved cookies are still valid"""
        if not os.path.exists(MtgMeleeConstants.COOKIE_FILE):
            return False
        
        try:
            with open(MtgMeleeConstants.COOKIE_FILE, "r") as f:
                data = json.load(f)
                timestamp = data.get("_timestamp")
                if not timestamp:
                    return False
                age = datetime.now() - datetime.fromtimestamp(timestamp)
                return age < timedelta(days=MtgMeleeConstants.COOKIE_MAX_AGE_DAYS)
        except Exception:
            return False
    
    def _load_cookies(self):
        """Load cookies from file"""
        with open(MtgMeleeConstants.COOKIE_FILE, "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", {})
            self.session.cookies.update(cookies)
            self.cookies = cookies
    
    def _refresh_cookies(self):
        """Authenticate and refresh cookies"""
        logger.info("Refreshing authentication cookies...")
        
        # Clear existing cookies
        self.session.cookies.clear()
        
        # Headers for login page
        classic_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://melee.gg/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Get login page
        login_page = self.session.get("https://melee.gg/Account/SignIn", headers=classic_headers)
        if login_page.status_code != 200:
            raise Exception(f"Failed to load login page: {login_page.status_code}")
        
        # Extract CSRF token
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            raise Exception("CSRF token not found")
        token = token_input["value"]
        
        # Load credentials
        if not os.path.exists(MtgMeleeConstants.CRED_FILE):
            raise FileNotFoundError(f"Missing credentials: {MtgMeleeConstants.CRED_FILE}")
        
        with open(MtgMeleeConstants.CRED_FILE, "r") as f:
            creds_raw = json.load(f)
            creds = {
                'email': creds_raw.get('email', creds_raw.get('login')),
                'password': creds_raw.get('password', creds_raw.get('mdp'))
            }
        
        # AJAX headers for login
        ajax_headers = {
            "User-Agent": classic_headers["User-Agent"],
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://melee.gg",
            "Referer": "https://melee.gg/Account/SignIn"
        }
        
        login_payload = {
            "email": creds['email'],
            "password": creds['password'],
            "__RequestVerificationToken": token
        }
        
        # Submit login
        response = self.session.post(
            "https://melee.gg/Account/SignInPassword",
            headers=ajax_headers,
            data=login_payload
        )
        
        if response.status_code != 200 or '"Error":true' in response.text:
            raise Exception(f"Login failed: status={response.status_code}")
        
        if ".AspNet.ApplicationCookie" not in self.session.cookies.get_dict():
            raise Exception("Login did not set auth cookie properly")
        
        # Save cookies
        cookies_to_store = {
            "cookies": self.session.cookies.get_dict(),
            "_timestamp": time.time()
        }
        with open(MtgMeleeConstants.COOKIE_FILE, "w") as f:
            json.dump(cookies_to_store, f, indent=2)
        
        self.cookies = self.session.cookies.get_dict()
        logger.info("✅ Authentication successful")


# ==================== Main Client ====================

class MtgMeleeClient:
    """Main client for interacting with Melee.gg"""
    
    def __init__(self):
        self.auth_manager = MtgMeleeAuthManager()
        self._client = None
    
    def get_client(self, load_cookies: bool = True) -> requests.Session:
        """Get authenticated client session"""
        return self.auth_manager.get_client(load_cookies)
    
    @staticmethod
    def normalize_spaces(data: str) -> str:
        """Normalize whitespace in text"""
        return re.sub(r'\s+', ' ', data).strip()
    
    def get_tournaments(self, start_date: datetime, end_date: datetime) -> List[MtgMeleeTournamentInfo]:
        """Get tournaments between dates"""
        length_tournament_page = 500
        result = []
        draw = 1
        starting_point = 0
        seen_ids = set()
        
        while True:
            payload = MtgMeleeConstants.build_magic_payload(
                start_date, end_date, 
                length=length_tournament_page, 
                draw=draw, 
                start=starting_point
            )
            
            tournament_list_url = 'https://melee.gg/Decklist/SearchDecklists'
            
            # Retry logic
            MAX_RETRIES = 3
            DELAY_SECONDS = 2
            
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = self.get_client(load_cookies=True).post(
                        tournament_list_url, 
                        data=payload
                    )
                    
                    if response.text.strip():
                        tournament_data = json.loads(response.text)
                        break
                    else:
                        logger.warning(f"Attempt {attempt}: Empty response")
                except json.JSONDecodeError:
                    logger.warning(f"Attempt {attempt}: Failed to parse JSON")
                
                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_SECONDS)
            else:
                logger.error("Failed to get tournament data after retries")
                return result
            
            # Process tournament data
            new_tournaments = tournament_data.get("data", [])
            
            for tournament in new_tournaments:
                tournament_id = tournament.get('Guid')
                if tournament_id and tournament_id not in seen_ids:
                    result.append(tournament)
                    seen_ids.add(tournament_id)
            
            # Check if we have all data
            if tournament_data["recordsFiltered"] == len(result):
                break
            if ((draw-1) * length_tournament_page) >= tournament_data["recordsFiltered"]:
                break
            
            draw += 1
            starting_point += length_tournament_page
        
        # Group by tournament and process
        tournaments = self._process_tournament_data(result)
        
        # Convert to MtgMeleeTournamentInfo objects
        tournament_infos = []
        for tournament_id, data in tournaments.items():
            tournament_info = MtgMeleeTournamentInfo(
                tournament_id=tournament_id,
                uri=data['uri'],
                date=data['date'],
                organizer=data['organizer'],
                name=data['name'],
                decklists=data['players'],
                formats=data['formats'],
                statut=data['statut'],
            )
            tournament_infos.append(tournament_info)
        
        return tournament_infos
    
    def _process_tournament_data(self, result: List[Dict]) -> Dict:
        """Process raw tournament data into structured format"""
        tournaments = {}
        
        for item in result:
            tournament_id = item['TournamentId']
            
            # Initialize tournament if not exists
            if tournament_id not in tournaments:
                tournament_url = MtgMeleeConstants.TOURNAMENT_PAGE.replace("{tournamentId}", str(tournament_id))
                
                # Get tournament format
                tournament_format = self._get_tournament_format(tournament_url)
                
                tournaments[tournament_id] = {
                    'players': {},
                    'date': parser.parse(item['TournamentStartDate']),
                    'name': item.get('TournamentName', 'Unnamed Tournament'),
                    'organizer': item['OrganizationName'],
                    'formats': tournament_format,
                    'uri': tournament_url,
                    'statut': str(item['TournamentStatusDescription']),
                }
            
            # Add player decklist
            player_name = self.normalize_spaces(item.get('OwnerUsername')) or "UnknownPlayer"
            Guid_deck = item.get('Guid')
            
            if player_name not in tournaments[tournament_id]['players']:
                tournaments[tournament_id]['players'][player_name] = {}
            
            tournaments[tournament_id]['players'][player_name][Guid_deck] = melee_extract_decklist(
                date=parser.parse(item['TournamentStartDate']),
                TournamentId=tournament_id,
                Valid=item.get('IsValid'),
                OwnerDisplayName=self.normalize_spaces(item.get('OwnerDisplayName')),
                OwnerUsername=player_name,
                Guid=Guid_deck,
                DecklistName=item.get('DecklistName'),
                decklists=item['Records'],
                decklists_formats=item.get('FormatDescription')
            )
        
        # Clean up duplicate decks per player
        for tournament_id, tournament in tournaments.items():
            players = tournament['players']
            for player_name, decks in players.items():
                if len(decks) > 1:
                    # Keep only valid decks if exactly one
                    valid_decks = {guid: deck for guid, deck in decks.items() if deck.Valid}
                    if len(valid_decks) == 1:
                        players[player_name] = valid_decks
                    else:
                        # Check if all decks are identical
                        decklists = list(decks.values())
                        first_deck = decklists[0]
                        all_identical = all(
                            deck.decklists == first_deck.decklists and 
                            deck.decklists_formats == first_deck.decklists_formats
                            for deck in decklists[1:]
                        )
                        if all_identical:
                            first_guid = next(iter(decks))
                            players[player_name] = {first_guid: first_deck}
        
        return tournaments
    
    def _get_tournament_format(self, tournament_url: str) -> str:
        """Get tournament format from tournament page"""
        try:
            tournament_page = self.get_client().get(tournament_url).text
            soup = BeautifulSoup(tournament_page, "html.parser")
            
            # Look for format in registration info
            registration_info = soup.find("p", id="tournament-headline-registration")
            if registration_info:
                text = registration_info.get_text()
                match = re.search(r'Format: (.*?) \|', text)
                if match:
                    return match.group(1)
            
            return "Unknown"
        except Exception as e:
            logger.error(f"Error getting tournament format: {e}")
            return "Unknown"
    
    def get_players(self, tournament: MtgMeleeTournamentInfo, 
                   max_players: Optional[int] = None) -> List[MtgMeleePlayerInfo]:
        """Get player standings and deck information"""
        result = []
        uri = tournament.uri
        
        # Get tournament page
        page_content = self.get_client().get(uri).text
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Find completed rounds
        round_nodes = soup.select('button.btn.btn-gray.round-selector[data-is-completed="True"]')
        if not round_nodes:
            return None
        
        round_ids = [node['data-id'] for node in round_nodes]
        
        # Get standings from last round
        has_data = True
        offset = 0
        round_id = round_ids[-1]
        
        while has_data and (max_players is None or offset < max_players):
            has_data = False
            
            # Build round parameters
            round_parameters = MtgMeleeConstants.ROUND_PAGE_PARAMETERS.replace(
                "{start}", str(offset)
            ).replace("{roundId}", round_id)
            
            round_url = "https://melee.gg/Tournament/GetStandings"
            
            # Retry logic for standings
            MAX_RETRIES = 3
            DELAY_SECONDS = 2
            
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = self.get_client().post(round_url, data=round_parameters)
                    if response.text.strip():
                        round_data = json.loads(response.text)
                        break
                except Exception as e:
                    logger.warning(f"Attempt {attempt}: Error getting standings - {e}")
                
                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_SECONDS)
            else:
                return result
            
            # Process standings data
            used_deck_ids = set()
            
            if len(round_data['data']) == 0 and offset == 0:
                if len(round_ids) > 1:
                    round_ids = round_ids[:-1]
                    round_id = round_ids[-1]
                    has_data = True
                    continue
                else:
                    break
            
            for entry in round_data['data']:
                has_data = True
                
                # Extract player info
                player_name = self.normalize_spaces(entry['Team']['Players'][0]['DisplayName'])
                if not player_name:
                    continue
                
                user_name = entry['Team']['Players'][0]['Username']
                
                # Create standing
                standing = Standing(
                    player=player_name,
                    rank=entry['Rank'],
                    points=entry['Points'],
                    wins=entry['MatchWins'],
                    losses=entry['MatchLosses'],
                    draws=entry['MatchDraws'],
                    omwp=entry['OpponentMatchWinPercentage'],
                    gwp=entry['TeamGameWinPercentage'],
                    ogwp=entry['OpponentGameWinPercentage']
                )
                
                # Get player decks
                player_decks = []
                
                # Get from tournament decklists
                player_decklists = tournament.decklists.get(user_name, None)
                if player_decklists:
                    for deck_list_id, player_decklist in player_decklists.items():
                        if deck_list_id not in used_deck_ids:
                            used_deck_ids.add(deck_list_id)
                            player_decks.append(MtgMeleePlayerDeck(
                                deck_id=deck_list_id,
                                format=player_decklist.decklists_formats,
                                uri=MtgMeleeConstants.format_url(
                                    MtgMeleeConstants.DECK_PAGE, 
                                    deckId=deck_list_id
                                ),
                                tournament_decklists=player_decklist
                            ))
                else:
                    # Fallback to entry decklists
                    for decklist in entry.get('Decklists', []):
                        deck_list_id = decklist.get('DecklistId')
                        if deck_list_id:
                            player_decks.append(MtgMeleePlayerDeck(
                                deck_id=deck_list_id,
                                format=decklist.get('Format', 'Unknown'),
                                uri=MtgMeleeConstants.format_url(
                                    MtgMeleeConstants.DECK_PAGE,
                                    deckId=deck_list_id
                                )
                            ))
                
                # Create player info
                result.append(MtgMeleePlayerInfo(
                    username=user_name,
                    player_name=player_name,
                    result=f"{standing.wins}-{standing.losses}-{standing.draws}",
                    standing=standing,
                    decks=player_decks if player_decks else None,
                    nb_of_oppo=entry.get('OpponentCount', 0)
                ))
            
            offset += 25
        
        return result
    
    def get_deck(self, uri: str, players: List[MtgMeleePlayerInfo], 
                skip_round_data: bool = False) -> MtgMeleeDeckInfo:
        """Get complete deck information including cards and rounds"""
        
        # Get deck page
        deck_page_content = self.get_client().get(uri).text
        deck_soup = BeautifulSoup(deck_page_content, 'html.parser')
        
        # Extract deck text
        deck_text = deck_soup.select_one("pre#decklist-text")
        if not deck_text:
            return None
        
        card_list = deck_text.text.split("\r\n")
        
        # Get player info
        player_link_element = deck_soup.select_one("a.text-nowrap.text-muted")
        if player_link_element:
            player_url = player_link_element['href']
            player_raw = player_link_element.select_one("span.text-nowrap").text.strip()
            player_id = player_url.split("/")[-1]
            player_name = self.get_player_name(player_raw, player_id, players)
        else:
            player_name = "Unknown"
        
        # Get date
        date_string = deck_soup.select_one('span[data-toggle="date"]')
        if date_string:
            date_value = date_string.get('data-value', '').strip()
            try:
                date_tournament = datetime.strptime(date_value, "%m/%d/%Y %I:%M:%S %p")
            except:
                date_tournament = None
        else:
            date_tournament = None
        
        # Get format
        format_div = deck_soup.select_one(".d-flex.flex-row.gap-8px .text-nowrap:last-of-type")
        format_name = format_div.text.strip() if format_div else "Unknown"
        
        # Parse cards
        main_board = []
        side_board = []
        inside_sideboard = False
        inside_companion = False
        inside_commander = False
        
        CardNameNormalizer.initialize()
        
        for card in card_list:
            if card in ['MainDeck', 'Companion', 'Sideboard', 'Commander', '', 'Deck']:
                if card == 'Commander':
                    inside_commander = True
                    inside_sideboard = True
                elif card == 'Companion':
                    inside_companion = True
                elif card == 'Sideboard':
                    inside_sideboard = True
                elif card == 'Deck' and inside_commander:
                    inside_sideboard = False
                    inside_commander = False
                    inside_companion = False
            else:
                if inside_companion and not inside_commander:
                    continue
                
                try:
                    count, name = card.split(" ", 1)
                    count = int(count)
                    name = CardNameNormalizer.normalize(name)
                    
                    if inside_sideboard:
                        side_board.append(DeckItem(card_name=name, count=count))
                    else:
                        main_board.append(DeckItem(card_name=name, count=count))
                except:
                    continue
        
        # Get rounds data if needed
        rounds = []
        if not skip_round_data:
            rounds = self._get_deck_rounds(uri, player_name)
        
        return MtgMeleeDeckInfo(
            date=None,  # Match original behavior
            deck_uri=uri,
            player=player_name,
            format=format_name,
            mainboard=main_board,
            sideboard=side_board,
            rounds=rounds if rounds else None
        )
    
    def _get_deck_rounds(self, deck_uri: str, player_name: str) -> List[MtgMeleeRoundInfo]:
        """Get round/match data for a deck"""
        rounds = []
        
        try:
            # Extract deck GUID
            decklist_guid = deck_uri.split('/')[-1]
            api_url = f"https://melee.gg/Decklist/GetTournamentViewData/{decklist_guid}"
            
            response = self.get_client().get(api_url)
            if response.status_code == 200:
                match_data = response.json()
                
                # Parse nested JSON
                if 'Json' in match_data and match_data['Json']:
                    inner_data = json.loads(match_data['Json'])
                    
                    if 'Matches' in inner_data and inner_data['Matches']:
                        for match in inner_data['Matches']:
                            round_name = f"Round {match['Round']}"
                            opponent_name = self.normalize_spaces(match['Opponent']) if match['Opponent'] else "-"
                            result = match['Result']
                            
                            round_info = self.get_round_from_api(
                                round_name, player_name, opponent_name, 
                                self.normalize_spaces(result)
                            )
                            if round_info:
                                rounds.append(round_info)
        except Exception as e:
            logger.error(f"Error fetching match data: {e}")
        
        return rounds
    
    def get_round_from_api(self, round_name: str, player_name: str, 
                          opponent_name: str, result: str) -> Optional[MtgMeleeRoundInfo]:
        """Parse round information from API data"""
        item = None
        
        if result.startswith(f"{player_name} won"):
            item = RoundItem(player1=player_name, player2=opponent_name, result=result.split(" ")[-1])
        elif opponent_name != "-" and result.startswith(f"{opponent_name} won"):
            item = RoundItem(player1=opponent_name, player2=player_name, result=result.split(" ")[-1])
        elif "Draw" in result:
            item = RoundItem(player1=player_name, player2=opponent_name, result=result.split(" ")[0])
        elif "bye" in result or "was awarded a bye" in result:
            item = RoundItem(player1=player_name, player2="-", result="2-0-0")
        elif result.startswith("won "):
            item = RoundItem(player1="-", player2=player_name, result="2-0-0")
        elif result.startswith(f"{player_name} forfeited"):
            item = RoundItem(player1=player_name, player2=opponent_name, result="0-2-0")
        elif result.startswith("Not reported") or "[FORMAT EXCEPTION]" in result:
            item = RoundItem(player1=player_name, player2=opponent_name, result="0-0-0")
        elif f"{player_name} forfeited" in result and f"{opponent_name} forfeited" in result:
            item = RoundItem(player1=player_name, player2=opponent_name, result="0-0-0")
        
        if item is None:
            return None
        
        # Ensure result has draws
        if len(item.result.split("-")) == 2:
            item.result += "-0"
        
        return MtgMeleeRoundInfo(round_name=round_name, match=item)
    
    def get_player_name(self, player_name_raw: str, player_id: str, 
                       players: List[MtgMeleePlayerInfo]) -> str:
        """Get normalized player name"""
        if player_id:
            player_info = next((p for p in players if p.username == player_id), None)
            if player_info:
                return player_info.player_name
            elif player_name_raw:
                return self.normalize_spaces(player_name_raw)
        return "-"


# ==================== Tournament Analyzer ====================

class MtgMeleeAnalyzer:
    """Analyzes tournaments and filters based on criteria"""
    
    def __init__(self):
        self._banned_only_in_duel = None
    
    def get_scraper_tournaments(self, tournament: MtgMeleeTournamentInfo) -> Optional[List[MtgMeleeTournament]]:
        """Process tournament and return list of MtgMeleeTournament objects"""
        
        # Check if Pro Tour
        is_pro_tour = (
            tournament.organizer == "Wizards of the Coast" and
            ("Pro Tour" in tournament.name or "World Championship" in tournament.name) and
            "Qualifier" not in tournament.name
        )
        
        # Skip blacklisted tournaments
        if any(term.lower() in tournament.name.lower() for term in MtgMeleeAnalyzerSettings.BlacklistedTerms):
            return None
        
        # Skip invalid formats
        if not is_pro_tour and tournament.formats not in MtgMeleeAnalyzerSettings.ValidFormats:
            return None
        
        # Skip in-progress tournaments
        if tournament.statut != 'Ended' and (tournament.date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)) < timedelta(days=5):
            return None
        
        # Check deck validity
        Number_of_deck = sum(len(player_decks) for player_decks in tournament.decklists.values())
        Number_of_valid_decklist = sum(
            1
            for player_decks in tournament.decklists.values()
            for decklist in player_decks.values()
            if decklist.Valid
        )
        ratio_of_valid_decklist = Number_of_valid_decklist / Number_of_deck if Number_of_deck > 0 else 0
        
        if Number_of_valid_decklist < MtgMeleeConstants.Min_number_of_valid_decklists:
            return None
        if ratio_of_valid_decklist < MtgMeleeConstants.VALID_DECKLIST_THRESHOLD:
            return None
        
        # Get players
        client = MtgMeleeClient()
        players = client.get_players(tournament, MtgMeleeAnalyzerSettings.PlayersLoadedForAnalysis)
        
        if not players:
            return None
        
        # Commander format check
        if tournament.formats == 'Commander':
            for player in players:
                if player.nb_of_oppo > (player.standing.wins + player.standing.losses + player.standing.draws):
                    return None
        
        # Determine tournament type
        max_decks_per_player = max((len(p.decks) for p in players if p.decks), default=0)
        
        if is_pro_tour:
            return [self.generate_pro_tour_tournament(tournament, players)]
        else:
            if max_decks_per_player == 1:
                return [self.generate_single_format_tournament(tournament)]
            else:
                result = []
                for i in range(max_decks_per_player):
                    result.append(self.generate_multi_format_tournament(tournament, players, i, max_decks_per_player))
                return result
    
    def generate_single_format_tournament(self, tournament: MtgMeleeTournamentInfo) -> MtgMeleeTournament:
        """Generate tournament object for single format tournament"""
        format_detected = tournament.formats
        return MtgMeleeTournament(
            uri=tournament.uri,
            date=tournament.date,
            name=tournament.name,
            formats=format_detected,
            json_file=self.generate_file_name(tournament, format_detected, -1),
            decklists=tournament.decklists
        )
    
    def generate_multi_format_tournament(self, tournament: MtgMeleeTournamentInfo, 
                                       players: List[MtgMeleePlayerInfo], 
                                       offset: int, expected_decks: int) -> MtgMeleeTournament:
        """Generate tournament object for multi-format tournament"""
        # Sample decks to detect format
        client = MtgMeleeClient()
        deck_uris = [
            p.decks[offset].uri for p in players 
            if p.decks and len(p.decks) > offset
        ][:MtgMeleeAnalyzerSettings.DecksLoadedForAnalysis]
        
        decks = [client.get_deck(uri, players, True) for uri in deck_uris]
        formats = {deck.format for deck in decks}
        
        valid_formats = {f for f in formats if f in MtgMeleeAnalyzerSettings.ValidFormats}
        if len(valid_formats) > 1:
            raise ValueError(f"Multiple formats detected: {formats}")
        elif len(valid_formats) == 1:
            format_detected = valid_formats.pop()
        else:
            format_detected = "Unknown"
        
        return MtgMeleeTournament(
            uri=tournament.uri,
            date=tournament.date,
            name=tournament.name,
            formats=format_detected,
            json_file=FilenameGenerator.generate_file_name(
                tournament_id=tournament.uri.split("/")[-1],
                tournament_name=tournament.name,
                tournament_date=tournament.date,
                tournament_format=format_detected,
                valid_formats=MtgMeleeAnalyzerSettings.ValidFormats,
                seat=offset
            ),
            deck_offset=offset,
            expected_decks=expected_decks,
            fix_behavior="Skip",
            decklists=tournament.decklists
        )
    
    def generate_pro_tour_tournament(self, tournament: MtgMeleeTournamentInfo, 
                                   players: List[MtgMeleePlayerInfo]) -> MtgMeleeTournament:
        """Generate tournament object for Pro Tour"""
        # Sample last deck for each player
        client = MtgMeleeClient()
        deck_uris = [p.decks[-1].uri for p in players if p.decks]
        decks = [client.get_deck(uri, players, True) for uri in deck_uris]
        
        formats = {deck.format for deck in decks}
        valid_formats = {f for f in formats if f in MtgMeleeAnalyzerSettings.ValidFormats}
        
        if len(valid_formats) > 1:
            raise ValueError(f"Multiple formats detected: {formats}")
        elif len(valid_formats) == 1:
            format_detected = valid_formats.pop()
        else:
            format_detected = "Unknown"
        
        return MtgMeleeTournament(
            uri=tournament.uri,
            date=tournament.date,
            name=tournament.name,
            formats=format_detected,
            json_file=self.generate_file_name(tournament, format_detected, -1),
            deck_offset=0,
            expected_decks=3,
            fix_behavior="UseFirst",
            excluded_rounds=["Round 1", "Round 2", "Round 3", "Round 9", "Round 10", "Round 11"],
            decklists=tournament.decklists
        )
    
    def generate_file_name(self, tournament: MtgMeleeTournamentInfo, 
                          format_name: str, offset: int) -> str:
        """Generate standardized filename"""
        return FilenameGenerator.generate_file_name(
            tournament_id=tournament.uri.split("/")[-1],
            tournament_name=tournament.name,
            tournament_date=tournament.date,
            tournament_format=format_name,
            valid_formats=MtgMeleeAnalyzerSettings.ValidFormats,
            seat=offset
        )


# ==================== Tournament List ====================

class TournamentList:
    """Main entry point for tournament processing"""
    
    def get_tournament_details(self, tournament: MtgMeleeTournament) -> CacheItem:
        """Get complete tournament details"""
        client = MtgMeleeClient()
        players = client.get_players(tournament)
        
        decks = []
        standings = []
        consolidated_rounds = {}
        
        for player in players:
            standings.append(player.standing)
            
            player_position = player.standing.rank
            player_result = (f"{player_position}st Place" if player_position <= 3 
                           else f"{player_position}th Place")
            
            # Get deck
            deck = None
            if len(player.decks) > 0:
                deck_uri = player.decks[-1].uri
                deck = client.get_deck(deck_uri, players)
            
            if deck is not None:
                deck.result = player_result
                decks.append(deck)
                
                # Consolidate rounds
                if deck.rounds:
                    for deck_round in deck.rounds:
                        if (tournament.excluded_rounds is not None and 
                            deck_round.round_name in tournament.excluded_rounds):
                            continue
                        
                        if deck_round.round_name not in consolidated_rounds:
                            consolidated_rounds[deck_round.round_name] = {}
                        
                        round_item_key = (f"{deck_round.round_name}_{deck_round.match.player1}_"
                                        f"{deck_round.match.player2}")
                        if round_item_key not in consolidated_rounds[deck_round.round_name]:
                            consolidated_rounds[deck_round.round_name][round_item_key] = deck_round.match
        
        # Convert rounds to list
        rounds = [
            Round(round_name, list(matches.values())) 
            for round_name, matches in consolidated_rounds.items()
        ]
        
        return CacheItem(
            tournament=tournament,
            decks=decks,
            standings=standings,
            rounds=rounds
        )
    
    @classmethod
    def DL_tournaments(cls, start_date: datetime, end_date: datetime = None) -> List[MtgMeleeTournament]:
        """Download tournaments between dates"""
        if start_date < datetime(2020, 1, 1, tzinfo=timezone.utc):
            return []
        
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        result = []
        
        while start_date < end_date:
            current_end_date = start_date + timedelta(days=7)
            logger.info(f"Downloading tournaments from {start_date.strftime('%Y-%m-%d')} "
                       f"to {current_end_date.strftime('%Y-%m-%d')}")
            
            # Get tournaments
            client = MtgMeleeClient()
            tournaments = client.get_tournaments(start_date, current_end_date)
            
            # Analyze tournaments
            analyzer = MtgMeleeAnalyzer()
            for tournament in tournaments:
                melee_tournaments = analyzer.get_scraper_tournaments(tournament)
                if melee_tournaments:
                    result.extend(melee_tournaments)
            
            start_date = current_end_date
        
        logger.info(f"Download finished - found {len(result)} tournaments")
        return result


# ==================== Main Function ====================

def main():
    """Test the complete scraper"""
    # Test downloading tournaments
    start_date = datetime.now(timezone.utc) - timedelta(days=7)
    end_date = datetime.now(timezone.utc)
    
    tournaments = TournamentList.DL_tournaments(start_date, end_date)
    logger.info(f"Found {len(tournaments)} tournaments")
    
    # Get details for first tournament
    if tournaments:
        tournament_list = TournamentList()
        details = tournament_list.get_tournament_details(tournaments[0])
        logger.info(f"Tournament: {tournaments[0].name}")
        logger.info(f"Decks: {len(details.decks)}")
        logger.info(f"Standings: {len(details.standings)}")
        logger.info(f"Rounds: {len(details.rounds)}")


if __name__ == "__main__":
    main()