#!/usr/bin/env python3
"""
Topdeck Scraper - Scraper pour MTGTop8 et autres sources
Récupère les données depuis les sites de decklists populaires
"""

import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .base_scraper import BaseScraper

class TopdeckScraper(BaseScraper):
    """Scraper pour MTGTop8 et autres sources de decklists"""
    
    def __init__(self, cache_folder: str, api_config: Dict):
        super().__init__(cache_folder, api_config)
        self.base_url = "https://mtgtop8.com"
        self.api_key = None
        
    async def authenticate(self):
        """Authentification optionnelle pour certaines sources"""
        try:
            # Charger l'API key si disponible
            api_key_file = self.api_config.get('api_key_file', './credentials/topdeck_api.txt')
            try:
                with open(api_key_file, 'r') as f:
                    self.api_key = f.read().strip()
                    self.logger.info("Topdeck API key loaded")
            except FileNotFoundError:
                self.logger.info("No Topdeck API key found, using public access")
                # Créer un fichier d'exemple
                with open(api_key_file, 'w') as f:
                    f.write("YOUR_API_KEY_HERE")
                    
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            
    async def search_tournaments(self, format_name: str, start_date: str, end_date: str) -> List[str]:
        """Recherche les tournois dans une période"""
        tournament_ids = []
        
        try:
            # Convertir les dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Rechercher par pages
            page = 1
            while True:
                params = {
                    'format': self.format_name_to_id(format_name),
                    'date_start': start_dt.strftime('%d/%m/%Y'),
                    'date_end': end_dt.strftime('%d/%m/%Y'),
                    'current_page': page
                }
                
                if self.api_key:
                    params['api_key'] = self.api_key
                    
                async with self.session.get(f'{self.base_url}/search', params=params) as resp:
                    if resp.status != 200:
                        self.logger.error(f"Search failed: {resp.status}")
                        break
                        
                    html_content = await resp.text()
                    
                    # Extraire les IDs des tournois depuis le HTML
                    page_tournament_ids = self.extract_tournament_ids_from_html(html_content)
                    
                    if not page_tournament_ids:
                        break
                        
                    tournament_ids.extend(page_tournament_ids)
                    
                    # Vérifier s'il y a une page suivante
                    if not self.has_next_page(html_content):
                        break
                        
                    page += 1
                    
        except Exception as e:
            self.logger.error(f"Failed to search tournaments: {e}")
            
        return tournament_ids
        
    def format_name_to_id(self, format_name: str) -> str:
        """Convertit le nom du format vers l'ID MTGTop8"""
        format_mapping = {
            'modern': 'MO',
            'legacy': 'LE',
            'vintage': 'VI',
            'standard': 'ST',
            'pioneer': 'PI',
            'pauper': 'PAU',
            'commander': 'EDH'
        }
        return format_mapping.get(format_name.lower(), 'MO')
        
    def extract_tournament_ids_from_html(self, html_content: str) -> List[str]:
        """Extrait les IDs des tournois depuis le HTML"""
        tournament_ids = []
        
        try:
            import re
            
            # Rechercher les liens vers les tournois
            tournament_links = re.findall(r'event\?e=(\d+)', html_content)
            tournament_ids.extend(tournament_links)
            
            # Rechercher dans les formulaires
            form_ids = re.findall(r'name="e" value="(\d+)"', html_content)
            tournament_ids.extend(form_ids)
            
        except Exception as e:
            self.logger.error(f"Failed to extract tournament IDs: {e}")
            
        return list(set(tournament_ids))  # Supprimer les doublons
        
    def has_next_page(self, html_content: str) -> bool:
        """Vérifie s'il y a une page suivante"""
        try:
            return 'Next' in html_content or 'Suivant' in html_content
        except:
            return False
            
    async def fetch_tournament(self, tournament_id: str) -> Optional[Dict]:
        """Récupère les données d'un tournoi"""
        try:
            # URL du tournoi
            url = f"{self.base_url}/event"
            params = {'e': tournament_id}
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    self.logger.error(f"Failed to fetch tournament {tournament_id}: {resp.status}")
                    return None
                    
                html_content = await resp.text()
                
            # Parser le HTML
            tournament_data = self.parse_tournament_html(html_content, tournament_id)
            
            if tournament_data:
                return self.format_tournament_data(tournament_data, tournament_data.get('standings', []))
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to fetch tournament {tournament_id}: {e}")
            return None
            
    def parse_tournament_html(self, html_content: str, tournament_id: str) -> Optional[Dict]:
        """Parse le HTML d'un tournoi"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            tournament_data = {
                'id': tournament_id,
                'name': self.extract_tournament_name(soup),
                'date': self.extract_tournament_date(soup),
                'format': self.extract_tournament_format(soup),
                'type': self.extract_tournament_type(soup),
                'location': self.extract_tournament_location(soup),
                'standings': self.extract_standings(soup)
            }
            
            return tournament_data
            
        except Exception as e:
            self.logger.error(f"Failed to parse tournament HTML: {e}")
            return None
            
    def extract_tournament_name(self, soup) -> str:
        """Extrait le nom du tournoi"""
        try:
            # Rechercher dans les balises de titre
            title_elem = soup.find('h1') or soup.find('h2')
            if title_elem:
                return title_elem.get_text().strip()
                
            # Rechercher dans les métadonnées
            meta_title = soup.find('meta', {'property': 'og:title'})
            if meta_title:
                return meta_title.get('content', '').strip()
                
        except:
            pass
        return "MTGTop8 Tournament"
        
    def extract_tournament_date(self, soup) -> str:
        """Extrait la date du tournoi"""
        try:
            # Rechercher les patterns de date
            import re
            text = soup.get_text()
            
            # Formats de date courants
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
                    
        except:
            pass
        return datetime.now().isoformat()
        
    def extract_tournament_format(self, soup) -> str:
        """Extrait le format du tournoi"""
        try:
            text = soup.get_text().lower()
            
            formats = ['modern', 'legacy', 'vintage', 'standard', 'pioneer', 'pauper', 'commander']
            for fmt in formats:
                if fmt in text:
                    return fmt.title()
                    
        except:
            pass
        return 'Unknown'
        
    def extract_tournament_type(self, soup) -> str:
        """Extrait le type de tournoi"""
        try:
            text = soup.get_text().lower()
            
            if 'grand prix' in text or 'gp' in text:
                return 'Grand Prix'
            elif 'pro tour' in text or 'pt' in text:
                return 'Pro Tour'
            elif 'scg' in text or 'star city' in text:
                return 'SCG'
            elif 'fnm' in text or 'friday night' in text:
                return 'FNM'
            elif 'pptq' in text:
                return 'PPTQ'
            elif 'ptq' in text:
                return 'PTQ'
                
        except:
            pass
        return 'Tournament'
        
    def extract_tournament_location(self, soup) -> str:
        """Extrait la localisation du tournoi"""
        try:
            # Rechercher les informations de localisation
            location_elem = soup.find('span', class_='location') or soup.find('div', class_='location')
            if location_elem:
                return location_elem.get_text().strip()
                
        except:
            pass
        return ''
        
    def extract_standings(self, soup) -> List[Dict]:
        """Extrait les classements et decklists"""
        standings = []
        
        try:
            # Rechercher les liens vers les decklists
            decklist_links = soup.find_all('a', href=lambda x: x and 'deck' in x.lower())
            
            for i, link in enumerate(decklist_links):
                try:
                    # Extraire les informations du lien
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Extraire le rang et le nom du joueur
                    rank = i + 1
                    player_name = self.extract_player_name_from_link(text)
                    
                    standing = {
                        'rank': rank,
                        'player': player_name,
                        'deck_url': href,
                        'wins': 0,  # Non disponible dans MTGTop8
                        'losses': 0,
                        'draws': 0,
                        'deck': {}
                    }
                    
                    standings.append(standing)
                    
                except Exception as e:
                    self.logger.error(f"Failed to parse standing: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to extract standings: {e}")
            
        return standings
        
    def extract_player_name_from_link(self, link_text: str) -> str:
        """Extrait le nom du joueur depuis le texte du lien"""
        try:
            # Nettoyer le texte
            text = link_text.strip()
            
            # Supprimer les patterns courants
            import re
            text = re.sub(r'\(\d+\)', '', text)  # Supprimer (1), (2), etc.
            text = re.sub(r'1st|2nd|3rd|\d+th', '', text)  # Supprimer les rangs
            text = re.sub(r'place', '', text, flags=re.IGNORECASE)
            
            return text.strip()
            
        except:
            return "Unknown"
            
    def format_tournament_data(self, tournament_data: Dict, standings: List[Dict]) -> Dict:
        """Formate les données vers le schéma MTGODecklistCache"""
        
        tournament_info = {
            "ID": str(tournament_data.get('id')),
            "Name": tournament_data.get('name', ''),
            "Date": tournament_data.get('date', datetime.now().isoformat()),
            "Format": tournament_data.get('format', 'Unknown'),
            "Players": len(standings),
            "Rounds": self.estimate_rounds(len(standings)),
            "Type": tournament_data.get('type', 'Tournament'),
            "Source": "mtgtop8",
            "URL": f"{self.base_url}/event?e={tournament_data.get('id')}",
            "Location": tournament_data.get('location', '')
        }
        
        # Formater les standings
        formatted_standings = []
        for standing in standings:
            player_data = {
                "Player": standing.get('player', ''),
                "Rank": standing.get('rank', 0),
                "Points": self.calculate_points(standing),
                "Wins": standing.get('wins', 0),
                "Losses": standing.get('losses', 0),
                "Draws": standing.get('draws', 0),
                "Deck": self._format_deck(standing.get('deck', {}))
            }
            formatted_standings.append(player_data)
            
        return {
            "Tournament": tournament_info,
            "Standings": formatted_standings,
            "Rounds": []
        }
        
    def estimate_rounds(self, num_players: int) -> int:
        """Estime le nombre de rounds"""
        if num_players <= 8:
            return 3
        elif num_players <= 16:
            return 4
        elif num_players <= 32:
            return 5
        elif num_players <= 64:
            return 6
        elif num_players <= 128:
            return 7
        else:
            return 8
            
    def calculate_points(self, standing: Dict) -> int:
        """Calcule les points basés sur le record"""
        wins = standing.get('wins', 0)
        draws = standing.get('draws', 0)
        return wins * 3 + draws 