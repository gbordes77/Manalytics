# src/api/models.py - Enhanced models with pagination

from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from datetime import date

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Items per page")
    
class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class CardModel(BaseModel):
    quantity: int
    name: str

class DecklistResponse(BaseModel):
    id: str
    player: str
    archetype: str
    tournament_name: Optional[str]
    tournament_date: Optional[date]
    position: Optional[int]
    wins: Optional[int]
    losses: Optional[int]
    mainboard: List[CardModel]
    sideboard: List[CardModel]

class ArchetypeResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str]
    color_identity: Optional[str]
    meta_share: float
    deck_count: int
    avg_win_rate: Optional[float]

class MetaSnapshotResponse(BaseModel):
    format: str
    date_from: date
    date_to: date
    total_decks: int
    total_tournaments: int
    archetypes: List[ArchetypeResponse]

class DeckFilters(BaseModel):
    """Filters for deck searches."""
    format: Optional[str] = None
    archetype: Optional[str] = None
    player: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_wins: Optional[int] = None
    tournament_name: Optional[str] = None