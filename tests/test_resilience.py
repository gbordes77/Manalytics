"""
Tests pour le module de résilience (Circuit Breaker, Retry, Error Monitor).
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Ajouter le chemin vers le module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

from resilience.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError
from resilience.retry_handler import RetryHandler, RetryStrategy, RetryExhaustedError
from resilience.error_monitor import ErrorMonitor, ErrorEvent
from resilience.decorators import with_circuit_breaker, with_retry, resilient


class TestCircuitBreaker:
    """Tests pour le Circuit Breaker"""
    
    def test_circuit_breaker_init(self):
        """Test de l'initialisation du circuit breaker"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30, name="test_cb")
        
        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 30
        assert cb.name == "test_cb"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_success(self):
        """Test du circuit breaker avec succès"""
        cb = CircuitBreaker(failure_threshold=3, name="test_success")
        
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.successful_requests == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_threshold(self):
        """Test de l'ouverture du circuit après le seuil d'échec"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1, name="test_failure")
        
        async def failing_func():
            raise ConnectionError("Network error")
        
        # Premier échec
        with pytest.raises(ConnectionError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 1
        
        # Deuxième échec - circuit s'ouvre
        with pytest.raises(ConnectionError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 2
        
        # Troisième tentative - circuit ouvert
        with pytest.raises(CircuitBreakerError):
            await cb.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test de la récupération du circuit breaker"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1, name="test_recovery")
        
        async def failing_func():
            raise ConnectionError("Network error")
        
        async def success_func():
            return "recovered"
        
        # Déclencher l'ouverture du circuit
        with pytest.raises(ConnectionError):
            await cb.call(failing_func)
        assert cb.state == CircuitState.OPEN
        
        # Attendre le timeout de récupération
        await asyncio.sleep(0.2)
        
        # Tentative de récupération - circuit passe en HALF_OPEN puis CLOSED
        result = await cb.call(success_func)
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_stats(self):
        """Test des statistiques du circuit breaker"""
        cb = CircuitBreaker(failure_threshold=3, name="test_stats")
        
        stats = cb.get_stats()
        assert stats['name'] == "test_stats"
        assert stats['state'] == CircuitState.CLOSED.value
        assert stats['failure_count'] == 0
        assert stats['total_requests'] == 0
        assert stats['success_rate'] == 0.0


class TestRetryHandler:
    """Tests pour le Retry Handler"""
    
    def test_retry_handler_init(self):
        """Test de l'initialisation du retry handler"""
        rh = RetryHandler(max_attempts=3, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL)
        
        assert rh.max_attempts == 3
        assert rh.base_delay == 1.0
        assert rh.strategy == RetryStrategy.EXPONENTIAL
    
    @pytest.mark.asyncio
    async def test_retry_handler_success_first_attempt(self):
        """Test du retry handler avec succès au premier essai"""
        rh = RetryHandler(max_attempts=3, name="test_success")
        
        async def success_func():
            return "success"
        
        result = await rh.call(success_func)
        assert result == "success"
        assert rh.successful_calls == 1
        assert rh.total_retries == 0
    
    @pytest.mark.asyncio
    async def test_retry_handler_success_after_retries(self):
        """Test du retry handler avec succès après retry"""
        rh = RetryHandler(max_attempts=3, base_delay=0.01, name="test_retry_success")
        
        call_count = 0
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary error")
            return "success"
        
        result = await rh.call(flaky_func)
        assert result == "success"
        assert call_count == 3
        assert rh.successful_calls == 1
        assert rh.total_retries == 2
    
    @pytest.mark.asyncio
    async def test_retry_handler_exhausted(self):
        """Test du retry handler avec épuisement des tentatives"""
        rh = RetryHandler(max_attempts=2, base_delay=0.01, name="test_exhausted")
        
        async def failing_func():
            raise ConnectionError("Persistent error")
        
        with pytest.raises(RetryExhaustedError):
            await rh.call(failing_func)
        
        assert rh.failed_calls == 1
        assert rh.total_retries == 1
    
    def test_retry_delay_calculation(self):
        """Test du calcul des délais de retry"""
        rh = RetryHandler(base_delay=1.0, backoff_multiplier=2.0, max_delay=10.0)
        
        # Test stratégie linéaire
        rh.strategy = RetryStrategy.LINEAR
        assert rh._calculate_delay(1) == 1.0
        assert rh._calculate_delay(2) == 2.0
        assert rh._calculate_delay(3) == 3.0
        
        # Test stratégie exponentielle
        rh.strategy = RetryStrategy.EXPONENTIAL
        assert rh._calculate_delay(1) == 1.0
        assert rh._calculate_delay(2) == 2.0
        assert rh._calculate_delay(3) == 4.0
        
        # Test limitation du délai maximum
        rh.strategy = RetryStrategy.EXPONENTIAL
        assert rh._calculate_delay(10) == 10.0  # Limité par max_delay
    
    def test_retry_stats(self):
        """Test des statistiques du retry handler"""
        rh = RetryHandler(max_attempts=3, name="test_stats")
        
        stats = rh.get_stats()
        assert stats['name'] == "test_stats"
        assert stats['max_attempts'] == 3
        assert stats['total_calls'] == 0
        assert stats['success_rate'] == 0.0


