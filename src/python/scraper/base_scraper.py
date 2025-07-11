import asyncio
import aiohttp
import aiofiles
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog

# Import du système de résilience
from ..resilience import CircuitBreaker, RetryHandler, ErrorMonitor

logger = structlog.get_logger()

class BaseScraper(ABC):
    """Classe de base abstraite pour tous les scrapers avec système de résilience intégré"""
    
    def __init__(self, cache_folder: str, config: Dict):
        self.cache_folder = cache_folder
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.get('concurrent_requests', 10))
        
        # Système de résilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60),
            expected_exception=(aiohttp.ClientError, asyncio.TimeoutError, ConnectionError),
            name=f"{self.__class__.__name__}_CB"
        )
        
        self.retry_handler = RetryHandler(
            max_attempts=config.get('max_retries', 3),
            base_delay=config.get('base_delay', 1.0),
            max_delay=config.get('max_delay', 30.0),
            retryable_exceptions=(aiohttp.ClientError, asyncio.TimeoutError, ConnectionError),
            name=f"{self.__class__.__name__}_Retry"
        )
        
        self.error_monitor = ErrorMonitor(
            error_rate_threshold=config.get('error_rate_threshold', 0.1),
            name=f"{self.__class__.__name__}_Monitor"
        )
        
        # Callback d'alerte pour logging
        self.error_monitor.add_alert_callback(self._alert_callback)
        
    def _alert_callback(self, alert_data: Dict[str, Any]):
        """Callback pour les alertes du système de résilience"""
        logger.warning(
            "Resilience Alert",
            alert_type=alert_data['alert_type'],
            component=alert_data['component'],
            message=alert_data['message'],
            severity=alert_data['severity']
        )
        
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
        
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> aiohttp.ClientResponse:
        """Faire une requête HTTP avec système de résilience intégré"""
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        async def _make_request():
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
        
        try:
            # Appliquer circuit breaker puis retry
            async def retry_with_cb():
                return await self.circuit_breaker.call(_make_request)
            
            return await self.retry_handler.call(retry_with_cb)
            
        except Exception as e:
            # Enregistrer l'erreur dans le monitor
            self.error_monitor.record_error(e, "http_request", context={
                'url': url,
                'method': method,
                'circuit_breaker_state': self.circuit_breaker.state.value
            })
            raise
                    
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
    
    def get_resilience_stats(self) -> Dict[str, Any]:
        """Retourner les statistiques de résilience"""
        return {
            'circuit_breaker': self.circuit_breaker.get_stats(),
            'retry_handler': self.retry_handler.get_stats(),
            'error_monitor': self.error_monitor.get_error_summary()
        }
    
    def reset_resilience_stats(self):
        """Réinitialiser les statistiques de résilience"""
        self.circuit_breaker.reset()
        self.retry_handler.reset_stats()
        self.error_monitor.clear_history() 