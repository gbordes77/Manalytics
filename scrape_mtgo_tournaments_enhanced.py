#!/usr/bin/env python3
"""
MTGO Tournament Scraper Script - Enhanced Version
Maximizes data extraction from MTGO tournaments
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse
from typing import List, Dict, Any
import csv

from scrapers.mtgo_scraper_enhanced import (
    MTGOEnhancedScraper, CacheItem, Tournament,
    DeckAnalyzer, MetagameAnalyzer
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTGODataSaver:
    """Save MTGO tournament data with enhanced organization"""
    
    def __init__(self, base_path: str = "data/raw/mtgo"):
        self.base_path = Path(base_path)
        self.stats = {
            'saved': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def save_tournament(self, cache_item: CacheItem) -> bool:
        """Save enhanced tournament data"""
        try:
            tournament = cache_item.tournament
            
            # Determine output path
            format_name = tournament.formats.lower() if tournament.formats else "unknown"
            format_path = self.base_path / format_name
            
            # Special handling for different tournament types
            if tournament.tournament_type == "league":
                format_path = format_path / "leagues"
            elif tournament.tournament_type in ["challenge", "showcase", "championship"]:
                format_path = format_path / tournament.tournament_type
            
            format_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            date_str = tournament.date.strftime("%Y%m%d")
            safe_name = "".join(c for c in tournament.name if c.isalnum() or c in " -_").strip()
            safe_name = safe_name.replace(" ", "_")[:100]
            filename = f"{date_str}_{safe_name}.json"
            filepath = format_path / filename
            
            # Check if exists
            if filepath.exists():
                logger.debug(f"File already exists: {filepath}")
                self.stats['skipped'] += 1
                return True
            
            # Convert to enhanced JSON format
            data = self._convert_to_dict(cache_item)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {tournament.tournament_type} to: {filepath}")
            self.stats['saved'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error saving tournament: {e}")
            self.stats['failed'] += 1
            return False
    
    def _convert_to_dict(self, cache_item: CacheItem) -> Dict[str, Any]:
        """Convert to enhanced dictionary format"""
        tournament = cache_item.tournament
        
        data = {
            "tournament_info": {
                "id": tournament.json_file.replace(".json", ""),
                "name": tournament.name,
                "date": tournament.date.isoformat(),
                "format": tournament.formats,
                "tournament_type": tournament.tournament_type,
                "url": tournament.uri,
                "source": "mtgo",
                "scraped_at": tournament.scraped_at.isoformat() if tournament.scraped_at else datetime.now(timezone.utc).isoformat()
            },
            "metadata": {},
            "standings": [],
            "players": [],
            "rounds": [],
            "metagame_breakdown": cache_item.metagame_breakdown or {}
        }
        
        # Add tournament metadata
        if tournament.metadata:
            data["metadata"] = {
                "total_players": tournament.metadata.total_players,
                "rounds_played": tournament.metadata.rounds_played,
                "top_cut_size": tournament.metadata.top_cut_size,
                "event_series": tournament.metadata.event_series
            }
        
        # Add standings
        if cache_item.standings:
            for standing in cache_item.standings:
                data["standings"].append({
                    "rank": standing.rank,
                    "player": standing.player,
                    "points": standing.points,
                    "wins": standing.wins,
                    "losses": standing.losses,
                    "draws": standing.draws,
                    "omwp": standing.omwp,
                    "gwp": standing.gwp,
                    "ogwp": standing.ogwp,
                    "match_points": standing.match_points,
                    "matches_played": standing.matches_played
                })
        
        # Add decks with enhanced data
        if cache_item.decks:
            for deck in cache_item.decks:
                player_data = {
                    "player": deck.player,
                    "result": deck.result,
                    "performance_rating": deck.performance_rating,
                    "deck_name": deck.deck_name,
                    "archetype": deck.archetype,
                    "mainboard": [
                        {
                            "count": item.count,
                            "card_name": item.card_name,
                            "metadata": {
                                "mana_cost": item.metadata.mana_cost,
                                "card_type": item.metadata.card_type,
                                "rarity": item.metadata.rarity,
                                "set_code": item.metadata.set_code
                            } if item.metadata else None
                        }
                        for item in deck.mainboard
                    ],
                    "sideboard": [
                        {
                            "count": item.count,
                            "card_name": item.card_name
                        }
                        for item in deck.sideboard
                    ]
                }
                
                # Add deck metrics
                if deck.metrics:
                    player_data["deck_metrics"] = {
                        "total_cards": deck.metrics.total_cards,
                        "unique_cards": deck.metrics.unique_cards,
                        "color_identity": deck.metrics.color_identity,
                        "card_types": deck.metrics.card_types,
                        "archetype_hints": deck.metrics.archetype_hints
                    }
                
                data["players"].append(player_data)
        
        # Add rounds/brackets
        if cache_item.rounds:
            for round_data in cache_item.rounds:
                round_dict = {
                    "round_name": round_data.round_name,
                    "round_number": round_data.round_number,
                    "is_elimination": round_data.is_elimination,
                    "matches": []
                }
                
                for match in round_data.matches:
                    round_dict["matches"].append({
                        "player1": match.player1,
                        "player2": match.player2,
                        "result": match.result,
                        "winner": match.winner,
                        "player1_wins": match.player1_wins,
                        "player2_wins": match.player2_wins,
                        "match_id": match.match_id
                    })
                
                data["rounds"].append(round_dict)
        
        return data
    
    def get_stats_summary(self) -> str:
        """Get save statistics summary"""
        total = sum(self.stats.values())
        return (f"Save statistics: {self.stats['saved']} saved, "
                f"{self.stats['skipped']} skipped, {self.stats['failed']} failed "
                f"(Total: {total})")


class EnhancedReport:
    """Generate enhanced scraping reports"""
    
    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_report(self, results: List[CacheItem]):
        """Generate comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"mtgo_enhanced_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("MTGO Enhanced Scraping Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total tournaments: {len(results)}\n\n")
            
            # Tournament breakdown
            f.write("Tournament Types:\n")
            type_counts = {}
            for item in results:
                t_type = item.tournament.tournament_type
                type_counts[t_type] = type_counts.get(t_type, 0) + 1
            
            for t_type, count in sorted(type_counts.items()):
                f.write(f"  {t_type}: {count}\n")
            
            # Format breakdown  
            f.write("\nFormats:\n")
            format_counts = {}
            for item in results:
                fmt = item.tournament.formats or "Unknown"
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
            for fmt, count in sorted(format_counts.items()):
                f.write(f"  {fmt}: {count}\n")
            
            # Data quality
            f.write("\nData Quality:\n")
            with_standings = sum(1 for item in results if item.standings)
            with_rounds = sum(1 for item in results if item.rounds)
            with_metagame = sum(1 for item in results if item.metagame_breakdown)
            
            f.write(f"  Tournaments with standings: {with_standings} ({with_standings/len(results)*100:.1f}%)\n")
            f.write(f"  Tournaments with round data: {with_rounds} ({with_rounds/len(results)*100:.1f}%)\n")
            f.write(f"  Tournaments with metagame analysis: {with_metagame} ({with_metagame/len(results)*100:.1f}%)\n")
            
            # Deck statistics
            total_decks = sum(len(item.decks) for item in results)
            avg_decks = total_decks / len(results) if results else 0
            
            f.write(f"\nDeck Statistics:\n")
            f.write(f"  Total decks: {total_decks}\n")
            f.write(f"  Average decks per tournament: {avg_decks:.1f}\n")
            
            # Enhanced data features
            decks_with_metrics = sum(
                sum(1 for deck in item.decks if deck.metrics)
                for item in results
            )
            f.write(f"  Decks with metrics analysis: {decks_with_metrics}\n")
            
            # Most common archetypes
            f.write("\nTop Archetypes (from hints):\n")
            archetype_counts = {}
            for item in results:
                for deck in item.decks:
                    if deck.metrics and deck.metrics.archetype_hints:
                        for hint in deck.metrics.archetype_hints:
                            archetype_counts[hint] = archetype_counts.get(hint, 0) + 1
            
            for archetype, count in sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"  {archetype}: {count}\n")
            
            # Tournament series
            f.write("\nTournament Series:\n")
            series_counts = {}
            for item in results:
                if item.tournament.metadata and item.tournament.metadata.event_series:
                    series = item.tournament.metadata.event_series
                    series_counts[series] = series_counts.get(series, 0) + 1
            
            for series, count in sorted(series_counts.items()):
                f.write(f"  {series}: {count}\n")
        
        logger.info(f"Report saved to: {report_file}")
        return report_file
    
    def generate_metagame_csv(self, results: List[CacheItem]):
        """Generate CSV with metagame breakdown"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"mtgo_metagame_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Date', 'Tournament', 'Format', 'Type', 'Players',
                'Top Archetype', 'Top %', 'Has Standings', 'Has Rounds'
            ])
            
            for item in results:
                tournament = item.tournament
                
                # Get top archetype
                top_archetype = "Unknown"
                top_percentage = 0
                if item.metagame_breakdown:
                    top_archetype = list(item.metagame_breakdown.keys())[0]
                    top_percentage = item.metagame_breakdown[top_archetype]
                
                writer.writerow([
                    tournament.date.strftime("%Y-%m-%d"),
                    tournament.name,
                    tournament.formats,
                    tournament.tournament_type,
                    tournament.metadata.total_players if tournament.metadata else len(item.decks),
                    top_archetype,
                    f"{top_percentage:.1f}%",
                    "Yes" if item.standings else "No",
                    "Yes" if item.rounds else "No"
                ])
        
        logger.info(f"Metagame CSV saved to: {csv_file}")
        return csv_file


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Scrape MTGO tournaments with enhanced data extraction",
        epilog="""
