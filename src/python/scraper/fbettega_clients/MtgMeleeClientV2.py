"""
MtgMeleeClientV2 - Reproduction du client Melee de fbettega/mtg_decklist_scrapper
Scraper pour Melee.gg selon l'architecture Jilliac/Fbettega avec credentials
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp


class MtgMeleeClientV2:
    """Client pour scraper Melee.gg selon l'architecture fbettega avec API credentials"""

    def __init__(self, cache_folder: str = "data/raw/melee", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://melee.gg/api"
        self.session = None
        self.credentials = self._load_credentials()

    def _load_credentials(self) -> Dict:
        """Load encrypted Melee credentials"""
        try:
            # Charger depuis le système de credentials chiffré
            from cryptography.fernet import Fernet

            # Lire la clé master
            with open("./credentials/master.key", "rb") as f:
                key = f.read()

            cipher = Fernet(key)

            # Lire les credentials chiffrés
            with open("./credentials/encrypted_credentials.json", "r") as f:
                encrypted_data = json.load(f)

            if "melee" in encrypted_data:
                # Déchiffrer les credentials Melee
                encrypted_cred = encrypted_data["melee"]["data"]
                decrypted_data = cipher.decrypt(encrypted_cred.encode())
                credentials = json.loads(decrypted_data.decode())

                self.logger.info("✅ Loaded Melee credentials from encrypted store")
                return credentials
            else:
                self.logger.warning("No Melee credentials found in encrypted store")
                return {}

        except Exception as e:
            self.logger.error(f"Error loading Melee credentials: {e}")
            return {}

    async def __aenter__(self):
        """Context manager entry"""
        headers = {"User-Agent": "Manalytics-Fbettega/1.0"}

        # Ajouter l'authentification si disponible
        if self.credentials.get("api_key"):
            headers["Authorization"] = f"Bearer {self.credentials['api_key']}"
        elif self.credentials.get("token"):
            headers["X-API-Token"] = self.credentials["token"]
        elif self.credentials.get("email") and self.credentials.get("password"):
            # Utiliser les credentials email/password pour l'authentification
            self.logger.info("Using email/password authentication for Melee")

        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30), headers=headers
        )

        # Authentification si nécessaire
        if self.credentials.get("email") and self.credentials.get("password"):
            await self._authenticate()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Fetch tournaments from Melee.gg for the specified period
        Reproduit la logique de fbettega/mtg_decklist_scrapper pour Melee
        """
        tournaments = []

        try:
            # Rechercher les tournois via l'API Melee
            api_tournaments = await self._fetch_api_tournaments(
                format_name, start_date, end_date
            )
            tournaments.extend(api_tournaments)

            # Fallback: scraping web si API limitée
            if len(tournaments) < 10:  # Seuil arbitraire
                web_tournaments = await self._fetch_web_tournaments(
                    format_name, start_date, end_date
                )
                tournaments.extend(web_tournaments)

            self.logger.info(
                f"Melee: Found {len(tournaments)} tournaments for {format_name} ({start_date} to {end_date})"
            )

        except Exception as e:
            self.logger.error(f"Error fetching Melee tournaments: {e}")

        return tournaments

    async def _fetch_api_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch tournaments via Melee API"""
        tournaments = []

        try:
            # Construire les paramètres API
            params = {
                "format": format_name.lower(),
                "start_date": start_date,
                "end_date": end_date,
                "game": "mtg",
                "status": "completed",
            }

            # Appel API pour récupérer les tournois
            async with self.session.get(
                f"{self.base_url}/tournaments", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    for tournament_data in data.get("tournaments", []):
                        tournament = await self._process_api_tournament(tournament_data)
                        if tournament:
                            tournaments.append(tournament)

                elif response.status == 401:
                    self.logger.warning(
                        "Melee API authentication failed - using web scraping fallback"
                    )
                else:
                    self.logger.warning(f"Melee API returned status {response.status}")

        except Exception as e:
            self.logger.warning(f"Error with Melee API: {e}")

        return tournaments

    async def _fetch_web_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fallback: fetch tournaments via web scraping"""
        tournaments = []

        try:
            # URLs de recherche Melee.gg
            search_urls = [
                f"https://melee.gg/Tournament/Search?game=mtg&format={format_name.lower()}",
                f"https://melee.gg/Decklists/Search?format={format_name.lower()}",
            ]

            for url in search_urls:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Parser le HTML pour extraire les tournois
                        page_tournaments = await self._parse_tournament_page(
                            html, format_name
                        )

                        # Filtrer par date
                        for tournament in page_tournaments:
                            if self._is_in_date_range(
                                tournament.get("date"), start_date, end_date
                            ):
                                tournaments.append(tournament)

        except Exception as e:
            self.logger.warning(f"Error with Melee web scraping: {e}")

        return tournaments

    async def _process_api_tournament(self, tournament_data: Dict) -> Optional[Dict]:
        """Process tournament data from API"""
        try:
            tournament_id = tournament_data.get("id")

            # Récupérer les decklists du tournoi
            decks = await self._fetch_tournament_decks(tournament_id)

            return {
                "id": tournament_id,
                "name": tournament_data.get("name", "Melee Tournament"),
                "date": tournament_data.get("date", ""),
                "format": tournament_data.get("format", "Standard"),
                "type": "Tournament",
                "url": f"https://melee.gg/Tournament/View/{tournament_id}",
                "source": "melee.gg",
                "decks": decks,
            }

        except Exception as e:
            self.logger.warning(f"Error processing API tournament: {e}")

        return None

    async def _fetch_tournament_decks(self, tournament_id: str) -> List[Dict]:
        """Fetch decks for a specific tournament"""
        decks = []

        try:
            # API call pour récupérer les decklists
            async with self.session.get(
                f"{self.base_url}/tournaments/{tournament_id}/decks"
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    for deck_data in data.get("decks", []):
                        deck = self._process_deck_data(deck_data)
                        if deck:
                            decks.append(deck)

        except Exception as e:
            self.logger.warning(f"Error fetching tournament decks: {e}")

        return decks

    def _process_deck_data(self, deck_data: Dict) -> Optional[Dict]:
        """Process individual deck data"""
        try:
            # Extraire la mainboard
            mainboard = []
            for card in deck_data.get("mainboard", []):
                mainboard.append(
                    {"CardName": card.get("name", ""), "Count": card.get("count", 1)}
                )

            # Extraire la sideboard
            sideboard = []
            for card in deck_data.get("sideboard", []):
                sideboard.append(
                    {"CardName": card.get("name", ""), "Count": card.get("count", 1)}
                )

            return {
                "Player": deck_data.get("player", "Unknown"),
                "Result": deck_data.get("record", "Unknown"),
                "Mainboard": mainboard,
                "Sideboard": sideboard,
                "AnchorUri": deck_data.get("url", ""),
            }

        except Exception as e:
            self.logger.warning(f"Error processing deck data: {e}")

        return None

    async def _parse_tournament_page(self, html: str, format_name: str) -> List[Dict]:
        """Parse tournament page HTML"""
        tournaments = []

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Chercher les liens de tournois
            tournament_links = soup.find_all(
                "a", href=lambda x: x and "/Tournament/View/" in x
            )

            for link in tournament_links:
                tournament_url = "https://melee.gg" + link["href"]
                tournament_data = await self._scrape_tournament_details(
                    tournament_url, format_name
                )

                if tournament_data:
                    tournaments.append(tournament_data)

        except Exception as e:
            self.logger.warning(f"Error parsing tournament page: {e}")

        return tournaments

    async def _scrape_tournament_details(
        self, url: str, format_name: str
    ) -> Optional[Dict]:
        """Scrape individual tournament details"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(html, "html.parser")

                    # Extraire les informations du tournoi
                    title = soup.find("h1")
                    date_elem = soup.find("span", class_="date")

                    # Extraire les decklists
                    decks = []
                    deck_sections = soup.find_all("div", class_="deck-entry")

                    for deck_section in deck_sections:
                        deck_data = self._parse_melee_deck(deck_section)
                        if deck_data:
                            decks.append(deck_data)

                    return {
                        "id": url.split("/")[-1],
                        "name": title.text.strip() if title else "Melee Tournament",
                        "date": self._extract_date(date_elem.text if date_elem else ""),
                        "format": format_name,
                        "type": "Tournament",
                        "url": url,
                        "source": "melee.gg",
                        "decks": decks,
                    }

        except Exception as e:
            self.logger.warning(f"Error scraping tournament {url}: {e}")

        return None

    def _parse_melee_deck(self, deck_section) -> Optional[Dict]:
        """Parse Melee deck section"""
        try:
            # Logique spécifique à Melee.gg
            player_elem = deck_section.find("span", class_="player-name")
            player_name = player_elem.text.strip() if player_elem else "Unknown"

            result_elem = deck_section.find("span", class_="record")
            result = result_elem.text.strip() if result_elem else "Unknown"

            # Parser la decklist
            mainboard = []
            card_elements = deck_section.find_all("div", class_="card-entry")

            for card_elem in card_elements:
                card_name_elem = card_elem.find("span", class_="card-name")
                count_elem = card_elem.find("span", class_="card-count")

                if card_name_elem:
                    mainboard.append(
                        {
                            "CardName": card_name_elem.text.strip(),
                            "Count": int(count_elem.text.strip()) if count_elem else 1,
                        }
                    )

            return {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": [],
                "AnchorUri": deck_section.find("a")["href"]
                if deck_section.find("a")
                else "",
            }

        except Exception as e:
            self.logger.warning(f"Error parsing Melee deck: {e}")

        return None

    def _extract_date(self, date_str: str) -> str:
        """Extract and normalize date from string"""
        try:
            import re

            # Patterns de dates Melee typiques
            patterns = [
                r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
                r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
                r"(\w+)\s+(\d{1,2}),\s+(\d{4})",  # Month DD, YYYY
            ]

            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    if "-" in date_str:
                        return match.group(0)
                    elif "/" in date_str:
                        month, day, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

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

    async def _authenticate(self):
        """Authentification avec Melee.gg"""
        try:
            login_url = "https://melee.gg/Account/Login"

            # Récupérer la page de login pour obtenir les tokens CSRF
            async with self.session.get(login_url) as response:
                if response.status == 200:
                    html = await response.text()
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(html, "html.parser")

                    # Extraire le token CSRF
                    csrf_token = None
                    csrf_input = soup.find(
                        "input", {"name": "__RequestVerificationToken"}
                    )
                    if csrf_input:
                        csrf_token = csrf_input.get("value")

                    # Données de login
                    login_data = {
                        "Email": self.credentials["email"],
                        "Password": self.credentials["password"],
                        "RememberMe": "false",
                    }

                    if csrf_token:
                        login_data["__RequestVerificationToken"] = csrf_token

                    # Effectuer le login
                    async with self.session.post(
                        login_url, data=login_data
                    ) as login_response:
                        if login_response.status == 200 or login_response.status == 302:
                            self.logger.info(
                                "✅ Successfully authenticated with Melee.gg"
                            )
                        else:
                            self.logger.warning(
                                f"Authentication may have failed: {login_response.status}"
                            )

        except Exception as e:
            self.logger.error(f"Error during Melee authentication: {e}")
