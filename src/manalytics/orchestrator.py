"""
Manalytics Orchestrator - Coordinates all pipeline operations
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import asyncio
import concurrent.futures

from .scrapers import MeleeScraper, MTGOScraper
from .parsers.archetype_engine import ArchetypeEngine
from .parsers.decklist_parser import DecklistParser
from .analyzers.meta_analyzer import MetaAnalyzer
from .analyzers.matchup_calculator import MatchupCalculator
from .visualizers.matchup_matrix import MatchupMatrixVisualizer
from .config import DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR
from .utils.data_loader import DataLoader

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Main orchestrator that coordinates all Manalytics operations:
    - Scraping from multiple platforms
    - Parsing and archetype detection
    - Analysis and calculations
    - Visualization generation
    """
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.archetype_engine = ArchetypeEngine()
        self.decklist_parser = DecklistParser()
        self.meta_analyzer = MetaAnalyzer()
        self.matchup_calculator = MatchupCalculator()
        self.visualizer = MatchupMatrixVisualizer()
        
        # Scraper instances
        self.scrapers = {
            'mtgo': MTGOScraper(),
            'melee': MeleeScraper()
        }
        
    def scrape_tournaments(
        self, 
        format_name: str, 
        days: int = 7,
        platforms: List[str] = ['mtgo', 'melee']
    ) -> Dict[str, Any]:
        """
        Scrape tournaments from specified platforms
        
        Args:
            format_name: MTG format (standard, modern, etc.)
            days: Number of days to scrape
            platforms: List of platforms to scrape from
            
        Returns:
            Dict with results from each platform
        """
        logger.info(f"Starting tournament scraping for {format_name} (last {days} days)")
        results = {}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Run scrapers in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            future_to_platform = {
                executor.submit(
                    self._scrape_platform,
                    platform,
                    format_name,
                    start_date,
                    end_date
                ): platform
                for platform in platforms if platform in self.scrapers
            }
            
            for future in concurrent.futures.as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    result = future.result()
                    results[platform] = result
                    logger.info(f"✓ {platform}: {len(result.get('tournaments', []))} tournaments")
                except Exception as e:
                    logger.error(f"✗ {platform} failed: {str(e)}")
                    results[platform] = {'error': str(e), 'tournaments': []}
                    
        return results
    
    def _scrape_platform(
        self,
        platform: str,
        format_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Scrape a single platform"""
        scraper = self.scrapers[platform]
        
        if platform == 'mtgo':
            tournaments = scraper.scrape_format(
                format_name, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
        else:  # melee
            tournaments = scraper.scrape_tournaments(
                format_name,
                start_date,
                end_date
            )
            
        return {
            'platform': platform,
            'format': format_name,
            'tournaments': tournaments,
            'count': len(tournaments)
        }
    
    def parse_and_detect(
        self, 
        scrape_results: Dict[str, Any],
        format_name: str
    ) -> Dict[str, Any]:
        """
        Parse decklists and detect archetypes
        
        Args:
            scrape_results: Results from scrape_tournaments
            format_name: MTG format
            
        Returns:
            Parsing results with archetype detection
        """
        logger.info("Starting decklist parsing and archetype detection")
        
        total_decks = 0
        valid_decks = 0
        archetype_counts = {}
        
        for platform, data in scrape_results.items():
            if 'error' in data:
                continue
                
            for tournament in data.get('tournaments', []):
                for deck in tournament.get('decklists', []):
                    total_decks += 1
                    
                    # Validate deck
                    mainboard = deck.get('mainboard', [])
                    sideboard = deck.get('sideboard', [])
                    
                    is_valid, errors = self.decklist_parser.validate_decklist(
                        mainboard, sideboard
                    )
                    
                    if not is_valid:
                        logger.debug(f"Invalid deck: {errors}")
                        continue
                        
                    valid_decks += 1
                    
                    # Detect archetype
                    archetype, method, confidence = self.archetype_engine.identify_archetype(
                        mainboard, format_name
                    )
                    
                    deck['archetype'] = archetype
                    deck['detection_method'] = method
                    deck['confidence'] = confidence
                    
                    # Count archetypes
                    archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
                    
        return {
            'total_decks': total_decks,
            'valid_decks': valid_decks,
            'archetype_counts': archetype_counts,
            'validation_rate': (valid_decks / total_decks * 100) if total_decks > 0 else 0
        }
    
    def analyze_metagame(self, format_name: str) -> Dict[str, Any]:
        """
        Analyze the metagame for a format
        
        Args:
            format_name: MTG format
            
        Returns:
            Metagame analysis results
        """
        logger.info(f"Analyzing {format_name} metagame")
        
        # Load recent tournament data
        tournaments = self.data_loader.load_format_data(format_name, days=30)
        
        if not tournaments:
            logger.warning("No tournament data found for analysis")
            return {}
            
        # Calculate meta percentages
        meta_stats = self.meta_analyzer.calculate_meta_percentage(tournaments)
        
        # Calculate matchups if enough data
        matchups = {}
        if len(tournaments) >= 5:  # Need minimum data for matchups
            matchups = self.matchup_calculator.calculate_all_matchups(
                tournaments, format_name
            )
            
        # Get top archetypes
        top_archetypes = sorted(
            meta_stats.items(),
            key=lambda x: x[1]['percentage'],
            reverse=True
        )[:10]
        
        return {
            'format': format_name,
            'total_tournaments': len(tournaments),
            'total_decks': sum(len(t.get('decklists', [])) for t in tournaments),
            'archetypes': meta_stats,
            'top_archetypes': [
                {
                    'name': arch,
                    'percentage': data['percentage'],
                    'count': data['count']
                }
                for arch, data in top_archetypes
            ],
            'matchups': matchups
        }
    
    def generate_visualizations(
        self,
        analysis_results: Dict[str, Any],
        format_name: str
    ) -> Dict[str, Any]:
        """
        Generate visualization files from analysis
        
        Args:
            analysis_results: Results from analyze_metagame
            format_name: MTG format
            
        Returns:
            Paths to generated visualization files
        """
        logger.info("Generating visualizations")
        
        output_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate matchup matrix if we have data
        if analysis_results.get('matchups'):
            matrix_path = OUTPUT_DIR / f"{format_name}_matchup_matrix_{timestamp}.png"
            self.visualizer.create_matchup_heatmap(
                analysis_results['matchups'],
                str(matrix_path)
            )
            output_files.append(str(matrix_path))
            
        # Generate meta pie chart
        if analysis_results.get('top_archetypes'):
            # This would use another visualizer
            # pie_path = OUTPUT_DIR / f"{format_name}_meta_pie_{timestamp}.png"
            # self.meta_visualizer.create_pie_chart(...)
            pass
            
        return {
            'files': output_files,
            'timestamp': timestamp
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            # Check data directories
            tournament_count = self.data_loader.count_tournaments()
            
            # Check if we can load archetype rules
            archetype_count = len(self.archetype_engine.rules)
            
            return {
                'status': 'operational',
                'database': 'connected',  # Would check actual DB
                'data_dir': str(DATA_DIR),
                'recent_tournaments': tournament_count,
                'archetypes_count': archetype_count,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def run_complete_pipeline(
        self,
        format_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline end-to-end
        
        Args:
            format_name: MTG format
            days: Number of days to process
            
        Returns:
            Complete pipeline results
        """
        logger.info(f"Running complete pipeline for {format_name}")
        
        results = {
            'format': format_name,
            'start_time': datetime.now().isoformat(),
            'steps': {}
        }
        
        try:
            # Step 1: Scrape
            scrape_results = self.scrape_tournaments(format_name, days)
            results['steps']['scrape'] = {
                'status': 'success',
                'platforms': list(scrape_results.keys()),
                'total_tournaments': sum(
                    len(r.get('tournaments', [])) 
                    for r in scrape_results.values()
                )
            }
            
            # Step 2: Parse
            parse_results = self.parse_and_detect(scrape_results, format_name)
            results['steps']['parse'] = {
                'status': 'success',
                **parse_results
            }
            
            # Step 3: Analyze
            analysis = self.analyze_metagame(format_name)
            results['steps']['analyze'] = {
                'status': 'success',
                'archetypes_found': len(analysis.get('archetypes', {})),
                'total_decks_analyzed': analysis.get('total_decks', 0)
            }
            
            # Step 4: Visualize
            viz_results = self.generate_visualizations(analysis, format_name)
            results['steps']['visualize'] = {
                'status': 'success',
                **viz_results
            }
            
            results['status'] = 'success'
            results['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            results['status'] = 'failed'
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()
            
        return results