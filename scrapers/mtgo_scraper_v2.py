#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MTGO Tournament Scraper V2
Based on original mtg_decklist_scrapper by fbettega
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone
from dateutil.parser import isoparse
from urllib.parse import urljoin
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DeckItem:
    """Represents a single card in a deck"""
    count: int
    card_name: str


@dataclass
class Deck:
    """Represents a complete deck"""
    date: datetime
    player: str
    result: str
    anchor_uri: str
    mainboard: List[DeckItem] = field(default_factory=list)
    sideboard: List[DeckItem] = field(default_factory=list)


@dataclass
class Tournament:
    """Represents a tournament"""
    name: str
    date: datetime
    uri: str
    formats: str
    json_file: str
    force_redownload: bool = False


@dataclass
class Standing:
    """Represents a player's standing in a tournament"""
    rank: int
    player: str
    points: int
    wins: int
    losses: int
    draws: int
    omwp: float
    gwp: float
    ogwp: float


@dataclass
class RoundItem:
    """Represents a match in a round"""
    player1: str
    player2: str
    result: str


@dataclass
class Round:
    """Represents a tournament round"""
    round_name: str
    matches: List[RoundItem]


@dataclass
class CacheItem:
    """Represents cached tournament data"""
    tournament: Tournament
    decks: List[Deck]
    rounds: Optional[List[Round]] = None
    standings: Optional[List[Standing]] = None


class MTGOSettings:
    """Configuration for MTGO scraping"""
    LIST_URL = "https://www.mtgo.com/decklists/{year}/{month}"
    ROOT_URL = "https://www.mtgo.com"
    LEAGUE_REDOWNLOAD_DAYS = 3
    ValidFormats = ["Standard", "Modern", "Pioneer", "Legacy", "Vintage", "Pauper", "Commander"]


class CardNameNormalizer:
    """Normalizes card names for consistency"""
    
    _replacements = {}
    
    @classmethod
    def initialize(cls):
        """Initialize card name replacements"""
        # Add any specific card name normalizations here
        cls._replacements = {
            # Example: "Teferi, Hero of Dominaria": "Teferi, Hero of Dominaria"
        }
    
    @classmethod
    def normalize(cls, name: str) -> str:
        """Normalize a card name"""
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Apply specific replacements
        if name in cls._replacements:
            return cls._replacements[name]
        
        # Remove split card indicators
        if "//" in name:
            # For split cards, just use the first part
            name = name.split("//")[0].strip()
        
        return name


class DeckNormalizer:
    """Normalizes deck data"""
    
    @staticmethod
    def normalize(deck: Deck) -> Deck:
        """Normalize a deck"""
        # Sort mainboard and sideboard by card name
        deck.mainboard.sort(key=lambda x: x.card_name)
        deck.sideboard.sort(key=lambda x: x.card_name)
        return deck


class OrderNormalizer:
    """Reorders decks based on standings and brackets"""
    
    @staticmethod
    def reorder_decks(decks: List[Deck], standings: List[Standing], 
                     bracket: Optional[List[Round]], has_bracket: bool) -> List[Deck]:
        """Reorder decks based on tournament results"""
        if not standings:
            return decks
        
        # Create a mapping of player names to decks
        deck_map = {deck.player: deck for deck in decks}
        
        # Reorder based on standings
        reordered = []
        for standing in standings:
            if standing.player in deck_map:
                reordered.append(deck_map[standing.player])
        
        # Add any remaining decks that weren't in standings
        for deck in decks:
            if deck not in reordered:
                reordered.append(deck)
        
        return reordered


