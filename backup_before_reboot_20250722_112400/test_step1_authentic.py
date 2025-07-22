#!/usr/bin/env python3
"""
Test Step 1 Authentic - Test de la reproduction fidèle de fbettega/mtg_decklist_scrapper
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.models.base_models import *
from scraper.mtgo_scraper_authentic import MTGOScraper


def test_mtgo_scraper():
    """Test du scraper MTGO authentique"""
    print("🧪 Test du scraper MTGO authentique...")

    # Créer le scraper
    cache_folder = "data/raw/mtgo"
    scraper = MTGOScraper(cache_folder)

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


def test_models():
    """Test des modèles de données"""
    print("\n🧪 Test des modèles de données...")

    # Test Tournament
    tournament = Tournament(
        date=datetime.now(),
        name="Test Tournament",
        uri="https://example.com",
        formats="Standard",
        json_file="test.json",
    )
    print(f"✅ Tournament créé: {tournament}")

    # Test DeckItem
    deck_item = DeckItem(count=4, card_name="Lightning Bolt")
    print(f"✅ DeckItem créé: {deck_item.to_dict()}")

    # Test Deck
    deck = Deck(
        date=datetime.now(),
        player="TestPlayer",
        result="5-0",
        anchor_uri="https://example.com#deck_TestPlayer",
        mainboard=[deck_item],
        sideboard=[],
    )
    print(f"✅ Deck créé: {deck}")

    # Test Standing
    standing = Standing(
        rank=1, player="TestPlayer", points=15, wins=5, losses=0, draws=0
    )
    print(f"✅ Standing créé: {standing}")

    # Test CacheItem
    cache_item = CacheItem(
        tournament=tournament, decks=[deck], rounds=[], standings=[standing]
    )
    print(f"✅ CacheItem créé: {cache_item}")


def main():
    """Fonction principale de test"""
    print("🚀 Test de la Step 1 Authentic - Reproduction fidèle de fbettega")
    print("=" * 60)

    # Test des modèles
    test_models()

    # Test du scraper MTGO
    test_mtgo_scraper()

    print("\n" + "=" * 60)
    print("✅ Tests terminés!")


if __name__ == "__main__":
    main()
