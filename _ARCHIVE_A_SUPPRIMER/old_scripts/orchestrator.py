#!/usr/bin/env python3
"""
Orchestrateur Principal - Pipeline Manalytics
Reproduction exacte du cahier des charges avec les 4 projets GitHub
"""

import asyncio
import subprocess
import yaml
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import aiofiles

class ManalyticsOrchestrator:
    def __init__(self, config_file='config.yaml'):
        """Initialise l'orchestrateur avec la config"""
        self.load_config(config_file)
        self.setup_logging()
        self.setup_directories()
        
    def load_config(self, config_file: str):
        """Charge la configuration YAML"""
        try:
            with open(config_file) as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Configuration par défaut
            self.config = {
                'cache_folder': './data',
                'format_data_path': './MTGOFormatData',
                'enabled_sources': ['melee', 'mtgo', 'topdeck'],
                'apis': {
                    'melee': {
                        'login_file': './credentials/melee_login.json'
                    },
                    'topdeck': {
                        'api_key_file': './credentials/topdeck_api.txt'
                    },
                    'mtgo': {}
                },
                'scraping': {
                    'max_retries': 5,
                    'retry_delay': 2,
                    'concurrent_requests': 10,
                    'rate_limit_delay': 0.5
                }
            }
            # Sauvegarder la config par défaut
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
        
    def setup_logging(self):
        """Configure le système de logging"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/manalytics_{datetime.now():%Y%m%d_%H%M%S}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Manalytics')
        
    def setup_directories(self):
        """Crée l'arborescence des dossiers"""
        directories = [
            'data/raw',
            'data/processed', 
            'data/output',
            'logs',
            'credentials',
            'src/python/scraper',
            'src/python/classifier',
            'src/python/utils',
            'src/r/analysis',
            'src/r/utils'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
    async def run_pipeline(self, format_name: str, start_date: str, end_date: str):
        """Exécute le pipeline complet selon le cahier des charges"""
        try:
            self.logger.info(f"🚀 DÉMARRAGE PIPELINE MANALYTICS")
            self.logger.info(f"Format: {format_name}")
            self.logger.info(f"Période: {start_date} → {end_date}")
            
            # ÉTAPE 1: Scraping des données (fbettega/mtg_decklist_scrapper)
            self.logger.info("📥 ÉTAPE 1: Scraping des données depuis Melee.gg/MTGO")
            await self.run_scrapers(format_name, start_date, end_date)
            
            # ÉTAPE 2: Formatage selon MTGODecklistCache (Jiliac/MTGODecklistCache)
            self.logger.info("📋 ÉTAPE 2: Formatage des données selon MTGODecklistCache")
            self.format_data_to_cache_schema(format_name)
            
            # ÉTAPE 3: Classification des archétypes (Badaro/MTGOArchetypeParser)
            self.logger.info("🏷️ ÉTAPE 3: Classification des archétypes")
            self.run_archetype_classification(format_name)
            
            # ÉTAPE 4: Analyse R (Jiliac/R-Meta-Analysis)
            self.logger.info("📊 ÉTAPE 4: Analyse statistique R")
            self.run_r_analysis(format_name)
            
            self.logger.info("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
            
        except Exception as e:
            self.logger.error(f"❌ ÉCHEC DU PIPELINE: {str(e)}")
            raise
            
    async def run_scrapers(self, format_name: str, start_date: str, end_date: str):
        """Exécute les scrapers selon fbettega/mtg_decklist_scrapper"""
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'src', 'python'))
        
        from scraper.melee_scraper import MeleeScraper
        from scraper.mtgo_scraper import MTGOScraper
        from scraper.topdeck_scraper import TopdeckScraper
        
        scrapers = []
        
        # Initialiser les scrapers activés
        if 'melee' in self.config['enabled_sources']:
            scrapers.append(MeleeScraper(
                cache_folder=self.config['cache_folder'],
                api_config=self.config['apis']['melee']
            ))
            
        if 'mtgo' in self.config['enabled_sources']:
            scrapers.append(MTGOScraper(
                cache_folder=self.config['cache_folder'],
                api_config=self.config['apis']['mtgo']
            ))
            
        if 'topdeck' in self.config['enabled_sources']:
            scrapers.append(TopdeckScraper(
                cache_folder=self.config['cache_folder'],
                api_config=self.config['apis']['topdeck']
            ))
        
        # Exécuter le scraping en parallèle
        tasks = []
        for scraper in scrapers:
            task = scraper.fetch_date_range(format_name, start_date, end_date)
            tasks.append(task)
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Vérifier les résultats
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Scraper {i} failed: {result}")
                else:
                    self.logger.info(f"Scraper {i} completed: {result}")
        else:
            self.logger.warning("Aucun scraper activé")
            
    def format_data_to_cache_schema(self, format_name: str):
        """Formate les données selon le schéma MTGODecklistCache"""
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'src', 'python'))
        
        from utils.cache_formatter import MTGODecklistCacheFormatter
        
        formatter = MTGODecklistCacheFormatter(
            input_dir=f"{self.config['cache_folder']}/raw",
            output_dir=f"{self.config['cache_folder']}/processed"
        )
        
        formatter.format_all_tournaments(format_name)
        self.logger.info(f"Formatage terminé pour {format_name}")
        
    def run_archetype_classification(self, format_name: str):
        """Exécute la classification selon MTGOArchetypeParser"""
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'src', 'python'))
        
        from classifier.archetype_engine import ArchetypeEngine
        
        engine = ArchetypeEngine(
            format_data_path=self.config['format_data_path'],
            input_dir=f"{self.config['cache_folder']}/processed",
            output_dir=f"{self.config['cache_folder']}/processed"
        )
        
        engine.classify_all_tournaments(format_name)
        self.logger.info(f"Classification terminée pour {format_name}")
        
    def run_r_analysis(self, format_name: str):
        """Exécute l'analyse R selon R-Meta-Analysis"""
        cmd = [
            'Rscript', 
            'src/r/analysis/run_analysis.R',
            f"{self.config['cache_folder']}/processed",
            f"{self.config['cache_folder']}/output/metagame_{format_name}_{datetime.now():%Y%m%d}.json",
            format_name
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info(f"Analyse R terminée: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erreur analyse R: {e.stderr}")
            raise
            
    def setup_dependencies(self):
        """Clone et configure les dépendances GitHub"""
        repos = [
            {
                'url': 'https://github.com/Badaro/MTGOFormatData.git',
                'path': 'MTGOFormatData'
            },
            {
                'url': 'https://github.com/Jiliac/MTGODecklistCache.git', 
                'path': 'MTGODecklistCache'
            }
        ]
        
        for repo in repos:
            if not os.path.exists(repo['path']):
                self.logger.info(f"Clonage de {repo['url']}")
                subprocess.run(['git', 'clone', repo['url'], repo['path']], check=True)
            else:
                self.logger.info(f"Mise à jour de {repo['path']}")
                subprocess.run(['git', 'pull'], cwd=repo['path'], check=True)

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline Manalytics - Analyse MTG')
    parser.add_argument('--format', required=True, help='Format MTG (modern, legacy, vintage, etc.)')
    parser.add_argument('--start-date', default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', default=datetime.now().strftime('%Y-%m-%d'), help='Date de fin (YYYY-MM-DD)')
    parser.add_argument('--setup', action='store_true', help='Configure les dépendances')
    
    args = parser.parse_args()
    
    orchestrator = ManalyticsOrchestrator()
    
    if args.setup:
        orchestrator.setup_dependencies()
        print("✅ Configuration terminée")
        return
        
    # Exécuter le pipeline
    asyncio.run(orchestrator.run_pipeline(args.format, args.start_date, args.end_date))

if __name__ == "__main__":
    main() 