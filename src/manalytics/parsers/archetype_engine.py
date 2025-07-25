import json
import logging
from typing import Dict, List, Tuple, Any
from collections import defaultdict

from config.settings import settings
from src.parsers.color_identity import ColorIdentityParser
from src.utils.card_utils import normalize_card_name
from database.db_pool import get_db_connection

logger = logging.getLogger(__name__)

class ArchetypeEngine:
    """Identifies deck archetypes using rules from the database with full logic."""

    def __init__(self):
        self.rules = self._load_rules_from_db()
        self.color_parser = ColorIdentityParser()

    def _load_rules_from_db(self) -> Dict[str, Dict[str, Any]]:
        rules_by_format = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT f.name as format, a.name as archetype, r.rule_type, r.rule_data
                        FROM archetype_rules r
                        JOIN archetypes a ON r.archetype_id = a.id
                        JOIN formats f ON a.format_id = f.id
                        WHERE r.active = true ORDER BY f.name, a.name, r.priority DESC;
                    """
                    cursor.execute(query)
                    for row in cursor.fetchall():
                        format_name, archetype_name, rule_type, rule_data = row
                        rules_by_format[format_name][archetype_name][rule_type].append(rule_data)
            logger.info("Successfully loaded archetype rules from database.")
        except Exception as e:
            logger.critical(f"Database error while loading rules: {e}")
        return rules_by_format

    def identify_archetype(self, decklist: List[Dict[str, Any]], format_name: str) -> Tuple[str, str, float]:
        if format_name not in self.rules:
            return "Unknown", "no_rules_for_format", 0.0

        cards = {normalize_card_name(card["name"]): card["quantity"] for card in decklist}
        
        archetype, confidence = self._apply_rules(cards, format_name)
        if archetype != "Unknown":
            return archetype, "rules", confidence
        
        archetype, confidence = self._apply_fallbacks(cards, format_name)
        if archetype != "Unknown":
            return archetype, "fallback", confidence
        
        colors = self.color_parser.get_deck_colors(cards)
        color_name = self.color_parser.get_color_identity_name(colors)
        return f"{color_name} Deck", "colors", 0.3

    def _apply_rules(self, cards: Dict[str, int], format_name: str) -> Tuple[str, float]:
        best_match = ("Unknown", 0.0)
        for archetype_name, rules in self.rules[format_name].items():
            if 'contains' in rules:
                contains_rules = [item for sublist in rules['contains'] for item in sublist]
                if not all(normalize_card_name(card) in cards for card in contains_rules):
                    continue

            score = self._calculate_archetype_score(cards, rules)
            if score > best_match[1]:
                best_match = (archetype_name, score)
        
        if best_match[1] >= 0.7:
            return best_match
        return "Unknown", 0.0

    def _calculate_archetype_score(self, cards: Dict[str, int], rules: Dict[str, List[Any]]) -> float:
        score, total_conditions = 0.0, 0
        
        if 'conditions' in rules:
            all_conditions = [item for sublist in rules['conditions'] for item in sublist]
            if not all_conditions: return 0.0

            for condition in all_conditions:
                total_conditions += 1
                if self._check_condition(cards, condition):
                    score += 1
            
            return score / total_conditions if total_conditions > 0 else 0.0
        return 1.0

    def _check_condition(self, cards: Dict[str, int], condition: Dict) -> bool:
        cond_type = condition.get("type")
        cond_cards = [normalize_card_name(c) for c in condition.get("cards", [])]

        if cond_type == "at_least":
            return any(cards.get(c, 0) >= condition["count"] for c in cond_cards)
        if cond_type == "total_count":
            return sum(cards.get(c, 0) for c in cond_cards) >= condition["min"]
        if cond_type == "color_identity":
            return set(condition["colors"]) == self.color_parser.get_deck_colors(cards)
        if cond_type == "does_not_contain":
             return not any(c in cards for c in cond_cards)
        
        return False

    def _apply_fallbacks(self, cards: Dict[str, int], format_name: str) -> Tuple[str, float]:
        best_match = ("Unknown", 0.0)
        for archetype_name, rules in self.rules[format_name].items():
            if "Fallbacks" in rules:
                for fallback_list in rules["Fallbacks"]:
                    for fallback in fallback_list:
                        common_cards = [normalize_card_name(c) for c in fallback.get("common_cards", [])]
                        if not common_cards: continue
                        
                        overlap = sum(1 for card in common_cards if card in cards)
                        overlap_ratio = overlap / len(common_cards)
                        
                        if overlap_ratio >= 0.4 and overlap_ratio > best_match[1]:
                            best_match = (fallback["name"], overlap_ratio)
        return best_match