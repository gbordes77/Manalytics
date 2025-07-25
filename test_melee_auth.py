#\!/usr/bin/env python3
"""Test Melee authentication"""

import json
import os
from scrapers.melee_scraper_complete import MtgMeleeClient, MtgMeleeConstants
from datetime import datetime, timezone, timedelta

def test_auth():
    print("Testing Melee authentication...")
    
    # Check credentials file
    if os.path.exists(MtgMeleeConstants.CRED_FILE):
        print(f"✓ Credentials file exists: {MtgMeleeConstants.CRED_FILE}")
        with open(MtgMeleeConstants.CRED_FILE, "r") as f:
            creds = json.load(f)
            print(f"  - Email: {creds['login']}")
    else:
        print(f"✗ Credentials file missing: {MtgMeleeConstants.CRED_FILE}")
        return
    
    # Try to get authenticated client
    try:
        print("\n1. Getting authenticated client...")
        client = MtgMeleeClient()
        session = client.get_client(load_cookies=True)
        print("✓ Client created successfully")
        
        # Check cookies
        cookies = session.cookies.get_dict()
        print(f"\n2. Cookies: {len(cookies)} cookies loaded")
        if ".AspNet.ApplicationCookie" in cookies:
            print("✓ Auth cookie present")
        else:
            print("✗ Auth cookie missing")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_simple_request():
    print("\n3. Testing simple tournament search...")
    
    client = MtgMeleeClient()
    
    # Test with a very short date range
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 2, tzinfo=timezone.utc)  # Just 1 day
    
    print(f"   Date range: {start_date.date()} to {end_date.date()}")
    
    payload = MtgMeleeConstants.build_magic_payload(start_date, end_date, length=10)
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = client.get_client(load_cookies=True).post(
            'https://melee.gg/Decklist/SearchDecklists',
            data=payload,
            timeout=30
        )
        
        print(f"\n   Response status: {response.status_code}")
        print(f"   Response length: {len(response.text)} chars")
        
        if response.text:
            data = response.json()
            print(f"   Records found: {data.get('recordsTotal', 0)}")
            print(f"   Data items: {len(data.get('data', []))}")
        else:
            print("   Empty response\!")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
    test_simple_request()
