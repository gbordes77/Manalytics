#!/usr/bin/env python3
"""
Scraper Unifié - Lance MTGO et Melee avec les mêmes paramètres
"""

import argparse
from datetime import datetime, timedelta
import subprocess
import sys
import logging
from typing import List, Set
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Formats supportés
ALL_FORMATS = ['standard', 'modern', 'legacy', 'vintage', 'pioneer', 'pauper', 'limited', 'duel-commander', 'commander']


def run_scraper(script_name: str, args: List[str]) -> bool:
    """Execute un scraper avec les arguments donnés"""
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Lancement de {script_name}")
        logger.info(f"{'='*60}")
        
        cmd = ['python', script_name] + args
        logger.info(f"Commande: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ {script_name} terminé avec succès")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"❌ {script_name} a échoué")
            if result.stderr:
                logger.error(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Scraper unifié pour MTGO et Melee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Standard sur 21 jours
  python scrape_all.py --format standard --days 21
  
  # Multi-formats avec dates
  python scrape_all.py --format standard modern pioneer --start-date 2025-07-01 --end-date 2025-07-21
  
  # Tous les formats sur 7 jours
  python scrape_all.py --format all --days 7
  
  # Seulement MTGO ou Melee
  python scrape_all.py --format standard --days 7 --only mtgo
  python scrape_all.py --format standard --days 7 --only melee
  
  # Avec round standings pour créer la matrice de matchups
  python scrape_all.py --format standard --days 21 --get-rounds
        """
    )
    
    # Arguments de date
    parser.add_argument('--start-date', type=str,
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD). Par défaut: aujourd\'hui')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours depuis aujourd\'hui')
    
    # Arguments de format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=ALL_FORMATS + ['all'],
                       default=['standard'],
                       help='Format(s) à scraper. Par défaut: standard')
    
    # Options de plateforme
    parser.add_argument('--only', type=str, choices=['mtgo', 'melee'],
                       help='Scraper seulement une plateforme')
    
    # Options supplémentaires
    parser.add_argument('--get-decks', action='store_true',
                       help='Récupérer les détails des decks pour Melee (plus lent)')
    parser.add_argument('--get-rounds', action='store_true',
                       help='Récupérer les round standings pour la matrice de matchups (Melee)')
    parser.add_argument('--incremental', action='store_true',
                       help='Mode incrémental (futur)')
    
    args = parser.parse_args()
    
    # Validation des dates
    if args.start_date and args.days:
        parser.error("Utiliser soit --start-date/--end-date, soit --days, pas les deux")
    
    # Construction des arguments pour les scrapers individuels
    scraper_args = []
    
    # Formats
    scraper_args.extend(['--format'] + args.format)
    
    # Dates
    if args.start_date:
        scraper_args.extend(['--start-date', args.start_date])
    if args.end_date:
        scraper_args.extend(['--end-date', args.end_date])
    elif args.days:
        scraper_args.extend(['--days', str(args.days)])
    
    # Options supplémentaires
    if args.incremental:
        scraper_args.append('--incremental')
    
    # Arguments spécifiques à Melee
    melee_args = scraper_args.copy()
    if args.get_decks:
        melee_args.append('--get-decks')
    if args.get_rounds:
        melee_args.append('--get-rounds')
    
    # Afficher la configuration
    logger.info("🎯 Manalytics - Scraper Unifié")
    logger.info("=" * 60)
    
    # Parser les dates pour l'affichage
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    elif args.days:
        start_date = end_date - timedelta(days=args.days)
    else:
        start_date = end_date - timedelta(days=7)
    
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(args.format)}")
    logger.info(f"🌐 Plateformes: {args.only if args.only else 'MTGO + Melee'}")
    if args.get_decks:
        logger.info("📝 Récupération des decks Melee activée")
    if args.get_rounds:
        logger.info("🎲 Récupération des round standings Melee activée")
    
    # Lancer les scrapers
    success_count = 0
    total_count = 0
    
    if not args.only or args.only == 'mtgo':
        total_count += 1
        if run_scraper('scrape_mtgo_flexible.py', scraper_args):
            success_count += 1
        time.sleep(2)  # Pause entre les scrapers
    
    if not args.only or args.only == 'melee':
        total_count += 1
        if run_scraper('scrape_melee_flexible.py', melee_args):
            success_count += 1
    
    # Résumé final
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 RÉSUMÉ FINAL")
    logger.info(f"{'='*60}")
    logger.info(f"✅ {success_count}/{total_count} scrapers ont réussi")
    
    if success_count == total_count:
        logger.info("🎉 Tous les scrapers ont terminé avec succès!")
        logger.info("\n💡 Prochaine étape: python scripts/process_all_standard_data.py")
    else:
        logger.warning("⚠️ Certains scrapers ont échoué. Vérifiez les logs ci-dessus.")
        sys.exit(1)


if __name__ == "__main__":
    main()