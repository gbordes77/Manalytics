#!/usr/bin/env python3
"""
Démonstration du système de cache intelligent Manalytics.
Montre l'utilisation du cache Redis, TournamentCache et décorateurs.
"""

import asyncio
import json
import time
import random
import sys
import os
from datetime import datetime, timedelta

# Ajouter le chemin vers le module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

# Mock Redis si non disponible
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis non disponible - utilisation du mode simulation")


class MockRedis:
    """Mock Redis pour la démonstration sans serveur Redis"""
    
    def __init__(self):
        self.data = {}
        self.ttl_data = {}
        print("🔧 Mode simulation Redis activé")
    
    async def get(self, key):
        if key in self.data:
            # Vérifier TTL
            if key in self.ttl_data:
                if time.time() > self.ttl_data[key]:
                    del self.data[key]
                    del self.ttl_data[key]
                    return None
            return self.data[key]
        return None
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
        self.ttl_data[key] = time.time() + ttl
    
    async def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                if key in self.ttl_data:
                    del self.ttl_data[key]
                deleted += 1
        return deleted
    
    async def exists(self, key):
        return 1 if key in self.data else 0
    
    async def ttl(self, key):
        if key in self.ttl_data:
            remaining = self.ttl_data[key] - time.time()
            return max(0, int(remaining))
        return -1
    
    async def expire(self, key, ttl):
        if key in self.data:
            self.ttl_data[key] = time.time() + ttl
            return True
        return False
    
    async def keys(self, pattern):
        # Simulation simple
        if pattern.endswith(b'*'):
            prefix = pattern[:-1].decode()
            return [key.encode() for key in self.data.keys() if key.startswith(prefix)]
        return [key.encode() for key in self.data.keys() if pattern.decode() in key]
    
    async def ping(self):
        return True
    
    async def info(self, section):
        return {'used_memory': len(str(self.data)), 'used_memory_human': f'{len(str(self.data))}B'}
    
    async def close(self):
        pass


class MockConnectionPool:
    async def disconnect(self):
        pass


# Données de démonstration
DEMO_TOURNAMENTS = [
    {
        "tournament": {
            "id": "demo_tournament_001",
            "name": "Demo Modern Tournament #1",
            "date": "2024-12-01T10:00:00Z",
            "format": "Modern"
        },
        "decks": [
            {"player": "Alice", "mainboard": [{"name": "Lightning Bolt", "count": 4}]},
            {"player": "Bob", "mainboard": [{"name": "Counterspell", "count": 4}]}
        ]
    },
    {
        "tournament": {
            "id": "demo_tournament_002", 
            "name": "Demo Legacy Tournament",
            "date": "2024-11-15T14:00:00Z",
            "format": "Legacy"
        },
        "decks": [
            {"player": "Charlie", "mainboard": [{"name": "Force of Will", "count": 4}]},
            {"player": "Diana", "mainboard": [{"name": "Brainstorm", "count": 4}]}
        ]
    },
    {
        "tournament": {
            "id": "demo_tournament_003",
            "name": "Demo Pioneer Tournament", 
            "date": "2024-10-01T16:00:00Z",
            "format": "Pioneer"
        },
        "decks": [
            {"player": "Eve", "mainboard": [{"name": "Thoughtseize", "count": 4}]},
            {"player": "Frank", "mainboard": [{"name": "Supreme Verdict", "count": 4}]}
        ]
    }
]


