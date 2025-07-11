"""
Tests pour le système de cache intelligent.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Ajouter le chemin vers le module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

# Mock Redis si non disponible
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class MockRedis:
    """Mock Redis pour les tests sans Redis"""
    
    def __init__(self):
        self.data = {}
        self.ttl_data = {}
    
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
    
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
            if key in self.ttl_data:
                del self.ttl_data[key]
            return 1
        return 0
    
    async def exists(self, key):
        return 1 if key in self.data else 0
    
    async def ttl(self, key):
        if key in self.ttl_data:
            remaining = self.ttl_data[key] - time.time()
            return max(1, int(remaining))  # Retourner au moins 1 pour les tests
        return -1
    
    async def expire(self, key, ttl):
        if key in self.data:
            self.ttl_data[key] = time.time() + ttl
            return True
        return False
    
    async def keys(self, pattern):
        # Simulation simple
        return [key.encode() for key in self.data.keys() if "*" in pattern or key.startswith(pattern)]
    
    async def ping(self):
        return True
    
    async def info(self, section):
        return {'used_memory': 1024, 'used_memory_human': '1KB'}
    
    async def close(self):
        pass


class MockConnectionPool:
    async def disconnect(self):
        pass


@pytest.fixture
def mock_redis():
    """Fixture pour un mock Redis"""
    return MockRedis()


@pytest.fixture
def cache_config():
    """Fixture pour la configuration du cache"""
    from cache.redis_cache import CacheConfig
    return CacheConfig(
        host="localhost",
        port=6379,
        db=0,
        default_ttl=3600,
        compression_threshold=100,
        key_prefix="test:",
        enable_stats=False  # Désactiver pour les tests
    )


class TestRedisCache:
    """Tests pour RedisCache"""
    
    @pytest.mark.asyncio
    async def test_redis_cache_init(self, cache_config):
        """Test de l'initialisation du cache Redis"""
        from cache.redis_cache import RedisCache
        
        # Mock Redis pour éviter l'erreur d'import
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                cache = RedisCache(cache_config)
                assert cache.config == cache_config
                assert cache.stats.hits == 0
                assert cache.stats.misses == 0
    
    @pytest.mark.asyncio
    async def test_redis_cache_operations(self, cache_config, mock_redis):
        """Test des opérations de base du cache"""
        from cache.redis_cache import RedisCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                cache = RedisCache(cache_config)
                cache.redis_client = mock_redis
                
                # Test set/get
                await cache.set("test_key", "test_value", 60)
                result = await cache.get("test_key")
                assert result == "test_value"
                
                # Test miss
                result = await cache.get("nonexistent_key")
                assert result is None
                
                # Test delete
                success = await cache.delete("test_key")
                assert success is True
                
                result = await cache.get("test_key")
                assert result is None
    
    @pytest.mark.asyncio
    async def test_redis_cache_serialization(self, cache_config, mock_redis):
        """Test de la sérialisation/désérialisation"""
        from cache.redis_cache import RedisCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                cache = RedisCache(cache_config)
                cache.redis_client = mock_redis
                
                # Test données JSON
                test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
                await cache.set("json_test", test_data)
                result = await cache.get("json_test")
                assert result == test_data
                
                # Test données complexes (pickle)
                complex_data = {"datetime": time.time(), "set": {1, 2, 3}}
                await cache.set("complex_test", complex_data)
                result = await cache.get("complex_test")
                assert result["datetime"] == complex_data["datetime"]
    
    @pytest.mark.asyncio
    async def test_redis_cache_compression(self, cache_config, mock_redis):
        """Test de la compression automatique"""
        from cache.redis_cache import RedisCache
        
        # Configuration avec seuil de compression bas
        cache_config.compression_threshold = 10
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                cache = RedisCache(cache_config)
                cache.redis_client = mock_redis
                
                # Données assez grandes pour déclencher la compression
                large_data = "x" * 50  # 50 caractères
                await cache.set("large_test", large_data)
                result = await cache.get("large_test")
                assert result == large_data
                
                # Vérifier que la compression a été utilisée
                assert cache.stats.compressed_items > 0
    
    @pytest.mark.asyncio
    async def test_redis_cache_ttl(self, cache_config, mock_redis):
        """Test de la gestion des TTL"""
        from cache.redis_cache import RedisCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                cache = RedisCache(cache_config)
                cache.redis_client = mock_redis
                
                # Test TTL
                await cache.set("ttl_test", "value", 1)  # 1 seconde
                
                # Vérifier existence
                assert await cache.exists("ttl_test") is True
                
                # Vérifier TTL
                ttl = await cache.get_ttl("ttl_test")
                assert ttl is not None and ttl > 0
                
                # Étendre TTL
                success = await cache.extend_ttl("ttl_test", 10)
                assert success is True


