import asyncio
import time
import pickle
import hashlib
import logging
from typing import Any, Optional, Dict, Set
from collections import defaultdict, OrderedDict
from pathlib import Path
import json
import os

# Imports conditionnels pour les dépendances
try:
    import lz4
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logger = logging.getLogger(__name__)

class SmartCache:
    """
    Cache intelligent avec:
    - Compression LZ4 (si disponible)
    - Prédiction des prochaines requêtes
    - Cache multi-niveaux (L1: mémoire, L2: Redis si disponible)
    - Éviction LRU intelligente
    - Prefetch prédictif basé sur patterns MTG
    
    🚀 OBJECTIFS PLAN EXPERT :
    - Cache hit rate > 80%
    - Prefetch prédictif
    - Compression intelligente
    - Performance < 1s pipeline
    """
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        l1_max_size_mb: int = 100,
        enable_prefetch: bool = True,
        enable_compression: bool = True
    ):
        self.redis_url = redis_url
        self.redis_client = None
        self.redis_available = False
        
        # Configuration L1 cache (mémoire)
        self.l1_cache = OrderedDict()  # LRU cache en mémoire
        self.l1_max_size = l1_max_size_mb * 1024 * 1024  # Convertir en bytes
        self.l1_current_size = 0
        
        # Configuration
        self.enable_prefetch = enable_prefetch
        self.enable_compression = enable_compression and HAS_LZ4
        
        # Patterns d'accès pour prédiction
        self.access_patterns = defaultdict(list)
        
        # Statistiques
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "prefetch_hits": 0,
            "compressions": 0,
            "decompressions": 0
        }
        
        # Prefetch queue
        self.prefetch_queue = asyncio.Queue(maxsize=100) if enable_prefetch else None
        self.prefetch_task = None
        
        # Initialisation
        self._initialize_async()
        
        logger.info("SmartCache initialized", extra={
            'l1_max_size_mb': l1_max_size_mb,
            'compression_enabled': self.enable_compression,
            'prefetch_enabled': enable_prefetch,
            'redis_url': redis_url
        })
    
    def _initialize_async(self):
        """Initialisation asynchrone"""
        if HAS_REDIS:
            try:
                # Initialiser Redis (sera connecté à la première utilisation)
                self.redis_client = redis.from_url(self.redis_url)
                self.redis_available = True
                logger.info("Redis cache L2 configured")
            except Exception as e:
                logger.warning(f"Redis not available, using L1 only: {e}")
                self.redis_available = False
        else:
            logger.info("Redis not installed, using L1 cache only")
        
        # Démarrer prefetch worker si activé
        if self.enable_prefetch:
            self._ensure_prefetch_worker()
    
    def _ensure_prefetch_worker(self):
        """S'assurer que le worker prefetch est démarré"""
        if self.prefetch_task is None:
            try:
                self.prefetch_task = asyncio.create_task(self._prefetch_worker())
            except RuntimeError:
                # Pas d'event loop, sera démarré plus tard
                pass
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupération avec cache intelligent"""
        
        # Check L1 cache (mémoire)
        if key in self.l1_cache:
            # Déplacer en fin pour LRU
            self.l1_cache.move_to_end(key)
            self.cache_stats["hits"] += 1
            self.cache_stats["l1_hits"] += 1
            
            # Enregistrer pattern d'accès
            self._record_access_pattern(key)
            
            # Déclencher prefetch prédictif
            if self.enable_prefetch:
                await self._trigger_prefetch(key)
            
            return self.l1_cache[key]
        
        # Check L2 cache (Redis)
        if self.redis_available:
            try:
                compressed_data = await self.redis_client.get(f"cache:{key}")
                
                if compressed_data:
                    # Décompresser si nécessaire
                    try:
                        if self.enable_compression:
                            data = pickle.loads(lz4.decompress(compressed_data))
                            self.cache_stats["decompressions"] += 1
                        else:
                            data = pickle.loads(compressed_data)
                        
                        # Ajouter à L1
                        self._add_to_l1(key, data)
                        
                        self.cache_stats["hits"] += 1
                        self.cache_stats["l2_hits"] += 1
                        
                        # Patterns et prefetch
                        self._record_access_pattern(key)
                        if self.enable_prefetch:
                            await self._trigger_prefetch(key)
                        
                        return data
                        
                    except Exception as e:
                        logger.error(f"Cache decompression error for {key}: {e}")
                        await self.redis_client.delete(f"cache:{key}")
                        
            except Exception as e:
                logger.warning(f"Redis error for key {key}: {e}")
        
        # Cache miss
        self.cache_stats["misses"] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600,
        skip_l1: bool = False
    ) -> bool:
        """Stockage avec compression intelligente"""
        
        try:
            # Sérialiser
            serialized = pickle.dumps(value)
            
            # Compresser si avantageux
            if self.enable_compression and len(serialized) > 1024:  # > 1KB
                compressed = lz4.compress(serialized)
                compression_ratio = len(compressed) / len(serialized)
                
                if compression_ratio < 0.9:  # Compression efficace
                    data_to_store = compressed
                    self.cache_stats["compressions"] += 1
                else:
                    data_to_store = serialized
            else:
                data_to_store = serialized
            
            # Stocker en L2 (Redis)
            if self.redis_available:
                try:
                    await self.redis_client.set(
                        f"cache:{key}",
                        data_to_store,
                        ex=ttl
                    )
                except Exception as e:
                    logger.warning(f"Redis set error for {key}: {e}")
            
            # Ajouter à L1 si pertinent
            if not skip_l1:
                self._add_to_l1(key, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False
    
    def _add_to_l1(self, key: str, value: Any):
        """Ajouter à L1 avec éviction LRU si nécessaire"""
        
        # Calculer taille approximative
        size = len(pickle.dumps(value))
        
        # Éviction LRU si nécessaire
        while self.l1_current_size + size > self.l1_max_size and self.l1_cache:
            evicted_key, evicted_value = self.l1_cache.popitem(last=False)
            evicted_size = len(pickle.dumps(evicted_value))
            self.l1_current_size -= evicted_size
            logger.debug(f"Evicted {evicted_key} from L1 cache")
        
        # Ajouter nouvelle entrée
        self.l1_cache[key] = value
        self.l1_current_size += size
    
    def _record_access_pattern(self, key: str):
        """Enregistrer pattern d'accès pour prédiction"""
        
        current_time = time.time()
        
        # Garder historique des 10 derniers accès
        self.access_patterns[key].append(current_time)
        if len(self.access_patterns[key]) > 10:
            self.access_patterns[key].pop(0)
    
    async def _trigger_prefetch(self, accessed_key: str):
        """Déclencher prefetch basé sur patterns MTG"""
        
        if not self.enable_prefetch or not self.prefetch_queue:
            return
        
        predictions = self._predict_next_keys(accessed_key)
        
        for predicted_key in predictions:
            if predicted_key not in self.l1_cache:
                try:
                    await self.prefetch_queue.put(predicted_key)
                except asyncio.QueueFull:
                    break
    
    def _predict_next_keys(self, key: str) -> Set[str]:
        """Prédiction intelligente basée sur patterns MTG"""
        
        predictions = set()
        
        # Pattern 1: Après chargement tournois → analyse
        if key.startswith("tournaments_"):
            parts = key.split("_")
            if len(parts) >= 3:
                format_name = parts[1]
                date_range = "_".join(parts[2:])
                
                predictions.update([
                    f"analysis_{format_name}_{date_range}",
                    f"classification_{format_name}_{date_range}",
                    f"archetypes_{format_name}_{date_range}",
                    f"metagame_share_{format_name}_{date_range}"
                ])
        
        # Pattern 2: Après classification → visualisations
        elif key.startswith("classification_"):
            parts = key.split("_", 1)
            if len(parts) > 1:
                suffix = parts[1]
                
                predictions.update([
                    f"pie_chart_{suffix}",
                    f"bar_chart_{suffix}",
                    f"matchup_matrix_{suffix}",
                    f"diversity_index_{suffix}",
                    f"trend_analysis_{suffix}"
                ])
        
        # Pattern 3: Données liées par format
        elif "_Standard_" in key or "_Modern_" in key or "_Legacy_" in key:
            for format_name in ["Standard", "Modern", "Legacy"]:
                if f"_{format_name}_" in key:
                    # Prédire autres données du même format
                    base = key.split(f"_{format_name}_")[0]
                    date = key.split(f"_{format_name}_")[1] if len(key.split(f"_{format_name}_")) > 1 else ""
                    
                    predictions.update([
                        f"metagame_share_{format_name}_{date}",
                        f"top_decks_{format_name}_{date}",
                        f"sideboard_guide_{format_name}",
                        f"matchup_data_{format_name}_{date}"
                    ])
                    break
        
        # Pattern 4: Après analyse → visualisations avancées
        elif key.startswith("analysis_"):
            suffix = key.replace("analysis_", "")
            predictions.update([
                f"advanced_charts_{suffix}",
                f"export_data_{suffix}",
                f"report_html_{suffix}"
            ])
        
        return predictions
    
    async def _prefetch_worker(self):
        """Worker background pour prefetch non-bloquant"""
        
        while True:
            try:
                # Attendre clé à prefetch
                key = await asyncio.wait_for(
                    self.prefetch_queue.get(), 
                    timeout=5.0
                )
                
                # Vérifier si pas déjà en cache
                if key not in self.l1_cache:
                    # Prefetch depuis L2
                    if self.redis_available:
                        try:
                            compressed_data = await self.redis_client.get(f"cache:{key}")
                            
                            if compressed_data:
                                try:
                                    if self.enable_compression:
                                        data = pickle.loads(lz4.decompress(compressed_data))
                                    else:
                                        data = pickle.loads(compressed_data)
                                    
                                    self._add_to_l1(key, data)
                                    self.cache_stats["prefetch_hits"] += 1
                                    logger.debug(f"Prefetched {key} successfully")
                                except Exception as e:
                                    logger.error(f"Prefetch error for {key}: {e}")
                        except Exception as e:
                            logger.warning(f"Prefetch Redis error for {key}: {e}")
                
            except asyncio.TimeoutError:
                continue  # Pas de prefetch à faire
            except Exception as e:
                logger.error(f"Prefetch worker error: {e}")
                await asyncio.sleep(1)
    
    async def invalidate(self, key: str) -> bool:
        """Invalider une clé du cache"""
        
        # Supprimer de L1
        if key in self.l1_cache:
            value = self.l1_cache.pop(key)
            self.l1_current_size -= len(pickle.dumps(value))
        
        # Supprimer de L2
        if self.redis_available:
            try:
                await self.redis_client.delete(f"cache:{key}")
            except Exception as e:
                logger.warning(f"Redis delete error for {key}: {e}")
        
        return True
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalider toutes les clés correspondant à un pattern"""
        
        count = 0
        
        # Invalider L1
        keys_to_remove = [k for k in self.l1_cache.keys() if pattern in k]
        for key in keys_to_remove:
            await self.invalidate(key)
            count += 1
        
        # Invalider L2
        if self.redis_available:
            try:
                keys = await self.redis_client.keys(f"cache:*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    count += len(keys)
            except Exception as e:
                logger.warning(f"Redis pattern delete error: {e}")
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir statistiques du cache"""
        
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / max(1, total_requests) * 100
        
        return {
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total_requests,
            "l1_size_mb": self.l1_current_size / (1024 * 1024),
            "l1_items": len(self.l1_cache),
            "l1_hit_rate": self.cache_stats["l1_hits"] / max(1, self.cache_stats["hits"]) * 100,
            "l2_available": self.redis_available,
            "prefetch_effectiveness": self.cache_stats["prefetch_hits"] / max(1, total_requests) * 100,
            "compression_enabled": self.enable_compression,
            "compression_ratio": f"{self.cache_stats['compressions']}/{total_requests}" if total_requests > 0 else "0",
            **self.cache_stats
        }
    
    async def clear(self):
        """Vider tout le cache"""
        
        # Vider L1
        self.l1_cache.clear()
        self.l1_current_size = 0
        
        # Vider L2
        if self.redis_available:
            try:
                await self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis flush error: {e}")
        
        # Reset stats
        self.cache_stats = {k: 0 for k in self.cache_stats}
        
        logger.info("Cache cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier santé du cache"""
        
        health = {
            "l1_cache": "healthy",
            "l2_cache": "not_available",
            "prefetch": "disabled",
            "compression": "disabled"
        }
        
        # Test L2
        if self.redis_available:
            try:
                await self.redis_client.ping()
                health["l2_cache"] = "healthy"
            except Exception as e:
                health["l2_cache"] = f"error: {e}"
        
        # Test prefetch
        if self.enable_prefetch:
            health["prefetch"] = "enabled"
        
        # Test compression
        if self.enable_compression:
            health["compression"] = "enabled"
        
        return health
    
    def __del__(self):
        """Cleanup lors de la destruction"""
        if self.prefetch_task:
            self.prefetch_task.cancel()


# Instance globale avec configuration optimisée
smart_cache = SmartCache(
    redis_url="redis://localhost:6379",
    l1_max_size_mb=100,
    enable_prefetch=True,
    enable_compression=True
) 