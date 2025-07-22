#!/usr/bin/env python3
"""
Script de scraping complet pour Manalytics
Récupère 2 ans de données réelles depuis MTGO.com et Melee.gg
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/comprehensive_scraping.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ComprehensiveScraper:
    """Scraper complet pour récupérer 2 ans de données MTG"""

    def __init__(self):
        self.session = None
        self.cache_dir = Path("data/raw")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # URLs des APIs
        self.mtgo_api = "https://www.mtgo.com/api"
        self.melee_api = "https://api.melee.gg"

        # Headers pour éviter le blocage
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def __aenter__(self):
        """Gestionnaire de contexte async"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture de la session"""
        if self.session:
            await self.session.close()

    async def scrape_mtgo_data(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Scrape les données MTGO pour une période donnée"""
        logger.info(
            f"🌐 Scraping MTGO data from {start_date.date()} to {end_date.date()}"
        )

        tournaments = []
        current_date = start_date

        while current_date <= end_date:
            try:
                # Scraper les tournois du jour
                daily_tournaments = await self._scrape_mtgo_daily(current_date)
                tournaments.extend(daily_tournaments)

                logger.info(
                    f"✅ MTGO {current_date.date()}: {len(daily_tournaments)} tournaments"
                )

                # Pause pour éviter le rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ Error scraping MTGO {current_date.date()}: {e}")

            current_date += timedelta(days=1)

        logger.info(f"🎯 MTGO scraping complete: {len(tournaments)} total tournaments")
        return tournaments

    async def _scrape_mtgo_daily(self, date: datetime) -> List[Dict]:
        """Scrape les tournois MTGO d'une journée spécifique"""
        tournaments = []

        try:
            # URL des decklists MTGO pour la date
            date_str = date.strftime("%Y-%m-%d")
            url = f"https://www.mtgo.com/en/mtgo/decklist"

            params = {"date": date_str, "format": "all"}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    tournaments = await self._parse_mtgo_html(html, date)
                else:
                    logger.warning(f"MTGO {date_str}: HTTP {response.status}")

        except Exception as e:
            logger.error(f"Error scraping MTGO {date}: {e}")

        return tournaments

    async def _parse_mtgo_html(self, html: str, date: datetime) -> List[Dict]:
        """Parse le HTML MTGO pour extraire les tournois"""
        from bs4 import BeautifulSoup

        tournaments = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Chercher les liens vers les decklists
            decklist_links = soup.find_all("a", href=lambda x: x and "/decklist/" in x)

            for link in decklist_links:
                try:
                    href = link.get("href")
                    tournament_data = await self._fetch_mtgo_tournament(href, date)
                    if tournament_data:
                        tournaments.append(tournament_data)
                except Exception as e:
                    logger.error(f"Error parsing MTGO link {href}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing MTGO HTML: {e}")

        return tournaments

    async def _fetch_mtgo_tournament(self, href: str, date: datetime) -> Optional[Dict]:
        """Récupère les données complètes d'un tournoi MTGO"""
        try:
            url = f"https://www.mtgo.com{href}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return await self._parse_mtgo_tournament_page(html, href, date)
                else:
                    logger.warning(f"MTGO tournament {href}: HTTP {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching MTGO tournament {href}: {e}")
            return None

    async def _parse_mtgo_tournament_page(
        self, html: str, href: str, date: datetime
    ) -> Optional[Dict]:
        """Parse une page de tournoi MTGO"""
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Extraire les informations du tournoi
            tournament_name = (
                soup.find("h1").text.strip() if soup.find("h1") else "MTGO Tournament"
            )

            # Chercher les decklists
            decklists = []
            decklist_sections = soup.find_all("div", class_="decklist")

            for section in decklist_sections:
                try:
                    player_name = (
                        section.find("h3").text.strip()
                        if section.find("h3")
                        else "Unknown Player"
                    )

                    # Extraire le mainboard
                    mainboard = []
                    mainboard_section = section.find("div", class_="mainboard")
                    if mainboard_section:
                        for card in mainboard_section.find_all("li"):
                            card_text = card.text.strip()
                            if "x" in card_text:
                                count, name = card_text.split("x", 1)
                                mainboard.append(
                                    {"Name": name.strip(), "Count": int(count.strip())}
                                )

                    # Extraire le sideboard
                    sideboard = []
                    sideboard_section = section.find("div", class_="sideboard")
                    if sideboard_section:
                        for card in sideboard_section.find_all("li"):
                            card_text = card.text.strip()
                            if "x" in card_text:
                                count, name = card_text.split("x", 1)
                                sideboard.append(
                                    {"Name": name.strip(), "Count": int(count.strip())}
                                )

                    decklists.append(
                        {
                            "Player": player_name,
                            "Mainboard": mainboard,
                            "Sideboard": sideboard,
                            "Wins": 0,  # À extraire si disponible
                            "Losses": 0,
                            "Result": "0-0",
                        }
                    )

                except Exception as e:
                    logger.error(f"Error parsing decklist: {e}")
                    continue

            if decklists:
                return {
                    "Tournament": {
                        "Name": tournament_name,
                        "Date": date.isoformat(),
                        "Format": "Standard",  # À détecter automatiquement
                        "Uri": href,
                    },
                    "Standings": decklists,
                }

        except Exception as e:
            logger.error(f"Error parsing MTGO tournament page: {e}")

        return None

    async def scrape_melee_data(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Scrape les données Melee.gg pour une période donnée"""
        logger.info(
            f"🌐 Scraping Melee.gg data from {start_date.date()} to {end_date.date()}"
        )

        tournaments = []

        try:
            # Récupérer la liste des tournois
            url = f"{self.melee_api}/tournaments"

            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000,
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tournament_list = data.get("tournaments", [])

                    logger.info(f"📋 Found {len(tournament_list)} Melee tournaments")

                    # Récupérer les détails de chaque tournoi
                    for tournament in tournament_list:
                        try:
                            tournament_details = await self._fetch_melee_tournament(
                                tournament["id"]
                            )
                            if tournament_details:
                                tournaments.append(tournament_details)

                            # Pause pour éviter le rate limiting
                            await asyncio.sleep(0.5)

                        except Exception as e:
                            logger.error(
                                f"Error fetching Melee tournament {tournament['id']}: {e}"
                            )
                            continue
                else:
                    logger.warning(f"Melee API: HTTP {response.status}")

        except Exception as e:
            logger.error(f"Error scraping Melee data: {e}")

        logger.info(f"🎯 Melee scraping complete: {len(tournaments)} total tournaments")
        return tournaments

    async def _fetch_melee_tournament(self, tournament_id: str) -> Optional[Dict]:
        """Récupère les détails complets d'un tournoi Melee"""
        try:
            # Récupérer les détails du tournoi
            url = f"{self.melee_api}/tournaments/{tournament_id}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    tournament_data = await response.json()

                    # Récupérer les decklists
                    decklists_url = (
                        f"{self.melee_api}/tournaments/{tournament_id}/decklists"
                    )

                    async with self.session.get(decklists_url) as decklists_response:
                        if decklists_response.status == 200:
                            decklists_data = await decklists_response.json()
                            tournament_data["decklists"] = decklists_data.get(
                                "decklists", []
                            )

                            return self._format_melee_tournament(tournament_data)
                        else:
                            logger.warning(
                                f"Melee decklists {tournament_id}: HTTP {decklists_response.status}"
                            )
                            return None
                else:
                    logger.warning(
                        f"Melee tournament {tournament_id}: HTTP {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error fetching Melee tournament {tournament_id}: {e}")
            return None

    def _format_melee_tournament(self, tournament_data: Dict) -> Dict:
        """Formate les données Melee au format MTGODecklistCache"""
        try:
            standings = []

            for decklist in tournament_data.get("decklists", []):
                # Convertir le format Melee vers MTGODecklistCache
                mainboard = []
                for card in decklist.get("mainboard", []):
                    mainboard.append(
                        {"Name": card.get("name", ""), "Count": card.get("quantity", 0)}
                    )

                sideboard = []
                for card in decklist.get("sideboard", []):
                    sideboard.append(
                        {"Name": card.get("name", ""), "Count": card.get("quantity", 0)}
                    )

                standings.append(
                    {
                        "Player": decklist.get("player", {}).get("name", "Unknown"),
                        "Wins": decklist.get("wins", 0),
                        "Losses": decklist.get("losses", 0),
                        "Deck": {"Mainboard": mainboard, "Sideboard": sideboard},
                    }
                )

            return {
                "Tournament": {
                    "Name": tournament_data.get("name", "Melee Tournament"),
                    "Date": tournament_data.get("date", ""),
                    "Format": tournament_data.get("format", "Standard"),
                    "Uri": f"melee_{tournament_data.get('id', '')}",
                },
                "Standings": standings,
            }

        except Exception as e:
            logger.error(f"Error formatting Melee tournament: {e}")
            return None

    def save_tournaments(self, tournaments: List[Dict], source: str):
        """Sauvegarde les tournois dans le cache local"""
        logger.info(f"💾 Saving {len(tournaments)} {source} tournaments to cache")

        # Organiser par date
        tournaments_by_date = {}

        for tournament in tournaments:
            try:
                date_str = tournament.get("Tournament", {}).get("Date", "")
                if date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_key = date.strftime("%Y/%m/%d")

                    if date_key not in tournaments_by_date:
                        tournaments_by_date[date_key] = []

                    tournaments_by_date[date_key].append(tournament)

            except Exception as e:
                logger.error(f"Error processing tournament date: {e}")
                continue

        # Sauvegarder par date
        for date_key, daily_tournaments in tournaments_by_date.items():
            try:
                # Créer le dossier
                save_dir = self.cache_dir / source / date_key
                save_dir.mkdir(parents=True, exist_ok=True)

                # Sauvegarder chaque tournoi
                for i, tournament in enumerate(daily_tournaments):
                    tournament_name = tournament.get("Tournament", {}).get(
                        "Name", f"tournament_{i}"
                    )
                    format_name = (
                        tournament.get("Tournament", {})
                        .get("Format", "unknown")
                        .lower()
                    )

                    # Nettoyer le nom de fichier
                    safe_name = "".join(
                        c
                        for c in tournament_name
                        if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    safe_name = safe_name.replace(" ", "-")

                    filename = (
                        f"{safe_name}-{format_name}-{date_key.replace('/', '-')}.json"
                    )
                    filepath = save_dir / filename

                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(tournament, f, indent=2, ensure_ascii=False)

            except Exception as e:
                logger.error(f"Error saving tournaments for {date_key}: {e}")

    async def run_comprehensive_scraping(self):
        """Lance le scraping complet pour 2 ans de données"""
        logger.info("🚀 Starting comprehensive scraping for 2 years of data")

        # Calculer la période (2 ans en arrière)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2 * 365)

        logger.info(f"📅 Period: {start_date.date()} to {end_date.date()}")

        # Scraping MTGO
        logger.info("🌐 Starting MTGO scraping...")
        mtgo_tournaments = await self.scrape_mtgo_data(start_date, end_date)
        self.save_tournaments(mtgo_tournaments, "mtgo")

        # Scraping Melee
        logger.info("🌐 Starting Melee.gg scraping...")
        melee_tournaments = await self.scrape_melee_data(start_date, end_date)
        self.save_tournaments(melee_tournaments, "melee")

        # Résumé final
        total_tournaments = len(mtgo_tournaments) + len(melee_tournaments)
        logger.info(f"🎯 Comprehensive scraping complete!")
        logger.info(f"   - MTGO: {len(mtgo_tournaments)} tournaments")
        logger.info(f"   - Melee: {len(melee_tournaments)} tournaments")
        logger.info(f"   - Total: {total_tournaments} tournaments")
        logger.info(f"   - Cache location: {self.cache_dir}")


async def main():
    """Fonction principale"""
    logger.info("🚀 Manalytics Comprehensive Scraping")
    logger.info("=" * 50)

    async with ComprehensiveScraper() as scraper:
        await scraper.run_comprehensive_scraping()


if __name__ == "__main__":
    # Créer le dossier logs
    Path("logs").mkdir(exist_ok=True)

    # Lancer le scraping
    asyncio.run(main())
