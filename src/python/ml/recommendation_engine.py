"""
Système de recommandation personnalisé pour les decks
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict, Counter
import json
import math

logger = logging.getLogger(__name__)

@dataclass
class PlayerProfile:
    """Profil d'un joueur"""
    player_id: str
    aggression_level: float  # 0-1, 0 = control, 1 = aggro
    control_preference: float  # 0-1, préférence pour le contrôle
    combo_affinity: float  # 0-1, affinité pour les combos
    favorite_colors: List[str]  # Couleurs préférées
    skill_level: float  # 0-1, niveau de compétence estimé
    budget_range: Optional[Tuple[float, float]] = None
    preferred_formats: List[str] = None
    play_style_tags: List[str] = None
    
    def __post_init__(self):
        if self.preferred_formats is None:
            self.preferred_formats = []
        if self.play_style_tags is None:
            self.play_style_tags = []

@dataclass
class DeckRecommendation:
    """Recommandation de deck"""
    archetype: str
    match_score: float
    expected_winrate: float
    learning_curve: float
    price_estimate: float
    reasons: List[str]
    suggested_cards: List[Dict]
    sideboard_suggestions: List[Dict]
    meta_positioning: Dict

class CollaborativeFiltering:
    """Filtrage collaboratif pour les recommandations"""
    
    def __init__(self):
        self.user_item_matrix = {}  # user_id -> {archetype: rating}
        self.item_features = {}     # archetype -> features
        self.user_similarities = {}
        
    def add_user_rating(self, user_id: str, archetype: str, rating: float):
        """Ajouter une note utilisateur"""
        if user_id not in self.user_item_matrix:
            self.user_item_matrix[user_id] = {}
        self.user_item_matrix[user_id][archetype] = rating
        
    def calculate_user_similarity(self, user1: str, user2: str) -> float:
        """Calculer la similarité entre deux utilisateurs"""
        if user1 not in self.user_item_matrix or user2 not in self.user_item_matrix:
            return 0.0
            
        ratings1 = self.user_item_matrix[user1]
        ratings2 = self.user_item_matrix[user2]
        
        # Trouver les archétypes communs
        common_archetypes = set(ratings1.keys()) & set(ratings2.keys())
        
        if len(common_archetypes) == 0:
            return 0.0
            
        # Calculer la corrélation de Pearson
        sum1 = sum(ratings1[arch] for arch in common_archetypes)
        sum2 = sum(ratings2[arch] for arch in common_archetypes)
        
        sum1_sq = sum(ratings1[arch] ** 2 for arch in common_archetypes)
        sum2_sq = sum(ratings2[arch] ** 2 for arch in common_archetypes)
        
        sum_products = sum(ratings1[arch] * ratings2[arch] for arch in common_archetypes)
        
        n = len(common_archetypes)
        
        numerator = sum_products - (sum1 * sum2 / n)
        denominator = math.sqrt((sum1_sq - sum1 ** 2 / n) * (sum2_sq - sum2 ** 2 / n))
        
        if denominator == 0:
            return 0.0
            
        return numerator / denominator
        
    def get_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[Tuple[str, float]]:
        """Obtenir des recommandations pour un utilisateur"""
        if user_id not in self.user_item_matrix:
            return []
            
        # Calculer les similarités avec tous les autres utilisateurs
        similarities = {}
        for other_user in self.user_item_matrix:
            if other_user != user_id:
                similarities[other_user] = self.calculate_user_similarity(user_id, other_user)
                
        # Trier par similarité
        similar_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Calculer les scores pour chaque archétype
        archetype_scores = defaultdict(float)
        archetype_weights = defaultdict(float)
        
        user_ratings = self.user_item_matrix[user_id]
        
        for similar_user, similarity in similar_users[:10]:  # Top 10 utilisateurs similaires
            if similarity <= 0:
                continue
                
            for archetype, rating in self.user_item_matrix[similar_user].items():
                if archetype not in user_ratings:  # Archétype non encore essayé
                    archetype_scores[archetype] += similarity * rating
                    archetype_weights[archetype] += similarity
                    
        # Normaliser les scores
        recommendations = []
        for archetype, score in archetype_scores.items():
            if archetype_weights[archetype] > 0:
                normalized_score = score / archetype_weights[archetype]
                recommendations.append((archetype, normalized_score))
                
        return sorted(recommendations, key=lambda x: x[1], reverse=True)[:n_recommendations]

