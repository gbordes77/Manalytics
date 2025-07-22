#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MTGMelee API Client for the MTG Analytics pipeline.
This module allows retrieving tournament data from the MTGMelee API.
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('mtgmelee_client')

class RateLimiter:
    """Rate limit manager for the MTGMelee API."""
    
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = []
        self.hour_requests = []
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        
        # Clean up old requests
        self.minute_requests = [t for t in self.minute_requests if current_time - t < 60]
        self.hour_requests = [t for t in self.hour_requests if current_time - t < 3600]
        
        # Check limits
        if len(self.minute_requests) >= self.requests_per_minute:
            sleep_time = 60 - (current_time - self.minute_requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit per minute reached. Waiting {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
        
        if len(self.hour_requests) >= self.requests_per_hour:
            sleep_time = 3600 - (current_time - self.hour_requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit per hour reached. Waiting {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
    
    def record_request(self):
        """Record a request."""
        current_time = time.time()
        self.minute_requests.append(current_time)
        self.hour_requests.append(current_time)

class AuthManager:
    """Authentication manager for the MTGMelee API."""
    
    def __init__(self, login_url, token_refresh_url):
        self.login_url = login_url
        self.token_refresh_url = token_refresh_url
        self.token = None
        self.token_expiry = None
    
    def authenticate(self, username, password):
        """Authenticate the user and retrieve a token."""
        try:
            response = requests.post(
                self.login_url,
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                # Assume token expires in 24 hours
                self.token_expiry = datetime.now() + timedelta(hours=24)
                logger.info("Authentication successful.")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False
    
    def refresh_token(self):
        """Refresh the token if necessary."""
        if not self.token or not self.token_expiry or datetime.now() >= self.token_expiry:
            logger.info("Token expired or not set. New authentication required.")
            return False
        
        try:
            response = requests.post(
                self.token_refresh_url,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                # Assume token expires in 24 hours
                self.token_expiry = datetime.now() + timedelta(hours=24)
                logger.info("Token refreshed successfully.")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Error during token refresh: {str(e)}")
            return False
    
    def get_headers(self):
        """Return authentication headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

class MTGMeleeClient:
    """Client for the MTGMelee API."""
    
    def __init__(self, config_path=None):
        """Initialize the MTGMelee client."""
        self.config = self._load_config(config_path)
        self.credentials = self._load_credentials()
        
        api_config = self.config.get("mtgmelee", {}).get("api", {})
        self.base_url = api_config.get("base_url")
        self.endpoints = api_config.get("endpoints", {})
        
        auth_config = api_config.get("auth", {})
        self.auth_manager = AuthManager(
            auth_config.get("login_url"),
            auth_config.get("token_refresh_url")
        )
        
        rate_limit_config = self.config.get("mtgmelee", {}).get("api_config", {}).get("rate_limit", {})
        self.rate_limiter = RateLimiter(
            rate_limit_config.get("requests_per_minute", 60),
            rate_limit_config.get("requests_per_hour", 1000)
        )
        
        self.formats = self.config.get("mtgmelee", {}).get("formats", {})
        self.max_retries = self.config.get("mtgmelee", {}).get("api_config", {}).get("max_retries", 3)
        self.retry_delay = self.config.get("mtgmelee", {}).get("api_config", {}).get("retry_delay", 5)
        self.timeout = self.config.get("mtgmelee", {}).get("api_config", {}).get("timeout", 30)
    
    def _load_config(self, config_path=None):
        """Load configuration from sources.json file."""
        if not config_path:
            # Go up two levels from the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            config_path = os.path.join(base_dir, "config", "sources.json")
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"JSON format error in configuration file: {config_path}")
            return {}
    
    def _load_credentials(self):
        """Load credentials from credentials.json file."""
        # Go up two levels from the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        credentials_path = os.path.join(base_dir, "config", "credentials.json")
        
        try:
            with open(credentials_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Credentials file not found: {credentials_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"JSON format error in credentials file: {credentials_path}")
            return {}
    
    def authenticate(self):
        """Authenticate the client with the provided credentials."""
        if not self.credentials or "mtgmelee" not in self.credentials:
            logger.warning("MTGMelee credentials not found. Using API without authentication.")
            return False
        
        mtgmelee_creds = self.credentials.get("mtgmelee", {})
        username = mtgmelee_creds.get("username")
        password = mtgmelee_creds.get("password")
        
        if not username or not password:
            logger.warning("MTGMelee username or password not found.")
            return False
        
        return self.auth_manager.authenticate(username, password)
    
    def _make_request(self, endpoint, method="GET", params=None, data=None):
        """Make a request to the MTGMelee API with error handling and rate limiting."""
        if not self.base_url:
            logger.error("MTGMelee API base URL not defined.")
            return None
        
        url = urljoin(self.base_url, endpoint)
        headers = self.auth_manager.get_headers()
        
        for attempt in range(self.max_retries):
            try:
                # Wait if necessary to respect rate limits
                self.rate_limiter.wait_if_needed()
                
                # Make the request
                if method == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
                else:
                    logger.error(f"Unsupported method: {method}")
                    return None
                
                # Record the request
                self.rate_limiter.record_request()
                
                # Check the response
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    # Token expired, try to refresh
                    if self.auth_manager.refresh_token():
                        headers = self.auth_manager.get_headers()
                        continue
                    else:
                        # Try to authenticate again
                        if self.authenticate():
                            headers = self.auth_manager.get_headers()
                            continue
                        else:
                            logger.error("Authentication failed after token expiration.")
                            return None
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    
                    # Wait before retrying
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
            except requests.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                
                # Wait before retrying
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        logger.error(f"Failed after {self.max_retries} attempts.")
        return None
    
    def get_tournaments(self, format_id=None, start_date=None, end_date=None, page=1, page_size=100):
        """Get the list of tournaments."""
        endpoint = self.endpoints.get("tournaments")
        if not endpoint:
            logger.error("Endpoint 'tournaments' not defined.")
            return None
        
        params = {"page": page, "pageSize": page_size}
        
        if format_id:
            params["formatId"] = format_id
        
        if start_date:
            params["startDate"] = start_date.isoformat()
        
        if end_date:
            params["endDate"] = end_date.isoformat()
        
        return self._make_request(endpoint, params=params)
    
    def get_tournament_details(self, tournament_id):
        """Get the details of a tournament."""
        endpoint = self.endpoints.get("tournament_details", "").replace("{tournament_id}", str(tournament_id))
        if not endpoint:
            logger.error("Endpoint 'tournament_details' not defined.")
            return None
        
        return self._make_request(endpoint)
    
    def get_tournament_standings(self, tournament_id):
        """Get the standings of a tournament."""
        endpoint = self.endpoints.get("tournament_standings", "").replace("{tournament_id}", str(tournament_id))
        if not endpoint:
            logger.error("Endpoint 'tournament_standings' not defined.")
            return None
        
        return self._make_request(endpoint)
    
    def get_tournament_pairings(self, tournament_id):
        """Get the pairings of a tournament."""
        endpoint = self.endpoints.get("tournament_pairings", "").replace("{tournament_id}", str(tournament_id))
        if not endpoint:
            logger.error("Endpoint 'tournament_pairings' not defined.")
            return None
        
        return self._make_request(endpoint)
    
    def get_tournament_decklists(self, tournament_id):
        """Get the decklists of a tournament."""
        endpoint = self.endpoints.get("tournament_decklists", "").replace("{tournament_id}", str(tournament_id))
        if not endpoint:
            logger.error("Endpoint 'tournament_decklists' not defined.")
            return None
        
        return self._make_request(endpoint)
    
    def get_decklist(self, decklist_id):
        """Get a specific decklist."""
        endpoint = self.endpoints.get("decklist", "").replace("{decklist_id}", str(decklist_id))
        if not endpoint:
            logger.error("Endpoint 'decklist' not defined.")
            return None
        
        return self._make_request(endpoint)
    
    def get_recent_tournaments(self, format_name=None, days=7):
        """Get recent tournaments for a given format."""
        format_id = None
        if format_name:
            format_id = self.formats.get(format_name.lower())
            if not format_id:
                logger.error(f"Unrecognized format: {format_name}")
                return None
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.get_tournaments(format_id=format_id, start_date=start_date, end_date=end_date)
    
    def get_tournament_data(self, tournament_id):
        """Get all data for a tournament (details, standings, pairings, decklists)."""
        details = self.get_tournament_details(tournament_id)
        if not details:
            logger.error(f"Unable to retrieve details for tournament {tournament_id}")
            return None
        
        standings = self.get_tournament_standings(tournament_id)
        pairings = self.get_tournament_pairings(tournament_id)
        decklists_info = self.get_tournament_decklists(tournament_id)
        
        # Get complete decklists
        decklists = []
        if decklists_info:
            for decklist_info in decklists_info:
                decklist_id = decklist_info.get("id")
                if decklist_id:
                    decklist = self.get_decklist(decklist_id)
                    if decklist:
                        decklists.append(decklist)
        
        return {
            "details": details,
            "standings": standings,
            "pairings": pairings,
            "decklists": decklists
        }
    
    def convert_to_unified_format(self, tournament_data):
        """Convert MTGMelee data to unified format."""
        if not tournament_data or "details" not in tournament_data:
            logger.error("Invalid tournament data.")
            return None
        
        details = tournament_data.get("details")
        standings = tournament_data.get("standings", [])
        pairings = tournament_data.get("pairings", [])
        decklists = tournament_data.get("decklists", [])
        
        # Create a dictionary for easy access to standings by player
        standings_dict = {}
        for standing in standings:
            player_id = standing.get("playerId")
            if player_id:
                standings_dict[player_id] = standing
        
        # Create a dictionary for easy access to decklists by player
        decklists_dict = {}
        for decklist in decklists:
            player_id = decklist.get("playerId")
            if player_id:
                decklists_dict[player_id] = decklist
        
        # Create a dictionary for easy access to match results by player
        matches_dict = {}
        for pairing in pairings:
            round_num = pairing.get("round")
            player1_id = pairing.get("player1Id")
            player2_id = pairing.get("player2Id")
            result = pairing.get("result", "")
            winner_id = pairing.get("winnerId")
            
            if player1_id and player2_id:
                # Add the match for player 1
                if player1_id not in matches_dict:
                    matches_dict[player1_id] = []
                
                result1 = "win" if winner_id == player1_id else "loss" if winner_id == player2_id else "draw"
                matches_dict[player1_id].append({
                    "opponent_id": f"mtgmelee-{details.get('id')}-{player2_id}",
                    "result": result1,
                    "round": round_num
                })
                
                # Add the match for player 2
                if player2_id not in matches_dict:
                    matches_dict[player2_id] = []
                
                result2 = "win" if winner_id == player2_id else "loss" if winner_id == player1_id else "draw"
                matches_dict[player2_id].append({
                    "opponent_id": f"mtgmelee-{details.get('id')}-{player1_id}",
                    "result": result2,
                    "round": round_num
                })
        
        # Create the unified format
        unified_data = {
            "tournament_id": f"mtgmelee-{details.get('id')}",
            "source": "MTGMelee",
            "name": details.get("name"),
            "format": details.get("formatName"),
            "date": details.get("startDate", "").split("T")[0],
            "url": f"https://mtgmelee.com/Tournament/View/{details.get('id')}",
            "decks": []
        }
        
        # Add the decks
        for player_id, decklist in decklists_dict.items():
            standing = standings_dict.get(player_id, {})
            matches = matches_dict.get(player_id, [])
            
            # Convert the decklist
            mainboard = []
            sideboard = []
            
            for card in decklist.get("mainboard", []):
                mainboard.append({
                    "card_name": card.get("card", {}).get("name"),
                    "quantity": card.get("quantity")
                })
            
            for card in decklist.get("sideboard", []):
                sideboard.append({
                    "card_name": card.get("card", {}).get("name"),
                    "quantity": card.get("quantity")
                })
            
            unified_data["decks"].append({
                "deck_id": f"mtgmelee-{details.get('id')}-{player_id}",
                "player_name": standing.get("playerName", f"Player{player_id}"),
                "rank": standing.get("rank"),
                "mainboard": mainboard,
                "sideboard": sideboard,
                "matches": matches
            })
        
        return unified_data
    
    def save_tournament_data(self, tournament_data, output_dir=None):
        """Save tournament data in unified format."""
        if not tournament_data:
            logger.error("No tournament data to save.")
            return False
        
        unified_data = self.convert_to_unified_format(tournament_data)
        if not unified_data:
            logger.error("Failed to convert to unified format.")
            return False
        
        if not output_dir:
            # Go up two levels from the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            output_dir = os.path.join(base_dir, "data-collection", "raw-cache")
        
        os.makedirs(output_dir, exist_ok=True)
        
        tournament_id = unified_data.get("tournament_id")
        output_file = os.path.join(output_dir, f"{tournament_id}.json")
        
        try:
            with open(output_file, 'w') as f:
                json.dump(unified_data, f, indent=2)
            logger.info(f"Data saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MTGMelee API Client")
    parser.add_argument("--format", help="Game format (standard, modern, etc.)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to retrieve")
    parser.add_argument("--tournament", type=int, help="Tournament ID to retrieve")
    args = parser.parse_args()
    
    client = MTGMeleeClient()
    client.authenticate()
    
    if args.tournament:
        logger.info(f"Retrieving tournament {args.tournament}...")
        tournament_data = client.get_tournament_data(args.tournament)
        if tournament_data:
            client.save_tournament_data(tournament_data)
    elif args.format:
        logger.info(f"Retrieving {args.format} tournaments from the last {args.days} days...")
        tournaments = client.get_recent_tournaments(args.format, args.days)
        if tournaments:
            for tournament in tournaments:
                tournament_id = tournament.get("id")
                if tournament_id:
                    logger.info(f"Retrieving tournament {tournament_id}...")
                    tournament_data = client.get_tournament_data(tournament_id)
                    if tournament_data:
                        client.save_tournament_data(tournament_data)
    else:
        logger.error("Please specify a format or tournament ID.")