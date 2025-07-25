#!/usr/bin/env python3
"""
Scraper MTGO minimal pour tester
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import re
import time


def scrape_mtgo_standard():
    """Scrape MTGO Standard tournaments"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Get main page
    url = "https://www.mtgo.com/decklists"
    print(f"🔍 Fetching: {url}")
    
    response = session.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to get main page: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Debug - save page
    with open('mtgo_page_debug.html', 'w') as f:
        f.write(response.text)
    print("💾 Saved page to mtgo_page_debug.html for inspection")
    
    # Find tournament links
    links = soup.find_all('a', href=True)
    tournament_links = []
    
    print(f"📊 Total links found: {len(links)}")
    
    for link in links:
        href = link.get('href', '')
        text = link.text.strip()
        
        # Debug first few links
        if len(tournament_links) < 5 and '/decklist/' in href:
            print(f"  Link: {href} - Text: {text[:50]}")
        
        # Look for tournament links (skip /en prefix)
        if '/decklist/' in href and not href.startswith('/en/'):
            tournament_links.append({
                'url': 'https://www.mtgo.com' + href,
                'name': text,
                'tournament_id': href.split('/')[-1]
            })
    
    print(f"✅ Found {len(tournament_links)} tournament links")
    
    # Filter for Standard
    standard_tournaments = []
    for t in tournament_links:
        if 'standard' in t['name'].lower():
            standard_tournaments.append(t)
    
    print(f"✅ Found {len(standard_tournaments)} Standard tournaments")
    tournament_links = standard_tournaments
    
    # Create output directory
    output_dir = Path("data/raw/mtgo/standard")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each tournament
    for i, tournament in enumerate(tournament_links[:5]):  # Limit to 5 for testing
        print(f"\n📊 Processing {i+1}/{min(5, len(tournament_links))}: {tournament['name']}")
        
        try:
            # Get tournament page
            tourn_response = session.get(tournament['url'])
            if tourn_response.status_code != 200:
                print(f"  ❌ Failed to get tournament: {tourn_response.status_code}")
                continue
                
            tourn_soup = BeautifulSoup(tourn_response.text, 'html.parser')
            
            # Extract basic info
            tournament_data = {
                'source': 'mtgo',
                'format': 'standard',
                'name': tournament['name'],
                'url': tournament['url'],
                'tournament_id': tournament['tournament_id'],
                'scraped_at': datetime.now().isoformat(),
                'decklists': []
            }
            
            # Extract date from title if possible
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', tournament['name'])
            if date_match:
                tournament_data['date'] = date_match.group(1)
            else:
                tournament_data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Find deck links
            deck_links = tourn_soup.find_all('a', href=True)
            deck_count = 0
            
            for deck_link in deck_links:
                if 'decklist-view-deck-button' in deck_link.get('class', []):
                    deck_count += 1
                    # Here you would fetch each deck, but for now just count
                    
            tournament_data['deck_count'] = deck_count
            print(f"  ✅ Found {deck_count} decks")
            
            # Save tournament
            filename = f"{tournament_data['date']}_{tournament['tournament_id']}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(tournament_data, f, indent=2)
                
            print(f"  💾 Saved: {filename}")
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    print("\n✅ Scraping complete!")


if __name__ == "__main__":
    scrape_mtgo_standard()