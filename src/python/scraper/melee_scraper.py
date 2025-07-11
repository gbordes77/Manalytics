import json
import os
from typing import Dict, List
from datetime import datetime, timedelta
import structlog
from src.python.scraper.base_scraper import BaseScraper

logger = structlog.get_logger()

class MeleeScraper(BaseScraper):
    """Scraper pour Melee.gg"""
    
    def __init__(self, cache_folder: str, config: Dict):
        super().__init__(cache_folder, config)
        self.auth_token = None
        self.base_url = "https://melee.gg"
        
    async def authenticate(self):
        """Authentification sur Melee.gg"""
        try:
            login_file = self.config.get('login_file')
            if not login_file or not os.path.exists(login_file):
                logger.warning("No Melee credentials found, skipping authentication")
                return
                
            with open(login_file, 'r') as f:
                credentials = json.load(f)
                
            login_data = {
                'email': credentials['login'],
                'password': credentials['mdp']
            }
            
            response = await self.make_request(
                f"{self.base_url}/api/auth/login",
                method="POST",
                json=login_data
            )
            
            response_data = await response.json()
            self.auth_token = response_data.get('token')
            
            if self.auth_token:
                logger.info("Successfully authenticated with Melee.gg")
            else:
                logger.error("Failed to get auth token from Melee.gg")
                
        except Exception as e:
            logger.error("Melee authentication failed", error=str(e))
            
    async def discover_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Découvrir les tournois Melee dans une plage de dates"""
        tournament_ids = []
        
        try:
            # Construire les paramètres de recherche
            params = {
                'format': format_name.lower(),
                'start_date': start_date,
                'end_date': end_date,
                'status': 'completed'
            }
            
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
                
            response = await self.make_request(
                f"{self.base_url}/api/tournaments/search",
                headers=headers,
                params=params
            )
            
            data = await response.json()
            
            for tournament in data.get('tournaments', []):
                tournament_ids.append(tournament['id'])
                
            logger.info("Discovered Melee tournaments", count=len(tournament_ids))
            
        except Exception as e:
            logger.error("Failed to discover Melee tournaments", error=str(e))
            
        return tournament_ids
        
    async def fetch_tournament(self, tournament_id: str) -> Dict:
        """Récupérer les données d'un tournoi Melee"""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
                
            # Récupérer les métadonnées du tournoi
            tournament_response = await self.make_request(
                f"{self.base_url}/api/tournament/{tournament_id}",
                headers=headers
            )
            tournament_data = await tournament_response.json()
            
            # Récupérer les standings/decklists
            standings_response = await self.make_request(
                f"{self.base_url}/api/tournament/{tournament_id}/standings",
                headers=headers
            )
            standings_data = await standings_response.json()
            
            # Formater selon le schéma MTGODecklistCache
            formatted_data = await self._format_tournament_data(tournament_data, standings_data)
            
            return formatted_data
            
        except Exception as e:
            logger.error("Failed to fetch Melee tournament", tournament_id=tournament_id, error=str(e))
            return {}
            
    async def _format_tournament_data(self, tournament_data: Dict, standings_data: Dict) -> Dict:
        """Formater les données selon le schéma MTGODecklistCache"""
        
        # Structure de base
        formatted = {
            "tournament": {
                "id": tournament_data['id'],
                "name": tournament_data['name'],
                "date": tournament_data['start_date'],
                "format": tournament_data.get('format', 'Unknown'),
                "source": "melee.gg",
                "url": f"https://melee.gg/Tournament/View/{tournament_data['id']}"
            },
            "decks": [],
            "standings": standings_data.get('standings', []),
            "brackets": standings_data.get('brackets', [])
        }
        
        # Traiter chaque deck
        for standing in standings_data.get('standings', []):
            if 'decklist' in standing and standing['decklist']:
                deck = await self._parse_decklist(standing)
                if deck:
                    formatted['decks'].append(deck)
                    
        return formatted
        
    async def _parse_decklist(self, standing: Dict) -> Dict:
        """Parser une decklist Melee"""
        try:
            decklist_data = standing['decklist']
            
            deck = {
                "player": standing.get('player_name', 'Unknown'),
                "rank": standing.get('rank'),
                "wins": standing.get('wins', 0),
                "losses": standing.get('losses', 0),
                "mainboard": [],
                "sideboard": []
            }
            
            # Parser le mainboard
            for card in decklist_data.get('mainboard', []):
                deck['mainboard'].append({
                    "name": card['name'],
                    "count": card['quantity'],
                    "set": card.get('set', ''),
                    "number": card.get('collector_number', '')
                })
                
            # Parser le sideboard
            for card in decklist_data.get('sideboard', []):
                deck['sideboard'].append({
                    "name": card['name'],
                    "count": card['quantity'],
                    "set": card.get('set', ''),
                    "number": card.get('collector_number', '')
                })
                
            return deck
            
        except Exception as e:
            logger.error("Failed to parse Melee decklist", error=str(e))
            return {} 