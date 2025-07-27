#!/usr/bin/env python3
"""
Pipeline modifié pour utiliser les données existantes au lieu de scraper
"""

import click
import logging
from datetime import datetime, timedelta
from tqdm import tqdm
from config.settings import settings
from config import logging_config
from src.utils.data_loader import DataLoader
from src.parsers.archetype_engine import ArchetypeEngine
from src.parsers.decklist_parser import DecklistParser
from src.analyzers.meta_analyzer import MetaAnalyzer
from src.analyzers.matchup_calculator import MatchupCalculator
from src.visualizers.matchup_matrix import MatchupMatrixVisualizer
from database.db_pool import get_db_connection, close_db_pool
from database.db_manager import save_tournament_results

logger = logging.getLogger(__name__)

def process_tournaments(tournaments: list, format_name: str, archetype_engine: ArchetypeEngine):
    """Process tournament data and detect archetypes."""
    if not tournaments:
        logger.info("No tournaments to process.")
        return
    
    logger.info("=== Processing Decklists & Detecting Archetypes ===")
    deck_parser = DecklistParser()
    
    all_decklists = [deck for t in tournaments for deck in t.get('decklists', [])]
    
    with tqdm(total=len(all_decklists), desc="Analyzing Decks") as pbar:
        for tournament in tournaments:
            valid_decks = []
            for decklist in tournament.get('decklists', []):
                mainboard = decklist.get('mainboard', [])
                sideboard = decklist.get('sideboard', [])
                
                is_valid, errors = deck_parser.validate_decklist(mainboard, sideboard)
                if not is_valid:
                    logger.warning(f"Invalid decklist for player {decklist.get('player', 'N/A')}: {', '.join(errors)}")
                    pbar.update(1)
                    continue

                if mainboard:
                    archetype, method, confidence = archetype_engine.identify_archetype(mainboard, format_name)
                    decklist['archetype'] = archetype
                    decklist['detection_method'] = method
                    decklist['confidence'] = confidence
                    valid_decks.append(decklist)
                pbar.update(1)
            tournament['decklists'] = valid_decks

@click.command()
@click.option('--format', 'format_name', default='standard', help='Format to analyze.')
@click.option('--platform', default=None, help='Platform to load (mtgo/melee). None = all')
@click.option('--days', default=30, help='Number of days of data to load.')
@click.option('--use-existing/--scrape-new', default=True, help='Use existing data or scrape new.')
def main(format_name: str, platform: str, days: int, use_existing: bool):
    """Run the Manalytics pipeline with existing data."""
    logger.info(f"Starting Manalytics pipeline for format: {format_name}")
    
    if use_existing:
        logger.info("=== Loading Existing Data ===")
        loader = DataLoader()
        
        # Count available data
        counts = loader.count_tournaments(platform=platform, format_name=format_name)
        logger.info("Available tournaments:")
        for key, count in counts.items():
            logger.info(f"  - {key}: {count} tournaments")
        
        # Load tournaments
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_tournaments = loader.load_tournaments(
            platform=platform,
            format_name=format_name,
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Loaded {len(all_tournaments)} tournaments from disk")
    else:
        logger.error("Scraping mode not implemented in this script. Use run_pipeline.py for scraping.")
        return
    
    if not all_tournaments:
        logger.warning("No tournaments found. Exiting.")
        return
    
    # Initialize archetype engine
    archetype_engine = ArchetypeEngine()
    
    # Process tournaments
    process_tournaments(all_tournaments, format_name, archetype_engine)
    
    logger.info("=== Saving Results to Database ===")
    with get_db_connection() as conn:
        for tournament in tqdm(all_tournaments, desc="Saving tournaments"):
            if tournament.get('decklists'):
                save_tournament_results(conn, tournament)
    
    logger.info("=== Analyzing Data ===")
    with get_db_connection() as conn:
        meta_analyzer = MetaAnalyzer(conn)
        meta_breakdown = meta_analyzer.get_meta_breakdown(format_name, days_back=days)
        
        logger.info("Meta Breakdown:")
        for arch in meta_breakdown[:10]:
            logger.info(f"  - {arch['archetype']} ({arch['deck_count']} decks): {arch['meta_share']:.2f}%")

        matchup_calculator = MatchupCalculator(conn)
        matchup_data = matchup_calculator.calculate_matchups(format_name, days_back=days)
    
    logger.info("=== Generating Visualizations ===")
    visualizer = MatchupMatrixVisualizer()
    heatmap_path = visualizer.generate_heatmap(matchup_data, format_name)
    if heatmap_path:
        logger.info(f"Matchup heatmap saved to: {heatmap_path}")
    
    close_db_pool()
    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()