#!/usr/bin/env python3
"""
Test du code MTGO copié directement depuis fbettega/mtg_decklist_scrapper
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.fbettega_clients.mtgo_client import TournamentList


def test_fbettega_mtgo_code():
    """Test du code MTGO de fbettega directement"""
    print("🧪 Test du code MTGO de fbettega (copie directe)...")

    # Définir une période de test (derniers 7 jours)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)

    print(f"📅 Période de test: {start_date.date()} à {end_date.date()}")

    try:
        # Test de DL_tournaments (copié depuis fbettega)
        print("🔍 Test de DL_tournaments()...")
        tournaments = TournamentList.DL_tournaments(start_date, end_date)

        print(f"✅ {len(tournaments)} tournois récupérés")

        if tournaments:
            # Tester avec le premier tournoi
            test_tournament = tournaments[0]
            print(f"🎯 Test avec le tournoi: {test_tournament.name}")
            print(f"   Date: {test_tournament.date}")
            print(f"   URI: {test_tournament.uri}")
            print(f"   Format: {test_tournament.formats}")
            print(f"   JSON file: {test_tournament.json_file}")

            # Test de get_tournament_details (copié depuis fbettega)
            print("📊 Test de get_tournament_details()...")
            tournament_list = TournamentList()
            details = tournament_list.get_tournament_details(test_tournament)

            if details:
                print(f"✅ Détails récupérés avec succès!")
                print(
                    f"   Nombre de decks: {len(details.decks) if details.decks else 0}"
                )
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
                        if deck.mainboard:
                            print(
                                f"      Quelques cartes: {[f'{item.count}x {item.card_name}' for item in deck.mainboard[:3]]}"
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

            else:
                print("❌ Impossible de récupérer les détails du tournoi")

        else:
            print("⚠️ Aucun tournoi trouvé dans la période spécifiée")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Fonction principale de test"""
    print("🚀 Test du code MTGO copié directement depuis fbettega")
    print("=" * 70)

    test_fbettega_mtgo_code()

    print("\n" + "=" * 70)
    print("✅ Test terminé!")


if __name__ == "__main__":
    main()
