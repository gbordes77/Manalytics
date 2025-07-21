"""
MTGO Cache Manager - Gestionnaire de cache pour les données de matchup MTGO
Gère le stockage et la récupération des données de tournois et matchups
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MTGOCacheManager:
    """
    Gestionnaire de cache pour les données MTGO
    Stocke et récupère les données de tournois et matchups
    """

    def __init__(self, cache_dir: str = "data/cache/mtgo_listener"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Fichiers de cache
        self.tournaments_file = self.cache_dir / "tournaments.json"
        self.matchups_file = self.cache_dir / "matchups.json"
        self.stats_file = self.cache_dir / "stats.json"

        # Initialiser les fichiers s'ils n'existent pas
        self._initialize_cache_files()

        logger.info(f"✅ MTGO Cache Manager initialized: {self.cache_dir}")

    def _initialize_cache_files(self):
        """Initialise les fichiers de cache s'ils n'existent pas"""
        cache_files = [
            (self.tournaments_file, []),
            (self.matchups_file, []),
            (self.stats_file, {}),
        ]

        for file_path, default_data in cache_files:
            if not file_path.exists():
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2, ensure_ascii=False)
                logger.info(f"📁 Created cache file: {file_path}")

    def _load_json_file(self, file_path: Path) -> Any:
        """Charge un fichier JSON avec gestion d'erreur"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Error loading {file_path}: {e}")
            return None

    def _save_json_file(self, file_path: Path, data: Any):
        """Sauvegarde des données dans un fichier JSON avec gestion d'erreur"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.debug(f"💾 Saved data to {file_path}")
        except Exception as e:
            logger.error(f"❌ Error saving to {file_path}: {e}")

    async def save_tournament_data(self, tournament_data: Dict[str, Any]):
        """Sauvegarde les données d'un tournoi avec déduplication intelligente"""
        try:
            # Charger les tournois existants
            tournaments = self._load_json_file(self.tournaments_file) or []

            # 🔍 DÉDUPLICATION INTELLIGENTE
            is_duplicate = self._check_for_duplicates(tournament_data, tournaments)
            if is_duplicate:
                logger.info(
                    f"⚠️ Duplicate tournament detected, skipping: {tournament_data.get('tournament_name', 'Unknown')}"
                )
                return

            # Ajouter le nouveau tournoi
            tournament_data["cached_at"] = datetime.now().isoformat()
            tournaments.append(tournament_data)

            # Sauvegarder
            self._save_json_file(self.tournaments_file, tournaments)

            logger.info(
                f"✅ Saved tournament: {tournament_data.get('tournament_name', 'Unknown')}"
            )

        except Exception as e:
            logger.error(f"❌ Error saving tournament data: {e}")

    async def save_matchup_data(self, matchup_data: Dict[str, Any]):
        """Sauvegarde les données d'un matchup"""
        try:
            # Charger les matchups existants
            matchups = self._load_json_file(self.matchups_file) or []

            # Ajouter le nouveau matchup
            matchup_data["cached_at"] = datetime.now().isoformat()
            matchups.append(matchup_data)

            # Sauvegarder
            self._save_json_file(self.matchups_file, matchups)

            logger.info(f"✅ Saved matchup: {matchup_data.get('match_id', 'Unknown')}")

        except Exception as e:
            logger.error(f"❌ Error saving matchup data: {e}")

    def get_tournaments(
        self,
        format_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Récupère les tournois avec filtres optionnels"""
        try:
            tournaments = self._load_json_file(self.tournaments_file) or []

            # Appliquer les filtres
            if format_name:
                tournaments = [t for t in tournaments if t.get("format") == format_name]

            if start_date:
                tournaments = [
                    t for t in tournaments if t.get("tournament_date", "") >= start_date
                ]

            if end_date:
                tournaments = [
                    t for t in tournaments if t.get("tournament_date", "") <= end_date
                ]

            logger.info(f"📊 Retrieved {len(tournaments)} tournaments")
            return tournaments

        except Exception as e:
            logger.error(f"❌ Error retrieving tournaments: {e}")
            return []

    def get_matchups(
        self,
        format_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Récupère les matchups avec filtres optionnels"""
        try:
            matchups = self._load_json_file(self.matchups_file) or []

            # Appliquer les filtres
            if format_name:
                matchups = [m for m in matchups if m.get("format") == format_name]

            if start_date:
                matchups = [m for m in matchups if m.get("timestamp", "") >= start_date]

            if end_date:
                matchups = [m for m in matchups if m.get("timestamp", "") <= end_date]

            logger.info(f"📊 Retrieved {len(matchups)} matchups")
            return matchups

        except Exception as e:
            logger.error(f"❌ Error retrieving matchups: {e}")
            return []

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache"""
        try:
            tournaments = self._load_json_file(self.tournaments_file) or []
            matchups = self._load_json_file(self.matchups_file) or []

            stats = {
                "total_tournaments": len(tournaments),
                "total_matchups": len(matchups),
                "cache_size_mb": self._get_cache_size_mb(),
                "last_updated": datetime.now().isoformat(),
                "formats": self._get_formats_distribution(tournaments),
                "recent_activity": self._get_recent_activity(tournaments, matchups),
            }

            # Sauvegarder les stats
            self._save_json_file(self.stats_file, stats)

            return stats

        except Exception as e:
            logger.error(f"❌ Error getting cache statistics: {e}")
            return {}

    def _get_cache_size_mb(self) -> float:
        """Calcule la taille du cache en MB"""
        try:
            total_size = 0
            for file_path in [
                self.tournaments_file,
                self.matchups_file,
                self.stats_file,
            ]:
                if file_path.exists():
                    total_size += file_path.stat().st_size

            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0

    def _get_formats_distribution(
        self, tournaments: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calcule la distribution des formats"""
        formats = {}
        for tournament in tournaments:
            format_name = tournament.get("format", "Unknown")
            formats[format_name] = formats.get(format_name, 0) + 1
        return formats

    def _get_recent_activity(
        self, tournaments: List[Dict[str, Any]], matchups: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calcule l'activité récente (dernières 24h)"""
        try:
            now = datetime.now()
            one_day_ago = now.replace(hour=0, minute=0, second=0, microsecond=0)

            recent_tournaments = 0
            recent_matchups = 0

            for tournament in tournaments:
                cached_at = tournament.get("cached_at")
                if cached_at:
                    try:
                        cached_time = datetime.fromisoformat(
                            cached_at.replace("Z", "+00:00")
                        )
                        if cached_time >= one_day_ago:
                            recent_tournaments += 1
                    except:
                        pass

            for matchup in matchups:
                cached_at = matchup.get("cached_at")
                if cached_at:
                    try:
                        cached_time = datetime.fromisoformat(
                            cached_at.replace("Z", "+00:00")
                        )
                        if cached_time >= one_day_ago:
                            recent_matchups += 1
                    except:
                        pass

            return {
                "tournaments_today": recent_tournaments,
                "matchups_today": recent_matchups,
            }

        except Exception:
            return {"tournaments_today": 0, "matchups_today": 0}

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Nettoie le cache (optionnellement par âge)"""
        try:
            if older_than_days is None:
                # Nettoyer tout le cache
                self._initialize_cache_files()
                logger.info("🗑️ Cache cleared completely")
            else:
                # Nettoyer par âge
                cutoff_date = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                cutoff_date = cutoff_date.replace(day=cutoff_date.day - older_than_days)

                # Nettoyer les tournois
                tournaments = self._load_json_file(self.tournaments_file) or []
                filtered_tournaments = []
                for tournament in tournaments:
                    cached_at = tournament.get("cached_at")
                    if cached_at:
                        try:
                            cached_time = datetime.fromisoformat(
                                cached_at.replace("Z", "+00:00")
                            )
                            if cached_time >= cutoff_date:
                                filtered_tournaments.append(tournament)
                        except:
                            filtered_tournaments.append(tournament)

                # Nettoyer les matchups
                matchups = self._load_json_file(self.matchups_file) or []
                filtered_matchups = []
                for matchup in matchups:
                    cached_at = matchup.get("cached_at")
                    if cached_at:
                        try:
                            cached_time = datetime.fromisoformat(
                                cached_at.replace("Z", "+00:00")
                            )
                            if cached_time >= cutoff_date:
                                filtered_matchups.append(matchup)
                        except:
                            filtered_matchups.append(matchup)

                # Sauvegarder les données filtrées
                self._save_json_file(self.tournaments_file, filtered_tournaments)
                self._save_json_file(self.matchups_file, filtered_matchups)

                logger.info(
                    f"🗑️ Cache cleared: removed data older than {older_than_days} days"
                )

        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")

    def export_cache_data(self, output_dir: str) -> bool:
        """Exporte les données du cache vers un répertoire"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Exporter les tournois
            tournaments = self._load_json_file(self.tournaments_file) or []
            tournaments_file = output_path / "mtgo_tournaments.json"
            self._save_json_file(tournaments_file, tournaments)

            # Exporter les matchups
            matchups = self._load_json_file(self.matchups_file) or []
            matchups_file = output_path / "mtgo_matchups.json"
            self._save_json_file(matchups_file, matchups)

            # Exporter les stats
            stats = self.get_cache_statistics()
            stats_file = output_path / "mtgo_cache_stats.json"
            self._save_json_file(stats_file, stats)

            logger.info(f"📤 Cache data exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error exporting cache data: {e}")
            return False

    def _check_for_duplicates(
        self, new_tournament: Dict[str, Any], existing_tournaments: List[Dict[str, Any]]
    ) -> bool:
        """Vérifie les doublons entre scraper et listener"""
        try:
            new_date = new_tournament.get("tournament_date")
            new_format = new_tournament.get("format")
            new_decks = new_tournament.get("decks", [])

            # Extraire les noms des joueurs du nouveau tournoi
            new_players = set()
            for deck in new_decks:
                player_name = deck.get("player_name", "").strip().lower()
                if player_name:
                    new_players.add(player_name)

            # Vérifier contre les tournois existants
            for existing_tournament in existing_tournaments:
                existing_date = existing_tournament.get("tournament_date")
                existing_format = existing_tournament.get("format")
                existing_decks = existing_tournament.get("decks", [])

                # Vérifier date et format
                if new_date == existing_date and new_format == existing_format:
                    # Extraire les joueurs existants
                    existing_players = set()
                    for deck in existing_decks:
                        player_name = deck.get("player_name", "").strip().lower()
                        if player_name:
                            existing_players.add(player_name)

                    # Vérifier chevauchement des joueurs (>= 50% de joueurs communs)
                    if existing_players and new_players:
                        overlap = len(new_players.intersection(existing_players))
                        overlap_percentage = overlap / min(
                            len(new_players), len(existing_players)
                        )

                        if overlap_percentage >= 0.5:  # 50% de joueurs en commun
                            logger.info(
                                f"🔍 Duplicate detected: {overlap_percentage:.1%} player overlap"
                            )
                            return True

            return False

        except Exception as e:
            logger.error(f"❌ Error checking duplicates: {e}")
            return False
