#!/usr/bin/env python3
"""
Debug the actual response content from Melee API.
"""
import asyncio
import httpx
import json
from datetime import datetime
from bs4 import BeautifulSoup

async def debug_response():
    """Check what we're actually getting from Melee."""
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        client.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # Visit main page first to get any necessary cookies
        print("=== Getting main page for cookies ===")
        main_response = await client.get("https://melee.gg")
        print(f"Main page status: {main_response.status_code}")
        print(f"Cookies: {list(client.cookies.keys())}")
        
        # Now try the search
        print("\n=== Testing SearchTournaments ===")
        search_url = "https://melee.gg/Tournament/SearchTournaments"
        
        search_payload = {
            "draw": "1",
            "columns": [
                {"data": "ID", "name": ""},
                {"data": "Name", "name": ""},
                {"data": "StartDate", "name": ""},
                {"data": "Status", "name": ""},
                {"data": "Format", "name": ""},
                {"data": "OrganizationName", "name": ""},
                {"data": "Decklists", "name": ""},
                {"data": "Description", "dir": "desc"}
            ],
            "order": [{"column": 2, "dir": "desc"}],
            "start": 0,
            "length": 25,
            "search": {"value": "", "regex": False},
            "startDate": "2025-07-01T00:00:00.000Z",
            "endDate": "2025-07-24T23:59:59.999Z"
        }
        
        response = await client.post(search_url, json=search_payload)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response length: {len(response.text)}")
        print("\n=== First 500 chars of response ===")
        print(response.text[:500])
        print("\n=== Last 200 chars of response ===")
        print(response.text[-200:])
        
        # If it's HTML, parse it to see what page we're on
        if 'text/html' in response.headers.get('content-type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"\nPage title: {title.get_text()}")
            
            # Look for error messages
            error_divs = soup.find_all('div', class_=['error', 'alert', 'warning'])
            for div in error_divs:
                print(f"Error message: {div.get_text(strip=True)}")
        
        # Try a different approach - maybe it needs form data instead of JSON
        print("\n=== Trying with form data ===")
        form_data = {
            "draw": "1",
            "start": "0",
            "length": "25",
            "startDate": "2025-07-01T00:00:00.000Z",
            "endDate": "2025-07-24T23:59:59.999Z"
        }
        
        response2 = await client.post(search_url, data=form_data)
        print(f"Form data status: {response2.status_code}")
        print(f"Form data response: {response2.text[:200]}")
        
        # Try GET request to see if there's a search page
        print("\n=== Trying GET to Tournament page ===")
        tournament_list_url = "https://melee.gg/Tournament"
        response3 = await client.get(tournament_list_url)
        print(f"Tournament list status: {response3.status_code}")
        
        if response3.status_code == 200:
            soup = BeautifulSoup(response3.text, 'html.parser')
            
            # Look for tournament links
            tournament_links = soup.find_all('a', href=lambda x: x and '/Tournament/' in x)
            print(f"Found {len(tournament_links)} tournament links")
            
            for i, link in enumerate(tournament_links[:5]):
                href = link.get('href')
                text = link.get_text(strip=True)
                print(f"  {i+1}: {text} -> {href}")

if __name__ == "__main__":
    asyncio.run(debug_response())