from typing import Dict, Set

class ColorIdentityParser:
    """Parses and identifies deck color identity."""

    def __init__(self):
        self.color_mappings = {
            "W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green",
            "WU": "Azorius", "UB": "Dimir", "BR": "Rakdos", "RG": "Gruul",
            "GW": "Selesnya", "WB": "Orzhov", "UR": "Izzet", "BG": "Golgari",
            "RW": "Boros", "GU": "Simic", "WUBRG": "Five-Color"
        }
        self.dual_lands = {
            "hallowed fountain": ["W", "U"], "watery grave": ["U", "B"],
            "blood crypt": ["B", "R"], "stomping ground": ["R", "G"],
            "temple garden": ["G", "W"], "godless shrine": ["W", "B"],
            "steam vents": ["U", "R"], "overgrown tomb": ["B", "G"],
            "sacred foundry": ["R", "W"], "breeding pool": ["G", "U"]
        }

    def get_deck_colors(self, cards: Dict[str, int]) -> Set[str]:
        colors = set()
        for card_name in cards.keys():
            if card_name in self.dual_lands:
                colors.update(self.dual_lands[card_name])
            elif "plains" in card_name: colors.add("W")
            elif "island" in card_name: colors.add("U")
            elif "swamp" in card_name: colors.add("B")
            elif "mountain" in card_name: colors.add("R")
            elif "forest" in card_name: colors.add("G")
        return colors

    def get_color_identity_name(self, colors: Set[str]) -> str:
        if not colors:
            return "Colorless"
        color_order = ["W", "U", "B", "R", "G"]
        sorted_colors = sorted(list(colors), key=lambda c: color_order.index(c))
        color_string = "".join(sorted_colors)
        return self.color_mappings.get(color_string, f"{len(colors)}-Color")