async def demo_redis_cache():
    """Démonstration du cache Redis de base"""
    print("\n🔧 === DÉMONSTRATION REDIS CACHE ===")
    
    # Configuration et patch pour la démo
    if not REDIS_AVAILABLE:
        # Patch le module pour utiliser notre mock
        import cache.redis_cache as redis_cache_module
        redis_cache_module.REDIS_AVAILABLE = True
        redis_cache_module.redis = type('MockRedisModule', (), {
            'ConnectionPool': MockConnectionPool,
            'Redis': lambda connection_pool: MockRedis()
        })()
    
    from cache.redis_cache import RedisCache, CacheConfig
    
    # Configuration
    config = CacheConfig(
        host="localhost",
        port=6379,
        default_ttl=60,
        compression_threshold=50,
        key_prefix="demo:",
        enable_stats=True,
        stats_interval=30
    )
    
    print(f"Configuration: TTL={config.default_ttl}s, compression>{config.compression_threshold} bytes")
    
    # Initialiser le cache
    cache = RedisCache(config)
    if not REDIS_AVAILABLE:
        cache.redis_client = MockRedis()
        cache.redis_pool = MockConnectionPool()
    else:
        await cache.connect()
    
    try:
        # Test des opérations de base
        print("\n📈 Tests des opérations de base...")
        
        # Set/Get simple
        await cache.set("simple_key", "simple_value", 30)
        result = await cache.get("simple_key")
        print(f"  ✅ Set/Get simple: {result}")
        
        # Données JSON
        json_data = {"name": "Test Tournament", "players": 64, "format": "Modern"}
        await cache.set("json_data", json_data, 60)
        result = await cache.get("json_data")
        print(f"  ✅ Données JSON: {result['name']} ({result['players']} joueurs)")
        
        # Données avec compression
        large_data = "x" * 100  # 100 caractères pour déclencher la compression
        await cache.set("large_data", large_data, 60)
        result = await cache.get("large_data")
        print(f"  ✅ Compression: {len(result)} caractères récupérés")
        
        # Test TTL
        await cache.set("ttl_test", "will_expire", 2)
        ttl = await cache.get_ttl("ttl_test")
        print(f"  ✅ TTL: {ttl} secondes restantes")
        
        # Test invalidation par pattern
        await cache.set("pattern_test_1", "value1", 60)
        await cache.set("pattern_test_2", "value2", 60)
        deleted = await cache.invalidate_pattern("pattern_test_*")
        print(f"  ✅ Invalidation pattern: {deleted} clés supprimées")
        
        # Statistiques
        stats = cache.get_stats()
        print(f"\n📊 Statistiques du cache:")
        print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
        print(f"  Taux de hit: {stats['hit_rate']:.2%}")
        print(f"  Éléments compressés: {stats['compressed_items']}")
        
    finally:
        if REDIS_AVAILABLE:
            await cache.disconnect()


async def demo_tournament_cache():
    """Démonstration du cache de tournois spécialisé"""
    print("\n🏆 === DÉMONSTRATION TOURNAMENT CACHE ===")
    
    # Initialiser les caches
    from cache.redis_cache import RedisCache, CacheConfig
    from cache.tournament_cache import TournamentCache
    
    config = CacheConfig(key_prefix="tournament_demo:", enable_stats=False)
    redis_cache = RedisCache(config)
    
    if not REDIS_AVAILABLE:
        redis_cache.redis_client = MockRedis()
        redis_cache.redis_pool = MockConnectionPool()
    else:
        await redis_cache.connect()
    
    tournament_cache = TournamentCache(redis_cache)
    
    try:
        print("Configuration: TTL adaptatif selon l'âge des tournois")
        
        # Cacher des tournois de démonstration
        print("\n📈 Cache des tournois de démonstration...")
        for i, tournament_data in enumerate(DEMO_TOURNAMENTS):
            source = f"demo_source_{i+1}"
            success = await tournament_cache.set_tournament(tournament_data, source)
            tournament_id = tournament_data["tournament"]["id"]
            tournament_name = tournament_data["tournament"]["name"]
            print(f"  ✅ Tournoi caché: {tournament_name} (ID: {tournament_id})")
        
        # Test de récupération
        print("\n📈 Récupération des tournois...")
        for i, tournament_data in enumerate(DEMO_TOURNAMENTS):
            tournament_id = tournament_data["tournament"]["id"]
            source = f"demo_source_{i+1}"
            
            cached_data = await tournament_cache.get_tournament(tournament_id, source)
            if cached_data:
                original_data = cached_data['tournament_data']
                print(f"  ✅ Récupéré: {original_data['tournament']['name']}")
                
                # Test des métadonnées
                metadata = await tournament_cache.get_tournament_metadata(tournament_id, source)
                print(f"    📊 {metadata['deck_count']} decks, caché le {metadata['cached_at'][:19]}")
        
        # Test de détection de doublons
        print("\n📈 Test de détection de doublons...")
        test_tournament = DEMO_TOURNAMENTS[0]
        is_duplicate = await tournament_cache.is_tournament_duplicate(test_tournament, "demo_source_1")
        print(f"  ✅ Doublon détecté: {is_duplicate}")
        
        # Modifier et re-tester
        modified_tournament = test_tournament.copy()
        modified_tournament["tournament"]["name"] = "Modified Tournament Name"
        is_duplicate = await tournament_cache.is_tournament_duplicate(modified_tournament, "demo_source_1")
        print(f"  ✅ Tournoi modifié est doublon: {is_duplicate}")
        
        # Test de recherche par format
        print("\n📈 Recherche par format...")
        modern_tournaments = await tournament_cache.get_tournaments_by_format(
            "Modern", "2024-01-01", "2024-12-31"
        )
        print(f"  ✅ Tournois Modern trouvés: {len(modern_tournaments)}")
        
        # Statistiques du cache de tournois
        stats = await tournament_cache.get_cache_stats()
        print(f"\n📊 Statistiques du cache de tournois:")
        print(f"  Tournois en cache: {stats['tournament_count']}")
        print(f"  Configuration TTL: {stats['ttl_config']}")
        
    finally:
        if REDIS_AVAILABLE:
            await redis_cache.disconnect()


