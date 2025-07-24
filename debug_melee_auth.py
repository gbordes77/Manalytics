#!/usr/bin/env python3
"""
Debug Melee authentication and search.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_melee():
    """Debug Melee authentication."""
    base_url = "https://melee.gg"
    
    # These should be set in environment
    email = "gbordes64@gmail.com"
    password = "Ctr0Dur!"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Set browser headers
        client.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Step 1: Get login page
        logger.info("Getting login page...")
        login_page_url = f"{base_url}/Account/SignIn"
        response = await client.get(login_page_url)
        logger.info(f"Login page status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find CSRF token
        csrf_token = None
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if token_input:
            csrf_token = token_input.get('value')
            logger.info(f"Found CSRF token: {csrf_token[:20]}...")
        else:
            logger.error("No CSRF token found!")
            # Try to find any hidden inputs
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                logger.info(f"Hidden input: {inp.get('name')} = {inp.get('value', '')[:20]}...")
        
        if not csrf_token:
            return
        
        # Step 2: Submit login
        logger.info("Submitting login...")
        login_url = f"{base_url}/Account/SignInPassword"
        login_data = {
            'Email': email,
            'Password': password,
            '__RequestVerificationToken': csrf_token,
            'RememberMe': 'true'
        }
        
        response = await client.post(
            login_url,
            data=login_data,
            headers={
                'Referer': login_page_url,
                'Origin': base_url
            }
        )
        
        logger.info(f"Login response status: {response.status_code}")
        logger.info(f"Login response URL: {response.url}")
        
        # Check cookies
        logger.info("Cookies after login:")
        for name, value in client.cookies.items():
            logger.info(f"  {name}: {value[:20] if len(value) > 20 else value}...")
        
        # Step 3: Try to search tournaments
        logger.info("\nTrying to search tournaments...")
        search_url = f"{base_url}/Decklist/SearchDecklists"
        
        search_data = {
            'Formats': 'Standard',
            'StartDate': '07/01/2025',
            'EndDate': '07/24/2025',
            'MinNumberOfPlayers': '8',
            'IncludeLeagues': 'false',
            'SortBy': 'DateDescending',
            'PageNumber': '1'
        }
        
        response = await client.post(search_url, data=search_data)
        logger.info(f"Search response status: {response.status_code}")
        logger.info(f"Search response URL: {response.url}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for tournament links
            tournament_links = soup.find_all('a', href=lambda x: x and '/Tournament/' in x)
            logger.info(f"Found {len(tournament_links)} tournament links")
            
            for i, link in enumerate(tournament_links[:5]):
                logger.info(f"  Tournament {i+1}: {link.get_text(strip=True)} - {link['href']}")
            
            # Check if we're on an error page
            if 'error' in str(response.url).lower():
                logger.error("Redirected to error page!")
                error_msg = soup.find('div', class_='error-message')
                if error_msg:
                    logger.error(f"Error message: {error_msg.get_text(strip=True)}")

if __name__ == "__main__":
    asyncio.run(debug_melee())