class TestErrorMonitor:
    """Tests pour l'Error Monitor"""
    
    def test_error_monitor_init(self):
        """Test de l'initialisation de l'error monitor"""
        em = ErrorMonitor(max_events_per_component=100, name="test_monitor")
        
        assert em.max_events_per_component == 100
        assert em.name == "test_monitor"
        assert em.total_events == 0
    
    def test_record_error(self):
        """Test de l'enregistrement d'erreurs"""
        em = ErrorMonitor(name="test_record")
        
        error = ConnectionError("Network error")
        em.record_error(error, "test_component", "ERROR")
        
        assert em.total_events == 1
        assert "test_component" in em.components_stats
        
        stats = em.get_component_stats("test_component")
        assert stats.component == "test_component"
        assert stats.total_errors == 1
        assert stats.most_common_error == "ConnectionError"
    
    def test_record_custom_error(self):
        """Test de l'enregistrement d'erreurs personnalisées"""
        em = ErrorMonitor(name="test_custom")
        
        em.record_custom_error("CustomError", "Custom message", "test_component", "WARNING")
        
        assert em.total_events == 1
        stats = em.get_component_stats("test_component")
        assert stats.error_types["CustomError"] == 1
    
    def test_error_rate_calculation(self):
        """Test du calcul du taux d'erreur"""
        em = ErrorMonitor(time_window_minutes=1, name="test_rate")
        
        # Ajouter plusieurs erreurs
        for i in range(5):
            em.record_custom_error("TestError", f"Error {i}", "test_component")
        
        stats = em.get_component_stats("test_component")
        assert stats.error_rate == 5.0  # 5 erreurs par minute
    
    def test_alert_callback(self):
        """Test des callbacks d'alerte"""
        em = ErrorMonitor(error_rate_threshold=0.5, time_window_minutes=1, name="test_alert")
        
        alerts_received = []
        def alert_callback(alert_data):
            alerts_received.append(alert_data)
        
        em.add_alert_callback(alert_callback)
        
        # Déclencher une alerte en dépassant le seuil
        for i in range(5):  # 5 erreurs > 0.5 erreur/min
            em.record_custom_error("TestError", f"Error {i}", "test_component")
        
        # Vérifier qu'une alerte a été déclenchée
        assert len(alerts_received) > 0
        assert alerts_received[0]['alert_type'] == "HIGH_ERROR_RATE"
        assert alerts_received[0]['component'] == "test_component"
    
    def test_get_error_summary(self):
        """Test du résumé des erreurs"""
        em = ErrorMonitor(name="test_summary")
        
        em.record_custom_error("Error1", "Message 1", "component1")
        em.record_custom_error("Error2", "Message 2", "component2")
        
        summary = em.get_error_summary()
        assert summary['monitor_name'] == "test_summary"
        assert summary['total_events'] == 2
        assert summary['total_components'] == 2
        assert "component1" in summary['components']
        assert "component2" in summary['components']
    
    def test_export_errors(self):
        """Test de l'export des erreurs"""
        em = ErrorMonitor(name="test_export")
        
        em.record_custom_error("TestError", "Test message", "test_component")
        
        export_data = em.export_errors(component="test_component", format="json")
        assert "TestError" in export_data
        assert "test_component" in export_data
        assert "Test message" in export_data