async def demo_cache_decorators():
    """Démonstration des décorateurs de cache"""
    print("\n🎨 === DÉMONSTRATION DÉCORATEURS ===")
    
    # Initialiser le cache
    from cache.redis_cache import RedisCache, CacheConfig
    from cache.tournament_cache import TournamentCache
    from cache.cache_decorators import cached, tournament_cached
    
    config = CacheConfig(key_prefix="decorator_demo:", enable_stats=False)
    redis_cache = RedisCache(config)
    
    if not REDIS_AVAILABLE:
        redis_cache.redis_client = MockRedis()
        redis_cache.redis_pool = MockConnectionPool()
    else:
        await redis_cache.connect()
    
    tournament_cache = TournamentCache(redis_cache)
    
    try:
        # Fonction avec cache simple
        call_count_simple = 0
        
        @cached(redis_cache, ttl=60, key_prefix="api:")
        async def fetch_api_data(endpoint: str, params: dict = None):
            nonlocal call_count_simple
            call_count_simple += 1
            await asyncio.sleep(0.1)  # Simuler un délai réseau
            return {
                "endpoint": endpoint,
                "params": params or {},
                "timestamp": datetime.now().isoformat(),
                "call_number": call_count_simple
            }
        
        print("\n📈 Test du décorateur @cached...")
        
        # Premier appel
        start_time = time.time()
        result1 = await fetch_api_data("/tournaments", {"format": "Modern"})
        time1 = time.time() - start_time
        print(f"  ✅ Premier appel: {time1:.3f}s - Call #{result1['call_number']}")
        
        # Deuxième appel (devrait utiliser le cache)
        start_time = time.time()
        result2 = await fetch_api_data("/tournaments", {"format": "Modern"})
        time2 = time.time() - start_time
        print(f"  ✅ Deuxième appel: {time2:.3f}s - Call #{result2['call_number']} (cache hit)")
        
        # Vérifier que c'est le même résultat
        assert result1['call_number'] == result2['call_number']
        print(f"  ✅ Accélération: {time1/max(time2, 0.001):.1f}x plus rapide")
        
        # Fonction avec cache de tournois
        call_count_tournament = 0
        
        @tournament_cached(tournament_cache, source="api_demo")
        async def fetch_tournament_from_api(tournament_id: str):
            nonlocal call_count_tournament
            call_count_tournament += 1
            await asyncio.sleep(0.2)  # Simuler un appel API lent
            
            # Simuler la récupération d'un tournoi
            if tournament_id == "slow_api_tournament":
                return {
                    "tournament": {
                        "id": tournament_id,
                        "name": f"API Tournament {call_count_tournament}",
                        "date": "2024-12-01T10:00:00Z",
                        "format": "Modern"
                    },
                    "decks": [
                        {"player": f"Player {i+1}", "mainboard": [{"name": "Card", "count": 4}]}
                        for i in range(32)
                    ]
                }
            return None
        
        print("\n📈 Test du décorateur @tournament_cached...")
        
        # Premier appel
        start_time = time.time()
        result1 = await fetch_tournament_from_api("slow_api_tournament")
        time1 = time.time() - start_time
        print(f"  ✅ Premier appel: {time1:.3f}s - {result1['tournament']['name']}")
        
        # Deuxième appel (devrait utiliser le cache)
        start_time = time.time()
        result2 = await fetch_tournament_from_api("slow_api_tournament")
        time2 = time.time() - start_time
        print(f"  ✅ Deuxième appel: {time2:.3f}s - {result2['tournament']['name']} (cache hit)")
        
        print(f"  ✅ Accélération: {time1/max(time2, 0.001):.1f}x plus rapide")
        
    finally:
        if REDIS_AVAILABLE:
            await redis_cache.disconnect()


