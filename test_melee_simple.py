#\!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# Test direct authentication
print("Testing Melee authentication...")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

# Get login page
print("1. Getting login page...")
login_page = session.get("https://melee.gg/Account/SignIn")
print(f"   Status: {login_page.status_code}")

if login_page.status_code == 200:
    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.find("input", {"name": "__RequestVerificationToken"})
    if token:
        token_value = token["value"]
        print(f"   Token found: {token_value[:20]}...")
        
        # Try login
        print("\n2. Attempting login...")
        ajax_headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://melee.gg",
            "Referer": "https://melee.gg/Account/SignIn"
        }
        
        login_data = {
            "email": "gbordes64@gmail.com",
            "password": "Ctr0Dur\!",
            "__RequestVerificationToken": token_value
        }
        
        login_resp = session.post(
            "https://melee.gg/Account/SignInPassword",
            headers=ajax_headers,
            data=login_data
        )
        
        print(f"   Login status: {login_resp.status_code}")
        print(f"   Response: {login_resp.text[:200]}")
        print(f"   Cookies: {session.cookies.get_dict()}")
        
        if ".AspNet.ApplicationCookie" in session.cookies.get_dict():
            print("   ✓ Auth cookie received\!")
            
            # Test API
            print("\n3. Testing API...")
            payload = {
                "draw": "1",
                "columns[0][data]": "TournamentStartDate",
                "columns[0][searchable]": "false",
                "columns[0][orderable]": "true",
                "order[0][column]": "0",
                "order[0][dir]": "desc",
                "start": "0",
                "length": "10",
                "search[value]": "",
                "search[regex]": "false",
                "showOnlyMyDecklists": "false",
                "gameId": "1",
                "dateMin": "2025-07-01",
                "dateMax": "2025-07-02"
            }
            
            api_resp = session.post(
                'https://melee.gg/Decklist/SearchDecklists',
                data=payload,
                headers={'X-Requested-With': 'XMLHttpRequest'},
                timeout=30
            )
            
            print(f"   API status: {api_resp.status_code}")
            if api_resp.text:
                data = api_resp.json()
                print(f"   Records: {data.get('recordsTotal', 0)}")
            else:
                print("   Empty response")
