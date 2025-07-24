#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MTGO Tournament Scraper - Robust Version
Enhanced version with better error handling and tournament type detection
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse
from urllib.parse import urljoin
import os
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
import logging
import time
from pathlib import Path
import hashlib

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DeckItem:
    """Represents a single card in a deck"""
    count: int
    card_name: str


@dataclass
class Deck:
    """Represents a complete deck"""
    date: datetime
    player: str
    result: str
    anchor_uri: str
    mainboard: List[DeckItem] = field(default_factory=list)
    sideboard: List[DeckItem] = field(default_factory=list)


@dataclass
class Tournament:
    """Represents a tournament"""
    name: str
    date: datetime
    uri: str
    formats: str
    tournament_type: str  # New field for tournament type
    json_file: str
    force_redownload: bool = False


@dataclass
class Standing:
    """Represents a player's standing in a tournament"""
    rank: int
    player: str
    points: int
    wins: int
    losses: int
    draws: int
    omwp: float
    gwp: float
    ogwp: float


@dataclass
class RoundItem:
    """Represents a match in a round"""
    player1: str
    player2: str
    result: str


@dataclass
class Round:
    """Represents a tournament round"""
    round_name: str
    matches: List[RoundItem]


@dataclass
class CacheItem:
    """Represents cached tournament data"""
    tournament: Tournament
    decks: List[Deck]
    rounds: Optional[List[Round]] = None
    standings: Optional[List[Standing]] = None


class MTGOSettings:
    """Configuration for MTGO scraping"""
    LIST_URL = "https://www.mtgo.com/decklists/{year}/{month}"
    ROOT_URL = "https://www.mtgo.com"
    LEAGUE_REDOWNLOAD_DAYS = 3
    
    # Expanded format list with aliases
    ValidFormats = {
        "Standard": ["Standard"],
        "Modern": ["Modern"],
        "Pioneer": ["Pioneer"],
        "Legacy": ["Legacy"],
        "Vintage": ["Vintage"],
        "Pauper": ["Pauper"],
        "Commander": ["Commander", "Duel"],
        "Limited": ["Limited", "Draft", "Sealed"]
    }
    
    # Tournament types to track
    TournamentTypes = {
        "league": ["League"],
        "challenge": ["Challenge"],
        "qualifier": ["Qualifier", "PTQ", "RC", "RCQ", "RPTQ"],
        "showcase": ["Showcase"],
        "championship": ["Championship", "Champs", "Finals"],
        "trial": ["Trial"],
        "prelim": ["Prelim", "Preliminary"],
        "special": ["Special", "Festival", "Anniversary"],
        "other": []  # Catch-all
    }
    
    # Network settings
    REQUEST_TIMEOUT = 60  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds


class TournamentTypeDetector:
    """Enhanced tournament type detection"""
    
    @staticmethod
    def detect_format(title: str) -> Optional[str]:
        """Detect format from tournament title with better accuracy"""
        title_lower = title.lower()
        
        # Check each format and its aliases
        for format_name, aliases in MTGOSettings.ValidFormats.items():
            for alias in aliases:
                if alias.lower() in title_lower:
                    return format_name
        
        # Special cases
        if "duel commander" in title_lower:
            return "Commander"
        
        logger.warning(f"Could not detect format from title: {title}")
        return None
    
    @staticmethod
    def detect_tournament_type(title: str) -> str:
        """Detect tournament type from title"""
        title_lower = title.lower()
        
        for type_name, keywords in MTGOSettings.TournamentTypes.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return type_name
        
        # Default to 'other' if no match
        return "other"


