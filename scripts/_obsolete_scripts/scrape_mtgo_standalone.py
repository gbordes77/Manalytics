#!/usr/bin/env python3
"""
MTGO Scraper Standalone - Récupère tous les tournois de juillet 2025
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import re
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MTGOScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://www.mtgo.com"
        
    def get_july_tournaments(self):
        """Récupère tous les tournois de juillet 2025"""
        url = f"{self.base_url}/decklists"
        logger.info(f"Fetching: {url}")
        
        response = self.session.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to get main page: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les liens de tournois
        tournament_links = []
        
        # Chercher tous les liens
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/decklist/' in href and not href.startswith('/en/'):
                tournament_links.append({
                    'url': self.base_url + href,
                    'text': link.text.strip(),
                    'href': href
                })
        
        # Debug - afficher quelques liens
        logger.info(f"Found {len(tournament_links)} total tournament links")
        if tournament_links:
            logger.info("First 5 tournaments:")
            for t in tournament_links[:5]:
                logger.info(f"  - {t['text']}")
        
        # Filtrer pour juillet 2025
        july_tournaments = []
        for t in tournament_links:
            # Nettoyer le texte
            text = t['text'].replace('\n', ' ').strip()
            
            # Chercher July et 2025
            if 'July' in text and '2025' in text:
                # Extraire le nom (avant la date)
                parts = text.split('July')
                name = parts[0].strip()
                
                # Extraire le jour
                match = re.search(r'July\s+(\d+)\s+2025', text)
                if match:
                    day = int(match.group(1))
                    date = f"2025-07-{day:02d}"
                    
                    july_tournaments.append({
                        'name': name,
                        'date': date,
                        'url': t['url'],
                        'tournament_id': t['href'].split('/')[-1]
                    })
        
        return july_tournaments
    
    def save_tournaments(self, tournaments):
        """Sauvegarde les tournois"""
        base_dir = Path("data/raw/mtgo")
        
        # Grouper par format
        by_format = {}
        for t in tournaments:
            format_name = self._get_format(t['name'])
            if format_name not in by_format:
                by_format[format_name] = []
            by_format[format_name].append(t)
        
        saved_count = 0
        
        for format_name, format_tournaments in by_format.items():
            format_dir = base_dir / format_name
            format_dir.mkdir(parents=True, exist_ok=True)
            
            for tournament in format_tournaments:
                try:
                    # Créer le nom de fichier
                    filename = f"{tournament['date']}_{tournament['tournament_id']}.json"
                    filepath = format_dir / filename
                    
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
    
    def _get_format(self, name):
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
        elif 'limited' in name_lower:
            return 'limited'
        else:
            return 'other'


def main():
    logger.info("🎯 Scraping MTGO tournaments for July 2025")
    logger.info("=" * 50)
    
    scraper = MTGOScraper()
    
    # Récupérer les tournois
    tournaments = scraper.get_july_tournaments()
    logger.info(f"\n✅ Found {len(tournaments)} July 2025 tournaments")
    
    if tournaments:
        # Afficher le résumé
        formats = {}
        for t in tournaments:
            fmt = scraper._get_format(t['name'])
            formats[fmt] = formats.get(fmt, 0) + 1
        
        logger.info("\n📊 Summary by format:")
        for fmt, count in formats.items():
            logger.info(f"  {fmt}: {count} tournaments")
        
        # Sauvegarder
        saved = scraper.save_tournaments(tournaments)
        logger.info(f"\n✅ Saved {saved} tournament files")
    else:
        logger.warning("No tournaments found")


if __name__ == "__main__":
    main()