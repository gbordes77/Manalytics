#!/usr/bin/env python3
"""
Melee Tournament Scraper Script - Complete Version
Uses the complete Melee scraper with all original functionality
"""

import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
import argparse
from typing import List, Dict, Any, Set
import csv

from scrapers.melee_scraper_complete import (
    MtgMeleeClient, MtgMeleeTournamentInfo, MtgMeleePlayerDeck,
    MtgMeleeConstants, MtgMeleeAuthManager, TournamentList,
    Standing, RoundItem, Round
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeleeDataSaver:
    """Handles saving Melee tournament data with proper organization"""
    
    def __init__(self, base_path: str = "data/raw/melee"):
        self.base_path = Path(base_path)
        self.stats = {
            'saved': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def save_tournament(self, tournament: TournamentData) -> bool:
        """Save tournament data to JSON file"""
        try:
            # Determine format folder
            format_name = tournament.format.lower()
            format_path = self.base_path / format_name
            
            # Special handling for leagues - store in subfolder
            if tournament.tournament_type == "league":
                format_path = format_path / "leagues"
            # Other special tournament types can have their own folders
            elif tournament.tournament_type in ["rcq", "championship", "qualifier"]:
                format_path = format_path / tournament.tournament_type
            elif tournament.tournament_type == "fnm":
                format_path = format_path / "fnm"
            elif tournament.tournament_type == "prerelease":
                format_path = format_path / "prerelease"
            
            format_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            date_str = tournament.date.strftime("%Y%m%d")
            safe_name = "".join(c for c in tournament.name if c.isalnum() or c in " -_").strip()
            safe_name = safe_name.replace(" ", "_")[:100]  # Limit length
            filename = f"{date_str}_{safe_name}_{tournament.id}.json"
            filepath = format_path / filename
            
            # Check if file already exists
            if filepath.exists():
                logger.debug(f"File already exists: {filepath}")
                self.stats['skipped'] += 1
                return True
            
            # Convert to JSON-serializable format
            tournament_data = self._convert_to_dict(tournament)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {tournament.tournament_type} to: {filepath}")
            self.stats['saved'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error saving tournament: {e}")
            self.stats['failed'] += 1
            return False
    
    def _convert_to_dict(self, tournament: TournamentData) -> Dict[str, Any]:
        """Convert TournamentData to dictionary format"""
        tournament_dict = {
            "tournament_info": {
                "id": tournament.id,
                "name": tournament.name,
                "date": tournament.date.isoformat(),
                "format": tournament.format,
                "tournament_type": tournament.tournament_type,
                "organization": tournament.organization,
                "player_count": tournament.player_count,
                "url": tournament.url,
                "source": "melee",
                "pro_tour": tournament.pro_tour,
                "scraped_at": datetime.now(timezone.utc).isoformat()
            },
            "standings": [],
            "players": [],
            "round_metadata": []
        }
        
        # Add standings
        for standing in tournament.standings:
            standing_data = {
                "rank": standing.rank,
                "player": standing.player,
                "points": standing.points,
                "omwp": standing.omwp,
                "gwp": standing.gwp,
                "ogwp": standing.ogwp
            }
            tournament_dict["standings"].append(standing_data)
        
        # Add decklists
        for decklist in tournament.decklists:
            player_data = {
                "rank": decklist.rank,
                "player": decklist.player,
                "deck_name": decklist.deck_name,
                "archetype": decklist.archetype,
                "mainboard": [
                    {
                        "count": card.quantity,
                        "card_name": card.name
                    }
                    for card in decklist.mainboard
                ],
                "sideboard": [
                    {
                        "count": card.quantity,
                        "card_name": card.name
                    }
                    for card in decklist.sideboard
                ]
            }
            
            # Add commander if present
            if decklist.commander:
                player_data["commander"] = decklist.commander
            
            tournament_dict["players"].append(player_data)
        
        # Add round metadata
        for round_data in tournament.round_metadata:
            round_dict = {
                "round": round_data.round_number,
                "matches": []
            }
            
            for match in round_data.matches:
                match_dict = {
                    "player1": match.player1,
                    "player2": match.player2,
                    "result": match.result,
                    "winner": match.winner,
                    "player1_wins": match.player1_wins,
                    "player2_wins": match.player2_wins
                }
                round_dict["matches"].append(match_dict)
            
            tournament_dict["round_metadata"].append(round_dict)
        
        return tournament_dict
    
    def get_stats_summary(self) -> str:
        """Get summary of save statistics"""
        total = sum(self.stats.values())
        return (f"Save statistics: {self.stats['saved']} saved, "
                f"{self.stats['skipped']} skipped, {self.stats['failed']} failed "
                f"(Total: {total})")


class ScrapeReport:
    """Generate detailed scraping reports"""
    
    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_report(self, tournaments: List[TournamentData], 
                               scraped: List[str], failed: List[str]):
        """Generate a comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"melee_scrape_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("Melee.gg Scraping Report - Complete Version\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total tournaments found: {len(tournaments)}\n")
            f.write(f"Successfully scraped: {len(scraped)}\n")
            f.write(f"Failed to scrape: {len(failed)}\n\n")
            
            # Tournament type breakdown
            f.write("Tournament Types:\n")
            type_counts = {}
            league_count = 0
            for t in tournaments:
                type_counts[t.tournament_type] = type_counts.get(t.tournament_type, 0) + 1
                if t.tournament_type == "league":
                    league_count += 1
            
            for t_type, count in sorted(type_counts.items()):
                f.write(f"  {t_type}: {count}")
                if t_type == "league":
                    f.write(" (stored in separate leagues/ subdirectory)")
                f.write("\n")
            
            # Format breakdown
            f.write("\nFormats:\n")
            format_counts = {}
            for t in tournaments:
                format_counts[t.format] = format_counts.get(t.format, 0) + 1
            for fmt, count in sorted(format_counts.items()):
                f.write(f"  {fmt}: {count}\n")
            
            # Organization breakdown
            f.write("\nTop 10 Organizations:\n")
            org_counts = {}
            for t in tournaments:
                org_counts[t.organization] = org_counts.get(t.organization, 0) + 1
            for org, count in sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"  {org}: {count}\n")
            
            # Pro Tour tournaments
            pro_tour_count = sum(1 for t in tournaments if t.pro_tour)
            if pro_tour_count > 0:
                f.write(f"\nPro Tour tournaments: {pro_tour_count}\n")
            
            # Deck statistics
            total_decks = sum(len(t.decklists) for t in tournaments)
            avg_decks = total_decks / len(tournaments) if tournaments else 0
            
            # Standing statistics  
            total_standings = sum(len(t.standings) for t in tournaments)
            avg_standings = total_standings / len(tournaments) if tournaments else 0
            
            # Round data statistics
            tournaments_with_rounds = sum(1 for t in tournaments if t.round_metadata)
            
            f.write(f"\nData Statistics:\n")
            f.write(f"  Total decklists: {total_decks}\n")
            f.write(f"  Average decks per tournament: {avg_decks:.1f}\n")
            f.write(f"  Total standings: {total_standings}\n")
            f.write(f"  Average standings per tournament: {avg_standings:.1f}\n")
            f.write(f"  Tournaments with round data: {tournaments_with_rounds}\n")
            
            # Failed tournaments
            if failed:
                f.write("\nFailed Tournaments:\n")
                for name in failed[:20]:  # Limit to first 20
                    f.write(f"  - {name}\n")
                if len(failed) > 20:
                    f.write(f"  ... and {len(failed) - 20} more\n")
            
            # Special notes
            if league_count > 0:
                f.write(f"\nNote: {league_count} league tournaments are stored in separate 'leagues' subdirectories\n")
                f.write("      for future separate analysis and won't appear in main data.\n")
        
        logger.info(f"Report saved to: {report_file}")
        return report_file
    
    def generate_csv_report(self, tournaments: List[TournamentData]):
        """Generate CSV report of all tournaments"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"melee_tournaments_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Date', 'Name', 'Format', 'Type', 'Organization', 
                'Players', 'Decks', 'Standings', 'Has Rounds', 'Pro Tour', 'URL'
            ])
            
            for t in tournaments:
                writer.writerow([
                    t.date.strftime("%Y-%m-%d"),
                    t.name,
                    t.format,
                    t.tournament_type,
                    t.organization,
                    t.player_count,
                    len(t.decklists),
                    len(t.standings),
                    'Yes' if t.round_metadata else 'No',
                    'Yes' if t.pro_tour else 'No',
                    t.url
                ])
        
        logger.info(f"CSV report saved to: {csv_file}")
        return csv_file


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Scrape Melee.gg tournaments with complete functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all formats from last 30 days
  %(prog)s --days 30
  
  # Scrape only Standard (excluding leagues by default)
  %(prog)s --format standard --days 30
  
  # Include leagues in scraping
  %(prog)s --format standard --include-leagues --days 30
  
  # Scrape only specific tournament types
  %(prog)s --format standard --tournament-types rcq,championship
  
  # Scrape multiple formats with detailed report
  %(prog)s --formats modern,legacy,pioneer --days 7 --generate-report
  
  # Dry run to see what would be scraped
  %(prog)s --dry-run --days 7
  
  # Force redownload and include Pro Tour events
  %(prog)s --force-redownload --include-pro-tour --days 90
        """
    )
    
    parser.add_argument("--format", type=str,
                       help="Single format to scrape")
    parser.add_argument("--formats", type=str,
                       help="Comma-separated list of formats")
    parser.add_argument("--tournament-types", type=str,
                       help="Comma-separated list of tournament types (rcq,championship,fnm,etc)")
    parser.add_argument("--exclude-types", type=str,
                       help="Comma-separated list of tournament types to exclude")
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days to look back")
    parser.add_argument("--start-date", type=str,
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int,
                       help="Limit number of tournaments to scrape")
    parser.add_argument("--output", type=str, default="data/raw/melee",
                       help="Output directory")
    parser.add_argument("--force-redownload", action="store_true",
                       help="Force redownload even if already processed")
    parser.add_argument("--include-leagues", action="store_true",
                       help="Include league tournaments (stored separately)")
    parser.add_argument("--include-pro-tour", action="store_true",
                       help="Include Pro Tour events")
    parser.add_argument("--min-deck-ratio", type=float, default=0.5,
                       help="Minimum deck validity ratio (default: 0.5)")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate detailed scraping report")
    parser.add_argument("--dry-run", action="store_true",
                       help="List tournaments without downloading")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--credentials", type=str, 
                       default="api_credentials/melee_login.json",
                       help="Path to credentials file")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load credentials
    creds_file = Path(args.credentials)
    if not creds_file.exists():
        logger.error(f"Credentials file not found: {creds_file}")
        logger.error("Please create the file with format: {\"email\": \"...\", \"password\": \"...\"}")
        return
    
    with open(creds_file) as f:
        creds_raw = json.load(f)
        # Handle different credential formats
        creds = {
            'email': creds_raw.get('email', creds_raw.get('login')),
            'password': creds_raw.get('password', creds_raw.get('mdp'))
        }
    
    # Parse date range
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        start_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        end_date = datetime.now(timezone.utc)
    
    logger.info(f"Scraping Melee tournaments from {start_date.date()} to {end_date.date()}")
    
    # Determine format filter
    format_filter = args.format
    if args.formats:
        # For multiple formats, we'll need to run multiple times
        formats = [f.strip() for f in args.formats.split(',')]
    else:
        formats = [format_filter] if format_filter else [None]
    
    # Parse tournament type filters
    included_types = None
    excluded_types = set()
    
    if args.tournament_types:
        included_types = {t.strip().lower() for t in args.tournament_types.split(',')}
    
    if args.exclude_types:
        excluded_types = {t.strip().lower() for t in args.exclude_types.split(',')}
    
    # Default exclude leagues unless explicitly included
    if not args.include_leagues and not (included_types and "league" in included_types):
        excluded_types.add("league")
        logger.info("Note: Leagues excluded by default. Use --include-leagues to include them.")
    
    all_tournaments = []
    
    # Scrape tournaments
    async with MtgMeleeScraperComplete(creds['email'], creds['password']) as scraper:
        # Configure scraper settings
        scraper.min_deck_validity_ratio = args.min_deck_ratio
        scraper.include_pro_tour = args.include_pro_tour
        
        for fmt in formats:
            if fmt:
                logger.info(f"Scraping format: {fmt}")
            
            tournaments = await scraper.scrape_tournaments(
                format_filter=fmt,
                start_date=start_date,
                end_date=end_date,
                skip_processed=not args.force_redownload,
                limit=args.limit if len(formats) == 1 else None
            )
            
            # Apply tournament type filters
            filtered_tournaments = []
            for t in tournaments:
                # Check included types
                if included_types and t.tournament_type not in included_types:
                    continue
                # Check excluded types
                if t.tournament_type in excluded_types:
                    continue
                filtered_tournaments.append(t)
            
            if len(filtered_tournaments) < len(tournaments):
                logger.info(f"Filtered from {len(tournaments)} to {len(filtered_tournaments)} tournaments")
            
            all_tournaments.extend(filtered_tournaments)
            
            # Apply overall limit if multiple formats
            if args.limit and len(formats) > 1 and len(all_tournaments) >= args.limit:
                all_tournaments = all_tournaments[:args.limit]
                break
    
    logger.info(f"Found {len(all_tournaments)} tournaments total")
    
    # Show league count if any
    league_count = sum(1 for t in all_tournaments if t.tournament_type == "league")
    if league_count > 0:
        logger.info(f"Including {league_count} league tournaments (will be stored separately)")
    
    # Dry run - just list tournaments
    if args.dry_run:
        logger.info("DRY RUN - Listing tournaments without saving:")
        for t in all_tournaments:
            league_marker = " [LEAGUE]" if t.tournament_type == "league" else ""
            pro_tour_marker = " [PRO TOUR]" if t.pro_tour else ""
            print(f"{t.date.date()} - {t.name} ({t.format}/{t.tournament_type}) "
                  f"- {t.organization} - {len(t.decklists)} decks, "
                  f"{len(t.standings)} standings{league_marker}{pro_tour_marker}")
        return
    
    # Save tournaments
    saver = MeleeDataSaver(args.output)
    scraped = []
    failed = []
    
    for tournament in all_tournaments:
        try:
            if saver.save_tournament(tournament):
                scraped.append(tournament.name)
            else:
                failed.append(tournament.name)
        except Exception as e:
            logger.error(f"Error saving {tournament.name}: {e}")
            failed.append(tournament.name)
    
    # Print summary
    logger.info("=" * 50)
    logger.info(saver.get_stats_summary())
    logger.info(f"Successfully scraped: {len(scraped)}")
    logger.info(f"Failed: {len(failed)}")
    
    # Generate report if requested
    if args.generate_report:
        report_gen = ScrapeReport()
        report_gen.generate_summary_report(all_tournaments, scraped, failed)
        report_gen.generate_csv_report(all_tournaments)


if __name__ == "__main__":
    asyncio.run(main())