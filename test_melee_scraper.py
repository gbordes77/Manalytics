#\!/usr/bin/env python3
import asyncio
import logging
from src.scrapers.melee_scraper import MeleeScraper

logging.basicConfig(level=logging.INFO)

async def test_melee():
    scraper = MeleeScraper("standard")
    tournaments = await scraper.run(days_back=3)
    print(f"Found {len(tournaments)} tournaments")
    for t in tournaments:
        print(f"- {t['name']} ({len(t.get('decklists', []))} decks)")
    return tournaments

if __name__ == "__main__":
    results = asyncio.run(test_melee())
EOF < /dev/null