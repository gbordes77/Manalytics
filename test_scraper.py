import asyncio
from datetime import datetime, timedelta
import sys
sys.path.append('/app')

from src.scrapers.mtgo_scraper import MTGOScraper

async def test_scraper():
    # Test with just 1 day
    scraper = MTGOScraper("standard")
    
    async with scraper:
        # July 24, 2025
        start_date = datetime(2025, 7, 24)
        end_date = datetime(2025, 7, 24)
        
        print(f"Testing scraper from {start_date} to {end_date}")
        tournaments = await scraper.scrape_tournaments(start_date, end_date)
        
        print(f"\nFound {len(tournaments)} tournaments")
        for t in tournaments:
            print(f"- {t['name']} on {t['date']} with {len(t.get('decklists', []))} decks")

if __name__ == "__main__":
    asyncio.run(test_scraper())