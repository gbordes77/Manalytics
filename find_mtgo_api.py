#!/usr/bin/env python3
"""
Chercher l'API ou les données JSON dans le HTML MTGO
"""

import asyncio
import json
import re

import aiohttp


async def find_mtgo_api():
    """Chercher l'API ou les données JSON dans le HTML"""

    url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🔍 Recherche de l'API MTGO:")
    print(f"   URL: {url}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()

                    # Chercher les patterns d'API
                    api_patterns = [
                        r'api["\']?\s*:\s*["\']([^"\']+)',
                        r'url["\']?\s*:\s*["\']([^"\']*api[^"\']*)',
                        r'endpoint["\']?\s*:\s*["\']([^"\']+)',
                        r'ajax["\']?\s*:\s*["\']([^"\']+)',
                        r'/api/[^"\'\s]+',
                        r'https?://[^"\'\s]*api[^"\'\s]*',
                    ]

                    print(f"   Recherche de patterns d'API...")
                    for pattern in api_patterns:
                        matches = re.findall(pattern, html, re.IGNORECASE)
                        if matches:
                            print(f"   Pattern '{pattern}': {len(matches)} matches")
                            for match in matches[:3]:  # Premiers 3
                                print(f"     - {match}")

                    # Chercher des données JSON inline
                    json_patterns = [
                        r"var\s+\w+\s*=\s*(\{[^;]+\});",
                        r"window\.\w+\s*=\s*(\{[^;]+\});",
                        r"data\s*:\s*(\{[^}]+\})",
                        r"decklist[^=]*=\s*(\{[^;]+\});",
                        r"tournament[^=]*=\s*(\{[^;]+\});",
                    ]

                    print(f"   Recherche de données JSON inline...")
                    for pattern in json_patterns:
                        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                        if matches:
                            print(f"   Pattern '{pattern}': {len(matches)} matches")
                            for i, match in enumerate(matches[:2]):  # Premiers 2
                                try:
                                    # Essayer de parser le JSON
                                    data = json.loads(match)
                                    print(
                                        f"     [{i}] JSON valide: {len(str(data))} chars"
                                    )
                                    if isinstance(data, dict):
                                        keys = list(data.keys())[:5]  # Premières 5 clés
                                        print(f"         Clés: {keys}")
                                except:
                                    print(f"     [{i}] JSON invalide: {match[:100]}...")

                    # Chercher des scripts avec des URLs
                    script_tags = re.findall(
                        r"<script[^>]*>(.*?)</script>", html, re.DOTALL | re.IGNORECASE
                    )
                    print(f"   Scripts trouvés: {len(script_tags)}")

                    for i, script in enumerate(script_tags):
                        # Chercher des URLs dans les scripts
                        urls = re.findall(r'https?://[^\s"\'<>]+', script)
                        if urls:
                            print(f"   Script {i}: {len(urls)} URLs")
                            for url in urls[:3]:  # Premières 3
                                if "api" in url.lower() or "decklist" in url.lower():
                                    print(f"     - {url}")

                    # Sauvegarder tous les scripts pour analyse
                    with open("mtgo_scripts.txt", "w", encoding="utf-8") as f:
                        for i, script in enumerate(script_tags):
                            f.write(f"\n=== SCRIPT {i} ===\n")
                            f.write(script)
                    print(f"   Scripts sauvegardés: mtgo_scripts.txt")

                else:
                    print(f"   Error: HTTP {response.status}")

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    asyncio.run(find_mtgo_api())
