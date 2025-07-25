#!/usr/bin/env python3
"""
Simple MTGO scraper test without dependencies.
"""
import asyncio
import re
import json
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

class SimpleMTGOScraper:
    def __init__(self, format_name):
        self.format_name = format_name
        self.base_url = "https://www.mtgo.com"
        self.format_mapping = {
            "standard": "standard",
            "modern": "modern", 
            "legacy": "legacy",
            "vintage": "vintage",
            "pioneer": "pioneer",
            "pauper": "pauper"
        }
    
    async def scrape_tournaments(self, start_date, end_date):
        """Scrape tournaments from MTGO site."""
        format_slug = self.format_mapping.get(self.format_name.lower())
        if not format_slug:
            print(f"Format not supported: {self.format_name}")
            return []

        tournaments = []
        
        # Step 1: Get the decklists page
        decklists_url = f"{self.base_url}/decklists"
        print(f"Fetching decklists page: {decklists_url}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(decklists_url)
                if response.status_code != 200:
                    print(f"Failed to fetch decklists page: {response.status_code}")
                    return []
                content = response.text
            except Exception as e:
                print(f"Error fetching decklists page: {e}")
                return []
        
        # Step 2: Parse to find tournament links
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all decklist links for our format
        all_links = soup.find_all('a', href=re.compile(f'/decklist/{format_slug}'))
        tournament_links = []
        
        print(f"Found {len(all_links)} {format_slug} links total")
        
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
                        full_url = f"{self.base_url}{href}"
                        tournament_links.append((full_url, link_text, link_date.strftime('%Y-%m-%d')))
                except ValueError:
                    pass
        
        print(f"Found {len(tournament_links)} tournament links for date range")
        
        # Step 3: Process each tournament (limit to first 3 for testing)
        for url, title, date_str in tournament_links[:3]:
            print(f"\nProcessing: {title} ({date_str})")
            tournament_data = await self._scrape_tournament_page(client, url, title, date_str)
            if tournament_data:
                tournaments.append(tournament_data)
        
        print(f"\nSuccessfully scraped {len(tournaments)} tournaments for {self.format_name}")
        return tournaments

    async def _scrape_tournament_page(self, client, url, title, date_str):
        """Scrape a single tournament page."""
        print(f"  Fetching: {url}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    print(f"  Failed to fetch tournament page: {response.status_code}")
                    return None
                content = response.text
            except Exception as e:
                print(f"  Error fetching tournament page: {e}")
                return None
        
        # Extract data from window.MTGO.decklists.data
        decklists = self._extract_mtgo_data(content)
        if not decklists:
            print(f"  No decklists found")
            return None
        
        tournament_data = {
            "source": "mtgo",
            "format": self.format_name,
            "name": self._clean_tournament_name(title),
            "date": date_str,
            "url": url,
            "decklists": decklists
        }
        
        print(f"  Found {len(decklists)} decklists")
        return tournament_data

    def _extract_mtgo_data(self, content):
        """Extract deck data from window.MTGO.decklists.data."""
        decklists = []
        
        # Find window.MTGO.decklists.data assignment
        match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({[\s\S]+?});', content)
        if not match:
            return []
        
        try:
            # Parse the JSON data
            data = json.loads(match.group(1))
            
            # Extract decklists array
            if 'decklists' not in data:
                return []
            
            for deck_data in data['decklists']:
                parsed_deck = self._parse_mtgo_deck(deck_data)
                if parsed_deck:
                    decklists.append(parsed_deck)
        
        except json.JSONDecodeError as e:
            print(f"  Failed to parse MTGO JSON data: {e}")
        except Exception as e:
            print(f"  Error extracting MTGO data: {e}")
        
        return decklists

    def _parse_mtgo_deck(self, deck_data):
        """Parse a single deck from MTGO data format."""
        try:
            player_name = deck_data.get('player', 'Unknown')
            
            # Parse mainboard
            mainboard = []
            for card in deck_data.get('main_deck', []):
                if card.get('sideboard') == 'false':
                    mainboard.append({
                        "quantity": int(card.get('qty', 1)),
                        "name": card.get('card_attributes', {}).get('card_name', '')
                    })
            
            # Parse sideboard
            sideboard = []
            for card in deck_data.get('sideboard_deck', []):
                sideboard.append({
                    "quantity": int(card.get('qty', 1)),
                    "name": card.get('card_attributes', {}).get('card_name', '')
                })
            
            # Get wins/losses
            wins_data = deck_data.get('wins', {})
            wins = wins_data.get('wins') if isinstance(wins_data, dict) else None
            losses = wins_data.get('losses') if isinstance(wins_data, dict) else None
            
            if mainboard:
                return {
                    "player": player_name,
                    "mainboard": mainboard,
                    "sideboard": sideboard,
                    "wins": int(wins) if wins else None,
                    "losses": int(losses) if losses else None
                }
        
        except Exception as e:
            print(f"  Error parsing MTGO deck: {e}")
        
        return None

    def _clean_tournament_name(self, name):
        """Clean tournament name."""
        # Remove dates from the name
        name = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{1,2}\s*\d{4}', '', name)
        name = re.sub(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip() or f"{self.format_name.title()} Tournament"

async def main():
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 31)
    
    print(f"Testing MTGO scraper from {start_date.date()} to {end_date.date()}")
    
    scraper = SimpleMTGOScraper("standard")
    tournaments = await scraper.scrape_tournaments(start_date, end_date)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total tournaments found: {len(tournaments)}")
    
    if tournaments:
        for t in tournaments:
            print(f"\n{t['date']} - {t['name']}")
            print(f"  URL: {t['url']}")
            print(f"  Decklists: {len(t.get('decklists', []))}")

if __name__ == "__main__":
    asyncio.run(main())