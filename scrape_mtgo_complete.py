#!/usr/bin/env python3
"""
MTGO Scraper COMPLET - Récupère les tournois ET les decklists
Version qui récupère vraiment les données des decks
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timedelta
import re
import time
import logging
import argparse
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Formats supportés
SUPPORTED_FORMATS = {
    'standard': 'Standard',
    'modern': 'Modern', 
    'legacy': 'Legacy',
    'vintage': 'Vintage',
    'pioneer': 'Pioneer',
    'pauper': 'Pauper',
    'limited': 'Limited'
}


class MTGOCompleteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.base_url = "https://www.mtgo.com"
        
    def get_tournaments(self, start_date: datetime, end_date: datetime, formats: Set[str]) -> List[dict]:
        """Récupère les tournois pour la période et formats spécifiés"""
        url = f"{self.base_url}/decklists"
        logger.info(f"📋 Fetching tournament list: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to get main page: {e}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les liens de tournois
        tournament_links = []
        
        # Chercher dans la liste des decklists
        decklist_items = soup.find_all('li', class_='decklists-item')
        
        if not decklist_items:
            # Structure alternative
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/decklist/' in href and not href.startswith('/en/'):
                    tournament_links.append({
                        'url': self.base_url + href if not href.startswith('http') else href,
                        'text': link.text.strip(),
                        'href': href
                    })
        else:
            # Parser la structure moderne
            for item in decklist_items:
                link = item.find('a', class_='decklists-link')
                if link:
                    href = link.get('href', '')
                    details = item.find('div', class_='decklists-details')
                    
                    # Extraire le nom et la date
                    if details:
                        name_elem = details.find('h3')
                        date_elem = details.find('time')
                        
                        name = name_elem.text.strip() if name_elem else link.text.strip()
                        date_str = date_elem.get('datetime', '') if date_elem else ''
                        
                        tournament_links.append({
                            'url': self.base_url + href if not href.startswith('http') else href,
                            'text': name,
                            'href': href,
                            'date_str': date_str
                        })
        
        logger.info(f"Found {len(tournament_links)} total tournament links")
        
        # Filtrer par date et format
        filtered_tournaments = []
        
        for t in tournament_links:
            # Extraire la date
            tournament_date = None
            
            # D'abord essayer avec l'attribut datetime
            if 'date_str' in t and t['date_str']:
                try:
                    tournament_date = datetime.fromisoformat(t['date_str'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Sinon parser depuis le texte
            if not tournament_date:
                text = t['text']
                for month in ['January', 'February', 'March', 'April', 'May', 'June', 
                             'July', 'August', 'September', 'October', 'November', 'December']:
                    pattern = rf'{month}\s+(\d+),?\s+(\d{{4}})'
                    match = re.search(pattern, text)
                    if match:
                        month_num = {
                            'January': 1, 'February': 2, 'March': 3, 'April': 4,
                            'May': 5, 'June': 6, 'July': 7, 'August': 8,
                            'September': 9, 'October': 10, 'November': 11, 'December': 12
                        }[month]
                        day = int(match.group(1))
                        year = int(match.group(2))
                        tournament_date = datetime(year, month_num, day)
                        break
            
            if not tournament_date:
                # Essayer de parser depuis l'URL
                url_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', t['href'])
                if url_match:
                    year = int(url_match.group(1))
                    month = int(url_match.group(2))
                    day = int(url_match.group(3))
                    tournament_date = datetime(year, month, day)
            
            if not tournament_date:
                continue
                
            # Vérifier si dans la période
            if not (start_date <= tournament_date <= end_date):
                continue
                
            # Extraire le nom propre
            name = t['text']
            
            # Déterminer le format
            format_name = self._get_format(name)
            
            # Vérifier si le format est désiré
            if formats != {'all'} and format_name not in formats:
                continue
            
            # Extraire l'ID du tournoi depuis l'URL
            tournament_id = t['href'].split('/')[-1]
            
            filtered_tournaments.append({
                'name': name,
                'date': tournament_date.strftime('%Y-%m-%d'),
                'url': t['url'],
                'tournament_id': tournament_id,
                'format': format_name
            })
        
        # Trier par date
        filtered_tournaments.sort(key=lambda x: x['date'])
        
        return filtered_tournaments
    
    async def scrape_tournament_async(self, session: aiohttp.ClientSession, tournament: Dict) -> Optional[Dict]:
        """Version async du scraping d'un tournoi"""
        logger.info(f"🎯 Scraping: {tournament['name']}")
        
        try:
            async with session.get(tournament['url']) as response:
                if response.status != 200:
                    logger.error(f"Failed to get {tournament['name']}: {response.status}")
                    return None
                
                html = await response.text()
                return self._parse_tournament_page(html, tournament)
                
        except Exception as e:
            logger.error(f"Error scraping {tournament['name']}: {e}")
            return None
    
    def _parse_tournament_page(self, html: str, tournament: Dict) -> Optional[Dict]:
        """Parse le HTML d'une page de tournoi"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Structure pour stocker les données
        tournament_data = {
            'source': 'mtgo',
            'format': tournament['format'],
            'name': tournament['name'],
            'date': tournament['date'],
            'url': tournament['url'],
            'tournament_id': tournament['tournament_id'],
            'scraped_at': datetime.now().isoformat(),
            'decklists': []
        }
        
        # Stratégie 1: Chercher la structure moderne avec data-src
        deck_wrappers = soup.find_all('div', class_='deck-group')
        
        if not deck_wrappers:
            # Stratégie 2: Chercher les decks via les joueurs
            player_sections = soup.find_all(['div', 'section'], attrs={'data-player': True})
            
            for section in player_sections:
                player_name = section.get('data-player')
                deck_data = self._extract_deck_from_section(section, player_name)
                if deck_data:
                    tournament_data['decklists'].append(deck_data)
        
        if not tournament_data['decklists']:
            # Stratégie 3: Parser le JSON embarqué si présent
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'decks' in data:
                        for deck in data['decks']:
                            deck_data = self._parse_json_deck(deck)
                            if deck_data:
                                tournament_data['decklists'].append(deck_data)
                except:
                    continue
        
        if not tournament_data['decklists']:
            # Stratégie 4: Méthode classique - chercher les headers de joueurs
            # Patterns communs: "Player Name (Record)", "1st Place - Player", etc.
            player_patterns = [
                re.compile(r'^(.+?)\s*\((\d+-\d+(?:-\d+)?)\)'),  # "Player (3-0)"
                re.compile(r'^(\d+)(?:st|nd|rd|th)\s+Place\s*[-–]\s*(.+)'),  # "1st Place - Player"
                re.compile(r'^(.+?)\s*[-–]\s*(\d+)(?:st|nd|rd|th)\s+Place'),  # "Player - 1st Place"
            ]
            
            # Chercher tous les éléments qui pourraient contenir des noms de joueurs
            for elem in soup.find_all(['h3', 'h4', 'h5', 'div'], string=True):
                text = elem.text.strip()
                
                for pattern in player_patterns:
                    match = pattern.match(text)
                    if match:
                        # Trouvé un joueur, chercher le deck qui suit
                        deck_container = self._find_deck_after_element(elem)
                        if deck_container:
                            if pattern == player_patterns[0]:
                                player_name = match.group(1)
                                record = match.group(2)
                            else:
                                player_name = match.group(2) if match.group(1).isdigit() else match.group(1)
                                record = None
                            
                            deck_data = self._parse_deck_container(deck_container, player_name, record)
                            if deck_data:
                                tournament_data['decklists'].append(deck_data)
                        break
        
        # Si toujours rien, essayer une approche générique
        if not tournament_data['decklists']:
            # Chercher tous les blocs qui ressemblent à des decks
            potential_decks = soup.find_all('div', string=re.compile(r'\d+\s+\w+'))
            for deck_div in potential_decks:
                deck_text = deck_div.text
                if self._looks_like_deck(deck_text):
                    # Essayer de trouver le joueur associé
                    player_name = self._find_player_for_deck(deck_div)
                    deck_data = self._parse_deck_text(deck_text, player_name or "Unknown")
                    if deck_data:
                        tournament_data['decklists'].append(deck_data)
        
        logger.info(f"✅ Found {len(tournament_data['decklists'])} decklists")
        return tournament_data if tournament_data['decklists'] else None
    
    def _extract_deck_from_section(self, section, player_name: str) -> Optional[Dict]:
        """Extrait un deck depuis une section de joueur"""
        mainboard = []
        sideboard = []
        
        # Chercher les cartes du mainboard
        main_section = section.find(['div', 'ul'], class_=['mainboard', 'deck-main'])
        if main_section:
            for card in main_section.find_all(['li', 'div'], class_='card'):
                quantity = card.find(class_='quantity')
                name = card.find(class_='name')
                if quantity and name:
                    mainboard.append({
                        'quantity': int(quantity.text),
                        'name': name.text.strip()
                    })
        
        # Chercher le sideboard
        side_section = section.find(['div', 'ul'], class_=['sideboard', 'deck-side'])
        if side_section:
            for card in side_section.find_all(['li', 'div'], class_='card'):
                quantity = card.find(class_='quantity')
                name = card.find(class_='name')
                if quantity and name:
                    sideboard.append({
                        'quantity': int(quantity.text),
                        'name': name.text.strip()
                    })
        
        if mainboard:
            return {
                'player': player_name,
                'mainboard': mainboard,
                'sideboard': sideboard,
                'archetype': None
            }
        
        return None
    
    def _parse_json_deck(self, deck_data: Dict) -> Optional[Dict]:
        """Parse un deck depuis des données JSON"""
        if not isinstance(deck_data, dict):
            return None
            
        player = deck_data.get('player', 'Unknown')
        mainboard = []
        sideboard = []
        
        # Parser le mainboard
        if 'mainboard' in deck_data:
            for card in deck_data['mainboard']:
                if isinstance(card, dict):
                    mainboard.append({
                        'quantity': card.get('quantity', 1),
                        'name': card.get('name', '')
                    })
        
        # Parser le sideboard
        if 'sideboard' in deck_data:
            for card in deck_data['sideboard']:
                if isinstance(card, dict):
                    sideboard.append({
                        'quantity': card.get('quantity', 1),
                        'name': card.get('name', '')
                    })
        
        if mainboard:
            return {
                'player': player,
                'mainboard': mainboard,
                'sideboard': sideboard,
                'archetype': deck_data.get('archetype')
            }
        
        return None
    
    def _find_deck_after_element(self, element) -> Optional:
        """Trouve le conteneur de deck après un élément (nom de joueur)"""
        # Chercher dans les siblings suivants
        for sibling in element.find_next_siblings():
            if sibling.name in ['div', 'ul', 'pre']:
                text = sibling.text
                if self._looks_like_deck(text):
                    return sibling
                # Si on trouve un autre joueur, arrêter
                if re.match(r'^(.+?)\s*\((\d+-\d+)\)', text.strip()):
                    break
        
        # Chercher dans le parent puis les enfants suivants
        parent = element.parent
        if parent:
            found_self = False
            for child in parent.children:
                if child == element:
                    found_self = True
                    continue
                if found_self and hasattr(child, 'text'):
                    if self._looks_like_deck(child.text):
                        return child
        
        return None
    
    def _looks_like_deck(self, text: str) -> bool:
        """Vérifie si un texte ressemble à une decklist"""
        lines = text.strip().split('\n')
        card_pattern = re.compile(r'^\d+\s+.+$')
        card_count = 0
        
        for line in lines:
            if card_pattern.match(line.strip()):
                card_count += 1
        
        # Au moins 10 cartes pour être considéré comme un deck
        return card_count >= 10
    
    def _find_player_for_deck(self, deck_element) -> Optional[str]:
        """Essaie de trouver le nom du joueur pour un deck"""
        # Chercher dans les éléments précédents
        for elem in deck_element.find_all_previous(['h3', 'h4', 'h5', 'div']):
            text = elem.text.strip()
            if re.match(r'^(.+?)\s*\((\d+-\d+)\)', text):
                match = re.match(r'^(.+?)\s*\((\d+-\d+)\)', text)
                return match.group(1)
        
        return None
    
    def _parse_deck_container(self, container, player_name: str, record: Optional[str] = None) -> Optional[Dict]:
        """Parse un conteneur de deck"""
        text = container.text
        return self._parse_deck_text(text, player_name, record)
    
    def _parse_deck_text(self, text: str, player_name: str, record: Optional[str] = None) -> Optional[Dict]:
        """Parse le texte d'un deck"""
        mainboard = []
        sideboard = []
        current_section = mainboard
        
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Détecter le passage au sideboard
            if 'sideboard' in line.lower():
                current_section = sideboard
                continue
            
            # Parser les cartes
            card_match = re.match(r'^(\d+)\s+(.+)$', line)
            if card_match:
                quantity = int(card_match.group(1))
                card_name = card_match.group(2).strip()
                
                # Nettoyer le nom de la carte
                card_name = re.sub(r'\s*\[.*?\]\s*$', '', card_name)  # Enlever les tags [M21]
                card_name = re.sub(r'\s*\(.*?\)\s*$', '', card_name)  # Enlever les (FUT)
                
                current_section.append({
                    'quantity': quantity,
                    'name': card_name
                })
        
        if mainboard:
            result = {
                'player': player_name,
                'mainboard': mainboard,
                'sideboard': sideboard,
                'archetype': None
            }
            
            if record:
                result['record'] = record
            
            return result
        
        return None
    
    def _get_format(self, name: str) -> str:
        """Détermine le format depuis le nom"""
        name_lower = name.lower()
        
        if 'standard' in name_lower:
            return 'standard'
        elif 'modern' in name_lower:
            return 'modern'
        elif 'legacy' in name_lower:
            return 'legacy'
        elif 'vintage' in name_lower:
            return 'vintage'
        elif 'pioneer' in name_lower:
            return 'pioneer'
        elif 'pauper' in name_lower:
            return 'pauper'
        elif 'limited' in name_lower or 'draft' in name_lower or 'sealed' in name_lower:
            return 'limited'
        else:
            return 'other'
    
    def save_tournament_data(self, tournament_data: Dict) -> bool:
        """Sauvegarde les données d'un tournoi"""
        if not tournament_data or not tournament_data.get('decklists'):
            return False
            
        try:
            # Structure similaire à MTG_decklistcache
            base_dir = Path("data/mtg_decklistcache")
            format_name = tournament_data['format']
            
            # Créer l'arborescence
            format_dir = base_dir / format_name
            format_dir.mkdir(parents=True, exist_ok=True)
            
            # Nom du fichier
            filename = f"{tournament_data['date']}_{tournament_data['tournament_id']}.json"
            
            # Dossier leagues si nécessaire
            if 'league' in tournament_data['name'].lower():
                target_dir = format_dir / 'leagues'
                target_dir.mkdir(exist_ok=True)
            else:
                target_dir = format_dir
            
            filepath = target_dir / filename
            
            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved: {filepath} ({len(tournament_data['decklists'])} decks)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tournament data: {e}")
            return False
    
    async def scrape_tournaments_async(self, tournaments: List[Dict]) -> Tuple[int, int]:
        """Scrape plusieurs tournois en parallèle"""
        connector = aiohttp.TCPConnector(limit=5)  # Limiter les connexions simultanées
        timeout = aiohttp.ClientTimeout(total=60)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
            tasks = []
            for tournament in tournaments:
                task = self.scrape_tournament_async(session, tournament)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        # Sauvegarder les résultats
        success_count = 0
        total_decks = 0
        
        for tournament_data in results:
            if tournament_data:
                if self.save_tournament_data(tournament_data):
                    success_count += 1
                    total_decks += len(tournament_data['decklists'])
        
        return success_count, total_decks


