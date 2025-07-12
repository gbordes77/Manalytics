"""
Système d'achievements pour la gamification
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Achievement:
    """Définition d'un achievement"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    requirements: Dict[str, Any]
    category: str = "general"
    rarity: str = "common"  # common, rare, epic, legendary
    unlocked_by: List[str] = field(default_factory=list)
    
class AchievementSystem:
    """Système de gestion des achievements"""
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.user_achievements = {}
        
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialiser les achievements par défaut"""
        achievements = {}
        
        # Achievements de prédiction
        achievements['oracle'] = Achievement(
            id='oracle',
            name='Oracle',
            description='Réussir 5 prédictions consécutives',
            icon='🔮',
            points=100,
            requirements={'prediction_streak': 5},
            category='prediction',
            rarity='rare'
        )
        
        achievements['prophet'] = Achievement(
            id='prophet',
            name='Prophète',
            description='Réussir 10 prédictions consécutives',
            icon='🧙‍♂️',
            points=250,
            requirements={'prediction_streak': 10},
            category='prediction',
            rarity='epic'
        )
        
        # Achievements d'innovation
        achievements['pioneer'] = Achievement(
            id='pioneer',
            name='Pionnier',
            description='Créer un deck innovant avec score > 80%',
            icon='🚀',
            points=150,
            requirements={'innovation_score': 0.8},
            category='innovation',
            rarity='rare'
        )
        
        # Achievements d'activité
        achievements['dedicated'] = Achievement(
            id='dedicated',
            name='Dédié',
            description='Se connecter 7 jours consécutifs',
            icon='💪',
            points=75,
            requirements={'days_streak': 7},
            category='activity',
            rarity='common'
        )
        
        # Achievements d'expertise
        achievements['expert'] = Achievement(
            id='expert',
            name='Expert',
            description='Atteindre 1000 points',
            icon='🏆',
            points=200,
            requirements={'total_points': 1000},
            category='expertise',
            rarity='epic'
        )
        
        return achievements
        
    async def check_achievement(self, user_id: str, achievement_id: str, user_data: Dict) -> Optional[Achievement]:
        """Vérifier si un achievement est débloqué"""
        if achievement_id not in self.achievements:
            return None
            
        achievement = self.achievements[achievement_id]
        
        # Vérifier si déjà débloqué
        if user_id in self.user_achievements:
            if achievement_id in self.user_achievements[user_id]:
                return None
                
        # Vérifier les requirements
        if self._check_requirements(achievement.requirements, user_data):
            await self._unlock_achievement(user_id, achievement_id)
            return achievement
            
        return None
        
    def _check_requirements(self, requirements: Dict, user_data: Dict) -> bool:
        """Vérifier si les requirements sont satisfaits"""
        for key, required_value in requirements.items():
            if key not in user_data:
                return False
                
            user_value = user_data[key]
            
            if isinstance(required_value, (int, float)):
                if user_value < required_value:
                    return False
            elif isinstance(required_value, str):
                if user_value != required_value:
                    return False
                    
        return True
        
    async def _unlock_achievement(self, user_id: str, achievement_id: str):
        """Débloquer un achievement"""
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
            
        self.user_achievements[user_id].append(achievement_id)
        self.achievements[achievement_id].unlocked_by.append(user_id)
        
        logger.info(f"Achievement '{achievement_id}' unlocked for user {user_id}")
        
    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Récupérer les achievements d'un utilisateur"""
        if user_id not in self.user_achievements:
            return []
            
        return [
            self.achievements[achievement_id] 
            for achievement_id in self.user_achievements[user_id]
        ]
        
    def get_available_achievements(self, user_id: str) -> List[Achievement]:
        """Récupérer les achievements disponibles"""
        unlocked = self.user_achievements.get(user_id, [])
        return [
            achievement for achievement in self.achievements.values()
            if achievement.id not in unlocked
        ] 