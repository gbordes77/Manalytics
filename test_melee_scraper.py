#!/usr/bin/env python3
"""
Test Melee Scraper Authentique - Test de la reproduction fidèle de fbettega/mtg_decklist_scrapper
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.melee_scraper_authentic import MtgMeleeScraper
from scraper.models.base_models import *


def test_melee_scraper():
    """Test du scraper Melee authentique"""
    print("🧪 Test du scraper Melee authentique...")

    # Créer le scraper
    cache_folder = "data/raw/melee"
    scraper = MtgMeleeScraper(cache_folder)

    # Définir une période de test (derniers 7 jours)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)

    print(f"📅 Période de test: {start_date.date()} à {end_date.date()}")

    try:
        # Récupérer la liste des tournois
        print("🔍 Récupération de la liste des tournois...")
        tournaments = scraper.fetch_tournaments(start_date, end_date)

        print(f"✅ {len(tournaments)} tournois trouvés")

        if tournaments:
            # Tester avec le premier tournoi
            test_tournament = tournaments[0]
            print(f"🎯 Test avec le tournoi: {test_tournament.name}")
            print(f"   Date: {test_tournament.date}")
            print(f"   URI: {test_tournament.uri}")
            print(f"   Format: {test_tournament.formats}")

            # Récupérer les détails du tournoi
            print("📊 Récupération des détails du tournoi...")
            details = scraper.fetch_tournament_details(test_tournament)

            if details:
                print(f"✅ Détails récupérés avec succès!")
                print(f"   Nombre de decks: {len(details.decks)}")
                print(
                    f"   Nombre de rounds: {len(details.rounds) if details.rounds else 0}"
                )
                print(
                    f"   Nombre de standings: {len(details.standings) if details.standings else 0}"
                )

                # Afficher quelques exemples de decks
                if details.decks:
                    print("\n📋 Exemples de decks:")
                    for i, deck in enumerate(
                        details.decks[:3]
                    ):  # Afficher les 3 premiers
                        print(
                            f"   {i+1}. {deck.player} - {deck.result} - {len(deck.mainboard)} cartes main"
                        )

                # Afficher quelques exemples de standings
                if details.standings:
                    print("\n🏆 Exemples de standings:")
                    for i, standing in enumerate(
                        details.standings[:3]
                    ):  # Afficher les 3 premiers
                        print(
                            f"   {i+1}. {standing.player} - Rank {standing.rank} - {standing.wins}-{standing.losses}-{standing.draws}"
                        )

                # Sauvegarder le tournoi
                print("\n💾 Sauvegarde du tournoi...")
                target_folder = os.path.join(cache_folder, "test")
                saved_file = scraper.save_tournament(details, target_folder)
                print(f"✅ Tournoi sauvegardé: {saved_file}")

            else:
                print("❌ Impossible de récupérer les détails du tournoi")

        else:
            print("⚠️ Aucun tournoi trouvé dans la période spécifiée")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()


def test_melee_client():
    """Test du client Melee directement"""
    print("\n🧪 Test du client Melee directement...")

    from scraper.melee_scraper_authentic import MtgMeleeClient

    client = MtgMeleeClient()

    # Test de récupération des tournois
    print("🔍 Test de récupération des tournois...")
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=3)

    try:
        tournaments = client.get_tournaments(start_date, end_date)
        print(f"✅ {len(tournaments)} tournois récupérés via API")

        if tournaments:
            # Tester avec le premier tournoi
            test_tournament = tournaments[0]
            print(f"🎯 Test avec le tournoi: {test_tournament['name']}")
            print(f"   ID: {test_tournament['tournament_id']}")
            print(f"   Format: {test_tournament['formats']}")
            print(f"   Status: {test_tournament['status']}")

            # Test de récupération des joueurs
            print("👥 Test de récupération des joueurs...")
            players = client.get_players(test_tournament["uri"], max_players=5)

            if players:
                print(f"✅ {len(players)} joueurs récupérés")

                # Tester avec le premier joueur
                test_player = players[0]
                print(f"🎯 Test avec le joueur: {test_player['player_name']}")
                print(f"   Rank: {test_player['standing'].rank}")
                print(f"   Result: {test_player['result']}")
                print(f"   Decks: {len(test_player['decks'])}")

                if test_player["decks"]:
                    # Test de récupération d'un deck
                    print("📋 Test de récupération d'un deck...")
                    deck_info = test_player["decks"][0]
                    deck = client.get_deck(deck_info["uri"], players)

                    if deck:
                        print(f"✅ Deck récupéré avec succès!")
                        print(f"   Joueur: {deck['player']}")
                        print(f"   Format: {deck['format']}")
                        print(f"   Mainboard: {len(deck['mainboard'])} cartes")
                        print(f"   Sideboard: {len(deck['sideboard'])} cartes")
                    else:
                        print("❌ Impossible de récupérer le deck")

            else:
                print("❌ Aucun joueur récupéré")

    except Exception as e:
        print(f"❌ Erreur lors du test client: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Fonction principale de test"""
    print("🚀 Test du scraper Melee Authentic - Reproduction fidèle de fbettega")
    print("=" * 70)

    # Test du client Melee
    test_melee_client()

    # Test du scraper Melee complet
    test_melee_scraper()

    print("\n" + "=" * 70)
    print("✅ Tests terminés!")


if __name__ == "__main__":
    main()
