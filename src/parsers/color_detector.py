"""
Color detection system for Magic: The Gathering decks.
Based on MTGOArchetypeParser logic with card_colors.json database.
"""

import json
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict


class ColorDetector:
    """Detects deck colors using MTGOFormatData card database"""
    
    # Basic lands that define colors
    BASIC_LANDS = {
        'Plains': 'W',
        'Island': 'U', 
        'Swamp': 'B',
        'Mountain': 'R',
        'Forest': 'G'
    }
    
    # Snow basics
    SNOW_BASICS = {
        'Snow-Covered Plains': 'W',
        'Snow-Covered Island': 'U',
        'Snow-Covered Swamp': 'B', 
        'Snow-Covered Mountain': 'R',
        'Snow-Covered Forest': 'G'
    }
    
    def __init__(self, data_path: Path = None):
        """Initialize with path to archetype rules data"""
        if data_path is None:
            data_path = Path("data/archetype_rules")
        
        self.data_path = data_path
        self.card_colors = self._load_card_colors()
        self.color_overrides = self._load_color_overrides()
    
    def _load_card_colors(self) -> Dict[str, str]:
        """Load the global card_colors.json database"""
        colors_file = self.data_path / "card_colors.json"
        if colors_file.exists():
            with open(colors_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_color_overrides(self) -> Dict[str, Dict[str, str]]:
        """Load format-specific color overrides"""
        overrides_file = self.data_path / "standard" / "color_overrides.json"
        if overrides_file.exists():
            with open(overrides_file, 'r') as f:
                return json.load(f)
        return {}
    
    def detect_colors(self, mainboard: List[Dict], sideboard: List[Dict] = None) -> str:
        """
        Detect deck colors from mainboard (and optionally sideboard).
        Returns color identity string (e.g., "U", "UR", "URG")
        """
        colors = set()
        
        # Analyze mainboard
        for card in mainboard:
            card_name = card.get('CardName') or card.get('card_name', '')
            card_colors = self._get_card_colors(card_name)
            colors.update(card_colors)
        
        # Also check sideboard for color identity
        if sideboard:
            for card in sideboard:
                card_name = card.get('CardName') or card.get('card_name', '')
                card_colors = self._get_card_colors(card_name)
                colors.update(card_colors)
        
        # Convert to standard notation
        return self._format_colors(colors)
    
    def _get_card_colors(self, card_name: str) -> Set[str]:
        """Get colors for a specific card"""
        # Normalize card name (remove leading/trailing spaces)
        card_name = card_name.strip()
        
        # Check basic lands first
        if card_name in self.BASIC_LANDS:
            return {self.BASIC_LANDS[card_name]}
        
        # Check snow basics
        if card_name in self.SNOW_BASICS:
            return {self.SNOW_BASICS[card_name]}
        
        # Check color overrides (format-specific)
        if self.color_overrides:
            # Check Lands section
            lands = self.color_overrides.get('Lands', {})
            if card_name in lands:
                color_string = lands[card_name]
                return set(color_string) if color_string else set()
        
        # Check global card colors database
        if card_name in self.card_colors:
            color_string = self.card_colors[card_name]
            # Handle special cases
            if color_string == "C":  # Colorless
                return set()
            return set(color_string) if color_string else set()
        
        # Card not found - this shouldn't happen with complete database
        # But return empty for safety
        return set()
    
    def _format_colors(self, colors: Set[str]) -> str:
        """Format color set into standard WUBRG notation"""
        if not colors:
            return "C"  # Colorless
        
        # Sort in WUBRG order
        color_order = ['W', 'U', 'B', 'R', 'G']
        sorted_colors = [c for c in color_order if c in colors]
        
        return ''.join(sorted_colors)
    
    def get_color_name(self, color_code: str) -> str:
        """Convert color code to friendly name"""
        # Single colors
        single_colors = {
            'W': 'Mono White',
            'U': 'Mono Blue',
            'B': 'Mono Black',
            'R': 'Mono Red',
            'G': 'Mono Green',
            'C': 'Colorless'
        }
        
        if color_code in single_colors:
            return single_colors[color_code]
        
        # Guild names (2 colors)
        guilds = {
            'WU': 'Azorius',
            'UB': 'Dimir',
            'BR': 'Rakdos',
            'RG': 'Gruul',
            'GW': 'Selesnya',
            'WB': 'Orzhov',
            'UR': 'Izzet',
            'BG': 'Golgari',
            'RW': 'Boros',
            'GU': 'Simic'
        }
        
        # Shards/Wedges (3 colors)
        tricolor = {
            'WUB': 'Esper',
            'UBR': 'Grixis',
            'BRG': 'Jund',
            'RGW': 'Naya',
            'GWU': 'Bant',
            'WBG': 'Abzan',
            'URW': 'Jeskai',
            'BGU': 'Sultai',
            'RWB': 'Mardu',
            'GUR': 'Temur'
        }
        
        if color_code in guilds:
            return guilds[color_code]
        elif color_code in tricolor:
            return tricolor[color_code]
        elif len(color_code) == 4:
            return "Four Color"
        elif len(color_code) == 5:
            return "Five Color"
        else:
            return color_code  # Fallback
    
    def detect_companion(self, sideboard: List[Dict]) -> Optional[str]:
        """Detect companion from sideboard"""
        companions = [
            'Jegantha, the Wellspring',
            'Kaheera, the Orphanguard', 
            'Keruga, the Macrosage',
            'Lurrus of the Dream-Den',
            'Lutri, the Spellchaser',
            'Obosh, the Preypiercer',
            'Umori, the Collector',
            'Yorion, Sky Nomad',
            'Zirda, the Dawnwaker'
        ]
        
        if sideboard:
            for card in sideboard:
                card_name = card.get('CardName') or card.get('card_name', '')
                if card_name in companions:
                    return card_name
        
        return None