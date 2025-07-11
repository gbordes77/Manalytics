#!/usr/bin/env python3

import asyncio
import subprocess
import yaml
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import structlog

# Configuration du logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class ManalyticsOrchestrator:
    """Orchestrateur principal du pipeline Manalytics"""
    
    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.setup_logging()
        
    def setup_logging(self):
        """Configurer le système de logging"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_format = self.config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Créer le dossier de logs
        os.makedirs('logs', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"logs/manalytics_{timestamp}.log"
        
        logger.info("Logging configured", log_file=log_file, level=log_level)
        
    async def run_pipeline(self, format_name: str, start_date: str, end_date: str, skip_scraping: bool = False, skip_classification: bool = False):
        """Exécuter le pipeline complet"""
        
        logger.info("Starting Manalytics pipeline", 
                   format=format_name, 
                   start_date=start_date, 
                   end_date=end_date,
                   skip_scraping=skip_scraping,
                   skip_classification=skip_classification)
        
        try:
            # Phase 1: Scraping (si non skippé)
            if not skip_scraping:
                logger.info("Phase 1: Starting scraping phase")
                await self.run_scrapers(format_name, start_date, end_date)
                logger.info("Phase 1: Scraping completed")
            else:
                logger.info("Phase 1: Scraping skipped")
            
            # Phase 2: Classification (si non skippé)
            if not skip_classification:
                logger.info("Phase 2: Starting classification phase")
                await self.run_classifier(format_name)
                logger.info("Phase 2: Classification completed")
            else:
                logger.info("Phase 2: Classification skipped")
            
            # Phase 3: Analysis R
            logger.info("Phase 3: Starting R analysis phase")
            await self.run_r_analysis(format_name)
            logger.info("Phase 3: R analysis completed")
            
            logger.info("Pipeline completed successfully")
            
        except Exception as e:
            logger.error("Pipeline failed", error=str(e))
            raise
            
    async def run_scrapers(self, format_name: str, start_date: str, end_date: str):
        """Exécuter la phase de scraping"""
        
        # Import dynamique pour éviter les erreurs si les modules ne sont pas prêts
        try:
            from src.python.scraper import MeleeScraper, MTGOScraper, TopdeckScraper
        except ImportError as e:
            logger.error("Failed to import scrapers", error=str(e))
            raise
        
        scrapers = {}
        enabled_sources = self.config.get('enabled_sources', [])
        
        # Initialiser les scrapers activés
        if 'melee' in enabled_sources:
            scrapers['melee'] = MeleeScraper(
                self.config['cache_folder'], 
                self.config['apis']['melee']
            )
            
        if 'mtgo' in enabled_sources:
            scrapers['mtgo'] = MTGOScraper(
                self.config['cache_folder'], 
                self.config['apis']['mtgo']
            )
            
        if 'topdeck' in enabled_sources:
            scrapers['topdeck'] = TopdeckScraper(
                self.config['cache_folder'], 
                self.config['apis']['topdeck']
            )
        
        if not scrapers:
            logger.warning("No scrapers enabled")
            return
        
        # Exécuter les scrapers en parallèle
        tasks = []
        for source, scraper in scrapers.items():
            logger.info("Starting scraper", source=source)
            async with scraper:
                task = scraper.fetch_date_range(format_name, start_date, end_date)
                tasks.append(task)
        
        # Attendre que tous les scrapers terminent
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyser les résultats
        total_tournaments = 0
        for i, result in enumerate(results):
            source = list(scrapers.keys())[i]
            if isinstance(result, Exception):
                logger.error("Scraper failed", source=source, error=str(result))
            else:
                tournament_count = len(result) if result else 0
                total_tournaments += tournament_count
                logger.info("Scraper completed", source=source, tournaments=tournament_count)
        
        logger.info("All scrapers completed", total_tournaments=total_tournaments)
        
    async def run_classifier(self, format_name: str):
        """Exécuter la phase de classification"""
        
        input_dir = f"{self.config['cache_folder']}/raw"
        output_dir = f"{self.config['cache_folder']}/processed"
        rules_path = self.config['format_data_path']
        
        if not os.path.exists(input_dir):
            logger.warning("No raw data found for classification")
            return
            
        cmd = [
            sys.executable, 'src/python/classifier/run_classifier.py',
            '--input', input_dir,
            '--output', output_dir,
            '--format', format_name,
            '--rules', rules_path,
            '--concurrency', str(self.config.get('classification', {}).get('concurrency', 10))
        ]
        
        logger.info("Running classifier", command=' '.join(cmd))
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error("Classifier failed", 
                        returncode=process.returncode,
                        stdout=stdout.decode(),
                        stderr=stderr.decode())
            raise RuntimeError(f"Classifier failed with return code {process.returncode}")
        else:
            logger.info("Classifier completed successfully")
            
    async def run_r_analysis(self, format_name: str):
        """Exécuter la phase d'analyse R"""
        
        input_dir = f"{self.config['cache_folder']}/processed"
        output_dir = f"{self.config['cache_folder']}/output"
        
        # Créer le nom de fichier de sortie avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{output_dir}/metagame_{format_name}_{timestamp}.json"
        
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Paramètres d'analyse
        min_matches = self.config.get('analysis', {}).get('min_matches_for_matchup', 10)
        min_decks = self.config.get('analysis', {}).get('min_decks_for_archetype', 5)
        
        cmd = [
            'Rscript', 'src/r/analysis/metagame_analysis.R',
            input_dir,
            output_file,
            str(min_matches),
            str(min_decks)
        ]
        
        logger.info("Running R analysis", command=' '.join(cmd))
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error("R analysis failed", 
                        returncode=process.returncode,
                        stdout=stdout.decode(),
                        stderr=stderr.decode())
            raise RuntimeError(f"R analysis failed with return code {process.returncode}")
        else:
            logger.info("R analysis completed successfully", output_file=output_file)
            
            # Créer un lien symbolique vers le fichier le plus récent
            latest_link = f"{output_dir}/metagame_{format_name}_latest.json"
            if os.path.exists(latest_link):
                os.remove(latest_link)
            os.symlink(os.path.basename(output_file), latest_link)
            
            logger.info("Latest metagame file linked", latest_file=latest_link)

