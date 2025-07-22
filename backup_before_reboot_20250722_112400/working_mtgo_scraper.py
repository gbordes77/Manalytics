#!/usr/bin/env python3
"""
Scraper MTGO qui fonctionne réellement
Utilise les URLs qui marchent pour récupérer les données de tournois
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup


class WorkingMTGOScraper:
    def __init__(self):
        self.base_url = "https://www.mtgo.com"
        self.cache_dir = Path("data/raw/mtgo/2025")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_recent_tournaments(self, days_back: int = 30):
        """Scrape les tournois récents MTGO"""
        print(f"🚀 Scraping MTGO pour les {days_back} derniers jours")

        # URLs qui fonctionnent
        working_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
        ]

        all_tournaments = []

        async with aiohttp.ClientSession() as session:
            for url in working_urls:
                try:
                    print(f"📡 Scraping: {url}")
                    async with session.get(url, timeout=15) as response:
                        if response.status == 200:
                            content = await response.text()
                            tournaments = await self.extract_tournaments_from_page(
                                content, url
                            )
                            all_tournaments.extend(tournaments)
                            print(f"✅ Trouvé {len(tournaments)} tournois sur {url}")
                        else:
                            print(f"❌ Erreur {response.status} pour {url}")

                except Exception as e:
                    print(f"⚠️ Erreur avec {url}: {e}")

        # Sauvegarder tous les tournois trouvés
        if all_tournaments:
            await self.save_tournaments(all_tournaments)
        else:
            print("⚠️ Aucun tournoi trouvé")

    async def extract_tournaments_from_page(
        self, content: str, source_url: str
    ) -> list:
        """Extrait les tournois d'une page MTGO"""
        tournaments = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher les liens vers les decklists
        decklist_links = soup.find_all(
            "a", href=re.compile(r"decklist|tournament|result")
        )

        for link in decklist_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            if href and ("decklist" in href.lower() or "tournament" in href.lower()):
                # Construire l'URL complète
                if href.startswith("/"):
                    full_url = f"{self.base_url}{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = f"{self.base_url}/{href}"

                tournament = {
                    "url": full_url,
                    "title": text,
                    "source": source_url,
                    "found_at": datetime.now().isoformat(),
                }
                tournaments.append(tournament)

        # Chercher aussi les informations de format
        format_info = soup.find_all(
            text=re.compile(r"Modern|Standard|Legacy|Pioneer|Vintage|Pauper")
        )
        for format_text in format_info:
            if format_text.strip():
                tournament = {
                    "format": format_text.strip(),
                    "source": source_url,
                    "found_at": datetime.now().isoformat(),
                }
                tournaments.append(tournament)

        return tournaments

    async def save_tournaments(self, tournaments: list):
        """Sauvegarde les tournois trouvés"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sauvegarder en JSON
        json_file = self.cache_dir / f"mtgo_tournaments_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "total_tournaments": len(tournaments),
                    "tournaments": tournaments,
                },
                f,
                indent=2,
            )

        print(f"💾 {len(tournaments)} tournois sauvegardés dans {json_file}")

    async def scrape_magic_wizards(self):
        """Scrape aussi magic.wizards.com pour les données MTGO"""
        print("🔄 Scraping magic.wizards.com...")

        url = "https://magic.wizards.com/en/mtgo"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, "html.parser")

                        # Chercher les articles/annonces MTGO
                        articles = soup.find_all("article") + soup.find_all(
                            "div", class_=re.compile(r"article|news")
                        )

                        mtgo_data = []
                        for article in articles:
                            title_elem = (
                                article.find("h1")
                                or article.find("h2")
                                or article.find("h3")
                            )
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                if (
                                    "mtgo" in title.lower()
                                    or "magic online" in title.lower()
                                ):
                                    mtgo_data.append(
                                        {
                                            "title": title,
                                            "source": url,
                                            "found_at": datetime.now().isoformat(),
                                        }
                                    )

                        if mtgo_data:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            json_file = (
                                self.cache_dir / f"wizards_mtgo_{timestamp}.json"
                            )
                            with open(json_file, "w", encoding="utf-8") as f:
                                json.dump(
                                    {
                                        "scraped_at": datetime.now().isoformat(),
                                        "mtgo_articles": mtgo_data,
                                    },
                                    f,
                                    indent=2,
                                )
                            print(f"💾 {len(mtgo_data)} articles MTGO sauvegardés")
                        else:
                            print("⚠️ Aucun article MTGO trouvé sur Wizards")

            except Exception as e:
                print(f"⚠️ Erreur scraping Wizards: {e}")


async def main():
    """Fonction principale"""
    scraper = WorkingMTGOScraper()

    print("🎯 SCRAPING MTGO QUI FONCTIONNE")
    print("=" * 50)

    # 1. Scraper les tournois récents
    await scraper.scrape_recent_tournaments(days_back=30)

    # 2. Scraper Wizards.com
    await scraper.scrape_magic_wizards()

    print("\n✅ Scraping terminé!")
    print("📁 Vérifiez les fichiers dans data/raw/mtgo/2025/")


if __name__ == "__main__":
    asyncio.run(main())
