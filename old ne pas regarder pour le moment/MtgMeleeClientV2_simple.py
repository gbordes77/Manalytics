"""
MtgMeleeClientV2 - Version simplifiée pour web scraping Melee.gg
Reproduction de l'approche fbettega avec web scraping au lieu d'API
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup


class MtgMeleeClientV2:
    """Client pour scraper Melee.gg via web scraping (approche fbettega)"""

    def __init__(self, cache_folder: str = "data/raw/melee", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://melee.gg"
        self.session = None

    async def __aenter__(self):
        """Context manager entry"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30), headers=headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Fetch tournaments from Melee.gg using REAL fbettega method
        Endpoint: https://melee.gg/Decklist/SearchDecklists (POST)
        """
        tournaments = []

        try:
            from datetime import datetime

            # Convertir les dates string en datetime (méthode fbettega)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            self.logger.info(
                f"🌐 VRAIE MÉTHODE Melee.gg: {format_name} ({start_date} to {end_date})"
            )

            # Construire le payload DataTables (copié de fbettega)
            payload = self._build_melee_payload(
                start_dt, end_dt, length=500, draw=1, start=0
            )

            # Endpoint réel utilisé par fbettega
            search_url = "https://melee.gg/Decklist/SearchDecklists"

            self.logger.info(f"📡 POST: {search_url}")

            async with self.session.post(search_url, data=payload) as response:
                self.logger.info(f"Status: {response.status}")

                if response.status == 200:
                    try:
                        # Réponse JSON (format DataTables)
                        data = await response.json()

                        tournament_data = data.get("data", [])
                        self.logger.info(
                            f"✅ Données reçues: {len(tournament_data)} entrées"
                        )

                        # Grouper par tournoi (méthode fbettega)
                        tournaments_dict = {}

                        for item in tournament_data:
                            tournament_id = item.get("TournamentId")
                            if tournament_id not in tournaments_dict:
                                tournaments_dict[tournament_id] = {
                                    "id": tournament_id,
                                    "name": item.get(
                                        "TournamentName", f"Tournament {tournament_id}"
                                    ),
                                    "date": item.get("TournamentStartDate"),
                                    "format": item.get("FormatName", format_name),
                                    "source": "melee.gg",
                                    "decks": [],
                                }

                            # Ajouter la decklist
                            deck_info = {
                                "player": item.get("OwnerDisplayName"),
                                "decklist_id": item.get("Guid"),
                                "result": item.get("TeamRank"),
                                "wins": item.get("TeamMatchWins", 0),
                                "losses": 0,  # À calculer si nécessaire
                            }
                            tournaments_dict[tournament_id]["decks"].append(deck_info)

                        tournaments = list(tournaments_dict.values())

                        self.logger.info(f"🎯 Tournois groupés: {len(tournaments)}")
                        for t in tournaments[:3]:
                            self.logger.info(
                                f"   • {t['name']} - {len(t['decks'])} decks"
                            )

                    except Exception as e:
                        self.logger.error(f"❌ Erreur parsing JSON: {e}")
                        text = await response.text()
                        self.logger.info(f"Response text: {text[:500]}...")

                elif response.status == 403:
                    self.logger.error("❌ 403 Forbidden - Authentification requise")
                    self.logger.info("💡 Fbettega utilise des cookies de session")
                else:
                    self.logger.warning(f"⚠️  HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"❌ Error in REAL Melee method: {e}")

        return tournaments

    async def _parse_search_page(
        self, html_content: str, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Parse HTML search page to extract tournament information"""
        tournaments = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Rechercher les liens de tournois
            tournament_links = soup.find_all(
                "a", href=lambda x: x and "/Tournament/View/" in x
            )

            self.logger.info(
                f"🔍 Found {len(tournament_links)} tournament links in HTML"
            )

            for link in tournament_links[:10]:  # Limiter pour le test
                try:
                    tournament_url = link.get("href")
                    if not tournament_url.startswith("http"):
                        tournament_url = f"{self.base_url}{tournament_url}"

                    # Extraire l'ID du tournoi
                    tournament_id = tournament_url.split("/")[-1]

                    # Créer un tournoi basique pour le test
                    tournament_data = {
                        "id": tournament_id,
                        "name": f"Melee Tournament {tournament_id}",
                        "url": tournament_url,
                        "date": "2025-07-20",  # Placeholder pour le test
                        "format": format_name,
                        "source": "melee.gg",
                        "decks": [],  # À implémenter plus tard
                    }

                    # Vérifier la période (pour l'instant, accepter tous)
                    tournaments.append(tournament_data)

                except Exception as e:
                    self.logger.warning(f"⚠️  Error processing tournament link: {e}")
                    continue

            # Aussi chercher les decklists directement
            decklist_links = soup.find_all(
                "a", href=lambda x: x and "/Decklist/View/" in x
            )
            self.logger.info(f"🔍 Found {len(decklist_links)} decklist links in HTML")

        except Exception as e:
            self.logger.error(f"❌ Error parsing HTML: {e}")

        return tournaments

    def _build_melee_payload(
        self, start_date, end_date, length: int = 50, draw: int = 1, start: int = 0
    ):
        """Construire le payload DataTables exact de fbettega"""
        # Format date pour Melee (copié de fbettega)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        date_filter = f"{start_str}|{end_str}"

        # Payload DataTables complet (copié de fbettega)
        payload = {
            "draw": str(draw),
            "columns[0][data]": "DecklistName",
            "columns[0][name]": "DecklistName",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "Game",
            "columns[1][name]": "Game",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "MagicTheGathering",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "FormatId",
            "columns[2][name]": "FormatId",
            "columns[2][searchable]": "true",
            "columns[2][orderable]": "false",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "FormatName",
            "columns[3][name]": "FormatName",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "OwnerDisplayName",
            "columns[4][name]": "OwnerDisplayName",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "columns[5][data]": "TournamentName",
            "columns[5][name]": "TournamentName",
            "columns[5][searchable]": "true",
            "columns[5][orderable]": "true",
            "columns[5][search][value]": "",
            "columns[5][search][regex]": "false",
            "columns[6][data]": "SortDate",
            "columns[6][name]": "SortDate",
            "columns[6][searchable]": "true",
            "columns[6][orderable]": "true",
            "columns[6][search][value]": date_filter,  # 🎯 FILTRE DATE
            "columns[6][search][regex]": "false",
            "columns[7][data]": "TeamRank",
            "columns[7][name]": "TeamRank",
            "columns[7][searchable]": "false",
            "columns[7][orderable]": "true",
            "columns[7][search][value]": "",
            "columns[7][search][regex]": "false",
            "order[0][column]": "6",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
        }

        return payload

    def _is_in_date_range(
        self, tournament_date: str, start_date: str, end_date: str
    ) -> bool:
        """Check if tournament date is in the specified range"""
        try:
            # Pour l'instant, retourner True (à implémenter correctement plus tard)
            return True
        except Exception:
            return True
