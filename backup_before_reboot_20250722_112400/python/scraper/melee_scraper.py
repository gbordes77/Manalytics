"""
Melee.gg Scraper for Manalytics - MÉTHODE FBETTEGA
Scraper pour récupérer les données de tournois depuis melee.gg
Utilise la méthode fbettega avec l'API Round Standings
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MtgMeleeConstants:
    """Constantes pour l'API Melee basées sur fbettega"""

    TOURNAMENT_LIST_URL = "https://melee.gg/Decklist/TournamentSearch"
    ROUND_PAGE = "https://melee.gg/Standing/GetRoundStandings"
    DECK_PAGE = "https://melee.gg/Decklist/View/{deckId}"
    TOURNAMENT_PAGE = "https://melee.gg/Tournament/View/{tournamentId}"

    # Parameters for the Round Page (fbettega method)
    ROUND_PAGE_PARAMETERS = (
        "draw=1&columns%5B0%5D%5Bdata%5D=Rank&columns%5B0%5D%5Bname%5D=Rank&columns%5B0%5D%5Bsearchable%5D=true&"
        "columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B1%5D%5Bdata%5D=Player&columns%5B1%5D%5Bname%5D=Player&columns%5B1%5D%5Bsearchable%5D=false&"
        "columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B2%5D%5Bdata%5D=Decklists&columns%5B2%5D%5Bname%5D=Decklists&columns%5B2%5D%5Bsearchable%5D=false&"
        "columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B3%5D%5Bdata%5D=MatchRecord&columns%5B3%5D%5Bname%5D=MatchRecord&columns%5B3%5D%5Bsearchable%5D=false&"
        "columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B4%5D%5Bdata%5D=GameRecord&columns%5B4%5D%5Bname%5D=GameRecord&columns%5B4%5D%5Bsearchable%5D=false&"
        "columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B5%5D%5Bdata%5D=Points&columns%5B5%5D%5Bname%5D=Points&columns%5B5%5D%5Bsearchable%5D=true&"
        "columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B6%5D%5Bdata%5D=OpponentMatchWinPercentage&columns%5B6%5D%5Bname%5D=OpponentMatchWinPercentage&"
        "columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&"
        "columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=TeamGameWinPercentage&"
        "columns%5B7%5D%5Bname%5D=TeamGameWinPercentage&columns%5B7%5D%5Bsearchable%5D=false&"
        "columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B8%5D%5Bdata%5D=OpponentGameWinPercentage&columns%5B8%5D%5Bname%5D=OpponentGameWinPercentage&"
        "columns%5B8%5D%5Bsearchable%5D=false&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&"
        "columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=FinalTiebreaker&"
        "columns%5B9%5D%5Bname%5D=FinalTiebreaker&columns%5B9%5D%5Bsearchable%5D=true&"
        "columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B10%5D%5Bdata%5D=OpponentCount&columns%5B10%5D%5Bname%5D=OpponentCount&"
        "columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&"
        "columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&"
        "order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start={start}&length=25&"
        "search%5Bvalue%5D=&search%5Bregex%5D=false&roundId={roundId}"
    )

    @staticmethod
    def build_tournament_payload(
        start_date: datetime, end_date: datetime, start: int = 0, length: int = 100
    ):
        """Construit le payload pour la recherche de tournois"""
        return {
            "draw": "1",
            "columns[0][data]": "ID",
            "columns[0][name]": "ID",
            "columns[0][searchable]": "false",
            "columns[0][orderable]": "false",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "Name",
            "columns[1][name]": "Name",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "StartDate",
            "columns[2][name]": "StartDate",
            "columns[2][searchable]": "false",
            "columns[2][orderable]": "true",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "Status",
            "columns[3][name]": "Status",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "Format",
            "columns[4][name]": "Format",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "columns[5][data]": "OrganizationName",
            "columns[5][name]": "OrganizationName",
            "columns[5][searchable]": "true",
            "columns[5][orderable]": "true",
            "columns[5][search][value]": "",
            "columns[5][search][regex]": "false",
            "columns[6][data]": "Decklists",
            "columns[6][name]": "Decklists",
            "columns[6][searchable]": "true",
            "columns[6][orderable]": "true",
            "columns[6][search][value]": "",
            "columns[6][search][regex]": "false",
            "order[0][column]": "2",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "q": "",
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }


