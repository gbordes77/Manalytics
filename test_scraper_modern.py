#!/usr/bin/env python3
"""
Test the MTGO scraper specifically for Modern format to diagnose the issue.
"""
import asyncio
import sys
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp

# Simple test without full scraper dependencies
async def test_modern_scraping():
    """Test Modern tournament scraping step by step."""
    
    base_url = "https://www.mtgo.com"
    decklists_url = f"{base_url}/decklists"
    format_slug = "modern"
    
    # Date range for testing
    start_date = datetime(2025, 7, 20)
    end_date = datetime(2025, 7, 24)
    
    print(f"Testing Modern scraping from {start_date.date()} to {end_date.date()}")
    print(f"Format slug: {format_slug}")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Fetch decklists page
        print(f"\nStep 1: Fetching {decklists_url}")
        
        async with session.get(decklists_url) as response:
            if response.status != 200:
                print(f"Error: Status {response.status}")
                return
            
            content = await response.text()
        
        # Step 2: Parse and find Modern links
        print("\nStep 2: Parsing for Modern tournament links")
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all links matching the Modern format
        pattern = f'/decklist/{format_slug}'
        all_links = soup.find_all('a', href=re.compile(pattern))
        print(f"Found {len(all_links)} links matching pattern '{pattern}'")
        
        # Step 3: Filter by date
        print("\nStep 3: Filtering by date range")
        tournament_links = []
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # Debug first few links
            if len(tournament_links) < 3:
                print(f"\nChecking link: {href}")
                print(f"  Text: {link_text[:50]}...")
            
            # Extract date from href
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', href)
            if date_match:
                try:
                    link_date = datetime(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3))
                    )
                    
                    if len(tournament_links) < 3:
                        print(f"  Date found: {link_date.date()}")
                        print(f"  In range? {start_date <= link_date <= end_date}")
                    
                    if start_date <= link_date <= end_date:
                        full_url = base_url + href if href.startswith('/') else href
                        tournament_links.append({
                            'url': full_url,
                            'text': link_text,
                            'date': link_date.strftime('%Y-%m-%d')
                        })
                except ValueError as e:
                    print(f"  Date parse error: {e}")
        
        print(f"\nFound {len(tournament_links)} Modern tournaments in date range")
        
        # Step 4: Show all found tournaments
        if tournament_links:
            print("\nModern tournaments found:")
            for t in tournament_links:
                print(f"  {t['date']}: {t['text'][:50]}...")
                print(f"    URL: {t['url']}")
        
        # Step 5: Test scraping one tournament
        if tournament_links:
            print("\nStep 5: Testing data extraction from first tournament")
            first = tournament_links[0]
            
            async with session.get(first['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for window.MTGO.decklists.data
                    if 'window.MTGO.decklists.data' in content:
                        print("✓ Found window.MTGO.decklists.data")
                        
                        match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
                        if match:
                            import json
                            try:
                                data = json.loads(match.group(1))
                                if 'decklists' in data:
                                    print(f"✓ Successfully extracted {len(data['decklists'])} decklists")
                                else:
                                    print("✗ No 'decklists' key in data")
                            except json.JSONDecodeError:
                                print("✗ Failed to parse JSON")
                    else:
                        print("✗ No window.MTGO.decklists.data found")
                else:
                    print(f"✗ Failed to fetch tournament page: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_modern_scraping())