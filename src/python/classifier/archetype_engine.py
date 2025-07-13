#!/usr/bin/env python3
"""
Archetype Engine - Reproduction de Badaro/MTGOArchetypeParser
Classification des archétypes selon les règles MTGOFormatData
"""

import json
import os
import glob
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import re

class ArchetypeEngine:
    """Moteur de classification d'archétypes selon MTGOArchetypeParser"""
    
    def __init__(self, format_data_path: str, input_dir: str, output_dir: str):
        self.format_data_path = format_data_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger('ArchetypeEngine')
        
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
                        with open(archetype_file, 'r', encoding='utf-8') as f:
                            archetype_data = json.load(f)
                            self.archetypes[format_name][archetype_data['Name']] = archetype_data
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON in {archetype_file}: {e}")
                    except Exception as e:
                        self.logger.error(f"Failed to load archetype {archetype_file}: {e}")
                        
            # Charger les fallbacks
            fallbacks_path = format_path / "Fallbacks"
            if fallbacks_path.exists():
                for fallback_file in fallbacks_path.glob("*.json"):
                    try:
                        with open(fallback_file, 'r', encoding='utf-8') as f:
                            fallback_data = json.load(f)
                            self.fallbacks[format_name][fallback_data['Name']] = fallback_data
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON in {fallback_file}: {e}")
                    except Exception as e:
                        self.logger.error(f"Failed to load fallback {fallback_file}: {e}")
                        
            self.logger.info(f"Loaded {len(self.archetypes[format_name])} archetypes and {len(self.fallbacks[format_name])} fallbacks for {format_name}")
            
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
            
            self.logger.info(f"Found {len(tournament_files)} tournament files to classify")
            
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
            with open(tournament_file, 'r', encoding='utf-8') as f:
                tournament_data = json.load(f)
                
            # Vérifier si c'est le bon format
            tournament_format = tournament_data.get('Tournament', {}).get('Format', '').lower()
            if tournament_format and tournament_format != format_name.lower():
                return False
                
            # Classifier chaque deck
            standings = tournament_data.get('Standings', [])
            classified_standings = []
            
            for standing in standings:
                classified_standing = standing.copy()
                deck = standing.get('Deck', {})
                
                if deck:
                    archetype = self.classify_deck(deck, format_name)
                    classified_standing['Deck']['Archetype'] = archetype
                    
                classified_standings.append(classified_standing)
                
            # Mettre à jour les données
            tournament_data['Standings'] = classified_standings
            
            # Sauvegarder le fichier classifié
            output_file = Path(self.output_dir) / tournament_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to classify tournament file {tournament_file}: {e}")
            return False
            
    def classify_deck(self, deck: Dict, format_name: str) -> str:
        """Classifie un deck selon les règles d'archétypes"""
        try:
            format_name = format_name.lower()
            
            # Extraire les cartes du deck
            mainboard = self.extract_cardlist(deck.get('Mainboard', []))
            sideboard = self.extract_cardlist(deck.get('Sideboard', []))
            
            # Essayer d'abord les archétypes principaux
            archetype = self.match_archetypes(mainboard, sideboard, format_name)
            if archetype:
                return archetype
                
            # Essayer les fallbacks
            fallback = self.match_fallbacks(mainboard, sideboard, format_name)
            if fallback:
                return fallback
                
            # Aucune correspondance trouvée
            return "Unknown"
            
        except Exception as e:
            self.logger.error(f"Failed to classify deck: {e}")
            return "Unknown"
            
    def extract_cardlist(self, cards: List[Dict]) -> Dict[str, int]:
        """Extrait une liste de cartes vers un dictionnaire nom -> quantité"""
        cardlist = {}
        
        for card in cards:
            name = card.get('Name', '').strip()
            count = card.get('Count', 0)
            
            if name and count > 0:
                # Normaliser le nom de la carte
                normalized_name = self.normalize_card_name(name)
                cardlist[normalized_name] = cardlist.get(normalized_name, 0) + count
                
        return cardlist
        
    def normalize_card_name(self, name: str) -> str:
        """Normalise le nom d'une carte pour la correspondance"""
        # Supprimer les caractères spéciaux et normaliser
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
        
    def match_archetypes(self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str) -> Optional[str]:
        """Essaie de faire correspondre avec les archétypes principaux"""
        archetypes = self.archetypes.get(format_name, {})
        
        for archetype_name, archetype_data in archetypes.items():
            if self.matches_archetype_conditions(mainboard, sideboard, archetype_data):
                return archetype_name
                
        return None
        
    def match_fallbacks(self, mainboard: Dict[str, int], sideboard: Dict[str, int], format_name: str) -> Optional[str]:
        """Essaie de faire correspondre avec les fallbacks"""
        fallbacks = self.fallbacks.get(format_name, {})
        
        for fallback_name, fallback_data in fallbacks.items():
            if self.matches_archetype_conditions(mainboard, sideboard, fallback_data):
                return fallback_name
                
        return None
        
    def matches_archetype_conditions(self, mainboard: Dict[str, int], sideboard: Dict[str, int], archetype_data: Dict) -> bool:
        """Vérifie si un deck correspond aux conditions d'un archétype"""
        try:
            conditions = archetype_data.get('Conditions', [])
            
            for condition in conditions:
                if not self.evaluate_condition(mainboard, sideboard, condition):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate archetype conditions: {e}")
            return False
            
    def evaluate_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict) -> bool:
        """Évalue une condition individuelle"""
        try:
            condition_type = condition.get('Type', '').lower()
            
            if condition_type == 'contains':
                return self.evaluate_contains_condition(mainboard, sideboard, condition)
            elif condition_type == 'excludes':
                return self.evaluate_excludes_condition(mainboard, sideboard, condition)
            elif condition_type == 'and':
                return self.evaluate_and_condition(mainboard, sideboard, condition)
            elif condition_type == 'or':
                return self.evaluate_or_condition(mainboard, sideboard, condition)
            else:
                self.logger.warning(f"Unknown condition type: {condition_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to evaluate condition: {e}")
            return False
            
    def evaluate_contains_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict) -> bool:
        """Évalue une condition 'contains'"""
        cards = condition.get('Cards', [])
        min_count = condition.get('MinCount', 1)
        zones = condition.get('Zones', ['Mainboard', 'Sideboard'])
        
        total_count = 0
        
        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            
            if 'Mainboard' in zones:
                total_count += mainboard.get(normalized_name, 0)
            if 'Sideboard' in zones:
                total_count += sideboard.get(normalized_name, 0)
                
        return total_count >= min_count
        
    def evaluate_excludes_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict) -> bool:
        """Évalue une condition 'excludes'"""
        cards = condition.get('Cards', [])
        zones = condition.get('Zones', ['Mainboard', 'Sideboard'])
        
        for card_name in cards:
            normalized_name = self.normalize_card_name(card_name)
            
            if 'Mainboard' in zones and mainboard.get(normalized_name, 0) > 0:
                return False
            if 'Sideboard' in zones and sideboard.get(normalized_name, 0) > 0:
                return False
                
        return True
        
    def evaluate_and_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict) -> bool:
        """Évalue une condition 'and'"""
        sub_conditions = condition.get('Conditions', [])
        
        for sub_condition in sub_conditions:
            if not self.evaluate_condition(mainboard, sideboard, sub_condition):
                return False
                
        return True
        
    def evaluate_or_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], condition: Dict) -> bool:
        """Évalue une condition 'or'"""
        sub_conditions = condition.get('Conditions', [])
        
        for sub_condition in sub_conditions:
            if self.evaluate_condition(mainboard, sideboard, sub_condition):
                return True
                
        return False
        
    def get_classification_stats(self, format_name: str) -> Dict[str, Any]:
        """Retourne les statistiques de classification"""
        try:
            stats = {
                'total_archetypes': len(self.archetypes.get(format_name, {})),
                'total_fallbacks': len(self.fallbacks.get(format_name, {})),
                'archetype_names': list(self.archetypes.get(format_name, {}).keys()),
                'fallback_names': list(self.fallbacks.get(format_name, {}).keys())
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get classification stats: {e}")
            return {} 