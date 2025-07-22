"""
Décorateurs pour simplifier l'utilisation des patterns de résilience.
Permet d'ajouter facilement circuit breaker et retry aux fonctions.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Tuple, Union

from .circuit_breaker import CircuitBreaker, CircuitBreakerError
from .error_monitor import ErrorMonitor
from .retry_handler import RetryConfig, RetryExhaustedError, RetryHandler

logger = logging.getLogger(__name__)


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: tuple = (Exception,),
    name: Optional[str] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
):
    """
    Décorateur pour ajouter un circuit breaker à une fonction.

    Args:
        failure_threshold: Nombre d'échecs avant ouverture du circuit
        recovery_timeout: Temps d'attente avant tentative de récupération
        expected_exception: Types d'exceptions à surveiller
        name: Nom du circuit breaker (par défaut: nom de la fonction)
        circuit_breaker: Instance existante de CircuitBreaker à utiliser

    Example:
        @with_circuit_breaker(failure_threshold=3, recovery_timeout=30)
        async def fetch_data():
            # Code qui peut échouer
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Utiliser l'instance fournie ou créer une nouvelle
        cb = circuit_breaker or CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name or f"{func.__module__}.{func.__name__}",
        )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Pour les fonctions synchrones, utiliser asyncio.run
            return asyncio.run(cb.call(func, *args, **kwargs))

        # Ajouter l'instance du circuit breaker comme attribut
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper._circuit_breaker = cb

        return wrapper

    return decorator


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: str = "exponential",
    backoff_multiplier: float = 2.0,
    jitter_range: float = 0.1,
    retryable_exceptions: tuple = (Exception,),
    name: Optional[str] = None,
    retry_handler: Optional[RetryHandler] = None,
):
    """
    Décorateur pour ajouter un retry automatique à une fonction.

    Args:
        max_attempts: Nombre maximum de tentatives
        base_delay: Délai de base entre les tentatives
        max_delay: Délai maximum entre les tentatives
        strategy: Stratégie de retry ("linear", "exponential", "exponential_jitter", "fixed")
        backoff_multiplier: Multiplicateur pour le backoff exponentiel
        jitter_range: Plage de variation pour le jitter
        retryable_exceptions: Types d'exceptions à retry
        name: Nom du retry handler
        retry_handler: Instance existante de RetryHandler à utiliser

    Example:
        @with_retry(max_attempts=3, strategy="exponential_jitter")
        async def unreliable_operation():
            # Code qui peut échouer temporairement
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Utiliser l'instance fournie ou créer une nouvelle
        from .retry_handler import RetryStrategy

        strategy_enum = (
            RetryStrategy(strategy) if isinstance(strategy, str) else strategy
        )

        rh = retry_handler or RetryHandler(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy_enum,
            backoff_multiplier=backoff_multiplier,
            jitter_range=jitter_range,
            retryable_exceptions=retryable_exceptions,
            name=name or f"{func.__module__}.{func.__name__}",
        )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await rh.call(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Pour les fonctions synchrones, utiliser asyncio.run
            return asyncio.run(rh.call(func, *args, **kwargs))

        # Ajouter l'instance du retry handler comme attribut
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper._retry_handler = rh

        return wrapper

    return decorator


def with_error_monitoring(
    component: Optional[str] = None,
    error_monitor: Optional[ErrorMonitor] = None,
    severity: str = "ERROR",
    include_context: bool = True,
):
    """
    Décorateur pour ajouter un monitoring d'erreurs à une fonction.

    Args:
        component: Nom du composant (par défaut: nom de la fonction)
        error_monitor: Instance existante d'ErrorMonitor à utiliser
        severity: Niveau de sévérité des erreurs
        include_context: Inclure les arguments dans le contexte

    Example:
        @with_error_monitoring(component="scraper", severity="WARNING")
        async def scrape_data():
            # Code à monitorer
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Utiliser l'instance fournie ou créer une nouvelle
        em = error_monitor or ErrorMonitor(name="GlobalErrorMonitor")
        comp_name = component or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {}
                if include_context:
                    context = {
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    }

                em.record_error(e, comp_name, severity, context)
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {}
                if include_context:
                    context = {
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    }

                em.record_error(e, comp_name, severity, context)
                raise

        # Ajouter l'instance du error monitor comme attribut
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper._error_monitor = em

        return wrapper

    return decorator


