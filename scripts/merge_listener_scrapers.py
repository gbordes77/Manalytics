#!/usr/bin/env python3
"""
Script pour fusionner les données listener MTGO avec les scrapers MTGO
pour créer des JSONs compatibles avec MTGOArchetypeParser.

Le format de sortie doit contenir :
- Tournament : informations du tournoi
- Decks : decklists depuis les scrapers
- Rounds : matchs round par round depuis le listener
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_listener_data(listener_path: Path) -> Dict:
    """Charge les données du listener MTGO."""
    try:
        with open(listener_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement listener {listener_path}: {e}")
        return None


def load_scraper_data(scraper_path: Path) -> Dict:
    """Charge les données du scraper MTGO."""
    try:
        with open(scraper_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement scraper {scraper_path}: {e}")
        return None


def match_listener_to_scraper(listener_file: Path, scrapers_dir: Path) -> Optional[Path]:
    """
    Trouve le fichier scraper correspondant au listener.
    
    Le listener a un nom comme : standard-challenge-64-12801190.json
    Le scraper a un nom comme : 2025-07-01_0112801190.json
    """
    # Extraire l'ID du tournoi depuis le nom du listener
    listener_name = listener_file.stem
    parts = listener_name.split('-')
    if parts and parts[-1].isdigit():
        tournament_id = parts[-1]
        
        # Chercher le scraper correspondant
        for scraper_file in scrapers_dir.glob('*.json'):
            if tournament_id in scraper_file.name:
                return scraper_file
    
    return None


def merge_tournament_data(listener_data: Dict, scraper_data: Dict) -> Dict:
    """
    Fusionne les données listener et scraper au format MTGOArchetypeParser.
    """
    # Extraire la date depuis scraper_data
    date_str = scraper_data.get('date', '2025-07-01')
    
    # Créer la structure fusionnée
    merged = {
        "Tournament": {
            "Id": listener_data['Tournament']['Id'],
            "Date": listener_data['Tournament']['Date'],
            "Name": listener_data['Tournament']['Name'],
            "Uri": scraper_data.get('url', ''),
            "JsonFile": None,
            "ForceRedownload": False
        },
        "Decks": [],
        "Standings": [],
        "Rounds": listener_data.get('Rounds', [])
    }
    
    # Convertir les decklists au format attendu
    for decklist in scraper_data.get('decklists', []):
        deck = {
            "Player": decklist['player'],
            "Date": date_str + "T00:00:00",
            "Result": decklist.get('result', ''),
            "AnchorUri": scraper_data.get('url', ''),
            "Mainboard": [],
            "Sideboard": []
        }
        
        # Convertir mainboard
        for card in decklist.get('mainboard', []):
            deck['Mainboard'].append({
                "Count": card['count'],
                "Card": card['card_name']
            })
        
        # Convertir sideboard
        for card in decklist.get('sideboard', []):
            deck['Sideboard'].append({
                "Count": card['count'],
                "Card": card['card_name']
            })
        
        merged['Decks'].append(deck)
    
    # Extraire les standings depuis les résultats des matchs
    # (Note: C'est une approximation, les vraies standings nécessiteraient plus d'infos)
    player_stats = {}
    for round_data in merged['Rounds']:
        for match in round_data.get('Matches', []):
            player1 = match['Player1']
            player2 = match['Player2']
            result = match['Result'].split('-')
            
            if len(result) >= 2:
                p1_wins = int(result[0])
                p2_wins = int(result[1])
                
                # Initialiser les stats
                if player1 not in player_stats:
                    player_stats[player1] = {'Wins': 0, 'Losses': 0, 'Draws': 0}
                if player2 not in player_stats:
                    player_stats[player2] = {'Wins': 0, 'Losses': 0, 'Draws': 0}
                
                # Comptabiliser match wins/losses
                if p1_wins > p2_wins:
                    player_stats[player1]['Wins'] += 1
                    player_stats[player2]['Losses'] += 1
                elif p2_wins > p1_wins:
                    player_stats[player2]['Wins'] += 1
                    player_stats[player1]['Losses'] += 1
                else:
                    player_stats[player1]['Draws'] += 1
                    player_stats[player2]['Draws'] += 1
    
    # Créer les standings
    for player, stats in player_stats.items():
        points = stats['Wins'] * 3 + stats['Draws'] * 1
        merged['Standings'].append({
            "Player": player,
            "Points": points,
            "Wins": stats['Wins'],
            "Losses": stats['Losses'],
            "Draws": stats['Draws']
        })
    
    return merged


def process_format_data(format_name: str, start_date: str, end_date: str, 
                       output_dir: Path) -> int:
    """
    Traite tous les tournois d'un format pour une période donnée.
    """
    # Chemins des données
    base_dir = Path(__file__).parent.parent
    listener_base = base_dir / 'data' / 'mtgodata'
    scraper_base = base_dir / 'data' / 'raw' / 'mtgo' / format_name
    
    if not listener_base.exists():
        logger.error(f"Dossier listener inexistant : {listener_base}")
        return 0
    
    if not scraper_base.exists():
        logger.error(f"Dossier scraper inexistant : {scraper_base}")
        return 0
    
    # Créer le dossier de sortie
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convertir les dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    merged_count = 0
    
    # Parcourir les dates
    current = start
    while current <= end:
        year = current.year
        month = current.month
        day = current.day
        
        # Chemin du listener pour cette date
        listener_day_path = listener_base / str(year) / f"{month:02d}" / f"{day:02d}"
        
        if listener_day_path.exists():
            # Chercher les tournois du format
            for listener_file in listener_day_path.glob(f"{format_name}-*.json"):
                logger.info(f"Traitement : {listener_file.name}")
                
                # Charger les données listener
                listener_data = load_listener_data(listener_file)
                if not listener_data:
                    continue
                
                # Trouver le scraper correspondant
                scraper_file = match_listener_to_scraper(listener_file, scraper_base)
                if not scraper_file:
                    logger.warning(f"Pas de scraper trouvé pour : {listener_file.name}")
                    continue
                
                # Charger les données scraper
                scraper_data = load_scraper_data(scraper_file)
                if not scraper_data:
                    continue
                
                # Fusionner les données
                merged_data = merge_tournament_data(listener_data, scraper_data)
                
                # Sauvegarder le résultat
                output_file = output_dir / listener_file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(merged_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Fusionné : {output_file.name}")
                merged_count += 1
        
        # Passer au jour suivant
        current = datetime(year, month, day + 1) if day < 31 else datetime(year, month + 1, 1)
        if current.month > 12:
            current = datetime(year + 1, 1, 1)
    
    return merged_count


def main():
    parser = argparse.ArgumentParser(
        description="Fusionne les données listener et scraper pour MTGOArchetypeParser"
    )
    parser.add_argument(
        '--format', 
        default='standard',
        help='Format MTG (default: standard)'
    )
    parser.add_argument(
        '--start-date',
        default='2025-07-01',
        help='Date de début (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        default='2025-07-21',
        help='Date de fin (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('data/merged_tournaments'),
        help='Dossier de sortie'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Fusion des données {args.format} du {args.start_date} au {args.end_date}")
    
    count = process_format_data(
        args.format,
        args.start_date,
        args.end_date,
        args.output_dir / args.format
    )
    
    logger.info(f"Fusion terminée : {count} tournois fusionnés")
    logger.info(f"Fichiers sauvegardés dans : {args.output_dir / args.format}")


if __name__ == "__main__":
    main()