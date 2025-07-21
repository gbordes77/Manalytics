#!/usr/bin/env python3
"""
Test script pour le MTGO Listener
Vérifie que le listener peut démarrer et simuler des données de matchup
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.python.cache.mtgo_cache_manager import MTGOCacheManager
from src.python.scraper.mtgo_listener import MTGOListener, MTGOListenerManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_mtgo_listener():
    """Test du MTGO Listener"""
    print("🧪 Testing MTGO Listener...")

    try:
        # Créer le cache manager
        cache_manager = MTGOCacheManager()

        # Créer le listener
        listener = MTGOListener(cache_manager)

        # Tester la détection de processus MTGO
        print("\n🔍 Testing MTGO process detection...")
        mtgo_process = listener.find_mtgo_process()
        if mtgo_process:
            print(f"✅ MTGO process found: PID {mtgo_process.info['pid']}")
        else:
            print("⚠️ MTGO process not found (expected in test environment)")

        # Tester la détection de fenêtre MTGO
        print("\n🪟 Testing MTGO window detection...")
        window_info = listener.get_mtgo_window_info()
        if window_info:
            print(f"✅ MTGO window found: {window_info}")
        else:
            print("⚠️ MTGO window not found (expected in test environment)")

        # Tester la simulation de données de matchup
        print("\n📊 Testing matchup data simulation...")
        matchup_data = listener.simulate_matchup_data()
        print(
            f"✅ Simulated matchup: {matchup_data['player1']['deck']['name']} vs {matchup_data['player2']['deck']['name']}"
        )

        # Tester le gestionnaire du listener
        print("\n🎧 Testing MTGO Listener Manager...")
        manager = MTGOListenerManager(cache_manager)

        # Démarrer le listener
        print("🚀 Starting listener...")
        await manager.start_listener()

        # Attendre quelques secondes pour voir les données simulées
        print("⏳ Waiting for simulated matchups...")
        await asyncio.sleep(10)

        # Vérifier le statut
        status = manager.get_status()
        print(f"📈 Listener status: {status}")

        # Arrêter le listener
        print("🛑 Stopping listener...")
        await manager.stop_listener()

        print("\n✅ MTGO Listener test completed successfully!")

    except Exception as e:
        print(f"❌ Error during MTGO Listener test: {e}")
        import traceback

        traceback.print_exc()


async def test_orchestrator_integration():
    """Test de l'intégration avec l'orchestrateur"""
    print("\n🔧 Testing Orchestrator Integration...")

    try:
        from src.orchestrator import ManalyticsOrchestrator

        # Créer l'orchestrateur
        orchestrator = ManalyticsOrchestrator()

        # Vérifier que le listener est initialisé
        print("📋 Checking listener initialization...")
        status = orchestrator.get_mtgo_listener_status()
        print(f"📊 Initial status: {status}")

        # Démarrer le listener via l'orchestrateur
        print("🎧 Starting listener via orchestrator...")
        await orchestrator._start_mtgo_listener()

        # Attendre quelques secondes
        await asyncio.sleep(5)

        # Vérifier le statut
        status = orchestrator.get_mtgo_listener_status()
        print(f"📈 Status after start: {status}")

        # Arrêter le listener
        print("🛑 Stopping listener via orchestrator...")
        await orchestrator._stop_mtgo_listener()

        print("\n✅ Orchestrator integration test completed successfully!")

    except Exception as e:
        print(f"❌ Error during orchestrator integration test: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Fonction principale de test"""
    print("🚀 MTGO Listener Test Suite")
    print("=" * 50)

    # Test du listener seul
    await test_mtgo_listener()

    # Test de l'intégration avec l'orchestrateur
    await test_orchestrator_integration()

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