async def demo_cache_manager():
    """Démonstration du gestionnaire de cache centralisé"""
    print("\n🎛️ === DÉMONSTRATION CACHE MANAGER ===")
    
    from cache.cache_manager import CacheManager
    from cache.redis_cache import CacheConfig
    
    config = CacheConfig(
        key_prefix="manager_demo:",
        enable_stats=True,
        stats_interval=10
    )
    
    # Patch pour la démo si Redis non disponible
    if not REDIS_AVAILABLE:
        import cache.redis_cache as redis_cache_module
        redis_cache_module.REDIS_AVAILABLE = True
        redis_cache_module.redis = type('MockRedisModule', (), {
            'ConnectionPool': MockConnectionPool,
            'Redis': lambda connection_pool: MockRedis()
        })()
    
    manager = CacheManager(config)
    
    try:
        # Initialiser le gestionnaire
        print("📈 Initialisation du gestionnaire...")
        success = await manager.initialize()
        print(f"  ✅ Initialisation: {'Réussie' if success else 'Échouée'}")
        
        # Health check
        print("\n📈 Vérification de santé...")
        health = await manager.health_check()
        print(f"  ✅ Santé globale: {'OK' if health['overall'] else 'PROBLÈME'}")
        print(f"  ✅ Redis: {'OK' if health['redis'] else 'PROBLÈME'}")
        print(f"  ✅ Tournament Cache: {'OK' if health['tournament_cache'] else 'PROBLÈME'}")
        
        # Précharger des données
        print("\n📈 Préchargement de données...")
        success = await manager.preload_tournament_data(
            "Modern", "2024-01-01", "2024-12-31", DEMO_TOURNAMENTS[:2]
        )
        print(f"  ✅ Préchargement: {'Réussi' if success else 'Échoué'}")
        
        # Statistiques globales
        print("\n📈 Statistiques globales...")
        stats = await manager.get_global_stats()
        print(f"  ✅ Connexion: {'Active' if stats['is_connected'] else 'Inactive'}")
        
        global_metrics = stats.get('global_metrics', {})
        print(f"  ✅ Requêtes totales: {global_metrics.get('total_requests', 0)}")
        print(f"  ✅ Taux de hit global: {global_metrics.get('global_hit_rate', 0):.2%}")
        print(f"  ✅ Clés totales: {global_metrics.get('total_keys', 0)}")
        
        # Test d'optimisation
        print("\n📈 Optimisation du cache...")
        optimization_results = await manager.optimize_cache()
        print(f"  ✅ Clés expirées nettoyées: {optimization_results.get('expired_keys_cleaned', 0)}")
        print(f"  ✅ Clés de tournois rafraîchies: {optimization_results.get('tournament_keys_refreshed', 0)}")
        
        # Sauvegarde des clés
        print("\n📈 Sauvegarde des clés...")
        backup = await manager.backup_cache_keys()
        total_keys = sum(len(keys) for keys in backup.values())
        print(f"  ✅ Clés sauvegardées: {total_keys} au total")
        for key_type, keys in backup.items():
            print(f"    - {key_type}: {len(keys)} clés")
        
    finally:
        await manager.shutdown()
        print("  ✅ Gestionnaire arrêté")


