"""
Tournament Matcher - Matches listener match data with our tournament data.

This module is responsible for matching Jiliac listener match data (by tournament ID)
with our scraped tournament data to create a unified dataset.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class TournamentMatcher:
    """Matches listener match data with tournament data by ID"""
    
    def __init__(self, data_path: Path = None):
        """Initialize the matcher with data paths"""
        self.data_path = data_path or Path("data")
        self.listener_path = self.data_path / "listener" / "daily_jsons"
        self.raw_path = self.data_path / "raw"
        self.cache_path = self.data_path / "cache"
        
    def match_by_id(self, tournament_id: int) -> Optional[Dict]:
        """
        Match a tournament ID from listener data with our tournament data.
        
        Example:
        - Listener has: {"Id": 12801654}
        - We have: "Standard Challenge 32 (12801654)_2025-07-05.json"
        
        Args:
            tournament_id: The tournament ID from listener data
            
        Returns:
            Matched tournament data or None if not found
        """
        logger.info(f"Matching tournament ID: {tournament_id}")
        
        # Search in MTGO data
        mtgo_match = self._search_mtgo_tournaments(tournament_id)
        if mtgo_match:
            return mtgo_match
            
        # Search in Melee data (if they have IDs)
        melee_match = self._search_melee_tournaments(tournament_id)
        if melee_match:
            return melee_match
            
        logger.warning(f"No match found for tournament ID: {tournament_id}")
        return None
    
    def _search_mtgo_tournaments(self, tournament_id: int) -> Optional[Dict]:
        """Search MTGO tournaments for matching ID"""
        mtgo_path = self.raw_path / "mtgo"
        
        for format_dir in mtgo_path.iterdir():
            if not format_dir.is_dir():
                continue
                
            # Search in format directory
            for json_file in format_dir.glob("**/*.json"):
                # Skip leagues
                if "league" in json_file.name.lower():
                    continue
                    
                # Check if ID is in filename (MTGO pattern)
                if f"({tournament_id})" in json_file.name:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        return {
                            "file_path": str(json_file),
                            "tournament_id": tournament_id,
                            "format": format_dir.name,
                            "platform": "mtgo",
                            "data": data
                        }
                    except Exception as e:
                        logger.error(f"Error reading {json_file}: {e}")
                        
        return None
    
    def _search_melee_tournaments(self, tournament_id: int) -> Optional[Dict]:
        """Search Melee tournaments for matching ID"""
        melee_path = self.raw_path / "melee"
        
        # Melee might not have IDs in the same format
        # This is a placeholder for future implementation
        return None
    
    def get_listener_matches(self, date_range: Tuple[datetime, datetime]) -> List[Dict]:
        """
        Get all listener matches within a date range.
        
        Args:
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            List of match data from listener files
        """
        matches = []
        start_date, end_date = date_range
        
        if not self.listener_path.exists():
            logger.warning(f"Listener path does not exist: {self.listener_path}")
            return matches
        
        # Iterate through daily folders
        for day_folder in self.listener_path.iterdir():
            if not day_folder.is_dir():
                continue
                
            # Parse date from folder name (assuming YYYY-MM-DD format)
            try:
                folder_date = datetime.strptime(day_folder.name, "%Y-%m-%d")
                if not (start_date <= folder_date <= end_date):
                    continue
            except ValueError:
                logger.warning(f"Invalid date folder format: {day_folder.name}")
                continue
            
            # Read all match files in the folder
            for match_file in day_folder.glob("match_*.json"):
                try:
                    with open(match_file, 'r') as f:
                        match_data = json.load(f)
                        
                    # Only include Standard matches
                    if match_data.get('format', '').lower() == 'standard':
                        matches.append(match_data)
                        
                except Exception as e:
                    logger.error(f"Error reading match file {match_file}: {e}")
        
        logger.info(f"Found {len(matches)} Standard matches in date range")
        return matches
    
    def match_all_listener_data(self, date_range: Tuple[datetime, datetime]) -> Dict[int, Dict]:
        """
        Match all listener data with tournament data for a date range.
        
        Returns:
            Dictionary mapping tournament_id to enriched tournament data
        """
        matches = self.get_listener_matches(date_range)
        tournament_matches = {}
        
        # Group matches by tournament ID
        for match in matches:
            tournament_id = match.get('tournament_id')
            if not tournament_id:
                continue
                
            if tournament_id not in tournament_matches:
                # First time seeing this tournament, try to match it
                tournament_data = self.match_by_id(tournament_id)
                if tournament_data:
                    tournament_data['matches'] = []
                    tournament_matches[tournament_id] = tournament_data
            
            # Add match to tournament
            if tournament_id in tournament_matches:
                tournament_matches[tournament_id]['matches'].append(match)
        
        logger.info(f"Matched {len(tournament_matches)} tournaments with listener data")
        return tournament_matches
    
    def create_sample_listener_data(self):
        """Create sample listener data for testing (before real listener is implemented)"""
        sample_date = datetime(2025, 7, 5)
        sample_folder = self.listener_path / sample_date.strftime("%Y-%m-%d")
        sample_folder.mkdir(parents=True, exist_ok=True)
        
        # Sample match data matching our MTGO tournament IDs
        sample_matches = [
            {
                "match_id": "12345",
                "tournament_id": 12801654,  # Matches a real tournament in our data
                "format": "standard",
                "date": "2025-07-05T14:30:00Z",
                "round": 3,
                "player1": {
                    "name": "Alice",
                    "archetype": "Izzet Cauldron",
                    "deck_id": "abc123"
                },
                "player2": {
                    "name": "Bob",
                    "archetype": "Dimir Midrange",
                    "deck_id": "def456"
                },
                "result": {
                    "winner": "player1",
                    "games": [2, 1]
                }
            },
            {
                "match_id": "12346",
                "tournament_id": 12801654,
                "format": "standard",
                "date": "2025-07-05T15:00:00Z",
                "round": 4,
                "player1": {
                    "name": "Charlie",
                    "archetype": "Mono White Caretaker",
                    "deck_id": "ghi789"
                },
                "player2": {
                    "name": "Alice",
                    "archetype": "Izzet Cauldron",
                    "deck_id": "abc123"
                },
                "result": {
                    "winner": "player2",
                    "games": [2, 0]
                }
            }
        ]
        
        # Save sample matches
        for i, match in enumerate(sample_matches):
            match_file = sample_folder / f"match_{match['match_id']}.json"
            with open(match_file, 'w') as f:
                json.dump(match, f, indent=2)
        
        logger.info(f"Created {len(sample_matches)} sample listener matches in {sample_folder}")