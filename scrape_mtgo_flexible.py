#!/usr/bin/env python3
"""
MTGO Scraper Flexible - Support multi-formats et dates personnalisables
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
from typing import List, Set, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
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
    'limited': 'Limited',
    'duel-commander': 'Duel Commander'
}


class MTGOScraperFlexible:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://www.mtgo.com"
        
    def get_tournaments(self, start_date: datetime, end_date: datetime, formats: Set[str]) -> List[dict]:
        """Récupère les tournois pour la période et formats spécifiés"""
        url = f"{self.base_url}/decklists"
        logger.info(f"Fetching: {url}")
        
        response = self.session.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to get main page: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les liens de tournois
        tournament_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/decklist/' in href and not href.startswith('/en/'):
                tournament_links.append({
                    'url': self.base_url + href,
                    'text': link.text.strip(),
                    'href': href
                })
        
        logger.info(f"Found {len(tournament_links)} total tournament links")
        
        # Filtrer par date et format
        filtered_tournaments = []
        
        for t in tournament_links:
            # Nettoyer le texte
            text = t['text'].replace('\n', ' ').strip()
            
            # Extraire la date
            date_match = None
            for month in ['January', 'February', 'March', 'April', 'May', 'June', 
                         'July', 'August', 'September', 'October', 'November', 'December']:
                pattern = rf'{month}\s+(\d+)\s+(\d{{4}})'
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
                    date_match = tournament_date
                    break
            
            if not date_match:
                continue
                
            # Vérifier si dans la période
            if not (start_date <= tournament_date <= end_date):
                continue
                
            # Extraire le nom (avant la date)
            parts = text.split(match.group(0))
            name = parts[0].strip()
            
            # Déterminer le format
            format_name = self._get_format(name)
            
            # Vérifier si le format est désiré
            if formats != {'all'} and format_name not in formats:
                continue
            
            filtered_tournaments.append({
                'name': name,
                'date': tournament_date.strftime('%Y-%m-%d'),
                'url': t['url'],
                'tournament_id': t['href'].split('/')[-1],
                'format': format_name
            })
        
        return filtered_tournaments
    
    def save_tournaments(self, tournaments: List[dict]) -> int:
        """Sauvegarde les tournois"""
        base_dir = Path("data/raw/mtgo")
        
        # Grouper par format
        by_format = {}
        for t in tournaments:
            format_name = t['format']
            if format_name not in by_format:
                by_format[format_name] = []
            by_format[format_name].append(t)
        
        saved_count = 0
        
        for format_name, format_tournaments in by_format.items():
            format_dir = base_dir / format_name
            
            # Créer le dossier leagues si nécessaire
            if any('league' in t['name'].lower() for t in format_tournaments):
                leagues_dir = format_dir / 'leagues'
                leagues_dir.mkdir(parents=True, exist_ok=True)
            
            format_dir.mkdir(parents=True, exist_ok=True)
            
            for tournament in format_tournaments:
                try:
                    # Déterminer le bon dossier
                    if 'league' in tournament['name'].lower():
                        target_dir = format_dir / 'leagues'
                    else:
                        target_dir = format_dir
                    
                    # Créer le nom de fichier
                    filename = f"{tournament['date']}_{tournament['tournament_id']}.json"
                    filepath = target_dir / filename
                    
                    # Sauvegarder
                    with open(filepath, 'w') as f:
                        json.dump({
                            'source': 'mtgo',
                            'format': format_name,
                            'name': tournament['name'],
                            'date': tournament['date'],
                            'url': tournament['url'],
                            'tournament_id': tournament['tournament_id'],
                            'scraped_at': datetime.now().isoformat()
                        }, f, indent=2)
                    
                    logger.info(f"Saved: {format_name}/{filename}")
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving {tournament['name']}: {e}")
        
        return saved_count
    
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
        elif 'duel commander' in name_lower:
            return 'duel-commander'
        elif 'limited' in name_lower or 'draft' in name_lower or 'sealed' in name_lower:
            return 'limited'
        else:
            return 'other'


def main():
    parser = argparse.ArgumentParser(description='Scrape MTGO tournaments flexibly')
    
    # Arguments de date
    parser.add_argument('--start-date', type=str, 
                       help='Date de début (YYYY-MM-DD). Par défaut: 7 jours avant')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD). Par défaut: aujourd\'hui')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours à partir d\'aujourd\'hui')
    
    # Arguments de format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=list(SUPPORTED_FORMATS.keys()) + ['all'],
                       default=['standard'],
                       help='Format(s) à scraper. Par défaut: standard')
    
    # Mode incrémental (futur)
    parser.add_argument('--incremental', action='store_true',
                       help='Mode incrémental: scraper seulement les nouveaux tournois')
    
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
        start_date = end_date - timedelta(days=7)
    
    # Formats à scraper
    formats = set(args.format)
    
    logger.info("🎯 MTGO Flexible Scraper")
    logger.info("=" * 50)
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(formats)}")
    
    scraper = MTGOScraperFlexible()
    
    # Récupérer les tournois
    tournaments = scraper.get_tournaments(start_date, end_date, formats)
    logger.info(f"\n✅ Found {len(tournaments)} tournaments")
    
    if tournaments:
        # Afficher le résumé
        format_counts = {}
        for t in tournaments:
            fmt = t['format']
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
        
        logger.info("\n📊 Summary by format:")
        for fmt, count in sorted(format_counts.items()):
            logger.info(f"  {fmt}: {count} tournaments")
        
        # Sauvegarder
        saved = scraper.save_tournaments(tournaments)
        logger.info(f"\n✅ Saved {saved} tournament files")
        
        if args.incremental:
            logger.info("💡 Mode incrémental activé - seuls les nouveaux tournois ont été sauvés")
    else:
        logger.warning("No tournaments found for the specified criteria")


if __name__ == "__main__":
    main()