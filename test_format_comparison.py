#!/usr/bin/env python3
"""
Compare Standard vs Modern MTGO pages to understand the difference.
"""
import re
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_and_analyze(session, url, format_name):
    """Fetch and analyze a tournament page."""
    print(f"\n{'='*60}")
    print(f"Analyzing {format_name}: {url}")
    print('='*60)
    
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Error: Status {response.status}")
                return
            
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Check page title
            title = soup.title.string if soup.title else "No title"
            print(f"Page title: {title}")
            
            # 2. Look for scripts
            scripts = soup.find_all('script')
            print(f"Number of script tags: {len(scripts)}")
            
            # 3. Check for window.MTGO.decklists.data
            mtgo_data_found = False
            if 'window.MTGO.decklists.data' in content:
                print("✓ Found window.MTGO.decklists.data")
                mtgo_data_found = True
                
                # Extract and parse it
                match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        if 'decklists' in data:
                            print(f"  Contains {len(data['decklists'])} decklists")
                    except:
                        print("  Failed to parse JSON")
            else:
                print("✗ No window.MTGO.decklists.data found")
            
            # 4. Look for other window assignments
            window_vars = re.findall(r'window\.(\w+)\s*=', content)
            if window_vars:
                print(f"\nOther window variables found: {set(window_vars)}")
            
            # 5. Look for deck-related patterns
            deck_patterns = [
                (r'"player"\s*:', 'player references'),
                (r'"loginName"\s*:', 'loginName references'),
                (r'"cardName"\s*:', 'cardName references'),
                (r'"mainboard"\s*:', 'mainboard references'),
                (r'"sideboard"\s*:', 'sideboard references'),
                (r'"cards"\s*:', 'cards array references'),
                (r'"decklists"\s*:', 'decklists references')
            ]
            
            print("\nDeck-related patterns found:")
            for pattern, description in deck_patterns:
                count = len(re.findall(pattern, content))
                if count > 0:
                    print(f"  {description}: {count}")
            
            # 6. Check for JavaScript frameworks/libraries
            if 'React' in content:
                print("\n✓ React detected")
            if '__NEXT_DATA__' in content:
                print("✓ Next.js detected")
                
                # Try to extract Next.js data
                next_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>', content)
                if next_match:
                    try:
                        next_data = json.loads(next_match.group(1))
                        print(f"  Next.js data contains {len(next_data)} keys")
                        
                        # Look for props
                        if 'props' in next_data and 'pageProps' in next_data['props']:
                            page_props = next_data['props']['pageProps']
                            print(f"  pageProps keys: {list(page_props.keys())[:5]}...")
                            
                            # Check for deck data in pageProps
                            for key in page_props:
                                if 'deck' in key.lower() or 'list' in key.lower():
                                    print(f"    Found potential deck data in: {key}")
                                    if isinstance(page_props[key], list):
                                        print(f"      Contains {len(page_props[key])} items")
                    except:
                        print("  Failed to parse Next.js data")
            
            # 7. Look for API endpoints
            api_patterns = re.findall(r'["\'](/api/[^"\']+)["\']', content)
            if api_patterns:
                print(f"\nAPI endpoints found: {set(api_patterns)[:5]}...")
            
            # 8. Check meta tags for clues
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('property') == 'og:url':
                    print(f"\nCanonical URL: {meta.get('content')}")
                    
    except Exception as e:
        print(f"Error analyzing {format_name}: {e}")

async def main():
    """Compare Standard and Modern tournament pages."""
    
    # Test URLs from today and yesterday
    test_cases = [
        ("https://www.mtgo.com/decklist/standard-league-2025-07-249382", "Standard League"),
        ("https://www.mtgo.com/decklist/modern-league-2025-07-249358", "Modern League"),
        ("https://www.mtgo.com/decklist/standard-challenge-32-2025-07-2412804854", "Standard Challenge"),
        ("https://www.mtgo.com/decklist/modern-challenge-32-2025-07-2312804943", "Modern Challenge")
    ]
    
    async with aiohttp.ClientSession() as session:
        for url, format_name in test_cases:
            await fetch_and_analyze(session, url, format_name)
            await asyncio.sleep(1)  # Be polite

if __name__ == "__main__":
    asyncio.run(main())