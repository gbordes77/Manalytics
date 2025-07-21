"""
MTGO Archetype Parser

Reproduit la logique du MTGOArchetypeParser original de Badaro
github.com/Badaro/MTGOArchetypeParser

Ce module applique des règles d'archétypes depuis MTGOFormatData
pour classifier automatiquement les decklists.
"""

import json
import logging
import os
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ArchetypeCondition:
    """Représente une condition d'archétype"""

    def __init__(self, condition_type: str, cards: List[str]):
        self.type = condition_type
        self.cards = [card.lower() for card in cards]  # Normaliser en minuscules

    def matches(self, mainboard: List[str], sideboard: List[str]) -> bool:
        """Vérifie si la condition est satisfaite"""
        mainboard_lower = [card.lower() for card in mainboard]
        sideboard_lower = [card.lower() for card in sideboard]
        all_cards_lower = mainboard_lower + sideboard_lower

        if self.type == "InMainboard":
            return all(card in mainboard_lower for card in self.cards)
        elif self.type == "InSideboard":
            return all(card in sideboard_lower for card in self.cards)
        elif self.type == "InMainOrSideboard":
            return all(card in all_cards_lower for card in self.cards)
        elif self.type == "OneOrMoreInMainboard":
            return any(card in mainboard_lower for card in self.cards)
        elif self.type == "OneOrMoreInSideboard":
            return any(card in sideboard_lower for card in self.cards)
        elif self.type == "OneOrMoreInMainOrSideboard":
            return any(card in all_cards_lower for card in self.cards)
        elif self.type == "TwoOrMoreInMainboard":
            count = sum(1 for card in self.cards if card in mainboard_lower)
            return count >= 2
        elif self.type == "twoormoreinmainboard":
            count = sum(1 for card in self.cards if card in mainboard_lower)
            return count >= 2
        elif self.type == "TwoOrMoreInSideboard":
            count = sum(1 for card in self.cards if card in sideboard_lower)
            return count >= 2
        elif self.type == "twoormoreinsideboard":
            count = sum(1 for card in self.cards if card in sideboard_lower)
            return count >= 2
        elif self.type == "TwoOrMoreInMainOrSideboard":
            count = sum(1 for card in self.cards if card in all_cards_lower)
            return count >= 2
        elif self.type == "twoormoreinmainorsideboard":
            count = sum(1 for card in self.cards if card in all_cards_lower)
            return count >= 2
        elif self.type == "DoesNotContain":
            return not any(card in all_cards_lower for card in self.cards)
        elif self.type == "DoesNotContainMainboard":
            return not any(card in mainboard_lower for card in self.cards)
        elif self.type == "DoesNotContainSideboard":
            return not any(card in sideboard_lower for card in self.cards)
        else:
            logger.warning(f"Unknown condition type: {self.type}")
            return False


class ArchetypeVariant:
    """Représente une variante d'archétype"""

    def __init__(self, data: Dict):
        self.name = data.get("Name", "")
        self.include_color_in_name = data.get("IncludeColorInName", False)
        self.conditions = [
            ArchetypeCondition(cond["Type"], cond["Cards"])
            for cond in data.get("Conditions", [])
        ]

    def matches(self, mainboard: List[str], sideboard: List[str]) -> bool:
        """Vérifie si toutes les conditions sont satisfaites"""
        return all(cond.matches(mainboard, sideboard) for cond in self.conditions)


class ArchetypeDefinition:
    """Représente une définition d'archétype complète"""

    def __init__(self, data: Dict):
        self.name = data.get("Name", "")
        self.include_color_in_name = data.get("IncludeColorInName", False)
        self.conditions = [
            ArchetypeCondition(cond["Type"], cond["Cards"])
            for cond in data.get("Conditions", [])
        ]
        self.variants = [
            ArchetypeVariant(variant) for variant in data.get("Variants", [])
        ]

    def matches(self, mainboard: List[str], sideboard: List[str]) -> Optional[str]:
        """
        Vérifie si le deck correspond à cet archétype
        Retourne le nom de l'archétype (ou variant) si match, None sinon
        """
        # Vérifier d'abord les conditions principales
        if not all(cond.matches(mainboard, sideboard) for cond in self.conditions):
            return None

        # Vérifier les variants
        for variant in self.variants:
            if variant.matches(mainboard, sideboard):
                return f"{self.name} {variant.name}".strip()

        # Aucun variant trouvé, retourner l'archétype principal
        return self.name


class FallbackDefinition:
    """Représente une définition de fallback (pile)"""

    def __init__(self, data: Dict):
        self.name = data.get("Name", "")
        self.include_color_in_name = data.get("IncludeColorInName", False)
        self.common_cards = [card.lower() for card in data.get("CommonCards", [])]

    def calculate_score(self, mainboard: List[str], sideboard: List[str]) -> float:
        """
        Calcule le score de correspondance avec ce fallback
        Retourne le pourcentage de cartes communes trouvées
        """
        all_cards_lower = [card.lower() for card in mainboard + sideboard]
        unique_cards = set(all_cards_lower)

        if not self.common_cards:
            return 0.0

        # Compter les cartes communes trouvées
        matches = sum(1 for card in self.common_cards if card in unique_cards)
        score = (matches / len(self.common_cards)) * 100

        return score


