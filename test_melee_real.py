#!/usr/bin/env python3
"""Test RÉEL du scraper Melee en standard du 1er juillet à maintenant."""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Ajouter le projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock des modules manquants pour éviter les erreurs d'import
class MockRedis:
    pass

class MockCacheManager:
    def __init__(self):
        pass

sys.modules['redis'] = type('module', (), {'Redis': MockRedis})()
sys.modules['src.utils.cache_manager'] = type('module', (), {'CacheManager': MockCacheManager})()

from src.scrapers.melee_scraper import MeleeScraper

async def test_melee_real():
    """Test réel du scraper Melee en standard du 1er juillet à maintenant."""
    print("🧪 TEST RÉEL - Scraper Melee Standard du 1er juillet 2025 à maintenant")
    print("=" * 70)
    
    # Dates exactes demandées
    start_date = datetime(2025, 7, 1)
    end_date = datetime.now()
    
    print(f"📅 Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    print(f"🎯 Format: Standard")
    
    try:
        async with MeleeScraper('standard') as scraper:
            print(f"\n🔐 Authentification: ", end="")
            if scraper.cookies:
                print(f"✅ RÉUSSIE ({len(scraper.cookies)} cookies)")
                
                print(f"\n🔍 Recherche des tournois...")
                tournaments = await scraper.scrape_tournaments(start_date, end_date)
                
                print(f"\n📊 RÉSULTATS:")
                print(f"   🏆 Tournois trouvés: {len(tournaments)}")
                
                if tournaments:
                    print(f"\n📋 Détail des tournois:")
                    total_decklists = 0
                    
                    for i, tournament in enumerate(tournaments, 1):
                        print(f"\n   {i}. {tournament['name']}")
                        print(f"      📅 Date: {tournament['date']}")
                        print(f"      🔗 URL: {tournament['url']}")
                        
                        decklists = tournament.get('decklists', [])
                        print(f"      📝 Decklists: {len(decklists)}")
                        total_decklists += len(decklists)
                        
                        # Afficher les 3 premiers joueurs s'il y en a
                        if decklists:
                            print(f"         Top joueurs:")
                            for j, deck in enumerate(decklists[:3], 1):
                                player = deck.get('player', 'Inconnu')
                                mainboard_count = len(deck.get('mainboard', []))
                                print(f"         {j}. {player} ({mainboard_count} cartes main)")
                    
                    print(f"\n🎯 TOTAL DECKLISTS RÉCUPÉRÉES: {total_decklists}")
                    
                    if total_decklists > 0:
                        print(f"\n✅ SUCCÈS - Le scraper Melee fonctionne parfaitement!")
                        print(f"   - {len(tournaments)} tournois Standard trouvés")
                        print(f"   - {total_decklists} decklists récupérées")
                        print(f"   - Données prêtes pour l'analyse d'archétypes")
                    else:
                        print(f"\n⚠️  Tournois trouvés mais aucune decklist récupérée")
                        print(f"   - Possible problème de parsing des decklists")
                        
                else:
                    print(f"\n❌ AUCUN TOURNOI TROUVÉ")
                    print(f"   - Soit il n'y a pas de tournois Standard dans cette période")
                    print(f"   - Soit il y a un problème avec la recherche")
                    
            else:
                print(f"❌ ÉCHEC - Impossible de s'authentifier")
                print(f"   - Vérifiez les credentials dans .env")
                print(f"   - Vérifiez que Chrome est accessible")
                
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        
    print(f"\n" + "=" * 70)
    print(f"FIN DU TEST RÉEL")

if __name__ == "__main__":
    asyncio.run(test_melee_real())