def resilient(
    # Circuit Breaker params
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    # Retry params
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retry_strategy: str = "exponential_jitter",
    # Error monitoring params
    component: Optional[str] = None,
    monitor_errors: bool = True,
    # Shared params
    expected_exceptions: tuple = (Exception,),
    name: Optional[str] = None,
):
    """
    Décorateur combiné pour ajouter circuit breaker, retry et monitoring.

    Args:
        failure_threshold: Seuil d'échec pour circuit breaker
        recovery_timeout: Timeout de récupération circuit breaker
        max_attempts: Nombre maximum de tentatives retry
        base_delay: Délai de base retry
        retry_strategy: Stratégie de retry
        component: Nom du composant pour monitoring
        monitor_errors: Activer le monitoring d'erreurs
        expected_exceptions: Types d'exceptions à gérer
        name: Nom pour tous les composants

    Example:
        @resilient(
            failure_threshold=3,
            max_attempts=5,
            retry_strategy="exponential_jitter",
            component="api_client"
        )
        async def call_external_api():
            # Code robuste avec toutes les protections
            pass
    """

    def decorator(func: Callable) -> Callable:
        func_name = name or f"{func.__module__}.{func.__name__}"
        comp_name = component or func_name

        # Créer les instances
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exceptions,
            name=f"{func_name}_CB",
        )

        from .retry_handler import RetryStrategy

        rh = RetryHandler(
            max_attempts=max_attempts,
            base_delay=base_delay,
            strategy=RetryStrategy(retry_strategy),
            retryable_exceptions=expected_exceptions,
            name=f"{func_name}_Retry",
        )

        em = ErrorMonitor(name=f"{func_name}_Monitor") if monitor_errors else None

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Appliquer circuit breaker puis retry
                async def retry_with_cb():
                    return await cb.call(func, *args, **kwargs)

                return await rh.call(retry_with_cb)

            except Exception as e:
                # Enregistrer l'erreur si monitoring activé
                if em:
                    context = {
                        "function": func.__name__,
                        "circuit_breaker_state": cb.state.value,
                        "retry_attempts": rh.total_retries,
                    }
                    em.record_error(e, comp_name, "ERROR", context)
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                # Version synchrone
                async def async_version():
                    async def retry_with_cb():
                        return await cb.call(func, *args, **kwargs)

                    return await rh.call(retry_with_cb)

                return asyncio.run(async_version())

            except Exception as e:
                if em:
                    context = {
                        "function": func.__name__,
                        "circuit_breaker_state": cb.state.value,
                        "retry_attempts": rh.total_retries,
                    }
                    em.record_error(e, comp_name, "ERROR", context)
                raise

        # Ajouter les instances comme attributs
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper._circuit_breaker = cb
        wrapper._retry_handler = rh
        wrapper._error_monitor = em
        wrapper._resilience_stats = lambda: {
            "circuit_breaker": cb.get_stats(),
            "retry_handler": rh.get_stats(),
            "error_monitor": em.get_error_summary() if em else None,
        }

        return wrapper

    return decorator


# Décorateurs prédéfinis pour des cas d'usage courants
def network_resilient(name: Optional[str] = None):
    """Décorateur prédéfini pour les opérations réseau"""
    return resilient(
        failure_threshold=3,
        recovery_timeout=30,
        max_attempts=3,
        base_delay=1.0,
        retry_strategy="exponential_jitter",
        expected_exceptions=(ConnectionError, TimeoutError, OSError),
        name=name,
    )


def database_resilient(name: Optional[str] = None):
    """Décorateur prédéfini pour les opérations base de données"""
    return resilient(
        failure_threshold=5,
        recovery_timeout=60,
        max_attempts=5,
        base_delay=0.5,
        retry_strategy="exponential",
        expected_exceptions=(ConnectionError, TimeoutError),
        name=name,
    )


def file_resilient(name: Optional[str] = None):
    """Décorateur prédéfini pour les opérations fichier"""
    return resilient(
        failure_threshold=3,
        recovery_timeout=10,
        max_attempts=3,
        base_delay=0.1,
        retry_strategy="linear",
        expected_exceptions=(OSError, IOError),
        name=name,
    )
