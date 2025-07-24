#!/usr/bin/env python3
"""
MTGO Tournament Scraper Script - Robust Version
Scrapes MTGO tournaments with enhanced error handling and validation
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
import argparse
from typing import List, Dict, Any, Set
import csv

from scrapers.mtgo_scraper_robust import (
    TournamentList, Tournament, CacheItem, Deck, DeckItem,
    Standing, Round, RoundItem, TournamentTracker,
    MTGOSettings
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTGODataSaver:
    """Handles saving MTGO tournament data with enhanced features"""
    
    def __init__(self, base_path: str = "data/raw/mtgo"):
        self.base_path = Path(base_path)
        self.stats = {
            'saved': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def save_tournament(self, cache_item: CacheItem) -> bool:
        """Save tournament data to JSON file"""
        try:
            # Determine format folder
            format_name = cache_item.tournament.formats.lower()
            format_path = self.base_path / format_name
            
            # Determine subfolder based on tournament type
            if cache_item.tournament.tournament_type == "league":
                format_path = format_path / "leagues"
            elif cache_item.tournament.tournament_type in ["qualifier", "showcase", "championship"]:
                format_path = format_path / cache_item.tournament.tournament_type
            
            format_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename from tournament name and date
            date_str = cache_item.tournament.date.strftime("%Y%m%d")
            safe_name = "".join(c for c in cache_item.tournament.name if c.isalnum() or c in " -_").strip()
            safe_name = safe_name.replace(" ", "_")
            filename = f"{date_str}_{safe_name}.json"
            filepath = format_path / filename
            
            # Check if file already exists
            if filepath.exists():
                logger.debug(f"File already exists: {filepath}")
                self.stats['skipped'] += 1
                return True
            
            # Convert to JSON-serializable format
            tournament_data = self._convert_to_dict(cache_item)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {cache_item.tournament.tournament_type} to: {filepath}")
            self.stats['saved'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error saving tournament: {e}")
            self.stats['failed'] += 1
            return False
    
    def _convert_to_dict(self, cache_item: CacheItem) -> Dict[str, Any]:
        """Convert CacheItem to dictionary format"""
        tournament_dict = {
            "tournament_info": {
                "name": cache_item.tournament.name,
                "date": cache_item.tournament.date.isoformat(),
                "format": cache_item.tournament.formats,
                "tournament_type": cache_item.tournament.tournament_type,
                "url": cache_item.tournament.uri,
                "source": "mtgo",
                "scraped_at": datetime.now(timezone.utc).isoformat()
            },
            "players": []
        }
        
        # Add deck data
        for i, deck in enumerate(cache_item.decks):
            player_data = {
                "rank": i + 1,
                "player": deck.player,
                "result": deck.result,
                "deck_name": "Unknown",  # MTGO doesn't provide deck names
                "url": deck.anchor_uri,
                "mainboard": [
                    {
                        "count": item.count,
                        "card_name": item.card_name
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
            tournament_dict["players"].append(player_data)
        
        # Add standings if available
        if cache_item.standings:
            tournament_dict["standings"] = [
                {
                    "rank": standing.rank,
                    "player": standing.player,
                    "points": standing.points,
                    "wins": standing.wins,
                    "losses": standing.losses,
                    "draws": standing.draws,
                    "omwp": standing.omwp,
                    "gwp": standing.gwp,
                    "ogwp": standing.ogwp
                }
                for standing in cache_item.standings
            ]
        
        # Add rounds/bracket if available
        if cache_item.rounds:
            tournament_dict["rounds"] = []
            for round_data in cache_item.rounds:
                round_dict = {
                    "round_name": round_data.round_name,
                    "matches": [
                        {
                            "player1": match.player1,
                            "player2": match.player2,
                            "result": match.result
                        }
                        for match in round_data.matches
                    ]
                }
                tournament_dict["rounds"].append(round_dict)
        
        return tournament_dict
    
    def get_stats_summary(self) -> str:
        """Get summary of save statistics"""
        total = sum(self.stats.values())
        return (f"Save statistics: {self.stats['saved']} saved, "
                f"{self.stats['skipped']} skipped, {self.stats['failed']} failed "
                f"(Total: {total})")


class TournamentFilter:
    """Filter tournaments based on various criteria"""
    
    @staticmethod
    def filter_tournaments(tournaments: List[Tournament], 
                          formats: Set[str] = None,
                          tournament_types: Set[str] = None,
                          exclude_leagues: bool = False,
                          only_leagues: bool = False) -> List[Tournament]:
        """Filter tournaments based on criteria"""
        filtered = tournaments
        
        # Filter by format
        if formats:
            formats_lower = {f.lower() for f in formats}
            filtered = [t for t in filtered if t.formats.lower() in formats_lower]
        
        # Filter by tournament type
        if tournament_types:
            types_lower = {t.lower() for t in tournament_types}
            filtered = [t for t in filtered if t.tournament_type.lower() in types_lower]
        
        # League filters
        if exclude_leagues:
            filtered = [t for t in filtered if t.tournament_type != "league"]
        elif only_leagues:
            filtered = [t for t in filtered if t.tournament_type == "league"]
        
        return filtered


class ScrapeReport:
    """Generate scraping reports"""
    
    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_report(self, tournaments: List[Tournament], 
                               scraped: List[str], failed: List[str]):
        """Generate a summary report of the scraping session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"mtgo_scrape_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("MTGO Scraping Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total tournaments found: {len(tournaments)}\n")
            f.write(f"Successfully scraped: {len(scraped)}\n")
            f.write(f"Failed to scrape: {len(failed)}\n\n")
            
            # Tournament type breakdown
            f.write("Tournament Types:\n")
            type_counts = {}
            for t in tournaments:
                type_counts[t.tournament_type] = type_counts.get(t.tournament_type, 0) + 1
            for t_type, count in sorted(type_counts.items()):
                f.write(f"  {t_type}: {count}\n")
            
            # Format breakdown
            f.write("\nFormats:\n")
            format_counts = {}
            for t in tournaments:
                format_counts[t.formats] = format_counts.get(t.formats, 0) + 1
            for fmt, count in sorted(format_counts.items()):
                f.write(f"  {fmt}: {count}\n")
            
            # Failed tournaments
            if failed:
                f.write("\nFailed Tournaments:\n")
                for name in failed:
                    f.write(f"  - {name}\n")
        
        logger.info(f"Report saved to: {report_file}")
        return report_file
    
    def generate_csv_report(self, tournaments: List[Tournament]):
        """Generate CSV report of all tournaments"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"mtgo_tournaments_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Name', 'Format', 'Type', 'URL'])
            
            for t in tournaments:
                writer.writerow([
                    t.date.isoformat(),
                    t.name,
                    t.formats,
                    t.tournament_type,
                    t.uri
                ])
        
        logger.info(f"CSV report saved to: {csv_file}")
        return csv_file


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Scrape MTGO tournaments with enhanced features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all formats from last 30 days
  %(prog)s --days 30
  
  # Scrape only Standard tournaments, excluding leagues
  %(prog)s --format standard --exclude-leagues
  
  # Scrape only Modern and Legacy leagues
  %(prog)s --formats modern,legacy --only-leagues
  
  # Scrape specific tournament types
  %(prog)s --tournament-types challenge,showcase --days 7
  
  # Force redownload of all tournaments
  %(prog)s --days 7 --force-redownload
        """
    )
    
    parser.add_argument("--formats", type=str, 
                       help="Comma-separated list of formats to scrape")
    parser.add_argument("--format", type=str, 
                       help="Single format to scrape (legacy option)")
    parser.add_argument("--tournament-types", type=str,
                       help="Comma-separated list of tournament types")
    parser.add_argument("--days", type=int, default=30, 
                       help="Number of days to look back")
    parser.add_argument("--start-date", type=str,
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, 
                       help="Limit number of tournaments to scrape")
    parser.add_argument("--output", type=str, default="data/raw/mtgo", 
                       help="Output directory")
    parser.add_argument("--exclude-leagues", action="store_true", 
                       help="Exclude league tournaments")
    parser.add_argument("--only-leagues", action="store_true", 
                       help="Only scrape league tournaments")
    parser.add_argument("--force-redownload", action="store_true",
                       help="Force redownload even if already processed")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate scraping report")
    parser.add_argument("--dry-run", action="store_true",
                       help="List tournaments without downloading")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse date range
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        start_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        end_date = datetime.now(timezone.utc)
    
    logger.info(f"Scraping MTGO tournaments from {start_date.date()} to {end_date.date()}")
    
    # Initialize tournament list handler
    tournament_list = TournamentList()
    
    # Get tournament list
    tournaments = tournament_list.DL_tournaments(
        start_date, end_date, 
        skip_processed=not args.force_redownload
    )
    logger.info(f"Found {len(tournaments)} tournaments total")
    
    # Parse format filters
    formats = None
    if args.formats:
        formats = set(args.formats.split(','))
    elif args.format:
        formats = {args.format}
    
    # Parse tournament type filters
    tournament_types = None
    if args.tournament_types:
        tournament_types = set(args.tournament_types.split(','))
    
    # Apply filters
    filtered_tournaments = TournamentFilter.filter_tournaments(
        tournaments,
        formats=formats,
        tournament_types=tournament_types,
        exclude_leagues=args.exclude_leagues,
        only_leagues=args.only_leagues
    )
    
    logger.info(f"Filtered to {len(filtered_tournaments)} tournaments")
    
    # Apply limit if specified
    if args.limit:
        filtered_tournaments = filtered_tournaments[:args.limit]
    
    # Dry run - just list tournaments
    if args.dry_run:
        logger.info("DRY RUN - Listing tournaments without downloading:")
        for t in filtered_tournaments:
            print(f"{t.date} - {t.name} ({t.formats}/{t.tournament_type})")
        return
    
    # Initialize saver
    saver = MTGODataSaver(args.output)
    
    # Process tournaments
    scraped = []
    failed = []
    
    for i, tournament in enumerate(filtered_tournaments, 1):
        logger.info(f"Processing {i}/{len(filtered_tournaments)}: {tournament.name}")
        
        try:
            # Get tournament details
            details = tournament_list.get_tournament_details(tournament)
            
            if details:
                # Save tournament
                if saver.save_tournament(details):
                    scraped.append(tournament.name)
                else:
                    failed.append(tournament.name)
            else:
                logger.error(f"Failed to get details for: {tournament.name}")
                failed.append(tournament.name)
                
        except Exception as e:
            logger.error(f"Error processing {tournament.name}: {e}")
            failed.append(tournament.name)
    
    # Print summary
    logger.info("=" * 50)
    logger.info(saver.get_stats_summary())
    logger.info(f"Successfully scraped: {len(scraped)}")
    logger.info(f"Failed: {len(failed)}")
    
    # Generate report if requested
    if args.generate_report:
        report_gen = ScrapeReport()
        report_gen.generate_summary_report(filtered_tournaments, scraped, failed)
        report_gen.generate_csv_report(filtered_tournaments)


if __name__ == "__main__":
    main()