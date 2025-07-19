#!/usr/bin/env python3
"""
Test des améliorations fbettega:
1. MTGO Discovery (au lieu de génération d'URLs)
2. Melee Authentication avec credentials
"""

import asyncio
import logging
import os
import sys

sys.path.append("src")

from python.scraper.fbettega_clients.MtgMeleeClientV2 import MtgMeleeClientV2
from python.scraper.fbettega_clients.MTGOclient import MTGOClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_mtgo_discovery():
    """Test MTGO URL discovery"""
    print("\n🚀 TEST MTGO DISCOVERY")
    print("=" * 50)

    config = {"timeout": 30, "retries": 3}

    async with MTGOClient("data/raw/mtgo", config) as mtgo_client:
        # Test période courte pour validation
        tournaments = await mtgo_client.fetch_tournaments(
            "Standard", "2025-07-10", "2025-07-15"
        )

        print(f"📊 RÉSULTATS MTGO:")
        print(f"   - Tournois trouvés: {len(tournaments)}")

        valid_tournaments = 0
        total_decks = 0

        for tournament in tournaments:
            decks = tournament.get("decks", [])
            if len(decks) > 0:
                valid_tournaments += 1
                total_decks += len(decks)

                print(f"   ✅ {tournament.get('name', 'Unknown')}: {len(decks)} decks")

                # Vérifier qu'on a des cartes réelles
                for deck in decks[:2]:  # Vérifier les 2 premiers decks
                    mainboard = deck.get("Mainboard", [])
                    if len(mainboard) >= 10:
                        print(
                            f"      - {deck.get('Player', 'Unknown')}: {len(mainboard)} cartes mainboard"
                        )
                        break
            else:
                print(f"   ❌ {tournament.get('name', 'Unknown')}: 0 decks")

        print(f"\n📈 STATISTIQUES:")
        print(f"   - Tournois valides: {valid_tournaments}/{len(tournaments)}")
        print(f"   - Total decks: {total_decks}")
        print(
            f"   - Taux de succès: {(valid_tournaments/len(tournaments)*100):.1f}%"
            if tournaments
            else "0%"
        )


async def test_melee_authentication():
    """Test Melee authentication et récupération"""
    print("\n🔐 TEST MELEE AUTHENTICATION")
    print("=" * 50)

    config = {"timeout": 30, "retries": 3}

    async with MtgMeleeClientV2("data/raw/melee", config) as melee_client:
        # Vérifier que les credentials sont chargés
        if melee_client.credentials:
            print(
                f"✅ Credentials chargés: {melee_client.credentials.get('email', 'N/A')}"
            )
        else:
            print("❌ Pas de credentials trouvés")
            return

        # Test récupération de tournois
        tournaments = await melee_client.fetch_tournaments(
            "Standard", "2025-07-10", "2025-07-15"
        )

        print(f"📊 RÉSULTATS MELEE:")
        print(f"   - Tournois trouvés: {len(tournaments)}")

        for tournament in tournaments[:3]:  # Afficher les 3 premiers
            decks = tournament.get("decks", [])
            print(f"   - {tournament.get('name', 'Unknown')}: {len(decks)} decks")


async def test_combined_fbettega():
    """Test combiné des deux clients"""
    print("\n🔄 TEST COMBINÉ FBETTEGA")
    print("=" * 50)

    # Test en parallèle
    mtgo_task = test_mtgo_discovery()
    melee_task = test_melee_authentication()

    await asyncio.gather(mtgo_task, melee_task, return_exceptions=True)


async def main():
    """Test principal"""
    print("🧪 TEST AMÉLIORATIONS FBETTEGA")
    print("=" * 60)

    try:
        await test_combined_fbettega()

        print("\n✅ TESTS TERMINÉS")
        print("Vérifiez les logs ci-dessus pour valider les améliorations")

    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
