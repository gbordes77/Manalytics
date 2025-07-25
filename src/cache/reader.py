"""
Cache reader - provides fast access to cached tournament data.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

from .database import CacheDatabase
from .models import CachedDecklist, CachedCard


logger = logging.getLogger(__name__)


class CacheReader:
    """Fast reader for cached tournament data"""
    
    def __init__(self, cache_path: Path = None):
        """Initialize reader with cache path"""
        self.cache_path = cache_path or Path("data/cache")
        self.db = CacheDatabase(self.cache_path / "tournaments.db")
        
        # Cache loaded data for performance
        self._decklist_cache = {}
        self._archetype_cache = {}
    
    def load_tournaments(self, format: str = None, start_date: datetime = None, 
                        end_date: datetime = None) -> List[Dict]:
        """Load tournament metadata"""
        if format:
            tournaments = self.db.get_tournaments_by_format(format, start_date, end_date)
        else:
            # Would need to implement get_all_tournaments
            tournaments = []
        
        return [t.to_dict() for t in tournaments]
    
    def load_decklists(self, tournament_ids: List[str] = None, 
                      format: str = None, month: str = None) -> pd.DataFrame:
        """Load decklists from cache"""
        dfs = []
        
        if month:
            # Load specific month
            parquet_file = self.cache_path / "decklists" / f"{month}.parquet"
            if parquet_file.exists():
                df = pd.read_parquet(parquet_file)
                if tournament_ids:
                    df = df[df['tournament_id'].isin(tournament_ids)]
                dfs.append(df)
        else:
            # Load all available months
            decklists_dir = self.cache_path / "decklists"
            if decklists_dir.exists():
                for parquet_file in decklists_dir.glob("*.parquet"):
                    df = pd.read_parquet(parquet_file)
                    if tournament_ids:
                        df = df[df['tournament_id'].isin(tournament_ids)]
                    dfs.append(df)
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            # Parse JSON columns back to lists
            result['mainboard'] = result['mainboard'].apply(json.loads)
            result['sideboard'] = result['sideboard'].apply(json.loads)
            return result
        
        return pd.DataFrame()
    
    def get_meta_snapshot(self, format: str, date: datetime = None) -> Dict:
        """Get metagame snapshot for a specific date"""
        if date is None:
            date = datetime.now()
        
        # Load tournaments within 2 weeks of date
        start_date = date.replace(day=1)
        end_date = date
        
        tournaments = self.db.get_tournaments_by_format(format, start_date, end_date)
        tournament_ids = [t.id for t in tournaments]
        
        if not tournament_ids:
            return {
                'format': format,
                'date': date.isoformat(),
                'total_decks': 0,
                'archetypes': {},
                'colors': {}
            }
        
        # Load archetype summaries
        month_key = date.strftime("%Y-%m")
        archetypes_file = self.cache_path / "archetypes" / f"{month_key}.json"
        
        total_decks = 0
        archetype_counts = {}
        color_counts = {}
        
        if archetypes_file.exists():
            with open(archetypes_file, 'r') as f:
                all_summaries = json.load(f)
            
            for tid in tournament_ids:
                if tid in all_summaries:
                    summary = all_summaries[tid]
                    total_decks += summary['total_decks']
                    
                    # Aggregate archetype counts
                    for arch, count in summary['archetypes'].items():
                        if arch not in archetype_counts:
                            archetype_counts[arch] = 0
                        archetype_counts[arch] += count
                    
                    # Aggregate color counts
                    for color, count in summary['colors'].items():
                        if color not in color_counts:
                            color_counts[color] = 0
                        color_counts[color] += count
        
        # Calculate percentages
        archetype_meta = {}
        for arch, count in archetype_counts.items():
            archetype_meta[arch] = {
                'count': count,
                'percentage': round(count / total_decks * 100, 2) if total_decks > 0 else 0
            }
        
        color_meta = {}
        for color, count in color_counts.items():
            color_meta[color] = {
                'count': count,
                'percentage': round(count / total_decks * 100, 2) if total_decks > 0 else 0
            }
        
        return {
            'format': format,
            'date': date.isoformat(),
            'total_decks': total_decks,
            'tournament_count': len(tournament_ids),
            'archetypes': archetype_meta,
            'colors': color_meta
        }
    
    def get_archetype_performance(self, archetype: str, format: str = 'standard',
                                 start_date: datetime = None) -> Dict:
        """Get performance stats for an archetype"""
        # Load decklists
        tournaments = self.db.get_tournaments_by_format(format, start_date)
        tournament_ids = [t.id for t in tournaments]
        
        df = self.load_decklists(tournament_ids=tournament_ids)
        
        if df.empty:
            return {}
        
        # Filter by archetype
        archetype_df = df[df['archetype'] == archetype]
        
        if archetype_df.empty:
            return {}
        
        # Calculate stats
        total_decks = len(archetype_df)
        total_wins = archetype_df['wins'].sum()
        total_losses = archetype_df['losses'].sum()
        total_matches = total_wins + total_losses
        
        # Top finishes
        top8_count = len(archetype_df[archetype_df['rank'] <= 8])
        
        return {
            'archetype': archetype,
            'total_decks': total_decks,
            'total_matches': total_matches,
            'win_rate': round(total_wins / total_matches * 100, 2) if total_matches > 0 else 0,
            'top8_count': top8_count,
            'top8_rate': round(top8_count / total_decks * 100, 2) if total_decks > 0 else 0
        }
    
    def search_cards(self, card_names: List[str], zone: str = 'mainboard') -> pd.DataFrame:
        """Search for decks containing specific cards"""
        # Load all decklists
        df = self.load_decklists()
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter decks containing all specified cards
        matching_decks = []
        
        for idx, row in df.iterrows():
            cards_in_zone = row[zone]
            card_dict = {card['name']: card['count'] for card in cards_in_zone}
            
            # Check if all cards are present
            if all(card in card_dict for card in card_names):
                matching_decks.append(idx)
        
        return df.loc[matching_decks]