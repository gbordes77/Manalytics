#!/usr/bin/env python3
"""
Test that exactly mimics the MTGO scraper behavior for both formats.
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

async def test_both_formats():
    """Test both Standard and Modern scraping with same date range."""
    start_date = datetime(2025, 7, 20)
    end_date = datetime(2025, 7, 24)
    
    formats = ["standard", "modern"]
    
    for format_name in formats:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {format_name.upper()} format")
        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
        logger.info('='*60)
        
        scraper = MTGOScraper(format_name)
        
        try:
            async with scraper:
                tournaments = await scraper.scrape_tournaments(start_date, end_date)
                
                logger.info(f"\nSummary for {format_name}:")
                logger.info(f"  Total tournaments found: {len(tournaments)}")
                
                if tournaments:
                    total_decks = sum(len(t.get('decklists', [])) for t in tournaments)
                    logger.info(f"  Total decklists: {total_decks}")
                    
                    logger.info(f"\nTournament details:")
                    for t in tournaments:
                        deck_count = len(t.get('decklists', []))
                        logger.info(f"  {t['date']} - {t['name']} - {deck_count} decks")
                        logger.info(f"    URL: {t['url']}")
                        
                        # Show warning if tournament has very few decks
                        if deck_count < 5:
                            logger.warning(f"    ⚠️  Tournament has only {deck_count} decks!")
                else:
                    logger.warning(f"No tournaments found for {format_name}")
                    
        except Exception as e:
            logger.error(f"Error scraping {format_name}: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_both_formats())