#!/usr/bin/env python3
"""
MTGO Scraper JSON - Version qui parse le JSON embarqué dans les pages
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
from typing import List, Dict, Set, Optional
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTGOJsonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.base_url = "https://www.mtgo.com"
        
    def get_tournaments_list(self, start_date: datetime, end_date: datetime, 
                           formats: Set[str], include_leagues: bool = False) -> List[Dict]:
        """Récupère la liste des tournois depuis la page d'index"""
        url = f"{self.base_url}/decklists"
        logger.info(f"📋 Fetching tournament list: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to get main page: {e}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        tournaments = []
        
        # Chercher tous les liens de tournois
        for link in soup.find_all('a', href=re.compile(r'/decklist/')):
            href = link.get('href', '')
            text = link.text.strip()
            
            # Parser le nom et la date
            tournament_date = None
            
            # Essayer de parser la date depuis l'URL
            url_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', href)
            if url_match:
                year = int(url_match.group(1))
                month = int(url_match.group(2))
                day = int(url_match.group(3))
                tournament_date = datetime(year, month, day)
            
            if not tournament_date:
                continue
                
            # Vérifier la période
            if not (start_date <= tournament_date <= end_date):
                continue
            
            # Exclure les leagues si demandé
            if not include_leagues and 'league' in text.lower():
                continue
            
            # Déterminer le format
            format_name = self._get_format(text)
            if formats != {'all'} and format_name not in formats:
                continue
            
            # Extraire l'ID du tournoi
            tournament_id = href.split('/')[-1].split('-')[-1]
            
            tournaments.append({
                'name': text,
                'date': tournament_date.strftime('%Y-%m-%d'),
                'url': self.base_url + href,
                'tournament_id': tournament_id,
                'format': format_name,
                'href': href
            })
        
        # Trier par date
        tournaments.sort(key=lambda x: x['date'])
        return tournaments
    
    def scrape_tournament_json(self, tournament: Dict) -> Optional[Dict]:
        """Scrape un tournoi en extrayant le JSON embarqué"""
        logger.info(f"🎯 Scraping: {tournament['name']}")
        
        try:
            response = self.session.get(tournament['url'], timeout=30)
            response.raise_for_status()
            
            # Chercher le JSON dans le HTML
            json_match = re.search(r'window\.MTGO\.decklists\.data\s*=\s*({.*?});', response.text, re.DOTALL)
            
            if not json_match:
                logger.warning(f"No JSON data found for {tournament['name']}")
                return None
            
            # Parser le JSON
            json_data = json.loads(json_match.group(1))
            
            # Convertir au format attendu
            tournament_data = {
                'source': 'mtgo',
                'format': tournament['format'],
                'name': tournament['name'],
                'date': tournament['date'],
                'url': tournament['url'],
                'tournament_id': tournament['tournament_id'],
                'event_id': json_data.get('event_id'),
                'description': json_data.get('description', tournament['name']),
                'scraped_at': datetime.now().isoformat(),
                'decklists': []
            }
            
            # Parser les decklists
            for deck in json_data.get('decklists', []):
                parsed_deck = self._parse_json_deck(deck)
                if parsed_deck:
                    tournament_data['decklists'].append(parsed_deck)
            
            logger.info(f"✅ Found {len(tournament_data['decklists'])} decklists")
            return tournament_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {tournament['name']}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {tournament['name']}: {e}")
            return None
    
    def _parse_json_deck(self, deck_data: Dict) -> Optional[Dict]:
        """Parse un deck depuis le JSON MTGO"""
        player = deck_data.get('player', 'Unknown')
        
        mainboard = []
        sideboard = []
        
        # Parser le mainboard
        for card in deck_data.get('main_deck', []):
            card_info = card.get('card_attributes', {})
            mainboard.append({
                'quantity': int(card.get('qty', 1)),
                'name': card_info.get('card_name', 'Unknown Card')
            })
        
        # Parser le sideboard
        for card in deck_data.get('sideboard_deck', []):
            card_info = card.get('card_attributes', {})
            sideboard.append({
                'quantity': int(card.get('qty', 1)),
                'name': card_info.get('card_name', 'Unknown Card')
            })
        
        # Vérifier que le deck est valide
        main_count = sum(c['quantity'] for c in mainboard)
        side_count = sum(c['quantity'] for c in sideboard)
        
        if main_count < 60:
            logger.warning(f"Deck de {player} a seulement {main_count} cartes dans le main")
        
        return {
            'player': player,
            'login_id': deck_data.get('loginid'),
            'decktournamentid': deck_data.get('decktournamentid'),
            'mainboard': mainboard,
            'sideboard': sideboard,
            'archetype': None  # Sera déterminé par l'archetype parser
        }
    
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
    
    def scrape_parallel(self, tournaments: List[Dict], max_workers: int = 5) -> tuple:
        """Scrape plusieurs tournois en parallèle"""
        success_count = 0
        total_decks = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre tous les jobs
            future_to_tournament = {
                executor.submit(self.scrape_tournament_json, t): t 
                for t in tournaments
            }
            
            # Traiter les résultats au fur et à mesure
            for future in concurrent.futures.as_completed(future_to_tournament):
                tournament = future_to_tournament[future]
                try:
                    tournament_data = future.result()
                    if tournament_data and self.save_tournament_data(tournament_data):
                        success_count += 1
                        total_decks += len(tournament_data['decklists'])
                except Exception as e:
                    logger.error(f"Error processing {tournament['name']}: {e}")
        
        return success_count, total_decks


def main():
    parser = argparse.ArgumentParser(description='Scrape MTGO tournaments (JSON version)')
    
    # Arguments de date
    parser.add_argument('--start-date', type=str, 
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD)')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours')
    
    # Format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=['standard', 'modern', 'legacy', 'vintage', 'pioneer', 'pauper', 'limited', 'all'],
                       default=['standard'],
                       help='Format(s) à scraper')
    
    # Options
    parser.add_argument('--limit', type=int,
                       help='Limiter le nombre de tournois')
    parser.add_argument('--include-leagues', action='store_true',
                       help='Inclure les leagues (exclues par défaut)')
    parser.add_argument('--parallel', type=int, default=5,
                       help='Nombre de workers parallèles (défaut: 5)')
    
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
        # Période par défaut : juillet 1-21, 2025
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21)
    
    formats = set(args.format)
    
    logger.info("🎯 MTGO JSON Scraper")
    logger.info("=" * 60)
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(formats)}")
    logger.info(f"📊 Leagues: {'incluses' if args.include_leagues else 'exclues'}")
    
    scraper = MTGOJsonScraper()
    
    # Récupérer la liste des tournois
    tournaments = scraper.get_tournaments_list(start_date, end_date, formats, args.include_leagues)
    logger.info(f"\n✅ Found {len(tournaments)} tournaments")
    
    if not tournaments:
        logger.warning("Aucun tournoi trouvé!")
        return
    
    # Limiter si demandé
    if args.limit:
        tournaments = tournaments[:args.limit]
        logger.info(f"📊 Limité à {len(tournaments)} tournois")
    
    # Afficher les tournois
    logger.info("\n📋 Tournois à scraper:")
    for i, t in enumerate(tournaments[:10], 1):
        logger.info(f"  {i}. {t['date']} - {t['name']}")
    if len(tournaments) > 10:
        logger.info(f"  ... et {len(tournaments) - 10} autres")
    
    # Scraper
    start_time = time.time()
    
    if args.parallel > 1:
        logger.info(f"\n⚡ Mode parallèle avec {args.parallel} workers")
        success_count, total_decks = scraper.scrape_parallel(tournaments, args.parallel)
    else:
        # Mode séquentiel
        success_count = 0
        total_decks = 0
        
        for i, tournament in enumerate(tournaments, 1):
            logger.info(f"\n[{i}/{len(tournaments)}] Processing...")
            
            tournament_data = scraper.scrape_tournament_json(tournament)
            if tournament_data and scraper.save_tournament_data(tournament_data):
                success_count += 1
                total_decks += len(tournament_data['decklists'])
            
            if i < len(tournaments):
                time.sleep(0.5)
    
    elapsed = time.time() - start_time
    
    logger.info(f"\n✨ RÉSUMÉ:")
    logger.info(f"✅ Tournois scrapés: {success_count}/{len(tournaments)}")
    logger.info(f"🎴 Total decklists: {total_decks}")
    logger.info(f"⏱️ Temps: {elapsed:.1f}s")
    
    if total_decks == 0:
        logger.warning("\n⚠️ Aucune decklist trouvée!")


if __name__ == "__main__":
    main()