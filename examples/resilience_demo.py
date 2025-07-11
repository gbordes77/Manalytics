#!/usr/bin/env python3
"""
Démonstration du système de résilience Manalytics.
Montre l'utilisation du Circuit Breaker, Retry Handler et Error Monitor.
"""

import asyncio
import random
import time
import sys
import os

# Ajouter le chemin vers le module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

from resilience import CircuitBreaker, RetryHandler, ErrorMonitor
from resilience.decorators import resilient
from resilience.retry_handler import RetryStrategy


class DemoNetworkService:
    """Service de démonstration simulant des appels réseau instables"""
    
    def __init__(self, failure_rate: float = 0.3):
        self.failure_rate = failure_rate
        self.call_count = 0
        
    async def unstable_call(self, operation: str = "test") -> str:
        """Simule un appel réseau instable"""
        self.call_count += 1
        
        # Simuler un délai réseau
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Échouer selon le taux configuré
        if random.random() < self.failure_rate:
            raise ConnectionError(f"Network error on {operation} (call #{self.call_count})")
        
        return f"Success: {operation} completed (call #{self.call_count})"


async def demo_circuit_breaker():
    """Démonstration du Circuit Breaker"""
    print("\n🔧 === DÉMONSTRATION CIRCUIT BREAKER ===")
    
    service = DemoNetworkService(failure_rate=0.7)  # 70% d'échec
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2,
        name="DemoCircuitBreaker"
    )
    
    print(f"Configuration: seuil={cb.failure_threshold}, timeout={cb.recovery_timeout}s")
    
    # Phase 1: Déclencher l'ouverture du circuit
    print("\n📈 Phase 1: Accumulation d'échecs...")
    for i in range(5):
        try:
            result = await cb.call(service.unstable_call, f"operation_{i}")
            print(f"  ✅ {result}")
        except Exception as e:
            print(f"  ❌ Échec {i+1}: {e}")
            
        stats = cb.get_stats()
        print(f"  📊 État: {stats['state']}, Échecs: {stats['failure_count']}/{stats['failure_threshold']}")
        
        await asyncio.sleep(0.5)
    
    # Phase 2: Circuit ouvert
    print("\n🚫 Phase 2: Circuit ouvert...")
    try:
        await cb.call(service.unstable_call, "blocked_operation")
    except Exception as e:
        print(f"  ❌ Requête bloquée: {e}")
    
    # Phase 3: Récupération
    print(f"\n⏳ Phase 3: Attente de récupération ({cb.recovery_timeout}s)...")
    await asyncio.sleep(cb.recovery_timeout + 0.5)
    
    # Utiliser un service plus stable pour la récupération
    stable_service = DemoNetworkService(failure_rate=0.1)
    try:
        result = await cb.call(stable_service.unstable_call, "recovery_test")
        print(f"  ✅ Récupération réussie: {result}")
    except Exception as e:
        print(f"  ❌ Récupération échouée: {e}")
    
    print(f"\n📊 Statistiques finales:")
    stats = cb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def demo_retry_handler():
    """Démonstration du Retry Handler"""
    print("\n🔄 === DÉMONSTRATION RETRY HANDLER ===")
    
    service = DemoNetworkService(failure_rate=0.6)  # 60% d'échec
    rh = RetryHandler(
        max_attempts=4,
        base_delay=0.5,
        strategy=RetryStrategy.EXPONENTIAL_JITTER,
        name="DemoRetryHandler"
    )
    
    print(f"Configuration: max_attempts={rh.max_attempts}, stratégie={rh.strategy.value}")
    
    # Test avec succès après retry
    print("\n📈 Test avec succès après retry...")
    try:
        result = await rh.call(service.unstable_call, "retry_test")
        print(f"  ✅ Succès: {result}")
    except Exception as e:
        print(f"  ❌ Échec final: {e}")
    
    # Test avec échec complet
    print("\n📈 Test avec service très instable...")
    unstable_service = DemoNetworkService(failure_rate=0.9)
    try:
        result = await rh.call(unstable_service.unstable_call, "failing_test")
        print(f"  ✅ Succès inattendu: {result}")
    except Exception as e:
        print(f"  ❌ Échec après tous les retry: {e}")
    
    print(f"\n📊 Statistiques finales:")
    stats = rh.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def demo_error_monitor():
    """Démonstration de l'Error Monitor"""
    print("\n📊 === DÉMONSTRATION ERROR MONITOR ===")
    
    em = ErrorMonitor(
        error_rate_threshold=2.0,  # 2 erreurs par minute
        burst_threshold=3,
        name="DemoErrorMonitor"
    )
    
    # Callback d'alerte
    alerts = []
    def alert_callback(alert_data):
        alerts.append(alert_data)
        print(f"  🚨 ALERTE: {alert_data['alert_type']} - {alert_data['message']}")
    
    em.add_alert_callback(alert_callback)
    
    print("Configuration: seuil=2 erreurs/min, burst=3 erreurs")
    
    # Simuler des erreurs
    print("\n📈 Simulation d'erreurs...")
    service = DemoNetworkService(failure_rate=0.8)
    
    for i in range(6):
        try:
            await service.unstable_call(f"monitored_op_{i}")
        except Exception as e:
            em.record_error(e, "demo_service", context={'operation_id': i})
            print(f"  ❌ Erreur {i+1} enregistrée: {type(e).__name__}")
        
        await asyncio.sleep(0.2)
    
    # Afficher les statistiques
    print(f"\n📊 Statistiques d'erreurs:")
    stats = em.get_component_stats("demo_service")
    if stats:
        print(f"  Erreurs totales: {stats.total_errors}")
        print(f"  Taux d'erreur: {stats.error_rate:.2f} erreurs/min")
        print(f"  Erreur la plus fréquente: {stats.most_common_error}")
    
    print(f"\n🚨 Alertes déclenchées: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['alert_type']}: {alert['message']}")


