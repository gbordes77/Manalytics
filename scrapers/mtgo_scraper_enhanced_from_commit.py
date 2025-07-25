#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MTGO Tournament Scraper - Enhanced Version
Maximizes data extraction from MTGO while maintaining compatibility
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse
from urllib.parse import urljoin, urlparse
import os
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
import logging
import time
from pathlib import Path
import hashlib
from collections import Counter, defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CardMetadata:
    """Enhanced card information with additional metadata"""
    card_name: str
    mana_cost: Optional[str] = None
    card_type: Optional[str] = None
    rarity: Optional[str] = None
    set_code: Optional[str] = None


@dataclass
class DeckItem:
    """Enhanced deck item with metadata"""
    count: int
    card_name: str
    metadata: Optional[CardMetadata] = None


@dataclass
class DeckMetrics:
    """Calculated deck metrics for analysis"""
    total_cards: int
    unique_cards: int
    avg_cmc: Optional[float] = None
    color_identity: List[str] = field(default_factory=list)
    mana_curve: Dict[int, int] = field(default_factory=dict)
    card_types: Dict[str, int] = field(default_factory=dict)
    archetype_hints: List[str] = field(default_factory=list)


@dataclass
class Deck:
    """Enhanced deck with additional analysis"""
    date: datetime
    player: str
    result: str
    anchor_uri: str
    mainboard: List[DeckItem] = field(default_factory=list)
    sideboard: List[DeckItem] = field(default_factory=list)
    # New fields
    deck_name: Optional[str] = None
    archetype: Optional[str] = None
    metrics: Optional[DeckMetrics] = None
    performance_rating: Optional[float] = None  # Based on placement
    
    
@dataclass
class TournamentMetadata:
    """Additional tournament information"""
    total_players: Optional[int] = None
    rounds_played: Optional[int] = None
    top_cut_size: Optional[int] = None
    prize_pool: Optional[str] = None
    event_series: Optional[str] = None  # e.g., "MOCS", "Challenge", etc.
    

@dataclass
class Tournament:
    """Enhanced tournament with metadata"""
    name: str
    date: datetime
    uri: str
    formats: str
    tournament_type: str
    json_file: str
    force_redownload: bool = False
    # New fields
    metadata: Optional[TournamentMetadata] = None
    scraped_at: Optional[datetime] = None


@dataclass
class Standing:
    """Enhanced standing with additional stats"""
    rank: int
    player: str
    points: int
    wins: int
    losses: int
    draws: int
    omwp: float
    gwp: float
    ogwp: float
    # New fields
    match_points: Optional[int] = None
    game_points: Optional[int] = None
    matches_played: Optional[int] = None


@dataclass
class RoundItem:
    """Enhanced round item with more match details"""
    player1: str
    player2: str
    result: str
    # New fields
    winner: Optional[str] = None
    player1_wins: Optional[int] = None
    player2_wins: Optional[int] = None
    draws: Optional[int] = None
    match_id: Optional[str] = None


@dataclass
class Round:
    """Enhanced round with metadata"""
    round_name: str
    matches: List[RoundItem]
    # New fields
    round_number: Optional[int] = None
    is_elimination: bool = False
    
    
@dataclass
class PlayerStats:
    """Aggregate player statistics"""
    player_name: str
    tournaments_played: int = 0
    total_match_wins: int = 0
    total_match_losses: int = 0
    best_finish: Optional[int] = None
    avg_finish: Optional[float] = None
    preferred_archetypes: List[str] = field(default_factory=list)


@dataclass
class CacheItem:
    """Enhanced cache item with additional data"""
    tournament: Tournament
    decks: List[Deck]
    rounds: Optional[List[Round]] = None
    standings: Optional[List[Standing]] = None
    # New fields
    metagame_breakdown: Optional[Dict[str, float]] = None
    player_stats: Optional[List[PlayerStats]] = None


