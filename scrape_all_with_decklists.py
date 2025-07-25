#!/usr/bin/env python3
"""
Script complet pour scraper MTGO et Melee avec toutes les decklists
"""
import subprocess
import sys
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scraper(script_name, description):
    """Exécute un scraper et capture la sortie"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 {description}")
    logger.info(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Afficher la sortie
        if result.stdout:
            print(result.stdout)
        
        logger.info(f"✅ {description} - Terminé avec succès")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de {description}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    logger.info("🎯 SCRAPING COMPLET MTGO + MELEE AVEC DECKLISTS")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_count = 2
    
    # 1. Scraper MTGO avec decklists
    if run_scraper("scrape_mtgo_with_decklists.py", "Scraping MTGO Standard avec decklists"):
        success_count += 1
    
    # 2. Scraper Melee avec decklists
    if run_scraper("parse_melee_records.py", "Scraping Melee Standard avec decklists"):
        success_count += 1
    
    # Résumé final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RÉSUMÉ FINAL")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Scrapers réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        logger.info("🎉 Tous les scrapers ont réussi!")
        logger.info("\n📁 Fichiers créés dans:")
        logger.info("  - data/raw/mtgo/standard/ (avec sous-dossier challenge/)")
        logger.info("  - data/raw/melee/standard_complete/")
    else:
        logger.warning("⚠️ Certains scrapers ont échoué. Vérifiez les logs ci-dessus.")
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)