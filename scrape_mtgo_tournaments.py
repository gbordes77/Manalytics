#!/usr/bin/env python3
"""
MTGO Tournament Scraper Script
Scrapes MTGO tournaments and saves them in the expected format
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
import argparse
from typing import List, Dict, Any

from scrapers.mtgo_scraper_v2 import (
    TournamentList, Tournament, CacheItem, Deck, DeckItem,
    Standing, Round, RoundItem
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTGODataSaver:
    """Handles saving MTGO tournament data in the expected format"""
    
    def __init__(self, base_path: str = "data/raw/mtgo"):
        self.base_path = Path(base_path)
    
    def save_tournament(self, cache_item: CacheItem) -> bool:
        """Save tournament data to JSON file"""
        try:
            # Determine format folder
            format_name = cache_item.tournament.formats.lower()
            format_path = self.base_path / format_name
            
            # Check if it's a league and create subfolder
            if "league" in cache_item.tournament.name.lower():
                format_path = format_path / "leagues"
            
            format_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename from tournament name and date
            date_str = cache_item.tournament.date.strftime("%Y%m%d")
            safe_name = "".join(c for c in cache_item.tournament.name if c.isalnum() or c in " -_").strip()
            safe_name = safe_name.replace(" ", "_")
            filename = f"{date_str}_{safe_name}.json"
            filepath = format_path / filename
            
            # Convert to JSON-serializable format
            tournament_data = self._convert_to_dict(cache_item)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
            
            if "league" in cache_item.tournament.name.lower():
                logger.info(f"Saved league to: {filepath}")
            else:
                logger.info(f"Saved tournament to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tournament: {e}")
            return False
    
    def _convert_to_dict(self, cache_item: CacheItem) -> Dict[str, Any]:
        """Convert CacheItem to dictionary format matching existing structure"""
        tournament_dict = {
            "tournament_info": {
                "name": cache_item.tournament.name,
                "date": cache_item.tournament.date.isoformat(),
                "format": cache_item.tournament.formats,
                "url": cache_item.tournament.uri,
                "source": "mtgo"
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


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Scrape MTGO tournaments")
    parser.add_argument("--format", type=str, help="Format to scrape (e.g., standard, modern)")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    parser.add_argument("--limit", type=int, help="Limit number of tournaments to scrape")
    parser.add_argument("--output", type=str, default="data/raw/mtgo", help="Output directory")
    parser.add_argument("--exclude-leagues", action="store_true", help="Exclude league tournaments")
    parser.add_argument("--only-leagues", action="store_true", help="Only scrape league tournaments")
    
    args = parser.parse_args()
    
    # Set up date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=args.days)
    
    logger.info(f"Scraping MTGO tournaments from {start_date.date()} to {end_date.date()}")
    
    # Get tournament list
    tournaments = TournamentList.DL_tournaments(start_date, end_date)
    logger.info(f"Found {len(tournaments)} tournaments total")
    
    # Filter by format if specified
    if args.format:
        format_filter = args.format.lower()
        tournaments = [t for t in tournaments if t.formats.lower() == format_filter]
        logger.info(f"Filtered to {len(tournaments)} {args.format} tournaments")
    
    # Filter leagues based on arguments
    if args.exclude_leagues:
        tournaments = [t for t in tournaments if "league" not in t.name.lower()]
        logger.info(f"Excluded leagues, {len(tournaments)} tournaments remaining")
    elif args.only_leagues:
        tournaments = [t for t in tournaments if "league" in t.name.lower()]
        logger.info(f"Only leagues selected, {len(tournaments)} leagues found")
    
    # Apply limit if specified
    if args.limit:
        tournaments = tournaments[:args.limit]
    
    # Initialize saver
    saver = MTGODataSaver(args.output)
    
    # Process tournaments
    tournament_list = TournamentList()
    success_count = 0
    
    for i, tournament in enumerate(tournaments, 1):
        logger.info(f"Processing {i}/{len(tournaments)}: {tournament.name}")
        
        # Get tournament details
        details = tournament_list.get_tournament_details(tournament)
        
        if details:
            # Save tournament
            if saver.save_tournament(details):
                success_count += 1
            else:
                logger.error(f"Failed to save: {tournament.name}")
        else:
            logger.error(f"Failed to get details for: {tournament.name}")
    
    logger.info(f"Successfully saved {success_count}/{len(tournaments)} tournaments")


if __name__ == "__main__":
    main()