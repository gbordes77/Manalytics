"""
Archetype detection parser based on MTGOArchetypeParser.
Uses rules from MTGOFormatData to identify deck archetypes.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ConditionType(Enum):
    """Types of conditions for archetype detection"""
    # Presence in specific zone
    IN_MAINBOARD = "InMainboard"
    IN_SIDEBOARD = "InSideboard"
    IN_MAIN_OR_SIDEBOARD = "InMainOrSideboard"
    
    # Minimum quantity
    ONE_OR_MORE_IN_MAINBOARD = "OneOrMoreInMainboard"
    ONE_OR_MORE_IN_SIDEBOARD = "OneOrMoreInSideboard"
    ONE_OR_MORE_IN_MAIN_OR_SIDEBOARD = "OneOrMoreInMainOrSideboard"
    TWO_OR_MORE_IN_MAINBOARD = "TwoOrMoreInMainboard"
    TWO_OR_MORE_IN_SIDEBOARD = "TwoOrMoreInSideboard"
    TWO_OR_MORE_IN_MAIN_OR_SIDEBOARD = "TwoOrMoreInMainOrSideboard"
    
    # Exclusion
    DOES_NOT_CONTAIN = "DoesNotContain"
    DOES_NOT_CONTAIN_MAINBOARD = "DoesNotContainMainboard"
    DOES_NOT_CONTAIN_SIDEBOARD = "DoesNotContainSideboard"


@dataclass
class ArchetypeCondition:
    """Single condition for archetype matching"""
    type: ConditionType
    cards: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ArchetypeCondition':
        """Create from JSON dictionary"""
        return cls(
            type=ConditionType(data['Type']),
            cards=data['Cards']
        )


@dataclass
class ArchetypeVariant:
    """Variant of an archetype with additional conditions"""
    name: str
    conditions: List[ArchetypeCondition]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ArchetypeVariant':
        """Create from JSON dictionary"""
        conditions = [ArchetypeCondition.from_dict(c) for c in data.get('Conditions', [])]
        return cls(
            name=data['Name'],
            conditions=conditions
        )


@dataclass
class Archetype:
    """Archetype definition with conditions and variants"""
    name: str
    conditions: List[ArchetypeCondition]
    variants: List[ArchetypeVariant]
    include_color_in_name: bool
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Archetype':
        """Create from JSON dictionary"""
        conditions = [ArchetypeCondition.from_dict(c) for c in data.get('Conditions', [])]
        variants = [ArchetypeVariant.from_dict(v) for v in data.get('Variants', [])]
        return cls(
            name=data['Name'],
            conditions=conditions,
            variants=variants,
            include_color_in_name=data.get('IncludeColorInName', True)
        )


class ArchetypeParser:
    """Detects deck archetypes using MTGOFormatData rules"""
    
    def __init__(self, data_path: Path = None, format: str = "standard"):
        """Initialize with path to archetype rules"""
        if data_path is None:
            data_path = Path("data/archetype_rules")
        
        self.data_path = data_path
        self.format = format
        self.archetypes = self._load_archetypes()
        self.fallback_threshold = 0.1  # 10% for generic archetypes
    
    def _load_archetypes(self) -> List[Archetype]:
        """Load all archetype definitions for the format"""
        archetypes_dir = self.data_path / self.format / "archetypes"
        archetypes = []
        
        if archetypes_dir.exists():
            for json_file in archetypes_dir.glob("*.json"):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    archetypes.append(Archetype.from_dict(data))
        
        return archetypes
    
    def detect_archetype(self, mainboard: List[Dict], sideboard: List[Dict], 
                        color: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect archetype from decklist.
        Returns (archetype_name, variant_name)
        """
        # Convert card lists to lookup format for efficiency
        main_cards = self._cards_to_dict(mainboard)
        side_cards = self._cards_to_dict(sideboard)
        
        # Test each archetype
        matches = []
        for archetype in self.archetypes:
            if self._test_archetype(archetype, main_cards, side_cards):
                # Check for variants
                variant = self._test_variants(archetype.variants, main_cards, side_cards)
                
                # Format name
                if archetype.include_color_in_name and color:
                    name = f"{color} {archetype.name}"
                else:
                    name = archetype.name
                
                matches.append((name, variant.name if variant else None))
        
        if matches:
            # Return first match (following Jiliac's "First" conflict mode)
            return matches[0]
        
        # No specific archetype found
        return None, None
    
    def _cards_to_dict(self, cards: List[Dict]) -> Dict[str, int]:
        """Convert card list to {name: count} dictionary"""
        result = {}
        for card in cards:
            name = card.get('CardName') or card.get('card_name', '')
            count = card.get('Count') or card.get('count', 0)
            result[name] = count
        return result
    
    def _test_archetype(self, archetype: Archetype, main_cards: Dict[str, int], 
                       side_cards: Dict[str, int]) -> bool:
        """Test if deck matches archetype conditions"""
        # All conditions must be true (AND logic)
        for condition in archetype.conditions:
            if not self._test_condition(condition, main_cards, side_cards):
                return False
        return True
    
    def _test_variants(self, variants: List[ArchetypeVariant], main_cards: Dict[str, int],
                      side_cards: Dict[str, int]) -> Optional[ArchetypeVariant]:
        """Test variants and return first match"""
        for variant in variants:
            if all(self._test_condition(c, main_cards, side_cards) for c in variant.conditions):
                return variant
        return None
    
    def _test_condition(self, condition: ArchetypeCondition, main_cards: Dict[str, int],
                       side_cards: Dict[str, int]) -> bool:
        """Test a single condition"""
        if condition.type == ConditionType.IN_MAINBOARD:
            # All cards must be in mainboard
            return all(card in main_cards for card in condition.cards)
        
        elif condition.type == ConditionType.IN_SIDEBOARD:
            # All cards must be in sideboard
            return all(card in side_cards for card in condition.cards)
        
        elif condition.type == ConditionType.IN_MAIN_OR_SIDEBOARD:
            # All cards must be in either main or side
            return all(card in main_cards or card in side_cards for card in condition.cards)
        
        elif condition.type == ConditionType.ONE_OR_MORE_IN_MAINBOARD:
            # At least one card must be in mainboard
            return any(card in main_cards for card in condition.cards)
        
        elif condition.type == ConditionType.ONE_OR_MORE_IN_SIDEBOARD:
            # At least one card must be in sideboard
            return any(card in side_cards for card in condition.cards)
        
        elif condition.type == ConditionType.ONE_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            # At least one card must be in either
            return any(card in main_cards or card in side_cards for card in condition.cards)
        
        elif condition.type == ConditionType.TWO_OR_MORE_IN_MAINBOARD:
            # At least 2 cards must be in mainboard
            count = sum(1 for card in condition.cards if card in main_cards)
            return count >= 2
        
        elif condition.type == ConditionType.TWO_OR_MORE_IN_SIDEBOARD:
            # At least 2 cards must be in sideboard
            count = sum(1 for card in condition.cards if card in side_cards)
            return count >= 2
        
        elif condition.type == ConditionType.TWO_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            # At least 2 cards must be in either
            count = sum(1 for card in condition.cards if card in main_cards or card in side_cards)
            return count >= 2
        
        elif condition.type == ConditionType.DOES_NOT_CONTAIN:
            # None of the cards can be present
            return not any(card in main_cards or card in side_cards for card in condition.cards)
        
        elif condition.type == ConditionType.DOES_NOT_CONTAIN_MAINBOARD:
            # None of the cards can be in mainboard
            return not any(card in main_cards for card in condition.cards)
        
        elif condition.type == ConditionType.DOES_NOT_CONTAIN_SIDEBOARD:
            # None of the cards can be in sideboard
            return not any(card in side_cards for card in condition.cards)
        
        return False
    
    def _format_color_name(self, color: str) -> str:
        """Format color code for archetype name"""
        # This would use the color names from ColorDetector
        # For now, just return the code
        return color