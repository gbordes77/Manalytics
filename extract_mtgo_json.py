#!/usr/bin/env python3
"""
Extraire et analyser les données JSON des decks MTGO
"""

import asyncio
import json
import re

import aiohttp


async def extract_mtgo_json():
    """Extraire les données JSON des decks"""

    url = "https://www.mtgo.com/decklist/standard-challenge-32-2024-06-1512647468"

    print(f"🔍 Extraction des données JSON MTGO:")
    print(f"   URL: {url}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={"User-Agent": "Manalytics-Fbettega/1.0"},
    ) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()

                    # Chercher le pattern decklist JSON
                    pattern = r"decklist[^=]*=\s*(\{[^;]+\});"
                    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

                    if matches:
                        json_str = matches[0]
                        print(f"   JSON trouvé: {len(json_str)} caractères")

                        try:
                            data = json.loads(json_str)
                            print(f"   JSON parsé avec succès!")
                            print(f"   Clés principales: {list(data.keys())}")

                            # Analyser la structure
                            if "event_id" in data:
                                print(f"   Event ID: {data['event_id']}")
                            if "description" in data:
                                print(f"   Description: {data['description'][:100]}...")
                            if "format" in data:
                                print(f"   Format: {data['format']}")
                            if "type" in data:
                                print(f"   Type: {data['type']}")

                            # Chercher les decks
                            deck_keys = [
                                key for key in data.keys() if "deck" in key.lower()
                            ]
                            print(f"   Clés contenant 'deck': {deck_keys}")

                            # Chercher les standings/results
                            result_keys = [
                                key
                                for key in data.keys()
                                if any(
                                    word in key.lower()
                                    for word in ["result", "standing", "player", "rank"]
                                )
                            ]
                            print(f"   Clés de résultats: {result_keys}")

                            # Analyser chaque clé importante
                            for key in data.keys():
                                value = data[key]
                                if isinstance(value, list) and len(value) > 0:
                                    print(f"   {key}: liste de {len(value)} éléments")
                                    if isinstance(value[0], dict):
                                        sample_keys = list(value[0].keys())[:5]
                                        print(f"     Premier élément: {sample_keys}")
                                elif isinstance(value, dict) and len(value) > 0:
                                    print(
                                        f"   {key}: dictionnaire avec {len(value)} clés"
                                    )
                                    sample_keys = list(value.keys())[:5]
                                    print(f"     Clés: {sample_keys}")

                            # Sauvegarder le JSON pour analyse
                            with open(
                                "mtgo_decklist_data.json", "w", encoding="utf-8"
                            ) as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"   Données sauvegardées: mtgo_decklist_data.json")

                        except json.JSONDecodeError as e:
                            print(f"   Erreur de parsing JSON: {e}")
                            # Sauvegarder le JSON brut pour debug
                            with open("mtgo_raw_json.txt", "w", encoding="utf-8") as f:
                                f.write(json_str)
                            print(f"   JSON brut sauvegardé: mtgo_raw_json.txt")
                    else:
                        print(f"   Aucun JSON decklist trouvé")

                else:
                    print(f"   Error: HTTP {response.status}")

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    asyncio.run(extract_mtgo_json())
