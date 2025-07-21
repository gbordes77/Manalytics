#!/usr/bin/env python3
"""
Test du code copié directement depuis fbettega/mtg_decklist_scrapper
Vérification que le code original fonctionne sans modification
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.fbettega_clients.melee_client import MtgMeleeClient


def test_fbettega_melee_code():
    """Test du code Melee de fbettega directement"""
    print("🧪 Test du code Melee de fbettega (copie directe)...")

    # Créer le client exactement comme dans fbettega
    client = MtgMeleeClient()

    # Définir une période de test (derniers 3 jours)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=3)

    print(f"📅 Période de test: {start_date.date()} à {end_date.date()}")

    try:
        # Test de get_tournaments (copié depuis fbettega)
        print("🔍 Test de get_tournaments()...")
        tournaments = client.get_tournaments(start_date, end_date)

        print(f"✅ {len(tournaments)} tournois récupérés")

        if tournaments:
            # Prendre le premier tournoi qui a des decklists
            test_tournament = None
            for tournament in tournaments:
                if tournament.decklists > 0:
                    test_tournament = tournament
                    break

            if test_tournament:
                print(f"🎯 Test avec le tournoi: {test_tournament.name}")
                print(f"   ID: {test_tournament.tournament_id}")
                print(f"   Format: {test_tournament.formats}")
                print(f"   Status: {test_tournament.statut}")
                print(f"   Decklists: {test_tournament.decklists}")

                # Test de get_players (copié depuis fbettega)
                print("👥 Test de get_players()...")
                players = client.get_players(test_tournament.uri, max_players=5)

                if players:
                    print(f"✅ {len(players)} joueurs récupérés")

                    # Tester avec le premier joueur
                    test_player = players[0]
                    print(f"🎯 Test avec le joueur: {test_player.player_name}")
                    print(f"   Username: {test_player.username}")
                    print(f"   Rank: {test_player.standing.rank}")
                    print(f"   Result: {test_player.result}")
                    print(
                        f"   Decks: {len(test_player.decks) if test_player.decks else 0}"
                    )

                    if test_player.decks and len(test_player.decks) > 0:
                        # Test de get_deck (copié depuis fbettega)
                        print("📋 Test de get_deck()...")
                        deck_info = test_player.decks[0]
                        deck = client.get_deck(
                            deck_info.uri, players, skip_round_data=True
                        )

                        if deck:
                            print(f"✅ Deck récupéré avec succès!")
                            print(f"   Joueur: {deck.player}")
                            print(f"   Format: {deck.format}")
                            print(f"   Mainboard: {len(deck.mainboard)} cartes")
                            print(f"   Sideboard: {len(deck.sideboard)} cartes")
                            print(
                                f"   Quelques cartes main: {[f'{item.count}x {item.card_name}' for item in deck.mainboard[:3]]}"
                            )
                        else:
                            print("❌ Impossible de récupérer le deck")
                    else:
                        print("⚠️ Aucun deck disponible pour ce joueur")

                else:
                    print("❌ Aucun joueur récupéré")
            else:
                print("⚠️ Aucun tournoi avec des decklists trouvé")
        else:
            print("⚠️ Aucun tournoi trouvé dans la période spécifiée")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Fonction principale de test"""
    print("🚀 Test du code copié directement depuis fbettega")
    print("=" * 70)

    test_fbettega_melee_code()

    print("\n" + "=" * 70)
    print("✅ Test terminé!")


if __name__ == "__main__":
    main()