class MeleeScraper(BaseScraper):
    """Scraper pour les données de melee.gg - MÉTHODE FBETTEGA"""

    def __init__(self, cache_folder: str, api_config: Dict):
        """
        Initialise le scraper Melee

        Args:
            cache_folder: Répertoire de cache
            api_config: Configuration de l'API
        """
        super().__init__(cache_folder, api_config)
        self.base_url = "https://melee.gg"
        self.session = None

    async def authenticate(self):
        """Authentification auprès de l'API Melee"""
        # Pas d'authentification requise pour les données publiques
        pass

    async def __aenter__(self):
        """Gestionnaire de contexte async - entrée"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gestionnaire de contexte async - sortie"""
        if self.session:
            await self.session.close()

    @staticmethod
    def normalize_spaces(data):
        """Normalise les espaces dans les chaînes de caractères"""
        return re.sub(r"\s+", " ", data).strip()

    async def get_tournaments(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Récupère tous les tournois Standard (méthode fbettega)"""
        logger.info(
            f"🔍 Récupération des tournois Standard du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        )

        all_tournaments = []
        start = 0
        length = 100
        total_expected = None

        while True:
            payload = MtgMeleeConstants.build_tournament_payload(
                start_date, end_date, start, length
            )

            logger.info(
                f"📡 Page {start//length + 1}: Récupération de {start} à {start + length}..."
            )

            # Appel API avec retry
            MAX_RETRIES = 3
            DELAY_SECONDS = 2

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    async with self.session.post(
                        MtgMeleeConstants.TOURNAMENT_LIST_URL, data=payload
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            break
                        else:
                            logger.error(
                                f"❌ Tentative {attempt}: Erreur HTTP {response.status}"
                            )
                except Exception as e:
                    logger.error(f"❌ Tentative {attempt}: Erreur {e}")

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(DELAY_SECONDS)
            else:
                logger.error("❌ Échec après toutes les tentatives")
                break

            # Traitement des résultats
            tournaments = data.get("data", [])
            if not tournaments:
                logger.info("✅ Aucun tournoi supplémentaire trouvé")
                break

            # Filtrage Standard
            standard_tournaments = []
            for tournament in tournaments:
                format_desc = tournament.get("FormatDescription", "").lower()
                if "standard" in format_desc:
                    standard_tournaments.append(tournament)

            all_tournaments.extend(standard_tournaments)

            # Mise à jour du total attendu
            if total_expected is None:
                total_expected = data.get("recordsFiltered", 0)
                logger.info(f"📊 Total tournois disponibles: {total_expected}")

            logger.info(f"📊 Tournois Standard récupérés: {len(all_tournaments)}")

            # Vérification de fin
            if start + length >= total_expected:
                logger.info("✅ Pagination terminée")
                break

            start += length
            await asyncio.sleep(1)  # Pause entre les requêtes

        logger.info(
            f"🎯 Récupération terminée: {len(all_tournaments)} tournois Standard au total"
        )
        return all_tournaments

    async def get_round_ids(self, tournament_id: int) -> List[str]:
        """Récupère les IDs des rounds d'un tournoi (méthode fbettega)"""
        tournament_url = MtgMeleeConstants.TOURNAMENT_PAGE.replace(
            "{tournamentId}", str(tournament_id)
        )

        try:
            async with self.session.get(tournament_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "html.parser")

                    # Trouver les rounds complétés (méthode fbettega)
                    round_nodes = soup.select(
                        'button.btn.btn-gray.round-selector[data-is-completed="True"]'
                    )
                    round_ids = [node["data-id"] for node in round_nodes]

                    logger.info(f"    🔍 {len(round_ids)} rounds complétés trouvés")
                    return round_ids

        except Exception as e:
            logger.error(f"    ❌ Erreur récupération rounds: {e}")

        return []

    async def get_players_and_decks(
        self, tournament_id: int, round_id: str
    ) -> List[Dict]:
        """Récupère les joueurs et leurs deck IDs via l'API Round Standings (méthode fbettega)"""
        logger.info(f"    📊 Récupération des joueurs pour round {round_id}")

        players = []
        offset = 0

        while True:
            # Construire les paramètres pour l'API Round Standings
            round_parameters = MtgMeleeConstants.ROUND_PAGE_PARAMETERS.replace(
                "{start}", str(offset)
            ).replace("{roundId}", round_id)

            # Appel API avec retry
            MAX_RETRIES = 3
            DELAY_SECONDS = 2

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    async with self.session.post(
                        MtgMeleeConstants.ROUND_PAGE, data=round_parameters
                    ) as response:
                        if response.status == 200:
                            round_data = await response.json()
                            break
                        else:
                            logger.error(
                                f"      ❌ Tentative {attempt}: Erreur HTTP {response.status}"
                            )
                except Exception as e:
                    logger.error(f"      ❌ Tentative {attempt}: Erreur {e}")

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(DELAY_SECONDS)
            else:
                logger.error("      ❌ Échec après toutes les tentatives")
                break

            # Traitement des résultats
            entries = round_data.get("data", [])
            if not entries:
                logger.info("      ✅ Aucun joueur supplémentaire trouvé")
                break

            for entry in entries:
                player_name = entry["Team"]["Players"][0]["DisplayName"]
                if not player_name:
                    continue

                player_name = self.normalize_spaces(player_name)
                username = entry["Team"]["Players"][0]["Username"]

                # Récupérer les deck IDs (méthode fbettega)
                deck_ids = []
                for decklist in entry["Decklists"]:
                    deck_id = decklist["DecklistId"]
                    if deck_id:
                        deck_ids.append(deck_id)

                player_data = {
                    "player_name": player_name,
                    "username": username,
                    "deck_ids": deck_ids,
                    "rank": entry["Rank"],
                    "points": entry["Points"],
                    "wins": entry["MatchWins"],
                    "losses": entry["MatchLosses"],
                    "draws": entry["MatchDraws"],
                }
                players.append(player_data)

                logger.info(f"      👤 {player_name} - {len(deck_ids)} decks")

            offset += 25
            if len(entries) < 25:  # Plus de données
                break

            await asyncio.sleep(0.5)  # Pause entre les requêtes

        logger.info(f"      🎯 {len(players)} joueurs récupérés")
        return players

    async def get_deck_details(self, deck_id: str) -> Dict:
        """Récupère les détails d'un deck (méthode fbettega)"""
        deck_url = MtgMeleeConstants.DECK_PAGE.replace("{deckId}", deck_id)

        try:
            async with self.session.get(deck_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    deck_soup = BeautifulSoup(html_content, "html.parser")

                    # Extraire le nom du joueur (méthode fbettega)
                    player_link_element = deck_soup.select_one(
                        "a.text-nowrap.text-muted"
                    )
                    if player_link_element:
                        player_name = player_link_element.select_one(
                            "span.text-nowrap"
                        ).text.strip()
                    else:
                        player_name = "Unknown Player"

                    # Extraire les cartes (méthode fbettega)
                    deck_text = deck_soup.select_one("pre#decklist-text")
                    if deck_text:
                        card_list = deck_text.text.split("\r\n")

                        main_board = []
                        side_board = []
                        inside_sideboard = False

                        for card in card_list:
                            if card in [
                                "MainDeck",
                                "Companion",
                                "Sideboard",
                                "Commander",
                                "",
                            ]:
                                inside_sideboard = card == "Sideboard"
                            else:
                                if card and " " in card:
                                    count, name = card.split(" ", 1)
                                    try:
                                        count = int(count)
                                        if inside_sideboard:
                                            side_board.append(
                                                {"name": name, "count": count}
                                            )
                                        else:
                                            main_board.append(
                                                {"name": name, "count": count}
                                            )
                                    except ValueError:
                                        pass

                        deck_data = {
                            "player_name": player_name,
                            "main_board": main_board,
                            "side_board": side_board,
                            "deck_url": deck_url,
                        }

                        logger.info(
                            f"        ✅ {player_name} - {len(main_board)} main + {len(side_board)} side"
                        )
                        return deck_data

        except Exception as e:
            logger.error(f"        ❌ Erreur récupération deck {deck_id}: {e}")

        return None

    async def scrape_format_data(
        self, format_name: str = "Standard", days_back: int = 30
    ) -> Dict:
        """
        Scrape les données d'un format spécifique (MÉTHODE FBETTEGA)

        Args:
            format_name: Format des tournois (Standard, Modern, etc.)
            days_back: Nombre de jours à remonter

        Returns:
            Données des tournois et decks
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        # Configuration des dates
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)

        logger.info(f"🚀 SCRAPING MELEE {format_name.upper()} - MÉTHODE FBETTEGA")
        logger.info(
            f"📅 Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        )

        # Récupération de TOUS les tournois Standard
        tournaments = await self.get_tournaments(start_date, end_date)

        if not tournaments:
            logger.warning("❌ Aucun tournoi Standard trouvé")
            return {"tournaments": [], "total_decks": 0}

        logger.info(f"\n🏆 {len(tournaments)} tournois Standard trouvés")

        # Récupération des decks pour chaque tournoi Standard
        result = []
        total_decks = 0

        for i, tournament in enumerate(tournaments):
            tournament_id = tournament["ID"]
            tournament_name = tournament.get("Name", "Unnamed Tournament")
            tournament_date = datetime.fromisoformat(
                tournament["StartDate"].replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")

            logger.info(f"\n📋 [{i+1}/{len(tournaments)}] Tournoi: {tournament_name}")

            # Récupération des round IDs
            round_ids = await self.get_round_ids(tournament_id)

            all_decks = []
            for round_id in round_ids:
                # Récupération des joueurs et leurs deck IDs
                players = await self.get_players_and_decks(tournament_id, round_id)

                for player in players:
                    # Récupération des détails de chaque deck
                    for deck_id in player["deck_ids"]:
                        deck_details = await self.get_deck_details(deck_id)
                        if deck_details:
                            deck_details["player_rank"] = player["rank"]
                            deck_details["player_points"] = player["points"]
                            deck_details[
                                "player_record"
                            ] = f"{player['wins']}-{player['losses']}-{player['draws']}"
                            all_decks.append(deck_details)

                        await asyncio.sleep(0.5)  # Pause entre les decks

            if all_decks:
                tournament_data = {
                    "tournament": {
                        "Name": tournament_name,
                        "Date": tournament_date,
                        "Uri": MtgMeleeConstants.TOURNAMENT_PAGE.replace(
                            "{tournamentId}", str(tournament_id)
                        ),
                        "Format": format_name,
                        "Source": "melee.gg",
                    },
                    "decks": all_decks,
                }
                result.append(tournament_data)
                total_decks += len(all_decks)
                logger.info(f"  ✅ {len(all_decks)} decks ajoutés")
            else:
                logger.warning(f"  ⚠️ Aucun deck trouvé")

        logger.info(f"\n💾 Scraping terminé")
        logger.info(f"📊 Résumé:")
        logger.info(f"  • Tournois Standard traités: {len(result)}")
        logger.info(f"  • Total decks récupérés: {total_decks}")

        return {
            "tournaments": result,
            "total_decks": total_decks,
            "format": format_name,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }

    def save_to_cache(self, data: Dict, filename: str) -> str:
        """Sauvegarde les données en cache"""
        cache_path = Path(self.cache_folder) / filename
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"💾 Données sauvegardées: {cache_path}")
        return str(cache_path)

    def load_from_cache(self, filename: str) -> Optional[Dict]:
        """Charge les données depuis le cache"""
        cache_path = Path(self.cache_folder) / filename
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"📂 Données chargées depuis cache: {cache_path}")
            return data
        return None

    async def scrape_with_cache(
        self, format_name: str = "Standard", days_back: int = 30, cache_hours: int = 24
    ) -> Dict:
        """
        Scrape avec gestion du cache

        Args:
            format_name: Format des tournois
            days_back: Nombre de jours à remonter
            cache_hours: Durée de validité du cache en heures

        Returns:
            Données des tournois et decks
        """
        # Générer le nom du fichier cache
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)
        cache_filename = f"melee_{format_name.lower()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"

        # Vérifier le cache
        cached_data = self.load_from_cache(cache_filename)
        if cached_data:
            cache_time = datetime.fromisoformat(
                cached_data.get("cache_time", "1970-01-01T00:00:00+00:00")
            )
            if datetime.now(timezone.utc) - cache_time < timedelta(hours=cache_hours):
                logger.info("📂 Utilisation des données en cache")
                return cached_data

        # Scraper les nouvelles données
        data = await self.scrape_format_data(format_name, days_back)
        data["cache_time"] = datetime.now(timezone.utc).isoformat()

        # Sauvegarder en cache
        self.save_to_cache(data, cache_filename)

        return data
