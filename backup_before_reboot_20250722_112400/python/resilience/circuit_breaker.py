"""
Circuit Breaker Pattern pour la gestion des erreurs réseau.
Implémente les trois états : CLOSED, OPEN, HALF_OPEN.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """États du Circuit Breaker"""

    CLOSED = "CLOSED"  # Fonctionnement normal
    OPEN = "OPEN"  # Circuit ouvert, rejette les requêtes
    HALF_OPEN = "HALF_OPEN"  # Test de récupération


class CircuitBreakerError(Exception):
    """Exception levée quand le circuit breaker est ouvert"""

    pass


class CircuitBreaker:
    """
    Circuit Breaker pour éviter les cascades d'erreurs.

    États :
    - CLOSED : Fonctionnement normal, surveille les erreurs
    - OPEN : Circuit ouvert, rejette immédiatement les requêtes
    - HALF_OPEN : Test de récupération, permet une requête de test
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = (Exception,),
        name: str = "CircuitBreaker",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name

        # État interne
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        self.next_attempt_time: Optional[float] = None

        # Statistiques
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.circuit_open_count = 0

        logger.info(
            f"Circuit Breaker '{name}' initialisé: "
            f"seuil={failure_threshold}, timeout={recovery_timeout}s"
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute une fonction à travers le circuit breaker.

        Args:
            func: Fonction à exécuter
            *args, **kwargs: Arguments de la fonction

        Returns:
            Résultat de la fonction

        Raises:
            CircuitBreakerError: Si le circuit est ouvert
        """
        self.total_requests += 1

        # Vérifier l'état du circuit
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit Breaker '{self.name}' passe en HALF_OPEN")
            else:
                logger.warning(
                    f"Circuit Breaker '{self.name}' est OUVERT, requête rejetée"
                )
                raise CircuitBreakerError(f"Circuit breaker '{self.name}' est ouvert")

        try:
            # Exécuter la fonction
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Succès
            self._on_success()
            return result

        except self.expected_exception as e:
            # Échec attendu
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Détermine si on doit tenter une réinitialisation"""
        if self.next_attempt_time is None:
            return True
        return time.time() >= self.next_attempt_time

    def _on_success(self):
        """Appelé lors d'un succès"""
        self.successful_requests += 1

        if self.state == CircuitState.HALF_OPEN:
            # Récupération réussie
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            self.next_attempt_time = None
            logger.info(f"Circuit Breaker '{self.name}' récupéré, retour à CLOSED")
        elif self.state == CircuitState.CLOSED:
            # Réinitialiser le compteur d'échecs en cas de succès
            self.failure_count = 0

    def _on_failure(self):
        """Appelé lors d'un échec"""
        self.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Échec pendant la récupération, retour à OPEN
            self.state = CircuitState.OPEN
            self.next_attempt_time = time.time() + self.recovery_timeout
            self.circuit_open_count += 1
            logger.warning(
                f"Circuit Breaker '{self.name}' échec en HALF_OPEN, retour à OPEN"
            )

        elif (
            self.state == CircuitState.CLOSED
            and self.failure_count >= self.failure_threshold
        ):
            # Seuil d'échec atteint, ouverture du circuit
            self.state = CircuitState.OPEN
            self.next_attempt_time = time.time() + self.recovery_timeout
            self.circuit_open_count += 1
            logger.error(
                f"Circuit Breaker '{self.name}' OUVERT après {self.failure_count} échecs"
            )

    def reset(self):
        """Réinitialise manuellement le circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        logger.info(f"Circuit Breaker '{self.name}' réinitialisé manuellement")

    def get_stats(self) -> dict:
        """Retourne les statistiques du circuit breaker"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "circuit_open_count": self.circuit_open_count,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time,
        }

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
            f"failures={self.failure_count}/{self.failure_threshold})"
        )
