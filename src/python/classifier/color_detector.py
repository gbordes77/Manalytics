"""
Color Detection System for MTG Archetypes

This module analyzes decklists to determine their color identity
based on the cards they contain, using MTGOFormatData color information.
"""

import json
import logging
import os
from collections import Counter
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class ColorDetector:
    """Détecte les couleurs des archétypes basé sur les cartes des decklists"""

    def __init__(self, mtgo_format_data_path: str = "MTGOFormatData"):
        self.mtgo_format_data_path = mtgo_format_data_path
        self.card_colors = {}
        self.color_overrides = {}
        self._load_color_data()

        # Mapping des couleurs vers les noms de guildes
        self.color_combinations = {
            "W": "Mono White",
            "U": "Mono Blue",
            "B": "Mono Black",
            "R": "Mono Red",
            "G": "Mono Green",
            "WU": "Azorius",
            "WB": "Orzhov",
            "WR": "Boros",
            "WG": "Selesnya",
            "UB": "Dimir",
            "UR": "Izzet",
            "UG": "Simic",
            "BR": "Rakdos",
            "BG": "Golgari",
            "RG": "Gruul",
            "WUB": "Esper",
            "WUR": "Jeskai",
            "WUG": "Bant",
            "WBR": "Mardu",
            "WBG": "Abzan",
            "WRG": "Naya",
            "UBR": "Grixis",
            "UBG": "Sultai",
            "URG": "Temur",
            "BRG": "Jund",
            "WUBR": "Four-Color",
            "WUBG": "Four-Color",
            "WURG": "Four-Color",
            "WBRG": "Four-Color",
            "UBRG": "Four-Color",
            "WUBRG": "Five-Color",
        }

    def _load_color_data(self):
        """Charge les données de couleurs depuis MTGOFormatData"""
        try:
            # Charger les couleurs principales
            colors_file = os.path.join(
                self.mtgo_format_data_path, "Formats", "card_colors.json"
            )
            if os.path.exists(colors_file):
                with open(colors_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Extraire les couleurs de toutes les catégories
                for category in data:
                    if isinstance(data[category], list):
                        for card in data[category]:
                            if "Name" in card and "Color" in card:
                                self.card_colors[card["Name"]] = card["Color"]

                logger.info(
                    f"✅ Loaded {len(self.card_colors)} card colors from MTGOFormatData"
                )

            # Charger les overrides par format
            self._load_format_overrides("Standard")

        except Exception as e:
            logger.error(f"❌ Error loading color data: {e}")
            # Fallback: couleurs de base
            self.card_colors = {
                # Lands de base
                "Plains": "W",
                "Island": "U",
                "Swamp": "B",
                "Mountain": "R",
                "Forest": "G",
            }

    def _load_format_overrides(self, format_name: str):
        """Charge les overrides de couleur pour un format spécifique"""
        try:
            overrides_file = os.path.join(
                self.mtgo_format_data_path,
                "Formats",
                format_name,
                "color_overrides.json",
            )
            if os.path.exists(overrides_file):
                with open(overrides_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parse la structure {"Lands": [...], "NonLands": [...]}
                override_count = 0

                # Traiter les Lands
                if "Lands" in data and data["Lands"]:
                    for card in data["Lands"]:
                        if "Name" in card and "Color" in card:
                            self.card_colors[card["Name"]] = card["Color"]
                            override_count += 1

                # Traiter les NonLands
                if "NonLands" in data and data["NonLands"]:
                    for card in data["NonLands"]:
                        if "Name" in card and "Color" in card:
                            self.card_colors[card["Name"]] = card["Color"]
                            override_count += 1

                logger.info(
                    f"✅ Loaded {override_count} color overrides for {format_name}"
                )

        except Exception as e:
            logger.error(f"❌ Error loading color overrides for {format_name}: {e}")

    def get_card_color(self, card_name: str) -> str:
        """Obtient la couleur d'une carte"""
        # Les overrides sont déjà intégrés dans card_colors
        if card_name in self.card_colors:
            return self.card_colors[card_name]

        # Pas de couleur trouvée - probablement un artefact ou incolore
        return ""

    def analyze_decklist_colors(self, mainboard: List[Dict]) -> Dict:
        """Analyse les couleurs d'une decklist"""
        color_counts = Counter()
        total_colored_cards = 0

        for card in mainboard:
            # Support both formats: {"Name": "...", "Quantity": ...} and {"CardName": "...", "Count": ...}
            card_name = card.get("Name", card.get("CardName", ""))
            quantity = card.get("Quantity", card.get("Count", 1))

            card_color = self.get_card_color(card_name)

            if card_color:  # Si la carte a une couleur
                # Compter chaque couleur individuellement
                for color in card_color:
                    if color in "WUBRG":
                        color_counts[color] += quantity
                        total_colored_cards += quantity

        # Déterminer l'identité de couleur
        if total_colored_cards == 0:
            return {
                "identity": "",
                "guild_name": "Colorless",
                "colors": [],
                "color_distribution": {},
                "dominant_colors": [],
            }

        # Calculer la distribution en pourcentage
        color_distribution = {
            color: (count / total_colored_cards) * 100
            for color, count in color_counts.items()
        }

        # Déterminer les couleurs dominantes (>10% des cartes colorées)
        dominant_colors = [
            color for color, percentage in color_distribution.items() if percentage > 10
        ]

        # Créer l'identité de couleur (couleurs triées)
        identity = "".join(sorted(dominant_colors, key=lambda x: "WUBRG".index(x)))

        # Obtenir le nom de la guilde/combinaison
        guild_name = self.color_combinations.get(
            identity, f"{len(dominant_colors)}-Color"
        )

        return {
            "identity": identity,
            "guild_name": guild_name,
            "colors": dominant_colors,
            "color_distribution": color_distribution,
            "dominant_colors": dominant_colors,
            "total_colored_cards": total_colored_cards,
        }

    def get_archetype_color_identity(
        self, archetype_name: str, color_analysis: Dict
    ) -> str:
        """Génère le nom d'archétype avec identité de couleur"""
        guild_name = color_analysis["guild_name"]

        # Si l'archétype contient déjà une couleur, ne pas la dupliquer
        archetype_lower = archetype_name.lower()
        guild_lower = guild_name.lower()

        # Vérifier si l'archétype contient déjà une référence de couleur
        color_words = [
            "mono",
            "white",
            "blue",
            "black",
            "red",
            "green",
            "azorius",
            "dimir",
            "rakdos",
            "gruul",
            "selesnya",
            "orzhov",
            "golgari",
            "simic",
            "izzet",
            "boros",
            "esper",
            "jeskai",
            "bant",
            "mardu",
            "abzan",
            "naya",
            "grixis",
            "sultai",
            "temur",
            "jund",
        ]

        has_color_reference = any(word in archetype_lower for word in color_words)

        if has_color_reference:
            return archetype_name
        else:
            return f"{guild_name} {archetype_name}"

    def get_color_css_class(self, color_identity: str) -> str:
        """Retourne la classe CSS pour une identité de couleur"""
        color_classes = {
            "W": "color-white",
            "U": "color-blue",
            "B": "color-black",
            "R": "color-red",
            "G": "color-green",
            "WU": "color-azorius",
            "WB": "color-orzhov",
            "WR": "color-boros",
            "WG": "color-selesnya",
            "UB": "color-dimir",
            "UR": "color-izzet",
            "UG": "color-simic",
            "BR": "color-rakdos",
            "BG": "color-golgari",
            "RG": "color-gruul",
        }

        return color_classes.get(color_identity, "color-colorless")

    def get_color_symbols_html(self, color_identity: str) -> str:
        """Génère les symboles HTML pour une identité de couleur"""
        if not color_identity:
            return '<span class="mana-symbol mana-c">C</span>'

        symbols = []
        for color in color_identity:
            if color in "WUBRG":
                symbols.append(
                    f'<span class="mana-symbol mana-{color.lower()}">{color}</span>'
                )

        return "".join(symbols)
