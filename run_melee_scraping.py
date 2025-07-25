#!/usr/bin/env python3
"""
Script simple pour lancer le scraping Melee avec le scraper amélioré
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleMeleeScraper:
    """Simplified Melee scraper for standard tournaments"""
    
    def __init__(self, format_name: str):
        self.format_name = format_name
        self.base_url = "https://melee.gg"
        self.client = httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            },
            timeout=30.0,
            follow_redirects=True
        )
        self.authenticated = False
        self.auth_cookies = {}
        
    async def __aenter__(self):
        await self.authenticate()
        return self
        
    async def __aexit__(self, *args):
        await self.client.aclose()
        
    async def authenticate(self):
        """Authenticate with Melee"""
        email = os.getenv('MELEE_EMAIL')
        password = os.getenv('MELEE_PASSWORD')
        
        if not email or not password:
            logger.error("MELEE_EMAIL and MELEE_PASSWORD must be set in .env")
            return
            
        logger.info("Authenticating with Melee.gg...")
        
        try:
            # Get login page
            login_response = await self.client.get(f"{self.base_url}/Account/SignIn")
            
            soup = BeautifulSoup(login_response.text, 'html.parser')
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            if not token_input:
                logger.error("Could not find CSRF token")
                return
                
            csrf_token = token_input.get('value')
            
            # Submit login
            form_data = {
                'Email': email,
                'Password': password,
                '__RequestVerificationToken': csrf_token
            }
            
            login_submit = await self.client.post(
                f"{self.base_url}/Account/SignInPassword",
                data=form_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f'{self.base_url}/Account/SignIn'
                }
            )
            
            if login_submit.status_code == 200:
                logger.info("✅ Authentication successful")
                self.authenticated = True
                # Store CSRF token
                for name, value in self.client.cookies.items():
                    self.auth_cookies[name] = value
            else:
                logger.error("❌ Authentication failed")
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            
    async def scrape_tournaments(self, start_date: datetime, end_date: datetime):
        """Scrape tournaments for the given date range"""
        if not self.authenticated:
            logger.error("Not authenticated")
            return []
            
        logger.info(f"Searching Melee tournaments for {self.format_name}")
        
        # Update headers for AJAX request
        self.client.headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': f'{self.base_url}/Tournament/Search'
        })
        
        # Search payload
        search_payload = {
            "draw": "1",
            "start": "0", 
            "length": "1000",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/Tournament/SearchResults",
                data=search_payload
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}")
                return []
            
            data = response.json()
            
            if not isinstance(data, list):
                logger.error(f"Unexpected response format: {type(data)}")
                return []
            
            logger.info(f"Found {len(data)} tournaments from API")
            
            # Debug first tournament
            if data:
                logger.info(f"First tournament sample: {json.dumps(data[0], indent=2)}")
            
            # Filter and process tournaments
            tournaments = []
            magic_count = 0
            format_count = 0
            
            for tournament in data:
                # Check if it's a Magic tournament
                game_desc = tournament.get('gameDescription', '')
                if 'magic' not in game_desc.lower():
                    continue
                magic_count += 1
                    
                # Check format 
                format_desc = tournament.get('formatString', tournament.get('formatDescription', ''))
                if self.format_name.lower() not in format_desc.lower():
                    continue
                format_count += 1
                
                # Parse date
                start_date_str = tournament.get('startDate', '')
                if not start_date_str:
                    continue
                    
                try:
                    # Remove timezone and parse
                    start_date_str = start_date_str.replace('Z', '').split('T')[0]
                    tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    
                    # Check if within our date range
                    if not (start_date <= tournament_date <= end_date):
                        continue
                        
                except Exception:
                    continue
                
                tournament_id = tournament.get('id')
                if not tournament_id:
                    continue
                
                # Save tournament data
                tournament_info = {
                    "source": "melee",
                    "format": self.format_name,
                    "name": tournament.get('name', 'Unknown Tournament'),
                    "date": start_date_str,
                    "url": f"{self.base_url}/Tournament/{tournament_id}",
                    "tournament_id": str(tournament_id),
                    "organization": tournament.get('organizationName', 'N/A'),
                    "raw_data": tournament  # Keep raw data for analysis
                }
                
                tournaments.append(tournament_info)
                logger.info(f"Added tournament: {tournament_info['name']} ({start_date_str})")
                
                # Save immediately
                self._save_tournament(tournament_info)
            
            logger.info(f"Filter stats: {magic_count} Magic tournaments, {format_count} {self.format_name} tournaments")
            return tournaments
            
        except Exception as e:
            logger.error(f"Error searching tournaments: {e}")
            return []
            
    def _save_tournament(self, tournament_data):
        """Save tournament data to file"""
        output_dir = Path(f"data/raw/melee/{self.format_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        date_str = tournament_data['date']
        name_clean = tournament_data['name'].replace(' ', '_').replace('/', '_')[:50]
        filename = f"{date_str}_{name_clean}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(tournament_data, f, indent=2)
            
        logger.info(f"Saved: {filename}")


async def main():
    """Run the scraper"""
    format_name = "standard"
    days_back = 30
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    logger.info(f"🎯 Scraping Melee tournaments for {format_name}")
    logger.info(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    
    async with SimpleMeleeScraper(format_name) as scraper:
        tournaments = await scraper.scrape_tournaments(start_date, end_date)
        
    logger.info(f"\n✅ Scraped {len(tournaments)} tournaments")
    
    # Show summary
    if tournaments:
        logger.info("\nTournaments scraped:")
        for t in tournaments[:10]:  # Show first 10
            logger.info(f"  - {t['date']} {t['name']}")
        if len(tournaments) > 10:
            logger.info(f"  ... and {len(tournaments) - 10} more")


if __name__ == "__main__":
    asyncio.run(main())