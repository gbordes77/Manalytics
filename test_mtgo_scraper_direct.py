#!/usr/bin/env python3
"""
Direct test of MTGO scraper without database dependencies.
"""
import asyncio
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp

async def test_mtgo_scraper():
    """Test MTGO scraping logic directly."""
    base_url = "https://www.mtgo.com"
    decklists_url = f"{base_url}/decklists"
    
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 31)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Get the decklists page
        print(f"Fetching decklists page: {decklists_url}")
        async with session.get(decklists_url) as response:
            if response.status != 200:
                print(f"Failed to fetch decklists page: {response.status}")
                return
            content = await response.text()
        
        # Step 2: Parse to find tournament links
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all decklist links for standard format
        all_links = soup.find_all('a', href=re.compile(f'/decklist/standard'))
        tournament_links = []
        
        print(f"\nFound {len(all_links)} standard links total")
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # Extract date from href
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', href)
            if date_match:
                try:
                    link_date = datetime(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3))
                    )
                    if start_date <= link_date <= end_date:
                        full_url = f"{base_url}{href}"
                        tournament_links.append((full_url, link_text, link_date.strftime('%Y-%m-%d')))
                except ValueError:
                    pass
        
        print(f"\nFound {len(tournament_links)} tournament links for July 2025")
        
        # Show all found tournaments
        for url, title, date_str in sorted(tournament_links, key=lambda x: x[2]):
            print(f"  {date_str}: {title}")
            print(f"    URL: {url}")
        
        # Test scraping one tournament
        if tournament_links:
            test_url, test_title, test_date = tournament_links[0]
            print(f"\n=== Testing tournament scraping ===")
            print(f"URL: {test_url}")
            
            async with session.get(test_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract data from window.MTGO.decklists.data
                    match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            decklists = data.get('decklists', [])
                            print(f"✓ Found {len(decklists)} decklists")
                            
                            if decklists:
                                # Show first deck
                                first_deck = decklists[0]
                                print(f"\nFirst deck example:")
                                print(f"  Player: {first_deck.get('player', 'Unknown')}")
                                print(f"  Main deck cards: {len(first_deck.get('main_deck', []))}")
                                print(f"  Sideboard cards: {len(first_deck.get('sideboard_deck', []))}")
                        except json.JSONDecodeError as e:
                            print(f"✗ Failed to parse JSON: {e}")
                    else:
                        print("✗ No window.MTGO.decklists.data found")
                else:
                    print(f"✗ Failed to fetch tournament page: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_mtgo_scraper())