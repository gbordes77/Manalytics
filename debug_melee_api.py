#!/usr/bin/env python3
"""
Debug Melee API responses to understand the format
"""

import json
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

def debug_api():
    """Debug API responses"""
    
    # Load credentials
    creds_file = Path("api_credentials/melee_login.json")
    if not creds_file.exists():
        print("❌ Credentials file not found")
        return
    
    with open(creds_file) as f:
        creds = json.load(f)
    
    # Create session
    session = httpx.Client(
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        },
        timeout=30.0
    )
    
    # Authenticate
    print("🔐 Authenticating...")
    login_page = session.get("https://melee.gg/Account/SignIn")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
    
    login_data = {
        'Email': creds["login"],
        'Password': creds["mdp"],
        '__RequestVerificationToken': token
    }
    
    login_resp = session.post(
        "https://melee.gg/Account/SignInPassword",
        data=login_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
    )
    
    print(f"✅ Login response: {login_resp.status_code}")
    
    # Test 1: Tournament Search with minimal payload
    print("\n📊 Test 1: Minimal search payload")
    
    minimal_payload = {
        "draw": "1",
        "start": "0",
        "length": "10"
    }
    
    resp1 = session.post(
        "https://melee.gg/Tournament/SearchResults",
        data=minimal_payload,
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    
    print(f"Response status: {resp1.status_code}")
    if resp1.status_code == 200:
        data = resp1.json()
        print(f"Response type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if 'data' in data:
                print(f"Data length: {len(data['data'])}")
                if data['data']:
                    print(f"First item keys: {list(data['data'][0].keys())}")
                    print(f"Sample: {json.dumps(data['data'][0], indent=2)}")
        elif isinstance(data, list):
            print(f"List length: {len(data)}")
            if data:
                print(f"First item: {json.dumps(data[0], indent=2)}")
    
    # Test 2: With date filter
    print("\n📊 Test 2: With date filter")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    date_payload = {
        "draw": "1",
        "start": "0",
        "length": "10",
        "startDate": start_date.strftime("%Y-%m-%d") + "T00:00:00.000Z",
        "endDate": end_date.strftime("%Y-%m-%d") + "T23:59:59.999Z"
    }
    
    resp2 = session.post(
        "https://melee.gg/Tournament/SearchResults",
        data=date_payload,
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    
    print(f"Response status: {resp2.status_code}")
    if resp2.status_code == 200:
        data = resp2.json()
        with open("melee_api_debug.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Full response saved to melee_api_debug.json")
    
    # Test 3: Check a specific tournament page
    print("\n📊 Test 3: Tournament page structure")
    
    # Use a known tournament ID from our data
    tournament_url = "https://melee.gg/Tournament/View/341369"
    
    resp3 = session.get(tournament_url)
    if resp3.status_code == 200:
        soup = BeautifulSoup(resp3.text, 'html.parser')
        
        # Look for deck links
        deck_links = soup.select('a[href*="/Decklist/View/"]')
        print(f"Found {len(deck_links)} deck links")
        
        # Look for round/standings elements
        round_elements = soup.select('[data-round-id], a[href*="roundId="]')
        print(f"Found {len(round_elements)} round elements")
        
        # Save page for analysis
        with open("melee_tournament_page.html", "w") as f:
            f.write(resp3.text)
        print("✅ Tournament page saved to melee_tournament_page.html")

if __name__ == "__main__":
    debug_api()