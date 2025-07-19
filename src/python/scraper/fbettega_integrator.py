"""
Fbettega Integrator - Intégration complète de l'écosystème fbettega/mtg_decklist_scrapper
Reproduction fidèle de l'architecture Jilliac/Fbettega pour plus de tournois
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .fbettega_clients.ManatraderClient import ManatraderClient
from .fbettega_clients.MtgMeleeClientV2 import MtgMeleeClientV2
from .fbettega_clients.MTGOclient import MTGOClient
from .fbettega_clients.TopDeckClient import TopDeckClient


class FbettegaIntegrator:
    """
    Intégrateur principal pour l'écosystème fbettega
    Reproduit l'architecture Jilliac/Fbettega pour maximiser le nombre de tournois
    """

    def __init__(self, cache_folder: str = "data/raw", config: Dict = None):
        self.cache_folder = cache_folder
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialiser les clients selon l'architecture fbettega
        self.clients = {
            "mtgo": MTGOClient(f"{cache_folder}/mtgo", config),
            "melee": MtgMeleeClientV2(f"{cache_folder}/melee", config),
            "topdeck": TopDeckClient(f"{cache_folder}/topdeck", config),
            "manatraders": ManatraderClient(f"{cache_folder}/manatraders", config),
        }

        self.logger.info(
            "Fbettega Integrator initialized with 4 clients (MTGO, Melee, TopDeck, Manatraders)"
        )

    async def fetch_all_tournaments(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Fetch tournaments from all sources according to fbettega architecture
        Période de test : 1-15 juillet 2025
        """
        all_tournaments = []

        self.logger.info(
            f"🚀 Fbettega Integration: Fetching {format_name} tournaments ({start_date} to {end_date})"
        )

        # Paralléliser les appels selon l'architecture fbettega
        tasks = []
        for source_name, client in self.clients.items():
            task = self._fetch_from_source(
                source_name, client, format_name, start_date, end_date
            )
            tasks.append(task)

        # Exécuter tous les scrapers en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Consolider les résultats
        total_tournaments = 0
        for i, result in enumerate(results):
            source_name = list(self.clients.keys())[i]

            if isinstance(result, Exception):
                self.logger.error(f"❌ {source_name}: Error - {result}")
            else:
                tournaments = result or []
                all_tournaments.extend(tournaments)
                total_tournaments += len(tournaments)
                self.logger.info(f"✅ {source_name}: {len(tournaments)} tournaments")

        # Déduplication selon la logique fbettega
        deduplicated_tournaments = self._deduplicate_tournaments(all_tournaments)

        self.logger.info(f"🎯 Fbettega Integration Complete:")
        self.logger.info(f"   - Total sources: {len(self.clients)}")
        self.logger.info(f"   - Raw tournaments: {total_tournaments}")
        self.logger.info(f"   - After deduplication: {len(deduplicated_tournaments)}")

        return deduplicated_tournaments

    async def _fetch_from_source(
        self, source_name: str, client, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch tournaments from a specific source"""
        try:
            async with client:
                tournaments = await client.fetch_tournaments(
                    format_name, start_date, end_date
                )

                # Ajouter métadonnées fbettega
                for tournament in tournaments:
                    tournament["fbettega_source"] = source_name
                    tournament["fbettega_timestamp"] = datetime.now().isoformat()

                return tournaments

        except Exception as e:
            self.logger.error(f"Error fetching from {source_name}: {e}")
            return []

    def _deduplicate_tournaments(self, tournaments: List[Dict]) -> List[Dict]:
        """
        Deduplicate tournaments according to fbettega logic
        Évite les doublons entre sources tout en préservant la diversité
        """
        seen_tournaments = {}
        deduplicated = []

        for tournament in tournaments:
            # Créer une clé unique basée sur le nom, date et format
            key = self._create_tournament_key(tournament)

            if key not in seen_tournaments:
                seen_tournaments[key] = tournament
                deduplicated.append(tournament)
            else:
                # Merger les decks si même tournoi de sources différentes
                existing = seen_tournaments[key]
                merged = self._merge_tournaments(existing, tournament)

                # Remplacer dans la liste
                for i, t in enumerate(deduplicated):
                    if self._create_tournament_key(t) == key:
                        deduplicated[i] = merged
                        break

        return deduplicated

    def _create_tournament_key(self, tournament: Dict) -> str:
        """Create unique key for tournament deduplication"""
        name = tournament.get("name", "").lower().strip()
        date = tournament.get("date", "")
        format_name = tournament.get("format", "").lower()

        # Normaliser le nom pour éviter les variations mineures
        name = name.replace("tournament", "").replace("event", "").strip()

        return f"{format_name}_{date}_{name}"

    def _merge_tournaments(self, tournament1: Dict, tournament2: Dict) -> Dict:
        """Merge two tournaments from different sources"""
        # Prendre le tournoi avec le plus de decks
        if len(tournament2.get("decks", [])) > len(tournament1.get("decks", [])):
            primary = tournament2
            secondary = tournament1
        else:
            primary = tournament1
            secondary = tournament2

        # Merger les decks en évitant les doublons
        merged_decks = list(primary.get("decks", []))

        for deck in secondary.get("decks", []):
            if not self._is_duplicate_deck(deck, merged_decks):
                merged_decks.append(deck)

        # Créer le tournoi mergé
        merged = primary.copy()
        merged["decks"] = merged_decks
        merged["fbettega_sources"] = [
            primary.get("fbettega_source", ""),
            secondary.get("fbettega_source", ""),
        ]

        return merged

    def _is_duplicate_deck(self, deck: Dict, deck_list: List[Dict]) -> bool:
        """Check if deck is duplicate in the list"""
        player = deck.get("Player", "").lower().strip()
        result = deck.get("Result", "")

        for existing_deck in deck_list:
            existing_player = existing_deck.get("Player", "").lower().strip()
            existing_result = existing_deck.get("Result", "")

            if player == existing_player and result == existing_result:
                return True

        return False

    def save_tournaments_cache(
        self, tournaments: List[Dict], format_name: str, start_date: str, end_date: str
    ):
        """Save tournaments to cache according to fbettega structure"""
        try:
            cache_dir = Path(self.cache_folder) / "fbettega_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)

            cache_file = (
                cache_dir / f"{format_name.lower()}_{start_date}_{end_date}.json"
            )

            cache_data = {
                "format": format_name,
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat(),
                "tournament_count": len(tournaments),
                "total_decks": sum(len(t.get("decks", [])) for t in tournaments),
                "sources": list(
                    set(t.get("fbettega_source", "unknown") for t in tournaments)
                ),
                "tournaments": tournaments,
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Fbettega cache saved: {cache_file}")

        except Exception as e:
            self.logger.error(f"Error saving fbettega cache: {e}")

    def load_tournaments_cache(
        self, format_name: str, start_date: str, end_date: str
    ) -> Optional[List[Dict]]:
        """Load tournaments from cache if available"""
        try:
            cache_dir = Path(self.cache_folder) / "fbettega_cache"
            cache_file = (
                cache_dir / f"{format_name.lower()}_{start_date}_{end_date}.json"
            )

            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                # Vérifier si le cache est récent (moins de 24h)
                cache_time = datetime.fromisoformat(cache_data["timestamp"])
                if (datetime.now() - cache_time).total_seconds() < 86400:  # 24h
                    self.logger.info(
                        f"📂 Using fbettega cache: {len(cache_data['tournaments'])} tournaments"
                    )
                    return cache_data["tournaments"]
                else:
                    self.logger.info("📂 Fbettega cache expired, fetching fresh data")

        except Exception as e:
            self.logger.warning(f"Error loading fbettega cache: {e}")

        return None

    async def get_tournaments_with_cache(
        self, format_name: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Get tournaments with intelligent caching"""
        # Essayer le cache d'abord
        cached_tournaments = self.load_tournaments_cache(
            format_name, start_date, end_date
        )
        if cached_tournaments:
            return cached_tournaments

        # Sinon, fetch depuis les sources
        tournaments = await self.fetch_all_tournaments(
            format_name, start_date, end_date
        )

        # Sauvegarder en cache
        self.save_tournaments_cache(tournaments, format_name, start_date, end_date)

        return tournaments
