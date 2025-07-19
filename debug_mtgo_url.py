#!/usr/bin/env python3
"""
Debug de l'URL MTGO pour comprendre la structure HTML
"""

import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def debug_mtgo_url():
    """Debug l'URL MTGO pour voir la structure HTML"""

    url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🔍 Debug de l'URL MTGO:")
    print(f"   URL: {url}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:
        try:
            async with session.get(url) as response:
                print(f"   Status: {response.status}")

                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Analyser la structure
                    print(f"   HTML length: {len(html)}")

                    # Chercher le titre
                    title = soup.find("title")
                    print(
                        f"   Title: {title.get_text().strip() if title else 'Not found'}"
                    )

                    # Chercher les h1
                    h1_tags = soup.find_all("h1")
                    print(f"   H1 tags: {len(h1_tags)}")
                    for h1 in h1_tags[:3]:
                        print(f"     - {h1.get_text().strip()}")

                    # Chercher les patterns de decks
                    deck_patterns = [
                        ("div.deck-group", soup.find_all("div", class_="deck-group")),
                        ("div.deck", soup.find_all("div", class_="deck")),
                        ("div.decklist", soup.find_all("div", class_="decklist")),
                        ("section.deck", soup.find_all("section", class_="deck")),
                        (
                            'div[id*="deck"]',
                            soup.find_all(
                                "div", id=lambda x: x and "deck" in x.lower()
                            ),
                        ),
                        (
                            'a[href*="#deck"]',
                            soup.find_all("a", href=lambda x: x and "#deck" in x),
                        ),
                    ]

                    print(f"   Deck patterns found:")
                    for pattern_name, elements in deck_patterns:
                        print(f"     {pattern_name}: {len(elements)} elements")
                        if elements:
                            for i, elem in enumerate(elements[:2]):  # Premiers 2
                                text = elem.get_text().strip()[
                                    :100
                                ]  # Premiers 100 chars
                                print(f"       [{i}]: {text}...")

                    # Sauvegarder un échantillon du HTML pour analyse
                    with open("debug_mtgo_sample.html", "w", encoding="utf-8") as f:
                        f.write(html[:5000])  # Premiers 5000 chars
                    print(f"   HTML sample saved to debug_mtgo_sample.html")

                else:
                    print(f"   Error: HTTP {response.status}")

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    asyncio.run(debug_mtgo_url())
