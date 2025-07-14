"""
Advanced Archetype Classifier with Color Integration
Based on Aliquanto3's R-Meta-Analysis ecosystem
"""

import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd


class AdvancedArchetypeClassifier:
    """
    Advanced classifier that integrates colors with archetype names
    to improve classification accuracy and reduce "Others/Non-classified"
    """

    def __init__(self):
        self.color_guild_mapping = {
            "W": {"names": ["Mono-White", "White"], "guilds": []},
            "U": {"names": ["Mono-Blue", "Blue"], "guilds": []},
            "B": {"names": ["Mono-Black", "Black"], "guilds": []},
            "R": {"names": ["Mono-Red", "Red"], "guilds": []},
            "G": {"names": ["Mono-Green", "Green"], "guilds": []},
            "WU": {"names": ["Azorius"], "guilds": ["Azorius"]},
            "UB": {"names": ["Dimir"], "guilds": ["Dimir"]},
            "BR": {"names": ["Rakdos"], "guilds": ["Rakdos"]},
            "RG": {"names": ["Gruul"], "guilds": ["Gruul"]},
            "GW": {"names": ["Selesnya"], "guilds": ["Selesnya"]},
            "WB": {"names": ["Orzhov"], "guilds": ["Orzhov"]},
            "UR": {"names": ["Izzet"], "guilds": ["Izzet"]},
            "BG": {"names": ["Golgari"], "guilds": ["Golgari"]},
            "RW": {"names": ["Boros"], "guilds": ["Boros"]},
            "GU": {"names": ["Simic"], "guilds": ["Simic"]},
            "WUB": {"names": ["Esper"], "guilds": ["Esper"]},
            "UBR": {"names": ["Grixis"], "guilds": ["Grixis"]},
            "BRG": {"names": ["Jund"], "guilds": ["Jund"]},
            "RGW": {"names": ["Naya"], "guilds": ["Naya"]},
            "GWU": {"names": ["Bant"], "guilds": ["Bant"]},
            "WUBR": {"names": ["Sans-Green", "WUBR"], "guilds": []},
            "UBRG": {"names": ["Sans-White", "UBRG"], "guilds": []},
            "BRGW": {"names": ["Sans-Blue", "BRGW"], "guilds": []},
            "RGWU": {"names": ["Sans-Black", "RGWU"], "guilds": []},
            "GWUB": {"names": ["Sans-Red", "GWUB"], "guilds": []},
            "WUBRG": {"names": ["Five-Color", "5C", "WUBRG"], "guilds": []},
        }

        # Archetype patterns from Aliquanto3's system
        self.archetype_patterns = {
            "Control": {
                "keywords": [
                    "control",
                    "counterspell",
                    "wrath",
                    "board clear",
                    "card draw",
                ],
                "card_indicators": [
                    "Supreme Verdict",
                    "Counterspell",
                    "Teferi",
                    "Jace",
                    "Wrath of God",
                ],
                "strategy": "control",
            },
            "Aggro": {
                "keywords": ["aggressive", "burn", "rush", "fast", "cheap creatures"],
                "card_indicators": [
                    "Lightning Bolt",
                    "Goblin Guide",
                    "Monastery Swiftspear",
                ],
                "strategy": "aggro",
            },
            "Midrange": {
                "keywords": ["midrange", "value", "efficient", "versatile"],
                "card_indicators": ["Tarmogoyf", "Liliana", "Snapcaster Mage"],
                "strategy": "midrange",
            },
            "Combo": {
                "keywords": ["combo", "infinite", "synergy", "engine"],
                "card_indicators": ["Splinter Twin", "Ad Nauseam", "Storm"],
                "strategy": "combo",
            },
            "Ramp": {
                "keywords": ["ramp", "mana acceleration", "big spells"],
                "card_indicators": [
                    "Rampant Growth",
                    "Llanowar Elves",
                    "Primeval Titan",
                ],
                "strategy": "ramp",
            },
        }

        # Enhanced archetype library from R-Meta-Analysis patterns
        self.enhanced_archetypes = {
            "Prowess": {
                "base_name": "Prowess",
                "common_colors": ["UR", "R", "UBR"],
                "key_cards": [
                    "Monastery Swiftspear",
                    "Soul-Scar Mage",
                    "Stormwing Entity",
                ],
                "strategy_type": "aggro",
            },
            "Burn": {
                "base_name": "Burn",
                "common_colors": ["R", "RW"],
                "key_cards": ["Lightning Bolt", "Goblin Guide", "Lava Spike"],
                "strategy_type": "aggro",
            },
            "Tron": {
                "base_name": "Tron",
                "common_colors": ["G", "GU", "GW"],
                "key_cards": ["Urza's Tower", "Urza's Mine", "Urza's Power Plant"],
                "strategy_type": "ramp",
            },
            "Death's Shadow": {
                "base_name": "Death's Shadow",
                "common_colors": ["UBR", "BG"],
                "key_cards": ["Death's Shadow", "Street Wraith", "Thoughtseize"],
                "strategy_type": "aggro",
            },
            "Affinity": {
                "base_name": "Affinity",
                "common_colors": ["WU", "UBR"],
                "key_cards": ["Cranial Plating", "Arcbound Ravager", "Steel Overseer"],
                "strategy_type": "aggro",
            },
            "Amulet Titan": {
                "base_name": "Amulet Titan",
                "common_colors": ["RGW", "RG"],
                "key_cards": ["Amulet of Vigor", "Primeval Titan", "Tolaria West"],
                "strategy_type": "combo",
            },
        }

    def normalize_color_identity(self, colors: str) -> str:
        """Normalize color identity to standard WUBRG order"""
        if not colors:
            return ""

        # Remove duplicates and sort in WUBRG order
        color_set = set(colors.upper())
        wubrg_order = "WUBRG"
        normalized = "".join(c for c in wubrg_order if c in color_set)
        return normalized

    def get_color_name(self, color_identity: str) -> str:
        """Get the guild/shard/wedge name for a color combination"""
        normalized = self.normalize_color_identity(color_identity)

        if normalized in self.color_guild_mapping:
            return self.color_guild_mapping[normalized]["names"][0]

        # Fallback for unknown combinations
        if len(normalized) == 0:
            return "Colorless"
        elif len(normalized) == 1:
            color_names = {
                "W": "White",
                "U": "Blue",
                "B": "Black",
                "R": "Red",
                "G": "Green",
            }
            return color_names.get(normalized, normalized)
        else:
            return f"{len(normalized)}-Color"

    def analyze_deck_synergies(self, cards: List[str]) -> Dict[str, float]:
        """Analyze deck synergies to improve archetype detection"""
        synergy_scores = {}

        # Convert cards to lowercase for matching
        cards_lower = [card.lower() for card in cards]

        for archetype, data in self.enhanced_archetypes.items():
            score = 0.0
            key_card_matches = 0

            # Check for key cards
            for key_card in data["key_cards"]:
                if key_card.lower() in cards_lower:
                    key_card_matches += 1
                    score += 2.0  # High weight for key cards

            # Bonus for multiple key card matches
            if key_card_matches >= 2:
                score += key_card_matches * 1.5

            synergy_scores[archetype] = score

        return synergy_scores

    def classify_with_color_integration(self, deck_data: Dict) -> Dict[str, str]:
        """
        Advanced classification that integrates colors with archetype names
        Returns both simple archetype and color-integrated archetype
        """
        result = {
            "archetype": "Others",
            "archetype_with_colors": "Others",
            "color_identity": "",
            "guild_name": "",
            "confidence": 0.0,
            "strategy_type": "unknown",
        }

        # Get basic info
        cards = deck_data.get("cards", [])
        color_identity = deck_data.get("color_identity", "")

        # Normalize color identity
        normalized_colors = self.normalize_color_identity(color_identity)
        guild_name = self.get_color_name(normalized_colors)

        result["color_identity"] = normalized_colors
        result["guild_name"] = guild_name

        # Analyze synergies
        synergy_scores = self.analyze_deck_synergies(cards)

        # Find best matching archetype
        best_archetype = None
        best_score = 0.0

        for archetype, score in synergy_scores.items():
            if (
                score > best_score and score > 0.5
            ):  # Lowered threshold for better matching
                best_score = score
                best_archetype = archetype

        if best_archetype:
            archetype_data = self.enhanced_archetypes[best_archetype]

            # Check if color identity matches common colors for this archetype
            color_match = False
            for common_color in archetype_data["common_colors"]:
                if self.normalize_color_identity(common_color) == normalized_colors:
                    color_match = True
                    break

            result["archetype"] = best_archetype
            result["strategy_type"] = archetype_data["strategy_type"]
            result["confidence"] = min(best_score / 10.0, 1.0)  # Normalize to 0-1

            # Generate color-integrated name - more lenient approach
            if guild_name != "Colorless" and normalized_colors:
                result["archetype_with_colors"] = f"{guild_name} {best_archetype}"
            else:
                result["archetype_with_colors"] = best_archetype

        else:
            # Fallback to strategy-based classification
            strategy_scores = self._analyze_strategy_patterns(cards)
            best_strategy = max(strategy_scores.items(), key=lambda x: x[1])

            if best_strategy[1] > 0.5:
                strategy_name = best_strategy[0].title()
                result["archetype"] = strategy_name
                result["strategy_type"] = best_strategy[0]

                # Color-integrated fallback
                if guild_name != "Colorless":
                    result["archetype_with_colors"] = f"{guild_name} {strategy_name}"
                else:
                    result["archetype_with_colors"] = strategy_name
            else:
                # Ultimate fallback
                if guild_name != "Colorless":
                    result["archetype"] = f"{guild_name} Deck"
                    result["archetype_with_colors"] = f"{guild_name} Deck"

        return result

    def _analyze_strategy_patterns(self, cards: List[str]) -> Dict[str, float]:
        """Analyze cards for strategy patterns"""
        strategy_scores = defaultdict(float)
        cards_lower = [card.lower() for card in cards]

        for strategy, data in self.archetype_patterns.items():
            score = 0.0

            # Check for strategy indicators in card names
            for card in cards_lower:
                for indicator in data["card_indicators"]:
                    if indicator.lower() in card:
                        score += 1.0

                for keyword in data["keywords"]:
                    if keyword in card:
                        score += 0.5

            strategy_scores[strategy.lower()] = score / max(len(cards), 1)

        return dict(strategy_scores)

    def generate_archetype_statistics(self, classified_decks: List[Dict]) -> Dict:
        """Generate comprehensive archetype statistics"""
        stats = {
            "total_decks": len(classified_decks),
            "archetype_distribution": Counter(),
            "color_distribution": Counter(),
            "strategy_distribution": Counter(),
            "color_integrated_distribution": Counter(),
            "classification_accuracy": 0.0,
        }

        others_count = 0

        for deck in classified_decks:
            classification = deck.get("classification", {})

            archetype = classification.get("archetype", "Others")
            color_integrated = classification.get("archetype_with_colors", "Others")
            color_identity = classification.get("color_identity", "")
            strategy = classification.get("strategy_type", "unknown")

            stats["archetype_distribution"][archetype] += 1
            stats["color_integrated_distribution"][color_integrated] += 1
            stats["color_distribution"][color_identity] += 1
            stats["strategy_distribution"][strategy] += 1

            if archetype == "Others":
                others_count += 1

        # Calculate accuracy (fewer "Others" = better)
        stats["classification_accuracy"] = 1.0 - (
            others_count / max(len(classified_decks), 1)
        )
        stats["others_percentage"] = (
            others_count / max(len(classified_decks), 1)
        ) * 100

        return stats

    def improve_classification_rules(self, feedback_data: List[Dict]) -> None:
        """Improve classification rules based on feedback"""
        # This method can be used to update archetype patterns based on manual corrections
        archetype_corrections = defaultdict(list)

        for feedback in feedback_data:
            original = feedback.get("original_classification")
            corrected = feedback.get("corrected_classification")
            cards = feedback.get("cards", [])

            if original != corrected:
                archetype_corrections[corrected].extend(cards)

        # Update enhanced archetypes based on corrections
        for archetype, card_lists in archetype_corrections.items():
            all_cards = [card for cards in card_lists for card in cards]
            common_cards = [card for card, count in Counter(all_cards).most_common(10)]

            if archetype not in self.enhanced_archetypes:
                self.enhanced_archetypes[archetype] = {
                    "base_name": archetype,
                    "common_colors": [],
                    "key_cards": common_cards[:5],
                    "strategy_type": "unknown",
                }
            else:
                # Update existing archetype
                existing_cards = set(self.enhanced_archetypes[archetype]["key_cards"])
                new_cards = set(common_cards[:5])
                self.enhanced_archetypes[archetype]["key_cards"] = list(
                    existing_cards.union(new_cards)
                )[:10]