@pytest.fixture
def tournament_data():
    """Fixture pour données de tournoi"""
    return {
        "tournament": {
            "id": "test_tournament_123",
            "name": "Test Tournament",
            "date": "2024-01-15T10:00:00Z",
            "format": "Modern"
        },
        "decks": [
            {
                "player": "Player 1",
                "mainboard": [{"name": "Lightning Bolt", "count": 4}]
            },
            {
                "player": "Player 2", 
                "mainboard": [{"name": "Counterspell", "count": 4}]
            }
        ]
    }


class TestTournamentCache:
    """Tests pour TournamentCache"""
    
    @pytest.mark.asyncio
    async def test_tournament_cache_init(self, cache_config, mock_redis):
        """Test de l'initialisation du cache de tournois"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                assert tournament_cache.redis_cache == redis_cache
                assert len(tournament_cache.tournament_keys) == 0
    
    @pytest.mark.asyncio
    async def test_tournament_cache_operations(self, cache_config, mock_redis, tournament_data):
        """Test des opérations du cache de tournois"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                # Test set/get tournament
                success = await tournament_cache.set_tournament(tournament_data, "test_source")
                assert success is True
                
                # Vérifier existence
                exists = await tournament_cache.tournament_exists("test_tournament_123", "test_source")
                assert exists is True
                
                # Récupérer le tournoi
                cached_data = await tournament_cache.get_tournament("test_tournament_123", "test_source")
                assert cached_data is not None
                assert cached_data['tournament_data'] == tournament_data
    
    @pytest.mark.asyncio
    async def test_tournament_cache_ttl_calculation(self, cache_config, mock_redis):
        """Test du calcul de TTL adaptatif"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                # Test avec tournoi récent
                recent_date = "2024-12-01T10:00:00Z"
                ttl_recent = tournament_cache._calculate_tournament_ttl(recent_date)
                
                # Test avec tournoi ancien
                old_date = "2024-01-01T10:00:00Z"
                ttl_old = tournament_cache._calculate_tournament_ttl(old_date)
                
                # Le TTL des tournois anciens devrait être plus long
                assert ttl_old >= ttl_recent
    
    @pytest.mark.asyncio
    async def test_tournament_cache_duplicate_detection(self, cache_config, mock_redis, tournament_data):
        """Test de la détection de doublons"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                # Cacher le tournoi
                await tournament_cache.set_tournament(tournament_data, "test_source")
                
                # Vérifier que c'est un doublon
                is_duplicate = await tournament_cache.is_tournament_duplicate(tournament_data, "test_source")
                assert is_duplicate is True
                
                # Modifier les données et vérifier que ce n'est plus un doublon
                modified_data = tournament_data.copy()
                modified_data["tournament"]["name"] = "Modified Tournament"
                
                is_duplicate = await tournament_cache.is_tournament_duplicate(modified_data, "test_source")
                assert is_duplicate is False
    
    @pytest.mark.asyncio
    async def test_tournament_cache_metadata(self, cache_config, mock_redis, tournament_data):
        """Test de la récupération des métadonnées"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                # Cacher le tournoi
                await tournament_cache.set_tournament(tournament_data, "test_source")
                
                # Récupérer les métadonnées
                metadata = await tournament_cache.get_tournament_metadata("test_tournament_123", "test_source")
                
                assert metadata is not None
                assert metadata['id'] == "test_tournament_123"
                assert metadata['name'] == "Test Tournament"
                assert metadata['format'] == "Modern"
                assert metadata['deck_count'] == 2
                assert metadata['source'] == "test_source"


class TestCacheDecorators:
    """Tests pour les décorateurs de cache"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self, cache_config, mock_redis):
        """Test du décorateur @cached"""
        from cache.redis_cache import RedisCache
        from cache.cache_decorators import cached
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                call_count = 0
                
                @cached(redis_cache, ttl=60, key_prefix="test:")
                async def test_function(arg1, arg2="default"):
                    nonlocal call_count
                    call_count += 1
                    return f"result_{arg1}_{arg2}"
                
                # Premier appel - devrait exécuter la fonction
                result1 = await test_function("value1", arg2="value2")
                assert result1 == "result_value1_value2"
                assert call_count == 1
                
                # Deuxième appel avec mêmes arguments - devrait utiliser le cache
                result2 = await test_function("value1", arg2="value2")
                assert result2 == "result_value1_value2"
                assert call_count == 1  # Pas d'appel supplémentaire
                
                # Appel avec arguments différents - devrait exécuter la fonction
                result3 = await test_function("value3")
                assert result3 == "result_value3_default"
                assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_tournament_cached_decorator(self, cache_config, mock_redis, tournament_data):
        """Test du décorateur @tournament_cached"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        from cache.cache_decorators import tournament_cached
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                call_count = 0
                
                @tournament_cached(tournament_cache, source="test_source")
                async def fetch_tournament(tournament_id):
                    nonlocal call_count
                    call_count += 1
                    return tournament_data if tournament_id == "test_tournament_123" else None
                
                # Premier appel - devrait exécuter la fonction
                result1 = await fetch_tournament("test_tournament_123")
                assert result1 == tournament_data
                assert call_count == 1
                
                # Deuxième appel - devrait utiliser le cache
                result2 = await fetch_tournament("test_tournament_123")
                assert result2 == tournament_data
                assert call_count == 1  # Pas d'appel supplémentaire


class TestCacheManager:
    """Tests pour CacheManager"""
    
    @pytest.mark.asyncio
    async def test_cache_manager_init(self, cache_config):
        """Test de l'initialisation du gestionnaire de cache"""
        from cache.cache_manager import CacheManager
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                manager = CacheManager(cache_config)
                assert manager.config == cache_config
                assert manager.is_connected is False
    
    @pytest.mark.asyncio
    async def test_cache_manager_health_check(self, cache_config, mock_redis):
        """Test du health check du gestionnaire"""
        from cache.cache_manager import CacheManager
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                manager = CacheManager(cache_config)
                
                # Mock l'initialisation
                manager.redis_cache = MagicMock()
                manager.redis_cache.redis_client = mock_redis
                manager.tournament_cache = MagicMock()
                manager.tournament_cache.redis_cache = MagicMock()
                manager.tournament_cache.redis_cache.set = AsyncMock(return_value=True)
                manager.tournament_cache.redis_cache.get = AsyncMock(return_value="test")
                manager.tournament_cache.redis_cache.delete = AsyncMock(return_value=True)
                
                health = await manager.health_check()
                
                assert health['overall'] is True
                assert health['redis'] is True
                assert health['tournament_cache'] is True
                assert len(health['errors']) == 0


