import json
import os
from typing import Dict, List, Optional, Any
import structlog
from collections import defaultdict

logger = structlog.get_logger()

class ArchetypeEngine:
    """Moteur de classification d'archétypes basé sur des règles"""
    
    def __init__(self, format_data_path: str):
        self.format_data_path = format_data_path
        self.rules = {}
        self.fallbacks = {}
        self.color_overrides = {}
        
    def load_format_data(self, format_name: str) -> bool:
        """Charger les données d'un format spécifique"""
        try:
            format_path = os.path.join(self.format_data_path, "Formats", format_name)
            
            if not os.path.exists(format_path):
                logger.error("Format path not found", format=format_name, path=format_path)
                return False
                
            # Charger les archétypes
            archetypes_path = os.path.join(format_path, "Archetypes")
            if os.path.exists(archetypes_path):
                self.rules[format_name] = self._load_archetypes(archetypes_path)
                
            # Charger les fallbacks
            fallbacks_path = os.path.join(format_path, "Fallbacks")
            if os.path.exists(fallbacks_path):
                self.fallbacks[format_name] = self._load_fallbacks(fallbacks_path)
                
            # Charger les color overrides
            color_overrides_file = os.path.join(format_path, "color_overrides.json")
            if os.path.exists(color_overrides_file):
                with open(color_overrides_file, 'r', encoding='utf-8') as f:
                    self.color_overrides[format_name] = json.load(f)
                    
            logger.info("Format data loaded", format=format_name, 
                       archetypes=len(self.rules.get(format_name, [])),
                       fallbacks=len(self.fallbacks.get(format_name, [])))
            return True
            
        except Exception as e:
            logger.error("Failed to load format data", format=format_name, error=str(e))
            return False
            
    def _load_archetypes(self, archetypes_path: str) -> List[Dict]:
        """Charger tous les archétypes d'un dossier"""
        archetypes = []
        
        for filename in os.listdir(archetypes_path):
            if filename.endswith('.json'):
                file_path = os.path.join(archetypes_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        archetype_data = json.load(f)
                        archetypes.append(archetype_data)
                except Exception as e:
                    logger.warning("Failed to load archetype file", file=filename, error=str(e))
                    
        return archetypes
        
    def _load_fallbacks(self, fallbacks_path: str) -> List[Dict]:
        """Charger tous les fallbacks d'un dossier"""
        fallbacks = []
        
        for filename in os.listdir(fallbacks_path):
            if filename.endswith('.json'):
                file_path = os.path.join(fallbacks_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        fallback_data = json.load(f)
                        fallbacks.append(fallback_data)
                except Exception as e:
                    logger.warning("Failed to load fallback file", file=filename, error=str(e))
                    
        return fallbacks
        
    def classify_deck(self, deck: Dict, format_name: str) -> Optional[str]:
        """Classifier un deck selon son archétype"""
        
        if format_name not in self.rules:
            if not self.load_format_data(format_name):
                return "Unknown"
                
        # Extraire les cartes du deck
        mainboard = self._extract_card_dict(deck.get('mainboard', []))
        sideboard = self._extract_card_dict(deck.get('sideboard', []))
        
        # Essayer de matcher avec les archétypes
        for archetype in self.rules.get(format_name, []):
            if self._matches_archetype(mainboard, sideboard, archetype):
                archetype_name = archetype.get('Name', 'Unknown')
                
                # Vérifier les variantes
                variant = self._check_variants(mainboard, sideboard, archetype)
                if variant:
                    return f"{archetype_name} - {variant}"
                    
                return archetype_name
                
        # Si aucun archétype ne match, essayer les fallbacks
        fallback_name = self._try_fallbacks(mainboard, sideboard, format_name)
        if fallback_name:
            return fallback_name
            
        return "Unknown"
        
    def _extract_card_dict(self, card_list: List[Dict]) -> Dict[str, int]:
        """Convertir une liste de cartes en dictionnaire nom -> quantité"""
        card_dict = defaultdict(int)
        
        for card in card_list:
            name = card.get('name', '').strip()
            count = card.get('count', 1)
            if name:
                card_dict[name] += count
                
        return dict(card_dict)
        
    def _matches_archetype(self, mainboard: Dict, sideboard: Dict, archetype: Dict) -> bool:
        """Vérifier si un deck matche un archétype"""
        conditions = archetype.get('Conditions', [])
        
        for condition in conditions:
            if not self._evaluate_condition(mainboard, sideboard, condition):
                return False
                
        return True
        
    def _evaluate_condition(self, mainboard: Dict, sideboard: Dict, condition: Dict) -> bool:
        """Évaluer une condition d'archétype"""
        condition_type = condition.get('Type', '')
        cards = condition.get('Cards', [])
        
        if condition_type == 'InMainboard':
            return all(card in mainboard for card in cards)
            
        elif condition_type == 'InSideboard':
            return all(card in sideboard for card in cards)
            
        elif condition_type == 'InMainOrSideboard':
            return all(card in mainboard or card in sideboard for card in cards)
            
        elif condition_type == 'OneOrMoreInMainboard':
            return any(card in mainboard for card in cards)
            
        elif condition_type == 'OneOrMoreInSideboard':
            return any(card in sideboard for card in cards)
            
        elif condition_type == 'OneOrMoreInMainOrSideboard':
            return any(card in mainboard or card in sideboard for card in cards)
            
        elif condition_type == 'TwoOrMoreInMainboard':
            count = sum(1 for card in cards if card in mainboard)
            return count >= 2
            
        elif condition_type == 'TwoOrMoreInSideboard':
            count = sum(1 for card in cards if card in sideboard)
            return count >= 2
            
        elif condition_type == 'TwoOrMoreInMainOrSideboard':
            count = sum(1 for card in cards if card in mainboard or card in sideboard)
            return count >= 2
            
        elif condition_type == 'DoesNotContain':
            return not any(card in mainboard or card in sideboard for card in cards)
            
        elif condition_type == 'DoesNotContainMainboard':
            return not any(card in mainboard for card in cards)
            
        elif condition_type == 'DoesNotContainSideboard':
            return not any(card in sideboard for card in cards)
            
        else:
            logger.warning("Unknown condition type", type=condition_type)
            return False
            
    def _check_variants(self, mainboard: Dict, sideboard: Dict, archetype: Dict) -> Optional[str]:
        """Vérifier les variantes d'un archétype"""
        variants = archetype.get('Variants', [])
        
        for variant in variants:
            if self._matches_archetype(mainboard, sideboard, variant):
                return variant.get('Name', 'Unknown Variant')
                
        return None
        
    def _try_fallbacks(self, mainboard: Dict, sideboard: Dict, format_name: str) -> Optional[str]:
        """Essayer de classifier avec les fallbacks"""
        
        fallbacks = self.fallbacks.get(format_name, [])
        if not fallbacks:
            return None
            
        all_cards = set(mainboard.keys()) | set(sideboard.keys())
        best_match = None
        best_score = 0
        
        for fallback in fallbacks:
            common_cards = fallback.get('CommonCards', [])
            if not common_cards:
                continue
                
            # Calculer le score de correspondance
            matches = len(set(common_cards) & all_cards)
            score = matches / len(common_cards)
            
            # Seuil minimum de 10% comme dans le projet original
            if score >= 0.1 and score > best_score:
                best_score = score
                best_match = fallback.get('Name', 'Unknown Fallback')
                
        return best_match
        
    def classify_tournament(self, tournament_data: Dict, format_name: str) -> Dict:
        """Classifier tous les decks d'un tournoi"""
        classified_data = tournament_data.copy()
        
        for deck in classified_data.get('decks', []):
            archetype = self.classify_deck(deck, format_name)
            deck['archetype'] = archetype
            
        return classified_data 