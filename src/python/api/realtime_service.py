"""
Service de métagame en temps réel avec WebSocket
"""

import asyncio
import json
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect

from ..cache.redis_cache import RedisCache
from ..metrics.business_metrics import BusinessMetrics

logger = logging.getLogger(__name__)

@dataclass
class MetagameUpdate:
    """Mise à jour du métagame"""
    type: str
    format: str
    data: Dict[str, Any]
    tournament_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ConnectionManager:
    """Gestionnaire de connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket, format: str, user_id: Optional[str] = None):
        """Ajouter une connexion"""
        await websocket.accept()
        
        if format not in self.active_connections:
            self.active_connections[format] = set()
            
        self.active_connections[format].add(websocket)
        self.connection_metadata[websocket] = {
            'format': format,
            'user_id': user_id,
            'connected_at': datetime.now()
        }
        
        logger.info(f"Client connecté au format {format}, total: {len(self.active_connections[format])}")
        
    def disconnect(self, websocket: WebSocket):
        """Supprimer une connexion"""
        if websocket in self.connection_metadata:
            format = self.connection_metadata[websocket]['format']
            
            if format in self.active_connections:
                self.active_connections[format].discard(websocket)
                
            del self.connection_metadata[websocket]
            logger.info(f"Client déconnecté du format {format}")
            
    async def send_to_format(self, format: str, message: Dict):
        """Envoyer un message à tous les clients d'un format"""
        if format not in self.active_connections:
            return
            
        disconnected = []
        
        for connection in self.active_connections[format]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Erreur envoi message: {e}")
                disconnected.append(connection)
                
        # Nettoyer les connexions fermées
        for connection in disconnected:
            self.disconnect(connection)
            
    async def broadcast_all(self, message: Dict):
        """Diffuser un message à tous les clients"""
        for format in self.active_connections:
            await self.send_to_format(format, message)

