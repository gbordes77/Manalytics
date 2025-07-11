import os
from typing import Dict, List
from datetime import datetime
import structlog
from src.python.scraper.base_scraper import BaseScraper

logger = structlog.get_logger()

class TopdeckScraper(BaseScraper):
    """Scraper pour Topdeck"""
    
    def __init__(self, cache_folder: str, config: Dict):
        super().__init__(cache_folder, config)
        self.api_key = None
        self.base_url = "https://topdeck.gg/api"
        
    async def authenticate(self):
        """Charger la clé API Topdeck"""
        try:
            api_key_file = self.config.get('api_key_file')
            if not api_key_file or not os.path.exists(api_key_file):
                logger.warning("No Topdeck API key found")
                return
                
            with open(api_key_file, 'r') as f:
                self.api_key = f.read().strip()
                
            if self.api_key:
                logger.info("Topdeck API key loaded successfully")
            else:
                logger.error("Empty Topdeck API key")
                
        except Exception as e:
            logger.error("Failed to load Topdeck API key", error=str(e))
            
    async def discover_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Découvrir les tournois Topdeck dans une plage de dates"""
        tournament_ids = []
        
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            params = {
                'format': format_name,
                'start_date': start_date,
                'end_date': end_date,
                'status': 'completed',
                'limit': 100
            }
            
            response = await self.make_request(
                f"{self.base_url}/tournaments",
                headers=headers,
                params=params
            )
            
            data = await response.json()
            
            for tournament in data.get('data', []):
                tournament_ids.append(str(tournament['id']))
                
            logger.info("Discovered Topdeck tournaments", count=len(tournament_ids))
            
        except Exception as e:
            logger.error("Failed to discover Topdeck tournaments", error=str(e))
            
        return tournament_ids
        
    async def fetch_tournament(self, tournament_id: str) -> Dict:
        """Récupérer les données d'un tournoi Topdeck"""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Récupérer les métadonnées du tournoi
            tournament_response = await self.make_request(
                f"{self.base_url}/tournaments/{tournament_id}",
                headers=headers
            )
            tournament_data = await tournament_response.json()
            
            # Récupérer les decklists
            decklists_response = await self.make_request(
                f"{self.base_url}/tournaments/{tournament_id}/decklists",
                headers=headers
            )
            decklists_data = await decklists_response.json()
            
            # Formater selon le schéma MTGODecklistCache
            formatted_data = await self._format_tournament_data(tournament_data, decklists_data)
            
            return formatted_data
            
        except Exception as e:
            logger.error("Failed to fetch Topdeck tournament", tournament_id=tournament_id, error=str(e))
            return {}
            
    async def _format_tournament_data(self, tournament_data: Dict, decklists_data: Dict) -> Dict:
        """Formater les données selon le schéma MTGODecklistCache"""
        
        tournament = tournament_data.get('data', {})
        
        formatted = {
            "tournament": {
                "id": str(tournament['id']),
                "name": tournament['name'],
                "date": tournament['start_date'],
                "format": tournament.get('format', 'Unknown'),
                "source": "topdeck.gg",
                "url": f"https://topdeck.gg/tournament/{tournament['id']}"
            },
            "decks": [],
            "standings": []
        }
        
        # Traiter chaque decklist
        for decklist in decklists_data.get('data', []):
            deck = await self._parse_decklist(decklist)
            if deck:
                formatted['decks'].append(deck)
                
        return formatted
        
    async def _parse_decklist(self, decklist_data: Dict) -> Dict:
        """Parser une decklist Topdeck"""
        try:
            deck = {
                "player": decklist_data.get('player_name', 'Unknown'),
                "rank": decklist_data.get('rank'),
                "wins": decklist_data.get('wins', 0),
                "losses": decklist_data.get('losses', 0),
                "mainboard": [],
                "sideboard": []
            }
            
            # Parser le mainboard
            for card in decklist_data.get('mainboard', []):
                deck['mainboard'].append({
                    "name": card['name'],
                    "count": card['quantity'],
                    "set": card.get('set_code', ''),
                    "number": card.get('collector_number', '')
                })
                
            # Parser le sideboard
            for card in decklist_data.get('sideboard', []):
                deck['sideboard'].append({
                    "name": card['name'],
                    "count": card['quantity'],
                    "set": card.get('set_code', ''),
                    "number": card.get('collector_number', '')
                })
                
            return deck
            
        except Exception as e:
            logger.error("Failed to parse Topdeck decklist", error=str(e))
            return {} 