#!/usr/bin/env python3
"""
Test direct du FbettegaIntegrator avec les améliorations
"""

import asyncio
import os
import sys

sys.path.append("src")

from python.scraper.fbettega_integrator import FbettegaIntegrator


async def test_fbettega_integrator():
    """Test direct du FbettegaIntegrator"""

    print("🚀 TEST FBETTEGA INTEGRATOR DIRECT")
    print("=" * 60)

    try:
        # Configuration
        cache_folder = "data/raw"
        api_config = {"timeout": 30, "retries": 3}

        # Créer l'intégrateur
        fbettega = FbettegaIntegrator(cache_folder, api_config)

        print("📅 Période de test: 2025-07-10 à 2025-07-15")
        print("🎯 Format: Standard")

        # Fetch tournaments avec cache intelligent
        tournaments = await fbettega.get_tournaments_with_cache(
            "Standard", "2025-07-10", "2025-07-15"
        )

        print(f"\n📊 RÉSULTATS FBETTEGA INTEGRATOR:")
        print(f"   - Tournois trouvés: {len(tournaments)}")

        total_decks = 0
        valid_tournaments = 0

        for tournament in tournaments:
            decks = tournament.get("decks", [])
            total_decks += len(decks)

            if len(decks) > 0:
                valid_tournaments += 1
                source = tournament.get("fbettega_source", "unknown")
                print(
                    f"   ✅ [{source}] {tournament.get('name', 'Unknown')}: {len(decks)} decks"
                )

                # Vérifier quelques decks
                for deck in decks[:2]:
                    mainboard = deck.get("Mainboard", [])
                    player = deck.get("Player", "Unknown")
                    print(f"      - {player}: {len(mainboard)} cartes mainboard")
            else:
                print(f"   ❌ {tournament.get('name', 'Unknown')}: 0 decks")

        print(f"\n📈 STATISTIQUES FINALES:")
        print(f"   - Tournois valides: {valid_tournaments}/{len(tournaments)}")
        print(f"   - Total decks: {total_decks}")
        print(
            f"   - Taux de succès: {(valid_tournaments/len(tournaments)*100):.1f}%"
            if tournaments
            else "0%"
        )

        # Vérifier les sources
        sources = set()
        for tournament in tournaments:
            source = tournament.get("fbettega_source", "unknown")
            sources.add(source)

        print(f"   - Sources actives: {', '.join(sources)}")

        if total_decks > 0:
            print("\n🎉 SUCCÈS ! Fbettega fonctionne avec des données réelles")
        else:
            print("\n⚠️ Aucun deck trouvé - vérifier la configuration")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_fbettega_integrator())
