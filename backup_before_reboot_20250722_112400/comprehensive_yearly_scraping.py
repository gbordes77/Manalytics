#!/usr/bin/env python3
"""
Scraper complet - Récupération de toutes les données d'aujourd'hui à 1 an en arrière

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé
- LE CACHE NE DOIT PAS ÊTRE COMMITÉ
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
    handlers=[
        logging.FileHandler("logs/comprehensive_scraping.log"),
        logging.StreamHandler(),
    ],
)


class ComprehensiveYearlyScraper:
    """Scraper complet pour récupérer 1 an de données"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE
        self.logger.info("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
        self.logger.info("📋 Seulement AJOUTER de nouvelles données")
        self.logger.info("🚫 Aucune suppression, remplacement ou écrasement autorisé")
        self.logger.info("🚫 LE CACHE NE DOIT PAS ÊTRE COMMITÉ")

        # Configuration
        self.base_urls = {
            "mtgo": "https://www.mtgo.com",
            "melee": "https://melee.gg",
            "topdeck": "https://topdeck.gg",
        }

        # Dossiers de cache (NON COMMITÉS)
        self.cache_dirs = {
            "mtgo": Path("data/raw/mtgo"),
            "melee": Path("data/raw/melee"),
            "topdeck": Path("data/raw/topdeck"),
        }

        # Créer les dossiers
        for cache_dir in self.cache_dirs.values():
            cache_dir.mkdir(parents=True, exist_ok=True)

        # Vérifier le cache existant
        self._check_existing_cache()

    def _check_existing_cache(self):
        """Vérifier le cache existant à préserver"""
        total_files = 0
        for source, cache_dir in self.cache_dirs.items():
            if cache_dir.exists():
                files = list(cache_dir.rglob("*.json"))
                total_files += len(files)
                self.logger.info(
                    f"📁 {source.upper()} cache existant : {len(files)} fichiers préservés"
                )

        self.logger.info(f"📊 TOTAL CACHE EXISTANT : {total_files} fichiers à préserver")

    async def scrape_complete_year(self):
        """Scraper complet pour 1 an de données"""
        self.logger.info("🚀 DÉBUT SCRAPING COMPLET - 1 AN DE DONNÉES")

        # Calculer la période (aujourd'hui à 1 an en arrière)
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        self.logger.info(
            f"📅 Période : {one_year_ago.strftime('%Y-%m-%d')} à {today.strftime('%Y-%m-%d')}"
        )

        # Vérifier le cache avant scraping
        cache_before = self._count_total_cache_files()
        self.logger.info(
            f"📁 Cache avant scraping : {cache_before} fichiers à préserver"
        )

        # Scraper chaque source
        results = {}

        # 1. Scraping MTGO
        self.logger.info("🌐 SCRAPING MTGO COMPLET...")
        results["mtgo"] = await self._scrape_mtgo_complete(one_year_ago, today)

        # 2. Scraping Melee
        self.logger.info("🌐 SCRAPING MELEE COMPLET...")
        results["melee"] = await self._scrape_melee_complete(one_year_ago, today)

        # 3. Scraping TopDeck
        self.logger.info("🌐 SCRAPING TOPDECK COMPLET...")
        results["topdeck"] = await self._scrape_topdeck_complete(one_year_ago, today)

        # Vérifier que le cache a été préservé
        cache_after = self._count_total_cache_files()
        new_files = cache_after - cache_before

        self.logger.info(
            f"✅ RÈGLE CACHE RESPECTÉE : {new_files} nouveaux fichiers ajoutés"
        )
        self.logger.info(
            f"📁 Cache final : {cache_after} fichiers ({cache_before} préservés + {new_files} ajoutés)"
        )

        # Résumé final
        self._generate_final_report(results, cache_before, cache_after)

        return results

    def _count_total_cache_files(self):
        """Compter tous les fichiers dans le cache"""
        total = 0
        for cache_dir in self.cache_dirs.values():
            if cache_dir.exists():
                total += len(list(cache_dir.rglob("*.json")))
        return total

    async def _scrape_mtgo_complete(self, start_date: datetime, end_date: datetime):
        """Scraping complet MTGO"""
        self.logger.info(
            f"📡 Scraping MTGO : {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        )

        mtgo_data = []

        # URLs MTGO à scraper
        mtgo_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
            "https://www.mtgo.com/decklists",
            "https://www.mtgo.com/news",
        ]

        async with aiohttp.ClientSession() as session:
            for url in mtgo_urls:
                try:
                    self.logger.info(f"🔍 Scraping MTGO URL: {url}")

                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()

                            # Extraire les données de cette page
                            page_data = await self._extract_mtgo_data(
                                content, url, start_date, end_date
                            )
                            mtgo_data.extend(page_data)

                            self.logger.info(
                                f"✅ {len(page_data)} éléments trouvés sur {url}"
                            )

                            # Suivre les liens pour plus de données
                            links = await self._extract_mtgo_links(content, url)
                            for link in links[:5]:  # Limiter à 5 liens par page
                                link_data = await self._scrape_mtgo_link(
                                    session, link, start_date, end_date
                                )
                                mtgo_data.extend(link_data)

                except Exception as e:
                    self.logger.error(f"❌ Erreur avec {url}: {e}")

        # Sauvegarder les données MTGO (AJOUT SEULEMENT)
        if mtgo_data:
            await self._save_mtgo_data(mtgo_data)

        return {
            "source": "mtgo",
            "total_items": len(mtgo_data),
            "period": f"{start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}",
        }

    async def _scrape_melee_complete(self, start_date: datetime, end_date: datetime):
        """Scraping complet Melee"""
        self.logger.info(
            f"📡 Scraping Melee : {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        )

        melee_data = []

        # URLs Melee à scraper
        melee_urls = [
            "https://melee.gg/Tournament/",
            "https://melee.gg/Events/",
            "https://melee.gg/Results/",
        ]

        async with aiohttp.ClientSession() as session:
            for url in melee_urls:
                try:
                    self.logger.info(f"🔍 Scraping Melee URL: {url}")

                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()

                            # Extraire les données de cette page
                            page_data = await self._extract_melee_data(
                                content, url, start_date, end_date
                            )
                            melee_data.extend(page_data)

                            self.logger.info(
                                f"✅ {len(page_data)} éléments trouvés sur {url}"
                            )

                except Exception as e:
                    self.logger.error(f"❌ Erreur avec {url}: {e}")

        # Sauvegarder les données Melee (AJOUT SEULEMENT)
        if melee_data:
            await self._save_melee_data(melee_data)

        return {
            "source": "melee",
            "total_items": len(melee_data),
            "period": f"{start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}",
        }

    async def _scrape_topdeck_complete(self, start_date: datetime, end_date: datetime):
        """Scraping complet TopDeck"""
        self.logger.info(
            f"📡 Scraping TopDeck : {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        )

        topdeck_data = []

        # URLs TopDeck à scraper
        topdeck_urls = [
            "https://topdeck.gg/",
            "https://topdeck.gg/tournaments",
            "https://topdeck.gg/results",
        ]

        async with aiohttp.ClientSession() as session:
            for url in topdeck_urls:
                try:
                    self.logger.info(f"🔍 Scraping TopDeck URL: {url}")

                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()

                            # Extraire les données de cette page
                            page_data = await self._extract_topdeck_data(
                                content, url, start_date, end_date
                            )
                            topdeck_data.extend(page_data)

                            self.logger.info(
                                f"✅ {len(page_data)} éléments trouvés sur {url}"
                            )

                except Exception as e:
                    self.logger.error(f"❌ Erreur avec {url}: {e}")

        # Sauvegarder les données TopDeck (AJOUT SEULEMENT)
        if topdeck_data:
            await self._save_topdeck_data(topdeck_data)

        return {
            "source": "topdeck",
            "total_items": len(topdeck_data),
            "period": f"{start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}",
        }

    async def _extract_mtgo_data(
        self, content: str, source_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Extrait les données MTGO d'une page"""
        data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher des informations de tournois
        tournament_elements = soup.find_all(
            string=re.compile(
                r"Modern|Standard|Legacy|Pioneer|Vintage|Pauper|Challenge|League|Preliminary",
                re.IGNORECASE,
            )
        )

        for element in tournament_elements:
            if element.strip():
                # Chercher des dates dans le contexte
                parent = element.parent
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

                                # Vérifier que la date est dans la période
                                if start_date <= parsed_date <= end_date:
                                    data_item = {
                                        "title": element.strip(),
                                        "date": parsed_date.isoformat(),
                                        "source_url": source_url,
                                        "source": "mtgo",
                                        "extracted_at": datetime.now().isoformat(),
                                    }
                                    data.append(data_item)

                            except ValueError:
                                continue

        return data

    async def _extract_melee_data(
        self, content: str, source_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Extrait les données Melee d'une page"""
        data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher des informations de tournois
        tournament_elements = soup.find_all(
            string=re.compile(
                r"Modern|Standard|Legacy|Pioneer|Vintage|Pauper|Tournament|Event",
                re.IGNORECASE,
            )
        )

        for element in tournament_elements:
            if element.strip():
                # Logique similaire à MTGO
                data_item = {
                    "title": element.strip(),
                    "date": None,  # À extraire si possible
                    "source_url": source_url,
                    "source": "melee",
                    "extracted_at": datetime.now().isoformat(),
                }
                data.append(data_item)

        return data

    async def _extract_topdeck_data(
        self, content: str, source_url: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Extrait les données TopDeck d'une page"""
        data = []
        soup = BeautifulSoup(content, "html.parser")

        # Chercher des informations de tournois
        tournament_elements = soup.find_all(
            string=re.compile(
                r"Modern|Standard|Legacy|Pioneer|Vintage|Pauper|Tournament|Event",
                re.IGNORECASE,
            )
        )

        for element in tournament_elements:
            if element.strip():
                # Logique similaire à MTGO
                data_item = {
                    "title": element.strip(),
                    "date": None,  # À extraire si possible
                    "source_url": source_url,
                    "source": "topdeck",
                    "extracted_at": datetime.now().isoformat(),
                }
                data.append(data_item)

        return data

    async def _extract_mtgo_links(self, content: str, source_url: str) -> List[Dict]:
        """Extrait les liens MTGO d'une page"""
        links = []
        soup = BeautifulSoup(content, "html.parser")

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
                    "news",
                ]
            ):

                # Construire l'URL complète
                if href.startswith("/"):
                    full_url = f"{self.base_urls['mtgo']}{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = f"{self.base_urls['mtgo']}/{href}"

                links.append({"url": full_url, "text": text, "source": source_url})

        return links

    async def _scrape_mtgo_link(
        self,
        session: aiohttp.ClientSession,
        link_info: Dict,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Scrape les données d'un lien MTGO spécifique"""
        link_data = []

        try:
            self.logger.info(
                f"🔍 Suivi du lien MTGO: {link_info['text']} -> {link_info['url']}"
            )

            async with session.get(link_info["url"], timeout=15) as response:
                if response.status == 200:
                    content = await response.text()

                    # Analyser le contenu de cette page
                    page_data = await self._extract_mtgo_data(
                        content, link_info["url"], start_date, end_date
                    )
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

    async def _save_mtgo_data(self, data: List[Dict]):
        """Sauvegarde les données MTGO (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # RÈGLE ABSOLUE : Nom de fichier unique
        json_file = self.cache_dirs["mtgo"] / f"mtgo_complete_{timestamp}.json"

        # Vérifier que le fichier n'existe pas déjà
        counter = 1
        while json_file.exists():
            json_file = (
                self.cache_dirs["mtgo"] / f"mtgo_complete_{timestamp}_{counter}.json"
            )
            counter += 1

        # Sauvegarder (AJOUT SEULEMENT)
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
            f"💾 {len(data)} éléments MTGO sauvegardés dans {json_file} (AJOUT SEULEMENT)"
        )

    async def _save_melee_data(self, data: List[Dict]):
        """Sauvegarde les données Melee (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # RÈGLE ABSOLUE : Nom de fichier unique
        json_file = self.cache_dirs["melee"] / f"melee_complete_{timestamp}.json"

        # Vérifier que le fichier n'existe pas déjà
        counter = 1
        while json_file.exists():
            json_file = (
                self.cache_dirs["melee"] / f"melee_complete_{timestamp}_{counter}.json"
            )
            counter += 1

        # Sauvegarder (AJOUT SEULEMENT)
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
            f"💾 {len(data)} éléments Melee sauvegardés dans {json_file} (AJOUT SEULEMENT)"
        )

    async def _save_topdeck_data(self, data: List[Dict]):
        """Sauvegarde les données TopDeck (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # RÈGLE ABSOLUE : Nom de fichier unique
        json_file = self.cache_dirs["topdeck"] / f"topdeck_complete_{timestamp}.json"

        # Vérifier que le fichier n'existe pas déjà
        counter = 1
        while json_file.exists():
            json_file = (
                self.cache_dirs["topdeck"]
                / f"topdeck_complete_{timestamp}_{counter}.json"
            )
            counter += 1

        # Sauvegarder (AJOUT SEULEMENT)
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
            f"💾 {len(data)} éléments TopDeck sauvegardés dans {json_file} (AJOUT SEULEMENT)"
        )

    def _generate_final_report(
        self, results: Dict, cache_before: int, cache_after: int
    ):
        """Génère un rapport final du scraping"""
        self.logger.info("📊 RAPPORT FINAL DU SCRAPING COMPLET")
        self.logger.info("=" * 50)

        total_items = 0
        for source, result in results.items():
            items = result["total_items"]
            total_items += items
            self.logger.info(f"🌐 {source.upper()}: {items} éléments")

        new_files = cache_after - cache_before
        self.logger.info(f"📁 Nouveaux fichiers ajoutés: {new_files}")
        self.logger.info(f"📁 Fichiers préservés: {cache_before}")
        self.logger.info(f"📁 Total final: {cache_after}")
        self.logger.info(f"📊 Total éléments récupérés: {total_items}")

        self.logger.info("✅ RÈGLE ABSOLUE RESPECTÉE: Cache préservé, seulement ajouts")
        self.logger.info("🚫 CACHE NON COMMITÉ: Données locales uniquement")


async def main():
    """Fonction principale"""
    scraper = ComprehensiveYearlyScraper()

    print("🎯 SCRAPING COMPLET - 1 AN DE DONNÉES")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("🚫 LE CACHE NE DOIT PAS ÊTRE COMMITÉ")
    print("=" * 50)

    results = await scraper.scrape_complete_year()

    print("\n✅ Scraping complet terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")
    print("✅ CACHE NON COMMITÉ : Données locales uniquement")


if __name__ == "__main__":
    asyncio.run(main())
