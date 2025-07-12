"""
Décorateurs pour simplifier l'utilisation du cache.
"""

import asyncio
import functools
import hashlib
import json
from typing import Any, Callable, Optional, Union, Dict
import logging

logger = logging.getLogger(__name__)


def cache_key_builder(*args, **kwargs) -> str:
    """Construire une clé de cache à partir des arguments"""
    # Créer une représentation stable des arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    
    # Sérialiser et hasher
    json_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()


def cached(
    cache_instance: Any,
    ttl: Optional[int] = None,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None,
    skip_cache_on_error: bool = True
):
    """
    Décorateur pour cacher automatiquement les résultats d'une fonction.
    
    Args:
        cache_instance: Instance du cache (RedisCache ou TournamentCache)
        ttl: Durée de vie du cache en secondes
        key_prefix: Préfixe pour les clés de cache
        key_builder: Fonction pour construire les clés de cache
        skip_cache_on_error: Si True, ignore les erreurs de cache
    
    Example:
        @cached(redis_cache, ttl=3600, key_prefix="api:")
        async def fetch_tournament(tournament_id: str):
            # Code de récupération
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Construire la clé de cache
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_key_builder(*args, **kwargs)
            
            # Ajouter le préfixe et le nom de la fonction
            full_key = f"{key_prefix}{func.__name__}:{cache_key}"
            
            try:
                # Essayer de récupérer depuis le cache
                cached_result = await cache_instance.get(full_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit pour {full_key}")
                    return cached_result
                
                # Cache miss - exécuter la fonction
                logger.debug(f"Cache miss pour {full_key}")
                result = await func(*args, **kwargs)
                
                # Stocker le résultat dans le cache
                await cache_instance.set(full_key, result, ttl)
                return result
                
            except Exception as e:
                logger.error(f"Erreur de cache pour {full_key}: {e}")
                if skip_cache_on_error:
                    # Exécuter la fonction sans cache
                    return await func(*args, **kwargs)
                else:
                    raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Version synchrone (utilise asyncio.run)
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Retourner la version appropriée
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def tournament_cached(
    tournament_cache_instance: Any,
    ttl: Optional[int] = None,
    source: str = "",
    check_duplicates: bool = True
):
    """
    Décorateur spécialisé pour cacher les données de tournois.
    
    Args:
        tournament_cache_instance: Instance du TournamentCache
        ttl: Durée de vie du cache (None = TTL adaptatif)
        source: Source des données (pour la clé)
        check_duplicates: Vérifier les doublons avant de cacher
    
    Example:
        @tournament_cached(tournament_cache, source="melee")
        async def fetch_tournament_data(tournament_id: str):
            # Code de récupération
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extraire l'ID du tournoi (premier argument par convention)
            tournament_id = args[0] if args else kwargs.get('tournament_id')
            
            if not tournament_id:
                logger.warning("Impossible de cacher sans tournament_id")
                return await func(*args, **kwargs)
            
            try:
                # Vérifier si le tournoi existe déjà
                if await tournament_cache_instance.tournament_exists(tournament_id, source):
                    cached_data = await tournament_cache_instance.get_tournament(tournament_id, source)
                    if cached_data:
                        logger.debug(f"Tournoi trouvé dans le cache: {tournament_id}")
                        return cached_data.get('tournament_data')
                
                # Cache miss - récupérer les données
                logger.debug(f"Récupération du tournoi: {tournament_id}")
                tournament_data = await func(*args, **kwargs)
                
                if tournament_data:
                    # Vérifier les doublons si demandé
                    if check_duplicates:
                        if await tournament_cache_instance.is_tournament_duplicate(tournament_data, source):
                            logger.debug(f"Tournoi dupliqué détecté: {tournament_id}")
                            return tournament_data
                    
                    # Cacher le tournoi
                    await tournament_cache_instance.set_tournament(tournament_data, source)
                
                return tournament_data
                
            except Exception as e:
                logger.error(f"Erreur de cache tournoi pour {tournament_id}: {e}")
                # Fallback vers la fonction originale
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_invalidate(
    cache_instance: Any,
    pattern: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Décorateur pour invalider automatiquement le cache après une opération.
    
    Args:
        cache_instance: Instance du cache
        pattern: Pattern pour l'invalidation (ou clé exacte)
        key_builder: Fonction pour construire la clé d'invalidation
    
    Example:
        @cache_invalidate(redis_cache, pattern="tournament:*")
        async def update_tournament(tournament_id: str):
            # Code de mise à jour
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Exécuter la fonction
            result = await func(*args, **kwargs)
            
            try:
                # Invalider le cache
                if key_builder:
                    invalidate_key = key_builder(*args, **kwargs)
                elif pattern:
                    invalidate_key = pattern
                else:
                    # Utiliser le nom de la fonction comme pattern
                    invalidate_key = f"{func.__name__}:*"
                
                # Invalider
                if hasattr(cache_instance, 'invalidate_pattern'):
                    deleted = await cache_instance.invalidate_pattern(invalidate_key)
                    logger.debug(f"Cache invalidé: {deleted} clés supprimées pour {invalidate_key}")
                else:
                    await cache_instance.delete(invalidate_key)
                    logger.debug(f"Cache invalidé: {invalidate_key}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'invalidation du cache: {e}")
                # Ne pas faire échouer la fonction principale
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def conditional_cache(
    cache_instance: Any,
    condition: Callable,
    ttl: Optional[int] = None,
    key_prefix: str = ""
):
    """
    Décorateur pour cacher conditionnellement les résultats.
    
    Args:
        cache_instance: Instance du cache
        condition: Fonction qui détermine si on doit cacher (args, kwargs, result) -> bool
        ttl: Durée de vie du cache
        key_prefix: Préfixe pour les clés
    
    Example:
        @conditional_cache(
            redis_cache,
            condition=lambda args, kwargs, result: len(result) > 10,
            ttl=3600
        )
        async def search_tournaments(query: str):
            # Code de recherche
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Construire la clé de cache
            cache_key = f"{key_prefix}{func.__name__}:{cache_key_builder(*args, **kwargs)}"
            
            try:
                # Essayer le cache
                cached_result = await cache_instance.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Exécuter la fonction
                result = await func(*args, **kwargs)
                
                # Vérifier la condition pour cacher
                if condition(args, kwargs, result):
                    await cache_instance.set(cache_key, result, ttl)
                    logger.debug(f"Résultat caché conditionnellement: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Erreur de cache conditionnel: {e}")
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Décorateurs prédéfinis pour des cas d'usage courants
def cache_tournament_metadata(cache_instance: Any, ttl: int = 3600):
    """Décorateur prédéfini pour cacher les métadonnées de tournois"""
    return cached(
        cache_instance,
        ttl=ttl,
        key_prefix="tournament_meta:",
        skip_cache_on_error=True
    )


def cache_format_data(cache_instance: Any, ttl: int = 1800):
    """Décorateur prédéfini pour cacher les données de format"""
    return cached(
        cache_instance,
        ttl=ttl,
        key_prefix="format_data:",
        skip_cache_on_error=True
    )


def cache_large_results_only(cache_instance: Any, min_size: int = 100):
    """Décorateur pour cacher seulement les gros résultats"""
    def size_condition(args, kwargs, result):
        if isinstance(result, (list, dict)):
            return len(result) >= min_size
        return False
    
    return conditional_cache(
        cache_instance,
        condition=size_condition,
        ttl=3600,
        key_prefix="large_results:"
    ) 