"""
TopDeckClient - Reproduction du client TopDeck de fbettega/mtg_decklist_scrapper
Scraper pour TopDeck.gg selon l'architecture Jilliac/Fbettega
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup


class TopDeckClient:
    """Client pour scraper TopDeck.gg selon l'architecture fbettega"""

    def __init__(self, cache_folder: str = "data/raw/topdeck", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://topdeck.gg"
        self.session = None

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Manalytics-Fbettega/1.0"},
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
        Fetch tournaments from TopDeck.gg for the specified period
        Reproduit la logique de fbettega/mtg_decklist_scrapper
        """
        tournaments = []

        try:
            # Rechercher les tournois TopDeck
            search_tournaments = await self._fetch_search_tournaments(
                format_name, start_date, end_date
            )
            tournaments.extend(search_tournaments)

            # Rechercher les decklists récentes
            recent_decks = await self._fetch_recent_decklists(
                format_name, start_date, end_date
            )
            tournaments.extend(recent_decks)

            self.logger.info(
                f"TopDeck: Found {len(tournaments)} tournaments for {format_name} ({start_date} to {end_date})"
            )

        except Exception as e:
            self.logger.error(f"Error fetching TopDeck tournaments: {e}")

        return tournaments

    async def _fetch_search_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch tournaments via TopDeck search"""
        tournaments = []

        try:
            # URLs de recherche TopDeck
            search_urls = [
                f"{self.base_url}/tournament/search?format={format_name.lower()}",
                f"{self.base_url}/decks?format={format_name.lower()}",
            ]

            for url in search_urls:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Parser les tournois selon la structure TopDeck
                        tournament_cards = soup.find_all(
                            "div", class_="tournament-card"
                        )

                        for card in tournament_cards:
                            tournament_data = await self._parse_tournament_card(
                                card, format_name
                            )

                            if tournament_data and self._is_in_date_range(
                                tournament_data.get("date"), start_date, end_date
                            ):
                                tournaments.append(tournament_data)

        except Exception as e:
            self.logger.warning(f"Error fetching TopDeck search: {e}")

        return tournaments

    async def _fetch_recent_decklists(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch recent decklists from TopDeck"""
        tournaments = []

        try:
            # URL des decklists récentes
            decklist_url = f"{self.base_url}/decks/recent?format={format_name.lower()}"

            async with self.session.get(decklist_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Grouper les decklists par tournoi/date
                    deck_groups = self._group_decks_by_tournament(soup)

                    for group_date, decks in deck_groups.items():
                        if self._is_in_date_range(group_date, start_date, end_date):
                            tournament_data = {
                                "id": f"topdeck-{group_date}",
                                "name": f"TopDeck {format_name} - {group_date}",
                                "date": group_date,
                                "format": format_name,
                                "type": "Collection",
                                "url": decklist_url,
                                "source": "topdeck.gg",
                                "decks": decks,
                            }
                            tournaments.append(tournament_data)

        except Exception as e:
            self.logger.warning(f"Error fetching TopDeck recent decklists: {e}")

        return tournaments

    async def _parse_tournament_card(self, card, format_name: str) -> Optional[Dict]:
        """Parse tournament card from TopDeck"""
        try:
            # Extraire les informations du tournoi
            title_elem = card.find("h3") or card.find("a", class_="tournament-title")
            title = title_elem.text.strip() if title_elem else "TopDeck Tournament"

            date_elem = card.find("span", class_="date") or card.find("time")
            date_str = date_elem.text.strip() if date_elem else ""

            link_elem = card.find("a")
            tournament_url = (
                self.base_url + link_elem["href"]
                if link_elem and link_elem.get("href")
                else ""
            )

            # Récupérer les détails du tournoi
            if tournament_url:
                tournament_details = await self._fetch_tournament_details(
                    tournament_url
                )

                return {
                    "id": tournament_url.split("/")[-1],
                    "name": title,
                    "date": self._extract_date(date_str),
                    "format": format_name,
                    "type": "Tournament",
                    "url": tournament_url,
                    "source": "topdeck.gg",
                    "decks": tournament_details.get("decks", []),
                }

        except Exception as e:
            self.logger.warning(f"Error parsing TopDeck tournament card: {e}")

        return None

    async def _fetch_tournament_details(self, url: str) -> Dict:
        """Fetch detailed tournament information"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extraire les decklists
                    decks = []
                    deck_sections = soup.find_all("div", class_="deck-entry")

                    for deck_section in deck_sections:
                        deck_data = self._parse_topdeck_deck(deck_section)
                        if deck_data:
                            decks.append(deck_data)

                    return {"decks": decks}

        except Exception as e:
            self.logger.warning(f"Error fetching tournament details {url}: {e}")

        return {"decks": []}

    def _parse_topdeck_deck(self, deck_section) -> Optional[Dict]:
        """Parse TopDeck deck section"""
        try:
            # Extraire le nom du joueur
            player_elem = deck_section.find(
                "span", class_="player"
            ) or deck_section.find("h4")
            player_name = player_elem.text.strip() if player_elem else "Unknown"

            # Extraire le résultat
            result_elem = deck_section.find(
                "span", class_="result"
            ) or deck_section.find("span", class_="record")
            result = result_elem.text.strip() if result_elem else "Unknown"

            # Extraire la decklist
            mainboard = []
            card_elements = deck_section.find_all("div", class_="card-line")

            for card_elem in card_elements:
                count_elem = card_elem.find("span", class_="count")
                name_elem = card_elem.find("span", class_="name")

                if name_elem:
                    count = int(count_elem.text.strip()) if count_elem else 1
                    card_name = name_elem.text.strip()

                    mainboard.append({"CardName": card_name, "Count": count})

            # Lien vers la decklist
            link_elem = deck_section.find("a")
            deck_url = (
                self.base_url + link_elem["href"]
                if link_elem and link_elem.get("href")
                else ""
            )

            return {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": [],  # Simplification pour l'instant
                "AnchorUri": deck_url,
            }

        except Exception as e:
            self.logger.warning(f"Error parsing TopDeck deck: {e}")

        return None

    def _group_decks_by_tournament(self, soup) -> Dict[str, List[Dict]]:
        """Group decks by tournament/date"""
        groups = {}

        try:
            # Chercher les sections de decklists
            deck_sections = soup.find_all("div", class_="deck-item")

            for deck_section in deck_sections:
                # Extraire la date
                date_elem = deck_section.find("span", class_="date")
                date_str = self._extract_date(date_elem.text if date_elem else "")

                # Parser le deck
                deck_data = self._parse_topdeck_deck(deck_section)

                if deck_data:
                    if date_str not in groups:
                        groups[date_str] = []
                    groups[date_str].append(deck_data)

        except Exception as e:
            self.logger.warning(f"Error grouping TopDeck decks: {e}")

        return groups

    def _extract_date(self, date_str: str) -> str:
        """Extract and normalize date from string"""
        try:
            # Patterns de dates TopDeck typiques
            patterns = [
                r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
                r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
                r"(\w+)\s+(\d{1,2}),\s+(\d{4})",  # Month DD, YYYY
                r"(\d{1,2})\s+(\w+)\s+(\d{4})",  # DD Month YYYY
            ]

            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    if "-" in date_str:
                        return match.group(0)
                    elif "/" in date_str:
                        month, day, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Fallback à la date actuelle
            return datetime.now().strftime("%Y-%m-%d")

        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def _is_in_date_range(
        self, tournament_date: str, start_date: str, end_date: str
    ) -> bool:
        """Check if tournament date is in the specified range"""
        try:
            t_date = datetime.strptime(tournament_date, "%Y-%m-%d").date()
            s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            e_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            return s_date <= t_date <= e_date

        except Exception:
            return False
