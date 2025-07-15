#!/usr/bin/env python3
"""
Archetype Engine - Reproduction de Badaro/MTGOArchetypeParser
Classification des archétypes selon les règles MTGOFormatData
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ArchetypeEngine:
    """Moteur de classification d'archétypes selon MTGOArchetypeParser"""

    def __init__(self, format_data_path: str, input_dir: str, output_dir: str):
        self.format_data_path = format_data_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger("ArchetypeEngine")

        # Charger les règles d'archétypes
        self.archetypes = {}
        self.fallbacks = {}
        self.load_all_format_rules()

    def load_all_format_rules(self):
        """Charge toutes les règles de formats disponibles"""
        try:
            formats_path = Path(self.format_data_path) / "Formats"
            if not formats_path.exists():
                self.logger.error(f"Format data path not found: {formats_path}")
                return

            for format_dir in formats_path.iterdir():
                if format_dir.is_dir():
                    format_name = format_dir.name.lower()
                    self.load_format_rules(format_name, format_dir)

        except Exception as e:
            self.logger.error(f"Failed to load format rules: {e}")

    def load_format_rules(self, format_name: str, format_path: Path):
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
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON in {archetype_file}: {e}")
                    except Exception as e:
                        self.logger.error(
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
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON in {fallback_file}: {e}")
                    except Exception as e:
                        self.logger.error(
                            f"Failed to load fallback {fallback_file}: {e}"
                        )

            self.logger.info(
                f"Loaded {len(self.archetypes[format_name])} archetypes and "
                f"{len(self.fallbacks[format_name])} fallbacks for {format_name}"
            )

        except Exception as e:
            self.logger.error(f"Failed to load rules for {format_name}: {e}")

    def classify_all_tournaments(self, format_name: str):
        """Classifie tous les tournois d'un format"""
        try:
            input_path = Path(self.input_dir)
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Rechercher tous les fichiers JSON de tournois
            tournament_files = list(input_path.rglob("*.json"))

            self.logger.info(
                f"Found {len(tournament_files)} tournament files to classify"
            )

            classified_count = 0
            for tournament_file in tournament_files:
                try:
                    if self.classify_tournament_file(tournament_file, format_name):
                        classified_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to classify {tournament_file}: {e}")

            self.logger.info(f"Successfully classified {classified_count} tournaments")

        except Exception as e:
            self.logger.error(f"Failed to classify tournaments: {e}")

    def classify_tournament_file(self, tournament_file: Path, format_name: str) -> bool:
        """Classifie un fichier de tournoi"""
        try:
            with open(tournament_file, "r", encoding="utf-8") as f:
                tournament_data = json.load(f)

            # Vérifier si c'est le bon format
            tournament_format = (
                tournament_data.get("Tournament", {}).get("Format", "").lower()
            )
            if tournament_format and tournament_format != format_name.lower():
                return False

            # Classifier chaque deck
            standings = tournament_data.get("Standings", [])
            classified_standings = []

            for standing in standings:
                classified_standing = standing.copy()
                deck = standing.get("Deck", {})

                if deck:
                    archetype = self.classify_deck(deck, format_name)
                    classified_standing["Deck"]["Archetype"] = archetype

                classified_standings.append(classified_standing)

            # Mettre à jour les données
            tournament_data["Standings"] = classified_standings

            # Sauvegarder le fichier classifié
            output_file = Path(self.output_dir) / tournament_file.name
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to classify tournament file {tournament_file}: {e}"
            )
            return False

    def classify_deck(self, deck: Dict, format_name: str) -> str:
        """Classifie un deck selon les règles d'archétypes"""
        result = self.classify_deck_with_metadata(deck, format_name)
        return result["archetype_name"]

    def classify_deck_with_metadata(
        self, deck: Dict, format_name: str
    ) -> Dict[str, Any]:
        """
        Classifie un deck selon les règles d'archétypes avec métadonnées complètes

        Returns:
            Dict contenant:
            - archetype_name: Nom de l'archétype
            - include_color_in_name: Boolean du champ IncludeColorInName
            - archetype_data: Données complètes de l'archétype
            - classification_type: "archetype" ou "fallback"
        """
        try:
            format_name = format_name.lower()

            # Extraire les cartes du deck
            mainboard = self.extract_cardlist(deck.get("Mainboard", []))
            sideboard = self.extract_cardlist(deck.get("Sideboard", []))

            # Essayer d'abord les archétypes principaux
            archetype_result = self.match_archetypes_with_metadata(
                mainboard, sideboard, format_name
            )
            if archetype_result:
                return archetype_result

            # Essayer les fallbacks
            fallback_result = self.match_fallbacks_with_metadata(
                mainboard, sideboard, format_name
            )
            if fallback_result:
                return fallback_result

            # Aucune correspondance trouvée
            return {
                "archetype_name": "Unknown",
                "include_color_in_name": False,
                "archetype_data": None,
                "classification_type": "unknown",
            }

        except Exception as e:
            self.logger.error(f"Failed to classify deck: {e}")
            return {
                "archetype_name": "Unknown",
                "include_color_in_name": False,
                "archetype_data": None,
                "classification_type": "error",
            }

    def extract_cardlist(self, cards: List[Dict]) -> Dict[str, int]:
        """Extrait une liste de cartes vers un dictionnaire nom -> quantité"""
        cardlist = {}

        for card in cards:
            # Support both formats: MTGODecklistCache ("Name") and orchestrator ("CardName")
            name = card.get("Name", card.get("CardName", "")).strip()
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
        result = self.match_archetypes_with_metadata(mainboard, sideboard, format_name)
        return result["archetype_name"] if result else None

    def match_archetypes_with_metadata(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str
    ) -> Optional[Dict[str, Any]]:
        """Essaie de faire correspondre avec les archétypes principaux (avec métadonnées)"""
        archetypes = self.archetypes.get(format_name, {})

        for archetype_name, archetype_data in archetypes.items():
            if self.matches_archetype_conditions(mainboard, sideboard, archetype_data):
                # Check for variants if the main archetype matches
                variant_result = self.check_archetype_variants(
                    mainboard, sideboard, archetype_data
                )

                if variant_result:
                    # Return variant match
                    return {
                        "archetype_name": f"{archetype_name} - {variant_result['variant_name']}",
                        "include_color_in_name": variant_result.get(
                            "include_color_in_name",
                            archetype_data.get("IncludeColorInName", False),
                        ),
                        "archetype_data": archetype_data,
                        "variant_data": variant_result["variant_data"],
                        "classification_type": "archetype_variant",
                    }
                else:
                    # Return main archetype match
                    return {
                        "archetype_name": archetype_name,
                        "include_color_in_name": archetype_data.get(
                            "IncludeColorInName", False
                        ),
                        "archetype_data": archetype_data,
                        "classification_type": "archetype",
                    }

        return None

    def check_archetype_variants(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], archetype_data: Dict
    ) -> Optional[Dict[str, Any]]:
        """Check if deck matches any variant of the archetype"""
        variants = archetype_data.get("Variants", [])

        for variant in variants:
            if self.matches_archetype_conditions(mainboard, sideboard, variant):
                return {
                    "variant_name": variant.get("Name", "Unknown Variant"),
                    "variant_data": variant,
                    "include_color_in_name": variant.get(
                        "IncludeColorInName",
                        archetype_data.get("IncludeColorInName", False),
                    ),
                }

        return None

    def match_fallbacks(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str
    ) -> Optional[str]:
        """Essaie de faire correspondre avec les fallbacks"""
        result = self.match_fallbacks_with_metadata(mainboard, sideboard, format_name)
        return result["archetype_name"] if result else None

    def match_fallbacks_with_metadata(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str
    ) -> Optional[Dict[str, Any]]:
        """Essaie de faire correspondre avec les fallbacks (avec métadonnées)"""
        fallbacks = self.fallbacks.get(format_name, {})

        if not fallbacks:
            return None

        best_match = None
        best_score = 0.0
        minimum_threshold = 0.10  # 10% minimum as per MTGOArchetypeParser

        for fallback_name, fallback_data in fallbacks.items():
            # Check if this fallback has explicit conditions first
            if fallback_data.get("Conditions"):
                if self.matches_archetype_conditions(
                    mainboard, sideboard, fallback_data
                ):
                    return {
                        "archetype_name": fallback_name,
                        "include_color_in_name": fallback_data.get(
                            "IncludeColorInName", True
                        ),
                        "archetype_data": fallback_data,
                        "classification_type": "fallback",
                    }

            # Use common cards matching algorithm
            common_cards = fallback_data.get("CommonCards", [])
            if common_cards:
                score = self.calculate_common_cards_score(
                    mainboard, sideboard, common_cards
                )

                if score >= minimum_threshold and score > best_score:
                    best_score = score
                    best_match = {
                        "archetype_name": fallback_name,
                        "include_color_in_name": fallback_data.get(
                            "IncludeColorInName", True
                        ),
                        "archetype_data": fallback_data,
                        "classification_type": "fallback",
                        "match_score": score,
                    }

        return best_match

    def calculate_common_cards_score(
        self,
        mainboard: Dict[str, int],
        sideboard: Dict[str, int],
        common_cards: List[str],
    ) -> float:
        """Calculate the percentage of common cards present in the deck"""
        if not common_cards:
            return 0.0

        matched_cards = 0
        total_cards = len(common_cards)

        all_deck_cards = set()
        all_deck_cards.update(mainboard.keys())
        all_deck_cards.update(sideboard.keys())

        for card_name in common_cards:
            normalized_name = self.normalize_card_name(card_name)
            if normalized_name in all_deck_cards:
                matched_cards += 1

        return matched_cards / total_cards if total_cards > 0 else 0.0

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

            # MTGOFormatData standard conditions - COMPLETE SET
            if condition_type == "inmainboard":
                return self.evaluate_inmainboard_condition(mainboard, condition)
            elif condition_type == "insideboard":
                return self.evaluate_insideboard_condition(sideboard, condition)
            elif condition_type == "inmainorsideboard":
                return self.evaluate_inmainorsideboard_condition(
                    mainboard, sideboard, condition
                )
            elif condition_type == "oneormoreinmainboard":
                return self.evaluate_oneormoreinmainboard_condition(
                    mainboard, condition
                )
            elif condition_type == "oneormoreinsideboard":
                return self.evaluate_oneormoreinsideboard_condition(
                    sideboard, condition
                )
            elif condition_type == "oneormoreinmainorsideboard":
                return self.evaluate_oneormoreinmainorsideboard_condition(
                    mainboard, sideboard, condition
                )
            elif condition_type == "twoormoreinmainboard":
                return self.evaluate_twoormoreinmainboard_condition(
                    mainboard, condition
                )
            elif condition_type == "twoormoreinsideboard":
                return self.evaluate_twoormoreinsideboard_condition(
                    sideboard, condition
                )
            elif condition_type == "twoormoreinmainorsideboard":
                return self.evaluate_twoormoreinmainorsideboard_condition(
                    mainboard, sideboard, condition
                )
            elif condition_type == "doesnotcontain":
                return self.evaluate_doesnotcontain_condition(
                    mainboard, sideboard, condition
                )
            elif condition_type == "doesnotcontainmainboard":
                return self.evaluate_doesnotcontainmainboard_condition(
                    mainboard, condition
                )
            elif condition_type == "doesnotcontainsideboard":
                return self.evaluate_doesnotcontainsideboard_condition(
                    sideboard, condition
                )
            # Legacy conditions for backwards compatibility
            elif condition_type == "contains":
                return self.evaluate_contains_condition(mainboard, sideboard, condition)
            elif condition_type == "excludes":
                return self.evaluate_excludes_condition(mainboard, sideboard, condition)
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

    def evaluate_inmainboard_condition(
        self, mainboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'InMainboard' - toutes les cartes doivent être présentes"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if mainboard.get(normalized_name, 0) == 0:
                return False
        return True

    def evaluate_oneormoreinmainboard_condition(
        self, mainboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'OneOrMoreInMainboard' - au moins une carte doit être présente"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if mainboard.get(normalized_name, 0) > 0:
                return True
        return False

    def evaluate_doesnotcontain_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'DoesNotContain' - aucune des cartes ne doit être présente"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if (
                mainboard.get(normalized_name, 0) > 0
                or sideboard.get(normalized_name, 0) > 0
            ):
                return False
        return True

    def evaluate_insideboard_condition(
        self, sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'InSideboard' - cartes doivent être dans le sideboard"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if sideboard.get(normalized_name, 0) == 0:
                return False
        return True

    def evaluate_inmainorsideboard_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'InMainOrSideboard' - toutes les cartes doivent être présentes dans MB ou SB"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            total_count = mainboard.get(normalized_name, 0) + sideboard.get(
                normalized_name, 0
            )
            if total_count == 0:
                return False
        return True

    def evaluate_oneormoreinsideboard_condition(
        self, sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'OneOrMoreInSideboard' - au moins une carte doit être dans le sideboard"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if sideboard.get(normalized_name, 0) > 0:
                return True
        return False

    def evaluate_oneormoreinmainorsideboard_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'OneOrMoreInMainOrSideboard' - au moins une carte doit être dans MB ou SB"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            total_count = mainboard.get(normalized_name, 0) + sideboard.get(
                normalized_name, 0
            )
            if total_count > 0:
                return True
        return False

    def evaluate_twoormoreinmainboard_condition(
        self, mainboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'TwoOrMoreInMainboard' - au moins deux cartes de la liste doivent être dans le mainboard"""
        cards = condition.get("Cards", [])
        found_count = 0

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if mainboard.get(normalized_name, 0) > 0:
                found_count += 1
                if found_count >= 2:
                    return True
        return False

    def evaluate_twoormoreinsideboard_condition(
        self, sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'TwoOrMoreInSideboard' - au moins deux cartes de la liste doivent être dans le sideboard"""
        cards = condition.get("Cards", [])
        found_count = 0

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if sideboard.get(normalized_name, 0) > 0:
                found_count += 1
                if found_count >= 2:
                    return True
        return False

    def evaluate_twoormoreinmainorsideboard_condition(
        self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'TwoOrMoreInMainOrSideboard' - au moins deux cartes de la liste doivent être dans MB ou SB"""
        cards = condition.get("Cards", [])
        found_count = 0

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            total_count = mainboard.get(normalized_name, 0) + sideboard.get(
                normalized_name, 0
            )
            if total_count > 0:
                found_count += 1
                if found_count >= 2:
                    return True
        return False

    def evaluate_doesnotcontainmainboard_condition(
        self, mainboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'DoesNotContainMainboard' - aucune des cartes ne doit être dans le mainboard"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if mainboard.get(normalized_name, 0) > 0:
                return False
        return True

    def evaluate_doesnotcontainsideboard_condition(
        self, sideboard: Dict[str, int], condition: Dict
    ) -> bool:
        """Évalue une condition 'DoesNotContainSideboard' - aucune des cartes ne doit être dans le sideboard"""
        cards = condition.get("Cards", [])

        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            if sideboard.get(normalized_name, 0) > 0:
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