class MTGOEnhancedSettings:
    """Enhanced configuration for MTGO scraping"""
    LIST_URL = "https://www.mtgo.com/decklists/{year}/{month}"
    ROOT_URL = "https://www.mtgo.com"
    LEAGUE_REDOWNLOAD_DAYS = 3
    ValidFormats = ["Standard", "Modern", "Pioneer", "Legacy", "Vintage", "Pauper", "Commander"]
    
    # Tournament type patterns
    TOURNAMENT_PATTERNS = {
        "challenge": ["Challenge", "Weekend Challenge"],
        "league": ["League"],
        "trial": ["Last Chance", "Trial"],
        "qualifier": ["Qualifier", "PTQ", "RC", "RCQ", "RPTQ", "MCQ"],
        "showcase": ["Showcase", "Showcase Challenge", "Showcase Qualifier"],
        "championship": ["Championship", "Champs", "Finals", "MOCS"],
        "prelim": ["Prelim", "Preliminary"],
        "special": ["Special", "Festival", "Anniversary", "Celebration"],
        "other": []
    }
    
    # Archetype detection patterns
    ARCHETYPE_PATTERNS = {
        "Aggro": ["Goblin Guide", "Lightning Bolt", "Monastery Swiftspear"],
        "Control": ["Counterspell", "Teferi", "Supreme Verdict", "Wrath of God"],
        "Combo": ["Thassa's Oracle", "Splinter Twin", "Storm", "Grapeshot"],
        "Midrange": ["Thoughtseize", "Liliana", "Tarmogoyf"],
        "Ramp": ["Primeval Titan", "Cultivate", "Growth Spiral"],
        "Burn": ["Lightning Bolt", "Lava Spike", "Boros Charm"],
        "Mill": ["Hedron Crab", "Archive Trap", "Tasha's Hideous Laughter"],
        "Reanimator": ["Griselbrand", "Entomb", "Reanimate"],
    }
    
    @staticmethod
    def format_url(url, **params):
        return url.format(**params)


class TournamentTypeDetector:
    """Enhanced tournament type detection"""
    
    @staticmethod
    def detect_type(tournament_name: str) -> Tuple[str, Optional[str]]:
        """
        Detect tournament type and series from name
        Returns: (type, series)
        """
        name_lower = tournament_name.lower()
        
        # Check each pattern
        for type_name, patterns in MTGOEnhancedSettings.TOURNAMENT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    # Detect series
                    series = None
                    if "mocs" in name_lower:
                        series = "MOCS"
                    elif "showcase" in name_lower:
                        series = "Showcase"
                    elif "ptq" in name_lower or "pro tour" in name_lower:
                        series = "Pro Tour"
                    elif "rc" in name_lower or "regional" in name_lower:
                        series = "Regional Championship"
                    
                    return type_name, series
        
        return "other", None


