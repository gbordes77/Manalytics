"""
Listener Reader - Reads match data from MTGOData directory.

This module reads the listener/recorded match data from the MTGOData directory
and provides it in a format compatible with our analysis pipeline.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class ListenerReader:
    """Reads match data from MTGOData directory structure"""
    
    def __init__(self, data_path: Path = None):
        """Initialize the reader with MTGOData path"""
        if data_path is None:
            # Default path via symlink
            self.mtgodata_path = Path("data/mtgodata")
        else:
            self.mtgodata_path = data_path
            
        if not self.mtgodata_path.exists():
            logger.warning(f"MTGOData path does not exist: {self.mtgodata_path}")
    
    def get_tournaments_for_period(self, start_date: datetime, end_date: datetime, 
                                  format_filter: str = "standard") -> Dict[int, Dict]:
        """
        Get all tournaments with match data for a given period.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            format_filter: Tournament format to filter (default: "standard")
            
        Returns:
            Dictionary mapping tournament_id to tournament data with matches
        """
        tournaments = {}
        
        # Iterate through year/month/day structure
        year = start_date.year
        
        year_path = self.mtgodata_path / str(year)
        if not year_path.exists():
            logger.warning(f"Year directory does not exist: {year_path}")
            return tournaments
        
        # Iterate through months
        for month in range(start_date.month, end_date.month + 1):
            month_path = year_path / f"{month:02d}"
            if not month_path.exists():
                continue
            
            # Iterate through days
            start_day = 1 if month > start_date.month else start_date.day
            end_day = 31 if month < end_date.month else end_date.day
            
            for day in range(start_day, end_day + 1):
                day_path = month_path / f"{day:02d}"
                if not day_path.exists():
                    continue
                
                # Read all JSON files in the day directory
                for json_file in day_path.glob("*.json"):
                    # Filter by format
                    if format_filter and format_filter not in json_file.name.lower():
                        continue
                    
                    # Skip leagues
                    if "league" in json_file.name.lower():
                        continue
                    
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        tournament = data.get('Tournament', {})
                        tournament_id = tournament.get('Id')
                        
                        if tournament_id and data.get('Rounds'):
                            # Parse tournament date
                            date_str = tournament.get('Date', '')
                            if date_str:
                                tournament_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            else:
                                tournament_date = datetime(year, month, day)
                            
                            tournaments[tournament_id] = {
                                'id': tournament_id,
                                'name': tournament.get('Name', json_file.stem),
                                'date': tournament_date,
                                'format': format_filter,
                                'rounds': data.get('Rounds', []),
                                'file_path': str(json_file)
                            }
                            
                            logger.info(f"Loaded tournament {tournament_id}: {tournament.get('Name')}")
                    
                    except Exception as e:
                        logger.error(f"Error reading {json_file}: {e}")
        
        logger.info(f"Loaded {len(tournaments)} {format_filter} tournaments from {start_date} to {end_date}")
        return tournaments
    
    def get_all_matches(self, tournaments: Dict[int, Dict]) -> List[Dict]:
        """
        Extract all matches from tournaments.
        
        Args:
            tournaments: Dictionary of tournament data
            
        Returns:
            List of all matches with tournament context
        """
        all_matches = []
        
        for tournament_id, tournament_data in tournaments.items():
            tournament_name = tournament_data['name']
            tournament_date = tournament_data['date']
            
            for round_data in tournament_data.get('rounds', []):
                round_name = round_data.get('RoundName', 'Unknown')
                
                for match in round_data.get('Matches', []):
                    # Skip BYEs and incomplete results
                    if match.get('Player2') == 'BYE' or match.get('Result') in ['0-0-0', None, '']:
                        continue
                    
                    match_record = {
                        'tournament_id': tournament_id,
                        'tournament_name': tournament_name,
                        'tournament_date': tournament_date,
                        'round': round_name,
                        'player1': match.get('Player1'),
                        'player2': match.get('Player2'),
                        'result': match.get('Result')
                    }
                    
                    all_matches.append(match_record)
        
        logger.info(f"Extracted {len(all_matches)} matches from {len(tournaments)} tournaments")
        return all_matches
    
    def get_matches_by_date(self, date: datetime, format_filter: str = "standard") -> List[Dict]:
        """
        Get all matches for a specific date.
        
        Args:
            date: The date to get matches for
            format_filter: Tournament format to filter
            
        Returns:
            List of matches for that date
        """
        tournaments = self.get_tournaments_for_period(date, date, format_filter)
        return self.get_all_matches(tournaments)
    
    def get_tournament_by_id(self, tournament_id: int) -> Optional[Dict]:
        """
        Get a specific tournament by ID.
        
        Args:
            tournament_id: The tournament ID to search for
            
        Returns:
            Tournament data if found, None otherwise
        """
        # Search through all directories for the tournament
        for year_path in self.mtgodata_path.iterdir():
            if not year_path.is_dir() or not year_path.name.isdigit():
                continue
            
            for month_path in year_path.iterdir():
                if not month_path.is_dir():
                    continue
                
                for day_path in month_path.iterdir():
                    if not day_path.is_dir():
                        continue
                    
                    # Check all JSON files
                    for json_file in day_path.glob("*.json"):
                        if str(tournament_id) in json_file.name:
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                tournament = data.get('Tournament', {})
                                if tournament.get('Id') == tournament_id:
                                    return {
                                        'id': tournament_id,
                                        'name': tournament.get('Name'),
                                        'date': datetime.fromisoformat(tournament.get('Date', '').replace('Z', '+00:00')),
                                        'rounds': data.get('Rounds', []),
                                        'file_path': str(json_file)
                                    }
                            except Exception as e:
                                logger.error(f"Error reading {json_file}: {e}")
        
        return None
    
    def aggregate_matchup_stats(self, matches: List[Dict]) -> Dict[str, Dict[str, Dict]]:
        """
        Aggregate matchup statistics from matches.
        
        Args:
            matches: List of match records
            
        Returns:
            Dictionary of matchup statistics (needs archetype data to be useful)
        """
        matchup_stats = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0}))
        
        for match in matches:
            player1 = match['player1']
            player2 = match['player2']
            result = match['result']
            
            # Parse result
            if result and '-' in result:
                parts = result.split('-')
                if len(parts) >= 2:
                    try:
                        p1_wins = int(parts[0])
                        p2_wins = int(parts[1])
                        
                        # For now, just track player vs player
                        # In practice, we need archetype mapping
                        if p1_wins > p2_wins:
                            matchup_stats[player1][player2]['wins'] += 1
                            matchup_stats[player1][player2]['total'] += 1
                            matchup_stats[player2][player1]['losses'] += 1
                            matchup_stats[player2][player1]['total'] += 1
                        else:
                            matchup_stats[player1][player2]['losses'] += 1
                            matchup_stats[player1][player2]['total'] += 1
                            matchup_stats[player2][player1]['wins'] += 1
                            matchup_stats[player2][player1]['total'] += 1
                    except ValueError:
                        logger.warning(f"Could not parse result: {result}")
        
        return dict(matchup_stats)


def test_reader():
    """Test the listener reader with July 1-21 data"""
    reader = ListenerReader()
    
    # Test period: July 1-21, 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21)
    
    # Get Standard tournaments
    tournaments = reader.get_tournaments_for_period(start_date, end_date, "standard")
    print(f"\nFound {len(tournaments)} Standard tournaments")
    
    # Show first 5 tournaments
    for tid, tdata in list(tournaments.items())[:5]:
        print(f"\nTournament {tid}:")
        print(f"  Name: {tdata['name']}")
        print(f"  Date: {tdata['date']}")
        print(f"  Rounds: {len(tdata['rounds'])}")
        
        # Count matches
        total_matches = sum(len(r.get('Matches', [])) for r in tdata['rounds'])
        print(f"  Total matches: {total_matches}")
    
    # Get all matches
    all_matches = reader.get_all_matches(tournaments)
    print(f"\nTotal matches across all tournaments: {len(all_matches)}")
    
    # Example: Get specific tournament
    example_id = 12802771  # Standard Challenge from July 10
    tournament = reader.get_tournament_by_id(example_id)
    if tournament:
        print(f"\nFound tournament {example_id}: {tournament['name']}")
    
    return tournaments, all_matches


if __name__ == "__main__":
    test_reader()