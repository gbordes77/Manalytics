"""
Data loader utility to load existing tournament data from disk
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

class DataLoader:
    """Load tournament data from raw data directories."""
    
    def __init__(self):
        self.raw_data_path = settings.DATA_DIR / "raw"
    
    def load_tournaments(self, platform: Optional[str] = None, 
                        format_name: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Load tournament data from disk.
        
        Args:
            platform: Filter by platform (mtgo, melee). None = all platforms
            format_name: Filter by format (standard, modern, etc.). None = all formats
            start_date: Filter tournaments after this date
            end_date: Filter tournaments before this date
            
        Returns:
            List of tournament dictionaries
        """
        tournaments = []
        
        # Determine paths to search
        search_paths = []
        if platform:
            if format_name:
                # Specific platform and format
                path = self.raw_data_path / platform / format_name
                if path.exists():
                    search_paths.append(path)
            else:
                # All formats for a platform
                platform_path = self.raw_data_path / platform
                if platform_path.exists():
                    search_paths.extend([p for p in platform_path.iterdir() if p.is_dir()])
        else:
            # All platforms and formats
            for platform_dir in self.raw_data_path.iterdir():
                if platform_dir.is_dir():
                    for format_dir in platform_dir.iterdir():
                        if format_dir.is_dir():
                            search_paths.append(format_dir)
        
        # Load JSON files from each path
        for search_path in search_paths:
            logger.info(f"Loading tournaments from {search_path}")
            
            for json_file in search_path.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Parse date from filename or data
                    date_str = json_file.stem.split('_')[0]  # YYYY-MM-DD format
                    try:
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    except:
                        file_date = None
                    
                    # Apply date filters if provided
                    if file_date:
                        if start_date and file_date < start_date:
                            continue
                        if end_date and file_date > end_date:
                            continue
                    
                    # Normalize data structure for different formats
                    tournament = self._normalize_tournament_data(data, search_path.parent.name, search_path.name)
                    if tournament:
                        tournaments.append(tournament)
                        
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")
        
        logger.info(f"Loaded {len(tournaments)} tournaments from disk")
        return tournaments
    
    def _normalize_tournament_data(self, data: Dict[str, Any], platform: str, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Normalize tournament data to a common structure.
        Handles different data formats from various sources.
        """
        try:
            # Check if it's already in the expected format
            if "tournament" in data and "decks" in data:
                # New format (from scrapers/clients/)
                return {
                    "source": platform,
                    "format": format_name,
                    "name": data["tournament"]["name"],
                    "date": data["tournament"]["date"],
                    "url": data["tournament"].get("uri", data["tournament"].get("url", "")),
                    "decklists": [
                        {
                            "player": deck["player"],
                            "result": deck.get("result", ""),
                            "mainboard": [
                                {"name": card["card_name"], "quantity": card["count"]}
                                for card in deck.get("mainboard", [])
                            ],
                            "sideboard": [
                                {"name": card["card_name"], "quantity": card["count"]}
                                for card in deck.get("sideboard", [])
                            ]
                        }
                        for deck in data.get("decks", [])
                    ]
                }
            
            # Old format (from data/raw/)
            elif "source" in data and "decklists" in data:
                return data
            
            # Unknown format
            else:
                logger.warning(f"Unknown tournament data format: {list(data.keys())}")
                return None
                
        except Exception as e:
            logger.error(f"Error normalizing tournament data: {e}")
            return None

    def count_tournaments(self, platform: Optional[str] = None, format_name: Optional[str] = None) -> Dict[str, int]:
        """Count tournaments by platform and format."""
        counts = {}
        
        for platform_dir in self.raw_data_path.iterdir():
            if platform_dir.is_dir() and (not platform or platform_dir.name == platform):
                for format_dir in platform_dir.iterdir():
                    if format_dir.is_dir() and (not format_name or format_dir.name == format_name):
                        key = f"{platform_dir.name}/{format_dir.name}"
                        count = len(list(format_dir.glob("*.json")))
                        if count > 0:
                            counts[key] = count
        
        return counts


# Convenience functions
def load_all_tournaments() -> List[Dict[str, Any]]:
    """Load all tournaments from disk."""
    loader = DataLoader()
    return loader.load_tournaments()

def load_format_tournaments(format_name: str) -> List[Dict[str, Any]]:
    """Load all tournaments for a specific format."""
    loader = DataLoader()
    return loader.load_tournaments(format_name=format_name)

def load_platform_tournaments(platform: str, format_name: str) -> List[Dict[str, Any]]:
    """Load tournaments for a specific platform and format."""
    loader = DataLoader()
    return loader.load_tournaments(platform=platform, format_name=format_name)