class TournamentList:
    """Handles downloading and parsing tournament lists"""
    
    @staticmethod
    def increment_month(date: datetime) -> datetime:
        """Increment the month, rolling over to the next year if needed."""
        new_month = date.month + 1
        new_year = date.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        return date.replace(year=new_year, month=new_month, day=1)
    
    @staticmethod
    def DL_tournaments(start_date: datetime, end_date: datetime = None) -> List[Tournament]:
        """Download tournaments between start_date and end_date"""
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            tournament_list_url = MTGOSettings.LIST_URL.format(
                year=current_date.year,
                month=f"{current_date.month:02}"
            )
            
            logger.info(f"Fetching tournaments for {current_date.year}-{current_date.month:02}")
            
            try:
                response = requests.get(tournament_list_url, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {tournament_list_url}: {response.status_code}")
                    current_date = TournamentList.increment_month(current_date)
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                tournament_nodes = soup.select("li.decklists-item")
                
                if not tournament_nodes:
                    logger.info(f"No tournaments found for {current_date.year}-{current_date.month:02}")
                    current_date = TournamentList.increment_month(current_date)
                    continue
                
                for tournament_node in tournament_nodes:
                    try:
                        title = tournament_node.select_one("a > div > h3").text.strip()
                        url = tournament_node.select_one("a")["href"]
                        date_string = tournament_node.select_one("a > time")["datetime"]
                        
                        parsed_date = isoparse(date_string).date()
                        url = urljoin(MTGOSettings.ROOT_URL, url)
                        
                        # Extract format from title
                        base_format = title.split()[0]
                        format_name = 'Commander' if base_format == 'Duel' else base_format
                        
                        if format_name not in MTGOSettings.ValidFormats:
                            logger.warning(f"Unknown format in title: {title}")
                            continue
                        
                        tournament = Tournament(
                            name=title,
                            date=parsed_date,
                            uri=url,
                            formats=format_name,
                            json_file=os.path.splitext(os.path.basename(url))[0] + ".json",
                            force_redownload=("league" in title.lower() and
                                            (datetime.now(timezone.utc).date() - parsed_date).days < MTGOSettings.LEAGUE_REDOWNLOAD_DAYS)
                        )
                        
                        results.append(tournament)
                        logger.info(f"Found tournament: {title} ({format_name}) on {parsed_date}")
                        
                    except Exception as e:
                        logger.error(f"Error parsing tournament node: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error fetching tournaments for {current_date}: {e}")
            
            current_date = TournamentList.increment_month(current_date)
        
        # Filter results by date range
        filtered_results = [t for t in results if start_date.date() <= t.date <= end_date.date()]
        return sorted(filtered_results, key=lambda t: t.date, reverse=True)
    
    def get_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """Get detailed tournament data"""
        logger.info(f"Fetching details for: {tournament.name}")
        
        try:
            response = requests.get(tournament.uri, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch tournament details: {response.status_code}")
                return None
            
            html_content = response.text
            html_rows = [line.strip() for line in html_content.splitlines()]
            
            # Find the line containing JSON data
            data_row = next(
                (line for line in html_rows if line.startswith("window.MTGO.decklists.data = ")),
                None
            )
            
            if not data_row:
                logger.error("Could not find JSON data in tournament page")
                return None
            
            # Extract JSON data
            json_data = data_row[29:-1]  # Skip prefix and remove semicolon
            event_json = json.loads(json_data)
            
            # Check for errors
            if "errorCode" in event_json and event_json["errorCode"] == "SERVER_ERROR":
                logger.error("Server error in tournament data")
                return None
            
            # Determine event type
            event_type = "tournament" if "starttime" in event_json else "league"
            logger.info(f"Event type: {event_type}")
            
            # Parse tournament data
            winloss = None
            standings = None
            bracket = None
            
            if event_type == "tournament":
                winloss = TournamentLoader.parse_winloss(event_json)
                standings = TournamentLoader.parse_standing(event_json, winloss)
                bracket = TournamentLoader.parse_bracket(event_json)
            
            # Parse decks
            decks = TournamentLoader.parse_decks(tournament, event_type, winloss, event_json)
            
            if not decks:
                logger.warning("No decks found in tournament")
                return None
            
            # Reorder decks if we have standings
            if standings:
                decks = OrderNormalizer.reorder_decks(decks, standings, bracket, bracket is not None)
            
            logger.info(f"Successfully parsed {len(decks)} decks")
            
            return CacheItem(
                tournament=tournament,
                decks=decks,
                rounds=bracket,
                standings=standings
            )
            
        except Exception as e:
            logger.error(f"Error getting tournament details: {e}")
            return None


class TournamentLoader:
    """Handles parsing tournament data from JSON"""
    
    @staticmethod
    def parse_event_date(event_date_str: str) -> datetime:
        """Parse event date from various formats"""
        try:
            return datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(event_date_str, "%Y-%m-%d")
    
    @staticmethod
    def parse_winloss(event_json: dict) -> Optional[Dict[str, str]]:
        """Parse win/loss records"""
        if "winloss" not in event_json:
            return None
        
        player_winloss = {}
        for winloss in event_json["winloss"]:
            player_id = str(winloss["loginid"])
            wins = winloss["wins"]
            losses = winloss["losses"]
            player_winloss[player_id] = f"{wins}-{losses}"
        
        return player_winloss if player_winloss else None
    
    @staticmethod
    def parse_decks(tournament: Tournament, event_type: str, 
                   winloss: Optional[Dict[str, str]], event_json: dict) -> Optional[List[Deck]]:
        """Parse deck data from JSON"""
        # Get event date
        event_date_str = event_json.get("publish_date") if event_type == "league" else event_json.get("starttime")
        if not event_date_str:
            logger.error("No date found in event data")
            return None
        
        event_date_naive = TournamentLoader.parse_event_date(event_date_str)
        event_date = event_date_naive.replace(tzinfo=timezone.utc)
        
        # Check for decklists
        if "decklists" not in event_json:
            logger.error("No decklists found in event data")
            return None
        
        CardNameNormalizer.initialize()
        decks = []
        rank = 1
        
        for deck_data in event_json["decklists"]:
            try:
                mainboard = []
                sideboard = []
                player = deck_data.get("player", "Unknown")
                player_id = str(deck_data.get("loginid", ""))
                
                # Parse mainboard
                for card in deck_data.get("main_deck", []):
                    name = card["card_attributes"]["card_name"]
                    quantity = int(card["qty"])
                    name_normalized = CardNameNormalizer.normalize(name)
                    mainboard.append(DeckItem(count=quantity, card_name=name_normalized))
                
                # Parse sideboard
                for card in deck_data.get("sideboard_deck", []):
                    name = card["card_attributes"]["card_name"]
                    quantity = int(card["qty"])
                    name_normalized = CardNameNormalizer.normalize(name)
                    sideboard.append(DeckItem(count=quantity, card_name=name_normalized))
                
                # Determine result
                result = ""
                if event_type == "league":
                    wins = deck_data.get("wins", {}).get("wins", "0")
                    result = {
                        "5": "5-0",
                        "4": "4-1",
                        "3": "3-2",
                        "2": "2-1",
                        "1": "1-2",
                        "0": "0-3"
                    }.get(wins, "")
                else:
                    if winloss and player_id in winloss:
                        result = winloss[player_id]
                    else:
                        # Challenge results
                        if rank == 1:
                            result = "1st Place"
                        elif rank == 2:
                            result = "2nd Place"
                        elif rank == 3:
                            result = "3rd Place"
                        else:
                            result = f"{rank}th Place"
                        rank += 1
                
                deck = Deck(
                    date=event_date,
                    player=player,
                    result=result,
                    anchor_uri=f"{tournament.uri}#deck_{player}",
                    mainboard=mainboard,
                    sideboard=sideboard
                )
                
                deck = DeckNormalizer.normalize(deck)
                decks.append(deck)
                
            except Exception as e:
                logger.error(f"Error parsing deck: {e}")
                continue
        
        return decks if decks else None
    
    @staticmethod
    def parse_standing(json_data: dict, winloss: Optional[Dict[str, str]]) -> Optional[List[Standing]]:
        """Parse tournament standings"""
        if "standings" not in json_data:
            return None
        
        standings = []
        
        for standing_data in json_data["standings"]:
            try:
                player = standing_data["login_name"]
                player_id = str(standing_data["loginid"])
                points = int(standing_data["score"])
                rank = int(standing_data["rank"])
                gwp = float(standing_data["gamewinpercentage"])
                ogwp = float(standing_data["opponentgamewinpercentage"])
                omwp = float(standing_data["opponentmatchwinpercentage"])
                
                wins = 0
                losses = 0
                if winloss and player_id in winloss:
                    win_loss = winloss[player_id].split("-")
                    wins = int(win_loss[0])
                    losses = int(win_loss[1])
                
                standings.append(Standing(
                    rank=rank,
                    player=player,
                    points=points,
                    wins=wins,
                    losses=losses,
                    draws=0,
                    omwp=omwp,
                    gwp=gwp,
                    ogwp=ogwp
                ))
                
            except Exception as e:
                logger.error(f"Error parsing standing: {e}")
                continue
        
        return sorted(standings, key=lambda s: s.rank) if standings else None
    
    @staticmethod
    def parse_bracket(json_data: dict) -> Optional[List[Round]]:
        """Parse tournament bracket"""
        if "brackets" not in json_data:
            return None
        
        rounds = []
        
        for bracket in json_data["brackets"]:
            matches = []
            
            for match in bracket["matches"]:
                try:
                    player1 = match["players"][0]["player"]
                    player2 = match["players"][1]["player"]
                    player1_wins = match["players"][0]["wins"]
                    player2_wins = match["players"][1]["wins"]
                    reverse_order = match["players"][1].get("winner", False)
                    
                    if reverse_order:
                        matches.append(RoundItem(
                            player1=player2,
                            player2=player1,
                            result=f"{player2_wins}-{player1_wins}-0"
                        ))
                    else:
                        matches.append(RoundItem(
                            player1=player1,
                            player2=player2,
                            result=f"{player1_wins}-{player2_wins}-0"
                        ))
                        
                except Exception as e:
                    logger.error(f"Error parsing match: {e}")
                    continue
            
            if not matches:
                continue
            
            round_name = "Quarterfinals"
            if len(matches) == 2:
                round_name = "Semifinals"
            elif len(matches) == 1:
                round_name = "Finals"
            
            rounds.append(Round(
                round_name=round_name,
                matches=matches
            ))
        
        valid_brackets = [r for r in rounds if r.round_name in {"Quarterfinals", "Semifinals", "Finals"}]
        return valid_brackets if valid_brackets else None


def main():
    """Main function for testing"""
    logger.info("Starting MTGO scraper")
    
    # Test with recent dates
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)
    
    # Get tournament list
    tournaments = TournamentList.DL_tournaments(start_date, end_date)
    logger.info(f"Found {len(tournaments)} tournaments")
    
    # Get details for first few tournaments
    tournament_list = TournamentList()
    for tournament in tournaments[:3]:
        details = tournament_list.get_tournament_details(tournament)
        if details:
            logger.info(f"Successfully parsed {tournament.name} with {len(details.decks)} decks")
        else:
            logger.warning(f"Failed to parse {tournament.name}")


if __name__ == "__main__":
    main()