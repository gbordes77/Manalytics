#!/usr/bin/env python3
"""
Scraper MTGO corrigé - Suit les liens et scrape les vraies données

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FixedMTGOScraper:
    """Scraper MTGO qui suit les liens et trouve les vraies données"""

    def __init__(self):
        self.base_url = "https://www.mtgo.com"
        self.cache_dir = Path("data/raw/mtgo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE
        self.logger.info("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
        self.logger.info("📋 Seulement AJOUTER de nouvelles données")
        self.logger.info("🚫 Aucune suppression, remplacement ou écrasement autorisé")
        self.logger.info("🚫 LE CACHE NE DOIT PAS ÊTRE COMMITÉ")

    async def scrape_mtgo_data(self):
        """Scrape les données MTGO en suivant les liens"""
        self.logger.info("🚀 Début du scraping MTGO corrigé")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        # URLs principales
        main_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
        ]

        all_data = []

        async with aiohttp.ClientSession() as session:
            for main_url in main_urls:
                self.logger.info(f"📡 Scraping page principale: {main_url}")

                try:
                    async with session.get(main_url, timeout=15) as response:
                        if response.status == 200:
                            content = await response.text()

                            # 1. Extraire les liens de cette page
                            links = await self.extract_links(content, main_url)
                            self.logger.info(
                                f"🔗 Trouvé {len(links)} liens sur {main_url}"
                            )

                            # 2. Suivre chaque lien et scraper les données
                            for link in links:
                                link_data = await self.scrape_link_data(session, link)
                                if link_data:
                                    all_data.extend(link_data)

                except Exception as e:
                    self.logger.error(f"⚠️ Erreur avec {main_url}: {e}")

        # Sauvegarder toutes les données (AJOUT SEULEMENT)
        if all_data:
            await self.save_all_data(all_data)
        else:
            self.logger.warning("⚠️ Aucune donnée trouvée")

        # Vérifier le cache APRÈS sauvegarde
        final_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(
            f"📁 Cache final : {len(final_files)} fichiers (préserver + ajout)"
        )
        self.logger.info(
            f"✅ RÈGLE RESPECTÉE : {len(final_files) - len(existing_files)} nouveaux fichiers ajoutés"
        )

    async def extract_links(self, content: str, source_url: str) -> list:
        """Extrait tous les liens pertinents d'une page"""
        links = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher tous les liens
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Filtrer les liens pertinents
            if any(
                keyword in href.lower() or keyword in text.lower()
                for keyword in [
                    "decklist",
                    "tournament",
                    "result",
                    "challenge",
                    "league",
                ]
            ):

                # Construire l'URL complète
                if href.startswith("/"):
                    full_url = f"{self.base_url}{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = f"{self.base_url}/{href}"

                links.append({"url": full_url, "text": text, "source": source_url})

        return links

    async def scrape_link_data(
        self, session: aiohttp.ClientSession, link_info: dict
    ) -> list:
        """Scrape les données d'un lien spécifique"""
        link_data = []

        try:
            self.logger.info(
                f"🔍 Suivi du lien: {link_info['text']} -> {link_info['url']}"
            )

            async with session.get(link_info["url"], timeout=15) as response:
                if response.status == 200:
                    content = await response.text()

                    # Analyser le contenu de cette page
                    page_data = await self.analyze_page_content(content, link_info)
                    link_data.extend(page_data)

                    self.logger.info(
                        f"✅ {len(page_data)} éléments trouvés sur {link_info['url']}"
                    )
                else:
                    self.logger.warning(
                        f"❌ Erreur {response.status} pour {link_info['url']}"
                    )

        except Exception as e:
            self.logger.error(f"⚠️ Erreur avec le lien {link_info['url']}: {e}")

        return link_data

    async def analyze_page_content(self, content: str, link_info: dict) -> list:
        """Analyse le contenu d'une page pour extraire les données"""
        page_data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher des informations de tournois
        tournament_info = soup.find_all(
            string=re.compile(
                r"Modern|Standard|Legacy|Pioneer|Vintage|Pauper|Challenge|League",
                re.IGNORECASE,
            )
        )

        for info in tournament_info:
            if info.strip():
                # Chercher des dates dans le contexte
                parent = info.parent
                if parent:
                    # Chercher des dates
                    date_patterns = [
                        r"(\d{4}-\d{2}-\d{2})",
                        r"(\d{2}/\d{2}/\d{4})",
                        r"(\d{2}-\d{2}-\d{4})",
                    ]

                    for pattern in date_patterns:
                        date_matches = re.findall(pattern, str(parent))
                        for date_match in date_matches:
                            try:
                                if "/" in date_match:
                                    parsed_date = datetime.strptime(
                                        date_match, "%m/%d/%Y"
                                    )
                                elif (
                                    "-" in date_match
                                    and len(date_match.split("-")[0]) == 2
                                ):
                                    parsed_date = datetime.strptime(
                                        date_match, "%m-%d-%Y"
                                    )
                                else:
                                    parsed_date = datetime.strptime(
                                        date_match, "%Y-%m-%d"
                                    )

                                data_item = {
                                    "title": info.strip(),
                                    "date": parsed_date.isoformat(),
                                    "source_url": link_info["url"],
                                    "source_text": link_info["text"],
                                    "extracted_at": datetime.now().isoformat(),
                                }
                                page_data.append(data_item)

                            except ValueError:
                                continue

        # Si pas de dates trouvées, sauvegarder quand même les informations
        if not page_data and tournament_info:
            for info in tournament_info[:5]:  # Limiter à 5 éléments
                if info.strip():
                    data_item = {
                        "title": info.strip(),
                        "date": None,
                        "source_url": link_info["url"],
                        "source_text": link_info["text"],
                        "extracted_at": datetime.now().isoformat(),
                    }
                    page_data.append(data_item)

        return page_data

    async def save_all_data(self, data: list):
        """Sauvegarde toutes les données trouvées (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_complete_data_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = (
                self.cache_dir / f"mtgo_complete_data_{timestamp}_{counter}.json"
            )
            counter += 1

        # Sauvegarder en JSON (AJOUT SEULEMENT)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "total_items": len(data),
                    "data": data,
                    "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                    "git_rule": "CACHE_NOT_COMMITTED",
                },
                f,
                indent=2,
            )

        self.logger.info(
            f"💾 {len(data)} éléments sauvegardés dans {json_file} (AJOUT SEULEMENT)"
        )

        # Organiser par date si disponible (AJOUT SEULEMENT)
        dated_data = [item for item in data if item.get("date")]
        if dated_data:
            await self.organize_by_date(dated_data)

    async def organize_by_date(self, dated_data: list):
        """Organise les données par date (AJOUT SEULEMENT)"""
        for item in dated_data:
            try:
                item_date = datetime.fromisoformat(item["date"])
                year_month_dir = (
                    self.cache_dir / str(item_date.year) / f"{item_date.month:02d}"
                )
                year_month_dir.mkdir(parents=True, exist_ok=True)

                # RÈGLE ABSOLUE : Nom de fichier unique pour éviter l'écrasement
                timestamp = datetime.now().strftime("%H%M%S_%f")[
                    :-3
                ]  # Microsecondes pour unicité
                filename = f"mtgo_item_{item_date.strftime('%Y%m%d')}_{timestamp}.json"

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_item_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
                    file_path = year_month_dir / filename
                    counter += 1

                # Sauvegarder (AJOUT SEULEMENT)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            **item,
                            "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                            "git_rule": "CACHE_NOT_COMMITTED",
                        },
                        f,
                        indent=2,
                    )

            except Exception as e:
                self.logger.error(f"⚠️ Erreur organisation par date: {e}")


async def main():
    """Fonction principale"""
    scraper = FixedMTGOScraper()

    print("🎯 SCRAPER MTGO CORRIGÉ - SUIVI DES LIENS")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 50)

    await scraper.scrape_mtgo_data()

    print("\n✅ Scraping terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    asyncio.run(main())
