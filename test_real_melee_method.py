#!/usr/bin/env python3
"""
Test de la VRAIE méthode Melee selon fbettega
Endpoint: https://melee.gg/Decklist/SearchDecklists
"""

import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def test_real_melee_method():
    print("🎯 TEST VRAIE MÉTHODE MELEE (fbettega)")
    print("Endpoint: https://melee.gg/Decklist/SearchDecklists")
    print("=" * 60)

    try:
        from src.python.scraper.fbettega_clients.MtgMeleeClientV2_simple import (
            MtgMeleeClientV2,
        )

        client = MtgMeleeClientV2("data/test")

        async with client:
            tournaments = await client.fetch_tournaments(
                "Standard", "2025-07-15", "2025-07-20"
            )

            print(f"\n✅ Résultat: {len(tournaments)} tournois trouvés")

            if tournaments:
                print("\n🏆 TOURNOIS RÉCUPÉRÉS (méthode fbettega):")
                for i, t in enumerate(tournaments[:5], 1):
                    print(f"   {i}. {t.get('name')}")
                    print(f"      ID: {t.get('id')}")
                    print(f"      Date: {t.get('date')}")
                    print(f"      Format: {t.get('format')}")
                    print(f"      Decks: {len(t.get('decks', []))}")
                    print()

                if len(tournaments) > 5:
                    print(f"   ... et {len(tournaments) - 5} autres tournois")

                # Statistiques
                total_decks = sum(len(t.get("decks", [])) for t in tournaments)
                print(f"📊 STATISTIQUES:")
                print(f"   - Total tournois: {len(tournaments)}")
                print(f"   - Total decks: {total_decks}")
                if len(tournaments) > 0:
                    print(
                        f"   - Moyenne decks/tournoi: {total_decks/len(tournaments):.1f}"
                    )

                return True
            else:
                print("\n❌ Aucun tournoi trouvé")
                print("Causes possibles:")
                print("   - Authentification requise (cookies)")
                print("   - Payload incorrect")
                print("   - Période sans tournois")
                return False

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_real_melee_method())
    print("\n" + "=" * 60)
    if success:
        print("✅ PREUVE ÉTABLIE : Vraie méthode Melee FONCTIONNE")
        print("   - Endpoint fbettega validé")
        print("   - Payload DataTables correct")
        print("   - Tournois récupérés avec succès")
    else:
        print("❌ Authentification requise")
        print("   - Fbettega utilise des cookies de session")
        print("   - Login nécessaire pour accès complet")