class DeckAnalyzer:
    """Analyze decks for patterns and metrics"""
    
    @staticmethod
    def analyze_deck(deck: Deck) -> DeckMetrics:
        """Calculate comprehensive deck metrics"""
        metrics = DeckMetrics(
            total_cards=sum(item.count for item in deck.mainboard),
            unique_cards=len(deck.mainboard)
        )
        
        # Analyze card types
        for item in deck.mainboard:
            card_name = item.card_name.lower()
            
            # Simple type detection based on common patterns
            if "land" in card_name or card_name in ["island", "plains", "swamp", "mountain", "forest"]:
                metrics.card_types["Land"] = metrics.card_types.get("Land", 0) + item.count
            elif "creature" in card_name or any(x in card_name for x in ["knight", "wizard", "elemental", "beast"]):
                metrics.card_types["Creature"] = metrics.card_types.get("Creature", 0) + item.count
            elif any(x in card_name for x in ["instant", "flash"]):
                metrics.card_types["Instant"] = metrics.card_types.get("Instant", 0) + item.count
            elif "sorcery" in card_name:
                metrics.card_types["Sorcery"] = metrics.card_types.get("Sorcery", 0) + item.count
            elif any(x in card_name for x in ["enchantment", "aura"]):
                metrics.card_types["Enchantment"] = metrics.card_types.get("Enchantment", 0) + item.count
            elif "artifact" in card_name:
                metrics.card_types["Artifact"] = metrics.card_types.get("Artifact", 0) + item.count
            elif "planeswalker" in card_name:
                metrics.card_types["Planeswalker"] = metrics.card_types.get("Planeswalker", 0) + item.count
        
        # Detect color identity
        metrics.color_identity = DeckAnalyzer._detect_colors(deck)
        
        # Detect archetype hints
        metrics.archetype_hints = DeckAnalyzer._detect_archetype_hints(deck)
        
        return metrics
    
    @staticmethod
    def _detect_colors(deck: Deck) -> List[str]:
        """Detect deck colors based on cards"""
        colors = set()
        color_indicators = {
            "W": ["Plains", "White", "Selesnya", "Orzhov", "Boros", "Azorius"],
            "U": ["Island", "Blue", "Izzet", "Dimir", "Simic", "Azorius"],
            "B": ["Swamp", "Black", "Rakdos", "Golgari", "Dimir", "Orzhov"],
            "R": ["Mountain", "Red", "Gruul", "Rakdos", "Izzet", "Boros"],
            "G": ["Forest", "Green", "Simic", "Gruul", "Golgari", "Selesnya"]
        }
        
        for item in deck.mainboard:
            card_lower = item.card_name.lower()
            for color, indicators in color_indicators.items():
                if any(ind.lower() in card_lower for ind in indicators):
                    colors.add(color)
        
        return sorted(list(colors))
    
    @staticmethod
    def _detect_archetype_hints(deck: Deck) -> List[str]:
        """Detect potential archetypes based on key cards"""
        hints = []
        deck_cards = [item.card_name for item in deck.mainboard]
        
        for archetype, key_cards in MTGOEnhancedSettings.ARCHETYPE_PATTERNS.items():
            if any(card in deck_cards for card in key_cards):
                hints.append(archetype)
        
        return hints
    
    @staticmethod
    def calculate_performance_rating(placement: str) -> float:
        """Calculate a performance rating based on placement"""
        if "1st" in placement or placement == "5-0":
            return 1.0
        elif "2nd" in placement or placement == "4-1":
            return 0.9
        elif "3rd" in placement:
            return 0.85
        elif "4th" in placement:
            return 0.8
        elif "Top 8" in placement:
            return 0.75
        elif "3-2" in placement:
            return 0.6
        elif placement.endswith("th Place"):
            try:
                rank = int(placement.split("th")[0])
                return max(0.5, 1.0 - (rank / 100))
            except:
                return 0.5
        else:
            return 0.5


class MetagameAnalyzer:
    """Analyze tournament metagame"""
    
    @staticmethod
    def analyze_metagame(decks: List[Deck]) -> Dict[str, float]:
        """Calculate metagame breakdown by archetype"""
        if not decks:
            return {}
        
        archetype_counts = Counter()
        
        for deck in decks:
            if deck.archetype:
                archetype_counts[deck.archetype] += 1
            elif deck.metrics and deck.metrics.archetype_hints:
                # Use the most likely archetype hint
                archetype_counts[deck.metrics.archetype_hints[0]] += 1
            else:
                archetype_counts["Unknown"] += 1
        
        total_decks = len(decks)
        metagame = {
            archetype: (count / total_decks) * 100
            for archetype, count in archetype_counts.items()
        }
        
        return dict(sorted(metagame.items(), key=lambda x: x[1], reverse=True))


