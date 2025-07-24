#!/usr/bin/env python3
"""
Simple test to check MTGO URL patterns without full scraper dependencies.
"""
import re
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

async def fetch_url(session, url):
    """Fetch URL content."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

async def analyze_mtgo_formats():
    """Analyze MTGO website structure for different formats."""
    base_url = "https://www.mtgo.com"
    decklists_url = f"{base_url}/decklists"
    
    async with aiohttp.ClientSession() as session:
        print(f"Fetching: {decklists_url}")
        content = await fetch_url(session, decklists_url)
        
        if not content:
            print("Failed to fetch decklists page")
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all links containing /decklist/
        all_links = soup.find_all('a', href=re.compile(r'/decklist/'))
        
        format_patterns = {
            "standard": [],
            "modern": [],
            "legacy": [],
            "vintage": [],
            "pioneer": [],
            "pauper": []
        }
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            for fmt in format_patterns:
                if f'/decklist/{fmt}' in href:
                    format_patterns[fmt].append({
                        'href': href,
                        'text': text
                    })
        
        print("\n=== MTGO Format Analysis ===")
        for fmt, links in format_patterns.items():
            print(f"\n{fmt.upper()}: {len(links)} links found")
            if links:
                # Show recent examples
                recent_links = []
                for link in links[:10]:  # Check first 10
                    # Extract date from URL
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', link['href'])
                    if date_match:
                        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                        recent_links.append((date_str, link))
                
                # Sort by date and show most recent
                recent_links.sort(key=lambda x: x[0], reverse=True)
                for date_str, link in recent_links[:3]:
                    print(f"  {date_str}: {link['text'][:50]}...")
                    print(f"    URL: {base_url}{link['href']}")
        
        # Test specific URLs
        print("\n=== Testing Specific Tournament Pages ===")
        
        # Find one Standard and one Modern tournament from recent dates
        test_urls = {}
        
        for fmt in ["standard", "modern"]:
            pattern = f'/decklist/{fmt}'
            fmt_links = soup.find_all('a', href=re.compile(pattern))
            
            for link in fmt_links:
                href = link.get('href', '')
                # Look for July 2025 tournaments
                if '2025-07' in href:
                    test_urls[fmt] = base_url + href
                    break
        
        # Test each URL
        for fmt, url in test_urls.items():
            print(f"\nTesting {fmt.upper()} tournament: {url}")
            
            content = await fetch_url(session, url)
            if content:
                # Check for window.MTGO.decklists.data
                match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        deck_count = len(data.get('decklists', []))
                        print(f"  ✓ Found window.MTGO.decklists.data with {deck_count} decklists")
                    except:
                        print(f"  ✗ Found window.MTGO.decklists.data but failed to parse JSON")
                else:
                    print(f"  ✗ No window.MTGO.decklists.data found")
                    
                    # Check page structure
                    soup_page = BeautifulSoup(content, 'html.parser')
                    print(f"  Page title: {soup_page.title.string if soup_page.title else 'No title'}")
                    
                    # Look for any deck-related content
                    deck_elements = soup_page.find_all(class_=re.compile(r'deck|list', re.I))
                    print(f"  Found {len(deck_elements)} elements with 'deck' or 'list' in class")
            else:
                print(f"  ✗ Failed to fetch URL")

if __name__ == "__main__":
    asyncio.run(analyze_mtgo_formats())