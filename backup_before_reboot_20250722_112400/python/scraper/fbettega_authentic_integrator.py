# -*- coding: utf-8 -*-
"""
FBettega Authentic Integrator - Reproduction fidèle du script fetch_tournament.py
Intègre tous les scrapers (MTGO, Melee, Topdeck, Manatrader) comme dans l'original
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from dateutil import parser

from .models.base_models import *
from .mtgo_scraper_authentic import MTGOScraper


class Logger:
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log_file = open(log_file, "a", encoding="utf-8")

    def write(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        self.terminal.write(message)
        self.log_file.write(timestamp + message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()


def configure_logging(log_file_path):
    """Configure le logging vers fichier et console comme dans l'original"""
    sys.stdout = Logger(log_file_path)
    sys.stderr = sys.stdout


def sanitize_filename(filename):
    """Replace invalid characters in the filename with underscores."""
    return re.sub(r'[<>:"/\\|?*]', "", filename)


def clean_temp_files(cache_folder: str):
    """Delete all temporary files starting with 'Temp' and ending with '.tmp' in the cache folder."""
    for root, _, files in os.walk(cache_folder):
        for file in files:
            if file.startswith("Temp") and file.endswith(".tmp"):
                temp_file_path = os.path.join(root, file)
                try:
                    os.remove(temp_file_path)
                    print(f"Removed temporary file: {temp_file_path}")
                except Exception as e:
                    print(f"Error removing temporary file {temp_file_path}: {e}")


def run_with_retry(action, max_attempts: int):
    """Retry function avec délai comme dans l'original"""
    retry_count = 1
    while True:
        try:
            return action()
        except Exception as ex:
            if retry_count < max_attempts:
                print(
                    f"-- Error '{str(ex).strip('.')}' during call, retrying ({retry_count + 1}/{max_attempts})"
                )
                retry_count += 1
                time.sleep(5)  # Délai avant retry
            else:
                raise


def update_mtgo_folder(
    cache_root_folder: str, start_date: datetime, end_date: Optional[datetime]
):
    """Update MTGO folder - reproduction fidèle de l'original"""
    cache_folder = os.path.join(cache_root_folder, "mtgo.com")
    clean_temp_files(cache_folder)

    print(f"Downloading tournament list for MTGO")

    # Utiliser le scraper authentique
    scraper = MTGOScraper(cache_folder)
    tournaments = scraper.fetch_tournaments(start_date, end_date)
    tournaments.sort(key=lambda t: t.date)

    for tournament in tournaments:
        target_folder = os.path.join(
            cache_folder,
            str(tournament.date.year),
            f"{tournament.date.month:02d}",
            f"{tournament.date.day:02d}",
        )

        os.makedirs(target_folder, exist_ok=True)

        sanitize_json_file = sanitize_filename(tournament.json_file)
        target_file = os.path.join(target_folder, sanitize_json_file)

        # Skip si le fichier existe déjà (sauf si force_redownload)
        if os.path.exists(target_file) and not tournament.force_redownload:
            continue

        print(f"- Downloading tournament {sanitize_json_file}")

        # Récupérer les détails avec retry
        details = run_with_retry(
            lambda: scraper.fetch_tournament_details(tournament), 5
        )

        if not details:
            print(f"-- Tournament has no data, skipping")
            if not os.listdir(target_folder):
                os.rmdir(target_folder)
            continue

        if not details.decks:
            print(f"-- Tournament has no decks, skipping")
            if not os.listdir(target_folder):
                os.rmdir(target_folder)
            continue

        if all(len(deck.mainboard) == 0 for deck in details.decks):
            print(f"-- Tournament has only empty decks, skipping")
            if not os.listdir(target_folder):
                os.rmdir(target_folder)
            continue

        # Sauvegarder avec fichier temporaire comme dans l'original
        temp_file = os.path.join(cache_folder, f"Temp{sanitize_json_file}.tmp")
        temp_file = sanitize_filename(temp_file)

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(details.to_dict(), f, ensure_ascii=False, indent=2)

        os.replace(temp_file, target_file)


