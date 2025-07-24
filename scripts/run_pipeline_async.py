"""
Main pipeline orchestrator for data collection and analysis.
"""
import asyncio
import click
import logging
from datetime import datetime
from typing import List, Dict, Any

from config.settings import settings
from config.logging_config import setup_logging
from src.scrapers.mtgo_scraper import MTGOScraper
from src.scrapers.melee_scraper import MeleeScraper
from src.parsers.archetype_engine import ArchetypeEngine
from src.parsers.decklist_parser import DecklistParser
from database.db_pool import get_db_connection
from database.db_manager import save_tournament_results

logger = logging.getLogger(__name__)

class Pipeline:
    """Orchestrates the entire data pipeline."""
    
    def __init__(self, format_name: str, days_back: int):
        self.format_name = format_name
        self.days_back = days_back
        self.archetype_engine = ArchetypeEngine()
        self.decklist_parser = DecklistParser()
        
    async def run(self):
        """Run the complete pipeline."""
        logger.info(f"Starting pipeline for {self.format_name} - last {self.days_back} days")
        
        # Step 1: Collect data
        tournaments = await self._collect_data()
        logger.info(f"Collected {len(tournaments)} tournaments")
        
        # Step 2: Process and save each tournament
        success_count = 0
        for tournament in tournaments:
            if await self._process_tournament(tournament):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count}/{len(tournaments)} tournaments")
        
        # Step 3: Generate reports (optional)
        if success_count > 0:
            await self._generate_reports()
    
    async def _collect_data(self) -> List[Dict[str, Any]]:
        """Collect data from all enabled scrapers."""
        all_tournaments = []
        
        # Run scrapers concurrently
        tasks = []
        
        if "mtgo" in settings.ENABLED_SCRAPERS:
            scraper = MTGOScraper(self.format_name)
            tasks.append(scraper.run(self.days_back))
        
        if "melee" in settings.ENABLED_SCRAPERS:
            from src.scrapers.melee_scraper import MeleeScraper
            scraper = MeleeScraper(self.format_name)
            tasks.append(scraper.run(self.days_back))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraper error: {result}")
            elif isinstance(result, list):
                all_tournaments.extend(result)
        
        return all_tournaments
    
    async def _process_tournament(self, tournament: Dict[str, Any]) -> bool:
        """Process a single tournament."""
        try:
            # Identify archetypes for all decklists
            for decklist in tournament.get('decklists', []):
                # Combine mainboard and sideboard for detection
                all_cards = decklist.get('mainboard', []) + decklist.get('sideboard', [])
                
                archetype, method, confidence = self.archetype_engine.identify_archetype(
                    all_cards, self.format_name
                )
                
                decklist['archetype'] = archetype
                decklist['detection_method'] = method
                decklist['confidence'] = confidence
                
                # Validate decklist
                is_valid, errors = self.decklist_parser.validate_decklist(
                    decklist.get('mainboard', []),
                    decklist.get('sideboard', [])
                )
                
                if not is_valid:
                    logger.warning(f"Invalid decklist for {decklist.get('player')}: {errors}")
            
            # Save to database
            with get_db_connection() as conn:
                save_tournament_results(conn, tournament)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process tournament {tournament.get('name')}: {e}")
            return False
    
    async def _generate_reports(self):
        """Generate analysis reports after data collection."""
        logger.info("Generating analysis reports...")
        
        # This could trigger visualization generation, send notifications, etc.
        # For now, just log completion
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT t.id) as tournaments,
                       COUNT(d.id) as decklists
                FROM manalytics.tournaments t
                LEFT JOIN manalytics.decklists d ON d.tournament_id = t.id
                JOIN manalytics.formats f ON t.format_id = f.id
                WHERE f.name = %s
                AND t.date >= CURRENT_DATE - INTERVAL '%s days'
            """, (self.format_name, self.days_back))
            
            result = cursor.fetchone()
            logger.info(f"Report: {result[0]} tournaments, {result[1]} decklists in last {self.days_back} days")

@click.command()
@click.option('--format', 'format_name', required=True, 
              type=click.Choice(settings.ENABLED_FORMATS),
              help='MTG format to process')
@click.option('--days', 'days_back', default=7, type=int,
              help='Number of days to look back')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(format_name: str, days_back: int, debug: bool):
    """Run the Manalytics data pipeline."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    pipeline = Pipeline(format_name, days_back)
    
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()