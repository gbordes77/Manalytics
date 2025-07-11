import asyncio
import aiohttp
import aiofiles
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

class BaseScraper(ABC):
    """Classe de base abstraite pour tous les scrapers"""
    
    def __init__(self, cache_folder: str, config: Dict):
        self.cache_folder = cache_folder
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.get('concurrent_requests', 10))
        
    async def __aenter__(self):
        """Context manager entry"""
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
        self.session = aiohttp.ClientSession(timeout=timeout)
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def authenticate(self):
        """Méthode d'authentification à implémenter par chaque scraper"""
        pass
        
    @abstractmethod
    async def fetch_tournament(self, tournament_id: str) -> Dict:
        """Récupérer les données d'un tournoi"""
        pass
        
    @abstractmethod
    async def discover_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Découvrir les tournois dans une plage de dates"""
        pass
        
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> aiohttp.ClientResponse:
        """Faire une requête HTTP avec retry automatique"""
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        async with self.semaphore:
            await asyncio.sleep(self.config.get('rate_limit_delay', 0.5))
            
            if method.upper() == "GET":
                async with self.session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    return response
            elif method.upper() == "POST":
                async with self.session.post(url, **kwargs) as response:
                    response.raise_for_status()
                    return response
                    
    async def save_tournament(self, data: Dict, source: str):
        """Sauvegarder les données d'un tournoi dans le cache"""
        try:
            date = datetime.fromisoformat(data['tournament']['date'].replace('Z', '+00:00'))
            path = f"{self.cache_folder}/raw/{source}/{date.year}/{date.month:02d}/{date.day:02d}/"
            os.makedirs(path, exist_ok=True)
            
            filename = f"{path}/tournament_{data['tournament']['id']}.json"
            
            # Validation basique
            if not self._validate_tournament_data(data):
                logger.warning("Invalid tournament data", tournament_id=data.get('tournament', {}).get('id'))
                return False
                
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
                
            logger.info("Tournament saved", filename=filename, tournament_id=data['tournament']['id'])
            return True
            
        except Exception as e:
            logger.error("Failed to save tournament", error=str(e), tournament_id=data.get('tournament', {}).get('id'))
            return False
            
    def _validate_tournament_data(self, data: Dict) -> bool:
        """Valider la structure des données du tournoi"""
        required_fields = ['tournament', 'decks']
        
        for field in required_fields:
            if field not in data:
                return False
                
        tournament = data['tournament']
        required_tournament_fields = ['id', 'name', 'date', 'format']
        
        for field in required_tournament_fields:
            if field not in tournament:
                return False
                
        # Vérifier que les decks ont la structure minimale
        for deck in data['decks']:
            if 'player' not in deck or 'mainboard' not in deck:
                return False
                
        return True
        
    async def fetch_date_range(self, format_name: str, start_date: str, end_date: str) -> List[Dict]:
        """Récupérer tous les tournois dans une plage de dates"""
        tournaments = []
        
        try:
            tournament_ids = await self.discover_tournaments(format_name, start_date, end_date)
            logger.info("Discovered tournaments", count=len(tournament_ids), format=format_name)
            
            for tournament_id in tournament_ids:
                try:
                    tournament_data = await self.fetch_tournament(tournament_id)
                    if tournament_data:
                        tournaments.append(tournament_data)
                        await self.save_tournament(tournament_data, self.__class__.__name__.lower().replace('scraper', ''))
                        
                except Exception as e:
                    logger.error("Failed to fetch tournament", tournament_id=tournament_id, error=str(e))
                    continue
                    
        except Exception as e:
            logger.error("Failed to fetch date range", format=format_name, error=str(e))
            
        return tournaments 