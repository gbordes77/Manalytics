"""
Moteur de gamification pour l'engagement utilisateur
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json

from .achievement_system import AchievementSystem, Achievement
from .prediction_league import PredictionLeague, PredictionContest
from .leaderboard import Leaderboard, LeaderboardEntry

logger = logging.getLogger(__name__)

@dataclass
class UserStats:
    """Statistiques utilisateur pour la gamification"""
    user_id: str
    total_points: int = 0
    level: int = 1
    experience: int = 0
    achievements: List[str] = field(default_factory=list)
    prediction_streak: int = 0
    best_prediction_streak: int = 0
    deck_innovations: int = 0
    tournaments_predicted: int = 0
    correct_predictions: int = 0
    total_predictions: int = 0
    last_activity: Optional[datetime] = None
    badges: List[str] = field(default_factory=list)
    
    @property
    def prediction_accuracy(self) -> float:
        """Précision des prédictions"""
        if self.total_predictions == 0:
            return 0.0
        return self.correct_predictions / self.total_predictions
    
    @property
    def experience_to_next_level(self) -> int:
        """Expérience nécessaire pour le niveau suivant"""
        return self._calculate_level_requirement(self.level + 1) - self.experience
    
    def _calculate_level_requirement(self, level: int) -> int:
        """Calculer l'expérience requise pour un niveau"""
        return level * 100 + (level - 1) * 50

@dataclass
class UserAction:
    """Action utilisateur pour tracking"""
    user_id: str
    action_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    points_earned: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)

