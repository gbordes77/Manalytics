#!/usr/bin/env python3
"""
Découvrir les vraies URLs des tournois MTGO en scrappant les pages de listing
"""

import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup


async def discover_mtgo_urls():
    """Découvrir les URLs des tournois MTGO"""

    # Pages de listing MTGO à scraper
    listing_urls = [
        "https://www.mtgo.com/decklists",
        "https://www.mtgo.com/decklists/standard",
        "https://www.mtgo.com/decklists/modern",
        "https://www.mtgo.com/decklists/legacy",
        "https://www.mtgo.com/decklists/pioneer",
        "https://www.mtgo.com/decklist",  # Page principale
    ]

    print(f"🔍 Découverte des URLs MTGO:")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:

        all_tournament_urls = set()

        for listing_url in listing_urls:
            print(f"\n   Scraping: {listing_url}")

            try:
                async with session.get(listing_url) as response:
                    print(f"   Status: {response.status}")

                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Chercher tous les liens vers des decklists
                        tournament_patterns = [
                            soup.find_all(
                                "a",
                                href=re.compile(r"/decklist/[^/]+-\d{4}-\d{2}-\d{2}"),
                            ),
                            soup.find_all(
                                "a", href=re.compile(r"/decklist/.*challenge.*\d+")
                            ),
                            soup.find_all(
                                "a", href=re.compile(r"/decklist/.*league.*\d+")
                            ),
                            soup.find_all(
                                "a", href=re.compile(r"/decklist/.*qualifier.*\d+")
                            ),
                            soup.find_all(
                                "a", href=re.compile(r"/decklist/.*preliminary.*\d+")
                            ),
                        ]

                        found_urls = set()
                        for pattern in tournament_patterns:
                            for link in pattern:
                                href = link.get("href", "")
                                if href.startswith("/decklist/"):
                                    full_url = f"https://www.mtgo.com{href}"
                                    found_urls.add(full_url)
                                    all_tournament_urls.add(full_url)

                        print(f"   URLs trouvées: {len(found_urls)}")

                        # Afficher quelques exemples
                        for i, url in enumerate(list(found_urls)[:3]):
                            print(f"     - {url}")

                        # Sauvegarder le HTML pour analyse
                        with open(
                            f'mtgo_listing_{listing_url.split("/")[-1] or "main"}.html',
                            "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(html[:10000])  # Premiers 10k chars

                    else:
                        print(f"   Erreur HTTP: {response.status}")

            except Exception as e:
                print(f"   Exception: {e}")

        print(f"\n🎯 Résumé:")
        print(f"   Total URLs uniques trouvées: {len(all_tournament_urls)}")

        # Sauvegarder toutes les URLs
        with open("discovered_mtgo_urls.txt", "w", encoding="utf-8") as f:
            for url in sorted(all_tournament_urls):
                f.write(f"{url}\n")

        print(f"   URLs sauvegardées: discovered_mtgo_urls.txt")

        # Analyser les patterns d'URLs
        print(f"\n   Analyse des patterns:")
        patterns = {}
        for url in all_tournament_urls:
            # Extraire le pattern (sans les IDs numériques)
            pattern = re.sub(r"\d+", "X", url.split("/")[-1])
            patterns[pattern] = patterns.get(pattern, 0) + 1

        for pattern, count in sorted(
            patterns.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"     {pattern}: {count} URLs")


if __name__ == "__main__":
    asyncio.run(discover_mtgo_urls())