class PersonalizedRecommender:
    """Moteur de recommandation personnalisé"""
    
    def __init__(self):
        self.user_profiles = {}
        self.collaborative_filter = CollaborativeFiltering()
        self.archetype_features = {}
        self.card_database = {}
        
    def analyze_player_style(self, player_id: str, match_history: List[Dict]) -> PlayerProfile:
        """Analyser le style de jeu d'un joueur"""
        if not match_history:
            return self._create_default_profile(player_id)
            
        # Analyser l'agressivité
        aggression_level = self._calculate_aggression(match_history)
        
        # Analyser la préférence pour le contrôle
        control_preference = self._calculate_control_preference(match_history)
        
        # Analyser l'affinité pour les combos
        combo_affinity = self._calculate_combo_affinity(match_history)
        
        # Extraire les couleurs préférées
        favorite_colors = self._extract_color_preferences(match_history)
        
        # Estimer le niveau de compétence
        skill_level = self._estimate_skill_level(match_history)
        
        # Analyser les tags de style de jeu
        play_style_tags = self._analyze_play_style_tags(match_history)
        
        profile = PlayerProfile(
            player_id=player_id,
            aggression_level=aggression_level,
            control_preference=control_preference,
            combo_affinity=combo_affinity,
            favorite_colors=favorite_colors,
            skill_level=skill_level,
            play_style_tags=play_style_tags
        )
        
        self.user_profiles[player_id] = profile
        return profile
        
    def _create_default_profile(self, player_id: str) -> PlayerProfile:
        """Créer un profil par défaut"""
        return PlayerProfile(
            player_id=player_id,
            aggression_level=0.5,
            control_preference=0.5,
            combo_affinity=0.5,
            favorite_colors=['W', 'U', 'B', 'R', 'G'],
            skill_level=0.5
        )
        
    def _calculate_aggression(self, match_history: List[Dict]) -> float:
        """Calculer le niveau d'agressivité"""
        aggression_indicators = 0
        total_games = len(match_history)
        
        for match in match_history:
            deck = match.get('deck', {})
            archetype = deck.get('archetype', '').lower()
            
            # Indicateurs d'agressivité
            if any(keyword in archetype for keyword in ['aggro', 'burn', 'red', 'zoo']):
                aggression_indicators += 1
            elif any(keyword in archetype for keyword in ['control', 'combo', 'midrange']):
                aggression_indicators += 0.3
                
            # Analyser les cartes si disponibles
            cards = deck.get('cards', [])
            for card in cards:
                if self._is_aggressive_card(card):
                    aggression_indicators += 0.1
                    
        return min(aggression_indicators / max(total_games, 1), 1.0)
        
    def _calculate_control_preference(self, match_history: List[Dict]) -> float:
        """Calculer la préférence pour le contrôle"""
        control_indicators = 0
        total_games = len(match_history)
        
        for match in match_history:
            deck = match.get('deck', {})
            archetype = deck.get('archetype', '').lower()
            
            if any(keyword in archetype for keyword in ['control', 'permission']):
                control_indicators += 1
            elif 'midrange' in archetype:
                control_indicators += 0.6
                
            # Analyser les cartes de contrôle
            cards = deck.get('cards', [])
            for card in cards:
                if self._is_control_card(card):
                    control_indicators += 0.1
                    
        return min(control_indicators / max(total_games, 1), 1.0)
        
    def _calculate_combo_affinity(self, match_history: List[Dict]) -> float:
        """Calculer l'affinité pour les combos"""
        combo_indicators = 0
        total_games = len(match_history)
        
        for match in match_history:
            deck = match.get('deck', {})
            archetype = deck.get('archetype', '').lower()
            
            if any(keyword in archetype for keyword in ['combo', 'storm', 'twin']):
                combo_indicators += 1
                
            # Analyser les cartes de combo
            cards = deck.get('cards', [])
            for card in cards:
                if self._is_combo_card(card):
                    combo_indicators += 0.1
                    
        return min(combo_indicators / max(total_games, 1), 1.0)
        
    def _extract_color_preferences(self, match_history: List[Dict]) -> List[str]:
        """Extraire les préférences de couleur"""
        color_counts = Counter()
        
        for match in match_history:
            deck = match.get('deck', {})
            colors = deck.get('colors', [])
            
            for color in colors:
                color_counts[color] += 1
                
        # Retourner les couleurs les plus utilisées
        return [color for color, count in color_counts.most_common(3)]
        
    def _estimate_skill_level(self, match_history: List[Dict]) -> float:
        """Estimer le niveau de compétence"""
        if not match_history:
            return 0.5
            
        # Calculer le win rate
        wins = sum(1 for match in match_history if match.get('result') == 'win')
        total_games = len(match_history)
        win_rate = wins / total_games if total_games > 0 else 0.5
        
        # Analyser la complexité des decks joués
        complexity_score = 0
        for match in match_history:
            deck = match.get('deck', {})
            archetype = deck.get('archetype', '').lower()
            
            if any(keyword in archetype for keyword in ['combo', 'control']):
                complexity_score += 0.8
            elif 'midrange' in archetype:
                complexity_score += 0.6
            else:
                complexity_score += 0.4
                
        avg_complexity = complexity_score / max(total_games, 1)
        
        # Combiner win rate et complexité
        return (win_rate * 0.6 + avg_complexity * 0.4)
        
    def _analyze_play_style_tags(self, match_history: List[Dict]) -> List[str]:
        """Analyser les tags de style de jeu"""
        tags = []
        
        # Analyser les archétypes joués
        archetype_counts = Counter()
        for match in match_history:
            archetype = match.get('deck', {}).get('archetype', '')
            archetype_counts[archetype] += 1
            
        # Déterminer les tags basés sur les archétypes
        for archetype, count in archetype_counts.most_common():
            archetype_lower = archetype.lower()
            
            if 'aggro' in archetype_lower:
                tags.append('aggressive')
            elif 'control' in archetype_lower:
                tags.append('controlling')
            elif 'combo' in archetype_lower:
                tags.append('combo_player')
            elif 'midrange' in archetype_lower:
                tags.append('balanced')
                
        return list(set(tags))
        
    def _is_aggressive_card(self, card: Dict) -> bool:
        """Vérifier si une carte est agressive"""
        name = card.get('name', '').lower()
        cmc = card.get('cmc', 0)
        
        # Cartes agressives typiques
        aggressive_keywords = ['bolt', 'burn', 'shock', 'haste', 'goblin', 'elf']
        
        return (cmc <= 3 and any(keyword in name for keyword in aggressive_keywords))
        
    def _is_control_card(self, card: Dict) -> bool:
        """Vérifier si une carte est de contrôle"""
        name = card.get('name', '').lower()
        
        control_keywords = ['counter', 'draw', 'wrath', 'removal', 'planeswalker']
        
        return any(keyword in name for keyword in control_keywords)
        
    def _is_combo_card(self, card: Dict) -> bool:
        """Vérifier si une carte est de combo"""
        name = card.get('name', '').lower()
        
        combo_keywords = ['storm', 'twin', 'infinite', 'combo']
        
        return any(keyword in name for keyword in combo_keywords)
        
    def recommend_deck(self, player_id: str, format: str, budget: Optional[float] = None) -> List[DeckRecommendation]:
        """Recommander des decks personnalisés"""
        # Récupérer ou créer le profil
        if player_id not in self.user_profiles:
            # Créer un profil par défaut
            profile = self._create_default_profile(player_id)
        else:
            profile = self.user_profiles[player_id]
            
        # Obtenir le métagame actuel
        current_meta = self._get_current_metagame(format)
        
        # Calculer les scores de correspondance
        recommendations = []
        
        for archetype, meta_data in current_meta.items():
            match_score = self._calculate_style_match(profile, archetype, meta_data)
            
            # Appliquer le facteur budget
            if budget:
                match_score *= self._budget_factor(archetype, budget)
                
            # Prédire le winrate personnel
            expected_winrate = self._predict_personal_winrate(profile, archetype, meta_data)
            
            # Estimer la courbe d'apprentissage
            learning_curve = self._estimate_learning_curve(profile, archetype)
            
            # Estimer le prix
            price_estimate = self._estimate_deck_price(archetype)
            
            # Générer les raisons
            reasons = self._generate_recommendation_reasons(profile, archetype, match_score)
            
            # Suggestions de cartes
            suggested_cards = self._suggest_cards_for_profile(profile, archetype)
            
            # Suggestions de sideboard
            sideboard_suggestions = self._optimize_sideboard_for_player(profile, archetype)
            
            # Positionnement méta
            meta_positioning = self._analyze_meta_positioning(archetype, current_meta)
            
            recommendation = DeckRecommendation(
                archetype=archetype,
                match_score=match_score,
                expected_winrate=expected_winrate,
                learning_curve=learning_curve,
                price_estimate=price_estimate,
                reasons=reasons,
                suggested_cards=suggested_cards,
                sideboard_suggestions=sideboard_suggestions,
                meta_positioning=meta_positioning
            )
            
            recommendations.append(recommendation)
            
        # Trier par score de correspondance
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        return recommendations[:5]
        
    def _calculate_style_match(self, profile: PlayerProfile, archetype: str, meta_data: Dict) -> float:
        """Calculer la correspondance de style"""
        score = 0.0
        
        # Analyser l'archétype
        archetype_lower = archetype.lower()
        
        # Score d'agressivité
        if 'aggro' in archetype_lower:
            score += profile.aggression_level * 0.3
        elif 'control' in archetype_lower:
            score += profile.control_preference * 0.3
        elif 'combo' in archetype_lower:
            score += profile.combo_affinity * 0.3
        else:  # midrange
            score += (1 - abs(profile.aggression_level - 0.5)) * 0.3
            
        # Score de couleur
        archetype_colors = self._get_archetype_colors(archetype)
        color_match = len(set(profile.favorite_colors) & set(archetype_colors)) / max(len(archetype_colors), 1)
        score += color_match * 0.2
        
        # Score de performance méta
        win_rate = meta_data.get('win_rate', 0.5)
        score += win_rate * 0.2
        
        # Score de popularité (inverse pour éviter les decks trop populaires)
        popularity = meta_data.get('popularity', 0.5)
        score += (1 - popularity) * 0.1
        
        # Bonus pour les tags de style
        if any(tag in archetype_lower for tag in profile.play_style_tags):
            score += 0.2
            
        return min(score, 1.0)
        
    def _budget_factor(self, archetype: str, budget: float) -> float:
        """Calculer le facteur budget"""
        deck_price = self._estimate_deck_price(archetype)
        
        if deck_price <= budget:
            return 1.0
        elif deck_price <= budget * 1.5:
            return 0.8
        elif deck_price <= budget * 2:
            return 0.5
        else:
            return 0.2
            
    def _predict_personal_winrate(self, profile: PlayerProfile, archetype: str, meta_data: Dict) -> float:
        """Prédire le winrate personnel"""
        base_winrate = meta_data.get('win_rate', 0.5)
        
        # Ajuster selon le niveau de compétence
        skill_bonus = (profile.skill_level - 0.5) * 0.1
        
        # Ajuster selon la correspondance de style
        style_match = self._calculate_style_match(profile, archetype, meta_data)
        style_bonus = (style_match - 0.5) * 0.05
        
        return min(max(base_winrate + skill_bonus + style_bonus, 0.3), 0.8)
        
    def _estimate_learning_curve(self, profile: PlayerProfile, archetype: str) -> float:
        """Estimer la courbe d'apprentissage"""
        base_difficulty = self._get_archetype_difficulty(archetype)
        
        # Ajuster selon le niveau de compétence
        skill_factor = 1 - profile.skill_level * 0.5
        
        # Ajuster selon l'expérience avec le style
        style_familiarity = 0.5
        if 'combo' in archetype.lower() and profile.combo_affinity > 0.7:
            style_familiarity = 0.8
        elif 'control' in archetype.lower() and profile.control_preference > 0.7:
            style_familiarity = 0.8
        elif 'aggro' in archetype.lower() and profile.aggression_level > 0.7:
            style_familiarity = 0.8
            
        return base_difficulty * skill_factor * (1 - style_familiarity * 0.3)
        
    def _get_current_metagame(self, format: str) -> Dict:
        """Récupérer le métagame actuel"""
        # Placeholder - en pratique, récupérer depuis la base de données
        return {
            'Burn': {'win_rate': 0.52, 'popularity': 0.15},
            'Control': {'win_rate': 0.48, 'popularity': 0.12},
            'Combo': {'win_rate': 0.55, 'popularity': 0.08},
            'Midrange': {'win_rate': 0.50, 'popularity': 0.20}
        }
        
    def _get_archetype_colors(self, archetype: str) -> List[str]:
        """Obtenir les couleurs d'un archétype"""
        # Mapping simplifié
        color_mapping = {
            'burn': ['R'],
            'control': ['W', 'U'],
            'combo': ['U', 'R'],
            'midrange': ['B', 'G']
        }
        
        archetype_lower = archetype.lower()
        for key, colors in color_mapping.items():
            if key in archetype_lower:
                return colors
                
        return ['W', 'U', 'B', 'R', 'G']  # Toutes les couleurs par défaut
        
    def _estimate_deck_price(self, archetype: str) -> float:
        """Estimer le prix d'un deck"""
        # Prix estimés par archétype
        price_estimates = {
            'burn': 150.0,
            'control': 800.0,
            'combo': 600.0,
            'midrange': 400.0
        }
        
        archetype_lower = archetype.lower()
        for key, price in price_estimates.items():
            if key in archetype_lower:
                return price
                
        return 500.0  # Prix par défaut
        
    def _get_archetype_difficulty(self, archetype: str) -> float:
        """Obtenir la difficulté d'un archétype"""
        difficulty_map = {
            'burn': 0.2,
            'aggro': 0.3,
            'midrange': 0.5,
            'control': 0.8,
            'combo': 0.9
        }
        
        archetype_lower = archetype.lower()
        for key, difficulty in difficulty_map.items():
            if key in archetype_lower:
                return difficulty
                
        return 0.5  # Difficulté par défaut
        
    def _generate_recommendation_reasons(self, profile: PlayerProfile, archetype: str, match_score: float) -> List[str]:
        """Générer les raisons de la recommandation"""
        reasons = []
        
        if match_score > 0.8:
            reasons.append("Excellent match avec votre style de jeu")
        elif match_score > 0.6:
            reasons.append("Bon match avec vos préférences")
            
        archetype_lower = archetype.lower()
        
        if 'aggro' in archetype_lower and profile.aggression_level > 0.7:
            reasons.append("Correspond à votre style agressif")
        elif 'control' in archetype_lower and profile.control_preference > 0.7:
            reasons.append("Correspond à votre préférence pour le contrôle")
        elif 'combo' in archetype_lower and profile.combo_affinity > 0.7:
            reasons.append("Correspond à votre affinité pour les combos")
            
        return reasons
        
    def _suggest_cards_for_profile(self, profile: PlayerProfile, archetype: str) -> List[Dict]:
        """Suggérer des cartes pour le profil"""
        # Suggestions simplifiées
        return [
            {'name': 'Suggested Card', 'reason': 'Fits your playstyle'}
        ]
        
    def _optimize_sideboard_for_player(self, profile: PlayerProfile, archetype: str) -> List[Dict]:
        """Optimiser le sideboard pour le joueur"""
        # Suggestions simplifiées
        return [
            {'name': 'Sideboard Card', 'reason': 'Good against current meta'}
        ]
        
    def _analyze_meta_positioning(self, archetype: str, current_meta: Dict) -> Dict:
        """Analyser le positionnement méta"""
        return {
            'tier': 'Tier 1',
            'favorable_matchups': ['Archetype A'],
            'unfavorable_matchups': ['Archetype B'],
            'meta_share': 0.15
        } 