#!/usr/bin/env python3
"""
Test du scraper MTGO fbettega avec une URL réelle
"""

import asyncio
import logging

from src.python.scraper.fbettega_clients.MTGOclient import MTGOClient

# Configuration du logging
logging.basicConfig(level=logging.INFO)


async def test_mtgo_scraper():
    """Test le scraper MTGO avec une URL réelle"""

    # URL d'un tournoi réel de juin 2024
    test_url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🧪 Test du scraper MTGO avec URL réelle:")
    print(f"   URL: {test_url}")

    async with MTGOClient() as client:
        # Tester le parsing d'une URL spécifique
        tournament_data = await client._parse_tournament_url(test_url)

        if tournament_data:
            print(f"✅ Tournoi trouvé:")
            print(f"   Nom: {tournament_data.get('name', 'N/A')}")
            print(f"   Date: {tournament_data.get('date', 'N/A')}")
            print(f"   Type: {tournament_data.get('type', 'N/A')}")
            print(f"   Decks: {len(tournament_data.get('decks', []))}")

            # Afficher quelques decks
            decks = tournament_data.get("decks", [])
            for i, deck in enumerate(decks[:3]):  # Premiers 3 decks
                print(
                    f"   Deck {i+1}: {deck.get('Player', 'N/A')} - {deck.get('Result', 'N/A')} - {len(deck.get('Mainboard', []))} cartes"
                )
        else:
            print("❌ Aucun tournoi trouvé")


if __name__ == "__main__":
    asyncio.run(test_mtgo_scraper())