class TestDecorators:
    """Tests pour les décorateurs de résilience"""
    
    @pytest.mark.asyncio
    async def test_with_circuit_breaker_decorator(self):
        """Test du décorateur circuit breaker"""
        
        @with_circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
        async def test_func():
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert hasattr(test_func, '_circuit_breaker')
        
        cb = test_func._circuit_breaker
        assert cb.successful_requests == 1
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator(self):
        """Test du décorateur retry"""
        
        call_count = 0
        
        @with_retry(max_attempts=3, base_delay=0.01)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary error")
            return "success"
        
        result = await flaky_func()
        assert result == "success"
        assert call_count == 2
        assert hasattr(flaky_func, '_retry_handler')
        
        rh = flaky_func._retry_handler
        assert rh.successful_calls == 1
        assert rh.total_retries == 1
    
    @pytest.mark.asyncio
    async def test_resilient_decorator(self):
        """Test du décorateur resilient combiné"""
        
        @resilient(
            failure_threshold=3,
            max_attempts=2,
            retry_strategy="exponential",
            component="test_component"
        )
        async def test_func():
            return "success"
        
        result = await test_func()
        assert result == "success"
        
        # Vérifier que tous les composants sont présents
        assert hasattr(test_func, '_circuit_breaker')
        assert hasattr(test_func, '_retry_handler')
        assert hasattr(test_func, '_error_monitor')
        assert hasattr(test_func, '_resilience_stats')
        
        # Vérifier les statistiques
        stats = test_func._resilience_stats()
        assert 'circuit_breaker' in stats
        assert 'retry_handler' in stats
        assert 'error_monitor' in stats


class TestIntegration:
    """Tests d'intégration des composants de résilience"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_retry(self):
        """Test de l'intégration circuit breaker + retry"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, name="integration_cb")
        rh = RetryHandler(max_attempts=3, base_delay=0.01, name="integration_retry")
        
        call_count = 0
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise ConnectionError("Network error")
            return "success"
        
        # Premier appel - retry puis circuit breaker s'ouvre
        async def retry_with_cb():
            return await cb.call(flaky_func)
        
        with pytest.raises(RetryExhaustedError):
            await rh.call(retry_with_cb)
        
        assert cb.state == CircuitState.OPEN
        assert rh.failed_calls == 1
    
    @pytest.mark.asyncio
    async def test_full_resilience_stack(self):
        """Test de la pile complète de résilience"""
        em = ErrorMonitor(name="integration_monitor")
        
        # Simuler une fonction qui échoue puis réussit
        call_count = 0
        async def recovering_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error = ConnectionError(f"Attempt {call_count} failed")
                em.record_error(error, "integration_test")
                raise error
            return "recovered"
        
        # Utiliser le décorateur resilient
        @resilient(
            failure_threshold=5,
            max_attempts=4,
            retry_strategy="exponential",
            component="integration_test"
        )
        async def test_func():
            return await recovering_func()
        
        result = await test_func()
        assert result == "recovered"
        assert call_count == 3
        
        # Vérifier que les erreurs ont été enregistrées
        stats = em.get_component_stats("integration_test")
        assert stats.total_errors == 2  # 2 échecs avant le succès


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 