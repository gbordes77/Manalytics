#!/usr/bin/env python3
"""
Scraper MTGO avancé - Récupération de données sur plusieurs années
Capable de scraper rétroactivement et de remplir le cache jusqu'à aujourd'hui
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/mtgo_scraping.log"), logging.StreamHandler()],
)


class AdvancedMTGOScraper:
    """Scraper MTGO avancé avec capacités rétroactives"""

    def __init__(self):
        self.base_url = "https://www.mtgo.com"
        self.cache_dir = Path("data/raw/mtgo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # URLs qui fonctionnent
        self.working_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
            "https://www.mtgo.com/decklists",
        ]

        # Sources alternatives
        self.alternative_sources = [
            "https://magic.wizards.com/en/mtgo",
            "https://www.mtgtop8.com/",
            "https://www.mtggoldfish.com/",
        ]

    async def scrape_historical_data(self, years_back: int = 2):
        """Scrape les données historiques sur plusieurs années"""
        self.logger.info(f"🚀 Début du scraping historique sur {years_back} années")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years_back)

        # Créer les dossiers par année/mois
        current_date = start_date
        while current_date <= end_date:
            year_month_dir = (
                self.cache_dir / str(current_date.year) / f"{current_date.month:02d}"
            )
            year_month_dir.mkdir(parents=True, exist_ok=True)
            current_date += timedelta(days=32)  # Passer au mois suivant
            current_date = current_date.replace(day=1)

        # Scraping par période
        await self.scrape_by_periods(start_date, end_date)

    async def scrape_by_periods(self, start_date: datetime, end_date: datetime):
        """Scrape les données par périodes de 30 jours"""
        current_start = start_date

        async with aiohttp.ClientSession() as session:
            while current_start < end_date:
                current_end = min(current_start + timedelta(days=30), end_date)

                period_str = f"{current_start.strftime('%Y-%m-%d')}_to_{current_end.strftime('%Y-%m-%d')}"
                self.logger.info(f"📅 Scraping période: {period_str}")

                # Scraper toutes les sources pour cette période
                all_data = []

                # 1. Scraper MTGO principal
                mtgo_data = await self.scrape_mtgo_period(
                    session, current_start, current_end
                )
                all_data.extend(mtgo_data)

                # 2. Scraper sources alternatives
                alt_data = await self.scrape_alternative_sources_period(
                    session, current_start, current_end
                )
                all_data.extend(alt_data)

                # 3. Sauvegarder les données de la période
                if all_data:
                    await self.save_period_data(all_data, current_start, current_end)

                current_start = current_end

    async def scrape_mtgo_period(
        self, session: aiohttp.ClientSession, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Scrape les données MTGO pour une période donnée"""
        period_data = []

        for url in self.working_urls:
            try:
                self.logger.info(f"📡 Scraping MTGO: {url}")
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Extraire les données de la période
                        extracted_data = await self.extract_period_data(
                            content, url, start_date, end_date
                        )
                        period_data.extend(extracted_data)

                        self.logger.info(
                            f"✅ {len(extracted_data)} éléments trouvés sur {url}"
                        )
                    else:
                        self.logger.warning(f"❌ Erreur {response.status} pour {url}")

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        return period_data

    async def extract_period_data(
        self, content: str, source_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Extrait les données d'une période spécifique"""
        extracted_data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher les dates dans le contenu
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"(\d{2}/\d{2}/\d{4})",  # MM/DD/YYYY
            r"(\d{2}-\d{2}-\d{4})",  # MM-DD-YYYY
        ]

        # Chercher les tournois et decklists
        tournament_elements = soup.find_all(
            ["a", "div", "span"],
            href=re.compile(r"tournament|decklist|result|challenge|league"),
        )

        for element in tournament_elements:
            element_text = element.get_text(strip=True)
            href = element.get("href", "")

            # Vérifier si l'élément contient une date dans la période
            for pattern in date_patterns:
                date_matches = re.findall(pattern, element_text)
                for date_match in date_matches:
                    try:
                        if "/" in date_match:
                            parsed_date = datetime.strptime(date_match, "%m/%d/%Y")
                        elif "-" in date_match and len(date_match.split("-")[0]) == 2:
                            parsed_date = datetime.strptime(date_match, "%m-%d-%Y")
                        else:
                            parsed_date = datetime.strptime(date_match, "%Y-%m-%d")

                        if start_date <= parsed_date <= end_date:
                            data_item = {
                                "title": element_text,
                                "url": href
                                if href.startswith("http")
                                else f"{self.base_url}{href}",
                                "date": parsed_date.isoformat(),
                                "source": source_url,
                                "extracted_at": datetime.now().isoformat(),
                            }
                            extracted_data.append(data_item)

                    except ValueError:
                        continue  # Date non parsable

        return extracted_data

    async def scrape_alternative_sources_period(
        self, session: aiohttp.ClientSession, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Scrape les sources alternatives pour une période"""
        alt_data = []

        for url in self.alternative_sources:
            try:
                self.logger.info(f"📡 Scraping source alternative: {url}")
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Extraire les données MTGO des sources alternatives
                        extracted = await self.extract_mtgo_from_alternative(
                            content, url, start_date, end_date
                        )
                        alt_data.extend(extracted)

                        self.logger.info(
                            f"✅ {len(extracted)} éléments MTGO trouvés sur {url}"
                        )
                    else:
                        self.logger.warning(f"❌ Erreur {response.status} pour {url}")

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec source alternative {url}: {e}")

        return alt_data

    async def extract_mtgo_from_alternative(
        self, content: str, source_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Extrait les données MTGO des sources alternatives"""
        mtgo_data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher les références MTGO
        mtgo_references = soup.find_all(
            text=re.compile(r"MTGO|Magic Online|mtgo\.com", re.IGNORECASE)
        )

        for reference in mtgo_references:
            parent = reference.parent
            if parent:
                # Chercher des dates associées
                date_patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{2}/\d{2}/\d{4})"]

                for pattern in date_patterns:
                    date_matches = re.findall(pattern, str(parent))
                    for date_match in date_matches:
                        try:
                            if "/" in date_match:
                                parsed_date = datetime.strptime(date_match, "%m/%d/%Y")
                            else:
                                parsed_date = datetime.strptime(date_match, "%Y-%m-%d")

                            if start_date <= parsed_date <= end_date:
                                data_item = {
                                    "title": reference.strip(),
                                    "source": source_url,
                                    "date": parsed_date.isoformat(),
                                    "extracted_at": datetime.now().isoformat(),
                                }
                                mtgo_data.append(data_item)

                        except ValueError:
                            continue

        return mtgo_data

    async def save_period_data(
        self, data: List[Dict], start_date: datetime, end_date: datetime
    ):
        """Sauvegarde les données d'une période"""
        if not data:
            return

        # Organiser par année/mois
        for item in data:
            try:
                item_date = datetime.fromisoformat(item["date"])
                year_month_dir = (
                    self.cache_dir / str(item_date.year) / f"{item_date.month:02d}"
                )
                year_month_dir.mkdir(parents=True, exist_ok=True)

                # Nom de fichier unique
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mtgo_data_{item_date.strftime('%Y%m%d')}_{timestamp}.json"

                with open(year_month_dir / filename, "w", encoding="utf-8") as f:
                    json.dump(item, f, indent=2)

            except Exception as e:
                self.logger.error(f"⚠️ Erreur sauvegarde item: {e}")

        self.logger.info(
            f"💾 {len(data)} éléments sauvegardés pour la période {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        )

    async def verify_cache_completeness(self):
        """Vérifie que le cache est bien rempli jusqu'à aujourd'hui"""
        self.logger.info("🔍 Vérification de la complétude du cache")

        today = datetime.now()
        cache_stats = {
            "total_files": 0,
            "years_covered": set(),
            "months_covered": set(),
            "latest_date": None,
            "missing_periods": [],
        }

        # Analyser le cache existant
        for year_dir in self.cache_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = int(year_dir.name)
                cache_stats["years_covered"].add(year)

                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir() and month_dir.name.isdigit():
                        month = int(month_dir.name)
                        cache_stats["months_covered"].add(f"{year}-{month:02d}")

                        # Compter les fichiers
                        json_files = list(month_dir.glob("*.json"))
                        cache_stats["total_files"] += len(json_files)

                        # Trouver la date la plus récente
                        for json_file in json_files:
                            try:
                                with open(json_file, "r") as f:
                                    data = json.load(f)
                                    if "date" in data:
                                        file_date = datetime.fromisoformat(data["date"])
                                        if (
                                            not cache_stats["latest_date"]
                                            or file_date > cache_stats["latest_date"]
                                        ):
                                            cache_stats["latest_date"] = file_date
                            except:
                                continue

        # Identifier les périodes manquantes
        current_date = datetime.now() - timedelta(days=365 * 2)  # 2 ans en arrière
        while current_date <= today:
            year_month = f"{current_date.year}-{current_date.month:02d}"
            if year_month not in cache_stats["months_covered"]:
                cache_stats["missing_periods"].append(year_month)
            current_date += timedelta(days=32)
            current_date = current_date.replace(day=1)

        # Sauvegarder le rapport
        report_file = self.cache_dir / "cache_completeness_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "generated_at": datetime.now().isoformat(),
                    "total_files": cache_stats["total_files"],
                    "years_covered": sorted(list(cache_stats["years_covered"])),
                    "months_covered": sorted(list(cache_stats["months_covered"])),
                    "latest_date": cache_stats["latest_date"].isoformat()
                    if cache_stats["latest_date"]
                    else None,
                    "missing_periods": cache_stats["missing_periods"],
                    "coverage_percentage": len(cache_stats["months_covered"])
                    / (24 * 2)
                    * 100,  # 24 mois sur 2 ans
                },
                f,
                indent=2,
            )

        self.logger.info(f"📊 Rapport de complétude sauvegardé: {report_file}")
        self.logger.info(
            f"📈 Couverture: {len(cache_stats['months_covered'])} mois sur {24 * 2} attendus"
        )
        self.logger.info(f"📅 Dernière date: {cache_stats['latest_date']}")

        return cache_stats


async def main():
    """Fonction principale"""
    scraper = AdvancedMTGOScraper()

    print("🎯 SCRAPER MTGO AVANCÉ - RÉCUPÉRATION HISTORIQUE")
    print("=" * 60)

    # 1. Scraping historique sur 2 ans
    await scraper.scrape_historical_data(years_back=2)

    # 2. Vérification de la complétude du cache
    cache_stats = await scraper.verify_cache_completeness()

    print("\n✅ Scraping historique terminé!")
    print(f"📁 Cache vérifié: {cache_stats['total_files']} fichiers")
    print(f"📅 Couverture: {len(cache_stats['months_covered'])} mois")
    print(f"🔍 Rapport détaillé: data/raw/mtgo/cache_completeness_report.json")


if __name__ == "__main__":
    asyncio.run(main())
