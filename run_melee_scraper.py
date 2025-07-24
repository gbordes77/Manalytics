#!/usr/bin/env python3
"""
Run Melee scraper for Standard format.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.scrapers.melee_scraper import MeleeScraper
from src.data.tournament_repository import TournamentRepository
from src.utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

async def run_melee_scraper():
    """Run the Melee scraper."""
    start_date = datetime(2025, 7, 1)
    end_date = datetime.now()
    
    logger.info(f"Collecting Melee tournaments from {start_date.date()} to {end_date.date()}")
    
    # Initialize repository
    tournament_repo = TournamentRepository()
    
    # Create Melee scraper
    melee_scraper = MeleeScraper("standard")
    
    try:
        # Scrape tournaments
        tournaments = await melee_scraper.scrape_tournaments(start_date, end_date)
        logger.info(f"Found {len(tournaments)} Melee tournaments")
        
        # Save each tournament
        saved_count = 0
        for tournament in tournaments:
            try:
                await tournament_repo.save_tournament(tournament)
                saved_count += 1
                logger.info(f"Saved Melee tournament: {tournament['name']} ({tournament['date']})")
            except Exception as e:
                logger.error(f"Error saving tournament {tournament['name']}: {e}")
        
        logger.info(f"Successfully saved {saved_count}/{len(tournaments)} Melee tournaments")
        
    except Exception as e:
        logger.error(f"Error running Melee scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_melee_scraper())