import re
from typing import Dict, List
from datetime import datetime, timedelta
import structlog
from src.python.scraper.base_scraper import BaseScraper

logger = structlog.get_logger()

class MTGOScraper(BaseScraper):
    """Scraper pour MTGO (Magic Online)"""
    
    def __init__(self, cache_folder: str, config: Dict):
        super().__init__(cache_folder, config)
        self.base_url = "https://www.mtgo.com"
        
    async def authenticate(self):
        """Pas d'authentification nécessaire pour MTGO"""
        logger.info("MTGO scraper initialized (no auth required)")
        
    async def discover_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Découvrir les tournois MTGO dans une plage de dates"""
        tournament_ids = []
        
        try:
            # MTGO utilise un système de pagination pour les résultats
            page = 1
            max_pages = 10  # Limite de sécurité
            
            while page <= max_pages:
                response = await self.make_request(
                    f"{self.base_url}/en/mtgo/decklists",
                    params={
                        'format': format_name,
                        'page': page,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
                
                html_content = await response.text()
                
                # Parser les liens vers les tournois
                tournament_links = re.findall(r'/en/articles/archive/mtgo-standings/([^"]+)', html_content)
                
                if not tournament_links:
                    break  # Plus de résultats
                    
                tournament_ids.extend(tournament_links)
                page += 1
                
            logger.info("Discovered MTGO tournaments", count=len(tournament_ids))
            
        except Exception as e:
            logger.error("Failed to discover MTGO tournaments", error=str(e))
            
        return tournament_ids
        
    async def fetch_tournament(self, tournament_id: str) -> Dict:
        """Récupérer les données d'un tournoi MTGO"""
        try:
            url = f"{self.base_url}/en/articles/archive/mtgo-standings/{tournament_id}"
            response = await self.make_request(url)
            html_content = await response.text()
            
            # Parser la page HTML
            tournament_data = await self._parse_mtgo_page(html_content, tournament_id, url)
            
            return tournament_data
            
        except Exception as e:
            logger.error("Failed to fetch MTGO tournament", tournament_id=tournament_id, error=str(e))
            return {}
            
    async def _parse_mtgo_page(self, html_content: str, tournament_id: str, url: str) -> Dict:
        """Parser une page de résultats MTGO"""
        try:
            # Extraire les informations du tournoi
            title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
            title = title_match.group(1).strip() if title_match else f"MTGO Tournament {tournament_id}"
            
            # Extraire la date
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html_content)
            date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
            
            # Extraire le format
            format_match = re.search(r'(Modern|Legacy|Standard|Pioneer|Vintage|Pauper)', title, re.IGNORECASE)
            format_name = format_match.group(1) if format_match else "Unknown"
            
            tournament_data = {
                "tournament": {
                    "id": tournament_id,
                    "name": title,
                    "date": f"{date}T00:00:00Z",
                    "format": format_name,
                    "source": "mtgo.com",
                    "url": url
                },
                "decks": [],
                "standings": []
            }
            
            # Parser les decklists
            decklist_sections = re.findall(
                r'<h3[^>]*>([^<]+)</h3>(.*?)(?=<h3|$)', 
                html_content, 
                re.DOTALL
            )
            
            for i, (player_info, decklist_html) in enumerate(decklist_sections):
                deck = await self._parse_mtgo_decklist(player_info, decklist_html, i+1)
                if deck:
                    tournament_data['decks'].append(deck)
                    
            return tournament_data
            
        except Exception as e:
            logger.error("Failed to parse MTGO page", error=str(e))
            return {}
            
    async def _parse_mtgo_decklist(self, player_info: str, decklist_html: str, rank: int) -> Dict:
        """Parser une decklist MTGO individuelle"""
        try:
            # Extraire le nom du joueur
            player_match = re.search(r'([^(]+)', player_info)
            player_name = player_match.group(1).strip() if player_match else f"Player {rank}"
            
            # Extraire le record (wins-losses)
            record_match = re.search(r'\((\d+)-(\d+)\)', player_info)
            wins = int(record_match.group(1)) if record_match else 0
            losses = int(record_match.group(2)) if record_match else 0
            
            deck = {
                "player": player_name,
                "rank": rank,
                "wins": wins,
                "losses": losses,
                "mainboard": [],
                "sideboard": []
            }
            
            # Parser les cartes du mainboard
            mainboard_section = re.search(r'<div[^>]*class="[^"]*deck-list[^"]*"[^>]*>(.*?)(?:<div[^>]*class="[^"]*sideboard|$)', decklist_html, re.DOTALL)
            if mainboard_section:
                cards = re.findall(r'(\d+)\s+([^<\n]+)', mainboard_section.group(1))
                for count, name in cards:
                    deck['mainboard'].append({
                        "name": name.strip(),
                        "count": int(count),
                        "set": "",
                        "number": ""
                    })
                    
            # Parser les cartes du sideboard
            sideboard_section = re.search(r'<div[^>]*class="[^"]*sideboard[^"]*"[^>]*>(.*?)</div>', decklist_html, re.DOTALL)
            if sideboard_section:
                cards = re.findall(r'(\d+)\s+([^<\n]+)', sideboard_section.group(1))
                for count, name in cards:
                    deck['sideboard'].append({
                        "name": name.strip(),
                        "count": int(count),
                        "set": "",
                        "number": ""
                    })
                    
            return deck
            
        except Exception as e:
            logger.error("Failed to parse MTGO decklist", error=str(e))
            return {} 