def update_melee_folder(
    cache_root_folder: str, start_date: datetime, end_date: Optional[datetime]
):
    """Update Melee folder - placeholder pour l'instant"""
    cache_folder = os.path.join(cache_root_folder, "melee.gg")
    print(f"Downloading tournament list for Melee (placeholder)")
    # TODO: Implémenter le scraper Melee authentique


def update_topdeck_folder(
    cache_root_folder: str, start_date: datetime, end_date: Optional[datetime]
):
    """Update Topdeck folder - placeholder pour l'instant"""
    cache_folder = os.path.join(cache_root_folder, "topdeck.gg")
    print(f"Downloading tournament list for Topdeck (placeholder)")
    # TODO: Implémenter le scraper Topdeck authentique


def update_manatrader_folder(
    cache_root_folder: str, start_date: datetime, end_date: Optional[datetime]
):
    """Update Manatrader folder - placeholder pour l'instant"""
    cache_folder = os.path.join(cache_root_folder, "manatraders.com")
    print(f"Downloading tournament list for Manatrader (placeholder)")
    # TODO: Implémenter le scraper Manatrader authentique


def main():
    """Main function - reproduction fidèle de l'original"""
    configure_logging("log_scraping.txt")

    # Configure argparse
    arg_parser = argparse.ArgumentParser(
        description="MTGO Decklist Cache Updater - Authentic FBettega Reproduction"
    )
    arg_parser.add_argument("cache_folder", type=str, help="Path to the cache folder.")
    arg_parser.add_argument(
        "start_date",
        type=str,
        nargs="?",
        help="Start date in YYYY-MM-DD format. Defaults to 7 days ago.",
        default=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    )
    arg_parser.add_argument(
        "end_date",
        type=str,
        nargs="?",
        help="End date in YYYY-MM-DD format. Defaults to today.",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    arg_parser.add_argument(
        "source",
        type=str,
        nargs="?",
        help="Source type: 'mtgo', 'melee', 'topdeck','manatrader', or 'all'. Defaults to 'all'.",
        default="all",
    )
    arg_parser.add_argument(
        "leagues",
        type=str,
        nargs="?",
        help="Include leagues? Use 'keepleague' or 'skipleagues'. Defaults to 'keepleague'.",
        default="keepleague",
    )
    args = arg_parser.parse_args()

    # Convert arguments to variables
    cache_folder = os.path.abspath(args.cache_folder)
    start_date = parser.parse(args.start_date).astimezone(timezone.utc)
    end_date = parser.parse(args.end_date).astimezone(timezone.utc)
    use_mtgo = args.source.lower() in ["mtgo", "all"]
    use_mtg_melee = args.source.lower() in ["melee", "all"]
    use_topdeck = args.source.lower() in ["topdeck", "all"]
    use_manatrader = args.source.lower() in [
        "manatrader"
    ]  # Manatrader seulement si explicitement demandé
    include_leagues = args.leagues.lower() != "skipleagues"

    print(f"Cache folder: {cache_folder}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    print(f"Using MTGO: {use_mtgo}")
    print(f"Using MTG Melee: {use_mtg_melee}")
    print(f"Using Topdeck: {use_topdeck}")
    print(f"Including Leagues: {include_leagues}")

    # Update folders based on source
    if use_mtgo:
        print("Updating MTGO...")
        update_mtgo_folder(cache_folder, start_date, end_date)

    if use_mtg_melee:
        print("Updating MTG Melee...")
        update_melee_folder(cache_folder, start_date, end_date)

    if use_topdeck:
        print("Updating Topdeck...")
        update_topdeck_folder(cache_folder, start_date, end_date)

    if use_manatrader:
        print("Updating Manatrader...")
        update_manatrader_folder(cache_folder, start_date, end_date)


if __name__ == "__main__":
    main()
