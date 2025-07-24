#!/usr/bin/env python3
"""Test de l'authentification Melee avec le nouveau scraper."""

import asyncio
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.melee_scraper import MeleeScraper
from config.settings import settings

async def test_melee_scraper():
    """Test du scraper Melee avec authentification."""
    print("🧪 Testing Melee scraper with authentication...")
    print(f"Email: {settings.MELEE_EMAIL}")
    print(f"Password: {'*' * len(settings.MELEE_PASSWORD)}")
    
    try:
        async with MeleeScraper('standard') as scraper:
            print(f"✅ Authentication status: {scraper.authenticated}")
            print(f"🍪 Number of cookies: {len(scraper.selenium_cookies)}")
            
            if scraper.authenticated:
                # Tester directement l'API avec une requête simple
                print("🧪 Testing direct API call...")
                
                try:
                    response = await scraper.client.get("https://melee.gg/Decklist/SearchDecklists")
                    print(f"GET status: {response.status_code}")
                    print(f"Content-Type: {response.headers.get('content-type')}")
                    print(f"Response length: {len(response.text)}")
                    print(f"First 200 chars: {response.text[:200]}")
                except Exception as e:
                    print(f"API error: {e}")
                
                # Tester sur 3 jours pour pas attendre trop longtemps
                tournaments = await scraper.run(days_back=3)
                print(f"🏆 Found {len(tournaments)} tournaments")
                
                for t in tournaments[:3]:
                    print(f"  - {t['name']}: {len(t.get('decklists', []))} decks")
            else:
                print("❌ Authentication failed")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_melee_scraper())