Examples:
  # Scrape all formats from last 30 days
  %(prog)s --days 30
  
  # Scrape only Modern Challenges
  %(prog)s --format modern --tournament-types challenge --days 30
  
  # Include leagues (stored separately)
  %(prog)s --format standard --include-leagues --days 7
  
  # Generate detailed reports
  %(prog)s --days 30 --generate-report
        """
    )
    
    parser.add_argument("--format", type=str,
                       help="Format to scrape (standard, modern, legacy, etc)")
    parser.add_argument("--tournament-types", type=str,
                       help="Comma-separated tournament types (challenge,league,showcase,etc)")
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days to look back")
    parser.add_argument("--start-date", type=str,
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date (YYYY-MM-DD)")
    parser.add_argument("--include-leagues", action="store_true",
                       help="Include league tournaments")
    parser.add_argument("--force-redownload", action="store_true",
                       help="Force redownload even if already processed")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate enhanced analysis reports")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse dates
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        start_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        end_date = datetime.now(timezone.utc)
    
    # Parse tournament types
    tournament_types = None
    if args.tournament_types:
        tournament_types = [t.strip() for t in args.tournament_types.split(',')]
    elif not args.include_leagues:
        # Exclude leagues by default
        tournament_types = ["challenge", "showcase", "championship", "qualifier", "prelim", "special", "other"]
    
    logger.info(f"Scraping MTGO tournaments from {start_date.date()} to {end_date.date()}")
    if args.format:
        logger.info(f"Format filter: {args.format}")
    if tournament_types:
        logger.info(f"Tournament types: {tournament_types}")
    
    # Scrape tournaments
    scraper = MTGOEnhancedScraper()
    results = scraper.scrape_tournaments(
        start_date=start_date,
        end_date=end_date,
        format_filter=args.format,
        tournament_types=tournament_types,
        skip_processed=not args.force_redownload
    )
    
    logger.info(f"Scraped {len(results)} tournaments")
    
    # Save data
    saver = MTGODataSaver()
    for cache_item in results:
        saver.save_tournament(cache_item)
    
    # Summary
    logger.info("=" * 50)
    logger.info(saver.get_stats_summary())
    
    # Generate reports
    if args.generate_report and results:
        report_gen = EnhancedReport()
        report_gen.generate_summary_report(results)
        report_gen.generate_metagame_csv(results)
        
        # Show enhanced data statistics
        logger.info("\nEnhanced Data Extracted:")
        logger.info(f"- Tournaments with standings: {sum(1 for r in results if r.standings)}")
        logger.info(f"- Tournaments with rounds: {sum(1 for r in results if r.rounds)}")
        logger.info(f"- Decks with metrics: {sum(sum(1 for d in r.decks if d.metrics) for r in results)}")
        logger.info(f"- Metagame breakdowns: {sum(1 for r in results if r.metagame_breakdown)}")


if __name__ == "__main__":
    main()