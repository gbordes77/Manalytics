#!/usr/bin/env python3
"""Test du nouveau scraper Melee avec Selenium."""
import asyncio
import logging
from datetime import datetime, timedelta
from src.scrapers.melee_scraper import MeleeScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def test_melee_scraper():
    """Test du nouveau scraper Melee."""
    print("🧪 Testing new Melee scraper with Selenium authentication...")
    
    format_name = "modern"
    days_back = 7
    
    try:
        async with MeleeScraper(format_name) as scraper:
            if not scraper.cookies:
                print("❌ Authentication failed - no cookies retrieved")
                return
            
            print(f"✅ Authentication successful - {len(scraper.cookies)} cookies retrieved")
            
            # Test scraping
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            print(f"🔍 Searching for {format_name} tournaments from {start_date.date()} to {end_date.date()}")
            
            tournaments = await scraper.scrape_tournaments(start_date, end_date)
            
            print(f"\n🏆 Results:")
            print(f"  - Found {len(tournaments)} tournaments")
            
            if tournaments:
                print(f"\n📋 Tournament details:")
                for i, tournament in enumerate(tournaments[:5]):  # Show first 5
                    print(f"  {i+1}. {tournament['name']}")
                    print(f"     Date: {tournament['date']}")
                    print(f"     Decklists: {len(tournament.get('decklists', []))}")
                    print(f"     URL: {tournament['url']}")
                    print()
            else:
                print("  No tournaments found for the specified period")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_melee_scraper())