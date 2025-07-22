#!/usr/bin/env python3
"""
Base Scraper - Reproduction de fbettega/mtg_decklist_scrapper
Architecture modulaire pour scraper Melee.gg, MTGO et autres sources
"""

import asyncio
import json
import logging
import os
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers MTG"""

    def __init__(self, cache_folder: str, api_config: Dict):
        self.cache_folder = cache_folder
        self.api_config = api_config
        self.session = None
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # Configuration par défaut
        self.max_retries = 5
        self.retry_delay = 2
        self.rate_limit_delay = 0.5
        self.concurrent_requests = 10

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Manalytics-Pipeline/1.0"},
        )
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def authenticate(self):
        """Authentification auprès de l'API"""
        pass

    @abstractmethod
    async def fetch_tournament(self, tournament_id: str) -> Optional[Dict]:
        """Récupère les données d'un tournoi"""
        pass

    @abstractmethod
    async def search_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[str]:
        """Recherche les tournois dans une période donnée"""
        pass

    async def fetch_date_range(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Récupère tous les tournois dans une période"""
        self.logger.info(
            f"Scraping {format_name} tournaments from {start_date} to {end_date}"
        )

        async with self:
            # Rechercher les tournois
            tournament_ids = await self.search_tournaments(
                format_name, start_date, end_date
            )
            self.logger.info(f"Found {len(tournament_ids)} tournaments to scrape")

            # Limiter la concurrence
            semaphore = asyncio.Semaphore(self.concurrent_requests)

            # Scraper les tournois en parallèle
            tasks = []
            for tournament_id in tournament_ids:
                task = self._fetch_tournament_with_semaphore(semaphore, tournament_id)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filtrer les résultats valides
            tournaments = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to fetch tournament: {result}")
                elif result:
                    tournaments.append(result)

            self.logger.info(f"Successfully scraped {len(tournaments)} tournaments")
            return tournaments

    async def _fetch_tournament_with_semaphore(
        self, semaphore: asyncio.Semaphore, tournament_id: str
    ) -> Optional[Dict]:
        """Fetch tournament with concurrency control"""
        async with semaphore:
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)

            # Retry logic
            for attempt in range(self.max_retries):
                try:
                    tournament = await self.fetch_tournament(tournament_id)
                    if tournament:
                        await self.save_tournament(tournament)
                        return tournament
                except Exception as e:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for tournament {tournament_id}: {e}"
                    )
                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        delay = self.retry_delay * (2**attempt) + random.uniform(0, 1)
                        await asyncio.sleep(delay)

            self.logger.error(
                f"Failed to fetch tournament {tournament_id} after {self.max_retries} attempts"
            )
            return None

    async def save_tournament(self, tournament: Dict) -> None:
        """Sauvegarde un tournoi selon le format MTGODecklistCache"""
        try:
            # Extraire les métadonnées
            date_str = tournament.get("date", datetime.now().isoformat())
            tournament_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # Créer le chemin selon la structure MTGODecklistCache
            source_name = self.__class__.__name__.lower().replace("scraper", "")
            year = tournament_date.year
            month = tournament_date.month
            day = tournament_date.day

            path = (
                Path(self.cache_folder)
                / "raw"
                / source_name
                / str(year)
                / f"{month:02d}"
                / f"{day:02d}"
            )
            path.mkdir(parents=True, exist_ok=True)

            # Nom du fichier
            tournament_id = tournament.get("id", "unknown")
            filename = f"{tournament.get('name', 'tournament').lower().replace(' ', '-')}-{tournament_id}.json"
            filepath = path / filename

            # Sauvegarder
            async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                await f.write(json.dumps(tournament, indent=2, ensure_ascii=False))

            self.logger.debug(f"Saved tournament to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to save tournament: {e}")

    def format_tournament_data(
        self, tournament_data: Dict, standings: List[Dict]
    ) -> Dict:
        """Formate les données selon le schéma MTGODecklistCache"""

        # Structure de base selon MTGODecklistCache
        formatted = {
            "Tournament": {
                "ID": tournament_data.get("id"),
                "Name": tournament_data.get("name"),
                "Date": tournament_data.get("date"),
                "Format": tournament_data.get("format"),
                "Players": len(standings),
                "Rounds": tournament_data.get("rounds", 0),
                "Type": tournament_data.get("type", "Unknown"),
                "Source": self.__class__.__name__.lower().replace("scraper", ""),
            },
            "Standings": [],
            "Rounds": [],
        }

        # Traiter les classements
        for standing in standings:
            player_data = {
                "Player": standing.get("player", ""),
                "Rank": standing.get("rank", 0),
                "Points": standing.get("points", 0),
                "Wins": standing.get("wins", 0),
                "Losses": standing.get("losses", 0),
                "Draws": standing.get("draws", 0),
                "Deck": self._format_deck(standing.get("deck", {})),
            }
            formatted["Standings"].append(player_data)

        return formatted

    def _format_deck(self, deck_data: Dict) -> Dict:
        """Formate une decklist selon le schéma MTGODecklistCache"""
        return {
            "Mainboard": self._format_cardlist(deck_data.get("mainboard", [])),
            "Sideboard": self._format_cardlist(deck_data.get("sideboard", [])),
            "Archetype": deck_data.get("archetype", "Unknown"),
        }

    def _format_cardlist(self, cards: List[Dict]) -> List[Dict]:
        """Formate une liste de cartes"""
        formatted_cards = []
        for card in cards:
            formatted_cards.append(
                {
                    "Name": card.get("name", ""),
                    "Count": card.get("count", 0),
                    "IsSideboard": card.get("is_sideboard", False),
                }
            )
        return formatted_cards

    async def validate_tournament_data(self, tournament: Dict) -> bool:
        """Valide les données d'un tournoi"""
        required_fields = ["Tournament", "Standings"]

        for field in required_fields:
            if field not in tournament:
                self.logger.warning(f"Missing required field: {field}")
                return False

        # Vérifier que nous avons des standings
        if not tournament.get("Standings"):
            self.logger.warning("No standings data found")
            return False

        # Vérifier que nous avons des decks
        decks_with_cards = 0
        for standing in tournament["Standings"]:
            deck = standing.get("Deck", {})
            if deck.get("Mainboard"):
                decks_with_cards += 1

        if decks_with_cards == 0:
            self.logger.warning("No deck data found")
            return False

        return True
