"""
ManatraderClient - Reproduction du client Manatrader de fbettega/mtg_decklist_scrapper
Scraper pour Manatraders.com selon l'architecture Jilliac/Fbettega
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup


class ManatraderClient:
    """Client pour scraper Manatraders.com selon l'architecture fbettega"""

    def __init__(self, cache_folder: str = "data/raw/manatraders", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.manatraders.com"
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
        Fetch tournaments from Manatraders.com for the specified period
        Reproduit la logique de fbettega/mtg_decklist_scrapper
        """
        tournaments = []

        try:
            # Rechercher les tournois Manatraders
            tournament_list = await self._fetch_tournament_list(
                format_name, start_date, end_date
            )
            tournaments.extend(tournament_list)

            self.logger.info(
                f"Manatraders: Found {len(tournaments)} tournaments for {format_name} ({start_date} to {end_date})"
            )

        except Exception as e:
            self.logger.error(f"Error fetching Manatraders tournaments: {e}")

        return tournaments

    async def _fetch_tournament_list(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch tournament list from Manatraders"""
        tournaments = []

        try:
            # URLs typiques Manatraders
            search_urls = [
                f"{self.base_url}/tournaments/{format_name.lower()}",
                f"{self.base_url}/decklists/{format_name.lower()}",
                f"{self.base_url}/events",
            ]

            for url in search_urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, "html.parser")

                            # Parser les tournois selon la structure Manatraders
                            tournament_links = soup.find_all(
                                "a", href=re.compile(r"/tournament/|/event/")
                            )

                            for link in tournament_links:
                                tournament_url = (
                                    self.base_url + link["href"]
                                    if not link["href"].startswith("http")
                                    else link["href"]
                                )
                                tournament_data = await self._parse_tournament(
                                    tournament_url, format_name
                                )

                                if tournament_data and self._is_in_date_range(
                                    tournament_data.get("date"), start_date, end_date
                                ):
                                    tournaments.append(tournament_data)

                except Exception as e:
                    self.logger.warning(f"Error fetching from {url}: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Error in Manatraders tournament list: {e}")

        return tournaments

    async def _parse_tournament(self, url: str, format_name: str) -> Optional[Dict]:
        """Parse individual tournament from Manatraders"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extraire les informations du tournoi
                    title_elem = soup.find("h1") or soup.find(
                        "h2", class_="tournament-title"
                    )
                    title = (
                        title_elem.text.strip()
                        if title_elem
                        else "Manatraders Tournament"
                    )

                    date_elem = soup.find("span", class_="date") or soup.find("time")
                    date_str = date_elem.text.strip() if date_elem else ""

                    # Extraire les decklists
                    decks = []
                    deck_sections = soup.find_all(
                        "div", class_="deck"
                    ) or soup.find_all("div", class_="decklist")

                    for deck_section in deck_sections:
                        deck_data = self._parse_manatraders_deck(deck_section)
                        if deck_data:
                            decks.append(deck_data)

                    # Si pas de decks trouvés, chercher dans d'autres structures
                    if not decks:
                        deck_tables = soup.find_all("table", class_="results")
                        for table in deck_tables:
                            table_decks = self._parse_results_table(table)
                            decks.extend(table_decks)

                    return {
                        "id": url.split("/")[-1],
                        "name": title,
                        "date": self._extract_date(date_str),
                        "format": format_name,
                        "type": "Tournament",
                        "url": url,
                        "source": "manatraders.com",
                        "decks": decks,
                    }

        except Exception as e:
            self.logger.warning(f"Error parsing Manatraders tournament {url}: {e}")

        return None

    def _parse_manatraders_deck(self, deck_section) -> Optional[Dict]:
        """Parse Manatraders deck section"""
        try:
            # Extraire le nom du joueur
            player_elem = deck_section.find(
                "span", class_="player"
            ) or deck_section.find("h3")
            player_name = player_elem.text.strip() if player_elem else "Unknown"

            # Extraire le résultat
            result_elem = deck_section.find(
                "span", class_="result"
            ) or deck_section.find("span", class_="record")
            result = result_elem.text.strip() if result_elem else "Unknown"

            # Extraire la decklist
            mainboard = []

            # Chercher les cartes dans différents formats
            card_elements = (
                deck_section.find_all("div", class_="card")
                or deck_section.find_all("li", class_="card")
                or deck_section.find_all("tr")
            )

            for card_elem in card_elements:
                card_data = self._extract_card_from_element(card_elem)
                if card_data:
                    mainboard.append(card_data)

            # Lien vers la decklist
            link_elem = deck_section.find("a")
            deck_url = ""
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                deck_url = self.base_url + href if not href.startswith("http") else href

            return {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": [],  # Simplification pour l'instant
                "AnchorUri": deck_url,
            }

        except Exception as e:
            self.logger.warning(f"Error parsing Manatraders deck: {e}")

        return None

    def _parse_results_table(self, table) -> List[Dict]:
        """Parse results table from Manatraders"""
        decks = []

        try:
            rows = table.find_all("tr")[1:]  # Skip header

            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    # Structure typique: Position | Player | Record | Deck
                    player_name = cells[1].text.strip()
                    result = cells[2].text.strip()

                    # Chercher le lien vers la decklist
                    deck_link = row.find("a")
                    deck_url = ""
                    if deck_link and deck_link.get("href"):
                        href = deck_link["href"]
                        deck_url = (
                            self.base_url + href
                            if not href.startswith("http")
                            else href
                        )

                    deck_data = {
                        "Player": player_name,
                        "Result": result,
                        "Mainboard": [],  # À remplir si on fetch la decklist complète
                        "Sideboard": [],
                        "AnchorUri": deck_url,
                    }

                    decks.append(deck_data)

        except Exception as e:
            self.logger.warning(f"Error parsing Manatraders results table: {e}")

        return decks

    def _extract_card_from_element(self, card_elem) -> Optional[Dict]:
        """Extract card information from element"""
        try:
            # Différents patterns pour extraire nom et quantité
            text = card_elem.get_text().strip()

            # Pattern: "4 Lightning Bolt"
            match = re.match(r"(\d+)\s+(.+)", text)
            if match:
                count, name = match.groups()
                return {"CardName": name.strip(), "Count": int(count)}

            # Pattern: nom dans span séparé
            count_elem = card_elem.find("span", class_="count")
            name_elem = card_elem.find("span", class_="name")

            if name_elem:
                count = int(count_elem.text.strip()) if count_elem else 1
                return {"CardName": name_elem.text.strip(), "Count": count}

            # Fallback: tout le texte comme nom de carte
            if text and not text.isdigit():
                return {"CardName": text, "Count": 1}

        except Exception as e:
            self.logger.warning(f"Error extracting card from element: {e}")

        return None

    def _extract_date(self, date_str: str) -> str:
        """Extract and normalize date from string"""
        try:
            # Patterns de dates Manatraders typiques
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
