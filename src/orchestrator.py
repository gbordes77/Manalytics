"""
Orchestrator Manalytics - Phase 2 (Production-Ready)
Sans ML, Dashboard, ou fonctionnalités avancées
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from src.python.scraper import ScraperFactory
from src.python.classifier import ArchetypeEngine
from src.python.cache import RedisCache
from src.python.api import create_app
from src.python.monitoring import MetricsCollector

class ManalyticsOrchestrator:
    """Orchestrateur Phase 2 - Stable et Production-Ready"""
    
    def __init__(self, config_file='config_phase2.yaml'):
        self.config = self.load_config(config_file)
        self.cache = RedisCache(self.config['redis'])
        self.metrics = MetricsCollector()
        
    async def run_pipeline(self, format: str, start_date: str, end_date: str):
        """Pipeline Phase 2 sans ML ni prédictions"""
        try:
            # 1. Scraping avec cache
            await self.run_scrapers(format, start_date, end_date)
            
            # 2. Classification
            self.run_classifier(format)
            
            # 3. Analyse basique (pas de R avancé)
            self.generate_metagame_json(format)
            
            # 4. Update cache & metrics
            await self.update_cache()
            self.metrics.record_pipeline_run(format)
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            raise
