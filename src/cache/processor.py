"""
Cache processor - processes raw tournament data and creates optimized cache.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from ..parsers.color_detector import ColorDetector
from ..parsers.archetype_parser import ArchetypeParser
from .database import CacheDatabase
from .models import CachedTournament, CachedDecklist, CachedCard
from ..utils.color_names import format_archetype_name


logger = logging.getLogger(__name__)


class CacheProcessor:
    """Processes raw tournament data into optimized cache"""
    
    def __init__(self, raw_data_path: Path = None, cache_path: Path = None):
        """Initialize processor with paths"""
        self.raw_data_path = raw_data_path or Path("data/raw")
        self.cache_path = cache_path or Path("data/cache")
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.db = CacheDatabase(self.cache_path / "tournaments.db")
        self.color_detector = ColorDetector()
        self.archetype_parser = ArchetypeParser()
        
        # Create subdirectories
        (self.cache_path / "decklists").mkdir(exist_ok=True)
        (self.cache_path / "archetypes").mkdir(exist_ok=True)
        (self.cache_path / "meta_snapshots").mkdir(exist_ok=True)
    
    def process_all_new(self):
        """Process all new tournaments not yet in cache"""
        logger.info("Starting cache processing...")
        
        # Find new tournaments
        new_tournaments = self._find_new_tournaments()
        logger.info(f"Found {len(new_tournaments)} new tournaments to process")
        
        # Process each tournament
        for tournament_file in new_tournaments:
            self.process_tournament(tournament_file)
    
    def process_tournament(self, tournament_file: Path):
        """Process a single tournament file"""
        
        # PERMANENT LEAGUE FILTER - Skip ANY file with "league" in the name
        if "league" in str(tournament_file).lower():
            logger.warning(f"⚠️ SKIPPING LEAGUE: {tournament_file.name} - Leagues are permanently excluded")
            return
        
        logger.info(f"Processing tournament: {tournament_file}")
        
        try:
            # Load tournament data
            with open(tournament_file, 'r') as f:
                data = json.load(f)
            
            # Determine platform
            platform = "mtgo" if "mtgo" in str(tournament_file) else "melee"
            
            # Create tournament metadata
            tournament = self._create_tournament_metadata(data, tournament_file, platform)
            
            # Process decklists
            decklists = self._process_decklists(data, tournament.id, platform)
            
            # Save to cache
            self._save_to_cache(tournament, decklists)
            
            # Update database
            tournament.processed_at = datetime.now()
            tournament.colors_detected = True
            tournament.archetypes_detected = True
            self.db.insert_tournament(tournament)
            
            logger.info(f"✓ Processed {len(decklists)} decks from {tournament.name}")
            
        except Exception as e:
            logger.error(f"Error processing {tournament_file}: {e}")
    
    def _find_new_tournaments(self) -> List[Path]:
        """Find tournament files not yet processed"""
        new_files = []
        
        # Check MTGO tournaments
        mtgo_dir = self.raw_data_path / "mtgo"
        if mtgo_dir.exists():
            for format_dir in mtgo_dir.iterdir():
                if format_dir.is_dir():
                    # Check main directory
                    for json_file in format_dir.glob("*.json"):
                        # PERMANENT FILTER: Skip leagues
                        if "league" in json_file.name.lower():
                            continue
                        if not self._is_processed(json_file):
                            new_files.append(json_file)
                    
                    # Check subdirectories
                    for subdir in format_dir.iterdir():
                        if subdir.is_dir():
                            # Skip 'leagues' subdirectories entirely
                            if subdir.name.lower() == "leagues":
                                continue
                            for json_file in subdir.glob("*.json"):
                                # PERMANENT FILTER: Skip leagues
                                if "league" in json_file.name.lower():
                                    continue
                                if not self._is_processed(json_file):
                                    new_files.append(json_file)
        
        # Check Melee tournaments
        melee_dir = self.raw_data_path / "melee"
        if melee_dir.exists():
            for format_dir in melee_dir.iterdir():
                if format_dir.is_dir():
                    for json_file in format_dir.glob("*.json"):
                        if not self._is_processed(json_file):
                            new_files.append(json_file)
        
        return new_files
    
    def _is_processed(self, file_path: Path) -> bool:
        """Check if tournament is already processed"""
        # Generate tournament ID from file path
        tournament_id = self._generate_tournament_id(file_path)
        tournament = self.db.get_tournament(tournament_id)
        return tournament is not None and tournament.archetypes_detected
    
    def _create_tournament_metadata(self, data: Dict, file_path: Path, platform: str) -> CachedTournament:
        """Create tournament metadata from raw data"""
        if platform == "mtgo":
            # Check new format first
            if 'tournament_id' in data:
                # New simplified format
                return CachedTournament(
                    id=data.get('tournament_id', self._generate_tournament_id(file_path)),
                    platform=platform,
                    format=data.get('format', 'standard').lower(),
                    type=data.get('tournament_type', 'tournament'),
                    name=data.get('name', ''),
                    date=datetime.strptime(data.get('date', ''), '%Y-%m-%d'),
                    players=data.get('total_players', 0),
                    raw_file=str(file_path),
                    cache_file=None
                )
            else:
                # Old format with TournamentInfo
                tournament_info = data.get('TournamentInfo', {})
                date_str = tournament_info.get('Date', '')
                if date_str:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    # Extract from filename as fallback
                    date = datetime.strptime(file_path.stem.split('_')[0], '%Y-%m-%d')
                
                return CachedTournament(
                    id=self._generate_tournament_id(file_path),
                    platform=platform,
                    format=tournament_info.get('Format', 'standard').lower(),
                    type=self._extract_tournament_type(tournament_info.get('Name', '')),
                    name=tournament_info.get('Name', ''),
                    date=date,
                    players=len(data.get('Standings', [])),
                    raw_file=str(file_path),
                    cache_file=None
                )
        else:
            # Melee format
            return CachedTournament(
                id=self._generate_tournament_id(file_path),
                platform=platform,
                format=data.get('FormatDescription', 'Standard').lower(),
                type="tournament",
                name=data.get('TournamentName', ''),
                date=datetime.fromisoformat(data.get('TournamentStartDate', '').replace('Z', '+00:00')),
                players=data.get('TotalPlayers', 0),
                raw_file=str(file_path),
                cache_file=None
            )
    
    def _process_decklists(self, data: Dict, tournament_id: str, platform: str) -> List[CachedDecklist]:
        """Process all decklists in a tournament"""
        decklists = []
        
        if platform == "mtgo":
            # Check format - new format uses 'decklists', old uses 'Decks'
            decks_key = 'decklists' if 'decklists' in data else 'Decks'
            for deck_data in data.get(decks_key, []):
                decklist = self._process_mtgo_deck(deck_data, tournament_id)
                if decklist:
                    decklists.append(decklist)
        else:
            # Melee format
            for deck_data in data.get('Decks', []):
                decklist = self._process_melee_deck(deck_data, tournament_id)
                if decklist:
                    decklists.append(decklist)
        
        return decklists
    
    def _process_mtgo_deck(self, deck_data: Dict, tournament_id: str) -> Optional[CachedDecklist]:
        """Process single MTGO deck"""
        try:
            # Check format - new format uses lowercase keys
            if 'mainboard' in deck_data:
                # New format
                mainboard = [
                    CachedCard(name=card['card_name'], count=card['count'])
                    for card in deck_data.get('mainboard', [])
                ]
                sideboard = [
                    CachedCard(name=card['card_name'], count=card['count'])
                    for card in deck_data.get('sideboard', [])
                ]
                
                # Convert for color/archetype detection
                mainboard_for_detect = [
                    {'CardName': card['card_name'], 'Count': card['count']}
                    for card in deck_data.get('mainboard', [])
                ]
                sideboard_for_detect = [
                    {'CardName': card['card_name'], 'Count': card['count']}
                    for card in deck_data.get('sideboard', [])
                ]
                
                # Extract result for rank/wins/losses
                result = deck_data.get('result', '0-0')
                wins, losses = map(int, result.split('-')) if '-' in result else (0, 0)
                
                player = deck_data.get('player', '')
                deck_id = f"{tournament_id}_{player}"
                
            else:
                # Old format
                mainboard = [
                    CachedCard(name=card['CardName'], count=card['Count'])
                    for card in deck_data.get('Mainboard', [])
                ]
                sideboard = [
                    CachedCard(name=card['CardName'], count=card['Count'])
                    for card in deck_data.get('Sideboard', [])
                ]
                
                mainboard_for_detect = deck_data.get('Mainboard', [])
                sideboard_for_detect = deck_data.get('Sideboard', [])
                
                player = deck_data.get('Player', '')
                deck_id = deck_data.get('DeckId', f"{tournament_id}_{player}")
                wins = deck_data.get('Wins', 0)
                losses = deck_data.get('Losses', 0)
            
            # Detect colors
            colors = self.color_detector.detect_colors(
                mainboard_for_detect,
                sideboard_for_detect
            )
            
            # Detect companion
            companion = self.color_detector.detect_companion(sideboard_for_detect)
            
            # Detect archetype
            archetype, variant = self.archetype_parser.detect_archetype(
                mainboard_for_detect,
                sideboard_for_detect,
                colors
            )
            
            # Format archetype name with full color names and variant
            if archetype:
                # The archetype already includes the color code, don't pass colors again
                archetype_name = format_archetype_name(archetype)
                if variant:
                    archetype_name = f"{archetype_name} ({variant})"
            else:
                archetype_name = None
            
            return CachedDecklist(
                deck_id=deck_id,
                tournament_id=tournament_id,
                player=player,
                rank=deck_data.get('Rank', deck_data.get('rank', 0)),
                wins=wins,
                losses=losses,
                deck_name=deck_data.get('DeckName', deck_data.get('deck_name')),
                archetype=archetype_name,
                colors=colors,
                companion=companion,
                mainboard=mainboard,
                sideboard=sideboard,
                cached_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error processing MTGO deck: {e}")
            return None
    
    def _process_melee_deck(self, deck_data: Dict, tournament_id: str) -> Optional[CachedDecklist]:
        """Process single Melee deck"""
        try:
            # Extract cards
            mainboard = [
                CachedCard(name=card['CardName'], count=card['Count'])
                for card in deck_data.get('Mainboard', [])
            ]
            sideboard = [
                CachedCard(name=card['CardName'], count=card['Count'])
                for card in deck_data.get('Sideboard', [])
            ]
            
            # Detect colors
            colors = self.color_detector.detect_colors(
                deck_data.get('Mainboard', []),
                deck_data.get('Sideboard', [])
            )
            
            # Detect companion
            companion = self.color_detector.detect_companion(deck_data.get('Sideboard', []))
            
            # Detect archetype
            archetype, variant = self.archetype_parser.detect_archetype(
                deck_data.get('Mainboard', []),
                deck_data.get('Sideboard', []),
                colors
            )
            
            # Format archetype name with full color names and variant
            if archetype:
                # The archetype already includes the color code, don't pass colors again
                archetype_name = format_archetype_name(archetype)
                if variant:
                    archetype_name = f"{archetype_name} ({variant})"
            else:
                archetype_name = None
            
            return CachedDecklist(
                deck_id=deck_data.get('DeckId', ''),
                tournament_id=tournament_id,
                player=deck_data.get('PlayerName', ''),
                rank=deck_data.get('Rank', 0),
                wins=deck_data.get('Wins', 0),
                losses=deck_data.get('Losses', 0),
                deck_name=deck_data.get('DeckName'),
                archetype=archetype_name,
                colors=colors,
                companion=companion,
                mainboard=mainboard,
                sideboard=sideboard,
                cached_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error processing Melee deck: {e}")
            return None
    
    def _save_to_cache(self, tournament: CachedTournament, decklists: List[CachedDecklist]):
        """Save processed data to cache files"""
        # Determine month for partitioning
        month_key = tournament.date.strftime("%Y-%m")
        
        # Save decklists to JSON (simpler than Parquet for now)
        decklists_file = self.cache_path / "decklists" / f"{month_key}.json"
        
        # Load existing data if file exists
        existing_data = {}
        if decklists_file.exists():
            with open(decklists_file, 'r') as f:
                existing_data = json.load(f)
        
        # Add new tournament data
        tournament_data = {
            'tournament_id': tournament.id,
            'date': tournament.date.isoformat(),
            'format': tournament.format,
            'platform': tournament.platform,
            'decklists': [deck.to_dict() for deck in decklists]
        }
        
        existing_data[tournament.id] = tournament_data
        
        # Save back to JSON
        with open(decklists_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        tournament.cache_file = str(decklists_file)
        
        # Save archetype summary
        archetypes_file = self.cache_path / "archetypes" / f"{month_key}.json"
        archetype_summary = self._create_archetype_summary(tournament.id, decklists)
        
        if archetypes_file.exists():
            with open(archetypes_file, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        existing_data[tournament.id] = archetype_summary
        
        with open(archetypes_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def _create_archetype_summary(self, tournament_id: str, decklists: List[CachedDecklist]) -> Dict:
        """Create archetype distribution summary"""
        summary = {
            'tournament_id': tournament_id,
            'total_decks': len(decklists),
            'archetypes': {},
            'colors': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Count archetypes
        for deck in decklists:
            if deck.archetype:
                if deck.archetype not in summary['archetypes']:
                    summary['archetypes'][deck.archetype] = 0
                summary['archetypes'][deck.archetype] += 1
            
            if deck.colors:
                if deck.colors not in summary['colors']:
                    summary['colors'][deck.colors] = 0
                summary['colors'][deck.colors] += 1
        
        return summary
    
    def _generate_tournament_id(self, file_path: Path) -> str:
        """Generate unique tournament ID from file path"""
        # Use filename without extension as ID
        return file_path.stem
    
    def _extract_tournament_type(self, tournament_name: str) -> str:
        """Extract tournament type from name"""
        name_lower = tournament_name.lower()
        if 'challenge' in name_lower:
            return 'challenge'
        elif 'league' in name_lower:
            return 'league'
        elif 'qualifier' in name_lower:
            return 'qualifier'
        else:
            return 'tournament'