class NetworkHelper:
    """Helper class for network operations with retry logic"""
    
    @staticmethod
    def fetch_with_retry(url: str, max_retries: int = MTGOSettings.MAX_RETRIES) -> Optional[requests.Response]:
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
                response = requests.get(url, timeout=MTGOSettings.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 404:
                    logger.warning(f"404 Not Found: {url}")
                    return None
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error fetching {url}")
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(MTGOSettings.RETRY_DELAY)
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None


class DataValidator:
    """Validate tournament and deck data"""
    
    @staticmethod
    def validate_deck(deck: Deck) -> bool:
        """Validate deck data"""
        # Check mainboard size (should be at least 60 for most formats)
        mainboard_count = sum(item.count for item in deck.mainboard)
        if mainboard_count < 40:  # Allow for limited formats
            logger.warning(f"Deck for {deck.player} has only {mainboard_count} mainboard cards")
            return False
        
        # Check sideboard size (should be 0-15)
        sideboard_count = sum(item.count for item in deck.sideboard)
        if sideboard_count > 15:
            logger.warning(f"Deck for {deck.player} has {sideboard_count} sideboard cards")
            return False
        
        # Check for empty player name
        if not deck.player or deck.player == "Unknown":
            logger.warning("Deck has invalid player name")
            return False
        
        return True
    
    @staticmethod
    def validate_tournament(tournament: Tournament) -> bool:
        """Validate tournament data"""
        # Check date is reasonable (not in future, not too old)
        now = datetime.now(timezone.utc)
        if tournament.date > now.date():
            logger.warning(f"Tournament date is in the future: {tournament.date}")
            return False
        
        # Check date is not too old (e.g., more than 5 years)
        if (now.date() - tournament.date).days > 1825:  # 5 years
            logger.warning(f"Tournament date is very old: {tournament.date}")
            return False
        
        # Check format is valid
        if not tournament.formats:
            logger.warning(f"Tournament has no format: {tournament.name}")
            return False
        
        return True


class TournamentTracker:
    """Track processed tournaments to avoid duplicates"""
    
    def __init__(self, tracker_file: str = "data/raw/mtgo/.processed_tournaments.json"):
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
    
    def get_tournament_id(self, tournament: Tournament) -> str:
        """Generate unique ID for tournament"""
        # Use URL hash for unique ID
        return hashlib.md5(tournament.uri.encode()).hexdigest()
    
    def is_processed(self, tournament: Tournament) -> bool:
        """Check if tournament was already processed"""
        return self.get_tournament_id(tournament) in self.processed
    
    def mark_processed(self, tournament: Tournament):
        """Mark tournament as processed"""
        self.processed.add(self.get_tournament_id(tournament))
        self.save()


class CardNameNormalizer:
    """Enhanced card name normalization"""
    
    _replacements = {}
    _split_card_pattern = re.compile(r'\s*//\s*')
    
    @classmethod
    def initialize(cls):
        """Initialize card name replacements"""
        cls._replacements = {
            # Common card name issues
            "Teferi, Who Slows the Sunset": "Teferi, Who Slows the Sunset",
            # Add more as needed
        }
    
    @classmethod
    def normalize(cls, name: str) -> str:
        """Normalize a card name"""
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Apply specific replacements
        if name in cls._replacements:
            return cls._replacements[name]
        
        # Handle split cards
        if "//" in name:
            # For split cards, keep the full name but normalize spacing
            parts = cls._split_card_pattern.split(name)
            name = " // ".join(part.strip() for part in parts)
        
        # Remove any multiple spaces
        name = ' '.join(name.split())
        
        return name


class DeckNormalizer:
    """Normalizes deck data"""
    
    @staticmethod
    def normalize(deck: Deck) -> Deck:
        """Normalize a deck"""
        # Sort mainboard and sideboard by card name
        deck.mainboard.sort(key=lambda x: (x.card_name, -x.count))
        deck.sideboard.sort(key=lambda x: (x.card_name, -x.count))
        
        # Validate deck
        if not DataValidator.validate_deck(deck):
            logger.warning(f"Deck validation failed for {deck.player}")
        
        return deck


class TournamentList:
    """Enhanced tournament list handler"""
    
    def __init__(self):
        self.tracker = TournamentTracker()
    
    @staticmethod
    def increment_month(date: datetime) -> datetime:
        """Increment the month, rolling over to the next year if needed."""
        new_month = date.month + 1
        new_year = date.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        return date.replace(year=new_year, month=new_month, day=1)
    
    def DL_tournaments(self, start_date: datetime, end_date: datetime = None,
                      skip_processed: bool = True) -> List[Tournament]:
        """Download tournaments with enhanced error handling"""
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        results = []
        current_date = start_date
        failed_months = []
        
        while current_date <= end_date:
            tournament_list_url = MTGOSettings.LIST_URL.format(
                year=current_date.year,
                month=f"{current_date.month:02}"
            )
            
            logger.info(f"Fetching tournaments for {current_date.year}-{current_date.month:02}")
            
            response = NetworkHelper.fetch_with_retry(tournament_list_url)
            if response is None:
                failed_months.append(f"{current_date.year}-{current_date.month:02}")
                current_date = self.increment_month(current_date)
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                tournament_nodes = soup.select("li.decklists-item")
                
                if not tournament_nodes:
                    logger.info(f"No tournaments found for {current_date.year}-{current_date.month:02}")
                    current_date = self.increment_month(current_date)
                    continue
                
                month_tournaments = 0
                for tournament_node in tournament_nodes:
                    tournament = self._parse_tournament_node(tournament_node)
                    if tournament:
                        # Skip if already processed
                        if skip_processed and self.tracker.is_processed(tournament):
                            logger.debug(f"Skipping already processed: {tournament.name}")
                            continue
                        
                        # Validate tournament
                        if DataValidator.validate_tournament(tournament):
                            results.append(tournament)
                            month_tournaments += 1
                
                logger.info(f"Found {month_tournaments} new tournaments for {current_date.year}-{current_date.month:02}")
                
            except Exception as e:
                logger.error(f"Error parsing tournaments for {current_date}: {e}")
                failed_months.append(f"{current_date.year}-{current_date.month:02}")
            
            current_date = self.increment_month(current_date)
        
        if failed_months:
            logger.warning(f"Failed to fetch tournaments for months: {', '.join(failed_months)}")
        
        # Filter results by date range
        filtered_results = [t for t in results if start_date.date() <= t.date <= end_date.date()]
        
        # Sort by date (newest first)
        sorted_results = sorted(filtered_results, key=lambda t: t.date, reverse=True)
        
        logger.info(f"Total tournaments found: {len(sorted_results)}")
        return sorted_results
    
    def _parse_tournament_node(self, tournament_node) -> Optional[Tournament]:
        """Parse a single tournament node with better error handling"""
        try:
            # Extract basic info
            title_elem = tournament_node.select_one("a > div > h3")
            url_elem = tournament_node.select_one("a")
            time_elem = tournament_node.select_one("a > time")
            
            if not all([title_elem, url_elem, time_elem]):
                logger.warning("Missing required elements in tournament node")
                return None
            
            title = title_elem.text.strip()
            url = url_elem.get("href", "")
            date_string = time_elem.get("datetime", "")
            
            if not all([title, url, date_string]):
                logger.warning(f"Missing data in tournament node: title={title}, url={url}, date={date_string}")
                return None
            
            # Parse date
            try:
                parsed_date = isoparse(date_string).date()
            except Exception as e:
                logger.error(f"Error parsing date '{date_string}': {e}")
                return None
            
            # Build full URL
            url = urljoin(MTGOSettings.ROOT_URL, url)
            
            # Detect format and tournament type
            format_name = TournamentTypeDetector.detect_format(title)
            if not format_name:
                logger.warning(f"Skipping tournament with unknown format: {title}")
                return None
            
            tournament_type = TournamentTypeDetector.detect_tournament_type(title)
            
            # Create tournament object
            tournament = Tournament(
                name=title,
                date=parsed_date,
                uri=url,
                formats=format_name,
                tournament_type=tournament_type,
                json_file=os.path.splitext(os.path.basename(url))[0] + ".json",
                force_redownload=("league" in title.lower() and
                                (datetime.now(timezone.utc).date() - parsed_date).days < MTGOSettings.LEAGUE_REDOWNLOAD_DAYS)
            )
            
            logger.debug(f"Parsed tournament: {title} ({format_name}/{tournament_type}) on {parsed_date}")
            return tournament
            
        except Exception as e:
            logger.error(f"Error parsing tournament node: {e}")
            return None
    
    def get_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """Get tournament details with enhanced error handling"""
        logger.info(f"Fetching details for: {tournament.name}")
        
        response = NetworkHelper.fetch_with_retry(tournament.uri)
        if response is None:
            return None
        
        try:
            html_content = response.text
            
            # Find JSON data with multiple patterns
            json_data = self._extract_json_data(html_content)
            if not json_data:
                logger.error("Could not extract JSON data from tournament page")
                return None
            
            # Parse JSON
            try:
                event_json = json.loads(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON data: {e}")
                return None
            
            # Check for errors
            if "errorCode" in event_json:
                logger.error(f"Server error in tournament data: {event_json.get('errorCode')}")
                return None
            
            # Determine event type
            event_type = "tournament" if "starttime" in event_json else "league"
            logger.info(f"Event type: {event_type}")
            
            # Parse tournament data
            winloss = None
            standings = None
            bracket = None
            
            if event_type == "tournament":
                winloss = TournamentLoader.parse_winloss(event_json)
                standings = TournamentLoader.parse_standing(event_json, winloss)
                bracket = TournamentLoader.parse_bracket(event_json)
            
            # Parse decks
            decks = TournamentLoader.parse_decks(tournament, event_type, winloss, event_json)
            
            if not decks:
                logger.warning("No decks found in tournament")
                return None
            
            # Validate decks
            valid_decks = []
            for deck in decks:
                if DataValidator.validate_deck(deck):
                    valid_decks.append(deck)
                else:
                    logger.warning(f"Skipping invalid deck for player {deck.player}")
            
            if not valid_decks:
                logger.error("No valid decks found in tournament")
                return None
            
            # Reorder decks if we have standings
            if standings:
                valid_decks = OrderNormalizer.reorder_decks(valid_decks, standings, bracket, bracket is not None)
            
            logger.info(f"Successfully parsed {len(valid_decks)} valid decks")
            
            # Mark tournament as processed
            self.tracker.mark_processed(tournament)
            
            return CacheItem(
                tournament=tournament,
                decks=valid_decks,
                rounds=bracket,
                standings=standings
            )
            
        except Exception as e:
            logger.error(f"Error getting tournament details: {e}", exc_info=True)
            return None
    
    def _extract_json_data(self, html_content: str) -> Optional[str]:
        """Extract JSON data from HTML with multiple patterns"""
        patterns = [
            r'window\.MTGO\.decklists\.data\s*=\s*({.*?});',
            r'window\.MTGO\.decklists\.data\s*=\s*({.*?})\s*;',
            r'<script[^>]*>\s*window\.MTGO\.decklists\.data\s*=\s*({.*?});\s*</script>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                return match.group(1)
        
        # Try line-by-line approach
        for line in html_content.splitlines():
            line = line.strip()
            if line.startswith("window.MTGO.decklists.data = "):
                return line[29:-1]  # Remove prefix and semicolon
        
        return None


class OrderNormalizer:
    """Reorders decks based on standings and brackets"""
    
    @staticmethod
    def reorder_decks(decks: List[Deck], standings: List[Standing], 
                     bracket: Optional[List[Round]], has_bracket: bool) -> List[Deck]:
        """Reorder decks based on tournament results"""
        if not standings:
            return decks
        
        # Create a mapping of player names to decks
        deck_map = {deck.player: deck for deck in decks}
        
        # Reorder based on standings
        reordered = []
        for standing in standings:
            if standing.player in deck_map:
                reordered.append(deck_map[standing.player])
        
        # Add any remaining decks that weren't in standings
        for deck in decks:
            if deck not in reordered:
                reordered.append(deck)
        
        return reordered


class TournamentLoader:
    """Enhanced tournament data parser"""
    
    @staticmethod
    def parse_event_date(event_date_str: str) -> datetime:
        """Parse event date from various formats"""
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(event_date_str, fmt)
            except ValueError:
                continue
        
        # Try isoparse as fallback
        try:
            return isoparse(event_date_str)
        except Exception:
            pass
        
        raise ValueError(f"Could not parse date: {event_date_str}")
    
    @staticmethod
    def parse_winloss(event_json: dict) -> Optional[Dict[str, str]]:
        """Parse win/loss records"""
        if "winloss" not in event_json:
            return None
        
        player_winloss = {}
        for winloss in event_json["winloss"]:
            try:
                player_id = str(winloss["loginid"])
                wins = int(winloss.get("wins", 0))
                losses = int(winloss.get("losses", 0))
                player_winloss[player_id] = f"{wins}-{losses}"
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing winloss entry: {e}")
                continue
        
        return player_winloss if player_winloss else None
    
    @staticmethod
    def parse_decks(tournament: Tournament, event_type: str, 
                   winloss: Optional[Dict[str, str]], event_json: dict) -> Optional[List[Deck]]:
        """Parse deck data from JSON with enhanced error handling"""
        # Get event date
        date_fields = ["publish_date", "starttime", "date", "event_date"]
        event_date_str = None
        
        for field in date_fields:
            if field in event_json and event_json[field]:
                event_date_str = event_json[field]
                break
        
        if not event_date_str:
            logger.error(f"No date found in event data. Available fields: {list(event_json.keys())}")
            return None
        
        try:
            event_date_naive = TournamentLoader.parse_event_date(event_date_str)
            event_date = event_date_naive.replace(tzinfo=timezone.utc)
        except ValueError as e:
            logger.error(f"Error parsing event date: {e}")
            return None
        
        # Check for decklists
        if "decklists" not in event_json:
            logger.error("No decklists found in event data")
            return None
        
        CardNameNormalizer.initialize()
        decks = []
        rank = 1
        
        for deck_data in event_json["decklists"]:
            try:
                deck = TournamentLoader._parse_single_deck(
                    deck_data, tournament, event_type, winloss, 
                    event_date, rank
                )
                if deck:
                    deck = DeckNormalizer.normalize(deck)
                    decks.append(deck)
                    if not winloss:  # Only increment rank for challenges without winloss
                        rank += 1
                
            except Exception as e:
                logger.error(f"Error parsing deck: {e}", exc_info=True)
                continue
        
        return decks if decks else None
    
    @staticmethod
    def _parse_single_deck(deck_data: dict, tournament: Tournament, event_type: str,
                          winloss: Optional[Dict[str, str]], event_date: datetime, 
                          rank: int) -> Optional[Deck]:
        """Parse a single deck entry"""
        mainboard = []
        sideboard = []
        
        # Get player info
        player = deck_data.get("player", deck_data.get("login_name", "Unknown"))
        player_id = str(deck_data.get("loginid", ""))
        
        if player == "Unknown" and not player_id:
            logger.warning("Deck missing player information")
            return None
        
        # Parse mainboard
        main_deck = deck_data.get("main_deck", deck_data.get("mainboard", []))
        for card in main_deck:
            try:
                if isinstance(card, dict):
                    name = card.get("card_attributes", {}).get("card_name") or card.get("name", "")
                    quantity = int(card.get("qty", card.get("quantity", 0)))
                else:
                    logger.warning(f"Unexpected card format: {type(card)}")
                    continue
                
                if name and quantity > 0:
                    name_normalized = CardNameNormalizer.normalize(name)
                    mainboard.append(DeckItem(count=quantity, card_name=name_normalized))
                    
            except Exception as e:
                logger.warning(f"Error parsing mainboard card: {e}")
                continue
        
        # Parse sideboard
        sideboard_deck = deck_data.get("sideboard_deck", deck_data.get("sideboard", []))
        for card in sideboard_deck:
            try:
                if isinstance(card, dict):
                    name = card.get("card_attributes", {}).get("card_name") or card.get("name", "")
                    quantity = int(card.get("qty", card.get("quantity", 0)))
                else:
                    logger.warning(f"Unexpected card format: {type(card)}")
                    continue
                
                if name and quantity > 0:
                    name_normalized = CardNameNormalizer.normalize(name)
                    sideboard.append(DeckItem(count=quantity, card_name=name_normalized))
                    
            except Exception as e:
                logger.warning(f"Error parsing sideboard card: {e}")
                continue
        
        # Determine result
        result = TournamentLoader._determine_result(
            deck_data, event_type, winloss, player_id, rank
        )
        
        # Create deck object
        deck = Deck(
            date=event_date,
            player=player,
            result=result,
            anchor_uri=f"{tournament.uri}#deck_{player}",
            mainboard=mainboard,
            sideboard=sideboard
        )
        
        return deck
    
    @staticmethod
    def _determine_result(deck_data: dict, event_type: str, 
                         winloss: Optional[Dict[str, str]], 
                         player_id: str, rank: int) -> str:
        """Determine player result with better handling"""
        result = ""
        
        if event_type == "league":
            # Try multiple ways to get wins
            wins = None
            
            # Method 1: wins.wins
            if "wins" in deck_data and isinstance(deck_data["wins"], dict):
                wins = str(deck_data["wins"].get("wins", ""))
            
            # Method 2: direct wins field
            elif "wins" in deck_data:
                wins = str(deck_data["wins"])
            
            # Method 3: record field
            elif "record" in deck_data:
                record = deck_data["record"]
                if isinstance(record, str) and "-" in record:
                    wins = record.split("-")[0]
            
            # Map wins to result
            if wins:
                result = {
                    "5": "5-0",
                    "4": "4-1",
                    "3": "3-2",
                    "2": "2-1",
                    "1": "1-2",
                    "0": "0-3"
                }.get(wins, f"{wins} wins")
            else:
                result = "Unknown"
                
        else:  # Tournament
            if winloss and player_id in winloss:
                result = winloss[player_id]
            else:
                # Use placement
                if rank == 1:
                    result = "1st Place"
                elif rank == 2:
                    result = "2nd Place"
                elif rank == 3:
                    result = "3rd Place"
                elif rank <= 8:
                    result = f"Top 8"
                elif rank <= 16:
                    result = f"Top 16"
                elif rank <= 32:
                    result = f"Top 32"
                else:
                    result = f"{rank}th Place"
        
        return result
    
    @staticmethod
    def parse_standing(json_data: dict, winloss: Optional[Dict[str, str]]) -> Optional[List[Standing]]:
        """Parse tournament standings with enhanced error handling"""
        if "standings" not in json_data:
            return None
        
        standings = []
        
        for standing_data in json_data["standings"]:
            try:
                player = standing_data.get("login_name", standing_data.get("player", "Unknown"))
                player_id = str(standing_data.get("loginid", ""))
                
                # Parse numeric fields with defaults
                points = int(standing_data.get("score", standing_data.get("points", 0)))
                rank = int(standing_data.get("rank", len(standings) + 1))
                
                # Parse percentage fields
                gwp = float(standing_data.get("gamewinpercentage", 0))
                ogwp = float(standing_data.get("opponentgamewinpercentage", 0))
                omwp = float(standing_data.get("opponentmatchwinpercentage", 0))
                
                # Get wins/losses
                wins = 0
                losses = 0
                draws = 0
                
                if winloss and player_id in winloss:
                    parts = winloss[player_id].split("-")
                    if len(parts) >= 2:
                        wins = int(parts[0])
                        losses = int(parts[1])
                        if len(parts) >= 3:
                            draws = int(parts[2])
                
                standings.append(Standing(
                    rank=rank,
                    player=player,
                    points=points,
                    wins=wins,
                    losses=losses,
                    draws=draws,
                    omwp=omwp,
                    gwp=gwp,
                    ogwp=ogwp
                ))
                
            except Exception as e:
                logger.error(f"Error parsing standing: {e}")
                continue
        
        return sorted(standings, key=lambda s: s.rank) if standings else None
    
    @staticmethod
    def parse_bracket(json_data: dict) -> Optional[List[Round]]:
        """Parse tournament bracket with enhanced error handling"""
        if "brackets" not in json_data:
            return None
        
        rounds = []
        
        for bracket in json_data["brackets"]:
            matches = []
            
            # Get round name if available
            round_name = bracket.get("round_name", "")
            
            for match in bracket.get("matches", []):
                try:
                    players = match.get("players", [])
                    if len(players) < 2:
                        logger.warning("Match has less than 2 players")
                        continue
                    
                    player1 = players[0].get("player", players[0].get("name", "Unknown"))
                    player2 = players[1].get("player", players[1].get("name", "Unknown"))
                    
                    player1_wins = int(players[0].get("wins", 0))
                    player2_wins = int(players[1].get("wins", 0))
                    
                    # Check for draws
                    player1_draws = int(players[0].get("draws", 0))
                    player2_draws = int(players[1].get("draws", 0))
                    draws = max(player1_draws, player2_draws)
                    
                    # Determine winner
                    reverse_order = players[1].get("winner", False)
                    
                    if reverse_order:
                        result = f"{player2_wins}-{player1_wins}"
                    else:
                        result = f"{player1_wins}-{player2_wins}"
                    
                    if draws > 0:
                        result += f"-{draws}"
                    
                    matches.append(RoundItem(
                        player1=player1 if not reverse_order else player2,
                        player2=player2 if not reverse_order else player1,
                        result=result
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing match: {e}")
                    continue
            
            if not matches:
                continue
            
            # Determine round name based on number of matches if not provided
            if not round_name:
                if len(matches) >= 4:
                    round_name = "Quarterfinals"
                elif len(matches) == 2:
                    round_name = "Semifinals"
                elif len(matches) == 1:
                    round_name = "Finals"
                else:
                    round_name = f"Round of {len(matches) * 2}"
            
            rounds.append(Round(
                round_name=round_name,
                matches=matches
            ))
        
        return rounds if rounds else None


def main():
    """Main function for testing"""
    logger.info("Starting MTGO scraper (Robust Version)")
    
    # Test with recent dates
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)
    
    # Create tournament list handler
    tournament_list = TournamentList()
    
    # Get tournament list
    tournaments = tournament_list.DL_tournaments(start_date, end_date)
    logger.info(f"Found {len(tournaments)} tournaments")
    
    # Show tournament type distribution
    type_counts = {}
    format_counts = {}
    
    for tournament in tournaments:
        type_counts[tournament.tournament_type] = type_counts.get(tournament.tournament_type, 0) + 1
        format_counts[tournament.formats] = format_counts.get(tournament.formats, 0) + 1
    
    logger.info("Tournament types found:")
    for t_type, count in sorted(type_counts.items()):
        logger.info(f"  {t_type}: {count}")
    
    logger.info("Formats found:")
    for fmt, count in sorted(format_counts.items()):
        logger.info(f"  {fmt}: {count}")
    
    # Get details for first few tournaments
    for tournament in tournaments[:3]:
        details = tournament_list.get_tournament_details(tournament)
        if details:
            logger.info(f"Successfully parsed {tournament.name} with {len(details.decks)} decks")
        else:
            logger.warning(f"Failed to parse {tournament.name}")


if __name__ == "__main__":
    main()