class CardNameNormalizer:
    """Enhanced card name normalization with caching"""
    _normalized_cache = {}
    _split_cards = {}
    
    @classmethod
    def initialize(cls):
        """Initialize normalization data"""
        if not cls._split_cards:
            # Common split cards
            cls._split_cards = {
                "Fire // Ice": "Fire // Ice",
                "Wear // Tear": "Wear // Tear",
                # Add more split cards as needed
            }
    
    @classmethod
    def normalize(cls, card_name: str) -> str:
        """Normalize card name with caching"""
        if card_name in cls._normalized_cache:
            return cls._normalized_cache[card_name]
        
        # Basic normalization
        normalized = card_name.strip()
        
        # Handle split cards
        if "//" in normalized:
            parts = normalized.split("//")
            normalized = " // ".join(part.strip() for part in parts)
        
        # Handle DFCs (double-faced cards)
        if " // " not in normalized and "/" in normalized:
            normalized = normalized.split("/")[0].strip()
        
        cls._normalized_cache[card_name] = normalized
        return normalized


class TournamentEnhancedLoader:
    """Enhanced tournament data loader with maximum data extraction"""
    
    @staticmethod
    def get_tournament_details(tournament: Tournament) -> Optional[CacheItem]:
        """Get enhanced tournament details"""
        try:
            response = requests.get(tournament.uri, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch tournament: {response.status_code}")
                return None
            
            html_content = response.text
            event_json = TournamentEnhancedLoader._extract_json_data(html_content)
            
            if not event_json:
                logger.error("No JSON data found in tournament page")
                return None
            
            # Extract all available data
            event_type = "tournament" if "starttime" in event_json else "league"
            
            # Parse enhanced tournament metadata
            tournament.metadata = TournamentEnhancedLoader._parse_metadata(event_json, html_content)
            tournament.scraped_at = datetime.now(timezone.utc)
            
            # Parse all components
            winloss = TournamentEnhancedLoader._parse_winloss(event_json) if event_type == "tournament" else None
            standings = TournamentEnhancedLoader._parse_standings(event_json, winloss) if event_type == "tournament" else None
            rounds = TournamentEnhancedLoader._parse_rounds(event_json) if event_type == "tournament" else None
            decks = TournamentEnhancedLoader._parse_decks(tournament, event_type, winloss, event_json)
            
            # Enhance decks with analysis
            if decks:
                for deck in decks:
                    deck.metrics = DeckAnalyzer.analyze_deck(deck)
                    deck.performance_rating = DeckAnalyzer.calculate_performance_rating(deck.result)
            
            # Calculate metagame breakdown
            metagame = MetagameAnalyzer.analyze_metagame(decks) if decks else None
            
            # Reorder decks based on standings
            if standings and decks:
                decks = TournamentEnhancedLoader._reorder_decks(decks, standings, rounds)
            
            return CacheItem(
                tournament=tournament,
                decks=decks,
                rounds=rounds,
                standings=standings,
                metagame_breakdown=metagame
            )
            
        except Exception as e:
            logger.error(f"Error loading tournament details: {e}")
            return None
    
    @staticmethod
    def _extract_json_data(html_content: str) -> Optional[Dict]:
        """Extract JSON data from HTML"""
        html_rows = [line.strip() for line in html_content.splitlines()]
        data_row = next(
            (line for line in html_rows if line.startswith("window.MTGO.decklists.data = ")),
            None
        )
        
        if not data_row:
            return None
        
        json_data = data_row[29:-1]  # Remove prefix and semicolon
        return json.loads(json_data)
    
    @staticmethod
    def _parse_metadata(event_json: Dict, html_content: str) -> TournamentMetadata:
        """Parse enhanced tournament metadata"""
        metadata = TournamentMetadata()
        
        # Extract from JSON
        if "totalplayers" in event_json:
            metadata.total_players = int(event_json["totalplayers"])
        elif "decklists" in event_json:
            metadata.total_players = len(event_json["decklists"])
        
        # Parse HTML for additional info
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for tournament info sections
        info_sections = soup.find_all(['div', 'section'], class_=re.compile('tournament|event|info'))
        for section in info_sections:
            text = section.get_text()
            
            # Extract rounds
            rounds_match = re.search(r'(\d+)\s*rounds?', text, re.IGNORECASE)
            if rounds_match:
                metadata.rounds_played = int(rounds_match.group(1))
            
            # Extract top cut
            topcut_match = re.search(r'top\s*(\d+)', text, re.IGNORECASE)
            if topcut_match:
                metadata.top_cut_size = int(topcut_match.group(1))
        
        return metadata
    
    @staticmethod
    def _parse_winloss(event_json: Dict) -> Optional[Dict[str, str]]:
        """Parse win/loss records"""
        if "winloss" not in event_json:
            return None
        
        player_winloss = {}
        for winloss in event_json["winloss"]:
            player_id = str(winloss["loginid"])
            wins = winloss["wins"]
            losses = winloss["losses"]
            player_winloss[player_id] = f"{wins}-{losses}"
        
        return player_winloss if player_winloss else None
    
    @staticmethod
    def _parse_standings(event_json: Dict, winloss: Optional[Dict]) -> Optional[List[Standing]]:
        """Parse enhanced standings"""
        if "standings" not in event_json:
            return None
        
        standings = []
        for standing_data in event_json["standings"]:
            standing = Standing(
                rank=int(standing_data["rank"]),
                player=standing_data["login_name"],
                points=int(standing_data["score"]),
                wins=0,
                losses=0,
                draws=0,
                omwp=float(standing_data.get("opponentmatchwinpercentage", 0)),
                gwp=float(standing_data.get("gamewinpercentage", 0)),
                ogwp=float(standing_data.get("opponentgamewinpercentage", 0))
            )
            
            # Add win/loss from winloss data
            player_id = str(standing_data["loginid"])
            if winloss and player_id in winloss:
                parts = winloss[player_id].split("-")
                standing.wins = int(parts[0])
                standing.losses = int(parts[1])
            
            # Calculate additional stats
            standing.matches_played = standing.wins + standing.losses + standing.draws
            if standing.matches_played > 0:
                standing.match_points = standing.wins * 3 + standing.draws
            
            standings.append(standing)
        
        return sorted(standings, key=lambda s: s.rank) if standings else None
    
    @staticmethod
    def _parse_rounds(event_json: Dict) -> Optional[List[Round]]:
        """Parse enhanced round/bracket data"""
        if "brackets" not in event_json:
            return None
        
        rounds = []
        round_number = 1
        
        for bracket in event_json["brackets"]:
            matches = []
            
            for match in bracket["matches"]:
                player1_data = match["players"][0]
                player2_data = match["players"][1]
                
                round_item = RoundItem(
                    player1=player1_data["player"],
                    player2=player2_data["player"],
                    result=f"{player1_data['wins']}-{player2_data['wins']}-0",
                    player1_wins=player1_data["wins"],
                    player2_wins=player2_data["wins"],
                    draws=0
                )
                
                # Determine winner
                if player1_data.get("winner"):
                    round_item.winner = round_item.player1
                elif player2_data.get("winner"):
                    round_item.winner = round_item.player2
                
                # Generate match ID
                round_item.match_id = hashlib.md5(
                    f"{round_number}_{round_item.player1}_{round_item.player2}".encode()
                ).hexdigest()[:8]
                
                matches.append(round_item)
            
            # Determine round name and type
            round_name = "Quarterfinals"
            is_elimination = True
            
            if len(matches) == 2:
                round_name = "Semifinals"
            elif len(matches) == 1:
                round_name = "Finals"
            
            rounds.append(Round(
                round_name=round_name,
                matches=matches,
                round_number=round_number,
                is_elimination=is_elimination
            ))
            
            round_number += 1
        
        return rounds if rounds else None
    
    @staticmethod
    def _parse_decks(tournament: Tournament, event_type: str, 
                    winloss: Optional[Dict], event_json: Dict) -> Optional[List[Deck]]:
        """Parse enhanced deck data"""
        if "decklists" not in event_json:
            return None
        
        # Initialize normalizer
        CardNameNormalizer.initialize()
        
        # Parse event date
        event_date_str = event_json.get("publish_date") if event_type == "league" else event_json.get("starttime")
        event_date = TournamentEnhancedLoader._parse_date(event_date_str)
        
        decks = []
        rank = 1
        
        for deck_data in event_json["decklists"]:
            # Parse basic info
            player = deck_data.get("player", "Unknown")
            player_id = str(deck_data.get("loginid", ""))
            
            # Parse cards
            mainboard = []
            sideboard = []
            
            for card in deck_data.get("main_deck", []):
                card_attrs = card["card_attributes"]
                normalized_name = CardNameNormalizer.normalize(card_attrs["card_name"])
                
                # Create enhanced deck item
                deck_item = DeckItem(
                    count=int(card["qty"]),
                    card_name=normalized_name,
                    metadata=CardMetadata(
                        card_name=normalized_name,
                        mana_cost=card_attrs.get("mana_cost"),
                        card_type=card_attrs.get("card_type"),
                        rarity=card_attrs.get("rarity"),
                        set_code=card_attrs.get("set")
                    )
                )
                mainboard.append(deck_item)
            
            for card in deck_data.get("sideboard_deck", []):
                card_attrs = card["card_attributes"]
                normalized_name = CardNameNormalizer.normalize(card_attrs["card_name"])
                
                deck_item = DeckItem(
                    count=int(card["qty"]),
                    card_name=normalized_name,
                    metadata=CardMetadata(
                        card_name=normalized_name,
                        mana_cost=card_attrs.get("mana_cost"),
                        card_type=card_attrs.get("card_type"),
                        rarity=card_attrs.get("rarity"),
                        set_code=card_attrs.get("set")
                    )
                )
                sideboard.append(deck_item)
            
            # Determine result
            result = TournamentEnhancedLoader._determine_result(
                event_type, deck_data, winloss, player_id, rank
            )
            
            # Create enhanced deck
            deck = Deck(
                date=event_date,
                player=player,
                result=result,
                anchor_uri=f"{tournament.uri}#deck_{player}",
                mainboard=mainboard,
                sideboard=sideboard
            )
            
            # Try to detect deck name/archetype from deck data
            if "deck_name" in deck_data:
                deck.deck_name = deck_data["deck_name"]
            
            decks.append(deck)
            rank += 1
        
        return decks if decks else None
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse various date formats"""
        try:
            # Try full datetime format
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                # Try date only format
                return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                # Try ISO format
                return isoparse(date_str).replace(tzinfo=timezone.utc)
    
    @staticmethod
    def _determine_result(event_type: str, deck_data: Dict, 
                         winloss: Optional[Dict], player_id: str, rank: int) -> str:
        """Determine player result with enhanced logic"""
        if event_type == "league":
            wins = deck_data.get("wins", {}).get("wins", "0")
            return {
                "5": "5-0", "4": "4-1", "3": "3-2",
                "2": "2-1", "1": "1-4", "0": "0-5"
            }.get(wins, f"{wins} wins")
        else:
            if winloss and player_id in winloss:
                return winloss[player_id]
            else:
                # Enhanced placement strings
                if rank == 1:
                    return "1st Place (Champion)"
                elif rank == 2:
                    return "2nd Place (Finalist)"
                elif rank == 3:
                    return "3rd Place"
                elif rank == 4:
                    return "4th Place"
                elif rank <= 8:
                    return f"{rank}th Place (Top 8)"
                else:
                    return f"{rank}th Place"
    
    @staticmethod
    def _reorder_decks(decks: List[Deck], standings: List[Standing], 
                      rounds: Optional[List[Round]]) -> List[Deck]:
        """Reorder decks based on standings with enhanced logic"""
        # Create player to deck mapping
        player_deck_map = {deck.player: deck for deck in decks}
        
        # Reorder based on standings
        ordered_decks = []
        for standing in standings:
            if standing.player in player_deck_map:
                ordered_decks.append(player_deck_map[standing.player])
        
        # Add any remaining decks
        for deck in decks:
            if deck not in ordered_decks:
                ordered_decks.append(deck)
        
        return ordered_decks


class TournamentTracker:
    """Track processed tournaments with enhanced metadata"""
    
    def __init__(self, tracker_file: str = "data/raw/mtgo/.processed_tournaments_enhanced.json"):
        self.tracker_file = Path(tracker_file)
        self.processed: Dict[str, Dict] = {}
        self.load()
    
    def load(self):
        """Load processed tournament data"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    self.processed = data.get('processed', {})
                logger.info(f"Loaded {len(self.processed)} processed tournaments")
            except Exception as e:
                logger.error(f"Error loading tracker file: {e}")
    
    def save(self):
        """Save processed tournament data"""
        try:
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_file, 'w') as f:
                json.dump({
                    'processed': self.processed,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracker file: {e}")
    
    def is_processed(self, tournament_id: str) -> bool:
        """Check if tournament was already processed"""
        return tournament_id in self.processed
    
    def mark_processed(self, tournament_id: str, metadata: Dict):
        """Mark tournament as processed with metadata"""
        self.processed[tournament_id] = {
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata
        }
        self.save()


class MTGOEnhancedScraper:
    """Enhanced MTGO scraper with maximum data extraction
    
    IMPORTANT: Tournament ID Handling
    =================================
    MTGO tournament IDs are NOT sequential or predictable. Never try to guess IDs.
    
    Example of wrong approach:
    - Found: 12803688, assumed next would be 12803689 ❌
    - Reality: Next was 12803671 (different by 17!)
    
    Correct approach:
    - Always parse the official listing page: https://www.mtgo.com/decklists
    - Extract ALL tournament URLs from the HTML
    - The scraper handles duplicates by using unique IDs in filenames
    
    This is why we parse the listing page first, then fetch individual tournaments.
    """
    
    def __init__(self):
        self.tracker = TournamentTracker()
    
    def scrape_tournaments(self, start_date: datetime, end_date: datetime = None,
                          format_filter: str = None, tournament_types: List[str] = None,
                          skip_processed: bool = True) -> List[CacheItem]:
        """Scrape tournaments with enhanced data extraction"""
        
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        logger.info(f"Scraping MTGO tournaments from {start_date.date()} to {end_date.date()}")
        
        # Get tournament list
        tournaments = self._get_tournament_list(start_date, end_date)
        logger.info(f"Found {len(tournaments)} tournaments")
        
        # Filter tournaments
        filtered = self._filter_tournaments(tournaments, format_filter, tournament_types)
        logger.info(f"Filtered to {len(filtered)} tournaments")
        
        # Process each tournament
        results = []
        for i, tournament in enumerate(filtered):
            try:
                logger.info(f"Processing {i+1}/{len(filtered)}: {tournament.name}")
                
                # Check if already processed
                tournament_id = self._get_tournament_id(tournament)
                if skip_processed and self.tracker.is_processed(tournament_id):
                    logger.info(f"Skipping already processed: {tournament.name}")
                    continue
                
                # Load tournament details
                cache_item = TournamentEnhancedLoader.get_tournament_details(tournament)
                
                if cache_item and cache_item.decks:
                    results.append(cache_item)
                    
                    # Mark as processed
                    self.tracker.mark_processed(tournament_id, {
                        'name': tournament.name,
                        'format': tournament.formats,
                        'type': tournament.tournament_type,
                        'decks': len(cache_item.decks),
                        'has_standings': cache_item.standings is not None,
                        'has_rounds': cache_item.rounds is not None
                    })
                    
                    logger.info(f"✅ Scraped {len(cache_item.decks)} decks")
                else:
                    logger.warning(f"No decks found for: {tournament.name}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {tournament.name}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(results)} tournaments")
        return results
    
    def _get_tournament_list(self, start_date: datetime, end_date: datetime) -> List[Tournament]:
        """Get list of tournaments with enhanced metadata"""
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            month_url = MTGOEnhancedSettings.format_url(
                MTGOEnhancedSettings.LIST_URL,
                year=current_date.year,
                month=f"{current_date.month:02}"
            )
            
            try:
                response = requests.get(month_url, timeout=30)
                if response.status_code != 200:
                    current_date = self._increment_month(current_date)
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                tournament_nodes = soup.select("li.decklists-item")
                
                for node in tournament_nodes:
                    tournament = self._parse_tournament_node(node)
                    if tournament and start_date.date() <= tournament.date.date() <= end_date.date():
                        results.append(tournament)
                
            except Exception as e:
                logger.error(f"Error fetching tournaments for {current_date.strftime('%Y-%m')}: {e}")
            
            current_date = self._increment_month(current_date)
        
        return sorted(results, key=lambda t: t.date, reverse=True)
    
    def _parse_tournament_node(self, node) -> Optional[Tournament]:
        """Parse tournament from HTML node with enhanced detection"""
        try:
            title = node.select_one("a > div > h3").text.strip()
            url = node.select_one("a")["href"]
            date_string = node.select_one("a > time")["datetime"]
            
            parsed_date = isoparse(date_string)
            if not parsed_date.tzinfo:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            
            url = urljoin(MTGOEnhancedSettings.ROOT_URL, url)
            
            # Enhanced format detection
            base_format = title.split()[0]
            format_name = 'Commander' if base_format == 'Duel' else base_format
            
            if format_name not in MTGOEnhancedSettings.ValidFormats:
                # Try to extract format from title
                for valid_format in MTGOEnhancedSettings.ValidFormats:
                    if valid_format.lower() in title.lower():
                        format_name = valid_format
                        break
                else:
                    format_name = None
            
            # Detect tournament type and series
            tournament_type, series = TournamentTypeDetector.detect_type(title)
            
            tournament = Tournament(
                name=title,
                date=parsed_date,
                uri=url,
                formats=format_name,
                tournament_type=tournament_type,
                json_file=os.path.splitext(os.path.basename(url))[0] + ".json",
                force_redownload=("league" in title.lower() and 
                                (datetime.now(timezone.utc) - parsed_date).days < MTGOEnhancedSettings.LEAGUE_REDOWNLOAD_DAYS)
            )
            
            # Add metadata if series detected
            if series:
                tournament.metadata = TournamentMetadata(event_series=series)
            
            return tournament
            
        except Exception as e:
            logger.error(f"Error parsing tournament node: {e}")
            return None
    
    def _filter_tournaments(self, tournaments: List[Tournament], 
                          format_filter: str = None,
                          tournament_types: List[str] = None) -> List[Tournament]:
        """Filter tournaments based on criteria"""
        filtered = tournaments
        
        # Filter by format
        if format_filter:
            filtered = [t for t in filtered if t.formats and t.formats.lower() == format_filter.lower()]
        
        # Filter by tournament type
        if tournament_types:
            filtered = [t for t in filtered if t.tournament_type in tournament_types]
        
        return filtered
    
    def _get_tournament_id(self, tournament: Tournament) -> str:
        """Generate unique tournament ID"""
        return hashlib.md5(f"{tournament.uri}_{tournament.date}".encode()).hexdigest()
    
    def _increment_month(self, date: datetime) -> datetime:
        """Increment month handling year rollover"""
        new_month = date.month + 1
        new_year = date.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        return date.replace(year=new_year, month=new_month, day=1)