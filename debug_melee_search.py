#!/usr/bin/env python3
"""
Debug Melee search by first doing a GET to understand the form.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_search():
    """Debug Melee search."""
    base_url = "https://melee.gg"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Browser headers
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # First, let's GET the search page to see the form
        logger.info("Getting search page...")
        search_page_url = f"{base_url}/Decklist/Search"
        response = await client.get(search_page_url)
        
        if response.status_code != 200:
            # Try another URL
            search_page_url = f"{base_url}/Tournament/Index"
            response = await client.get(search_page_url)
        
        logger.info(f"Search page status: {response.status_code}")
        logger.info(f"Search page URL: {response.url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        logger.info(f"\nFound {len(forms)} forms")
        
        for i, form in enumerate(forms):
            logger.info(f"\nForm {i+1}:")
            logger.info(f"  Action: {form.get('action', 'None')}")
            logger.info(f"  Method: {form.get('method', 'GET')}")
            
            # Find all inputs
            inputs = form.find_all(['input', 'select'])
            for inp in inputs[:10]:  # First 10 inputs
                if inp.name == 'input':
                    logger.info(f"  Input: {inp.get('name')} (type: {inp.get('type')})")
                else:
                    logger.info(f"  Select: {inp.get('name')}")
        
        # Look for tournament links directly
        logger.info("\nLooking for recent tournaments...")
        tournament_links = soup.find_all('a', href=lambda x: x and '/Tournament/' in x and x != '/Tournament/Edit' and x != '/Tournament/Index')
        
        logger.info(f"Found {len(tournament_links)} tournament links")
        for i, link in enumerate(tournament_links[:10]):
            logger.info(f"  {i+1}: {link.get_text(strip=True)} - {link['href']}")

if __name__ == "__main__":
    asyncio.run(debug_search())