#!/usr/bin/env python3
"""Test minimal du scraper Melee sans dépendances complexes."""
import asyncio
import json
import sys
import os

# Mock les dépendances manquantes
class MockCacheManager:
    def get_cached_url(self, *args): return None
    def cache_url(self, *args): pass

sys.modules['src.utils.cache_manager'] = type('module', (), {'CacheManager': MockCacheManager})()

# Mock Redis
class MockRedis:
    pass
sys.modules['redis'] = type('module', (), {'Redis': MockRedis})()

# Maintenant on peut importer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.melee_scraper import MeleeScraper

async def test_melee():
    """Test simple du scraper Melee."""
    print("🧪 Test scraper Melee...")
    
    try:
        async with MeleeScraper('standard') as scraper:
            print(f"✅ Authentification: {scraper.authenticated}")
            
            if scraper.authenticated:
                print("✅ Scraper authentifié avec succès!")
                
                # Test sur 3 jours seulement
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=3)
                
                tournaments = await scraper.scrape_tournaments(start_date, end_date)
                print(f"🏆 Tournois trouvés: {len(tournaments)}")
                
                for t in tournaments[:3]:
                    print(f"  - {t['name']}: {len(t.get('decklists', []))} decks")
                    
            else:
                print("❌ Échec authentification")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_melee())