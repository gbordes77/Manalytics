"""
Color detection system for Magic: The Gathering decks.
Based on MTGOArchetypeParser logic.
"""

import re
from typing import List, Set, Dict, Optional
from collections import defaultdict

class ColorDetector:
    """Detects deck colors based on card analysis"""
    
    # Basic lands that define colors
    BASIC_LANDS = {
        'Plains': 'W',
        'Island': 'U', 
        'Swamp': 'B',
        'Mountain': 'R',
        'Forest': 'G'
    }
    
    # Dual/Tri lands and their colors
    MULTICOLOR_LANDS = {
        # Fastlands
        'Darkslick Shores': 'UB',
        'Seachrome Coast': 'WU',
        'Copperline Gorge': 'RG',
        'Razorverge Thicket': 'GW',
        'Blackcleave Cliffs': 'BR',
        
        # Vergelands (BLB)
        'Gloomlake Verge': 'UB',
        'Sunbillow Verge': 'GW',
        'Hushwood Verge': 'GW',
        'Thornspire Verge': 'RG',
        'Stormcatch Verge': 'UR',
        
        # Slowlands
        'Haunted Ridge': 'BR',
        'Shattered Sanctum': 'WB',
        'Overgrown Farmland': 'GW',
        'Stormcarved Coast': 'UR',
        'Dreamroot Cascade': 'GU',
        
        # Painlands
        'Underground River': 'UB',
        'Battlefield Forge': 'RW',
        'Brushland': 'GW',
        'Shivan Reef': 'UR',
        'Yavimaya Coast': 'GU',
        
        # Triomes
        'Raffine\'s Tower': 'WUB',
        'Xander\'s Lounge': 'UBR',
        'Ziatora\'s Proving Ground': 'BRG',
        'Jetmir\'s Garden': 'RGW',
        'Spara\'s Headquarters': 'GWU',
    }
    
    def __init__(self, color_overrides: Optional[Dict] = None):
        self.color_overrides = color_overrides or {}
        
    def detect_colors(self, decklist: List[Dict]) -> str:
        """
        Detect deck colors from decklist.
        Returns color identity string (e.g., "WU", "RGB", "Mono Red")
        """
        colors = set()
        
        # Analyze each card
        for card in decklist:
            card_name = card.get('card_name', '')
            card_colors = self._get_card_colors(card_name)
            colors.update(card_colors)
        
        # Convert to standard notation
        return self._format_colors(colors)
    
    def _get_card_colors(self, card_name: str) -> Set[str]:
        """Get colors for a specific card"""
        # Check basic lands
        if card_name in self.BASIC_LANDS:
            return {self.BASIC_LANDS[card_name]}
        
        # Check multicolor lands
        if card_name in self.MULTICOLOR_LANDS:
            return set(self.MULTICOLOR_LANDS[card_name])
        
        # Check color overrides
        if self.color_overrides:
            lands = self.color_overrides.get('Lands', {})
            if card_name in lands:
                return set(lands[card_name])
        
        # For non-lands, we'd need a card database
        # For now, return empty (to be enhanced with Scryfall API)
        return set()
    
    def _format_colors(self, colors: Set[str]) -> str:
        """Format color set into standard notation"""
        if not colors:
            return "Colorless"
        
        # Sort in WUBRG order
        color_order = ['W', 'U', 'B', 'R', 'G']
        sorted_colors = [c for c in color_order if c in colors]
        
        if len(sorted_colors) == 1:
            color_names = {
                'W': 'White',
                'U': 'Blue', 
                'B': 'Black',
                'R': 'Red',
                'G': 'Green'
            }
            return f"Mono {color_names[sorted_colors[0]]}"
        
        return ''.join(sorted_colors)
    
    def get_color_combinations(self) -> Dict[str, str]:
        """Get common color combination names"""
        return {
            'WU': 'Azorius',
            'UB': 'Dimir',
            'BR': 'Rakdos',
            'RG': 'Gruul',
            'GW': 'Selesnya',
            'WB': 'Orzhov',
            'UR': 'Izzet',
            'BG': 'Golgari',
            'RW': 'Boros',
            'GU': 'Simic',
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