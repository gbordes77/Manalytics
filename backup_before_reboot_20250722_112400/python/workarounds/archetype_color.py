"""
Archetype Color - Workaround #4 (MOYEN)

Reproduit fidèlement les enum flags C# pour les couleurs d'archétypes
pour préserver 100% la logique de détection des couleurs.

Impact: Préserve 100% la logique de détection des couleurs
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class ArchetypeColor:
    """
    Reproduction fidèle des enum flags C# pour les couleurs

    Le code C# original utilise:
    public enum ArchetypeColor
    {
        C = 0,
        W = 1, U = 2, B = 4, R = 8, G = 16,
        WU = W | U,  // Flags combinés
        WB = W | B,
        // ...
    }

    Cette classe reproduit exactement ce comportement en Python.
    """

    # Couleurs de base (valeurs flags comme en C#)
    C = 0  # Colorless
    W = 1  # White
    U = 2  # Blue
    B = 4  # Black
    R = 8  # Red
    G = 16  # Green

    # Combinaisons à 2 couleurs (guildes)
    WU = W | U  # Azorius
    WB = W | B  # Orzhov
    WR = W | R  # Boros
    WG = W | G  # Selesnya
    UB = U | B  # Dimir
    UR = U | R  # Izzet
    UG = U | G  # Simic
    BR = B | R  # Rakdos
    BG = B | G  # Golgari
    RG = R | G  # Gruul

    # Combinaisons à 3 couleurs (shards et wedges)
    WUB = W | U | B  # Esper
    WUR = W | U | R  # Jeskai
    WUG = W | U | G  # Bant
    WBR = W | B | R  # Mardu
    WBG = W | B | G  # Abzan
    WRG = W | R | G  # Naya
    UBR = U | B | R  # Grixis
    UBG = U | B | G  # Sultai
    URG = U | R | G  # Temur
    BRG = B | R | G  # Jund

    # Combinaisons à 4 couleurs
    WUBR = W | U | B | R
    WUBG = W | U | B | G
    WURG = W | U | R | G
    WBRG = W | B | R | G
    UBRG = U | B | R | G

    # 5 couleurs
    WUBRG = W | U | B | R | G

    # Mapping des noms de guildes (pour compatibilité)
    GUILD_NAMES = {
        WU: "Azorius",
        WB: "Orzhov",
        WR: "Boros",
        WG: "Selesnya",
        UB: "Dimir",
        UR: "Izzet",
        UG: "Simic",
        BR: "Rakdos",
        BG: "Golgari",
        RG: "Gruul",
        WUB: "Esper",
        WUR: "Jeskai",
        WUG: "Bant",
        WBR: "Mardu",
        WBG: "Abzan",
        WRG: "Naya",
        UBR: "Grixis",
        UBG: "Sultai",
        URG: "Temur",
        BRG: "Jund",
        WUBRG: "WUBRG",
        C: "Colorless",
    }

    @classmethod
    def from_string(cls, color_str: str) -> int:
        """
        Convertit une chaîne de couleurs en valeur flags

        Reproduit la logique C# de parsing des couleurs:
        string finalColor = String.Empty;
        if (colorsInLands['W'] > 0 && colorsInNonLands['W'] > 0) finalColor += "W";
        // ...
        return (ArchetypeColor)Enum.Parse(typeof(ArchetypeColor), finalColor);

        Args:
            color_str: Chaîne de couleurs (ex: "WU", "RG", "WUBRG")

        Returns:
            Valeur flags correspondante
        """
        if not color_str or color_str.upper() == "C":
            return cls.C

        result = 0
        color_str = color_str.upper().strip()

        # Conversion caractère par caractère
        for char in color_str:
            if char == "W":
                result |= cls.W
            elif char == "U":
                result |= cls.U
            elif char == "B":
                result |= cls.B
            elif char == "R":
                result |= cls.R
            elif char == "G":
                result |= cls.G

        return result if result > 0 else cls.C

    @classmethod
    def to_string(cls, color_value: int) -> str:
        """
        Convertit une valeur flags en chaîne de couleurs

        Args:
            color_value: Valeur flags

        Returns:
            Chaîne de couleurs (ex: "WU", "RG", "WUBRG")
        """
        if color_value == cls.C:
            return "C"

        colors = []

        # Ordre WUBRG (standard Magic)
        if color_value & cls.W:
            colors.append("W")
        if color_value & cls.U:
            colors.append("U")
        if color_value & cls.B:
            colors.append("B")
        if color_value & cls.R:
            colors.append("R")
        if color_value & cls.G:
            colors.append("G")

        return "".join(colors) if colors else "C"

    @classmethod
    def get_guild_name(cls, color_value: int) -> str:
        """
        Retourne le nom de guilde pour une combinaison de couleurs

        Args:
            color_value: Valeur flags des couleurs

        Returns:
            Nom de la guilde ou chaîne de couleurs si pas de guilde
        """
        return cls.GUILD_NAMES.get(color_value, cls.to_string(color_value))

    @classmethod
    def calculate_colors(
        cls,
        mainboard_cards: List[Dict],
        sideboard_cards: List[Dict],
        land_colors: Dict[str, int],
        card_colors: Dict[str, int],
    ) -> int:
        """
        Calcule les couleurs d'un deck selon la logique C# originale

        Reproduit la logique C#:
        private static ArchetypeColor GetColors(Card[] mainboardCards, Card[] sideboardCards,
                                              Dictionary<string, ArchetypeColor> landColors,
                                              Dictionary<string, ArchetypeColor> cardColors)
        {
            Dictionary<char, int> colorsInLands = new Dictionary<char, int>();
            Dictionary<char, int> colorsInNonLands = new Dictionary<char, int>();

            // Comptage des couleurs dans les terrains et non-terrains
            foreach (var card in mainboardCards.Concat(sideboardCards))
            {
                if (landColors.ContainsKey(card.Name))
                {
                    foreach (var color in landColors[card.Name].ToString())
                    {
                        colorsInLands[color] += card.Count;
                    }
                }
                if (cardColors.ContainsKey(card.Name))
                {
                    foreach (var color in cardColors[card.Name].ToString())
                    {
                        colorsInNonLands[color] += card.Count;
                    }
                }
            }

            string finalColor = String.Empty;
            if (colorsInLands['W'] > 0 && colorsInNonLands['W'] > 0) finalColor += "W";
            if (colorsInLands['U'] > 0 && colorsInNonLands['U'] > 0) finalColor += "U";
            if (colorsInLands['B'] > 0 && colorsInNonLands['B'] > 0) finalColor += "B";
            if (colorsInLands['R'] > 0 && colorsInNonLands['R'] > 0) finalColor += "R";
            if (colorsInLands['G'] > 0 && colorsInNonLands['G'] > 0) finalColor += "G";

            return finalColor.Length > 0 ? (ArchetypeColor)Enum.Parse(typeof(ArchetypeColor), finalColor) : ArchetypeColor.C;
        }

        Args:
            mainboard_cards: Cartes du mainboard
            sideboard_cards: Cartes du sideboard
            land_colors: Dictionnaire des couleurs des terrains
            card_colors: Dictionnaire des couleurs des non-terrains

        Returns:
            Valeur flags des couleurs du deck
        """
        # Initialisation des compteurs (comme en C#)
        colors_in_lands = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0}
        colors_in_non_lands = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0}

        # Traitement de toutes les cartes (mainboard + sideboard)
        all_cards = mainboard_cards + sideboard_cards

        for card in all_cards:
            card_name = card.get("card", card.get("name", ""))
            card_count = card.get("count", 1)

            # Couleurs des terrains
            if card_name in land_colors:
                land_color_value = land_colors[card_name]
                land_color_str = cls.to_string(land_color_value)
                for color_char in land_color_str:
                    if color_char in colors_in_lands:
                        colors_in_lands[color_char] += card_count

            # Couleurs des non-terrains
            if card_name in card_colors:
                card_color_value = card_colors[card_name]
                card_color_str = cls.to_string(card_color_value)
                for color_char in card_color_str:
                    if color_char in colors_in_non_lands:
                        colors_in_non_lands[color_char] += card_count

        # Détermination des couleurs finales (logique C# exacte)
        final_color = ""
        if colors_in_lands["W"] > 0 and colors_in_non_lands["W"] > 0:
            final_color += "W"
        if colors_in_lands["U"] > 0 and colors_in_non_lands["U"] > 0:
            final_color += "U"
        if colors_in_lands["B"] > 0 and colors_in_non_lands["B"] > 0:
            final_color += "B"
        if colors_in_lands["R"] > 0 and colors_in_non_lands["R"] > 0:
            final_color += "R"
        if colors_in_lands["G"] > 0 and colors_in_non_lands["G"] > 0:
            final_color += "G"

        # Conversion en valeur flags
        return cls.from_string(final_color) if final_color else cls.C

    @classmethod
    def has_color(cls, color_value: int, target_color: int) -> bool:
        """
        Vérifie si une combinaison de couleurs contient une couleur spécifique

        Args:
            color_value: Valeur flags des couleurs
            target_color: Couleur cible à vérifier

        Returns:
            True si la couleur est présente, False sinon
        """
        return (color_value & target_color) != 0

    @classmethod
    def get_color_count(cls, color_value: int) -> int:
        """
        Compte le nombre de couleurs dans une combinaison

        Args:
            color_value: Valeur flags des couleurs

        Returns:
            Nombre de couleurs (0-5)
        """
        if color_value == cls.C:
            return 0

        count = 0
        if color_value & cls.W:
            count += 1
        if color_value & cls.U:
            count += 1
        if color_value & cls.B:
            count += 1
        if color_value & cls.R:
            count += 1
        if color_value & cls.G:
            count += 1

        return count

    @classmethod
    def is_multicolor(cls, color_value: int) -> bool:
        """
        Vérifie si une combinaison est multicolore

        Args:
            color_value: Valeur flags des couleurs

        Returns:
            True si multicolore (2+ couleurs), False sinon
        """
        return cls.get_color_count(color_value) >= 2