class GamificationEngine:
    """Moteur de gamification principal"""
    
    def __init__(self):
        self.achievement_system = AchievementSystem()
        self.prediction_league = PredictionLeague()
        self.leaderboard = Leaderboard()
        self.user_stats = {}
        self.active_contests = {}
        self.point_values = self._initialize_point_values()
        
    def _initialize_point_values(self) -> Dict[str, int]:
        """Initialiser les valeurs de points"""
        return {
            'deck_innovation': 50,
            'prediction_success': 25,
            'tournament_prediction': 15,
            'daily_login': 5,
            'deck_analysis': 10,
            'share_content': 20,
            'help_community': 30,
            'perfect_prediction': 100,
            'upset_prediction': 75,
            'meta_call': 60
        }
        
    async def track_user_action(self, user_id: str, action_type: str, action_data: Dict) -> UserAction:
        """Tracker une action utilisateur"""
        logger.info(f"Tracking action: {action_type} for user {user_id}")
        
        # Récupérer ou créer les stats utilisateur
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id)
            
        user_stats = self.user_stats[user_id]
        
        # Calculer les points gagnés
        points_earned = self._calculate_points(action_type, action_data)
        
        # Vérifier les achievements
        achievements_unlocked = await self._check_achievements(user_id, action_type, action_data)
        
        # Mettre à jour les stats
        await self._update_user_stats(user_id, action_type, action_data, points_earned)
        
        # Créer l'action
        action = UserAction(
            user_id=user_id,
            action_type=action_type,
            data=action_data,
            points_earned=points_earned,
            achievements_unlocked=achievements_unlocked
        )
        
        # Mettre à jour le leaderboard
        await self.leaderboard.update_user_score(user_id, user_stats.total_points)
        
        return action
        
    def _calculate_points(self, action_type: str, action_data: Dict) -> int:
        """Calculer les points pour une action"""
        base_points = self.point_values.get(action_type, 0)
        
        # Modificateurs basés sur les données
        multiplier = 1.0
        
        if action_type == 'prediction_success':
            confidence = action_data.get('confidence', 0.5)
            multiplier = 1 + confidence  # Bonus pour les prédictions confiantes
            
        elif action_type == 'deck_innovation':
            innovation_score = action_data.get('innovation_score', 0.5)
            multiplier = 1 + innovation_score
            
        elif action_type == 'tournament_prediction':
            difficulty = action_data.get('difficulty', 'normal')
            if difficulty == 'hard':
                multiplier = 1.5
            elif difficulty == 'expert':
                multiplier = 2.0
                
        return int(base_points * multiplier)
        
    async def _check_achievements(self, user_id: str, action_type: str, action_data: Dict) -> List[str]:
        """Vérifier les achievements débloqués"""
        achievements_earned = []
        user_stats = self.user_stats[user_id]
        
        # Achievement pour les prédictions
        if action_type == 'prediction_success':
            # Streak achievements
            if user_stats.prediction_streak >= 5:
                achievement = await self.achievement_system.check_achievement(
                    user_id, 'oracle', {'streak': user_stats.prediction_streak}
                )
                if achievement:
                    achievements_earned.append('oracle')
                    
            if user_stats.prediction_streak >= 10:
                achievement = await self.achievement_system.check_achievement(
                    user_id, 'prophet', {'streak': user_stats.prediction_streak}
                )
                if achievement:
                    achievements_earned.append('prophet')
                    
        # Achievement pour l'innovation
        elif action_type == 'deck_innovation':
            innovation_score = action_data.get('innovation_score', 0)
            if innovation_score > 0.8:
                achievement = await self.achievement_system.check_achievement(
                    user_id, 'pioneer', {'innovation_score': innovation_score}
                )
                if achievement:
                    achievements_earned.append('pioneer')
                    
        # Achievement pour l'activité
        elif action_type == 'daily_login':
            days_streak = action_data.get('days_streak', 1)
            if days_streak >= 7:
                achievement = await self.achievement_system.check_achievement(
                    user_id, 'dedicated', {'days_streak': days_streak}
                )
                if achievement:
                    achievements_earned.append('dedicated')
                    
        # Achievement pour l'expertise
        if user_stats.total_points >= 1000:
            achievement = await self.achievement_system.check_achievement(
                user_id, 'expert', {'total_points': user_stats.total_points}
            )
            if achievement:
                achievements_earned.append('expert')
                
        return achievements_earned
        
    async def _update_user_stats(self, user_id: str, action_type: str, action_data: Dict, points_earned: int):
        """Mettre à jour les statistiques utilisateur"""
        user_stats = self.user_stats[user_id]
        
        # Mettre à jour les points et l'expérience
        user_stats.total_points += points_earned
        user_stats.experience += points_earned
        user_stats.last_activity = datetime.now()
        
        # Calculer le nouveau niveau
        new_level = self._calculate_level(user_stats.experience)
        if new_level > user_stats.level:
            user_stats.level = new_level
            # Bonus de niveau
            await self._handle_level_up(user_id, new_level)
            
        # Mettre à jour les stats spécifiques
        if action_type == 'prediction_success':
            user_stats.correct_predictions += 1
            user_stats.total_predictions += 1
            user_stats.prediction_streak += 1
            
            if user_stats.prediction_streak > user_stats.best_prediction_streak:
                user_stats.best_prediction_streak = user_stats.prediction_streak
                
        elif action_type == 'prediction_failure':
            user_stats.total_predictions += 1
            user_stats.prediction_streak = 0
            
        elif action_type == 'deck_innovation':
            user_stats.deck_innovations += 1
            
        elif action_type == 'tournament_prediction':
            user_stats.tournaments_predicted += 1
            
    def _calculate_level(self, experience: int) -> int:
        """Calculer le niveau basé sur l'expérience"""
        level = 1
        while experience >= self._calculate_level_requirement(level):
            level += 1
        return level - 1
        
    def _calculate_level_requirement(self, level: int) -> int:
        """Calculer l'expérience requise pour un niveau"""
        return level * 100 + (level - 1) * 50
        
    async def _handle_level_up(self, user_id: str, new_level: int):
        """Gérer la montée de niveau"""
        logger.info(f"User {user_id} reached level {new_level}")
        
        # Bonus de niveau
        bonus_points = new_level * 10
        self.user_stats[user_id].total_points += bonus_points
        
        # Débloquer des badges spéciaux
        if new_level == 10:
            self.user_stats[user_id].badges.append('veteran')
        elif new_level == 25:
            self.user_stats[user_id].badges.append('master')
        elif new_level == 50:
            self.user_stats[user_id].badges.append('legend')
            
    async def create_prediction_contest(self, tournament_id: str, contest_config: Dict) -> PredictionContest:
        """Créer un concours de prédictions"""
        contest = PredictionContest(
            tournament_id=tournament_id,
            prize_pool=contest_config.get('prize_pool', 1000),
            scoring_rules=contest_config.get('scoring_rules', {
                'exact_top8': 100,
                'archetype_in_top8': 25,
                'winner_prediction': 200,
                'biggest_upset': 150
            }),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=1)
        )
        
        self.active_contests[tournament_id] = contest
        return contest
        
    async def submit_prediction(self, user_id: str, tournament_id: str, prediction: Dict) -> bool:
        """Soumettre une prédiction pour un concours"""
        if tournament_id not in self.active_contests:
            return False
            
        contest = self.active_contests[tournament_id]
        success = await contest.submit_prediction(user_id, prediction)
        
        if success:
            await self.track_user_action(user_id, 'tournament_prediction', {
                'tournament_id': tournament_id,
                'prediction': prediction
            })
            
        return success
        
    async def evaluate_predictions(self, tournament_id: str, results: Dict) -> Dict:
        """Évaluer les prédictions d'un tournoi"""
        if tournament_id not in self.active_contests:
            return {}
            
        contest = self.active_contests[tournament_id]
        evaluation_results = await contest.evaluate_predictions(results)
        
        # Distribuer les points et achievements
        for user_id, score in evaluation_results.get('scores', {}).items():
            if score > 0:
                await self.track_user_action(user_id, 'prediction_success', {
                    'tournament_id': tournament_id,
                    'score': score,
                    'confidence': score / 100  # Normaliser
                })
            else:
                await self.track_user_action(user_id, 'prediction_failure', {
                    'tournament_id': tournament_id
                })
                
        return evaluation_results
        
    async def get_user_profile(self, user_id: str) -> Dict:
        """Récupérer le profil gamification d'un utilisateur"""
        if user_id not in self.user_stats:
            return {}
            
        user_stats = self.user_stats[user_id]
        
        # Récupérer les achievements
        achievements = await self.achievement_system.get_user_achievements(user_id)
        
        # Récupérer la position au leaderboard
        leaderboard_position = await self.leaderboard.get_user_position(user_id)
        
        return {
            'user_id': user_id,
            'level': user_stats.level,
            'experience': user_stats.experience,
            'experience_to_next_level': user_stats.experience_to_next_level,
            'total_points': user_stats.total_points,
            'prediction_accuracy': user_stats.prediction_accuracy,
            'prediction_streak': user_stats.prediction_streak,
            'best_prediction_streak': user_stats.best_prediction_streak,
            'deck_innovations': user_stats.deck_innovations,
            'tournaments_predicted': user_stats.tournaments_predicted,
            'achievements': achievements,
            'badges': user_stats.badges,
            'leaderboard_position': leaderboard_position,
            'last_activity': user_stats.last_activity.isoformat() if user_stats.last_activity else None
        }
        
    async def get_leaderboard(self, period: str = 'all_time', limit: int = 10) -> List[Dict]:
        """Récupérer le leaderboard"""
        entries = await self.leaderboard.get_top_users(period, limit)
        
        leaderboard_data = []
        for entry in entries:
            user_profile = await self.get_user_profile(entry.user_id)
            leaderboard_data.append({
                'position': entry.position,
                'user_id': entry.user_id,
                'score': entry.score,
                'level': user_profile.get('level', 1),
                'badges': user_profile.get('badges', []),
                'prediction_accuracy': user_profile.get('prediction_accuracy', 0)
            })
            
        return leaderboard_data
        
    async def get_active_contests(self) -> List[Dict]:
        """Récupérer les concours actifs"""
        active_contests = []
        
        for tournament_id, contest in self.active_contests.items():
            if contest.is_active():
                active_contests.append({
                    'tournament_id': tournament_id,
                    'prize_pool': contest.prize_pool,
                    'participants': len(contest.predictions),
                    'end_time': contest.end_time.isoformat(),
                    'scoring_rules': contest.scoring_rules
                })
                
        return active_contests
        
    async def get_user_achievements(self, user_id: str) -> List[Dict]:
        """Récupérer les achievements d'un utilisateur"""
        return await self.achievement_system.get_user_achievements(user_id)
        
    async def suggest_next_actions(self, user_id: str) -> List[Dict]:
        """Suggérer les prochaines actions pour un utilisateur"""
        suggestions = []
        
        if user_id not in self.user_stats:
            return suggestions
            
        user_stats = self.user_stats[user_id]
        
        # Suggérer des prédictions si aucune récente
        if user_stats.last_activity and (datetime.now() - user_stats.last_activity).days > 1:
            suggestions.append({
                'action': 'make_prediction',
                'title': 'Faire une prédiction',
                'description': 'Prédisez les résultats du prochain tournoi',
                'points': 25,
                'difficulty': 'easy'
            })
            
        # Suggérer l'innovation si peu d'innovations
        if user_stats.deck_innovations < 5:
            suggestions.append({
                'action': 'innovate_deck',
                'title': 'Innover un deck',
                'description': 'Créez ou modifiez un deck unique',
                'points': 50,
                'difficulty': 'medium'
            })
            
        # Suggérer des défis basés sur le niveau
        if user_stats.level < 10:
            suggestions.append({
                'action': 'daily_challenge',
                'title': 'Défi quotidien',
                'description': 'Complétez le défi du jour',
                'points': 30,
                'difficulty': 'easy'
            })
            
        return suggestions
        
    async def get_user_statistics(self, user_id: str) -> Dict:
        """Récupérer les statistiques détaillées d'un utilisateur"""
        if user_id not in self.user_stats:
            return {}
            
        user_stats = self.user_stats[user_id]
        
        return {
            'overview': {
                'level': user_stats.level,
                'total_points': user_stats.total_points,
                'experience': user_stats.experience,
                'achievements_count': len(user_stats.achievements)
            },
            'predictions': {
                'total': user_stats.total_predictions,
                'correct': user_stats.correct_predictions,
                'accuracy': user_stats.prediction_accuracy,
                'current_streak': user_stats.prediction_streak,
                'best_streak': user_stats.best_prediction_streak
            },
            'innovation': {
                'deck_innovations': user_stats.deck_innovations,
                'tournaments_predicted': user_stats.tournaments_predicted
            },
            'engagement': {
                'last_activity': user_stats.last_activity.isoformat() if user_stats.last_activity else None,
                'badges': user_stats.badges
            }
        } 