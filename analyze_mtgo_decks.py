#!/usr/bin/env python3
"""
Analyse détaillée de la structure des decks MTGO
"""

import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def analyze_mtgo_decks():
    """Analyse la structure des decks sur une page MTGO"""

    url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🔍 Analyse détaillée des decks MTGO:")
    print(f"   URL: {url}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Chercher tous les éléments avec des IDs contenant "deck"
                    deck_elements = soup.find_all(
                        "div", id=lambda x: x and "deck" in x.lower()
                    )

                    print(f"   Éléments avec ID contenant 'deck': {len(deck_elements)}")

                    for i, deck_elem in enumerate(deck_elements):
                        print(f"\n   === DECK {i+1} ===")
                        print(f"   ID: {deck_elem.get('id', 'N/A')}")
                        print(f"   Classes: {deck_elem.get('class', [])}")

                        # Chercher le nom du joueur
                        player_patterns = [
                            deck_elem.find("h3"),
                            deck_elem.find("h4"),
                            deck_elem.find("h5"),
                            deck_elem.find("span", class_="player"),
                            deck_elem.find("div", class_="player"),
                            deck_elem.find("strong"),
                            deck_elem.find("b"),
                        ]

                        player_found = False
                        for pattern in player_patterns:
                            if pattern:
                                player_text = pattern.get_text().strip()
                                if (
                                    player_text and len(player_text) < 50
                                ):  # Nom raisonnable
                                    print(
                                        f"   Joueur (via {pattern.name}.{pattern.get('class', [])}): {player_text}"
                                    )
                                    player_found = True
                                    break

                        if not player_found:
                            # Chercher dans les premiers éléments de texte
                            text_content = deck_elem.get_text().strip()
                            lines = [
                                line.strip()
                                for line in text_content.split("\n")
                                if line.strip()
                            ]
                            if lines:
                                print(f"   Premier texte: {lines[0][:100]}...")

                        # Chercher les résultats
                        result_patterns = [
                            deck_elem.find("span", class_="result"),
                            deck_elem.find("span", class_="record"),
                            deck_elem.find("div", class_="placement"),
                            deck_elem.find("div", class_="result"),
                        ]

                        for pattern in result_patterns:
                            if pattern:
                                result_text = pattern.get_text().strip()
                                if result_text:
                                    print(
                                        f"   Résultat (via {pattern.name}.{pattern.get('class', [])}): {result_text}"
                                    )
                                    break

                        # Chercher les cartes
                        card_patterns = [
                            deck_elem.find_all("span", class_="card"),
                            deck_elem.find_all("div", class_="card"),
                            deck_elem.find_all("li", class_="card"),
                            deck_elem.find_all("span", class_="cardname"),
                            deck_elem.find_all("div", class_="cardname"),
                        ]

                        total_cards = 0
                        for pattern_name, pattern in zip(
                            [
                                "span.card",
                                "div.card",
                                "li.card",
                                "span.cardname",
                                "div.cardname",
                            ],
                            card_patterns,
                        ):
                            if pattern:
                                print(
                                    f"   Cartes trouvées via {pattern_name}: {len(pattern)}"
                                )
                                total_cards = max(total_cards, len(pattern))

                                # Afficher quelques exemples
                                for j, card in enumerate(pattern[:3]):
                                    card_text = card.get_text().strip()
                                    print(f"     [{j}]: {card_text}")

                        print(f"   Total cartes estimé: {total_cards}")

                        # Sauvegarder le HTML de ce deck pour analyse
                        with open(
                            f"deck_{i+1}_sample.html", "w", encoding="utf-8"
                        ) as f:
                            f.write(str(deck_elem))
                        print(f"   HTML sauvegardé: deck_{i+1}_sample.html")

                        if i >= 2:  # Limiter à 3 decks pour l'analyse
                            break

                else:
                    print(f"   Error: HTTP {response.status}")

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    asyncio.run(analyze_mtgo_decks())
