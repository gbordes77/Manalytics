#!/usr/bin/env python3
"""
Insert test data for demonstration purposes.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
import json
from database.db_pool import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_test_data():
    """Insert test tournaments and decklists."""
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Get format IDs
            cursor.execute("SELECT id, name FROM manalytics.formats")
            formats = {name: id for id, name in cursor.fetchall()}
            
            # Get source IDs
            cursor.execute("SELECT id, name FROM manalytics.sources")
            sources = {name: id for id, name in cursor.fetchall()}
            
            # Get archetype IDs
            cursor.execute("SELECT id, name FROM manalytics.archetypes WHERE format_id = %s", (formats['modern'],))
            archetypes = [(id, name) for id, name in cursor.fetchall()]
            
            if not archetypes:
                logger.error("No archetypes found for modern format")
                return
            
            # Insert test tournaments
            tournament_ids = []
            for i in range(5):
                date = datetime.now().date() - timedelta(days=i)
                cursor.execute("""
                    INSERT INTO manalytics.tournaments (name, date, players_count, format_id, source_id, url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    f"Test Modern League {date}",
                    date,
                    random.randint(50, 200),
                    formats['modern'],
                    sources['mtgo'],
                    f"https://example.com/tournament/{i}"
                ))
                tournament_ids.append(cursor.fetchone()[0])
            
            # Insert test players
            player_ids = []
            for i in range(20):
                cursor.execute("""
                    INSERT INTO manalytics.players (name)
                    VALUES (%s)
                    RETURNING id
                """, (f"TestPlayer{i}",))
                player_ids.append(cursor.fetchone()[0])
            
            # Insert test decklists
            deck_count = 0
            for tournament_id in tournament_ids:
                for position in range(1, 33):  # Top 32
                    archetype_id, archetype_name = random.choice(archetypes)
                    player_id = random.choice(player_ids)
                    wins = random.randint(3, 5)
                    losses = random.randint(0, 2)
                    
                    # Simple mainboard
                    mainboard = [
                        {"name": "Lightning Bolt", "quantity": 4},
                        {"name": "Ragavan, Nimble Pilferer", "quantity": 4},
                        {"name": "Dragon's Rage Channeler", "quantity": 4},
                        {"name": "Mountain", "quantity": 20}
                    ]
                    
                    sideboard = [
                        {"name": "Alpine Moon", "quantity": 2},
                        {"name": "Shattering Spree", "quantity": 2}
                    ]
                    
                    cursor.execute("""
                        INSERT INTO manalytics.decklists 
                        (tournament_id, player_id, archetype_id, position, wins, losses, mainboard, sideboard)
                        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                    """, (
                        tournament_id,
                        player_id,
                        archetype_id,
                        position,
                        wins,
                        losses,
                        json.dumps(mainboard),
                        json.dumps(sideboard)
                    ))
                    deck_count += 1
            
            conn.commit()
            logger.info(f"Inserted {len(tournament_ids)} tournaments and {deck_count} decklists")

if __name__ == "__main__":
    insert_test_data()