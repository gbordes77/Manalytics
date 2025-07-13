#!/usr/bin/env python3
"""
Script pour lancer le pipeline complet avec visualisations intégrées
"""

import asyncio
import sys
import logging
import webbrowser
import os
import argparse
from datetime import datetime, timedelta

# Ajouter le répertoire src au path
sys.path.append('src')

from src.orchestrator import ManalyticsOrchestrator

def setup_logging():
    """Configure le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pipeline.log')
        ]
    )

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description='Pipeline complet Manalytics')
    parser.add_argument('--format', default='Standard', 
                       choices=['Standard', 'Modern', 'Legacy', 'Pioneer', 'Pauper'],
                       help='Format de tournoi à analyser')
    parser.add_argument('--start-date', default='2025-07-02',
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', default='2025-07-12',
                       help='Date de fin (YYYY-MM-DD)')
    return parser.parse_args()

async def main():
    """Lance le pipeline complet"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 DÉMARRAGE DU PIPELINE COMPLET MANALYTICS")
        
        # Parser les arguments
        args = parse_arguments()
        
        format_name = args.format
        start_date = args.start_date
        end_date = args.end_date
        
        logger.info(f"📅 Période: {start_date} à {end_date}")
        logger.info(f"🎯 Format: {format_name}")
        
        # Créer l'orchestrateur
        orchestrator = ManalyticsOrchestrator()
        
        # Lancer le pipeline complet
        result = await orchestrator.run_pipeline(format_name, start_date, end_date)
        
        logger.info("🎉 PIPELINE TERMINÉ AVEC SUCCÈS!")
        logger.info("📊 Toutes les visualisations ont été générées automatiquement")
        logger.info(f"🌐 Ouvrez {result['analysis_folder']}/index.html pour voir les résultats")
        
        # NOUVEAU: Ouvrir automatiquement le dashboard dans l'explorateur
        dashboard_path = os.path.join(result['analysis_folder'], 'index.html')
        absolute_path = os.path.abspath(dashboard_path)
        analysis_folder_path = os.path.abspath(result['analysis_folder'])
        
        logger.info(f"🚀 Ouverture automatique du dashboard: {absolute_path}")
        
        try:
            # Ouvrir dans le navigateur par défaut
            webbrowser.open(f'file://{absolute_path}')
            logger.info("✅ Dashboard ouvert dans le navigateur!")
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'ouvrir automatiquement le dashboard: {e}")
            logger.info(f"📂 Ouvrez manuellement: {absolute_path}")
        
        # BONUS: Ouvrir aussi le dossier dans l'explorateur de fichiers
        try:
            import platform
            import time
            
            # Attendre un peu pour s'assurer que tous les fichiers sont créés
            time.sleep(1)
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Forcer l'ouverture du dossier principal, pas du sous-dossier
                os.system(f'open "{analysis_folder_path}"')
                # Attendre un peu puis sélectionner le fichier index.html
                time.sleep(0.5)
                os.system(f'open -R "{absolute_path}"')
                logger.info(f"📂 Dossier d'analyse ouvert dans le Finder: {analysis_folder_path}")
            elif system == "Windows":  # Windows
                os.system(f'explorer "{analysis_folder_path}"')
                logger.info("📂 Dossier d'analyse ouvert dans l'Explorateur!")
            elif system == "Linux":  # Linux
                os.system(f'xdg-open "{analysis_folder_path}"')
                logger.info("📂 Dossier d'analyse ouvert dans l'explorateur de fichiers!")
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'ouvrir le dossier automatiquement: {e}")
            logger.info(f"📂 Ouvrez manuellement: {analysis_folder_path}")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ ERREUR PIPELINE: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n🎯 SUCCÈS! Dashboard ouvert automatiquement!")
        print(f"📂 Dossier: {result['analysis_folder']}/")
        print(f"🌐 Fichier: {result['analysis_folder']}/index.html")
    else:
        print("\n❌ ÉCHEC! Vérifiez les logs pour plus de détails")
    sys.exit(0 if result else 1) 