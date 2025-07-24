from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
from datetime import date, datetime, timedelta
import json

from src.api.models import (
    DecklistResponse, PaginatedResponse, PaginationParams, DeckFilters, CardModel
)
from database.db_pool import get_db_connection

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[DecklistResponse])
async def get_decks(
    # Pagination
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    
    # Filters
    format: Optional[str] = Query(None, description="Format name"),
    archetype: Optional[str] = Query(None, description="Archetype name"),
    player: Optional[str] = Query(None, description="Player name (partial match)"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    min_wins: Optional[int] = Query(None, ge=0, description="Minimum wins"),
    tournament: Optional[str] = Query(None, description="Tournament name (partial match)")
):
    """
    Get paginated list of decks with advanced filtering.
    
    - **format**: Filter by format (e.g., "modern", "standard")
    - **archetype**: Filter by archetype name
    - **player**: Search by player name (partial match)
    - **date_from/date_to**: Filter by date range
    - **min_wins**: Only show decks with at least X wins
    - **tournament**: Search by tournament name
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Build the query dynamically
            base_query = """
                SELECT 
                    d.id::text,
                    p.name as player_name,
                    a.name as archetype_name,
                    t.name as tournament_name,
                    t.date,
                    d.position,
                    d.wins,
                    d.losses,
                    d.mainboard,
                    d.sideboard,
                    COUNT(*) OVER() as total_count
                FROM decklists d
                JOIN players p ON d.player_id = p.id
                JOIN archetypes a ON d.archetype_id = a.id
                JOIN tournaments t ON d.tournament_id = t.id
                JOIN formats f ON t.format_id = f.id
                WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            if format:
                conditions.append("f.name = %(format)s")
                params["format"] = format
                
            if archetype:
                conditions.append("a.name ILIKE %(archetype)s")
                params["archetype"] = f"%{archetype}%"
                
            if player:
                conditions.append("p.name ILIKE %(player)s")
                params["player"] = f"%{player}%"
                
            if date_from:
                conditions.append("t.date >= %(date_from)s")
                params["date_from"] = date_from
                
            if date_to:
                conditions.append("t.date <= %(date_to)s")
                params["date_to"] = date_to
                
            if min_wins is not None:
                conditions.append("d.wins >= %(min_wins)s")
                params["min_wins"] = min_wins
                
            if tournament:
                conditions.append("t.name ILIKE %(tournament)s")
                params["tournament"] = f"%{tournament}%"
            
            # Add conditions to query
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            # Add ordering and pagination
            base_query += """
                ORDER BY t.date DESC, d.position ASC
                LIMIT %(limit)s OFFSET %(offset)s
            """
            
            params["limit"] = size
            params["offset"] = (page - 1) * size
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            if not rows:
                return PaginatedResponse(
                    items=[], total=0, page=page, size=size, pages=0
                )
            
            # Extract total count from first row
            total = rows[0][-1] if rows else 0
            
            # Convert to response models
            items = []
            for row in rows:
                mainboard = [CardModel(**card) for card in row[8]]
                sideboard = [CardModel(**card) for card in row[9]] if row[9] else []
                
                items.append(DecklistResponse(
                    id=row[0],
                    player=row[1],
                    archetype=row[2],
                    tournament_name=row[3],
                    tournament_date=row[4],
                    position=row[5],
                    wins=row[6],
                    losses=row[7],
                    mainboard=mainboard,
                    sideboard=sideboard
                ))
            
            return PaginatedResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )

@router.get("/{deck_id}", response_model=DecklistResponse)
async def get_deck_by_id(deck_id: str):
    """Get a specific deck by ID."""
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    d.id::text,
                    p.name as player_name,
                    a.name as archetype_name,
                    t.name as tournament_name,
                    t.date,
                    d.position,
                    d.wins,
                    d.losses,
                    d.mainboard,
                    d.sideboard
                FROM decklists d
                JOIN players p ON d.player_id = p.id
                JOIN archetypes a ON d.archetype_id = a.id
                JOIN tournaments t ON d.tournament_id = t.id
                WHERE d.id = %(deck_id)s
            """
            
            cursor.execute(query, {"deck_id": deck_id})
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Deck not found")
            
            mainboard = [CardModel(**card) for card in row[8]]
            sideboard = [CardModel(**card) for card in row[9]] if row[9] else []
            
            return DecklistResponse(
                id=row[0],
                player=row[1],
                archetype=row[2],
                tournament_name=row[3],
                tournament_date=row[4],
                position=row[5],
                wins=row[6],
                losses=row[7],
                mainboard=mainboard,
                sideboard=sideboard
            )

@router.get("/search/cards", response_model=List[DecklistResponse])
async def search_decks_by_cards(
    cards: str = Query(..., description="Comma-separated list of card names"),
    format: Optional[str] = Query(None),
    limit: int = Query(10, le=50)
):
    """
    Search for decks containing specific cards.
    
    Example: `/api/decks/search/cards?cards=Lightning Bolt,Ragavan&format=modern`
    """
    
    card_list = [c.strip() for c in cards.split(",")]
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Build query to find decks containing all specified cards
            query = """
                WITH card_search AS (
                    SELECT d.id
                    FROM decklists d
                    JOIN tournaments t ON d.tournament_id = t.id
                    JOIN formats f ON t.format_id = f.id
                    WHERE 1=1
            """
            
            params = {"limit": limit}
            
            if format:
                query += " AND f.name = %(format)s"
                params["format"] = format
            
            # Add card conditions
            for i, card in enumerate(card_list):
                param_name = f"card_{i}"
                query += f"""
                    AND EXISTS (
                        SELECT 1 FROM jsonb_array_elements(d.mainboard || COALESCE(d.sideboard, '[]'::jsonb)) AS c
                        WHERE c->>'name' ILIKE %({param_name})s
                    )
                """
                params[param_name] = f"%{card}%"
            
            query += """
                    ORDER BY t.date DESC
                    LIMIT %(limit)s
                )
                SELECT 
                    d.id::text,
                    p.name as player_name,
                    a.name as archetype_name,
                    t.name as tournament_name,
                    t.date,
                    d.position,
                    d.wins,
                    d.losses,
                    d.mainboard,
                    d.sideboard
                FROM decklists d
                JOIN card_search cs ON d.id = cs.id
                JOIN players p ON d.player_id = p.id
                JOIN archetypes a ON d.archetype_id = a.id
                JOIN tournaments t ON d.tournament_id = t.id
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                mainboard = [CardModel(**card) for card in row[8]]
                sideboard = [CardModel(**card) for card in row[9]] if row[9] else []
                
                items.append(DecklistResponse(
                    id=row[0],
                    player=row[1],
                    archetype=row[2],
                    tournament_name=row[3],
                    tournament_date=row[4],
                    position=row[5],
                    wins=row[6],
                    losses=row[7],
                    mainboard=mainboard,
                    sideboard=sideboard
                ))
            
            return items