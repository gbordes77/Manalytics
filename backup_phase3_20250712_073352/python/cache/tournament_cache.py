"""
Cache spécialisé pour les données de tournois MTG.
"""

import hashlib
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import logging

from .redis_cache import RedisCache, CacheConfig

logger = logging.getLogger(__name__)


class TournamentCache:
    """
    Cache spécialisé pour les données de tournois MTG.
    
    Fonctionnalités :
    - Clés intelligentes basées sur les métadonnées du tournoi
    - TTL adaptatif selon l'âge du tournoi
    - Invalidation par format/date
    - Détection de doublons
    - Compression optimisée pour les données MTG
    """
    
    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        self.tournament_keys: Set[str] = set()  # Cache local des clés
        
        # Configuration spécifique aux tournois
        self.ttl_config = {
            'recent': 86400,      # 1 jour pour tournois récents
            'medium': 86400 * 7,  # 1 semaine pour tournois moyens
            'old': 86400 * 30,    # 1 mois pour anciens tournois
            'format_meta': 86400 * 3  # 3 jours pour méta par format
        }
    
    def _build_tournament_key(self, tournament_id: str, source: str = "") -> str:
        """Construire une clé pour un tournoi"""
        if source:
            return f"tournament:{source}:{tournament_id}"
        return f"tournament:{tournament_id}"
    
    def _build_format_key(self, format_name: str, date_range: str = "") -> str:
        """Construire une clé pour un format"""
        if date_range:
            return f"format:{format_name}:{date_range}"
        return f"format:{format_name}"
    
    def _build_meta_key(self, format_name: str, start_date: str, end_date: str) -> str:
        """Construire une clé pour les métadonnées d'un format"""
        return f"meta:{format_name}:{start_date}:{end_date}"
    
    def _calculate_tournament_ttl(self, tournament_date: str) -> int:
        """Calculer le TTL basé sur l'âge du tournoi"""
        try:
            # Parser la date du tournoi
            if tournament_date.endswith('Z'):
                tournament_date = tournament_date[:-1] + '+00:00'
            
            tournament_dt = datetime.fromisoformat(tournament_date)
            now = datetime.now(tournament_dt.tzinfo)
            age_days = (now - tournament_dt).days
            
            # TTL adaptatif selon l'âge
            if age_days <= 7:
                return self.ttl_config['recent']
            elif age_days <= 30:
                return self.ttl_config['medium']
            else:
                return self.ttl_config['old']
                
        except Exception as e:
            logger.warning(f"Erreur lors du calcul du TTL: {e}")
            return self.ttl_config['medium']
    
    def _generate_tournament_hash(self, tournament_data: Dict[str, Any]) -> str:
        """Générer un hash pour détecter les doublons"""
        # Utiliser les données clés pour le hash
        key_data = {
            'id': tournament_data.get('tournament', {}).get('id'),
            'name': tournament_data.get('tournament', {}).get('name'),
            'date': tournament_data.get('tournament', {}).get('date'),
            'format': tournament_data.get('tournament', {}).get('format'),
            'deck_count': len(tournament_data.get('decks', []))
        }
        
        # Créer un hash stable
        json_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    async def get_tournament(self, tournament_id: str, source: str = "") -> Optional[Dict[str, Any]]:
        """Récupérer un tournoi du cache"""
        key = self._build_tournament_key(tournament_id, source)
        return await self.redis_cache.get(key)
    
    async def set_tournament(self, tournament_data: Dict[str, Any], source: str = "") -> bool:
        """Stocker un tournoi dans le cache"""
        tournament_info = tournament_data.get('tournament', {})
        tournament_id = tournament_info.get('id')
        
        if not tournament_id:
            logger.warning("Impossible de cacher un tournoi sans ID")
            return False
        
        # Construire la clé
        key = self._build_tournament_key(tournament_id, source)
        
        # Calculer le TTL adaptatif
        tournament_date = tournament_info.get('date', '')
        ttl = self._calculate_tournament_ttl(tournament_date)
        
        # Ajouter des métadonnées de cache
        cached_data = {
            'tournament_data': tournament_data,
            'cached_at': datetime.now().isoformat(),
            'source': source,
            'hash': self._generate_tournament_hash(tournament_data)
        }
        
        # Stocker dans Redis
        success = await self.redis_cache.set(key, cached_data, ttl)
        
        if success:
            self.tournament_keys.add(key)
            logger.debug(f"Tournoi caché: {tournament_id} (TTL: {ttl}s)")
        
        return success
    
    async def tournament_exists(self, tournament_id: str, source: str = "") -> bool:
        """Vérifier si un tournoi existe dans le cache"""
        key = self._build_tournament_key(tournament_id, source)
        return await self.redis_cache.exists(key)
    
    async def get_tournament_hash(self, tournament_id: str, source: str = "") -> Optional[str]:
        """Récupérer le hash d'un tournoi pour détecter les changements"""
        cached_data = await self.get_tournament(tournament_id, source)
        if cached_data and 'hash' in cached_data:
            return cached_data['hash']
        return None
    
    async def is_tournament_duplicate(self, tournament_data: Dict[str, Any], source: str = "") -> bool:
        """Vérifier si un tournoi est un doublon"""
        tournament_id = tournament_data.get('tournament', {}).get('id')
        if not tournament_id:
            return False
        
        # Récupérer le hash existant
        existing_hash = await self.get_tournament_hash(tournament_id, source)
        if not existing_hash:
            return False
        
        # Comparer avec le nouveau hash
        new_hash = self._generate_tournament_hash(tournament_data)
        return existing_hash == new_hash
    
    async def get_tournaments_by_format(self, format_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Récupérer tous les tournois d'un format dans une plage de dates"""
        # Essayer de récupérer depuis le cache de format
        format_key = self._build_meta_key(format_name, start_date, end_date)
        cached_tournaments = await self.redis_cache.get(format_key)
        
        if cached_tournaments:
            logger.debug(f"Tournois récupérés depuis le cache format: {len(cached_tournaments)} tournois")
            return cached_tournaments
        
        # Sinon, chercher individuellement (plus lent)
        tournaments = []
        
        # Parcourir toutes les clés de tournois connues
        for key in self.tournament_keys:
            tournament_data = await self.redis_cache.get(key)
            if tournament_data:
                tournament_info = tournament_data.get('tournament_data', {}).get('tournament', {})
                
                # Vérifier format et date
                if tournament_info.get('format') == format_name:
                    tournament_date = tournament_info.get('date', '')
                    if start_date <= tournament_date <= end_date:
                        tournaments.append(tournament_data['tournament_data'])
        
        # Cacher le résultat pour les prochaines requêtes
        if tournaments:
            await self.redis_cache.set(format_key, tournaments, self.ttl_config['format_meta'])
        
        return tournaments
    
    async def cache_format_tournaments(self, format_name: str, start_date: str, end_date: str, tournaments: List[Dict[str, Any]]) -> bool:
        """Cacher une liste de tournois pour un format"""
        format_key = self._build_meta_key(format_name, start_date, end_date)
        
        # Cacher chaque tournoi individuellement
        for tournament_data in tournaments:
            await self.set_tournament(tournament_data, "batch")
        
        # Cacher la liste complète
        success = await self.redis_cache.set(format_key, tournaments, self.ttl_config['format_meta'])
        
        if success:
            logger.info(f"Format {format_name} caché: {len(tournaments)} tournois ({start_date} à {end_date})")
        
        return success
    
    async def invalidate_format(self, format_name: str) -> int:
        """Invalider tous les tournois d'un format"""
        pattern = f"*:{format_name}:*"
        deleted = await self.redis_cache.invalidate_pattern(pattern)
        
        # Nettoyer le cache local
        self.tournament_keys = {key for key in self.tournament_keys if format_name not in key}
        
        logger.info(f"Format {format_name} invalidé: {deleted} clés supprimées")
        return deleted
    
    async def invalidate_old_tournaments(self, days_old: int = 90) -> int:
        """Invalider les tournois plus anciens que X jours"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        # Parcourir toutes les clés de tournois
        keys_to_remove = []
        for key in self.tournament_keys:
            tournament_data = await self.redis_cache.get(key)
            if tournament_data:
                tournament_info = tournament_data.get('tournament_data', {}).get('tournament', {})
                tournament_date_str = tournament_info.get('date', '')
                
                try:
                    if tournament_date_str.endswith('Z'):
                        tournament_date_str = tournament_date_str[:-1] + '+00:00'
                    
                    tournament_date = datetime.fromisoformat(tournament_date_str)
                    
                    if tournament_date < cutoff_date:
                        await self.redis_cache.delete(key)
                        keys_to_remove.append(key)
                        deleted_count += 1
                        
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse de date pour {key}: {e}")
        
        # Nettoyer le cache local
        for key in keys_to_remove:
            self.tournament_keys.discard(key)
        
        logger.info(f"Tournois anciens invalidés: {deleted_count} tournois supprimés")
        return deleted_count
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du cache de tournois"""
        base_stats = self.redis_cache.get_stats()
        
        # Statistiques spécifiques aux tournois
        tournament_count = len(self.tournament_keys)
        cache_size = await self.redis_cache.get_cache_size()
        
        return {
            **base_stats,
            'tournament_count': tournament_count,
            'cache_size': cache_size,
            'ttl_config': self.ttl_config
        }
    
    async def refresh_tournament_keys(self):
        """Rafraîchir le cache local des clés de tournois"""
        pattern = "tournament:*"
        keys = await self.redis_cache.redis_client.keys(
            self.redis_cache._build_key(pattern)
        )
        
        # Nettoyer les clés (enlever le préfixe)
        prefix = self.redis_cache.config.key_prefix
        self.tournament_keys = {
            key.decode().replace(prefix, '') for key in keys
        }
        
        logger.info(f"Cache des clés rafraîchi: {len(self.tournament_keys)} tournois")
    
    async def cleanup_expired_keys(self):
        """Nettoyer les clés expirées du cache local"""
        active_keys = set()
        
        for key in self.tournament_keys:
            if await self.redis_cache.exists(key):
                active_keys.add(key)
        
        expired_count = len(self.tournament_keys) - len(active_keys)
        self.tournament_keys = active_keys
        
        if expired_count > 0:
            logger.info(f"Nettoyage: {expired_count} clés expirées supprimées")
    
    async def get_tournament_metadata(self, tournament_id: str, source: str = "") -> Optional[Dict[str, Any]]:
        """Récupérer seulement les métadonnées d'un tournoi (sans les decks)"""
        cached_data = await self.get_tournament(tournament_id, source)
        if not cached_data:
            return None
        
        tournament_data = cached_data.get('tournament_data', {})
        tournament_info = tournament_data.get('tournament', {})
        
        return {
            'id': tournament_info.get('id'),
            'name': tournament_info.get('name'),
            'date': tournament_info.get('date'),
            'format': tournament_info.get('format'),
            'deck_count': len(tournament_data.get('decks', [])),
            'cached_at': cached_data.get('cached_at'),
            'source': cached_data.get('source'),
            'hash': cached_data.get('hash')
        } 