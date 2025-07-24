#!/usr/bin/env python3
"""
Simple Melee scraper runner.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger(__name__)

async def run_melee():
    """Run Melee scraper."""
    from src.scrapers.melee_scraper import MeleeScraper
    from database.db_pool import init_db_pool, get_db_connection
    
    # Initialize DB pool
    init_db_pool()
    
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 24)
    
    logger.info(f"Running Melee scraper from {start_date} to {end_date}")
    
    scraper = MeleeScraper("standard")
    
    try:
        async with scraper:
            tournaments = await scraper.scrape_tournaments(start_date, end_date)
            
            logger.info(f"Found {len(tournaments)} Melee tournaments")
            
            # Save to database
            saved = 0
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get format and source IDs
                cursor.execute("SELECT id FROM manalytics.formats WHERE name = 'standard'")
                format_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM manalytics.sources WHERE name = 'melee'")
                source_id = cursor.fetchone()[0]
                
                for tournament in tournaments:
                    try:
                        # Check if tournament exists
                        cursor.execute(
                            "SELECT id FROM manalytics.tournaments WHERE url = %s",
                            (tournament['url'],)
                        )
                        
                        if not cursor.fetchone():
                            # Insert tournament
                            cursor.execute("""
                                INSERT INTO manalytics.tournaments (name, date, url, source_id, format_id, raw_data)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING id
                            """, (
                                tournament['name'],
                                datetime.strptime(tournament['date'], '%Y-%m-%d').date(),
                                tournament['url'],
                                source_id,
                                format_id,
                                str(tournament)
                            ))
                            
                            tournament_id = cursor.fetchone()[0]
                            saved += 1
                            
                            logger.info(f"Saved tournament: {tournament['name']} ({tournament['date']})")
                            
                            # Save decklists
                            for deck in tournament.get('decklists', []):
                                # Get or create player
                                cursor.execute(
                                    "SELECT id FROM manalytics.players WHERE name = %s",
                                    (deck.get('player', 'Unknown'),)
                                )
                                player_row = cursor.fetchone()
                                
                                if player_row:
                                    player_id = player_row[0]
                                else:
                                    cursor.execute(
                                        "INSERT INTO manalytics.players (name) VALUES (%s) RETURNING id",
                                        (deck.get('player', 'Unknown'),)
                                    )
                                    player_id = cursor.fetchone()[0]
                                
                                # Insert decklist
                                cursor.execute("""
                                    INSERT INTO manalytics.decklists (
                                        tournament_id, player_id, archetype_id,
                                        wins, losses, mainboard, sideboard
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    tournament_id,
                                    player_id,
                                    1,  # Default archetype
                                    deck.get('wins'),
                                    deck.get('losses'),
                                    str(deck.get('mainboard', [])),
                                    str(deck.get('sideboard', []))
                                ))
                        else:
                            logger.info(f"Tournament already exists: {tournament['name']}")
                    
                    except Exception as e:
                        logger.error(f"Error saving tournament: {e}")
                        conn.rollback()
                        continue
                    
                    conn.commit()
            
            logger.info(f"Successfully saved {saved} new Melee tournaments")
            
    except Exception as e:
        logger.error(f"Error running Melee scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_melee())