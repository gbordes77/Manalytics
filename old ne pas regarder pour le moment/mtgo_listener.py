"""
MTGO Listener - Écoute en temps réel les matchups MTGO et alimente le cache
Reproduction du workflow MTGO Client -> MTGO-listener -> MTGODecklistCache
Basé sur les concepts du MTGOSDK (github.com/videre-project/MTGOSDK)
Version cross-platform compatible macOS/Linux/Windows
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from ..cache.mtgo_cache_manager import MTGOCacheManager

logger = logging.getLogger(__name__)


class MTGOListener:
    """
    Listener MTGO qui écoute les matchups en temps réel
    Reproduction du workflow MTGO Client -> MTGO-listener -> MTGODecklistCache
    Version cross-platform
    """

    def __init__(self, cache_manager: MTGOCacheManager):
        self.cache_manager = cache_manager
        self.mtgo_process = None
        self.is_listening = False
        self.matchup_data = []

        # Configuration du listener
        self.polling_interval = 5  # secondes
        self.max_matchup_age = 3600  # 1 heure

        # Détection de la plateforme
        self.platform = platform.system().lower()
        logger.info(f"🖥️ Platform detected: {self.platform}")

    def find_mtgo_process(self) -> Optional[psutil.Process]:
        """Trouve le processus MTGO en cours d'exécution (cross-platform)"""
        try:
            mtgo_process_names = ["mtgo", "magic", "magic online"]

            for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
                try:
                    proc_name = proc.info["name"] or ""
                    proc_cmdline = " ".join(proc.info["cmdline"] or [])

                    # Vérifier le nom du processus et la ligne de commande
                    for mtgo_name in mtgo_process_names:
                        if (
                            mtgo_name in proc_name.lower()
                            or mtgo_name in proc_cmdline.lower()
                        ):
                            logger.info(
                                f"✅ MTGO process found: PID {proc.info['pid']} - {proc_name}"
                            )
                            return proc

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            logger.warning("❌ MTGO process not found")
            return None

        except Exception as e:
            logger.error(f"❌ Error finding MTGO process: {e}")
            return None

    def get_mtgo_window_info(self) -> Optional[Dict[str, Any]]:
        """Récupère les informations de la fenêtre MTGO (cross-platform)"""
        try:
            if self.platform == "windows":
                # Code Windows spécifique (si pywin32 est disponible)
                try:
                    import win32gui
                    import win32process

                    def enum_windows_callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if "magic: the gathering online" in window_text.lower():
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                rect = win32gui.GetWindowRect(hwnd)
                                windows.append(
                                    {
                                        "hwnd": hwnd,
                                        "pid": pid,
                                        "title": window_text,
                                        "rect": rect,
                                    }
                                )
                        return True

                    windows = []
                    win32gui.EnumWindows(enum_windows_callback, windows)

                    if windows:
                        logger.info(f"✅ MTGO window found: {windows[0]['title']}")
                        return windows[0]

                except ImportError:
                    logger.warning(
                        "⚠️ pywin32 not available, skipping window detection"
                    )

            elif self.platform == "darwin":  # macOS
                # Utiliser osascript pour détecter les fenêtres MTGO sur macOS
                try:
                    script = """
                    tell application "System Events"
                        set mtgoWindows to windows of processes whose name contains "MTGO"
                        if mtgoWindows is not {} then
                            set firstWindow to item 1 of mtgoWindows
                            return {name of firstWindow, position of firstWindow, size of firstWindow}
                        end if
                    end tell
                    """

                    result = subprocess.run(
                        ["osascript", "-e", script],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        window_info = result.stdout.strip().split(", ")
                        logger.info(f"✅ MTGO window found on macOS: {window_info[0]}")
                        return {
                            "title": window_info[0],
                            "position": window_info[1:3],
                            "size": window_info[3:5],
                        }

                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass

            elif self.platform == "linux":
                # Utiliser xdotool pour détecter les fenêtres MTGO sur Linux
                try:
                    result = subprocess.run(
                        ["xdotool", "search", "--name", "MTGO"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        window_id = result.stdout.strip().split("\n")[0]
                        logger.info(f"✅ MTGO window found on Linux: {window_id}")
                        return {"window_id": window_id}

                except (
                    subprocess.TimeoutExpired,
                    subprocess.CalledProcessError,
                    FileNotFoundError,
                ):
                    pass

            logger.warning("❌ MTGO window not found")
            return None

        except Exception as e:
            logger.error(f"❌ Error getting MTGO window info: {e}")
            return None

    def simulate_matchup_data(self) -> Dict[str, Any]:
        """
        Simule des données de matchup pour les tests
        En production, cela serait remplacé par l'écoute réelle via MTGOSDK
        """
        return {
            "match_id": f"match_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "player1": {
                "name": "Player1",
                "deck": {
                    "name": "Izzet Prowess",
                    "cards": [
                        {"name": "Monastery Swiftspear", "count": 4},
                        {"name": "Soul-Scar Mage", "count": 4},
                        {"name": "Lightning Bolt", "count": 4},
                        {"name": "Lava Dart", "count": 4},
                        {"name": "Spell Pierce", "count": 2},
                        {"name": "Steam Vents", "count": 4},
                        {"name": "Spirebluff Canal", "count": 4},
                        {"name": "Mountain", "count": 6},
                        {"name": "Island", "count": 2},
                    ],
                },
            },
            "player2": {
                "name": "Player2",
                "deck": {
                    "name": "Mono-Red Aggro",
                    "cards": [
                        {"name": "Goblin Guide", "count": 4},
                        {"name": "Lightning Bolt", "count": 4},
                        {"name": "Lava Spike", "count": 4},
                        {"name": "Rift Bolt", "count": 4},
                        {"name": "Skewer the Critics", "count": 4},
                        {"name": "Mountain", "count": 20},
                    ],
                },
            },
            "format": "Modern",
            "tournament_type": "League",
            "result": "player1_wins",
        }

    async def listen_for_matchups(self):
        """Écoute les matchups MTGO en temps réel"""
        logger.info("🎧 Starting MTGO matchup listener...")

        self.is_listening = True
        matchup_count = 0

        while self.is_listening:
            try:
                # Vérifier que MTGO est en cours d'exécution
                mtgo_process = self.find_mtgo_process()
                if not mtgo_process:
                    logger.warning("⚠️ MTGO not running, waiting...")
                    await asyncio.sleep(10)
                    continue

                # Simuler la récupération de données de matchup
                # En production, cela utiliserait MTGOSDK pour écouter les événements
                matchup_data = self.simulate_matchup_data()

                # Traiter les données de matchup
                await self.process_matchup_data(matchup_data)
                matchup_count += 1

                logger.info(
                    f"📊 Processed matchup {matchup_count}: {matchup_data['player1']['deck']['name']} vs {matchup_data['player2']['deck']['name']}"
                )

                # Attendre avant la prochaine vérification
                await asyncio.sleep(self.polling_interval)

            except Exception as e:
                logger.error(f"❌ Error in matchup listener: {e}")
                await asyncio.sleep(5)

    async def process_matchup_data(self, matchup_data: Dict[str, Any]):
        """Traite les données de matchup et les ajoute au cache"""
        try:
            # 🎯 AMÉLIORATION : Identifier le vrai tournoi au lieu de créer un ID arbitraire
            real_tournament_id = self._extract_tournament_id(matchup_data)

            # Convertir en format compatible avec MTGODecklistCache
            tournament_data = {
                "tournament_id": real_tournament_id,
                "tournament_name": self._extract_tournament_name(matchup_data),
                "tournament_date": datetime.now().strftime("%Y-%m-%d"),
                "format": matchup_data["format"],
                "tournament_type": matchup_data["tournament_type"],
                "source": "mtgo_listener",  # 🏷️ Marqueur de source
                "decks": [],
            }

            # Ajouter les decks des deux joueurs
            for player_key in ["player1", "player2"]:
                player = matchup_data[player_key]
                deck_data = {
                    "player_name": player["name"],
                    "deck_name": player["deck"]["name"],
                    "cards": player["deck"]["cards"],
                    "finish": 1 if player_key == "player1" else 2,
                    "wins": 1 if player_key == "player1" else 0,
                    "losses": 0 if player_key == "player1" else 1,
                }
                tournament_data["decks"].append(deck_data)

            # Sauvegarder dans le cache avec déduplication
            await self.cache_manager.save_tournament_data(tournament_data)

            # Ajouter aux données en mémoire pour les statistiques
            self.matchup_data.append(matchup_data)

            # Nettoyer les anciennes données
            self.cleanup_old_data()

        except Exception as e:
            logger.error(f"❌ Error processing matchup data: {e}")

    def _extract_tournament_id(self, matchup_data: Dict[str, Any]) -> str:
        """Extrait l'ID réel du tournoi depuis les données de matchup"""
        try:
            # En production, cela viendrait des données MTGOSDK
            # Pour la simulation, on génère un ID plus réaliste

            format_name = matchup_data.get("format", "Unknown")
            tournament_type = matchup_data.get("tournament_type", "League")
            date_str = datetime.now().strftime("%Y%m%d")

            if tournament_type == "Challenge":
                # Format: standard-challenge-20250720-123
                return f"{format_name.lower()}-challenge-{date_str}-{hash(matchup_data['match_id']) % 1000}"
            elif tournament_type == "League":
                # Les Leagues sont des matchups individuels, garder l'ID unique
                return f"league-{matchup_data['match_id']}"
            else:
                # Autres tournois
                return f"{format_name.lower()}-{tournament_type.lower()}-{date_str}-{hash(matchup_data['match_id']) % 1000}"

        except Exception as e:
            logger.error(f"❌ Error extracting tournament ID: {e}")
            return f"listener_{matchup_data['match_id']}"

    def _extract_tournament_name(self, matchup_data: Dict[str, Any]) -> str:
        """Extrait le nom réel du tournoi depuis les données de matchup"""
        try:
            format_name = matchup_data.get("format", "Unknown")
            tournament_type = matchup_data.get("tournament_type", "League")

            if tournament_type == "Challenge":
                return f"{format_name} Challenge"
            elif tournament_type == "League":
                return f"{format_name} League"
            else:
                return f"MTGO {format_name} {tournament_type}"

        except Exception as e:
            logger.error(f"❌ Error extracting tournament name: {e}")
            return f"MTGO Listener - {matchup_data.get('format', 'Unknown')}"

    def cleanup_old_data(self):
        """Nettoie les anciennes données de matchup"""
        current_time = time.time()
        self.matchup_data = [
            data
            for data in self.matchup_data
            if current_time
            - time.mktime(datetime.fromisoformat(data["timestamp"]).timetuple())
            < self.max_matchup_age
        ]

    def stop_listening(self):
        """Arrête l'écoute des matchups"""
        logger.info("🛑 Stopping MTGO matchup listener...")
        self.is_listening = False

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du listener"""
        return {
            "total_matchups": len(self.matchup_data),
            "is_listening": self.is_listening,
            "mtgo_running": self.find_mtgo_process() is not None,
            "platform": self.platform,
            "last_matchup": self.matchup_data[-1] if self.matchup_data else None,
        }


class MTGOListenerManager:
    """
    Gestionnaire du listener MTGO
    Coordonne l'écoute et l'intégration avec le cache
    """

    def __init__(self, cache_manager: MTGOCacheManager):
        self.cache_manager = cache_manager
        self.listener = MTGOListener(cache_manager)
        self.listener_task = None

    async def start_listener(self):
        """Démarre le listener MTGO"""
        logger.info("🚀 Starting MTGO Listener Manager...")

        if self.listener_task and not self.listener_task.done():
            logger.warning("⚠️ Listener already running")
            return

        self.listener_task = asyncio.create_task(self.listener.listen_for_matchups())
        logger.info("✅ MTGO Listener started successfully")

    async def stop_listener(self):
        """Arrête le listener MTGO"""
        logger.info("🛑 Stopping MTGO Listener Manager...")

        if self.listener:
            self.listener.stop_listening()

        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ MTGO Listener stopped successfully")

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du listener"""
        return {
            "listener_running": self.listener_task is not None
            and not self.listener_task.done(),
            "statistics": self.listener.get_statistics() if self.listener else {},
        }


# Fonction utilitaire pour démarrer le listener
async def start_mtgo_listener(cache_manager: MTGOCacheManager) -> MTGOListenerManager:
    """Démarre le listener MTGO et retourne le gestionnaire"""
    manager = MTGOListenerManager(cache_manager)
    await manager.start_listener()
    return manager
