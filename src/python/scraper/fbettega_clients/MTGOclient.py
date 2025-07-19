"""
MTGOClient - Reproduction du client MTGO de fbettega/mtg_decklist_scrapper
Scraper pour Magic Online selon l'architecture Jilliac/Fbettega
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup


class MTGOClient:
    """Client pour scraper MTGO selon l'architecture fbettega"""

    def __init__(self, cache_folder: str = "data/raw/mtgo", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.mtgo.com"
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
        Fetch tournaments from MTGO for the specified period
        CORRECTION: Découvrir les URLs depuis les pages de listing MTGO (comme fbettega/mtg_decklist_scrapper)
        """
        tournaments = []

        try:
            # 🔍 DÉCOUVRIR les URLs réelles depuis les pages de listing MTGO
            tournament_urls = await self._discover_tournament_urls(
                format_name, start_date, end_date
            )

            self.logger.info(
                f"MTGO: Discovered {len(tournament_urls)} real tournament URLs from listing pages"
            )

            # Parser chaque tournoi découvert
            for url in tournament_urls:
                tournament_data = await self._parse_tournament_url(url)
                if tournament_data and self._has_valid_standings(tournament_data):
                    tournaments.append(tournament_data)

            valid_tournaments = [t for t in tournaments if len(t.get("decks", [])) > 0]
            self.logger.info(
                f"MTGO: Found {len(valid_tournaments)} valid tournaments with data for {format_name} ({start_date} to {end_date})"
            )

        except Exception as e:
            self.logger.error(f"Error fetching MTGO tournaments: {e}")

        return tournaments

    async def _fetch_challenges(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch MTGO Challenges"""
        tournaments = []

        # URLs typiques des challenges MTGO
        challenge_urls = [
            f"{self.base_url}/decklist/{format_name.lower()}-challenge",
            f"{self.base_url}/decklist/{format_name.lower()}-super-qualifier",
        ]

        for url in challenge_urls:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Parser les tournois selon la structure MTGO
                        tournament_links = soup.find_all(
                            "a", href=re.compile(r"/decklist/")
                        )

                        for link in tournament_links:
                            tournament_url = self.base_url + link["href"]
                            tournament_data = await self._parse_tournament(
                                tournament_url, "Challenge"
                            )

                            if tournament_data and self._is_in_date_range(
                                tournament_data.get("date"), start_date, end_date
                            ):
                                tournaments.append(tournament_data)

            except Exception as e:
                self.logger.warning(f"Error fetching challenges from {url}: {e}")

        return tournaments

    async def _fetch_leagues(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch MTGO Leagues 5-0"""
        tournaments = []

        # URLs typiques des leagues MTGO
        league_urls = [
            f"{self.base_url}/decklist/{format_name.lower()}-league",
        ]

        for url in league_urls:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Parser les 5-0 leagues
                        league_sections = soup.find_all(
                            "div", class_="decklists-content"
                        )

                        for section in league_sections:
                            tournament_data = await self._parse_league_section(
                                section, format_name
                            )

                            if tournament_data and self._is_in_date_range(
                                tournament_data.get("date"), start_date, end_date
                            ):
                                tournaments.append(tournament_data)

            except Exception as e:
                self.logger.warning(f"Error fetching leagues from {url}: {e}")

        return tournaments

    async def _fetch_preliminaries(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch MTGO Preliminaries"""
        tournaments = []

        # URLs typiques des preliminaries MTGO
        prelim_urls = [
            f"{self.base_url}/decklist/{format_name.lower()}-preliminary",
        ]

        for url in prelim_urls:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Parser les preliminaries
                        tournament_links = soup.find_all(
                            "a", href=re.compile(r"/decklist/")
                        )

                        for link in tournament_links:
                            tournament_url = self.base_url + link["href"]
                            tournament_data = await self._parse_tournament(
                                tournament_url, "Preliminary"
                            )

                            if tournament_data and self._is_in_date_range(
                                tournament_data.get("date"), start_date, end_date
                            ):
                                tournaments.append(tournament_data)

            except Exception as e:
                self.logger.warning(f"Error fetching preliminaries from {url}: {e}")

        return tournaments

    async def _parse_tournament(self, url: str, tournament_type: str) -> Optional[Dict]:
        """Parse individual tournament page"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extraire les informations du tournoi
                    title = soup.find("h1")
                    date_elem = soup.find("time") or soup.find("span", class_="date")

                    # Extraire les decklists
                    decks = []
                    deck_sections = soup.find_all("div", class_="deck-group")

                    for deck_section in deck_sections:
                        deck_data = self._parse_deck_section(deck_section)
                        if deck_data:
                            decks.append(deck_data)

                    return {
                        "id": url.split("/")[-1],
                        "name": title.text.strip()
                        if title
                        else f"{tournament_type} Tournament",
                        "date": self._extract_date(date_elem.text if date_elem else ""),
                        "format": self._extract_format_from_url(url),
                        "type": tournament_type,
                        "url": url,
                        "source": "mtgo.com",
                        "decks": decks,
                    }

        except Exception as e:
            self.logger.warning(f"Error parsing tournament {url}: {e}")

        return None

    async def _parse_league_section(self, section, format_name: str) -> Optional[Dict]:
        """Parse league section for 5-0 decks"""
        try:
            # Extraire la date de la section
            date_elem = section.find("h3") or section.find("h2")
            date_str = date_elem.text if date_elem else ""

            # Extraire les decks 5-0
            decks = []
            deck_elements = section.find_all("div", class_="deck")

            for deck_elem in deck_elements:
                deck_data = self._parse_deck_element(deck_elem)
                if deck_data:
                    deck_data["result"] = "5-0"  # Leagues sont toujours 5-0
                    decks.append(deck_data)

            if decks:
                return {
                    "id": f"league-{self._extract_date(date_str)}",
                    "name": f"{format_name} League 5-0",
                    "date": self._extract_date(date_str),
                    "format": format_name,
                    "type": "League",
                    "source": "mtgo.com",
                    "decks": decks,
                }

        except Exception as e:
            self.logger.warning(f"Error parsing league section: {e}")

        return None

    def _parse_deck_section(self, deck_section) -> Optional[Dict]:
        """Parse individual deck section"""
        try:
            # Extraire le nom du joueur
            player_elem = deck_section.find(
                "span", class_="player"
            ) or deck_section.find("h4")
            player_name = player_elem.text.strip() if player_elem else "Unknown"

            # Extraire le résultat
            result_elem = deck_section.find("span", class_="record")
            result = result_elem.text.strip() if result_elem else "Unknown"

            # Extraire la decklist
            mainboard = []
            card_elements = deck_section.find_all("span", class_="card")

            for card_elem in card_elements:
                card_name = card_elem.text.strip()
                count_elem = card_elem.find_previous("span", class_="count")
                count = int(count_elem.text.strip()) if count_elem else 1

                mainboard.append({"CardName": card_name, "Count": count})

            return {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": [],  # Simplification pour l'instant
                "AnchorUri": deck_section.find("a")["href"]
                if deck_section.find("a")
                else "",
            }

        except Exception as e:
            self.logger.warning(f"Error parsing deck section: {e}")

        return None

    def _parse_deck_element(self, deck_elem) -> Optional[Dict]:
        """Parse deck element from league"""
        try:
            # Logique similaire à _parse_deck_section mais adaptée aux leagues
            player_name = deck_elem.get("data-player", "Unknown")

            mainboard = []
            # Parser la decklist selon la structure MTGO

            return {
                "Player": player_name,
                "Result": "5-0",
                "Mainboard": mainboard,
                "Sideboard": [],
                "AnchorUri": "",
            }

        except Exception as e:
            self.logger.warning(f"Error parsing deck element: {e}")

        return None

    def _extract_date(self, date_str: str) -> str:
        """Extract and normalize date from string"""
        try:
            # Patterns de dates MTGO typiques
            patterns = [
                r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
                r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
                r"(\w+)\s+(\d{1,2}),\s+(\d{4})",  # Month DD, YYYY
            ]

            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    # Normaliser au format YYYY-MM-DD
                    if "/" in date_str:
                        month, day, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    elif "-" in date_str:
                        return match.group(0)

            # Fallback à la date actuelle si pas trouvé
            return datetime.now().strftime("%Y-%m-%d")

        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def _extract_format_from_url(self, url: str) -> str:
        """Extract format from URL"""
        if "standard" in url.lower():
            return "Standard"
        elif "modern" in url.lower():
            return "Modern"
        elif "legacy" in url.lower():
            return "Legacy"
        elif "pioneer" in url.lower():
            return "Pioneer"
        else:
            return "Standard"  # Default

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

    async def _discover_tournament_urls(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[str]:
        """
        DÉCOUVRIR les URLs réelles depuis les pages de listing MTGO
        Reproduit la vraie logique de fbettega/mtg_decklist_scrapper
        """
        discovered_urls = []

        try:
            # 1. Découvrir depuis la page principale des decklists
            main_page_urls = await self._discover_from_main_decklist_page(format_name)
            discovered_urls.extend(main_page_urls)

            # 2. Découvrir depuis les pages spécifiques par format
            format_page_urls = await self._discover_from_format_pages(format_name)
            discovered_urls.extend(format_page_urls)

            # 3. Découvrir depuis les pages de challenges/leagues
            event_page_urls = await self._discover_from_event_pages(format_name)
            discovered_urls.extend(event_page_urls)

            # Filtrer par période et dédupliquer
            filtered_urls = self._filter_urls_by_date_range(
                discovered_urls, start_date, end_date
            )

            self.logger.info(
                f"MTGO Discovery: {len(discovered_urls)} total URLs found, {len(filtered_urls)} in date range"
            )

        except Exception as e:
            self.logger.error(f"Error discovering MTGO tournament URLs: {e}")

        return filtered_urls

    async def _discover_from_main_decklist_page(self, format_name: str) -> List[str]:
        """Découvrir les tournois depuis la page principale des decklists MTGO"""
        urls = []

        try:
            main_url = f"{self.base_url}/decklists"

            async with self.session.get(main_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Chercher tous les liens vers des decklists
                    decklist_links = soup.find_all("a", href=re.compile(r"/decklist/"))

                    for link in decklist_links:
                        href = link.get("href")
                        if href:
                            # Construire l'URL complète
                            if href.startswith("/"):
                                full_url = self.base_url + href
                            else:
                                full_url = href

                            # Filtrer par format si spécifié dans l'URL
                            if format_name.lower() in full_url.lower():
                                urls.append(full_url)

                    self.logger.info(
                        f"Main page discovery: Found {len(urls)} {format_name} tournament URLs"
                    )

        except Exception as e:
            self.logger.warning(f"Error discovering from main decklist page: {e}")

        return urls

    async def _discover_from_format_pages(self, format_name: str) -> List[str]:
        """Découvrir les tournois depuis les pages spécifiques par format"""
        urls = []
        format_lower = format_name.lower()

        # Pages spécifiques par format sur MTGO
        format_pages = [
            f"{self.base_url}/decklists/{format_lower}",
            f"{self.base_url}/decklist/{format_lower}",
            f"{self.base_url}/tournaments/{format_lower}",
        ]

        for page_url in format_pages:
            try:
                async with self.session.get(page_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Chercher les liens de tournois
                        tournament_links = soup.find_all(
                            "a", href=re.compile(r"/decklist/")
                        )

                        for link in tournament_links:
                            href = link.get("href")
                            if href:
                                if href.startswith("/"):
                                    full_url = self.base_url + href
                                else:
                                    full_url = href
                                urls.append(full_url)

            except Exception as e:
                self.logger.warning(
                    f"Error discovering from format page {page_url}: {e}"
                )
                continue

        self.logger.info(f"Format pages discovery: Found {len(urls)} tournament URLs")
        return urls

    async def _discover_from_event_pages(self, format_name: str) -> List[str]:
        """Découvrir les tournois depuis les pages d'événements (challenges, leagues)"""
        urls = []
        format_lower = format_name.lower()

        # Types d'événements MTGO
        event_types = [
            "challenge",
            "league",
            "preliminary",
            "super-qualifier",
            "showcase-challenge",
        ]

        for event_type in event_types:
            try:
                event_url = f"{self.base_url}/decklists/{format_lower}-{event_type}"

                async with self.session.get(event_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Chercher les liens spécifiques aux événements
                        event_links = soup.find_all(
                            "a",
                            href=re.compile(rf"/decklist/{format_lower}-{event_type}"),
                        )

                        for link in event_links:
                            href = link.get("href")
                            if href:
                                if href.startswith("/"):
                                    full_url = self.base_url + href
                                else:
                                    full_url = href
                                urls.append(full_url)

            except Exception as e:
                self.logger.warning(
                    f"Error discovering from event page {event_type}: {e}"
                )
                continue

        self.logger.info(f"Event pages discovery: Found {len(urls)} tournament URLs")
        return urls

    def _filter_urls_by_date_range(
        self, urls: List[str], start_date: str, end_date: str
    ) -> List[str]:
        """Filtrer les URLs par période et dédupliquer"""
        filtered_urls = []
        seen_urls = set()

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        for url in urls:
            # Éviter les doublons
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Extraire la date de l'URL si possible
            url_date = self._extract_date_from_url(url)
            if url_date:
                try:
                    url_dt = datetime.strptime(url_date, "%Y-%m-%d")
                    if start_dt <= url_dt <= end_dt:
                        filtered_urls.append(url)
                except:
                    # Si on ne peut pas parser la date, inclure l'URL quand même
                    filtered_urls.append(url)
            else:
                # Si pas de date trouvée, inclure l'URL
                filtered_urls.append(url)

        return filtered_urls

    async def _discover_tournament_urls(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[str]:
        """
        🚀 NOUVELLE APPROCHE: Découvrir les URLs réelles depuis les pages de listing MTGO
        Au lieu de générer des URLs, on scrape les pages de listing pour trouver les vrais tournois
        """
        discovered_urls = []

        try:
            # Pages de listing MTGO à scraper
            listing_pages = [
                f"{self.base_url}/decklists",
                f"{self.base_url}/decklists/{format_name.lower()}",
                f"{self.base_url}/tournaments",
                f"{self.base_url}/tournaments/{format_name.lower()}",
            ]

            for listing_url in listing_pages:
                try:
                    async with self.session.get(listing_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, "html.parser")

                            # Extraire tous les liens vers des tournois
                            tournament_links = soup.find_all(
                                "a", href=re.compile(r"/decklist/.*")
                            )

                            for link in tournament_links:
                                href = link.get("href")
                                if href:
                                    # Construire l'URL complète
                                    if href.startswith("/"):
                                        full_url = self.base_url + href
                                    else:
                                        full_url = href

                                    # Filtrer par format si possible
                                    if format_name.lower() in full_url.lower():
                                        discovered_urls.append(full_url)

                except Exception as e:
                    self.logger.warning(
                        f"Error scraping listing page {listing_url}: {e}"
                    )
                    continue

            # Dédupliquer les URLs
            discovered_urls = list(set(discovered_urls))

            # Filtrer par date si possible (basé sur l'URL ou le contenu)
            filtered_urls = await self._filter_urls_by_date(
                discovered_urls, start_date, end_date
            )

            self.logger.info(
                f"MTGO Discovery: {len(discovered_urls)} total URLs found, {len(filtered_urls)} after date filtering"
            )

            return filtered_urls

        except Exception as e:
            self.logger.error(f"Error in tournament URL discovery: {e}")
            return []

    async def _filter_urls_by_date(
        self, urls: List[str], start_date: str, end_date: str
    ) -> List[str]:
        """Filtrer les URLs par date basé sur les patterns dans l'URL"""
        filtered_urls = []

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        for url in urls:
            try:
                # Extraire la date de l'URL si possible
                date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", url)
                if date_match:
                    url_date = datetime.strptime(date_match.group(0), "%Y-%m-%d")
                    if start_dt <= url_date <= end_dt:
                        filtered_urls.append(url)
                else:
                    # Si pas de date dans l'URL, inclure par défaut
                    filtered_urls.append(url)

            except Exception:
                # En cas d'erreur, inclure l'URL
                filtered_urls.append(url)

        return filtered_urls

    def _has_valid_standings(self, tournament_data: Dict) -> bool:
        """Vérifier si le tournoi a des standings valides"""
        if not tournament_data:
            return False

        decks = tournament_data.get("decks", [])
        if not decks:
            return False

        # Vérifier qu'au moins un deck a des cartes
        for deck in decks:
            mainboard = deck.get("Mainboard", [])
            if len(mainboard) >= 10:  # Un deck doit avoir au moins 10 cartes
                return True

        return False

    async def _parse_tournament_url(self, url: str) -> Optional[Dict]:
        """Parse a specific tournament URL by extracting JSON data"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()

                    # Extraire les données JSON du tournoi
                    tournament_data = self._extract_json_data(html, url)

                    if tournament_data and len(tournament_data.get("decks", [])) > 0:
                        return tournament_data

        except Exception as e:
            # Ne pas logger chaque URL qui échoue (trop verbeux)
            pass

        return None

    def _extract_json_data(self, html: str, url: str) -> Optional[Dict]:
        """Extract tournament data from embedded JSON"""
        try:
            # Chercher le pattern decklist JSON
            pattern = r"decklist[^=]*=\s*(\{[^;]+\});"
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            if not matches:
                return None

            json_str = matches[0]
            data = json.loads(json_str)

            # Extraire les informations du tournoi
            tournament_info = {
                "id": data.get("event_id", url.split("/")[-1]),
                "name": data.get("description", "Unknown Tournament"),
                "date": self._parse_mtgo_date(data.get("starttime", "")),
                "format": self._normalize_format(data.get("format", "Standard")),
                "type": data.get("type", "Tournament"),
                "url": url,
                "source": "mtgo.com",
            }

            # Extraire et combiner les decks avec les standings
            decks = self._combine_decks_and_standings(
                data.get("decklists", []),
                data.get("standings", []),
                data.get("winloss", []),
            )

            tournament_info["decks"] = decks
            return tournament_info

        except Exception as e:
            self.logger.warning(f"Error extracting JSON data from {url}: {e}")
            return None

    def _parse_mtgo_date(self, date_str: str) -> str:
        """Parse MTGO date format to YYYY-MM-DD"""
        try:
            if date_str:
                # Format: "2024-06-15 02:00:00.0"
                date_part = date_str.split(" ")[0]
                return date_part
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def _normalize_format(self, format_str: str) -> str:
        """Normalize MTGO format to standard format"""
        format_map = {
            "CSTANDARD": "Standard",
            "CMODERN": "Modern",
            "CLEGACY": "Legacy",
            "CPIONEER": "Pioneer",
            "CPAUPER": "Pauper",
            "CVINTAGE": "Vintage",
        }
        return format_map.get(format_str, format_str.replace("C", "").title())

    def _combine_decks_and_standings(
        self, decklists: List[Dict], standings: List[Dict], winloss: List[Dict]
    ) -> List[Dict]:
        """Combine decklists with standings and results"""
        decks = []

        # Créer des maps pour lookup rapide
        standings_map = {s["loginid"]: s for s in standings}
        winloss_map = {w["loginid"]: w for w in winloss}

        for decklist in decklists:
            loginid = decklist.get("loginid")
            player_name = decklist.get("player", "Unknown")

            # Récupérer les standings
            standing = standings_map.get(loginid, {})
            wl = winloss_map.get(loginid, {})

            # Déterminer le résultat
            rank = standing.get("rank", "Unknown")
            wins = wl.get("wins", 0)
            losses = wl.get("losses", 0)

            result = self._format_result(rank, wins, losses)

            # Extraire les cartes
            all_cards = decklist.get("main_deck", [])
            mainboard = self._extract_cards_from_decklist(all_cards, False)
            sideboard = self._extract_cards_from_decklist(all_cards, True)

            # Créer le deck au format standard
            deck = {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": sideboard,
                "AnchorUri": f"#{decklist.get('decktournamentid', '')}",
            }

            decks.append(deck)

        return decks

    def _format_result(self, rank: str, wins: int, losses: int) -> str:
        """Format result string from rank and win/loss"""
        try:
            rank_int = int(rank)
            if rank_int == 1:
                return "1st Place"
            elif rank_int == 2:
                return "2nd Place"
            elif rank_int == 3:
                return "3rd Place"
            elif rank_int <= 8:
                return f"{rank_int}th Place"
            else:
                return f"{wins}-{losses}"
        except:
            return f"{wins}-{losses}" if wins or losses else "Unknown"

    def _extract_cards_from_decklist(
        self, card_list: List[Dict], is_sideboard: bool
    ) -> List[Dict]:
        """Extract cards from MTGO decklist format"""
        cards = []

        for card_data in card_list:
            # Vérifier si c'est un sideboard
            card_sideboard = card_data.get("sideboard", "false").lower() == "true"

            if is_sideboard and not card_sideboard:
                continue
            if not is_sideboard and card_sideboard:
                continue

            card_attrs = card_data.get("card_attributes", {})
            card_name = card_attrs.get("card_name", "Unknown Card")
            count = int(card_data.get("qty", 1))

            cards.append({"CardName": card_name, "Count": count})

        return cards

    def _extract_tournament_info(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Extract tournament information from page"""
        try:
            # Extraire le titre
            title_elem = soup.find("h1") or soup.find("title")
            title = title_elem.get_text().strip() if title_elem else ""

            # Extraire la date
            date_elem = soup.find("time") or soup.find("span", class_="date")
            date_str = date_elem.get_text().strip() if date_elem else ""

            # Extraire le nom du tournoi depuis l'URL si pas trouvé
            if not title:
                url_parts = url.split("/")[-1]
                title = url_parts.replace("-", " ").title()

            return {
                "id": url.split("/")[-1],
                "name": title,
                "date": self._extract_date(date_str)
                if date_str
                else self._extract_date_from_url(url),
                "format": self._extract_format_from_url(url),
                "type": self._extract_type_from_url(url),
                "url": url,
                "source": "mtgo.com",
            }

        except Exception as e:
            self.logger.warning(f"Error extracting tournament info from {url}: {e}")
            return None

    def _extract_decks_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract decks from tournament page"""
        decks = []

        try:
            # Chercher les différents patterns de decks sur MTGO
            deck_patterns = [
                soup.find_all("div", class_="deck-group"),
                soup.find_all("div", class_="deck"),
                soup.find_all("div", class_="decklist"),
                soup.find_all("section", class_="deck"),
            ]

            for pattern in deck_patterns:
                if pattern:
                    for deck_elem in pattern:
                        deck_data = self._parse_deck_element_improved(deck_elem)
                        if deck_data:
                            decks.append(deck_data)
                    break  # Utiliser le premier pattern qui fonctionne

            # Si pas de decks trouvés, essayer une approche plus générale
            if not decks:
                decks = self._extract_decks_fallback(soup)

        except Exception as e:
            self.logger.warning(f"Error extracting decks: {e}")

        return decks

    def _parse_deck_element_improved(self, deck_elem) -> Optional[Dict]:
        """Parse deck element with improved selectors"""
        try:
            # Extraire le joueur
            player_selectors = [
                deck_elem.find("span", class_="player"),
                deck_elem.find("h4"),
                deck_elem.find("h3"),
                deck_elem.find("strong"),
            ]

            player_name = "Unknown"
            for selector in player_selectors:
                if selector:
                    player_name = selector.get_text().strip()
                    break

            # Extraire le résultat
            result_selectors = [
                deck_elem.find("span", class_="record"),
                deck_elem.find("span", class_="result"),
                deck_elem.find("div", class_="placement"),
            ]

            result = "Unknown"
            for selector in result_selectors:
                if selector:
                    result = selector.get_text().strip()
                    break

            # Extraire les cartes
            mainboard = self._extract_cards_from_element(deck_elem, "mainboard")
            sideboard = self._extract_cards_from_element(deck_elem, "sideboard")

            # Valider qu'on a au moins quelques cartes
            if len(mainboard) < 10:  # Un deck doit avoir au moins 10 cartes
                return None

            return {
                "Player": player_name,
                "Result": result,
                "Mainboard": mainboard,
                "Sideboard": sideboard,
                "AnchorUri": deck_elem.find("a")["href"] if deck_elem.find("a") else "",
            }

        except Exception as e:
            return None

    def _extract_cards_from_element(self, deck_elem, section_type: str) -> List[Dict]:
        """Extract cards from deck element"""
        cards = []

        try:
            # Chercher les cartes avec différents patterns
            card_patterns = [
                deck_elem.find_all("span", class_="card"),
                deck_elem.find_all("div", class_="card"),
                deck_elem.find_all("li", class_="card"),
            ]

            for pattern in card_patterns:
                if pattern:
                    for card_elem in pattern:
                        card_name = card_elem.get_text().strip()

                        # Chercher le nombre
                        count_elem = (
                            card_elem.find_previous("span", class_="count")
                            or card_elem.find_previous("span", class_="qty")
                            or card_elem.find("span", class_="count")
                        )

                        count = 1
                        if count_elem:
                            try:
                                count = int(count_elem.get_text().strip())
                            except:
                                count = 1

                        if card_name and len(card_name) > 2:  # Nom valide
                            cards.append({"CardName": card_name, "Count": count})
                    break

        except Exception:
            pass

        return cards

    def _extract_decks_fallback(self, soup: BeautifulSoup) -> List[Dict]:
        """Fallback method to extract decks when standard patterns fail"""
        decks = []

        try:
            # Chercher tous les liens vers des decks
            deck_links = soup.find_all("a", href=re.compile(r"#deck_"))

            for link in deck_links:
                player_name = link.get_text().strip()
                if player_name:
                    # Créer un deck minimal
                    deck = {
                        "Player": player_name,
                        "Result": "Unknown",
                        "Mainboard": [],
                        "Sideboard": [],
                        "AnchorUri": link["href"],
                    }
                    decks.append(deck)

        except Exception:
            pass

        return decks

    def _extract_date_from_url(self, url: str) -> str:
        """Extract date from URL pattern"""
        try:
            # Pattern: standard-challenge-32-2025-07-1512802868
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", url)
            if match:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        except:
            pass

        return datetime.now().strftime("%Y-%m-%d")

    def _extract_type_from_url(self, url: str) -> str:
        """Extract tournament type from URL"""
        if "challenge" in url.lower():
            return "Challenge"
        elif "league" in url.lower():
            return "League"
        elif "preliminary" in url.lower():
            return "Preliminary"
        elif "qualifier" in url.lower():
            return "Qualifier"
        else:
            return "Tournament"

    def _has_valid_standings(self, tournament_data: Dict) -> bool:
        """Check if tournament has valid standings"""
        decks = tournament_data.get("decks", [])

        # Vérifier qu'il y a des decks avec des données valides
        valid_decks = 0
        for deck in decks:
            if (
                deck.get("Player", "").strip() and len(deck.get("Mainboard", [])) > 10
            ):  # Au moins 10 cartes
                valid_decks += 1

        return valid_decks > 0
