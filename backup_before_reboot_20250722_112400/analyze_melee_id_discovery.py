#!/usr/bin/env python3
"""
Analyse : Comment fbettega découvre les IDs de tournois Melee
"""

import asyncio
import json
import re

import aiohttp
from bs4 import BeautifulSoup


async def analyze_id_discovery_methods():
    print("🔍 ANALYSE : Découverte des IDs Tournois Melee")
    print("=" * 60)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession(
        headers=headers, timeout=aiohttp.ClientTimeout(total=30)
    ) as session:

        # Méthode 1: API endpoints possibles
        print("🔍 Méthode 1: Recherche d'API endpoints")

        api_endpoints = [
            "https://melee.gg/api/tournaments",
            "https://melee.gg/api/tournament/search",
            "https://melee.gg/api/events",
            "https://melee.gg/Tournament/Api/Search",
            "https://melee.gg/Tournament/GetRecent",
            "https://melee.gg/api/v1/tournaments",
        ]

        for endpoint in api_endpoints:
            try:
                print(f"   Test: {endpoint}")
                async with session.get(endpoint) as response:
                    print(f"      Status: {response.status}")

                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"      ✅ JSON Response: {len(str(data))} chars")

                            # Chercher des IDs de tournois
                            data_str = str(data)
                            tournament_ids = re.findall(r'"id":\s*(\d+)', data_str)
                            if tournament_ids:
                                print(f"      🎯 IDs trouvés: {tournament_ids[:5]}")
                                return tournament_ids

                        except:
                            text = await response.text()
                            print(f"      📄 Text Response: {len(text)} chars")

                            # Chercher des patterns d'IDs dans le texte
                            tournament_ids = re.findall(r"/Tournament/View/(\d+)", text)
                            if tournament_ids:
                                print(
                                    f"      🎯 IDs trouvés dans HTML: {tournament_ids[:5]}"
                                )
                                return tournament_ids

                    elif response.status == 404:
                        print(f"      ❌ Endpoint n'existe pas")
                    else:
                        print(f"      ⚠️  Status {response.status}")

            except Exception as e:
                print(f"      ❌ Erreur: {e}")

        print()

        # Méthode 2: Pages de listing/recherche
        print("🔍 Méthode 2: Pages de listing avec JavaScript")

        listing_pages = [
            "https://melee.gg/Tournament/Search",
            "https://melee.gg/Tournament/Search?game=mtg",
            "https://melee.gg/Search",
            "https://melee.gg/Events",
            "https://melee.gg/",  # Page d'accueil
        ]

        for page_url in listing_pages:
            try:
                print(f"   Test: {page_url}")
                async with session.get(page_url) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Chercher des IDs dans le HTML
                        tournament_ids = re.findall(r"/Tournament/View/(\d+)", html)
                        decklist_ids = re.findall(r"/Decklist/View/(\d+)", html)

                        print(f"      Tournament IDs: {len(tournament_ids)} trouvés")
                        print(f"      Decklist IDs: {len(decklist_ids)} trouvés")

                        if tournament_ids:
                            print(
                                f"      🎯 Exemples Tournament IDs: {tournament_ids[:5]}"
                            )
                        if decklist_ids:
                            print(f"      🎯 Exemples Decklist IDs: {decklist_ids[:5]}")

                        # Chercher des scripts avec des données JSON
                        scripts = re.findall(
                            r"<script[^>]*>(.*?)</script>", html, re.DOTALL
                        )
                        for script in scripts:
                            if "tournament" in script.lower() and (
                                "{" in script or "[" in script
                            ):
                                print(
                                    f"      📜 Script avec données trouvé: {len(script)} chars"
                                )

                                # Chercher des IDs dans le JavaScript
                                js_ids = re.findall(r'"id":\s*(\d+)', script)
                                if js_ids:
                                    print(f"      🎯 IDs dans JavaScript: {js_ids[:5]}")
                                    return js_ids

                        if tournament_ids:
                            return tournament_ids

            except Exception as e:
                print(f"      ❌ Erreur: {e}")

        print()

        # Méthode 3: Analyse des patterns d'IDs existants
        print("🔍 Méthode 3: Analyse patterns IDs existants")

        # Analyser les IDs des données existantes
        existing_ids = [4383, 4616, 4500]  # De nos données 2020
        print(f"   IDs 2020: {existing_ids}")

        # Estimer les IDs 2025 (5 ans plus tard)
        # Si ~500 tournois/an, alors +2500 IDs
        estimated_2025_range = [id + 2500 for id in existing_ids]
        print(f"   IDs estimés 2025: {estimated_2025_range}")

        # Tester quelques IDs dans cette gamme
        print("   Test IDs estimés:")
        found_ids = []

        for test_id in estimated_2025_range:
            try:
                test_url = f"https://melee.gg/Tournament/View/{test_id}"
                async with session.get(test_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        if "tournament" in html.lower() and "2025" in html:
                            print(f"      ✅ ID {test_id} existe et contient 2025")
                            found_ids.append(test_id)
                    elif response.status == 404:
                        print(f"      ❌ ID {test_id} n'existe pas")

            except Exception as e:
                print(f"      ❌ Erreur ID {test_id}: {e}")

        if found_ids:
            return found_ids

        return []


if __name__ == "__main__":
    ids = asyncio.run(analyze_id_discovery_methods())
    print("\n" + "=" * 60)
    if ids:
        print(f"✅ MÉTHODE DÉCOUVERTE : {len(ids)} IDs trouvés")
        print(f"   IDs: {ids[:10]}")
        print("   → Fbettega utilise probablement cette méthode")
    else:
        print("❌ MÉTHODE NON DÉCOUVERTE")
        print("   → Fbettega utilise peut-être :")
        print("     - API privée avec credentials")
        print("     - Scraping incrémental par date")
        print("     - Notification webhooks")
        print("     - Partenariat direct avec Melee")
