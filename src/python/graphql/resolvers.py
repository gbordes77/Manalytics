"""
Résolveurs GraphQL
"""

import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime

@strawberry.type
class Archetype:
    """Type GraphQL pour un archétype"""
    name: str
    format: str
    share: float
    winrate: float
    trend: str

@strawberry.type
class Tournament:
    """Type GraphQL pour un tournoi"""
    id: str
    name: str
    format: str
    date: datetime
    participants: int

@strawberry.type
class Prediction:
    """Type GraphQL pour une prédiction"""
    id: str
    archetype: str
    confidence: float
    date: datetime

class QueryResolver:
    """Résolveurs pour les requêtes GraphQL"""
    
    @strawberry.field
    def get_metagame(self, format: str) -> List[Archetype]:
        """Récupérer le métagame"""
        # Données de test
        return [
            Archetype(
                name="Aggro",
                format=format,
                share=0.25,
                winrate=0.52,
                trend="rising"
            ),
            Archetype(
                name="Control",
                format=format,
                share=0.20,
                winrate=0.48,
                trend="stable"
            )
        ]
    
    @strawberry.field
    def get_tournaments(self, format: Optional[str] = None) -> List[Tournament]:
        """Récupérer les tournois"""
        return [
            Tournament(
                id="1",
                name="Test Tournament",
                format=format or "Standard",
                date=datetime.now(),
                participants=100
            )
        ]

class MutationResolver:
    """Résolveurs pour les mutations GraphQL"""
    
    @strawberry.mutation
    def create_prediction(self, archetype: str, confidence: float) -> Prediction:
        """Créer une prédiction"""
        return Prediction(
            id="pred_1",
            archetype=archetype,
            confidence=confidence,
            date=datetime.now()
        )

class SubscriptionResolver:
    """Résolveurs pour les subscriptions GraphQL"""
    
    @strawberry.subscription
    async def metagame_updates(self, format: str):
        """Subscription pour les mises à jour de métagame"""
        # Simulation d'une mise à jour
        yield Archetype(
            name="New Archetype",
            format=format,
            share=0.15,
            winrate=0.55,
            trend="emerging"
        ) 