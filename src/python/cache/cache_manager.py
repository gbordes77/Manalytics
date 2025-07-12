"""
Gestionnaire de cache centralisé pour Manalytics.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging

from .redis_cache import RedisCache, CacheConfig
from .tournament_cache import TournamentCache

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestionnaire de cache centralisé pour Manalytics.
    
    Fonctionnalités :
    - Gestion unifiée de tous les caches
    - Configuration centralisée
    - Monitoring global
    - Maintenance automatique
    - Fallback gracieux
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_cache: Optional[RedisCache] = None
        self.tournament_cache: Optional[TournamentCache] = None
        self.is_connected = False
        self.maintenance_task: Optional[asyncio.Task] = None
        
        # Configuration de maintenance
        self.maintenance_config = {
            'interval': 3600,  # 1 heure
            'cleanup_expired': True,
            'refresh_keys': True,
            'log_stats': True
        }
    
    async def initialize(self) -> bool:
        """Initialiser tous les caches"""
        try:
            # Initialiser Redis
            self.redis_cache = RedisCache(self.config)
            await self.redis_cache.connect()
            
            # Initialiser le cache de tournois
            self.tournament_cache = TournamentCache(self.redis_cache)
            await self.tournament_cache.refresh_tournament_keys()
            
            # Démarrer la maintenance
            self.maintenance_task = asyncio.create_task(self._maintenance_loop())
            
            self.is_connected = True
            logger.info("Cache Manager initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du cache: {e}")
            return False
    
    async def shutdown(self):
        """Arrêter tous les caches"""
        if self.maintenance_task:
            self.maintenance_task.cancel()
        
        if self.redis_cache:
            await self.redis_cache.disconnect()
        
        self.is_connected = False
        logger.info("Cache Manager arrêté")
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé de tous les caches"""
        health = {
            'overall': False,
            'redis': False,
            'tournament_cache': False,
            'errors': []
        }
        
        try:
            # Vérifier Redis
            if self.redis_cache and self.redis_cache.redis_client:
                await self.redis_cache.redis_client.ping()
                health['redis'] = True
            
            # Vérifier le cache de tournois
            if self.tournament_cache:
                # Test simple
                test_key = "health_check_test"
                await self.tournament_cache.redis_cache.set(test_key, "test", 10)
                result = await self.tournament_cache.redis_cache.get(test_key)
                if result == "test":
                    health['tournament_cache'] = True
                await self.tournament_cache.redis_cache.delete(test_key)
            
            health['overall'] = health['redis'] and health['tournament_cache']
            
        except Exception as e:
            health['errors'].append(str(e))
            logger.error(f"Erreur lors du health check: {e}")
        
        return health
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques globales"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'is_connected': self.is_connected,
            'redis_cache': {},
            'tournament_cache': {},
            'global_metrics': {}
        }
        
        try:
            # Statistiques Redis
            if self.redis_cache:
                stats['redis_cache'] = self.redis_cache.get_stats()
                cache_size = await self.redis_cache.get_cache_size()
                stats['redis_cache']['size'] = cache_size
            
            # Statistiques tournois
            if self.tournament_cache:
                stats['tournament_cache'] = await self.tournament_cache.get_cache_stats()
            
            # Métriques globales
            total_hits = stats['redis_cache'].get('hits', 0)
            total_misses = stats['redis_cache'].get('misses', 0)
            total_requests = total_hits + total_misses
            
            stats['global_metrics'] = {
                'total_requests': total_requests,
                'global_hit_rate': total_hits / max(total_requests, 1),
                'total_keys': stats['redis_cache'].get('size', {}).get('keys', 0),
                'memory_usage': stats['redis_cache'].get('size', {}).get('memory_human', '0B')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            stats['error'] = str(e)
        
        return stats
    
    async def clear_all_caches(self) -> Dict[str, bool]:
        """Vider tous les caches"""
        results = {
            'redis_cache': False,
            'tournament_cache': False
        }
        
        try:
            # Vider Redis
            if self.redis_cache:
                results['redis_cache'] = await self.redis_cache.flush_cache()
            
            # Réinitialiser le cache de tournois
            if self.tournament_cache:
                self.tournament_cache.tournament_keys.clear()
                results['tournament_cache'] = True
            
            logger.warning("Tous les caches ont été vidés")
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage des caches: {e}")
        
        return results
    
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalider toutes les clés correspondant à un pattern"""
        if not self.redis_cache:
            return 0
        
        try:
            deleted = await self.redis_cache.invalidate_pattern(pattern)
            
            # Nettoyer le cache local de tournois si nécessaire
            if self.tournament_cache and "tournament" in pattern:
                await self.tournament_cache.cleanup_expired_keys()
            
            return deleted
            
        except Exception as e:
            logger.error(f"Erreur lors de l'invalidation par pattern {pattern}: {e}")
            return 0
    
    async def get_cache_instance(self, cache_type: str) -> Optional[Any]:
        """Récupérer une instance de cache spécifique"""
        if cache_type == "redis":
            return self.redis_cache
        elif cache_type == "tournament":
            return self.tournament_cache
        else:
            logger.warning(f"Type de cache inconnu: {cache_type}")
            return None
    
    async def preload_tournament_data(self, format_name: str, start_date: str, end_date: str, tournaments: List[Dict[str, Any]]) -> bool:
        """Précharger des données de tournois"""
        if not self.tournament_cache:
            return False
        
        try:
            success = await self.tournament_cache.cache_format_tournaments(
                format_name, start_date, end_date, tournaments
            )
            
            if success:
                logger.info(f"Données préchargées: {len(tournaments)} tournois pour {format_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors du préchargement: {e}")
            return False
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimiser les caches (maintenance proactive)"""
        optimization_results = {
            'expired_keys_cleaned': 0,
            'tournament_keys_refreshed': 0,
            'memory_freed': 0,
            'errors': []
        }
        
        try:
            # Nettoyer les clés expirées
            if self.tournament_cache:
                await self.tournament_cache.cleanup_expired_keys()
                optimization_results['expired_keys_cleaned'] = len(self.tournament_cache.tournament_keys)
                
                # Rafraîchir les clés
                await self.tournament_cache.refresh_tournament_keys()
                optimization_results['tournament_keys_refreshed'] = len(self.tournament_cache.tournament_keys)
            
            # Statistiques mémoire
            if self.redis_cache:
                cache_size = await self.redis_cache.get_cache_size()
                optimization_results['memory_freed'] = cache_size.get('memory', 0)
            
            logger.info(f"Optimisation du cache terminée: {optimization_results}")
            
        except Exception as e:
            optimization_results['errors'].append(str(e))
            logger.error(f"Erreur lors de l'optimisation: {e}")
        
        return optimization_results
    
    async def _maintenance_loop(self):
        """Boucle de maintenance automatique"""
        while True:
            try:
                await asyncio.sleep(self.maintenance_config['interval'])
                
                logger.debug("Démarrage de la maintenance du cache")
                
                # Nettoyer les clés expirées
                if self.maintenance_config['cleanup_expired']:
                    await self.optimize_cache()
                
                # Logger les statistiques
                if self.maintenance_config['log_stats']:
                    stats = await self.get_global_stats()
                    logger.info(f"Cache Stats: {stats['global_metrics']}")
                
                # Vérifier la santé
                health = await self.health_check()
                if not health['overall']:
                    logger.warning(f"Problème de santé du cache: {health}")
                
            except asyncio.CancelledError:
                logger.info("Maintenance du cache arrêtée")
                break
            except Exception as e:
                logger.error(f"Erreur dans la maintenance du cache: {e}")
    
    async def backup_cache_keys(self) -> Dict[str, List[str]]:
        """Sauvegarder les clés importantes du cache"""
        backup = {
            'tournament_keys': [],
            'format_keys': [],
            'meta_keys': []
        }
        
        try:
            if self.redis_cache:
                # Récupérer toutes les clés
                all_keys = await self.redis_cache.redis_client.keys(
                    self.redis_cache._build_key("*")
                )
                
                prefix = self.redis_cache.config.key_prefix
                
                for key in all_keys:
                    clean_key = key.decode().replace(prefix, '')
                    
                    if clean_key.startswith('tournament:'):
                        backup['tournament_keys'].append(clean_key)
                    elif clean_key.startswith('format:'):
                        backup['format_keys'].append(clean_key)
                    elif clean_key.startswith('meta:'):
                        backup['meta_keys'].append(clean_key)
                
                logger.info(f"Sauvegarde des clés: {len(backup['tournament_keys'])} tournois, "
                           f"{len(backup['format_keys'])} formats, {len(backup['meta_keys'])} méta")
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des clés: {e}")
        
        return backup
    
    async def restore_cache_keys(self, backup: Dict[str, List[str]]) -> bool:
        """Restaurer les clés du cache depuis une sauvegarde"""
        try:
            if self.tournament_cache:
                # Restaurer les clés de tournois
                self.tournament_cache.tournament_keys = set(backup.get('tournament_keys', []))
                logger.info(f"Clés restaurées: {len(self.tournament_cache.tournament_keys)} tournois")
                return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la restauration des clés: {e}")
            return False
    
    # Context manager support
    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.shutdown() 