async def demo_performance_comparison():
    """Démonstration des gains de performance"""
    print("\n⚡ === DÉMONSTRATION PERFORMANCE ===")
    
    from cache.redis_cache import RedisCache, CacheConfig
    from cache.cache_decorators import cached
    
    config = CacheConfig(key_prefix="perf_demo:", enable_stats=False)
    redis_cache = RedisCache(config)
    
    if not REDIS_AVAILABLE:
        redis_cache.redis_client = MockRedis()
        redis_cache.redis_pool = MockConnectionPool()
    else:
        await redis_cache.connect()
    
    try:
        # Fonction lente simulée
        async def slow_computation(n: int):
            """Simule un calcul ou appel API lent"""
            await asyncio.sleep(0.1)  # 100ms de délai
            return sum(i*i for i in range(n))
        
        # Version avec cache
        @cached(redis_cache, ttl=300)
        async def cached_slow_computation(n: int):
            return await slow_computation(n)
        
        print("Comparaison de performance: calcul sans/avec cache")
        
        # Test sans cache
        print("\n📈 Tests sans cache...")
        start_time = time.time()
        results_no_cache = []
        for i in range(5):
            result = await slow_computation(1000)
            results_no_cache.append(result)
        time_no_cache = time.time() - start_time
        print(f"  ✅ 5 appels sans cache: {time_no_cache:.3f}s")
        
        # Test avec cache
        print("\n📈 Tests avec cache...")
        start_time = time.time()
        results_with_cache = []
        for i in range(5):
            result = await cached_slow_computation(1000)
            results_with_cache.append(result)
        time_with_cache = time.time() - start_time
        print(f"  ✅ 5 appels avec cache: {time_with_cache:.3f}s")
        
        # Calcul des gains
        speedup = time_no_cache / time_with_cache
        print(f"\n🚀 Gains de performance:")
        print(f"  ✅ Accélération: {speedup:.1f}x plus rapide")
        print(f"  ✅ Temps économisé: {time_no_cache - time_with_cache:.3f}s")
        print(f"  ✅ Réduction: {(1 - time_with_cache/time_no_cache)*100:.1f}%")
        
        # Vérifier que les résultats sont identiques
        assert results_no_cache == results_with_cache
        print(f"  ✅ Résultats identiques: {results_no_cache[0]}")
        
        # Statistiques du cache
        stats = redis_cache.get_stats()
        print(f"\n📊 Statistiques finales:")
        print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
        print(f"  Taux de hit: {stats['hit_rate']:.2%}")
        
    finally:
        if REDIS_AVAILABLE:
            await redis_cache.disconnect()


async def main():
    """Fonction principale de démonstration"""
    print("🎯 === DÉMONSTRATION SYSTÈME DE CACHE MANALYTICS ===")
    print("Ce script démontre les capacités du système de cache intelligent.")
    
    if not REDIS_AVAILABLE:
        print("⚠️ Redis non disponible - démonstration en mode simulation")
    else:
        print("✅ Redis disponible - démonstration complète")
    
    try:
        await demo_redis_cache()
        await demo_tournament_cache()
        await demo_cache_decorators()
        await demo_cache_manager()
        await demo_performance_comparison()
        
        print("\n🎉 === DÉMONSTRATION TERMINÉE ===")
        print("Le système de cache intelligent est opérationnel !")
        print("\n📋 Fonctionnalités démontrées:")
        print("  ✅ Cache Redis avec compression et TTL")
        print("  ✅ Cache spécialisé pour tournois MTG")
        print("  ✅ Décorateurs pour cache automatique")
        print("  ✅ Gestionnaire centralisé")
        print("  ✅ Gains de performance significatifs")
        
    except Exception as e:
        print(f"\n❌ Erreur dans la démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 