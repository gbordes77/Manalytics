"""
Tournament Cache System for Manalytics
Improves performance by caching parsed tournament data
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TournamentCache:
    """
    Manages cached tournament data to avoid re-parsing
    """
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-directories
        self.tournaments_dir = cache_dir / "tournaments"
        self.archetypes_dir = cache_dir / "archetypes"
        self.matchups_dir = cache_dir / "matchups"
        
        for dir in [self.tournaments_dir, self.archetypes_dir, self.matchups_dir]:
            dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, format_name: str, start_date: str, end_date: str) -> str:
        """Generate cache key for date range"""
        return f"{format_name}_{start_date}_{end_date}"
    
    def get_tournament_cache(
        self, 
        format_name: str, 
        start_date: datetime,
        end_date: datetime
    ) -> Optional[List[Dict]]:
        """
        Get cached tournament data if available and fresh
        """
        cache_key = self.get_cache_key(
            format_name,
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )
        
        cache_file = self.tournaments_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is fresh (less than 1 day old)
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if age < timedelta(days=1):
                logger.info(f"Loading tournaments from cache: {cache_file}")
                with open(cache_file, 'r') as f:
                    return json.load(f)
            else:
                logger.info(f"Cache expired: {cache_file}")
        
        return None
    
    def save_tournament_cache(
        self,
        format_name: str,
        start_date: datetime,
        end_date: datetime,
        tournaments: List[Dict]
    ):
        """Save tournaments to cache"""
        cache_key = self.get_cache_key(
            format_name,
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )
        
        cache_file = self.tournaments_dir / f"{cache_key}.json"
        
        logger.info(f"Saving {len(tournaments)} tournaments to cache: {cache_file}")
        with open(cache_file, 'w') as f:
            json.dump(tournaments, f, indent=2)
    
    def get_archetype_cache(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get cached archetype detection results"""
        cache_file = self.archetypes_dir / f"{format_name}_archetypes.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Check if cache is recent
            cache_date = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
            if datetime.now() - cache_date < timedelta(hours=6):
                logger.info(f"Using cached archetypes for {format_name}")
                return data['archetypes']
        
        return None
    
    def save_archetype_cache(self, format_name: str, archetypes: Dict[str, Any]):
        """Save archetype detection results"""
        cache_file = self.archetypes_dir / f"{format_name}_archetypes.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'format': format_name,
            'archetypes': archetypes
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_matchup_cache(self, format_name: str) -> Optional[Dict[str, Dict[str, float]]]:
        """Get cached matchup matrix"""
        cache_file = self.matchups_dir / f"{format_name}_matchups.json"
        
        if cache_file.exists():
            # Matchups are valid for 1 week
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if age < timedelta(days=7):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def save_matchup_cache(self, format_name: str, matchups: Dict[str, Dict[str, float]]):
        """Save matchup matrix to cache"""
        cache_file = self.matchups_dir / f"{format_name}_matchups.json"
        
        with open(cache_file, 'w') as f:
            json.dump(matchups, f, indent=2)
    
    def invalidate_cache(self, format_name: Optional[str] = None):
        """Invalidate cache for a format or all formats"""
        if format_name:
            # Remove specific format cache
            pattern = f"{format_name}_*"
            for cache_file in self.cache_dir.rglob(pattern):
                cache_file.unlink()
                logger.info(f"Removed cache: {cache_file}")
        else:
            # Clear all cache
            for cache_file in self.cache_dir.rglob("*.json"):
                cache_file.unlink()
            logger.info("Cleared all cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = 0
        file_count = 0
        
        for cache_file in self.cache_dir.rglob("*.json"):
            total_size += cache_file.stat().st_size
            file_count += 1
        
        return {
            'file_count': file_count,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'tournaments': len(list(self.tournaments_dir.glob("*.json"))),
            'archetypes': len(list(self.archetypes_dir.glob("*.json"))),
            'matchups': len(list(self.matchups_dir.glob("*.json")))
        }