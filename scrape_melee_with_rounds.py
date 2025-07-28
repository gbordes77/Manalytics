#!/usr/bin/env python3
"""
Enhanced Melee scraper that includes Round Standings data.
This allows us to extract match-by-match data for the matchup matrix!
"""

import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeleeRoundScraper:
    """Scraper for Melee.gg with Round Standings support"""
    
    def __init__(self):
        self.base_url = "https://melee.gg"
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://melee.gg',
            'Referer': 'https://melee.gg/'
        })
    
    def get_round_standings(self, tournament_id: int) -> Optional[List[Dict]]:
        """
        Get round-by-round standings for a tournament.
        This is the KEY endpoint that contains match data!
        """
        url = f"{self.api_base}/Standing/GetRoundStandings"
        
        # Based on the payload structure shown in the image
        payload = {
            "draw": "1",
            "columns[0][data]": "Rank",
            "columns[1][data]": "Player", 
            "columns[2][data]": "Decklists",
            "columns[3][data]": "MatchRecord",
            "columns[4][data]": "GameRecord",
            "columns[5][data]": "Points",
            "columns[6][data]": "OpponentMatchWinPercentage",
            "columns[7][data]": "TeamGamesWinPercentage",
            "columns[8][data]": "OpponentGameWinPercentage",
            "start": "0",
            "length": "25",
            "search[value]": "",
            "search[regex]": "false",
            "tournamentId": str(tournament_id),
            "roundId": "{roundId}"  # Will be replaced for each round
        }
        
        all_rounds = []
        
        # Get tournament info first to know how many rounds
        tournament_info = self.get_tournament_info(tournament_id)
        if not tournament_info:
            return None
            
        num_rounds = tournament_info.get('NumberOfRounds', 0)
        logger.info(f"🎲 Tournament has {num_rounds} rounds")
        
        # Get standings for each round
        for round_num in range(1, num_rounds + 1):
            round_payload = payload.copy()
            round_payload["roundId"] = str(round_num)
            
            try:
                response = self.session.post(url, data=round_payload)
                response.raise_for_status()
                
                round_data = response.json()
                
                if round_data.get('data'):
                    logger.info(f"  Round {round_num}: {len(round_data['data'])} players")
                    all_rounds.append({
                        'round': round_num,
                        'standings': round_data['data']
                    })
                
                time.sleep(0.5)  # Rate limit
                
            except Exception as e:
                logger.error(f"Error getting round {round_num}: {e}")
        
        return all_rounds
    
    def get_tournament_info(self, tournament_id: int) -> Optional[Dict]:
        """Get basic tournament information"""
        url = f"{self.api_base}/Tournament/GetTournament"
        
        payload = {
            "tournamentId": str(tournament_id)
        }
        
        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting tournament info: {e}")
            return None
    
    def get_decklists(self, tournament_id: int) -> List[Dict]:
        """Get decklists for a tournament"""
        url = f"{self.api_base}/Decklist/GetDecklistsByTournamentId"
        
        payload = {
            "tournamentId": str(tournament_id),
            "start": "0",
            "length": "1000",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Error getting decklists: {e}")
            return []
    
    def reconstruct_matches(self, round_standings: List[Dict], decklists: List[Dict]) -> List[Dict]:
        """
        Reconstruct match pairings from round standings.
        Swiss pairing means players with same record play each other.
        """
        matches = []
        
        # Create player -> decklist mapping
        player_decks = {}
        for deck in decklists:
            player = deck.get('PlayerName', '').strip()
            if player:
                player_decks[player] = deck.get('DeckName', 'Unknown')
        
        # Process each round
        for round_data in round_standings:
            round_num = round_data['round']
            standings = round_data['standings']
            
            # Group by points/record for Swiss pairing
            by_points = {}
            for standing in standings:
                points = standing.get('Points', 0)
                if points not in by_points:
                    by_points[points] = []
                by_points[points].append(standing)
            
            # Within each point group, pair players
            for points, players in by_points.items():
                # Sort by rank for consistent pairing
                players.sort(key=lambda x: x.get('Rank', 999))
                
                # Pair adjacent players (Swiss system)
                for i in range(0, len(players) - 1, 2):
                    if i + 1 < len(players):
                        p1 = players[i]
                        p2 = players[i + 1]
                        
                        p1_name = p1.get('Player', '').strip()
                        p2_name = p2.get('Player', '').strip()
                        
                        # Get match result from MatchRecord
                        p1_record = p1.get('MatchRecord', '')
                        p2_record = p2.get('MatchRecord', '')
                        
                        # Determine winner (higher rank = winner in that round)
                        if p1.get('Rank', 999) < p2.get('Rank', 999):
                            winner = p1_name
                            loser = p2_name
                        else:
                            winner = p2_name
                            loser = p1_name
                        
                        match = {
                            'round': round_num,
                            'player1': p1_name,
                            'player2': p2_name,
                            'deck1': player_decks.get(p1_name, 'Unknown'),
                            'deck2': player_decks.get(p2_name, 'Unknown'),
                            'winner': winner,
                            'p1_record': p1_record,
                            'p2_record': p2_record
                        }
                        
                        matches.append(match)
                        logger.debug(f"Round {round_num}: {p1_name} ({match['deck1']}) vs {p2_name} ({match['deck2']})")
        
        return matches
    
    def scrape_tournament_with_rounds(self, tournament_id: int) -> Dict:
        """Complete tournament scrape with round data"""
        logger.info(f"\n🎯 Scraping tournament {tournament_id} with rounds...")
        
        # Get tournament info
        tournament_info = self.get_tournament_info(tournament_id)
        if not tournament_info:
            return None
        
        # Get decklists
        decklists = self.get_decklists(tournament_id)
        logger.info(f"📋 Found {len(decklists)} decklists")
        
        # Get round standings
        round_standings = self.get_round_standings(tournament_id)
        if not round_standings:
            logger.warning("❌ No round standings found")
            return None
        
        # Reconstruct matches
        matches = self.reconstruct_matches(round_standings, decklists)
        logger.info(f"🎮 Reconstructed {len(matches)} matches")
        
        # Build complete tournament data
        tournament_data = {
            'tournament_id': tournament_id,
            'name': tournament_info.get('Name', 'Unknown'),
            'date': tournament_info.get('StartDate', ''),
            'format': tournament_info.get('FormatDescription', ''),
            'players': tournament_info.get('NumberOfPlayers', 0),
            'rounds': tournament_info.get('NumberOfRounds', 0),
            'decklists': decklists,
            'round_standings': round_standings,
            'matches': matches
        }
        
        return tournament_data
    
    def save_tournament(self, tournament_data: Dict, output_dir: Path):
        """Save tournament data with matches"""
        if not tournament_data:
            return
        
        # Create filename
        date_str = tournament_data['date'][:10] if tournament_data['date'] else 'unknown'
        filename = f"{date_str}_{tournament_data['name'].replace(' ', '_')}_WITH_ROUNDS.json"
        
        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tournament_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved to: {output_path}")
        
        # Summary
        logger.info(f"\n📊 Tournament Summary:")
        logger.info(f"  - Name: {tournament_data['name']}")
        logger.info(f"  - Players: {tournament_data['players']}")
        logger.info(f"  - Rounds: {tournament_data['rounds']}")
        logger.info(f"  - Matches: {len(tournament_data['matches'])}")
        logger.info(f"  - Decklists: {len(tournament_data['decklists'])}")


def main():
    parser = argparse.ArgumentParser(description='Scrape Melee tournaments with round data')
    parser.add_argument('--tournament-id', type=int, required=True, help='Tournament ID to scrape')
    parser.add_argument('--output-dir', type=str, default='data/raw/melee/standard', help='Output directory')
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = MeleeRoundScraper()
    
    # Scrape tournament
    tournament_data = scraper.scrape_tournament_with_rounds(args.tournament_id)
    
    # Save data
    if tournament_data:
        output_dir = Path(args.output_dir)
        scraper.save_tournament(tournament_data, output_dir)
        
        # Show sample matches
        if tournament_data['matches']:
            logger.info("\n🎯 Sample matches:")
            for match in tournament_data['matches'][:5]:
                logger.info(f"  Round {match['round']}: {match['player1']} ({match['deck1']}) vs {match['player2']} ({match['deck2']}) -> Winner: {match['winner']}")
    else:
        logger.error("❌ Failed to scrape tournament")


if __name__ == "__main__":
    main()