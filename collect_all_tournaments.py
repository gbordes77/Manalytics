#!/usr/bin/env python3
"""
Collect all tournaments from July 1st to today for both MTGO and Melee.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.scrapers.mtgo_scraper import MTGOScraper
from src.scrapers.melee_scraper import MeleeScraper
from src.data.tournament_repository import TournamentRepository
from src.data.player_repository import PlayerRepository
from src.utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

async def collect_all_tournaments():
    """Collect all tournaments from both sources."""
    start_date = datetime(2025, 7, 1)
    end_date = datetime.now()
    
    logger.info(f"Collecting tournaments from {start_date.date()} to {end_date.date()}")
    
    # Initialize repositories
    tournament_repo = TournamentRepository()
    player_repo = PlayerRepository()
    
    # Collect MTGO tournaments
    logger.info("=== Collecting MTGO tournaments ===")
    mtgo_scraper = MTGOScraper("standard")
    try:
        mtgo_tournaments = await mtgo_scraper.scrape_tournaments(start_date, end_date)
        logger.info(f"Found {len(mtgo_tournaments)} MTGO tournaments")
        
        # Save MTGO tournaments
        for tournament in mtgo_tournaments:
            try:
                await tournament_repo.save_tournament(tournament)
                logger.info(f"Saved MTGO tournament: {tournament['name']} ({tournament['date']})")
            except Exception as e:
                logger.error(f"Error saving MTGO tournament: {e}")
    except Exception as e:
        logger.error(f"Error collecting MTGO tournaments: {e}")
    
    # Collect Melee tournaments
    logger.info("\n=== Collecting Melee tournaments ===")
    melee_scraper = MeleeScraper("standard")
    try:
        melee_tournaments = await melee_scraper.scrape_tournaments(start_date, end_date)
        logger.info(f"Found {len(melee_tournaments)} Melee tournaments")
        
        # Save Melee tournaments
        for tournament in melee_tournaments:
            try:
                await tournament_repo.save_tournament(tournament)
                logger.info(f"Saved Melee tournament: {tournament['name']} ({tournament['date']})")
            except Exception as e:
                logger.error(f"Error saving Melee tournament: {e}")
    except Exception as e:
        logger.error(f"Error collecting Melee tournaments: {e}")
    
    # Summary
    logger.info("\n=== Collection Summary ===")
    logger.info(f"Total MTGO tournaments: {len(mtgo_tournaments) if 'mtgo_tournaments' in locals() else 0}")
    logger.info(f"Total Melee tournaments: {len(melee_tournaments) if 'melee_tournaments' in locals() else 0}")

if __name__ == "__main__":
    asyncio.run(collect_all_tournaments())