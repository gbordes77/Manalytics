#!/usr/bin/env python3
"""
Melee Tournament Scraper Script - Complete Version
Uses the complete Melee scraper with all original functionality
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
import argparse
from typing import List, Dict, Any

from scrapers.melee_scraper_complete import TournamentList, MtgMeleeConstants

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_tournament_data(tournament, details, platform, format_name):
    """Save tournament data in the expected format"""
    
    # Determine output directory
    output_dir = Path(f"data/raw/{platform}/{format_name.lower()}")
    
    # Detect tournament type from name
    tournament_name_lower = tournament.name.lower()
    tournament_type = "other"
    
    # League detection
    if "league" in tournament_name_lower:
        tournament_type = "league"
        output_dir = output_dir / "leagues"
    # RCQ detection
    elif any(x in tournament_name_lower for x in ["rcq", "regional championship qualifier"]):
        tournament_type = "rcq"
        output_dir = output_dir / "rcq"
    # Championship detection
    elif "championship" in tournament_name_lower and "qualifier" not in tournament_name_lower:
        tournament_type = "championship"
        output_dir = output_dir / "championship"
    # Qualifier detection
    elif any(x in tournament_name_lower for x in ["qualifier", "ptq", "mcq"]):
        tournament_type = "qualifier"
        output_dir = output_dir / "qualifier"
    # FNM detection
    elif "fnm" in tournament_name_lower or "friday night" in tournament_name_lower:
        tournament_type = "fnm"
        output_dir = output_dir / "fnm"
    # Prerelease detection
    elif "prerelease" in tournament_name_lower or "pre-release" in tournament_name_lower:
        tournament_type = "prerelease"
        output_dir = output_dir / "prerelease"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    date_str = tournament.date.strftime("%Y%m%d")
    safe_name = "".join(c for c in tournament.name if c.isalnum() or c in " -_").strip()
    safe_name = safe_name.replace(" ", "_")[:100]
    filename = f"{date_str}_{safe_name}_{tournament.id}.json"
    filepath = output_dir / filename
    
    # Check if already exists
    if filepath.exists():
        logger.debug(f"File already exists: {filepath}")
        return filepath, True
    
    # Convert to JSON format
    data = {
        "tournament_info": {
            "id": str(tournament.id),
            "name": tournament.name,
            "date": tournament.date.isoformat(),
            "format": format_name.lower(),
            "tournament_type": tournament_type,
            "organization": tournament.organizer,
            "url": tournament.uri,
            "source": "melee",
            "pro_tour": details.tournament.pro_tour if hasattr(details.tournament, 'pro_tour') else False,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        },
        "standings": [],
        "players": [],
        "round_metadata": []
    }
    
    # Add standings
    if hasattr(details, 'standings') and details.standings:
        for standing in details.standings:
            standing_data = {
                "rank": standing.rank,
                "player": standing.player,
                "points": standing.points,
                "omwp": standing.omwp,
                "gwp": standing.gwp,
                "ogwp": standing.ogwp
            }
            data["standings"].append(standing_data)
    
    # Add decklists
    if hasattr(details, 'decks') and details.decks:
        for deck in details.decks:
            player_data = {
                "rank": deck.rank if hasattr(deck, 'rank') else deck.result,
                "player": deck.player,
                "deck_name": deck.deck.deck_name if hasattr(deck.deck, 'deck_name') else "Unknown",
                "archetype": deck.deck.archetype if hasattr(deck.deck, 'archetype') else "Unknown",
                "mainboard": [],
                "sideboard": []
            }
            
            # Add mainboard
            for item in deck.mainboard:
                player_data["mainboard"].append({
                    "count": item.count,
                    "card_name": item.card_name
                })
            
            # Add sideboard
            for item in deck.sideboard:
                player_data["sideboard"].append({
                    "count": item.count,
                    "card_name": item.card_name
                })
            
            # Add commander if present
            if hasattr(deck, 'commander') and deck.commander:
                for cmd in deck.commander:
                    player_data["commander"] = cmd.card_name
                    break  # Only take first commander
            
            data["players"].append(player_data)
    
    # Add round metadata
    if hasattr(details, 'rounds') and details.rounds:
        for round_info in details.rounds:
            round_data = {
                "round": round_info.round,
                "matches": []
            }
            
            for match in round_info.matches:
                match_data = {
                    "player1": match.player1,
                    "player2": match.player2,
                    "result": match.result,
                    "winner": match.winner,
                    "player1_wins": match.p1_wins,
                    "player2_wins": match.p2_wins
                }
                round_data["matches"].append(match_data)
            
            data["round_metadata"].append(round_data)
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath, False


def main():
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
  
  # Limit number of tournaments
  %(prog)s --format standard --days 7 --limit 10
        """
    )
    
    parser.add_argument("--format", type=str,
                       help="Format to scrape (standard, modern, legacy, etc)")
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days to look back")
    parser.add_argument("--start-date", type=str,
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int,
                       help="Limit number of tournaments to scrape")
    parser.add_argument("--include-leagues", action="store_true",
                       help="Include league tournaments (stored separately)")
    parser.add_argument("--force-redownload", action="store_true",
                       help="Force redownload even if file exists")
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
    
    logger.info(f"Scraping Melee tournaments from {start_date.date()} to {end_date.date()}")
    
    try:
        # Get all tournaments in date range
        logger.info("Fetching tournament list...")
        all_tournaments = TournamentList.DL_tournaments(start_date, end_date)
        logger.info(f"Found {len(all_tournaments)} total tournaments")
        
        # Filter by format if specified
        filtered_tournaments = []
        for tournament in all_tournaments:
            # Skip non-Magic tournaments
            if not hasattr(tournament, 'formats') or not tournament.formats:
                continue
            
            # Check format filter
            if args.format:
                if tournament.formats.lower() != args.format.lower():
                    continue
            
            # Check league filter
            if not args.include_leagues and "league" in tournament.name.lower():
                logger.debug(f"Skipping league: {tournament.name}")
                continue
            
            filtered_tournaments.append(tournament)
        
        logger.info(f"Filtered to {len(filtered_tournaments)} tournaments")
        
        # Apply limit if specified
        if args.limit:
            filtered_tournaments = filtered_tournaments[:args.limit]
            logger.info(f"Limited to {args.limit} tournaments")
        
        # Load tournament details
        tournament_loader = TournamentList()
        saved_count = 0
        skipped_count = 0
        failed_count = 0
        league_count = 0
        
        for i, tournament in enumerate(filtered_tournaments):
            logger.info(f"\nProcessing {i+1}/{len(filtered_tournaments)}: {tournament.name} ({tournament.date})")
            
            try:
                # Get tournament details
                details = tournament_loader.get_tournament_details(tournament)
                
                if not details:
                    logger.warning("  ⚠ No details returned")
                    failed_count += 1
                    continue
                
                # Check if we have any data
                has_decks = hasattr(details, 'decks') and details.decks
                has_standings = hasattr(details, 'standings') and details.standings
                
                if not has_decks and not has_standings:
                    logger.warning("  ⚠ No decks or standings available")
                    failed_count += 1
                    continue
                
                # Save tournament
                filepath, existed = save_tournament_data(
                    tournament, 
                    details, 
                    "melee", 
                    tournament.formats
                )
                
                if existed and not args.force_redownload:
                    logger.info(f"  ⏭ Skipped (already exists): {filepath}")
                    skipped_count += 1
                else:
                    logger.info(f"  ✅ Saved to: {filepath}")
                    if has_decks:
                        logger.info(f"    - {len(details.decks)} decks")
                    if has_standings:
                        logger.info(f"    - {len(details.standings)} standings")
                    if hasattr(details, 'rounds') and details.rounds:
                        logger.info(f"    - {len(details.rounds)} rounds")
                    
                    saved_count += 1
                    
                    if "league" in tournament.name.lower():
                        league_count += 1
                
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
                failed_count += 1
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("Scraping Complete!")
        logger.info(f"  Total processed: {len(filtered_tournaments)}")
        logger.info(f"  Saved: {saved_count}")
        logger.info(f"  Skipped: {skipped_count}")
        logger.info(f"  Failed: {failed_count}")
        
        if league_count > 0:
            logger.info(f"\nNote: {league_count} league tournaments were saved to separate 'leagues' subdirectories")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())