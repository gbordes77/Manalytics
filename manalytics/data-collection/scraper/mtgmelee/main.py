#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script for collecting data from MTGMelee.
"""

import os
import sys
import argparse
import logging
from mtgmelee_client import MTGMeleeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('mtgmelee_main')

def main():
    parser = argparse.ArgumentParser(description="Data collection from MTGMelee")
    parser.add_argument("--format", help="Game format (standard, modern, etc.)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to retrieve")
    parser.add_argument("--tournament", type=int, help="Tournament ID to retrieve")
    parser.add_argument("--output-dir", help="Output directory for data")
    args = parser.parse_args()
    
    # Determine output directory
    output_dir = args.output_dir
    if not output_dir:
        # Go up two levels from the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        output_dir = os.path.join(base_dir, "data-collection", "raw-cache")
    
    # Create MTGMelee client
    client = MTGMeleeClient()
    
    # Authenticate client
    auth_success = client.authenticate()
    if auth_success:
        logger.info("Authentication successful.")
    else:
        logger.warning("Authentication failed. Using API without authentication.")
    
    # Collect data
    if args.tournament:
        logger.info(f"Retrieving tournament {args.tournament}...")
        tournament_data = client.get_tournament_data(args.tournament)
        if tournament_data:
            success = client.save_tournament_data(tournament_data, output_dir)
            if success:
                logger.info(f"Tournament {args.tournament} successfully saved.")
            else:
                logger.error(f"Failed to save tournament {args.tournament}.")
        else:
            logger.error(f"Failed to retrieve tournament {args.tournament}.")
            return 1
    elif args.format:
        logger.info(f"Retrieving {args.format} tournaments from the last {args.days} days...")
        tournaments = client.get_recent_tournaments(args.format, args.days)
        if tournaments:
            success_count = 0
            failure_count = 0
            
            for tournament in tournaments:
                tournament_id = tournament.get("id")
                if tournament_id:
                    logger.info(f"Retrieving tournament {tournament_id}...")
                    tournament_data = client.get_tournament_data(tournament_id)
                    if tournament_data:
                        success = client.save_tournament_data(tournament_data, output_dir)
                        if success:
                            logger.info(f"Tournament {tournament_id} successfully saved.")
                            success_count += 1
                        else:
                            logger.error(f"Failed to save tournament {tournament_id}.")
                            failure_count += 1
                    else:
                        logger.error(f"Failed to retrieve tournament {tournament_id}.")
                        failure_count += 1
            
            logger.info(f"Retrieval completed: {success_count} tournaments saved, {failure_count} failures.")
            
            if failure_count > 0:
                return 1
        else:
            logger.error(f"No tournaments found for format {args.format} in the last {args.days} days.")
            return 1
    else:
        logger.error("Please specify a format or tournament ID.")
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())