#!/usr/bin/env python3
"""
Test complet du rapport avec données réelles
"""

import asyncio
import os
import sys

sys.path.append("src")

from orchestrator import ManalyticsOrchestrator


async def test_complete_report():
    """Test complet avec données réelles"""

    print("🚀 TEST RAPPORT COMPLET AVEC DONNÉES RÉELLES")
    print("=" * 60)

    try:
        # Créer l'orchestrator
        orchestrator = ManalyticsOrchestrator()

        # Période avec données
        format_name = "Standard"
        start_date = "2025-07-01"
        end_date = "2025-07-15"

        print(f"📅 Période: {start_date} à {end_date}")
        print(f"🎯 Format: {format_name}")

        # Lancer le pipeline complet
        print("\n🔄 Lancement du pipeline complet...")
        await orchestrator.run_pipeline(format_name, start_date, end_date)

        print("\n✅ PIPELINE TERMINÉ")

        # Vérifier les fichiers générés
        analysis_folder = (
            f"Analyses/{format_name.lower()}_analysis_{start_date}_{end_date}"
        )

        print(f"\n📁 Vérification des fichiers dans {analysis_folder}:")

        # Page principale
        main_file = (
            f"{analysis_folder}/{format_name.lower()}_{start_date}_{end_date}.html"
        )
        if os.path.exists(main_file):
            print("✅ Page principale générée")
            print(f"📂 Chemin: {os.path.abspath(main_file)}")
        else:
            print("❌ Page principale manquante")

        # Page Leagues
        leagues_dir = f"{analysis_folder}/leagues_analysis"
        if os.path.exists(leagues_dir):
            print("✅ Dossier Leagues Analysis créé")

            leagues_file = f"{leagues_dir}/{format_name.lower()}_{start_date}_{end_date}_leagues.html"
            if os.path.exists(leagues_file):
                print("✅ Page Leagues Analysis générée")
                print(f"📂 Chemin: {os.path.abspath(leagues_file)}")

        print(f"\n🎉 RAPPORT COMPLET GÉNÉRÉ")
        return os.path.abspath(main_file) if os.path.exists(main_file) else None

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_complete_report())
    if result:
        print(f"\n🌐 RAPPORT PRÊT: {result}")
    else:
        print("\n❌ Échec de génération du rapport")
