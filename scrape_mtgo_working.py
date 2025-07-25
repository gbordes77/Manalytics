#!/usr/bin/env python3
"""
Scraper MTGO fonctionnel pour récupérer tous les tournois
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import re
import time


def scrape_mtgo_all_formats():
    """Scrape ALL MTGO tournaments from July 1st to today"""
    
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
    
    # Find ALL tournament links
    links = soup.find_all('a', href=True)
    tournament_links = []
    
    for link in links:
        href = link.get('href', '')
        text = link.text.strip()
        
        # Look for tournament links (skip /en prefix)
        if '/decklist/' in href and not href.startswith('/en/'):
            # Extract date from text
            date_match = re.search(r'(\w+)\s+(\d+)\s+(\d{4})', text)
            if date_match:
                month_name = date_match.group(1)
                day = int(date_match.group(2))
                year = int(date_match.group(3))
                
                # Convert month name to number
                months = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4,
                    'May': 5, 'June': 6, 'July': 7, 'August': 8,
                    'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                
                if month_name in months and year == 2025 and months[month_name] == 7:
                    # July 2025 tournament
                    tournament_links.append({
                        'url': 'https://www.mtgo.com' + href,
                        'name': text,
                        'tournament_id': href.split('/')[-1],
                        'date': f"2025-07-{day:02d}"
                    })
    
    print(f"✅ Found {len(tournament_links)} July 2025 tournament links")
    
    # Group by format
    tournaments_by_format = {}
    
    for tournament in tournament_links:
        # Determine format from name
        name_lower = tournament['name'].lower()
        format_name = 'unknown'
        
        if 'standard' in name_lower:
            format_name = 'standard'
        elif 'modern' in name_lower:
            format_name = 'modern'
        elif 'legacy' in name_lower:
            format_name = 'legacy'
        elif 'vintage' in name_lower:
            format_name = 'vintage'
        elif 'pioneer' in name_lower:
            format_name = 'pioneer'
        elif 'pauper' in name_lower:
            format_name = 'pauper'
        elif 'duel commander' in name_lower:
            format_name = 'duel-commander'
        elif 'limited' in name_lower:
            format_name = 'limited'
            
        if format_name not in tournaments_by_format:
            tournaments_by_format[format_name] = []
        tournaments_by_format[format_name].append(tournament)
    
    # Show summary
    print("\n📊 Summary by format:")
    for format_name, tournaments in tournaments_by_format.items():
        print(f"  {format_name}: {len(tournaments)} tournaments")
    
    # Create output directories and save
    base_dir = Path("data/raw/mtgo")
    saved_count = 0
    
    for format_name, tournaments in tournaments_by_format.items():
        format_dir = base_dir / format_name
        format_dir.mkdir(parents=True, exist_ok=True)
        
        for tournament in tournaments:
            try:
                print(f"\n📊 Processing: {tournament['name']}")
                
                # Get tournament page
                tourn_response = session.get(tournament['url'])
                if tourn_response.status_code != 200:
                    print(f"  ❌ Failed to get tournament: {tourn_response.status_code}")
                    continue
                    
                tourn_soup = BeautifulSoup(tourn_response.text, 'html.parser')
                
                # Extract basic info
                tournament_data = {
                    'source': 'mtgo',
                    'format': format_name,
                    'name': tournament['name'],
                    'url': tournament['url'],
                    'tournament_id': tournament['tournament_id'],
                    'date': tournament['date'],
                    'scraped_at': datetime.now().isoformat(),
                    'decklists': []
                }
                
                # Find deck count (for now just save the tournament info)
                deck_sections = tourn_soup.find_all('div', class_='decklist-group')
                tournament_data['deck_count'] = len(deck_sections)
                
                # Save tournament
                filename = f"{tournament['date']}_{tournament['tournament_id']}.json"
                filepath = format_dir / filename
                
                with open(filepath, 'w') as f:
                    json.dump(tournament_data, f, indent=2)
                    
                print(f"  💾 Saved: {format_name}/{filename}")
                saved_count += 1
                
                # Rate limit
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
    
    print(f"\n✅ Scraping complete! Saved {saved_count} tournaments")


if __name__ == "__main__":
    print("🎯 Scraping ALL MTGO tournaments for July 2025")
    print("=" * 50)
    scrape_mtgo_all_formats()