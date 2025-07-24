import re
from typing import List, Dict, Tuple

class DecklistParser:
    """Parses and validates decklists from text format."""

    def __init__(self):
        self.sideboard_markers = ['sideboard', 'sb', '//sideboard']

    def parse(self, decklist_text: str) -> Tuple[List[Dict[str, any]], List[Dict[str, any]]]:
        mainboard, sideboard = [], []
        is_sideboard = False
        lines = decklist_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            if any(marker in line.lower() for marker in self.sideboard_markers):
                is_sideboard = True
                continue
            match = re.match(r'^(\d+)x?\s+(.+)', line)
            if match:
                card_entry = {"quantity": int(match.group(1)), "name": match.group(2).strip()}
                if is_sideboard:
                    sideboard.append(card_entry)
                else:
                    mainboard.append(card_entry)
        return mainboard, sideboard

    def validate_decklist(self, mainboard: List[Dict], sideboard: List[Dict]) -> Tuple[bool, List[str]]:
        errors = []
        mainboard_count = sum(c['quantity'] for c in mainboard)
        sideboard_count = sum(c['quantity'] for c in sideboard)

        if mainboard_count < 60:
            errors.append(f"Mainboard has only {mainboard_count} cards (min 60).")
        
        if sideboard_count > 15:
            errors.append(f"Sideboard has {sideboard_count} cards (max 15).")

        return not errors, errors