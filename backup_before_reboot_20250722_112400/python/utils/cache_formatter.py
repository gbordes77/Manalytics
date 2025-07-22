#!/usr/bin/env python3
"""
Cache Formatter - Formatage des données selon MTGODecklistCache
Convertit les données brutes vers le schéma MTGODecklistCache
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MTGODecklistCacheFormatter:
    """Formateur pour le schéma MTGODecklistCache"""

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger("CacheFormatter")

    def format_all_tournaments(self, format_name: str):
        """Formate tous les tournois d'un format"""
        try:
            input_path = Path(self.input_dir)
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Rechercher tous les fichiers JSON
            tournament_files = list(input_path.rglob("*.json"))

            self.logger.info(f"Found {len(tournament_files)} files to format")

            formatted_count = 0
            for tournament_file in tournament_files:
                try:
                    if self.format_tournament_file(tournament_file, format_name):
                        formatted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to format {tournament_file}: {e}")

            self.logger.info(f"Successfully formatted {formatted_count} tournaments")

        except Exception as e:
            self.logger.error(f"Failed to format tournaments: {e}")

    def format_tournament_file(self, tournament_file: Path, format_name: str) -> bool:
        """Formate un fichier de tournoi"""
        try:
            with open(tournament_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # Vérifier si le fichier est déjà au bon format
            if self.is_already_formatted(raw_data):
                self.logger.debug(f"File {tournament_file} already formatted")
                return True

            # Formater selon le schéma MTGODecklistCache
            formatted_data = self.format_tournament_data(raw_data, format_name)

            if formatted_data:
                # Sauvegarder le fichier formaté
                output_file = Path(self.output_dir) / tournament_file.name
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(formatted_data, f, indent=2, ensure_ascii=False)

                return True
            else:
                self.logger.warning(f"Failed to format {tournament_file}")
                return False

        except Exception as e:
            self.logger.error(
                f"Failed to format tournament file {tournament_file}: {e}"
            )
            return False

    def is_already_formatted(self, data: Dict) -> bool:
        """Vérifie si les données sont déjà au format MTGODecklistCache"""
        try:
            # Vérifier la structure de base
            if "Tournament" not in data or "Standings" not in data:
                return False

            # Vérifier la structure Tournament
            tournament = data["Tournament"]
            required_fields = ["ID", "Name", "Date", "Format"]
            if not all(field in tournament for field in required_fields):
                return False

            # Vérifier la structure Standings
            standings = data["Standings"]
            if not isinstance(standings, list) or not standings:
                return False

            # Vérifier un standing
            standing = standings[0]
            required_standing_fields = ["Player", "Rank", "Deck"]
            if not all(field in standing for field in required_standing_fields):
                return False

            return True

        except Exception:
            return False

    def format_tournament_data(
        self, raw_data: Dict, format_name: str
    ) -> Optional[Dict]:
        """Formate les données d'un tournoi selon le schéma MTGODecklistCache"""
        try:
            # Détecter le format source
            source_format = self.detect_source_format(raw_data)

            if source_format == "melee":
                return self.format_from_melee(raw_data, format_name)
            elif source_format == "mtgo":
                return self.format_from_mtgo(raw_data, format_name)
            elif source_format == "mtgtop8":
                return self.format_from_mtgtop8(raw_data, format_name)
            else:
                return self.format_generic(raw_data, format_name)

        except Exception as e:
            self.logger.error(f"Failed to format tournament data: {e}")
            return None

    def detect_source_format(self, data: Dict) -> str:
        """Détecte le format source des données"""
        try:
            # Vérifier les indicateurs de source
            if "tournament" in data and "source" in data.get("tournament", {}):
                source = data["tournament"]["source"].lower()
                if "melee" in source:
                    return "melee"
                elif "mtgo" in source:
                    return "mtgo"
                elif "mtgtop8" in source:
                    return "mtgtop8"

            # Vérifier les structures spécifiques
            if "Tournament" in data and "Source" in data["Tournament"]:
                source = data["Tournament"]["Source"].lower()
                if "melee" in source:
                    return "melee"
                elif "mtgo" in source:
                    return "mtgo"
                elif "mtgtop8" in source:
                    return "mtgtop8"

            # Vérifier les patterns dans les URLs
            if "tournament" in data and "url" in data.get("tournament", {}):
                url = data["tournament"]["url"].lower()
                if "melee.gg" in url:
                    return "melee"
                elif "mtgo.com" in url or "wizards.com" in url:
                    return "mtgo"
                elif "mtgtop8.com" in url:
                    return "mtgtop8"

        except Exception:
            pass

        return "generic"

    def format_from_melee(self, data: Dict, format_name: str) -> Dict:
        """Formate les données depuis Melee.gg"""
        try:
            tournament_info = data.get("tournament", {})

            formatted = {
                "Tournament": {
                    "ID": str(tournament_info.get("id", "")),
                    "Name": tournament_info.get("name", ""),
                    "Date": tournament_info.get("date", datetime.now().isoformat()),
                    "Format": tournament_info.get("format", format_name),
                    "Players": len(data.get("decks", [])),
                    "Rounds": tournament_info.get("rounds", 0),
                    "Type": self.determine_tournament_type(
                        tournament_info.get("name", "")
                    ),
                    "Source": "melee.gg",
                    "URL": tournament_info.get("url", ""),
                },
                "Standings": [],
                "Rounds": [],
            }

            # Formater les standings
            for i, deck in enumerate(data.get("decks", [])):
                standing = {
                    "Player": deck.get("player", ""),
                    "Rank": deck.get("rank", i + 1),
                    "Points": self.calculate_points(deck),
                    "Wins": deck.get("wins", 0),
                    "Losses": deck.get("losses", 0),
                    "Draws": deck.get("draws", 0),
                    "Deck": self.format_deck_data(deck),
                }
                formatted["Standings"].append(standing)

            return formatted

        except Exception as e:
            self.logger.error(f"Failed to format Melee data: {e}")
            return None

    def format_from_mtgo(self, data: Dict, format_name: str) -> Dict:
        """Formate les données depuis MTGO"""
        try:
            tournament_info = data.get("tournament", {})

            formatted = {
                "Tournament": {
                    "ID": str(tournament_info.get("id", "")),
                    "Name": tournament_info.get("name", ""),
                    "Date": tournament_info.get("date", datetime.now().isoformat()),
                    "Format": tournament_info.get("format", format_name),
                    "Players": len(data.get("decks", [])),
                    "Rounds": self.estimate_rounds(len(data.get("decks", []))),
                    "Type": self.determine_tournament_type(
                        tournament_info.get("name", "")
                    ),
                    "Source": "mtgo.com",
                    "URL": tournament_info.get("url", ""),
                },
                "Standings": [],
                "Rounds": [],
            }

            # Formater les standings
            for deck in data.get("decks", []):
                standing = {
                    "Player": deck.get("player", ""),
                    "Rank": deck.get("rank", 0),
                    "Points": self.calculate_points(deck),
                    "Wins": deck.get("wins", 0),
                    "Losses": deck.get("losses", 0),
                    "Draws": deck.get("draws", 0),
                    "Deck": self.format_deck_data(deck),
                }
                formatted["Standings"].append(standing)

            return formatted

        except Exception as e:
            self.logger.error(f"Failed to format MTGO data: {e}")
            return None

    def format_from_mtgtop8(self, data: Dict, format_name: str) -> Dict:
        """Formate les données depuis MTGTop8"""
        try:
            tournament_info = data.get("tournament", {})

            formatted = {
                "Tournament": {
                    "ID": str(tournament_info.get("id", "")),
                    "Name": tournament_info.get("name", ""),
                    "Date": tournament_info.get("date", datetime.now().isoformat()),
                    "Format": tournament_info.get("format", format_name),
                    "Players": len(data.get("decks", [])),
                    "Rounds": self.estimate_rounds(len(data.get("decks", []))),
                    "Type": self.determine_tournament_type(
                        tournament_info.get("name", "")
                    ),
                    "Source": "mtgtop8.com",
                    "URL": tournament_info.get("url", ""),
                },
                "Standings": [],
                "Rounds": [],
            }

            # Formater les standings
            for deck in data.get("decks", []):
                standing = {
                    "Player": deck.get("player", ""),
                    "Rank": deck.get("rank", 0),
                    "Points": self.calculate_points(deck),
                    "Wins": deck.get("wins", 0),
                    "Losses": deck.get("losses", 0),
                    "Draws": deck.get("draws", 0),
                    "Deck": self.format_deck_data(deck),
                }
                formatted["Standings"].append(standing)

            return formatted

        except Exception as e:
            self.logger.error(f"Failed to format MTGTop8 data: {e}")
            return None

    def format_generic(self, data: Dict, format_name: str) -> Dict:
        """Formate les données génériques"""
        try:
            # Essayer d'extraire les informations disponibles
            tournament_info = data.get("tournament", data.get("Tournament", {}))

            formatted = {
                "Tournament": {
                    "ID": str(tournament_info.get("id", tournament_info.get("ID", ""))),
                    "Name": tournament_info.get(
                        "name", tournament_info.get("Name", "")
                    ),
                    "Date": tournament_info.get(
                        "date", tournament_info.get("Date", datetime.now().isoformat())
                    ),
                    "Format": tournament_info.get(
                        "format", tournament_info.get("Format", format_name)
                    ),
                    "Players": len(data.get("decks", data.get("Standings", []))),
                    "Rounds": tournament_info.get(
                        "rounds", tournament_info.get("Rounds", 0)
                    ),
                    "Type": tournament_info.get(
                        "type", tournament_info.get("Type", "Tournament")
                    ),
                    "Source": tournament_info.get(
                        "source", tournament_info.get("Source", "unknown")
                    ),
                    "URL": tournament_info.get("url", tournament_info.get("URL", "")),
                },
                "Standings": [],
                "Rounds": [],
            }

            # Formater les standings
            decks = data.get("decks", [])
            standings = data.get("Standings", [])

            if decks:
                for deck in decks:
                    standing = {
                        "Player": deck.get("player", ""),
                        "Rank": deck.get("rank", 0),
                        "Points": self.calculate_points(deck),
                        "Wins": deck.get("wins", 0),
                        "Losses": deck.get("losses", 0),
                        "Draws": deck.get("draws", 0),
                        "Deck": self.format_deck_data(deck),
                    }
                    formatted["Standings"].append(standing)
            elif standings:
                formatted["Standings"] = standings

            return formatted

        except Exception as e:
            self.logger.error(f"Failed to format generic data: {e}")
            return None

    def format_deck_data(self, deck: Dict) -> Dict:
        """Formate les données d'un deck"""
        try:
            mainboard = []
            sideboard = []

            # Traiter le mainboard
            for card in deck.get("mainboard", []):
                mainboard.append(
                    {
                        "Name": card.get("name", ""),
                        "Count": card.get("count", 0),
                        "IsSideboard": False,
                    }
                )

            # Traiter le sideboard
            for card in deck.get("sideboard", []):
                sideboard.append(
                    {
                        "Name": card.get("name", ""),
                        "Count": card.get("count", 0),
                        "IsSideboard": True,
                    }
                )

            return {
                "Mainboard": mainboard,
                "Sideboard": sideboard,
                "Archetype": deck.get("archetype", "Unknown"),
            }

        except Exception as e:
            self.logger.error(f"Failed to format deck data: {e}")
            return {"Mainboard": [], "Sideboard": [], "Archetype": "Unknown"}

    def determine_tournament_type(self, tournament_name: str) -> str:
        """Détermine le type de tournoi basé sur le nom"""
        try:
            name = tournament_name.lower()

            if "preliminary" in name or "prelim" in name:
                return "Preliminary"
            elif "challenge" in name:
                return "Challenge"
            elif "league" in name:
                return "League"
            elif "ptq" in name or "qualifier" in name:
                return "Qualifier"
            elif "championship" in name or "champ" in name:
                return "Championship"
            elif "grand prix" in name or "gp" in name:
                return "Grand Prix"
            elif "pro tour" in name or "pt" in name:
                return "Pro Tour"
            else:
                return "Tournament"

        except Exception:
            return "Tournament"

    def calculate_points(self, deck: Dict) -> int:
        """Calcule les points basés sur le record"""
        try:
            wins = deck.get("wins", 0)
            draws = deck.get("draws", 0)
            return wins * 3 + draws
        except Exception:
            return 0

    def estimate_rounds(self, num_players: int) -> int:
        """Estime le nombre de rounds basé sur le nombre de joueurs"""
        if num_players <= 8:
            return 3
        elif num_players <= 16:
            return 4
        elif num_players <= 32:
            return 5
        elif num_players <= 64:
            return 6
        elif num_players <= 128:
            return 7
        else:
            return 8
