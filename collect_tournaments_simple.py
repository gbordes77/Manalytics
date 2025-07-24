#!/usr/bin/env python3
"""
Simple script to collect all tournaments and save them.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import logging
from database.db_pool import DatabasePool
from src.scrapers.mtgo_scraper import MTGOScraper
from src.scrapers.melee_scraper import MeleeScraper
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def collect_and_save():
    """Collect and save tournaments."""
    start_date = datetime(2025, 7, 1)
    end_date = datetime.now()
    
    db_pool = DatabasePool()
    await db_pool.initialize()
    
    try:
        # Get format and source IDs
        async with db_pool.acquire() as conn:
            standard_format = await conn.fetchval("SELECT id FROM formats WHERE name = 'standard'")
            mtgo_source = await conn.fetchval("SELECT id FROM sources WHERE name = 'mtgo'")
            melee_source = await conn.fetchval("SELECT id FROM sources WHERE name = 'melee'")
        
        # Collect MTGO tournaments
        logger.info("=== Collecting MTGO tournaments ===")
        mtgo_scraper = MTGOScraper("standard")
        async with mtgo_scraper:
            mtgo_tournaments = await mtgo_scraper.scrape_tournaments(start_date, end_date)
            logger.info(f"Found {len(mtgo_tournaments)} MTGO tournaments")
            
            # Save MTGO tournaments directly
            async with db_pool.acquire() as conn:
                for tournament in mtgo_tournaments:
                    try:
                        # Check if tournament already exists
                        exists = await conn.fetchval(
                            "SELECT id FROM tournaments WHERE url = $1",
                            tournament['url']
                        )
                        
                        if not exists:
                            # Insert tournament
                            tournament_id = await conn.fetchval("""
                                INSERT INTO tournaments (name, date, url, source_id, format_id, raw_data)
                                VALUES ($1, $2, $3, $4, $5, $6)
                                RETURNING id
                            """, 
                            tournament['name'], 
                            datetime.strptime(tournament['date'], '%Y-%m-%d').date(),
                            tournament['url'],
                            mtgo_source,
                            standard_format,
                            json.dumps(tournament)
                            )
                            
                            logger.info(f"Saved MTGO tournament: {tournament['name']} ({tournament['date']})")
                            
                            # Save decklists
                            for deck in tournament.get('decklists', []):
                                # Insert player if not exists
                                player_id = await conn.fetchval("""
                                    INSERT INTO players (name) VALUES ($1)
                                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                                    RETURNING id
                                """, deck.get('player', 'Unknown'))
                                
                                # Insert decklist
                                await conn.execute("""
                                    INSERT INTO decklists (
                                        tournament_id, player_id, archetype_id, 
                                        wins, losses, mainboard, sideboard
                                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                                """,
                                tournament_id,
                                player_id,
                                1,  # Default archetype
                                deck.get('wins'),
                                deck.get('losses'),
                                json.dumps(deck.get('mainboard', [])),
                                json.dumps(deck.get('sideboard', []))
                                )
                        else:
                            logger.info(f"Tournament already exists: {tournament['name']} ({tournament['date']})")
                    
                    except Exception as e:
                        logger.error(f"Error saving MTGO tournament {tournament['name']}: {e}")
        
        # Collect Melee tournaments
        logger.info("\n=== Collecting Melee tournaments ===")
        melee_scraper = MeleeScraper("standard")
        async with melee_scraper:
            try:
                melee_tournaments = await melee_scraper.scrape_tournaments(start_date, end_date)
                logger.info(f"Found {len(melee_tournaments)} Melee tournaments")
                
                # Save Melee tournaments
                async with db_pool.acquire() as conn:
                    for tournament in melee_tournaments:
                        try:
                            # Check if tournament already exists
                            exists = await conn.fetchval(
                                "SELECT id FROM tournaments WHERE url = $1",
                                tournament['url']
                            )
                            
                            if not exists:
                                # Insert tournament
                                tournament_id = await conn.fetchval("""
                                    INSERT INTO tournaments (name, date, url, source_id, format_id, raw_data)
                                    VALUES ($1, $2, $3, $4, $5, $6)
                                    RETURNING id
                                """, 
                                tournament['name'], 
                                datetime.strptime(tournament['date'], '%Y-%m-%d').date(),
                                tournament['url'],
                                melee_source,
                                standard_format,
                                json.dumps(tournament)
                                )
                                
                                logger.info(f"Saved Melee tournament: {tournament['name']} ({tournament['date']})")
                                
                                # Save decklists
                                for deck in tournament.get('decklists', []):
                                    # Insert player if not exists
                                    player_id = await conn.fetchval("""
                                        INSERT INTO players (name) VALUES ($1)
                                        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                                        RETURNING id
                                    """, deck.get('player', 'Unknown'))
                                    
                                    # Insert decklist
                                    await conn.execute("""
                                        INSERT INTO decklists (
                                            tournament_id, player_id, archetype_id, 
                                            wins, losses, mainboard, sideboard
                                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                                    """,
                                    tournament_id,
                                    player_id,
                                    1,  # Default archetype
                                    deck.get('wins'),
                                    deck.get('losses'),
                                    json.dumps(deck.get('mainboard', [])),
                                    json.dumps(deck.get('sideboard', []))
                                    )
                            else:
                                logger.info(f"Tournament already exists: {tournament['name']} ({tournament['date']})")
                        
                        except Exception as e:
                            logger.error(f"Error saving Melee tournament {tournament['name']}: {e}")
            
            except Exception as e:
                logger.error(f"Error collecting Melee tournaments: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        await db_pool.close()
    
    # Summary
    logger.info("\n=== Final Summary ===")
    db_pool2 = DatabasePool()
    await db_pool2.initialize()
    async with db_pool2.acquire() as conn:
        mtgo_count = await conn.fetchval("""
            SELECT COUNT(*) FROM tournaments t 
            JOIN sources s ON t.source_id = s.id 
            WHERE s.name = 'mtgo' AND t.date >= '2025-07-01'
        """)
        melee_count = await conn.fetchval("""
            SELECT COUNT(*) FROM tournaments t 
            JOIN sources s ON t.source_id = s.id 
            WHERE s.name = 'melee' AND t.date >= '2025-07-01'
        """)
        total_decks = await conn.fetchval("""
            SELECT COUNT(*) FROM decklists d
            JOIN tournaments t ON d.tournament_id = t.id
            WHERE t.date >= '2025-07-01'
        """)
    await db_pool2.close()
    
    logger.info(f"Total MTGO tournaments in DB: {mtgo_count}")
    logger.info(f"Total Melee tournaments in DB: {melee_count}")
    logger.info(f"Total decks in DB: {total_decks}")

if __name__ == "__main__":
    import json  # Make sure json is imported at module level
    asyncio.run(collect_and_save())