#!/usr/bin/env python3
"""
Test MTGO scraper for early July dates.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.scrapers.mtgo_scraper import MTGOScraper
from src.utils.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

async def test_mtgo_early_july():
    """Test MTGO scraper for July 1-7."""
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 7)
    
    logger.info(f"Testing MTGO scraper from {start_date.date()} to {end_date.date()}")
    
    mtgo_scraper = MTGOScraper("standard")
    async with mtgo_scraper:
        tournaments = await mtgo_scraper.scrape_tournaments(start_date, end_date)
        
        logger.info(f"\nFound {len(tournaments)} tournaments:")
        for t in tournaments:
            logger.info(f"  {t['date']} - {t['name']} - {len(t.get('decklists', []))} decks")
            logger.info(f"    URL: {t['url']}")
        
        # Check if we can access one of the early July tournaments
        if tournaments:
            first_tournament = tournaments[0]
            logger.info(f"\nFirst tournament details:")
            logger.info(f"  Name: {first_tournament['name']}")
            logger.info(f"  Date: {first_tournament['date']}")
            logger.info(f"  URL: {first_tournament['url']}")
            logger.info(f"  Decklists: {len(first_tournament.get('decklists', []))}")
            
            # Show first decklist if available
            if first_tournament.get('decklists'):
                first_deck = first_tournament['decklists'][0]
                logger.info(f"\n  First deck:")
                logger.info(f"    Player: {first_deck.get('player', 'Unknown')}")
                logger.info(f"    Mainboard cards: {len(first_deck.get('mainboard', []))}")
                logger.info(f"    Sideboard cards: {len(first_deck.get('sideboard', []))}")

if __name__ == "__main__":
    asyncio.run(test_mtgo_early_july())