def main():
    parser = argparse.ArgumentParser(description='Scrape MTGO tournaments WITH decklists (Complete version)')
    
    # Arguments de date
    parser.add_argument('--start-date', type=str, 
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD)')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours à partir d\'aujourd\'hui')
    
    # Arguments de format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=list(SUPPORTED_FORMATS.keys()) + ['all'],
                       default=['standard'],
                       help='Format(s) à scraper. Par défaut: standard')
    
    # Limite de tournois
    parser.add_argument('--limit', type=int,
                       help='Limiter le nombre de tournois à scraper')
    
    # Mode async
    parser.add_argument('--async-mode', action='store_true',
                       help='Utiliser le scraping asynchrone (plus rapide)')
    
    args = parser.parse_args()
    
    # Déterminer les dates
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    elif args.days:
        start_date = end_date - timedelta(days=args.days)
    else:
        # Demander la période à l'utilisateur
        print("\n⚠️  Quelle période voulez-vous scraper?")
        print("1. Les 7 derniers jours")
        print("2. Les 30 derniers jours") 
        print("3. Juillet 1-21, 2025")
        print("4. Période personnalisée")
        
        choice = input("\nVotre choix (1-4): ")
        
        if choice == '1':
            start_date = end_date - timedelta(days=7)
        elif choice == '2':
            start_date = end_date - timedelta(days=30)
        elif choice == '3':
            start_date = datetime(2025, 7, 1)
            end_date = datetime(2025, 7, 21)
        else:
            start_str = input("Date de début (YYYY-MM-DD): ")
            end_str = input("Date de fin (YYYY-MM-DD): ")
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
    
    # Formats à scraper
    formats = set(args.format)
    
    logger.info("🎯 MTGO Complete Scraper (avec decklists)")
    logger.info("=" * 60)
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(formats)}")
    if args.limit:
        logger.info(f"🔢 Limite: {args.limit} tournois")
    
    # Confirmer avant de lancer
    confirm = input("\n▶️  Lancer le scraping? (y/n): ")
    if confirm.lower() != 'y':
        logger.info("Annulé.")
        return
    
    scraper = MTGOCompleteScraper()
    
    # Récupérer la liste des tournois
    tournaments = scraper.get_tournaments(start_date, end_date, formats)
    logger.info(f"\n✅ Found {len(tournaments)} tournaments to scrape")
    
    if tournaments:
        # Limiter si demandé
        if args.limit:
            tournaments = tournaments[:args.limit]
            logger.info(f"📊 Limited to {len(tournaments)} tournaments")
        
        # Afficher les tournois trouvés
        logger.info("\n📋 Tournois à scraper:")
        for i, t in enumerate(tournaments[:10], 1):
            logger.info(f"  {i}. {t['date']} - {t['name']}")
        if len(tournaments) > 10:
            logger.info(f"  ... et {len(tournaments) - 10} autres")
        
        # Scraper
        start_time = time.time()
        
        if args.async_mode:
            # Mode async
            logger.info("\n⚡ Mode async activé")
            loop = asyncio.get_event_loop()
            success_count, total_decks = loop.run_until_complete(
                scraper.scrape_tournaments_async(tournaments)
            )
        else:
            # Mode synchrone
            success_count = 0
            total_decks = 0
            
            for i, tournament in enumerate(tournaments, 1):
                logger.info(f"\n[{i}/{len(tournaments)}] Processing {tournament['name']}...")
                
                # Scraper le tournoi
                response = scraper.session.get(tournament['url'])
                if response.status_code == 200:
                    tournament_data = scraper._parse_tournament_page(response.text, tournament)
                    
                    if tournament_data and tournament_data['decklists']:
                        if scraper.save_tournament_data(tournament_data):
                            success_count += 1
                            total_decks += len(tournament_data['decklists'])
                
                # Pause pour ne pas surcharger
                if i < len(tournaments):
                    time.sleep(1)
        
        elapsed = time.time() - start_time
        
        logger.info(f"\n✨ SUMMARY:")
        logger.info(f"✅ Successfully scraped: {success_count}/{len(tournaments)} tournaments")
        logger.info(f"🎴 Total decklists: {total_decks}")
        logger.info(f"⏱️ Time elapsed: {elapsed:.1f} seconds")
        
        if total_decks == 0:
            logger.warning("\n⚠️  Aucune decklist trouvée!")
            logger.warning("Le format de la page MTGO a peut-être changé.")
            logger.warning("Vérifiez test_mtgo_page.html pour analyser la structure.")
    else:
        logger.warning("No tournaments found for the specified criteria")


if __name__ == "__main__":
    main()