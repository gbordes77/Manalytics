#!/usr/bin/env python3
"""
Debug exact Melee API calls as specified in instructions.
"""
import asyncio
import httpx
import json
from datetime import datetime

async def debug_melee_api():
    """Test the exact API endpoints mentioned in instructions."""
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Set proper headers
        client.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # Test 1: /Tournament/SearchTournaments endpoint
        print("=== Testing /Tournament/SearchTournaments ===")
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
        
        try:
            response = await client.post(search_url, json=search_payload)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Check if response is JSON or HTML
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")
                
                if 'application/json' in content_type:
                    data = response.json()
                    print(f"Response keys: {list(data.keys())}")
                    if "data" in data:
                        print(f"Found {len(data['data'])} tournaments")
                        for i, tournament in enumerate(data["data"][:3]):
                            print(f"  Tournament {i+1}: {tournament.get('Name')} - {tournament.get('Format')}")
                else:
                    print(f"Got HTML response instead of JSON:")
                    print(f"{response.text[:1000]}")
            else:
                print(f"Error response: {response.text[:500]}")
        except Exception as e:
            print(f"Error with SearchTournaments: {e}")
        
        # Test 2: Direct tournament page access
        print("\n=== Testing direct tournament access ===")
        # Try a sample tournament ID
        tournament_url = "https://melee.gg/Tournament/12345"  # Sample ID
        try:
            response = await client.get(tournament_url)
            print(f"Tournament page status: {response.status_code}")
            if response.status_code == 200:
                print("Tournament page accessible!")
            else:
                print(f"Tournament page error: {response.text[:200]}")
        except Exception as e:
            print(f"Error accessing tournament: {e}")
        
        # Test 3: /Round/GetRoundStandings endpoint
        print("\n=== Testing /Round/GetRoundStandings ===")
        standings_url = "https://melee.gg/Round/GetRoundStandings"
        
        standings_payload = {
            "draw": "1",
            "columns": [
                {"data": "Rank", "name": ""},
                {"data": "Player", "name": ""},
                {"data": "Decklists", "name": ""},
                {"data": "MatchRecord", "name": ""},
                {"data": "GameRecord", "name": ""},
                {"data": "Points", "name": ""}
            ],
            "order": [{"column": 0, "dir": "asc"}],
            "start": 0,
            "length": 25,
            "search": {"value": "", "regex": False},
            "roundId": "12345"  # Sample round ID
        }
        
        try:
            response = await client.post(standings_url, json=standings_payload)
            print(f"Standings status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Standings response keys: {list(data.keys())}")
            else:
                print(f"Standings error: {response.text[:200]}")
        except Exception as e:
            print(f"Error with GetRoundStandings: {e}")
        
        # Test 4: Check if we need to visit main page first for cookies
        print("\n=== Testing main page access ===")
        main_url = "https://melee.gg"
        try:
            response = await client.get(main_url)
            print(f"Main page status: {response.status_code}")
            print(f"Cookies after main page: {list(client.cookies.keys())}")
            
            # Now retry search with cookies
            print("\n=== Retrying search after main page visit ===")
            response = await client.post(search_url, json=search_payload)
            print(f"Search status after cookies: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {len(data.get('data', []))} tournaments")
            else:
                print(f"Still error: {response.text[:200]}")
                
        except Exception as e:
            print(f"Error with main page: {e}")

if __name__ == "__main__":
    asyncio.run(debug_melee_api())