class MTGOArchetypeParser:
    """
    Parser d'archétypes MTGO basé sur les règles MTGOFormatData
    Reproduit la logique de github.com/Badaro/MTGOArchetypeParser
    """

    def __init__(self, mtgo_format_data_path: str = "MTGOFormatData"):
        self.mtgo_format_data_path = mtgo_format_data_path
        self.archetypes = {}  # {format: [ArchetypeDefinition]}
        self.fallbacks = {}  # {format: [FallbackDefinition]}
        self.loaded_formats = set()

        logger.info("MTGOArchetypeParser initialized")

    def load_format(self, format_name: str):
        """Charge les définitions d'archétypes et fallbacks pour un format"""
        if format_name in self.loaded_formats:
            return

        try:
            format_path = os.path.join(
                self.mtgo_format_data_path, "Formats", format_name
            )

            if not os.path.exists(format_path):
                logger.warning(f"Format path not found: {format_path}")
                return

            # Charger les archétypes
            archetypes_path = os.path.join(format_path, "Archetypes")
            self.archetypes[format_name] = []

            if os.path.exists(archetypes_path):
                for filename in os.listdir(archetypes_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(archetypes_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                archetype = ArchetypeDefinition(data)
                                self.archetypes[format_name].append(archetype)
                        except Exception as e:
                            logger.error(f"Error loading archetype {filename}: {e}")

            # Charger les fallbacks
            fallbacks_path = os.path.join(format_path, "Fallbacks")
            self.fallbacks[format_name] = []

            if os.path.exists(fallbacks_path):
                for filename in os.listdir(fallbacks_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(fallbacks_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                fallback = FallbackDefinition(data)
                                self.fallbacks[format_name].append(fallback)
                        except Exception as e:
                            logger.error(f"Error loading fallback {filename}: {e}")

            self.loaded_formats.add(format_name)

            archetype_count = len(self.archetypes.get(format_name, []))
            fallback_count = len(self.fallbacks.get(format_name, []))

            logger.info(
                f"✅ Loaded {archetype_count} archetypes and {fallback_count} fallbacks for {format_name}"
            )

        except Exception as e:
            logger.error(f"Error loading format {format_name}: {e}")

    def _extract_card_names(self, decklist: List[Dict]) -> List[str]:
        """Extrait les noms de cartes d'une decklist"""
        card_names = []
        for card in decklist:
            # Support des formats: {"Name": "...", "Quantity": ...} et {"CardName": "...", "Count": ...}
            card_name = card.get("Name", card.get("CardName", ""))
            if card_name:
                card_names.append(card_name)
        return card_names

    def classify_deck(
        self,
        format_name: str,
        mainboard: List[Dict],
        sideboard: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Classifie un deck selon les règles d'archétypes

        Args:
            format_name: Le format (Standard, Modern, etc.)
            mainboard: Liste des cartes du mainboard
            sideboard: Liste des cartes du sideboard (optionnel)

        Returns:
            Dict avec les clés: archetype, confidence, method, variants
        """
        if sideboard is None:
            sideboard = []

        # Charger le format si nécessaire
        self.load_format(format_name)

        # Extraire les noms de cartes
        mainboard_names = self._extract_card_names(mainboard)
        sideboard_names = self._extract_card_names(sideboard)

        # Essayer les archétypes principaux
        for archetype in self.archetypes.get(format_name, []):
            result = archetype.matches(mainboard_names, sideboard_names)
            if result:
                return {
                    "archetype": result,
                    "confidence": 1.0,
                    "method": "archetype_rules",
                    "variants": [],
                    "original_name": archetype.name,
                    "include_color_in_name": archetype.include_color_in_name,
                }

        # Si aucun archétype ne correspond, essayer les fallbacks
        best_fallback = None
        best_score = 0.0

        for fallback in self.fallbacks.get(format_name, []):
            score = fallback.calculate_score(mainboard_names, sideboard_names)
            if score > best_score and score >= 10.0:  # Seuil minimum de 10%
                best_score = score
                best_fallback = fallback

        if best_fallback:
            return {
                "archetype": best_fallback.name,
                "confidence": best_score / 100.0,
                "method": "fallback_rules",
                "variants": [],
                "original_name": best_fallback.name,
                "include_color_in_name": best_fallback.include_color_in_name,
            }

        # Aucune classification trouvée
        return {
            "archetype": "Unknown",
            "confidence": 0.0,
            "method": "none",
            "variants": [],
            "original_name": "Unknown",
            "include_color_in_name": False,
        }

    def get_available_formats(self) -> List[str]:
        """Retourne la liste des formats disponibles"""
        formats_path = os.path.join(self.mtgo_format_data_path, "Formats")
        if not os.path.exists(formats_path):
            return []

        formats = []
        for item in os.listdir(formats_path):
            item_path = os.path.join(formats_path, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                # Vérifier que le format a des archétypes ou fallbacks
                archetypes_path = os.path.join(item_path, "Archetypes")
                fallbacks_path = os.path.join(item_path, "Fallbacks")
                if os.path.exists(archetypes_path) or os.path.exists(fallbacks_path):
                    formats.append(item)

        return sorted(formats)

    def get_format_statistics(self, format_name: str) -> Dict:
        """Retourne les statistiques d'un format"""
        self.load_format(format_name)

        archetype_count = len(self.archetypes.get(format_name, []))
        fallback_count = len(self.fallbacks.get(format_name, []))

        return {
            "format": format_name,
            "archetypes": archetype_count,
            "fallbacks": fallback_count,
            "total_rules": archetype_count + fallback_count,
        }
