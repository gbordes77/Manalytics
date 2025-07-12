"""
Système de leaderboard
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LeaderboardEntry:
    """Entrée du leaderboard"""
    user_id: str
    score: int
    rank: int
    username: str = ""
    avatar: str = ""
    
class Leaderboard:
    """Système de leaderboard"""
    
    def __init__(self):
        self.entries = {}
        self.rankings = []
        
    async def update_user_score(self, user_id: str, score: int):
        """Mettre à jour le score d'un utilisateur"""
        self.entries[user_id] = LeaderboardEntry(
            user_id=user_id,
            score=score,
            rank=0
        )
        
        await self._update_rankings()
        
    async def _update_rankings(self):
        """Mettre à jour les classements"""
        # Trier par score décroissant
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda x: x.score,
            reverse=True
        )
        
        # Assigner les rangs
        for i, entry in enumerate(sorted_entries):
            entry.rank = i + 1
            
        self.rankings = sorted_entries
        
    def get_top_users(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Récupérer le top des utilisateurs"""
        return self.rankings[:limit]
        
    def get_user_rank(self, user_id: str) -> Optional[int]:
        """Récupérer le rang d'un utilisateur"""
        if user_id in self.entries:
            return self.entries[user_id].rank
        return None 