@resilient(
    failure_threshold=2,
    max_attempts=3,
    retry_strategy="exponential_jitter",
    component="demo_api"
)
async def demo_resilient_function():
    """Fonction de démonstration avec résilience intégrée"""
    service = DemoNetworkService(failure_rate=0.5)
    return await service.unstable_call("resilient_operation")


async def demo_resilient_decorator():
    """Démonstration du décorateur resilient"""
    print("\n🛡️ === DÉMONSTRATION DÉCORATEUR RESILIENT ===")
    
    print("Test d'une fonction avec résilience intégrée...")
    
    try:
        result = await demo_resilient_function()
        print(f"  ✅ Succès: {result}")
    except Exception as e:
        print(f"  ❌ Échec final: {e}")
    
    # Accéder aux statistiques
    if hasattr(demo_resilient_function, '_resilience_stats'):
        print(f"\n📊 Statistiques de résilience:")
        stats = demo_resilient_function._resilience_stats()
        
        cb_stats = stats.get('circuit_breaker', {})
        print(f"  Circuit Breaker: {cb_stats.get('state', 'N/A')} ({cb_stats.get('total_requests', 0)} requêtes)")
        
        retry_stats = stats.get('retry_handler', {})
        print(f"  Retry Handler: {retry_stats.get('success_rate', 0):.2f} taux de succès")
        
        error_stats = stats.get('error_monitor', {})
        if error_stats:
            print(f"  Error Monitor: {error_stats.get('total_events', 0)} événements")


async def demo_integration():
    """Démonstration d'intégration complète"""
    print("\n🔗 === DÉMONSTRATION INTÉGRATION COMPLÈTE ===")
    
    # Créer un service très instable
    service = DemoNetworkService(failure_rate=0.8)
    
    # Créer les composants de résilience
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1, name="IntegrationCB")
    rh = RetryHandler(max_attempts=3, base_delay=0.2, name="IntegrationRetry")
    em = ErrorMonitor(error_rate_threshold=1.0, name="IntegrationMonitor")
    
    # Callback d'alerte
    def alert_callback(alert_data):
        print(f"    🚨 {alert_data['alert_type']}: {alert_data['message']}")
    
    em.add_alert_callback(alert_callback)
    
    print("Test d'intégration avec tous les composants...")
    
    for i in range(5):
        try:
            # Appliquer circuit breaker, retry et monitoring
            async def resilient_call():
                return await cb.call(service.unstable_call, f"integration_test_{i}")
            
            result = await rh.call(resilient_call)
            print(f"  ✅ Test {i+1}: {result}")
            
        except Exception as e:
            em.record_error(e, "integration_test")
            print(f"  ❌ Test {i+1}: {e}")
        
        await asyncio.sleep(0.3)
    
    # Résumé final
    print(f"\n📊 Résumé d'intégration:")
    print(f"  Circuit Breaker: {cb.get_stats()['state']} ({cb.get_stats()['total_requests']} requêtes)")
    print(f"  Retry Handler: {rh.get_stats()['success_rate']:.2f} taux de succès")
    print(f"  Error Monitor: {em.get_error_summary()['total_events']} événements")


async def main():
    """Fonction principale de démonstration"""
    print("🎯 === DÉMONSTRATION SYSTÈME DE RÉSILIENCE MANALYTICS ===")
    print("Ce script démontre les capacités du système de résilience intégré.")
    
    try:
        await demo_circuit_breaker()
        await demo_retry_handler()
        await demo_error_monitor()
        await demo_resilient_decorator()
        await demo_integration()
        
        print("\n🎉 === DÉMONSTRATION TERMINÉE ===")
        print("Le système de résilience est opérationnel et prêt pour la production !")
        
    except Exception as e:
        print(f"\n❌ Erreur dans la démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 