class RealtimeMetagameService:
    """Service de métagame en temps réel"""
    
    def __init__(self, cache: Optional[RedisCache] = None):
        self.cache = cache or RedisCache()
        self.connection_manager = ConnectionManager()
        self.business_metrics = BusinessMetrics()
        self.update_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Démarrer le service"""
        self.is_running = True
        asyncio.create_task(self._process_updates())
        logger.info("Service temps réel démarré")
        
    async def stop(self):
        """Arrêter le service"""
        self.is_running = False
        logger.info("Service temps réel arrêté")
        
    async def add_connection(self, websocket: WebSocket, format: str, user_id: Optional[str] = None):
        """Ajouter une connexion WebSocket"""
        await self.connection_manager.connect(websocket, format, user_id)
        
        # Envoyer l'état actuel
        current_state = await self.get_current_metagame(format)
        await websocket.send_json({
            'type': 'initial_state',
            'format': format,
            'data': current_state
        })
        
    def remove_connection(self, websocket: WebSocket):
        """Supprimer une connexion WebSocket"""
        self.connection_manager.disconnect(websocket)
        
    async def tournament_completed(self, tournament_id: str, format: str, results: Dict):
        """Traiter la fin d'un tournoi"""
        logger.info(f"Tournoi terminé: {tournament_id} ({format})")
        
        # Calculer les nouvelles statistiques
        new_stats = await self.calculate_incremental_stats(tournament_id, format, results)
        
        # Créer la mise à jour
        update = MetagameUpdate(
            type='tournament_completed',
            format=format,
            data=new_stats,
            tournament_id=tournament_id
        )
        
        # Ajouter à la queue
        await self.update_queue.put(update)
        
    async def meta_shift_detected(self, format: str, shift_data: Dict):
        """Détecter un changement de métagame"""
        logger.info(f"Changement de métagame détecté: {format}")
        
        update = MetagameUpdate(
            type='meta_shift',
            format=format,
            data=shift_data
        )
        
        await self.update_queue.put(update)
        
    async def deck_innovation_detected(self, format: str, innovation_data: Dict):
        """Détecter une innovation de deck"""
        logger.info(f"Innovation détectée: {format}")
        
        update = MetagameUpdate(
            type='deck_innovation',
            format=format,
            data=innovation_data
        )
        
        await self.update_queue.put(update)
        
    async def _process_updates(self):
        """Traiter les mises à jour en arrière-plan"""
        while self.is_running:
            try:
                # Attendre une mise à jour
                update = await asyncio.wait_for(self.update_queue.get(), timeout=1.0)
                
                # Préparer le message
                message = {
                    'type': update.type,
                    'format': update.format,
                    'data': update.data,
                    'timestamp': update.timestamp.isoformat()
                }
                
                if update.tournament_id:
                    message['tournament_id'] = update.tournament_id
                    
                # Diffuser aux clients
                await self.connection_manager.send_to_format(update.format, message)
                
                # Mettre à jour les métriques
                await self._update_realtime_metrics(update)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erreur traitement mise à jour: {e}")
                
    async def calculate_incremental_stats(self, tournament_id: str, format: str, results: Dict) -> Dict:
        """Calculer les statistiques incrémentales"""
        try:
            # Récupérer les stats actuelles
            current_stats = await self.get_current_metagame(format)
            
            # Analyser les résultats du tournoi
            tournament_impact = self._analyze_tournament_impact(results)
            
            # Calculer les nouvelles parts de métagame
            new_shares = self._calculate_new_shares(current_stats, tournament_impact)
            
            # Détecter les tendances
            trends = self._detect_trends(current_stats, new_shares)
            
            return {
                'meta_shares': new_shares,
                'trends': trends,
                'tournament_impact': tournament_impact,
                'last_updated': datetime.now().isoformat(),
                'data_points': current_stats.get('data_points', 0) + len(results.get('decks', []))
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul stats incrémentales: {e}")
            return {}
            
    async def get_current_metagame(self, format: str) -> Dict:
        """Récupérer l'état actuel du métagame"""
        try:
            # Essayer le cache d'abord
            cached = await self.cache.get(f"metagame:{format}")
            if cached:
                return json.loads(cached)
                
            # Calculer depuis les données
            stats = await self.business_metrics.calculate_metagame_stats(format)
            
            # Mettre en cache
            await self.cache.set(f"metagame:{format}", json.dumps(stats), ttl=300)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération métagame: {e}")
            return {}
            
    def _analyze_tournament_impact(self, results: Dict) -> Dict:
        """Analyser l'impact d'un tournoi"""
        decks = results.get('decks', [])
        
        if not decks:
            return {}
            
        # Compter les archétypes
        archetype_counts = {}
        archetype_performance = {}
        
        for deck in decks:
            archetype = deck.get('archetype', 'Unknown')
            wins = deck.get('wins', 0)
            losses = deck.get('losses', 0)
            
            if archetype not in archetype_counts:
                archetype_counts[archetype] = 0
                archetype_performance[archetype] = {'wins': 0, 'losses': 0}
                
            archetype_counts[archetype] += 1
            archetype_performance[archetype]['wins'] += wins
            archetype_performance[archetype]['losses'] += losses
            
        # Calculer les win rates
        win_rates = {}
        for archetype, perf in archetype_performance.items():
            total_games = perf['wins'] + perf['losses']
            if total_games > 0:
                win_rates[archetype] = perf['wins'] / total_games
                
        return {
            'archetype_counts': archetype_counts,
            'win_rates': win_rates,
            'total_decks': len(decks),
            'unique_archetypes': len(archetype_counts)
        }
        
    def _calculate_new_shares(self, current_stats: Dict, tournament_impact: Dict) -> Dict:
        """Calculer les nouvelles parts de métagame"""
        current_shares = current_stats.get('meta_shares', {})
        new_counts = tournament_impact.get('archetype_counts', {})
        
        if not new_counts:
            return current_shares
            
        # Pondérer avec les données existantes
        total_new = sum(new_counts.values())
        current_weight = 0.9  # Poids des données existantes
        new_weight = 0.1      # Poids des nouvelles données
        
        updated_shares = {}
        
        # Mettre à jour les archétypes existants
        for archetype, current_share in current_shares.items():
            new_share = new_counts.get(archetype, 0) / total_new if total_new > 0 else 0
            updated_shares[archetype] = current_weight * current_share + new_weight * new_share
            
        # Ajouter les nouveaux archétypes
        for archetype, count in new_counts.items():
            if archetype not in updated_shares:
                updated_shares[archetype] = new_weight * (count / total_new)
                
        return updated_shares
        
    def _detect_trends(self, current_stats: Dict, new_shares: Dict) -> Dict:
        """Détecter les tendances"""
        current_shares = current_stats.get('meta_shares', {})
        trends = {}
        
        for archetype, new_share in new_shares.items():
            old_share = current_shares.get(archetype, 0)
            change = new_share - old_share
            
            if abs(change) > 0.01:  # Seuil de 1%
                trends[archetype] = {
                    'change': change,
                    'direction': 'up' if change > 0 else 'down',
                    'magnitude': abs(change)
                }
                
        return trends
        
    async def _update_realtime_metrics(self, update: MetagameUpdate):
        """Mettre à jour les métriques temps réel"""
        try:
            # Compter les connexions actives
            total_connections = sum(len(connections) for connections in self.connection_manager.active_connections.values())
            
            # Enregistrer les métriques
            await self.cache.set('realtime:connections', str(total_connections), ttl=60)
            await self.cache.set(f'realtime:last_update:{update.format}', update.timestamp.isoformat(), ttl=3600)
            
            # Incrémenter les compteurs
            await self.cache.incr(f'realtime:updates:{update.type}')
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques temps réel: {e}")

# Instance globale
realtime_service = RealtimeMetagameService() 