class TestCacheIntegration:
    """Tests d'intégration du système de cache"""
    
    @pytest.mark.asyncio
    async def test_full_cache_workflow(self, cache_config, mock_redis, tournament_data):
        """Test du workflow complet du cache"""
        from cache.redis_cache import RedisCache
        from cache.tournament_cache import TournamentCache
        from cache.cache_manager import CacheManager
        
        with patch('cache.redis_cache.REDIS_AVAILABLE', True):
            with patch('cache.redis_cache.redis'):
                # Initialiser le système complet
                redis_cache = RedisCache(cache_config)
                redis_cache.redis_client = mock_redis
                
                tournament_cache = TournamentCache(redis_cache)
                
                # Test du workflow complet
                # 1. Cacher un tournoi
                success = await tournament_cache.set_tournament(tournament_data, "integration_test")
                assert success is True
                
                # 2. Vérifier qu'il existe
                exists = await tournament_cache.tournament_exists("test_tournament_123", "integration_test")
                assert exists is True
                
                # 3. Récupérer les données
                cached_data = await tournament_cache.get_tournament("test_tournament_123", "integration_test")
                assert cached_data is not None
                assert cached_data['tournament_data'] == tournament_data
                
                # 4. Vérifier les métadonnées
                metadata = await tournament_cache.get_tournament_metadata("test_tournament_123", "integration_test")
                assert metadata['id'] == "test_tournament_123"
                assert metadata['source'] == "integration_test"
                
                # 5. Test de détection de doublon
                is_duplicate = await tournament_cache.is_tournament_duplicate(tournament_data, "integration_test")
                assert is_duplicate is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 