def validate_date_format(date_string: str) -> bool:
    """Valider le format de date YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

async def main():
    parser = argparse.ArgumentParser(description='Manalytics - Pipeline d\'analyse de métagame MTG')
    parser.add_argument('--format', required=True, 
                       help='Format Magic (Modern, Legacy, Standard, Pioneer, etc.)')
    parser.add_argument('--start-date', 
                       default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', 
                       default=datetime.now().strftime('%Y-%m-%d'),
                       help='Date de fin (YYYY-MM-DD)')
    parser.add_argument('--config', default='config.yaml',
                       help='Fichier de configuration')
    parser.add_argument('--skip-scraping', action='store_true',
                       help='Ignorer la phase de scraping')
    parser.add_argument('--skip-classification', action='store_true',
                       help='Ignorer la phase de classification')
    
    args = parser.parse_args()
    
    # Validation des dates
    if not validate_date_format(args.start_date):
        print(f"Erreur: Format de date invalide pour start-date: {args.start_date}")
        sys.exit(1)
        
    if not validate_date_format(args.end_date):
        print(f"Erreur: Format de date invalide pour end-date: {args.end_date}")
        sys.exit(1)
        
    # Vérifier que start_date <= end_date
    start = datetime.strptime(args.start_date, '%Y-%m-%d')
    end = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    if start > end:
        print("Erreur: La date de début doit être antérieure ou égale à la date de fin")
        sys.exit(1)
    
    # Vérifier que le fichier de config existe
    if not os.path.exists(args.config):
        print(f"Erreur: Fichier de configuration non trouvé: {args.config}")
        sys.exit(1)
    
    try:
        orchestrator = ManalyticsOrchestrator(args.config)
        await orchestrator.run_pipeline(
            args.format, 
            args.start_date, 
            args.end_date,
            args.skip_scraping,
            args.skip_classification
        )
        print("Pipeline terminé avec succès!")
        
    except Exception as e:
        logger.error("Pipeline execution failed", error=str(e))
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 