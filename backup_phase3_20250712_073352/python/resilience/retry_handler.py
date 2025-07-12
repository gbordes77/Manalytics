"""
Gestionnaire de retry avec différentes stratégies.
Implémente retry linéaire, exponentiel, avec jitter.
"""

import asyncio
import random
import time
from typing import Callable, Any, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Stratégies de retry disponibles"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"
    FIXED = "fixed"


class RetryExhaustedError(Exception):
    """Exception levée quand tous les retry sont épuisés"""
    pass


class RetryHandler:
    """
    Gestionnaire de retry avec différentes stratégies.
    
    Stratégies supportées :
    - LINEAR : Délai constant entre chaque tentative
    - EXPONENTIAL : Délai doublé à chaque tentative
    - EXPONENTIAL_JITTER : Exponentiel avec variation aléatoire
    - FIXED : Délai fixe entre chaque tentative
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_multiplier: float = 2.0,
        jitter_range: float = 0.1,
        retryable_exceptions: tuple = (Exception,),
        name: str = "RetryHandler"
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_multiplier = backoff_multiplier
        self.jitter_range = jitter_range
        self.retryable_exceptions = retryable_exceptions
        self.name = name
        
        # Statistiques
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_retries = 0
        
        logger.info(f"Retry Handler '{name}' initialisé: "
                   f"max_attempts={max_attempts}, strategy={strategy.value if hasattr(strategy, 'value') else strategy}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute une fonction avec retry automatique.
        
        Args:
            func: Fonction à exécuter
            *args, **kwargs: Arguments de la fonction
            
        Returns:
            Résultat de la fonction
            
        Raises:
            RetryExhaustedError: Si tous les retry sont épuisés
        """
        self.total_calls += 1
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                # Exécuter la fonction
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Succès
                if attempt > 1:
                    logger.info(f"Retry Handler '{self.name}' succès à la tentative {attempt}")
                
                self.successful_calls += 1
                return result
                
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt == self.max_attempts:
                    # Dernier essai échoué
                    logger.error(f"Retry Handler '{self.name}' échec après {self.max_attempts} tentatives: {e}")
                    self.failed_calls += 1
                    break
                
                # Calculer le délai avant retry
                delay = self._calculate_delay(attempt)
                
                logger.warning(f"Retry Handler '{self.name}' tentative {attempt} échouée: {e}. "
                              f"Retry dans {delay:.2f}s")
                
                self.total_retries += 1
                await asyncio.sleep(delay)
            
            except Exception as e:
                # Exception non-retryable
                logger.error(f"Retry Handler '{self.name}' exception non-retryable: {e}")
                self.failed_calls += 1
                raise e
        
        # Tous les retry épuisés
        raise RetryExhaustedError(f"Retry épuisé après {self.max_attempts} tentatives. "
                                 f"Dernière erreur: {last_exception}")
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calcule le délai avant le prochain retry"""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
            
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * attempt
            
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_multiplier ** (attempt - 1))
            
        elif self.strategy == RetryStrategy.EXPONENTIAL_JITTER:
            base_delay = self.base_delay * (self.backoff_multiplier ** (attempt - 1))
            # Ajouter du jitter pour éviter les thundering herd
            jitter = base_delay * self.jitter_range * (random.random() * 2 - 1)
            delay = base_delay + jitter
            
        else:
            delay = self.base_delay
        
        # Limiter le délai maximum
        return min(delay, self.max_delay)
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_retries = 0
        logger.info(f"Retry Handler '{self.name}' statistiques réinitialisées")
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du retry handler"""
        return {
            'name': self.name,
            'strategy': self.strategy.value,
            'max_attempts': self.max_attempts,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'total_retries': self.total_retries,
            'success_rate': self.successful_calls / max(self.total_calls, 1),
            'average_retries_per_call': self.total_retries / max(self.total_calls, 1),
            'base_delay': self.base_delay,
            'max_delay': self.max_delay
        }
    
    def __repr__(self) -> str:
        return (f"RetryHandler(name='{self.name}', strategy={self.strategy.value}, "
                f"max_attempts={self.max_attempts})")


class RetryConfig:
    """Configuration prédéfinie pour différents types d'opérations"""
    
    @staticmethod
    def network_requests() -> RetryHandler:
        """Configuration pour les requêtes réseau"""
        return RetryHandler(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_JITTER,
            backoff_multiplier=2.0,
            jitter_range=0.1,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                OSError,
            ),
            name="NetworkRetry"
        )
    
    @staticmethod
    def database_operations() -> RetryHandler:
        """Configuration pour les opérations base de données"""
        return RetryHandler(
            max_attempts=5,
            base_delay=0.5,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=1.5,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
            ),
            name="DatabaseRetry"
        )
    
    @staticmethod
    def file_operations() -> RetryHandler:
        """Configuration pour les opérations fichier"""
        return RetryHandler(
            max_attempts=3,
            base_delay=0.1,
            max_delay=5.0,
            strategy=RetryStrategy.LINEAR,
            retryable_exceptions=(
                OSError,
                IOError,
            ),
            name="FileRetry"
        )
    
    @staticmethod
    def api_calls() -> RetryHandler:
        """Configuration pour les appels API"""
        return RetryHandler(
            max_attempts=4,
            base_delay=2.0,
            max_delay=60.0,
            strategy=RetryStrategy.EXPONENTIAL_JITTER,
            backoff_multiplier=2.0,
            jitter_range=0.2,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                # Ajouter ici les exceptions HTTP spécifiques
            ),
            name="APIRetry"
        ) 