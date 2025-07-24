import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch

logger = logging.getLogger(__name__)

def save_tournament_results(conn: psycopg2.extensions.connection, tournament_data: Dict[str, Any]) -> Optional[str]:
    """
    Save tournament and decklist data to the database with robust error handling.
    Uses bulk inserts for performance.
    """
    try:
        with conn.cursor() as cursor:
            # Get format and source IDs
            format_id = get_or_create_format(cursor, tournament_data['format'])
            source_id = get_or_create_source(cursor, tournament_data['source'])
            
            # Create or get tournament
            tournament_id = create_or_get_tournament(
                cursor, 
                source_id, 
                format_id,
                tournament_data['name'],
                tournament_data['date'],
                tournament_data.get('url'),
                tournament_data.get('raw_data')
            )
            
            if not tournament_id:
                logger.error(f"Failed to create/get tournament: {tournament_data['name']}")
                return None
            
            # Prepare bulk data for players and decks
            player_data = []
            deck_data = []
            
            for decklist in tournament_data.get('decklists', []):
                player_name = decklist['player']
                player_data.append((player_name, None))  # (name, mtgo_username)
                
                # Get archetype ID
                archetype_id = get_or_create_archetype(
                    cursor,
                    format_id,
                    decklist.get('archetype', 'Unknown'),
                    decklist.get('archetype', 'Unknown')
                )
                
                deck_data.append({
                    'tournament_id': tournament_id,
                    'player_name': player_name,
                    'archetype_id': archetype_id,
                    'position': decklist.get('position'),
                    'wins': decklist.get('wins'),
                    'losses': decklist.get('losses'),
                    'draws': decklist.get('draws'),
                    'mainboard': json.dumps(decklist['mainboard']),
                    'sideboard': json.dumps(decklist.get('sideboard', [])),
                    'original_archetype': decklist.get('archetype'),
                    'detection_method': decklist.get('detection_method', 'unknown'),
                    'confidence_score': decklist.get('confidence', 0.0)
                })
            
            # Bulk insert players
            if player_data:
                execute_batch(
                    cursor,
                    """
                    INSERT INTO players (name, mtgo_username) 
                    VALUES (%s, %s) 
                    ON CONFLICT (name, mtgo_username) DO NOTHING
                    """,
                    player_data
                )
            
            # Get player IDs
            player_ids = {}
            for player_name, _ in player_data:
                cursor.execute("SELECT id FROM players WHERE name = %s", (player_name,))
                result = cursor.fetchone()
                if result:
                    player_ids[player_name] = result[0]
            
            # Bulk insert decklists
            if deck_data:
                decklist_values = []
                for deck in deck_data:
                    player_id = player_ids.get(deck['player_name'])
                    if player_id:
                        decklist_values.append((
                            deck['tournament_id'],
                            player_id,
                            deck['archetype_id'],
                            deck['position'],
                            deck['wins'],
                            deck['losses'],
                            deck['draws'],
                            deck['mainboard'],
                            deck['sideboard'],
                            deck['original_archetype'],
                            deck['detection_method'],
                            deck['confidence_score']
                        ))
                
                execute_batch(
                    cursor,
                    """
                    INSERT INTO decklists (
                        tournament_id, player_id, archetype_id, position,
                        wins, losses, draws, mainboard, sideboard,
                        original_archetype, detection_method, confidence_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tournament_id, player_id) DO NOTHING
                    """,
                    decklist_values
                )
            
            conn.commit()
            logger.info(f"Successfully saved tournament: {tournament_data['name']} with {len(deck_data)} decks")
            return tournament_id
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving tournament data: {e}")
        return None

def get_or_create_format(cursor, format_name: str) -> int:
    """Get or create a format in the database."""
    cursor.execute("SELECT id FROM formats WHERE name = %s", (format_name.lower(),))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute(
            "INSERT INTO formats (name, display_name) VALUES (%s, %s) RETURNING id",
            (format_name.lower(), format_name.title())
        )
        return cursor.fetchone()[0]

def get_or_create_source(cursor, source_name: str) -> int:
    """Get or create a source in the database."""
    cursor.execute("SELECT id FROM sources WHERE name = %s", (source_name.lower(),))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute(
            "INSERT INTO sources (name) VALUES (%s) RETURNING id",
            (source_name.lower(),)
        )
        return cursor.fetchone()[0]

def get_or_create_archetype(cursor, format_id: int, name: str, display_name: str) -> int:
    """Get or create an archetype in the database."""
    cursor.execute(
        "SELECT id FROM archetypes WHERE format_id = %s AND name = %s",
        (format_id, name)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute(
            """
            INSERT INTO archetypes (format_id, name, display_name) 
            VALUES (%s, %s, %s) RETURNING id
            """,
            (format_id, name, display_name)
        )
        return cursor.fetchone()[0]

def create_or_get_tournament(cursor, source_id: int, format_id: int, name: str, 
                           date: str, url: Optional[str], raw_data: Optional[Dict]) -> Optional[str]:
    """Create or get a tournament, returning its UUID."""
    # Check if tournament already exists
    cursor.execute(
        """
        SELECT id FROM tournaments 
        WHERE source_id = %s AND name = %s AND date = %s
        """,
        (source_id, name, date)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new tournament
    try:
        cursor.execute(
            """
            INSERT INTO tournaments (source_id, format_id, name, date, url, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (source_id, format_id, name, date, url, json.dumps(raw_data) if raw_data else None)
        )
        return cursor.fetchone()[0]
    except psycopg2.IntegrityError as e:
        logger.warning(f"Tournament already exists: {name} on {date}")
        # Try to get it again
        cursor.execute(
            """
            SELECT id FROM tournaments 
            WHERE source_id = %s AND name = %s AND date = %s
            """,
            (source_id, name, date)
        )
        result = cursor.fetchone()
        return result[0] if result else None