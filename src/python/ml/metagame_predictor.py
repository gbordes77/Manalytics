"""
Modèle de prédiction de métagame avec LSTM
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import pickle

logger = logging.getLogger(__name__)

@dataclass
class MetagamePrediction:
    """Résultat de prédiction du métagame"""
    format: str
    predicted_shares: Dict[str, float]
    emerging_decks: List[Dict]
    declining_archetypes: List[Dict]
    confidence: float
    prediction_date: datetime
    weeks_ahead: int

class MetagameLSTM(nn.Module):
    """LSTM pour prédire l'évolution du métagame"""
    
    def __init__(self, num_archetypes: int, hidden_size: int = 256, num_layers: int = 3):
        super().__init__()
        self.num_archetypes = num_archetypes
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Couche d'entrée : share, winrate, popularity pour chaque archétype
        input_size = num_archetypes * 3
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0
        )
        
        # Couches de sortie
        self.output_layers = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, num_archetypes),
            nn.Softmax(dim=1)
        )
        
        # Couche pour prédire la confiance
        self.confidence_layer = nn.Sequential(
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor, h: Optional[Tuple] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        Args:
            x: (batch_size, seq_len, input_size)
            h: hidden state
        Returns:
            predictions: (batch_size, num_archetypes)
            confidence: (batch_size, 1)
        """
        lstm_out, hidden = self.lstm(x, h)
        
        # Utiliser la dernière sortie pour la prédiction
        last_output = lstm_out[:, -1, :]
        
        predictions = self.output_layers(last_output)
        confidence = self.confidence_layer(last_output)
        
        return predictions, confidence

class MetagamePredictor:
    """Prédicteur de métagame basé sur l'IA"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.archetype_encoder = {}
        self.archetype_decoder = {}
        self.scaler = None
        self.sequence_length = 12  # 12 semaines d'historique
        
        if model_path:
            self.load_model(model_path)
            
    def initialize_model(self, archetypes: List[str]) -> None:
        """Initialiser le modèle avec les archétypes"""
        # Créer les encodeurs/décodeurs
        self.archetype_encoder = {arch: i for i, arch in enumerate(archetypes)}
        self.archetype_decoder = {i: arch for i, arch in enumerate(archetypes)}
        
        # Créer le modèle
        self.model = MetagameLSTM(num_archetypes=len(archetypes))
        
        logger.info(f"Modèle initialisé avec {len(archetypes)} archétypes")
        
    def prepare_training_data(self, historical_data: List[Dict]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Préparer les données d'entraînement"""
        sequences = []
        targets = []
        
        # Trier par date
        historical_data = sorted(historical_data, key=lambda x: x['date'])
        
        for i in range(len(historical_data) - self.sequence_length):
            # Séquence d'entrée
            sequence = []
            for j in range(i, i + self.sequence_length):
                week_data = self._encode_week_data(historical_data[j])
                sequence.append(week_data)
            
            # Cible (semaine suivante)
            target = self._encode_target(historical_data[i + self.sequence_length])
            
            sequences.append(sequence)
            targets.append(target)
            
        return torch.tensor(sequences, dtype=torch.float32), torch.tensor(targets, dtype=torch.float32)
        
    def _encode_week_data(self, week_data: Dict) -> List[float]:
        """Encoder les données d'une semaine"""
        encoded = []
        
        for archetype in self.archetype_decoder.values():
            # Share, winrate, popularity
            share = week_data.get('shares', {}).get(archetype, 0.0)
            winrate = week_data.get('winrates', {}).get(archetype, 0.5)
            popularity = week_data.get('popularity', {}).get(archetype, 0.0)
            
            encoded.extend([share, winrate, popularity])
            
        return encoded
        
    def _encode_target(self, target_data: Dict) -> List[float]:
        """Encoder la cible"""
        target = []
        
        for archetype in self.archetype_decoder.values():
            share = target_data.get('shares', {}).get(archetype, 0.0)
            target.append(share)
            
        return target
        
    def train(self, historical_data: List[Dict], epochs: int = 100, lr: float = 0.001) -> Dict:
        """Entraîner le modèle"""
        if not self.model:
            raise ValueError("Modèle non initialisé")
            
        # Préparer les données
        X, y = self.prepare_training_data(historical_data)
        
        if len(X) == 0:
            raise ValueError("Pas assez de données pour l'entraînement")
            
        # Optimiseur et fonction de perte
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        # Entraînement
        losses = []
        
        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()
            
            predictions, confidence = self.model(X)
            loss = criterion(predictions, y)
            
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}, Loss: {loss.item():.4f}")
                
        return {
            'final_loss': losses[-1],
            'training_samples': len(X),
            'epochs': epochs
        }
        
    def predict_next_week(self, current_meta: Dict, weeks_ahead: int = 1) -> MetagamePrediction:
        """Prédire la composition du métagame pour les semaines suivantes"""
        if not self.model:
            raise ValueError("Modèle non entraîné")
            
        self.model.eval()
        
        # Préparer les données d'entrée
        input_sequence = self._prepare_prediction_input(current_meta)
        
        with torch.no_grad():
            predictions, confidence = self.model(input_sequence)
            
        # Décoder les prédictions
        predicted_shares = self._decode_predictions(predictions[0])
        
        # Analyser les changements
        emerging_decks = self._detect_emerging_patterns(current_meta, predicted_shares)
        declining_archetypes = self._detect_declining_patterns(current_meta, predicted_shares)
        
        return MetagamePrediction(
            format=current_meta.get('format', 'unknown'),
            predicted_shares=predicted_shares,
            emerging_decks=emerging_decks,
            declining_archetypes=declining_archetypes,
            confidence=confidence[0].item(),
            prediction_date=datetime.now(),
            weeks_ahead=weeks_ahead
        )
        
    def _prepare_prediction_input(self, current_meta: Dict) -> torch.Tensor:
        """Préparer l'entrée pour la prédiction"""
        # Pour la prédiction, on utilise les données actuelles répétées
        # En pratique, on devrait avoir l'historique complet
        sequence = []
        
        for _ in range(self.sequence_length):
            week_data = self._encode_week_data(current_meta)
            sequence.append(week_data)
            
        return torch.tensor([sequence], dtype=torch.float32)
        
    def _decode_predictions(self, predictions: torch.Tensor) -> Dict[str, float]:
        """Décoder les prédictions"""
        decoded = {}
        
        for i, archetype in self.archetype_decoder.items():
            decoded[archetype] = predictions[i].item()
            
        return decoded
        
    def _detect_emerging_patterns(self, current_meta: Dict, predicted_shares: Dict) -> List[Dict]:
        """Détecter les archétypes émergents"""
        emerging = []
        current_shares = current_meta.get('shares', {})
        
        for archetype, predicted_share in predicted_shares.items():
            current_share = current_shares.get(archetype, 0.0)
            growth = predicted_share - current_share
            
            if growth > 0.02:  # Seuil de 2% de croissance
                emerging.append({
                    'archetype': archetype,
                    'current_share': current_share,
                    'predicted_share': predicted_share,
                    'growth': growth,
                    'growth_rate': growth / max(current_share, 0.001)
                })
                
        return sorted(emerging, key=lambda x: x['growth'], reverse=True)
        
    def _detect_declining_patterns(self, current_meta: Dict, predicted_shares: Dict) -> List[Dict]:
        """Détecter les archétypes en déclin"""
        declining = []
        current_shares = current_meta.get('shares', {})
        
        for archetype, predicted_share in predicted_shares.items():
            current_share = current_shares.get(archetype, 0.0)
            decline = current_share - predicted_share
            
            if decline > 0.02:  # Seuil de 2% de déclin
                declining.append({
                    'archetype': archetype,
                    'current_share': current_share,
                    'predicted_share': predicted_share,
                    'decline': decline,
                    'decline_rate': decline / max(current_share, 0.001)
                })
                
        return sorted(declining, key=lambda x: x['decline'], reverse=True)
        
    def suggest_deck_positioning(self, current_deck: List[str], format: str) -> Dict:
        """Suggérer des modifications basées sur les prédictions"""
        # Prédire le métagame futur
        current_meta = self._get_current_meta(format)
        future_prediction = self.predict_next_week(current_meta)
        
        # Analyser le deck actuel
        deck_analysis = self._analyze_deck_vs_meta(current_deck, future_prediction.predicted_shares)
        
        return {
            'recommended_changes': self._generate_deck_recommendations(current_deck, deck_analysis),
            'expected_matchup_changes': self._calculate_matchup_changes(current_deck, future_prediction),
            'risk_assessment': self._assess_deck_risk(current_deck, future_prediction),
            'meta_positioning': deck_analysis
        }
        
    def _get_current_meta(self, format: str) -> Dict:
        """Récupérer le métagame actuel"""
        # Placeholder - en pratique, récupérer depuis la base de données
        return {
            'format': format,
            'shares': {},
            'winrates': {},
            'popularity': {}
        }
        
    def _analyze_deck_vs_meta(self, deck: List[str], predicted_shares: Dict) -> Dict:
        """Analyser un deck contre le métagame prédit"""
        # Analyse simplifiée
        return {
            'favorable_matchups': 0.6,
            'unfavorable_matchups': 0.3,
            'neutral_matchups': 0.1,
            'meta_share_against_favorable': 0.4
        }
        
    def _generate_deck_recommendations(self, deck: List[str], analysis: Dict) -> List[Dict]:
        """Générer des recommandations de deck"""
        return [
            {
                'type': 'sideboard',
                'recommendation': 'Ajouter plus de removal',
                'reason': 'Métagame plus agressif prévu'
            }
        ]
        
    def _calculate_matchup_changes(self, deck: List[str], prediction: MetagamePrediction) -> Dict:
        """Calculer les changements de matchups"""
        return {
            'overall_winrate_change': 0.02,
            'specific_matchups': {}
        }
        
    def _assess_deck_risk(self, deck: List[str], prediction: MetagamePrediction) -> Dict:
        """Évaluer le risque d'un deck"""
        return {
            'risk_level': 'medium',
            'risk_factors': ['Métagame shifting toward aggro'],
            'mitigation_strategies': ['Adjust sideboard for faster meta']
        }
        
    def save_model(self, path: str) -> None:
        """Sauvegarder le modèle"""
        if not self.model:
            raise ValueError("Aucun modèle à sauvegarder")
            
        save_data = {
            'model_state': self.model.state_dict(),
            'archetype_encoder': self.archetype_encoder,
            'archetype_decoder': self.archetype_decoder,
            'sequence_length': self.sequence_length
        }
        
        torch.save(save_data, path)
        logger.info(f"Modèle sauvegardé: {path}")
        
    def load_model(self, path: str) -> None:
        """Charger un modèle"""
        save_data = torch.load(path, map_location='cpu')
        
        self.archetype_encoder = save_data['archetype_encoder']
        self.archetype_decoder = save_data['archetype_decoder']
        self.sequence_length = save_data['sequence_length']
        
        # Recréer le modèle
        num_archetypes = len(self.archetype_encoder)
        self.model = MetagameLSTM(num_archetypes=num_archetypes)
        self.model.load_state_dict(save_data['model_state'])
        
        logger.info(f"Modèle chargé: {path}")
        
    def get_model_info(self) -> Dict:
        """Informations sur le modèle"""
        if not self.model:
            return {'status': 'not_initialized'}
            
        return {
            'status': 'ready',
            'num_archetypes': len(self.archetype_encoder),
            'sequence_length': self.sequence_length,
            'model_parameters': sum(p.numel() for p in self.model.parameters()),
            'archetypes': list(self.archetype_encoder.keys())
        } 