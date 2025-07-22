#!/usr/bin/env python3
"""
Test détaillé du scraper MTGO fbettega
"""

import asyncio
import logging

from src.python.scraper.fbettega_clients.MTGOclient import MTGOClient

# Configuration du logging
logging.basicConfig(level=logging.INFO)


async def test_mtgo_detailed():
    """Test détaillé du scraper MTGO"""

    # URL d'un tournoi réel de juin 2024
    test_url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🧪 Test détaillé du scraper MTGO:")
    print(f"   URL: {test_url}")

    async with MTGOClient() as client:
        # Tester le parsing d'une URL spécifique
        tournament_data = await client._parse_tournament_url(test_url)

        if tournament_data:
            print(f"✅ Tournoi trouvé:")
            print(f"   Nom: {tournament_data.get('name', 'N/A')}")
            print(f"   Date: {tournament_data.get('date', 'N/A')}")
            print(f"   Format: {tournament_data.get('format', 'N/A')}")
            print(f"   Type: {tournament_data.get('type', 'N/A')}")
            print(f"   Total decks: {len(tournament_data.get('decks', []))}")

            # Analyser les premiers decks en détail
            decks = tournament_data.get("decks", [])
            for i, deck in enumerate(decks[:3]):  # Premiers 3 decks
                print(f"\n   === DECK {i+1} ===")
                print(f"   Joueur: {deck.get('Player', 'N/A')}")
                print(f"   Résultat: {deck.get('Result', 'N/A')}")

                mainboard = deck.get("Mainboard", [])
                sideboard = deck.get("Sideboard", [])

                print(f"   Mainboard: {len(mainboard)} cartes")
                total_main = sum(card.get("Count", 0) for card in mainboard)
                print(f"   Total mainboard: {total_main} cartes")

                print(f"   Sideboard: {len(sideboard)} cartes")
                total_side = sum(card.get("Count", 0) for card in sideboard)
                print(f"   Total sideboard: {total_side} cartes")

                # Afficher quelques cartes du mainboard
                print(f"   Exemples mainboard:")
                for j, card in enumerate(mainboard[:5]):
                    print(
                        f"     {card.get('Count', 0)}x {card.get('CardName', 'Unknown')}"
                    )

                # Afficher quelques cartes du sideboard
                if sideboard:
                    print(f"   Exemples sideboard:")
                    for j, card in enumerate(sideboard[:3]):
                        print(
                            f"     {card.get('Count', 0)}x {card.get('CardName', 'Unknown')}"
                        )
                else:
                    print(f"   Pas de sideboard trouvé")
        else:
            print("❌ Aucun tournoi trouvé")


if __name__ == "__main__":
    asyncio.run(test_mtgo_detailed())
