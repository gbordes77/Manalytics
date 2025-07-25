"""
Data models for the cache system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class CachedCard:
    """Card with count in a deck"""
    name: str
    count: int


@dataclass 
class CachedDecklist:
    """Cached decklist with detected archetype and colors"""
    deck_id: str
    tournament_id: str
    player: str
    rank: int
    wins: int
    losses: int
    deck_name: Optional[str]
    
    # Detected fields
    archetype: Optional[str]
    colors: Optional[str]
    companion: Optional[str]
    
    # Card lists
    mainboard: List[CachedCard]
    sideboard: List[CachedCard]
    
    # Metadata
    cached_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'deck_id': self.deck_id,
            'tournament_id': self.tournament_id,
            'player': self.player,
            'rank': self.rank,
            'wins': self.wins,
            'losses': self.losses,
            'deck_name': self.deck_name,
            'archetype': self.archetype,
            'colors': self.colors,
            'companion': self.companion,
            'mainboard': [{'name': c.name, 'count': c.count} for c in self.mainboard],
            'sideboard': [{'name': c.name, 'count': c.count} for c in self.sideboard],
            'cached_at': self.cached_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CachedDecklist':
        """Create from dictionary"""
        return cls(
            deck_id=data['deck_id'],
            tournament_id=data['tournament_id'],
            player=data['player'],
            rank=data['rank'],
            wins=data['wins'],
            losses=data['losses'],
            deck_name=data.get('deck_name'),
            archetype=data.get('archetype'),
            colors=data.get('colors'),
            companion=data.get('companion'),
            mainboard=[CachedCard(**c) for c in data['mainboard']],
            sideboard=[CachedCard(**c) for c in data['sideboard']],
            cached_at=datetime.fromisoformat(data['cached_at'])
        )


@dataclass
class CachedTournament:
    """Cached tournament metadata"""
    id: str
    platform: str  # mtgo or melee
    format: str    # standard, modern, etc
    type: Optional[str]  # challenge, league, etc
    name: str
    date: datetime
    players: int
    raw_file: str
    cache_file: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    # Cache status
    colors_detected: bool = False
    archetypes_detected: bool = False
    cache_version: str = "1.0"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'platform': self.platform,
            'format': self.format,
            'type': self.type,
            'name': self.name,
            'date': self.date.isoformat(),
            'players': self.players,
            'raw_file': self.raw_file,
            'cache_file': self.cache_file,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'colors_detected': self.colors_detected,
            'archetypes_detected': self.archetypes_detected,
            'cache_version': self.cache_version
        }