"""
Melee.gg Scraper for Manalytics
Scraper pour récupérer les données de tournois depuis melee.gg
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class MeleeScraper(BaseScraper):
    """Scraper pour les données de melee.gg"""
    
    def __init__(self, cache_folder: str, api_config: Dict):
        """
        Initialise le scraper Melee
        
        Args:
            cache_folder: Répertoire de cache
            api_config: Configuration de l'API
        """
        super().__init__(cache_folder, api_config)
        self.base_url = "https://melee.gg"
        self.api_base = "https://api.melee.gg"
        self.session = None
        
    async def authenticate(self):
        """Authentification auprès de l'API Melee"""
        # Pour l'instant, pas d'authentification requise
        # Peut être étendu avec des credentials si nécessaire
        pass
        
    async def fetch_tournament(self, tournament_id: str) -> Optional[Dict]:
        """Récupère les données d'un tournoi"""
        try:
            details = await self.fetch_tournament_details(tournament_id)
            if details:
                decklists = await self.fetch_tournament_decklists(tournament_id)
                details['decklists'] = decklists
                return details
            return None
        except Exception as e:
            self.logger.error(f"Error fetching tournament {tournament_id}: {e}")
            return None
            
    async def search_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Recherche les tournois dans une période donnée"""
        try:
            tournaments = await self.fetch_tournament_list(format_name, 30)  # 30 jours par défaut
            tournament_ids = []
            
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            for tournament in tournaments:
                tournament_date = datetime.fromisoformat(tournament.get('date', ''))
                if start_dt <= tournament_date <= end_dt:
                    tournament_ids.append(tournament.get('id'))
                    
            return tournament_ids
        except Exception as e:
            self.logger.error(f"Error searching tournaments: {e}")
            return []
        
    async def __aenter__(self):
        """Gestionnaire de contexte async - entrée"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gestionnaire de contexte async - sortie"""
        if self.session:
            await self.session.close()
    
    async def fetch_tournament_list(self, 
                                  format_name: str = "Standard",
                                  days_back: int = 30) -> List[Dict]:
        """
        Récupère la liste des tournois récents
        
        Args:
            format_name: Format des tournois (Standard, Modern, etc.)
            days_back: Nombre de jours à remonter
            
        Returns:
            Liste des tournois
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        tournaments = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            # Simuler une requête API (remplacer par la vraie API)
            url = f"{self.api_base}/tournaments"
            params = {
                'format': format_name,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'limit': 100
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tournaments = data.get('tournaments', [])
                else:
                    logger.warning(f"Failed to fetch tournaments: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching tournament list: {e}")
            # Fallback avec des données d'exemple
            tournaments = self._get_fallback_tournaments(format_name)
        
        return tournaments
    
    async def fetch_tournament_details(self, tournament_id: str) -> Dict:
        """
        Récupère les détails d'un tournoi spécifique
        
        Args:
            tournament_id: ID du tournoi
            
        Returns:
            Détails du tournoi
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            url = f"{self.api_base}/tournaments/{tournament_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Failed to fetch tournament {tournament_id}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching tournament {tournament_id}: {e}")
            return {}
    
    async def fetch_tournament_decklists(self, tournament_id: str) -> List[Dict]:
        """
        Récupère les decklists d'un tournoi
        
        Args:
            tournament_id: ID du tournoi
            
        Returns:
            Liste des decklists
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            url = f"{self.api_base}/tournaments/{tournament_id}/decklists"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('decklists', [])
                else:
                    logger.warning(f"Failed to fetch decklists for {tournament_id}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching decklists for {tournament_id}: {e}")
            return []
    
    async def scrape_format_data(self, 
                               format_name: str = "Standard",
                               days_back: int = 30) -> Dict:
        """
        Scrape les données complètes d'un format
        
        Args:
            format_name: Format à scraper
            days_back: Nombre de jours à remonter
            
        Returns:
            Données complètes du format
        """
        logger.info(f"Starting scrape for {format_name} format ({days_back} days)")
        
        # Récupérer la liste des tournois
        tournaments = await self.fetch_tournament_list(format_name, days_back)
        
        all_decklists = []
        tournament_details = []
        
        # Traiter chaque tournoi
        for tournament in tournaments:
            tournament_id = tournament.get('id')
            if not tournament_id:
                continue
                
            # Récupérer les détails du tournoi
            details = await self.fetch_tournament_details(tournament_id)
            if details:
                tournament_details.append(details)
            
            # Récupérer les decklists
            decklists = await self.fetch_tournament_decklists(tournament_id)
            for decklist in decklists:
                decklist['tournament_id'] = tournament_id
                decklist['tournament_name'] = tournament.get('name', 'Unknown')
                decklist['date'] = tournament.get('date', datetime.now().isoformat())
                all_decklists.append(decklist)
            
            # Pause pour éviter la surcharge
            await asyncio.sleep(0.5)
        
        result = {
            'format': format_name,
            'scrape_date': datetime.now().isoformat(),
            'days_back': days_back,
            'tournaments': tournament_details,
            'decklists': all_decklists,
            'total_tournaments': len(tournament_details),
            'total_decklists': len(all_decklists)
        }
        
        logger.info(f"Scrape completed: {len(tournament_details)} tournaments, {len(all_decklists)} decklists")
        return result
    
    def _get_fallback_tournaments(self, format_name: str) -> List[Dict]:
        """
        Données de fallback en cas d'échec de l'API
        
        Args:
            format_name: Format demandé
            
        Returns:
            Liste de tournois d'exemple
        """
        return [
            {
                'id': 'melee_001',
                'name': f'{format_name} Weekly #1',
                'date': (datetime.now() - timedelta(days=7)).isoformat(),
                'format': format_name,
                'participants': 64
            },
            {
                'id': 'melee_002', 
                'name': f'{format_name} Weekly #2',
                'date': (datetime.now() - timedelta(days=14)).isoformat(),
                'format': format_name,
                'participants': 48
            },
            {
                'id': 'melee_003',
                'name': f'{format_name} Monthly',
                'date': (datetime.now() - timedelta(days=21)).isoformat(),
                'format': format_name,
                'participants': 128
            }
        ]
    
    def save_to_cache(self, data: Dict, filename: str) -> str:
        """
        Sauvegarde les données dans le cache
        
        Args:
            data: Données à sauvegarder
            filename: Nom du fichier
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if not self.cache_folder:
            return ""
        
        cache_path = Path(self.cache_folder)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        file_path = cache_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Data saved to cache: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            return ""
    
    def load_from_cache(self, filename: str) -> Optional[Dict]:
        """
        Charge les données depuis le cache
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Données chargées ou None
        """
        if not self.cache_folder:
            return None
        
        file_path = Path(self.cache_folder) / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Data loaded from cache: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None
    
    async def scrape_with_cache(self, 
                              format_name: str = "Standard",
                              days_back: int = 30,
                              cache_hours: int = 24) -> Dict:
        """
        Scrape avec gestion du cache
        
        Args:
            format_name: Format à scraper
            days_back: Nombre de jours à remonter
            cache_hours: Durée de validité du cache en heures
            
        Returns:
            Données scrapées (depuis cache ou API)
        """
        cache_filename = f"melee_{format_name.lower()}_{days_back}days.json"
        
        # Vérifier le cache
        cached_data = self.load_from_cache(cache_filename)
        if cached_data:
            scrape_date = datetime.fromisoformat(cached_data.get('scrape_date', ''))
            if datetime.now() - scrape_date < timedelta(hours=cache_hours):
                logger.info(f"Using cached data for {format_name}")
                return cached_data
        
        # Scraper de nouvelles données
        data = await self.scrape_format_data(format_name, days_back)
        
        # Sauvegarder dans le cache
        self.save_to_cache(data, cache_filename)
        
        return data 