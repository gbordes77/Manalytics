"""
Cache Redis intelligent avec compression, TTL et monitoring.
"""

import asyncio
import json
import gzip
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration du cache Redis"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    
    # Configuration du cache
    default_ttl: int = 3600  # 1 heure
    max_ttl: int = 86400 * 7  # 7 jours
    compression_threshold: int = 1024  # Compresser si > 1KB
    key_prefix: str = "manalytics:"
    
    # Monitoring
    enable_stats: bool = True
    stats_interval: int = 60  # Statistiques toutes les minutes


class CacheStats:
    """Statistiques du cache"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.compressed_items = 0
        self.total_size_saved = 0
        self.start_time = time.time()
    
    @property
    def hit_rate(self) -> float:
        """Taux de hit du cache"""
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0
    
    @property
    def uptime(self) -> float:
        """Temps de fonctionnement en secondes"""
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'errors': self.errors,
            'compressed_items': self.compressed_items,
            'total_size_saved': self.total_size_saved,
            'hit_rate': self.hit_rate,
            'uptime': self.uptime
        }


class RedisCache:
    """
    Cache Redis intelligent avec fonctionnalités avancées.
    
    Fonctionnalités :
    - TTL automatique et configurable
    - Compression automatique des grandes valeurs
    - Monitoring et statistiques
    - Sérialisation intelligente (JSON/Pickle)
    - Gestion des erreurs et fallback
    - Invalidation par pattern
    """
    
    def __init__(self, config: CacheConfig):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis n'est pas disponible. Installez redis-py avec: pip install redis")
        
        self.config = config
        self.stats = CacheStats()
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._stats_task: Optional[asyncio.Task] = None
        
        logger.info(f"Cache Redis configuré: {config.host}:{config.port}, DB={config.db}")
    
    async def connect(self):
        """Initialiser la connexion Redis"""
        try:
            self.redis_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=False  # Garder les bytes pour la compression
            )
            
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test de connexion
            await self.redis_client.ping()
            logger.info("Connexion Redis établie avec succès")
            
            # Démarrer les tâches de monitoring
            if self.config.enable_stats:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                self._stats_task = asyncio.create_task(self._stats_loop())
            
        except Exception as e:
            logger.error(f"Erreur de connexion Redis: {e}")
            self.stats.errors += 1
            raise
    
    async def disconnect(self):
        """Fermer la connexion Redis"""
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._stats_task:
            self._stats_task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()
        if self.redis_pool:
            await self.redis_pool.disconnect()
        
        logger.info("Connexion Redis fermée")
    
    def _build_key(self, key: str) -> str:
        """Construire la clé complète avec préfixe"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Sérialiser une valeur avec compression si nécessaire"""
        # Essayer JSON d'abord (plus rapide et lisible)
        try:
            json_data = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            serialized = json_data.encode('utf-8')
            is_json = True
        except (TypeError, ValueError):
            # Fallback vers pickle pour les objets complexes
            serialized = pickle.dumps(value)
            is_json = False
        
        # Compression si la taille dépasse le seuil
        if len(serialized) > self.config.compression_threshold:
            compressed = gzip.compress(serialized)
            self.stats.compressed_items += 1
            self.stats.total_size_saved += len(serialized) - len(compressed)
            
            # Préfixe pour indiquer compression + format
            prefix = b'gz_json:' if is_json else b'gz_pickle:'
            return prefix + compressed
        else:
            # Préfixe pour indiquer le format
            prefix = b'json:' if is_json else b'pickle:'
            return prefix + serialized
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Désérialiser une valeur avec décompression si nécessaire"""
        if data.startswith(b'gz_json:'):
            # Décompresser puis décoder JSON
            compressed_data = data[8:]  # Enlever le préfixe
            decompressed = gzip.decompress(compressed_data)
            return json.loads(decompressed.decode('utf-8'))
        
        elif data.startswith(b'gz_pickle:'):
            # Décompresser puis décoder pickle
            compressed_data = data[10:]  # Enlever le préfixe
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
        
        elif data.startswith(b'json:'):
            # Décoder JSON directement
            json_data = data[5:]  # Enlever le préfixe
            return json.loads(json_data.decode('utf-8'))
        
        elif data.startswith(b'pickle:'):
            # Décoder pickle directement
            pickle_data = data[7:]  # Enlever le préfixe
            return pickle.loads(pickle_data)
        
        else:
            # Format legacy ou inconnu, essayer pickle
            try:
                return pickle.loads(data)
            except Exception:
                raise ValueError(f"Format de données non reconnu: {data[:20]}...")
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if not self.redis_client:
            logger.warning("Client Redis non initialisé")
            return None
        
        try:
            full_key = self._build_key(key)
            data = await self.redis_client.get(full_key)
            
            if data is None:
                self.stats.misses += 1
                return None
            
            value = self._deserialize_value(data)
            self.stats.hits += 1
            return value
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du cache {key}: {e}")
            self.stats.errors += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocker une valeur dans le cache"""
        if not self.redis_client:
            logger.warning("Client Redis non initialisé")
            return False
        
        try:
            full_key = self._build_key(key)
            serialized_value = self._serialize_value(value)
            
            # Utiliser TTL par défaut si non spécifié
            cache_ttl = ttl or self.config.default_ttl
            cache_ttl = min(cache_ttl, self.config.max_ttl)  # Limiter le TTL max
            
            await self.redis_client.setex(full_key, cache_ttl, serialized_value)
            self.stats.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du stockage dans le cache {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Supprimer une clé du cache"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._build_key(key)
            result = await self.redis_client.delete(full_key)
            self.stats.deletes += 1
            return result > 0
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Vérifier si une clé existe dans le cache"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._build_key(key)
            return await self.redis_client.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'existence {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Récupérer le TTL d'une clé"""
        if not self.redis_client:
            return None
        
        try:
            full_key = self._build_key(key)
            ttl = await self.redis_client.ttl(full_key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du TTL {key}: {e}")
            return None
    
    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Étendre le TTL d'une clé"""
        if not self.redis_client:
            return False
        
        try:
            full_key = self._build_key(key)
            current_ttl = await self.redis_client.ttl(full_key)
            
            if current_ttl > 0:
                new_ttl = min(current_ttl + additional_seconds, self.config.max_ttl)
                await self.redis_client.expire(full_key, new_ttl)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extension du TTL {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalider toutes les clés correspondant à un pattern"""
        if not self.redis_client:
            return 0
        
        try:
            full_pattern = self._build_key(pattern)
            keys = await self.redis_client.keys(full_pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.stats.deletes += deleted
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Erreur lors de l'invalidation par pattern {pattern}: {e}")
            return 0
    
    async def get_cache_size(self) -> Dict[str, int]:
        """Récupérer la taille du cache"""
        if not self.redis_client:
            return {'keys': 0, 'memory': 0}
        
        try:
            # Compter les clés avec notre préfixe
            pattern = self._build_key("*")
            keys = await self.redis_client.keys(pattern)
            
            # Informations mémoire Redis
            info = await self.redis_client.info('memory')
            
            return {
                'keys': len(keys),
                'memory': info.get('used_memory', 0),
                'memory_human': info.get('used_memory_human', '0B')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la taille du cache: {e}")
            return {'keys': 0, 'memory': 0}
    
    async def flush_cache(self) -> bool:
        """Vider tout le cache (attention !)"""
        if not self.redis_client:
            return False
        
        try:
            # Supprimer seulement nos clés
            pattern = self._build_key("*")
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                logger.warning(f"Cache vidé: {len(keys)} clés supprimées")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage du cache: {e}")
            return False
    
    async def _health_check_loop(self):
        """Boucle de vérification de santé"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self.redis_client.ping()
                logger.debug("Health check Redis: OK")
            except Exception as e:
                logger.error(f"Health check Redis échoué: {e}")
                self.stats.errors += 1
    
    async def _stats_loop(self):
        """Boucle de logging des statistiques"""
        while True:
            try:
                await asyncio.sleep(self.config.stats_interval)
                stats = self.stats.to_dict()
                logger.info(f"Cache Stats: {stats}")
            except Exception as e:
                logger.error(f"Erreur dans la boucle de stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du cache"""
        return self.stats.to_dict()
    
    def reset_stats(self):
        """Réinitialiser les statistiques"""
        self.stats = CacheStats()
        logger.info("Statistiques du cache réinitialisées")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.disconnect() 