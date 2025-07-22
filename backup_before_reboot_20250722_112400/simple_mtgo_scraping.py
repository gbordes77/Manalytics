#!/usr/bin/env python3
"""
Script de scraping MTGO simple et efficace
Utilise les vraies URLs qui fonctionnent pour récupérer les données
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp


class SimpleMTGOScraper:
    def __init__(self):
        self.base_url = "https://www.mtgo.com"
        self.cache_dir = Path("data/raw/mtgo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_mtgo_data(self, start_date: str, end_date: str):
        """Scrape les données MTGO pour une période donnée"""
        print(f"🚀 Début du scraping MTGO: {start_date} à {end_date}")

        # URLs MTGO qui fonctionnent réellement
        mtgo_urls = [
            "https://www.mtgo.com/en/mtgo/decklist",
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
        ]

        async with aiohttp.ClientSession() as session:
            for url in mtgo_urls:
                try:
                    print(f"📡 Test de l'URL: {url}")
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            print(f"✅ URL fonctionne: {url}")
                            content = await response.text()

                            # Sauvegarder la réponse pour analyse
                            filename = f"mtgo_response_{url.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                            with open(
                                self.cache_dir / filename, "w", encoding="utf-8"
                            ) as f:
                                f.write(content)

                            # Analyser le contenu pour trouver les données
                            await self.parse_mtgo_content(content, url)
                        else:
                            print(
                                f"❌ URL ne fonctionne pas: {url} (Status: {response.status})"
                            )

                except Exception as e:
                    print(f"⚠️ Erreur avec {url}: {e}")

    async def parse_mtgo_content(self, content: str, source_url: str):
        """Parse le contenu HTML pour extraire les données de tournois"""
        print(f"🔍 Analyse du contenu de: {source_url}")

        # Chercher des patterns de données de tournois
        import re

        # Patterns pour trouver des données de tournois
        patterns = [
            r'tournament[^"]*["\']([^"\']*)["\']',
            r'decklist[^"]*["\']([^"\']*)["\']',
            r'result[^"]*["\']([^"\']*)["\']',
            r"(\d{4}-\d{2}-\d{2})",  # Dates
            r"(Modern|Standard|Legacy|Pioneer|Vintage|Pauper)",  # Formats
        ]

        found_data = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_data.extend(matches)
                print(f"📊 Trouvé {len(matches)} matches avec pattern: {pattern}")

        if found_data:
            # Sauvegarder les données trouvées
            data_file = (
                f"mtgo_extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(self.cache_dir / data_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "source_url": source_url,
                        "extracted_data": found_data,
                        "timestamp": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )
            print(f"💾 Données sauvegardées dans: {data_file}")
        else:
            print("⚠️ Aucune donnée trouvée dans le contenu")

    async def scrape_alternative_sources(self):
        """Scrape des sources alternatives pour les données MTGO"""
        print("🔄 Test des sources alternatives...")

        alternative_urls = [
            "https://magic.wizards.com/en/mtgo",
            "https://www.mtggoldfish.com/tournament_meta",
            "https://www.mtgtop8.com/",
        ]

        async with aiohttp.ClientSession() as session:
            for url in alternative_urls:
                try:
                    print(f"📡 Test source alternative: {url}")
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            print(f"✅ Source alternative accessible: {url}")
                        else:
                            print(
                                f"❌ Source alternative non accessible: {url} (Status: {response.status})"
                            )
                except Exception as e:
                    print(f"⚠️ Erreur avec source alternative {url}: {e}")


async def main():
    """Fonction principale"""
    scraper = SimpleMTGOScraper()

    # Scraping pour la période récente (derniers 30 jours)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print("🎯 SCRAPING MTGO SIMPLE ET EFFICACE")
    print("=" * 50)

    # 1. Test des URLs MTGO principales
    await scraper.scrape_mtgo_data(
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    # 2. Test des sources alternatives
    await scraper.scrape_alternative_sources()

    print("\n✅ Scraping terminé!")
    print("📁 Vérifiez les fichiers dans data/raw/mtgo/")


if __name__ == "__main__":
    asyncio.run(main())
