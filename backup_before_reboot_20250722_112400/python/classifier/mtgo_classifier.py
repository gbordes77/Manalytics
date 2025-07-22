#!/usr/bin/env python3
"""
MTGO Classifier - Intégration simplifiée du moteur MTGOFormatData
Pour utilisation dans le pipeline Manalytics
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class MTGOClassifier:
    """Classificateur simplifié utilisant MTGOFormatData"""

    def __init__(self, format_data_path: str = "MTGOFormatData"):
        self.format_data_path = Path(format_data_path)
        self.logger = logging.getLogger("MTGOClassifier")

        # Charger les règles d'archétypes
        self.archetypes = {}
        self.fallbacks = {}
        self.card_colors = {}

        self.load_format_rules()
        self.load_card_colors()

    def load_format_rules(self):
        """Charge les règles d'archétypes pour tous les formats"""
        try:
            formats_path = self.format_data_path / "Formats"
            if not formats_path.exists():
                self.logger.error(f"Format data path not found: {formats_path}")
                return

            for format_dir in formats_path.iterdir():
                if format_dir.is_dir() and format_dir.name != "Unspecified":
                    format_name = format_dir.name.lower()
                    self.load_format_rules_for_format(format_name, format_dir)

        except Exception as e:
            self.logger.error(f"Failed to load format rules: {e}")

    def load_format_rules_for_format(self, format_name: str, format_path: Path):
        """Charge les règles d'un format spécifique"""
        try:
            self.archetypes[format_name] = {}
            self.fallbacks[format_name] = {}

            # Charger les archétypes
            archetypes_path = format_path / "Archetypes"
            if archetypes_path.exists():
                for archetype_file in archetypes_path.glob("*.json"):
                    try:
                        with open(archetype_file, "r", encoding="utf-8") as f:
                            archetype_data = json.load(f)
                            self.archetypes[format_name][
                                archetype_data["Name"]
                            ] = archetype_data
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to load archetype {archetype_file}: {e}"
                        )

            # Charger les fallbacks
            fallbacks_path = format_path / "Fallbacks"
            if fallbacks_path.exists():
                for fallback_file in fallbacks_path.glob("*.json"):
                    try:
                        with open(fallback_file, "r", encoding="utf-8") as f:
                            fallback_data = json.load(f)
                            self.fallbacks[format_name][
                                fallback_data["Name"]
                            ] = fallback_data
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to load fallback {fallback_file}: {e}"
                        )

            self.logger.info(
                f"Loaded {len(self.archetypes[format_name])} archetypes and {len(self.fallbacks[format_name])} fallbacks for {format_name}"
            )

        except Exception as e:
            self.logger.error(f"Failed to load rules for {format_name}: {e}")

    def load_card_colors(self):
        """Charge les couleurs des cartes"""
        try:
            card_colors_file = self.format_data_path / "Formats" / "card_colors.json"
            if card_colors_file.exists():
                with open(card_colors_file, "r", encoding="utf-8") as f:
                    card_data = json.load(f)

                # Indexer par nom de carte
                for category, cards in card_data.items():
                    for card in cards:
                        name = card.get("Name", "").strip()
                        color = card.get("Color", "")
                        if name and color:
                            self.card_colors[name.lower()] = color

                self.logger.info(f"Loaded {len(self.card_colors)} card colors")
            else:
                self.logger.warning("card_colors.json not found")

        except Exception as e:
            self.logger.error(f"Failed to load card colors: {e}")

    def classify_deck(
        self, mainboard: List[Dict], sideboard: List[Dict], format_name: str
    ) -> str:
        """Classifie un deck selon les règles MTGOFormatData"""
        try:
            format_name = format_name.lower()

            # Extraire les cartes du deck
            mainboard_dict = self.extract_cardlist(mainboard)
            sideboard_dict = self.extract_cardlist(sideboard)

            # Essayer d'abord les archétypes principaux
            archetype = self.match_archetypes(
                mainboard_dict, sideboard_dict, format_name
            )
            if archetype:
                return archetype

            # Essayer les fallbacks
            fallback = self.match_fallbacks(mainboard_dict, sideboard_dict, format_name)
            if fallback:
                return fallback

            # Classification par couleurs si aucun archétype trouvé
            return self.classify_by_colors(mainboard_dict, sideboard_dict)

        except Exception as e:
            self.logger.error(f"Failed to classify deck: {e}")
            return "Unknown"

    def extract_cardlist(self, cards: List[Dict]) -> Dict[str, int]:
        """Extrait une liste de cartes vers un dictionnaire nom -> quantité"""
        cardlist = {}

        for card in cards:
            name = card.get("CardName", card.get("Name", "")).strip()
            count = card.get("Count", 0)

            if name and count > 0:
                # Normaliser le nom de la carte
                normalized_name = self.normalize_card_name(name)
                cardlist[normalized_name] = cardlist.get(normalized_name, 0) + count

        return cardlist

    def normalize_card_name(self, name: str) -> str:
        """Normalise le nom d'une carte pour la correspondance"""
        # Supprimer les caractères spéciaux et normaliser
        normalized = re.sub(r"[^\w\s]", "", name.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def match_archetypes(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str
    ) -> Optional[str]:
        """Essaie de faire correspondre avec les archétypes principaux"""
        archetypes = self.archetypes.get(format_name, {})

        for archetype_name, archetype_data in archetypes.items():
            if self.matches_archetype_conditions(mainboard, sideboard, archetype_data):
                return archetype_name

        return None

    def match_fallbacks(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str
    ) -> Optional[str]:
        """Essaie de faire correspondre avec les fallbacks"""
        fallbacks = self.fallbacks.get(format_name, {})

        for fallback_name, fallback_data in fallbacks.items():
            if self.matches_archetype_conditions(mainboard, sideboard, fallback_data):
                return fallback_name

        return None

    def matches_archetype_conditions(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], archetype_data: Dict
    ) -> bool:
        """Vérifie si un deck correspond aux conditions d'un archétype"""
        try:
            conditions = archetype_data.get("Conditions", [])

            for condition in conditions:
                if not self.evaluate_condition(mainboard, sideboard, condition):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to evaluate archetype conditions: {e}")
            return False

    def evaluate_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition individuelle"""
        try:
            condition_type = condition.get("Type", "").lower()

            if condition_type in ["inmainboard", "contains"]:
                return self.evaluate_contains_condition(mainboard, sideboard, condition)
            elif condition_type in ["doesnotcontain", "excludes"]:
                return self.evaluate_excludes_condition(mainboard, sideboard, condition)
            elif condition_type == "oneormoreinmainboard":
                return self.evaluate_oneormore_condition(
                    mainboard, sideboard, condition
                )
            elif condition_type == "and":
                return self.evaluate_and_condition(mainboard, sideboard, condition)
            elif condition_type == "or":
                return self.evaluate_or_condition(mainboard, sideboard, condition)
            else:
                self.logger.warning(f"Unknown condition type: {condition_type}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to evaluate condition: {e}")
            return False

    def evaluate_contains_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'contains'"""
        cards = condition.get("Cards", [])
        min_count = condition.get("MinCount", 1)
        zones = condition.get("Zones", ["Mainboard", "Sideboard"])

        total_count = 0

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)

            if "Mainboard" in zones:
                total_count += mainboard.get(normalized_name, 0)
            if "Sideboard" in zones:
                total_count += sideboard.get(normalized_name, 0)

        return total_count >= min_count

    def evaluate_oneormore_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'OneOrMoreInMainboard'"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if mainboard.get(normalized_name, 0) > 0:
                return True

        return False

    def evaluate_excludes_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'excludes'"""
        cards = condition.get("Cards", [])
        zones = condition.get("Zones", ["Mainboard", "Sideboard"])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)

            if "Mainboard" in zones and mainboard.get(normalized_name, 0) > 0:
                return False
            if "Sideboard" in zones and sideboard.get(normalized_name, 0) > 0:
                return False

        return True

    def evaluate_and_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'and'"""
        sub_conditions = condition.get("Conditions", [])

        for sub_condition in sub_conditions:
            if not self.evaluate_condition(mainboard, sideboard, sub_condition):
                return False

        return True

    def evaluate_or_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'or'"""
        sub_conditions = condition.get("Conditions", [])

        for sub_condition in sub_conditions:
            if self.evaluate_condition(mainboard, sideboard, sub_condition):
                return True

        return False

    def classify_by_colors(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int]
    ) -> str:
        """Classification par couleurs si aucun archétype trouvé"""
        try:
            # Détecter les couleurs du deck
            colors = set()

            for card_name in mainboard.keys():
                color = self.card_colors.get(card_name, "")
                if color:
                    colors.update(list(color))

            # Classification par nombre de couleurs
            if len(colors) == 1:
                return "Others"  # Monocolor = Others
            elif len(colors) == 2:
                color_pairs = {
                    frozenset(["W", "U"]): "Azorius",
                    frozenset(["W", "B"]): "Orzhov",
                    frozenset(["W", "R"]): "Boros",
                    frozenset(["W", "G"]): "Selesnya",
                    frozenset(["U", "B"]): "Dimir",
                    frozenset(["U", "R"]): "Izzet",
                    frozenset(["U", "G"]): "Simic",
                    frozenset(["B", "R"]): "Rakdos",
                    frozenset(["B", "G"]): "Golgari",
                    frozenset(["R", "G"]): "Gruul",
                }
                return f"{color_pairs.get(frozenset(colors), 'Multicolor')} Deck"
            elif len(colors) == 3:
                color_triples = {
                    frozenset(["W", "U", "B"]): "Esper",
                    frozenset(["W", "U", "R"]): "Jeskai",
                    frozenset(["W", "U", "G"]): "Bant",
                    frozenset(["W", "B", "R"]): "Mardu",
                    frozenset(["W", "B", "G"]): "Abzan",
                    frozenset(["W", "R", "G"]): "Naya",
                    frozenset(["U", "B", "R"]): "Grixis",
                    frozenset(["U", "B", "G"]): "Sultai",
                    frozenset(["U", "R", "G"]): "Temur",
                    frozenset(["B", "R", "G"]): "Jund",
                }
                return f"{color_triples.get(frozenset(colors), 'Three-Color')} Deck"
            else:
                return "Others"

        except Exception as e:
            self.logger.error(f"Failed to classify by colors: {e}")
            return "Others"

    def get_classification_stats(self, format_name: str) -> Dict[str, Any]:
        """Retourne les statistiques de classification"""
        try:
            stats = {
                "total_archetypes": len(self.archetypes.get(format_name, {})),
                "total_fallbacks": len(self.fallbacks.get(format_name, {})),
                "archetype_names": list(self.archetypes.get(format_name, {}).keys()),
                "fallback_names": list(self.fallbacks.get(format_name, {}).keys()),
            }

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get classification stats: {e}")
            return {}
