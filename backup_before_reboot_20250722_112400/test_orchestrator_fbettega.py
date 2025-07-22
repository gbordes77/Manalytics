#!/usr/bin/env python3
"""
Test de l'intégration fbettega avec l'orchestrator
"""

import asyncio
import os
import sys

sys.path.append("src")

from orchestrator import ManalyticsOrchestrator


async def test_orchestrator_with_fbettega():
    """Test l'orchestrator avec fbettega amélioré"""

    print("🚀 TEST ORCHESTRATOR AVEC FBETTEGA AMÉLIORÉ")
    print("=" * 60)

    # Configuration pour test rapide
    config = {
        "format": "Standard",
        "start_date": "2025-07-10",
        "end_date": "2025-07-15",
        "output_dir": "test_output_fbettega",
    }

    try:
        # Créer l'orchestrator
        orchestrator = ManalyticsOrchestrator()

        # Configurer les paramètres
        orchestrator.format = config["format"]
        orchestrator.start_date = config["start_date"]
        orchestrator.end_date = config["end_date"]
        orchestrator.output_dir = config["output_dir"]

        print(f"📅 Période: {config['start_date']} à {config['end_date']}")
        print(f"🎯 Format: {config['format']}")

        # Lancer l'analyse complète
        print("\n🔄 Lancement de l'analyse complète...")
        await orchestrator.run_pipeline(
            config["format"], config["start_date"], config["end_date"]
        )

        print("\n✅ ANALYSE TERMINÉE")
        print("Vérifiez le dossier test_output_fbettega pour les résultats")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_orchestrator_with_fbettega())
