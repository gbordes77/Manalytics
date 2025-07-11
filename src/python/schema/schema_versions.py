"""
Schema version implementations for different data sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseSchema(ABC):
    """Base class for all schema versions."""
    
    @abstractmethod
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data to unified format."""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data against schema."""
        pass
    
    def get_version(self) -> str:
        """Get schema version."""
        return self.__class__.__name__


class MTGOSchemaV1(BaseSchema):
    """MTGO schema version 1 (legacy format)."""
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MTGO v1 data to unified format."""
        try:
            normalized = {
                'tournament_id': data.get('id'),
                'name': data.get('name'),
                'date': self._parse_date(data.get('date')),
                'format': data.get('format', '').lower(),
                'source': 'mtgo',
                'schema_version': 'v1',
                'players': [],
                'rounds': data.get('rounds', []),
                'metadata': {
                    'total_players': data.get('player_count', 0),
                    'swiss_rounds': data.get('swiss_rounds', 0),
                    'playoff_rounds': data.get('playoff_rounds', 0)
                }
            }
            
            # Normalize player data
            for player_data in data.get('players', []):
                normalized_player = {
                    'name': player_data.get('player'),
                    'rank': player_data.get('rank'),
                    'wins': player_data.get('wins', 0),
                    'losses': player_data.get('losses', 0),
                    'draws': player_data.get('draws', 0),
                    'deck': self._normalize_deck_v1(player_data.get('deck', {}))
                }
                normalized['players'].append(normalized_player)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing MTGO v1 data: {e}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate MTGO v1 data structure."""
        required_fields = ['id', 'name', 'date', 'players']
        return all(field in data for field in required_fields)
    
    def _normalize_deck_v1(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize deck data for v1 format."""
        return {
            'mainboard': deck_data.get('mainboard', []),
            'sideboard': deck_data.get('sideboard', []),
            'archetype': deck_data.get('archetype'),
            'colors': deck_data.get('colors', [])
        }
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            return date_str
        except Exception:
            return date_str


class MTGOSchemaV2(BaseSchema):
    """MTGO schema version 2 (new format with companion support)."""
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MTGO v2 data to unified format."""
        try:
            normalized = {
                'tournament_id': data.get('tournament_id'),
                'name': data.get('tournament_name'),
                'date': data.get('date'),
                'format': data.get('format', '').lower(),
                'source': 'mtgo',
                'schema_version': 'v2',
                'players': [],
                'rounds': data.get('match_data', []),
                'metadata': {
                    'total_players': len(data.get('standings', [])),
                    'swiss_rounds': data.get('swiss_rounds', 0),
                    'playoff_rounds': data.get('elimination_rounds', 0),
                    'has_companion_data': True
                }
            }
            
            # Normalize player data (v2 has different structure)
            for standing in data.get('standings', []):
                player_data = standing.get('player', {})
                normalized_player = {
                    'name': player_data.get('name'),
                    'rank': standing.get('rank'),
                    'wins': standing.get('wins', 0),
                    'losses': standing.get('losses', 0),
                    'draws': standing.get('draws', 0),
                    'deck': self._normalize_deck_v2(player_data.get('deck', {}))
                }
                normalized['players'].append(normalized_player)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing MTGO v2 data: {e}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate MTGO v2 data structure."""
        required_fields = ['tournament_id', 'tournament_name', 'date', 'standings']
        return all(field in data for field in required_fields)
    
    def _normalize_deck_v2(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize deck data for v2 format (includes companion)."""
        return {
            'mainboard': deck_data.get('main', []),
            'sideboard': deck_data.get('side', []),
            'companion': deck_data.get('companion'),  # New in v2
            'archetype': deck_data.get('archetype'),
            'colors': deck_data.get('color_identity', [])
        }


class MeleeSchemaV1(BaseSchema):
    """Melee.gg schema version 1."""
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Melee data to unified format."""
        try:
            normalized = {
                'tournament_id': data.get('id'),
                'name': data.get('name'),
                'date': data.get('startDate'),
                'format': data.get('format', '').lower(),
                'source': 'melee',
                'schema_version': 'melee_v1',
                'players': [],
                'rounds': data.get('rounds', []),
                'metadata': {
                    'total_players': data.get('playerCount', 0),
                    'swiss_rounds': data.get('swissRounds', 0),
                    'playoff_rounds': data.get('playoffRounds', 0),
                    'has_matchups': 'matchups' in data,
                    'has_swiss_rounds': 'swiss_rounds' in data
                }
            }
            
            # Normalize standings
            for standing in data.get('standings', []):
                normalized_player = {
                    'name': standing.get('player', {}).get('name'),
                    'rank': standing.get('rank'),
                    'wins': standing.get('wins', 0),
                    'losses': standing.get('losses', 0),
                    'draws': standing.get('draws', 0),
                    'deck': self._normalize_melee_deck(standing.get('deck', {}))
                }
                normalized['players'].append(normalized_player)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing Melee data: {e}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate Melee data structure."""
        required_fields = ['id', 'name', 'startDate']
        has_matchups = 'matchups' in data and 'swiss_rounds' in data
        has_standings = 'standings' in data
        
        return (all(field in data for field in required_fields) and 
                (has_matchups or has_standings))
    
    def _normalize_melee_deck(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Melee deck data."""
        return {
            'mainboard': deck_data.get('mainboard', []),
            'sideboard': deck_data.get('sideboard', []),
            'archetype': deck_data.get('archetype'),
            'colors': self._extract_colors(deck_data.get('mainboard', []))
        }
    
    def _extract_colors(self, mainboard: list) -> list:
        """Extract colors from mainboard cards."""
        # Simple color extraction logic
        colors = set()
        for card in mainboard:
            if 'mana_cost' in card:
                mana_cost = card['mana_cost']
                if 'W' in mana_cost:
                    colors.add('W')
                if 'U' in mana_cost:
                    colors.add('U')
                if 'B' in mana_cost:
                    colors.add('B')
                if 'R' in mana_cost:
                    colors.add('R')
                if 'G' in mana_cost:
                    colors.add('G')
        return list(colors) 