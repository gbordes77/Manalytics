#!/usr/bin/env python3
"""
Test des URLs de juillet 2025 du rapport fbettega
"""

import asyncio
import json

import aiohttp


async def test_july_2025_urls():
    """Test les URLs de juillet 2025 du rapport fbettega"""

    print("🧪 Test des URLs juillet 2025:")

    # Charger le rapport fbettega
    with open(
        "rapport_fbettega_2025-07-01_2025-07-15.json", "r", encoding="utf-8"
    ) as f:
        rapport = json.load(f)

    # Prendre quelques URLs MTGO du rapport
    mtgo_urls = []
    for tournament in rapport["details_par_source"]["MTGO"][:5]:  # Premiers 5
        mtgo_urls.append(tournament["uri"])

    print(f"   URLs à tester: {len(mtgo_urls)}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:

        for i, url in enumerate(mtgo_urls):
            print(f"\n   === URL {i+1} ===")
            print(f"   {url}")

            try:
                async with session.get(url) as response:
                    print(f"   Status: {response.status}")

                    if response.status == 200:
                        html = await response.text()
                        print(f"   HTML length: {len(html)}")

                        # Chercher le pattern decklist JSON
                        import re

                        pattern = r"decklist[^=]*=\s*(\{[^;]+\});"
                        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

                        if matches:
                            print(f"   ✅ JSON decklist trouvé: {len(matches[0])} chars")

                            # Parser le JSON pour voir s'il y a des decks
                            try:
                                data = json.loads(matches[0])
                                decklists = data.get("decklists", [])
                                standings = data.get("standings", [])
                                print(f"   Decks: {len(decklists)}")
                                print(f"   Standings: {len(standings)}")

                                if decklists and standings:
                                    print(f"   ✅ Tournoi valide avec données!")
                                else:
                                    print(f"   ❌ Tournoi vide (pas de decks/standings)")

                            except Exception as e:
                                print(f"   ❌ Erreur parsing JSON: {e}")
                        else:
                            print(f"   ❌ Pas de JSON decklist trouvé")
                    else:
                        print(f"   ❌ HTTP Error: {response.status}")

            except Exception as e:
                print(f"   ❌ Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_july_2025_urls())
