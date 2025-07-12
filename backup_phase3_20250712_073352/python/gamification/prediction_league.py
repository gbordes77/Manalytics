"""
Système de ligue de prédictions
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PredictionContest:
    """Concours de prédiction"""
    contest_id: str
    tournament_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    predictions: Dict[str, Dict] = field(default_factory=dict)
    results: Optional[Dict] = None
    prize_pool: int = 0
    status: str = "active"  # active, ended, evaluated
    
class PredictionLeague:
    """Système de ligue de prédictions"""
    
    def __init__(self):
        self.contests = {}
        self.user_predictions = {}
        self.leaderboard = {}
        
    async def create_contest(self, contest_config: Dict) -> PredictionContest:
        """Créer un nouveau concours"""
        contest = PredictionContest(
            contest_id=contest_config['contest_id'],
            tournament_id=contest_config['tournament_id'],
            name=contest_config['name'],
            description=contest_config['description'],
            start_date=contest_config['start_date'],
            end_date=contest_config['end_date'],
            prize_pool=contest_config.get('prize_pool', 0)
        )
        
        self.contests[contest.contest_id] = contest
        return contest
        
    async def submit_prediction(self, user_id: str, contest_id: str, prediction: Dict) -> bool:
        """Soumettre une prédiction"""
        if contest_id not in self.contests:
            return False
            
        contest = self.contests[contest_id]
        
        # Vérifier si le concours est actif
        if contest.status != "active":
            return False
            
        # Vérifier la date limite
        if datetime.now() > contest.end_date:
            return False
            
        # Enregistrer la prédiction
        contest.predictions[user_id] = {
            'prediction': prediction,
            'timestamp': datetime.now(),
            'score': 0
        }
        
        return True
        
    async def evaluate_contest(self, contest_id: str, actual_results: Dict) -> Dict:
        """Évaluer un concours"""
        if contest_id not in self.contests:
            return {}
            
        contest = self.contests[contest_id]
        contest.results = actual_results
        contest.status = "evaluated"
        
        # Calculer les scores
        scores = {}
        for user_id, prediction_data in contest.predictions.items():
            score = self._calculate_prediction_score(
                prediction_data['prediction'], 
                actual_results
            )
            prediction_data['score'] = score
            scores[user_id] = score
            
        # Trier par score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'contest_id': contest_id,
            'leaderboard': sorted_scores,
            'total_participants': len(scores)
        }
        
    def _calculate_prediction_score(self, prediction: Dict, actual: Dict) -> float:
        """Calculer le score d'une prédiction"""
        score = 0.0
        
        # Score basé sur la précision des prédictions
        if 'top_decks' in prediction and 'top_decks' in actual:
            predicted_decks = set(prediction['top_decks'])
            actual_decks = set(actual['top_decks'])
            
            # Intersection des prédictions correctes
            correct_predictions = predicted_decks.intersection(actual_decks)
            score += len(correct_predictions) * 10
            
        # Bonus pour les prédictions difficiles
        if 'upset_predictions' in prediction:
            for upset in prediction['upset_predictions']:
                if upset in actual.get('upsets', []):
                    score += 25
                    
        return score 