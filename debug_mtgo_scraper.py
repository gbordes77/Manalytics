#!/usr/bin/env python3
"""
Debug MTGO scraper to understand why it returns 0 tournaments.
"""
import asyncio
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_mtgo_scraper():
    """Debug MTGO scraper step by step."""
    
    # Import after setting up logging
    from src.scrapers.mtgo_scraper import MTGOScraper
    
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 31)
    
    logger.info(f"Testing MTGO scraper from {start_date.date()} to {end_date.date()}")
    
    scraper = MTGOScraper("standard")
    
    # Check basic configuration
    logger.info(f"Format name: {scraper.format_name}")
    logger.info(f"Base URL: {scraper.base_url}")
    logger.info(f"Format mapping: {scraper.format_mapping}")
    
    async with scraper:
        # Test the scraping
        logger.info("Starting tournament scrape...")
        tournaments = await scraper.scrape_tournaments(start_date, end_date)
        
        logger.info(f"\nFound {len(tournaments)} tournaments")
        
        if tournaments:
            for i, t in enumerate(tournaments[:5]):  # Show first 5
                logger.info(f"\nTournament {i+1}:")
                logger.info(f"  Name: {t['name']}")
                logger.info(f"  Date: {t['date']}")
                logger.info(f"  URL: {t['url']}")
                logger.info(f"  Decklists: {len(t.get('decklists', []))}")
        else:
            logger.warning("No tournaments found!")
            
            # Let's try to fetch the decklists page directly
            logger.info("\nTrying to fetch decklists page directly...")
            import httpx
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{scraper.base_url}/decklists")
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text
                        logger.info(f"Page content length: {len(content)}")
                        
                        # Check if we find any standard links
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Find all links containing /decklist/standard
                        import re
                        standard_links = soup.find_all('a', href=re.compile('/decklist/standard'))
                        logger.info(f"Found {len(standard_links)} standard tournament links")
                        
                        if standard_links:
                            # Show first few
                            for link in standard_links[:3]:
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                logger.info(f"  Link: {href} - {text}")
                        
                except Exception as e:
                    logger.error(f"Error fetching page: {e}")

if __name__ == "__main__":
    asyncio.run(debug_mtgo_scraper())