import click
import logging
import asyncio
from tqdm import tqdm
from config.settings import settings
from config import logging_config
from src.scrapers.mtgo_scraper import MTGOScraper
from src.scrapers.melee_scraper import MeleeScraper
from src.parsers.archetype_engine import ArchetypeEngine
from src.parsers.decklist_parser import DecklistParser
from src.analyzers.meta_analyzer import MetaAnalyzer
from src.analyzers.matchup_calculator import MatchupCalculator
from src.visualizers.matchup_matrix import MatchupMatrixVisualizer
from database.db_pool import get_db_connection, close_db_pool
from database.db_manager import save_tournament_results

logger = logging.getLogger(__name__)

def process_tournaments(tournaments: list, format_name: str, archetype_engine: ArchetypeEngine):
    if not tournaments:
        logger.info("No tournaments to process.")
        return
    
    logger.info("=== Step 2: Processing Decklists & Detecting Archetypes ===")
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

async def scrape_all_tournaments(format_name: str, days: int):
    """Scrape tournaments from all enabled scrapers."""
    scrapers = {"mtgo": MTGOScraper, "melee": MeleeScraper}
    all_tournaments = []
    
    for name in settings.ENABLED_SCRAPERS:
        if name in scrapers:
            logger.info(f"Running {name} scraper...")
            scraper_instance = scrapers[name](format_name)
            tournaments = await scraper_instance.run(days_back=days)
            all_tournaments.extend(tournaments)
            logger.info(f"{name} scraper found {len(tournaments)} tournaments")
    
    return all_tournaments

@click.command()
@click.option('--format', 'format_name', default='standard', help='Format to analyze.')
@click.option('--days', default=7, help='Number of days of data to scrape.')
def main(format_name: str, days: int):
    logger.info(f"Starting Manalytics pipeline for format: {format_name}")
    
    archetype_engine = ArchetypeEngine()

    logger.info("=== Step 1: Scraping Data ===")
    all_tournaments = asyncio.run(scrape_all_tournaments(format_name, days))
    
    process_tournaments(all_tournaments, format_name, archetype_engine)
    
    logger.info("=== Step 3: Saving Results to Database ===")
    with get_db_connection() as conn:
        for tournament in tqdm(all_tournaments, desc="Saving tournaments"):
            if tournament.get('decklists'):
                save_tournament_results(conn, tournament)
    
    logger.info("=== Step 4: Analyzing Data ===")
    with get_db_connection() as conn:
        meta_analyzer = MetaAnalyzer(conn)
        meta_breakdown = meta_analyzer.get_meta_breakdown(format_name, days_back=days)
        logger.info("Meta Breakdown:")
        for arch in meta_breakdown[:10]:
            logger.info(f"  - {arch['archetype']} ({arch['deck_count']} decks): {arch['meta_share']:.2f}%")

        matchup_calculator = MatchupCalculator(conn)
        matchup_data = matchup_calculator.calculate_matchups(format_name, days_back=days)

    logger.info("=== Step 5: Generating Visualizations ===")
    visualizer = MatchupMatrixVisualizer()
    heatmap_path = visualizer.generate_heatmap(matchup_data, format_name)
    if heatmap_path:
        logger.info(f"Matchup heatmap saved to: {heatmap_path}")
    
    close_db_pool()
    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    main()