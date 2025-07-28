#!/usr/bin/env python3
"""
Scraper Melee corrigé avec récupération des vrais Round IDs
Basé sur le code existant dans scrapers/clients/MtgMeleeClientV2.py
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional, Set
import re
import argparse
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import du scraper existant
from scrape_melee_flexible import MtgMeleeClientFlexible, MELEE_FORMATS


class MtgMeleeClientWithRounds(MtgMeleeClientFlexible):
    """Extension du client Melee avec support correct des Round Standings"""
    
    def get_tournament_round_ids(self, tournament_id: int) -> List[str]:
        """Récupérer les IDs des rounds depuis la page HTML du tournoi"""
        try:
            # Récupérer la page du tournoi
            tournament_url = f"https://melee.gg/Tournament/View/{tournament_id}"
            response = self.session.get(tournament_url)
            
            if response.status_code != 200:
                logger.error(f"Erreur accès tournoi {tournament_id}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher les boutons de rounds complétés
            round_nodes = soup.select('button.btn.btn-gray.round-selector[data-is-completed="True"]')
            
            if not round_nodes:
                logger.warning(f"Pas de rounds trouvés pour tournoi {tournament_id}")
                return []
            
            # Extraire les IDs
            round_ids = [node.get('data-id') for node in round_nodes if node.get('data-id')]
            logger.info(f"   📋 {len(round_ids)} rounds trouvés: {round_ids}")
            
            return round_ids
            
        except Exception as e:
            logger.error(f"Erreur récupération round IDs: {e}")
            return []
    
    def save_tournaments_with_rounds(self, entries: List[Dict], get_decks: bool = False) -> int:
        """Sauvegarder les tournois avec récupération correcte des rounds"""
        # Grouper par tournoi et format
        tournaments_by_format = {}
        
        for entry in entries:
            format_key = self._get_format_key(entry.get("FormatDescription", ""))
            tournament_id = entry.get("TournamentId")
            
            if format_key not in tournaments_by_format:
                tournaments_by_format[format_key] = {}
                
            if tournament_id not in tournaments_by_format[format_key]:
                tournaments_by_format[format_key][tournament_id] = {
                    "TournamentId": tournament_id,
                    "TournamentName": entry.get("TournamentName"),
                    "TournamentStartDate": entry.get("TournamentStartDate"),
                    "OrganizationName": entry.get("OrganizationName"),
                    "FormatDescription": entry.get("FormatDescription"),
                    "Decks": []
                }
                
            deck_entry = {
                "DecklistId": entry.get("Guid"),
                "PlayerName": entry.get("OwnerDisplayName"),
                "DeckName": entry.get("DecklistName"),
                "Rank": entry.get("TeamRank"),
                "Wins": entry.get("TeamMatchWins"),
                "Losses": entry.get("TeamMatchLosses"),
                "Draws": entry.get("TeamMatchDraws"),
                "IsValid": entry.get("IsValid")
            }
            tournaments_by_format[format_key][tournament_id]["Decks"].append(deck_entry)
        
        # Sauvegarder par format
        saved_count = 0
        
        for format_key, tournaments in tournaments_by_format.items():
            output_dir = Path(f"data/raw/melee/{format_key}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for tournament_id, tournament_data in tournaments.items():
                # Parser la date
                date_str = tournament_data["TournamentStartDate"]
                if date_str:
                    date_str = date_str.rstrip("Z")
                    try:
                        date = datetime.fromisoformat(date_str)
                        date_formatted = date.strftime("%Y-%m-%d")
                    except:
                        date_formatted = "unknown"
                else:
                    date_formatted = "unknown"
                    
                # Nom de fichier
                name_clean = re.sub(r'[^\\w\\s-]', '', tournament_data["TournamentName"])
                name_clean = re.sub(r'[-\\s]+', '-', name_clean)
                filename = f"{date_formatted}_{name_clean}.json"
                filepath = output_dir / filename
                
                logger.info(f"📥 {format_key}: {tournament_data['TournamentName']}")
                logger.info(f"   {len(tournament_data['Decks'])} decks trouvés")
                
                # Récupérer les vrais round IDs
                logger.info(f"   🎲 Récupération des round IDs...")
                round_ids = self.get_tournament_round_ids(tournament_id)
                
                if round_ids:
                    logger.info(f"   📊 Récupération des standings pour {len(round_ids)} rounds...")
                    round_standings = []
                    
                    for idx, round_id in enumerate(round_ids, 1):
                        standings = self.get_round_standings(tournament_id, round_id)
                        if standings:
                            logger.info(f"      Round {idx} (ID: {round_id}): {len(standings)} joueurs")
                            round_standings.append({
                                'round': idx,
                                'round_id': round_id,
                                'standings': standings
                            })
                        else:
                            logger.warning(f"      Round {idx} (ID: {round_id}): Pas de données")
                    
                    if round_standings:
                        tournament_data['RoundStandings'] = round_standings
                        tournament_data['TotalRounds'] = len(round_standings)
                        tournament_data['RoundIds'] = round_ids
                        logger.info(f"   ✅ {len(round_standings)} rounds avec données récupérés!")
                else:
                    logger.warning(f"   ❌ Pas de rounds disponibles pour ce tournoi")
                
                # Sauvegarder
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(tournament_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"   💾 Sauvegardé: {filename}")
                saved_count += 1
                
        return saved_count


def main():
    parser = argparse.ArgumentParser(description='Scrape Melee.gg avec Round Standings corrects')
    
    # Arguments de date
    parser.add_argument('--start-date', type=str,
                       help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD). Par défaut: aujourd\'hui')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours à partir d\'aujourd\'hui')
    
    # Arguments de format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=list(MELEE_FORMATS.keys()) + ['all'],
                       default=['standard'],
                       help='Format(s) à scraper. Par défaut: standard')
    
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
    
    logger.info("🎯 Melee.gg Scraper avec Round Standings Corrects")
    logger.info("=" * 50)
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(formats)}")
    logger.info("🎲 Récupération des round standings activée (méthode corrigée)")
    
    # Initialiser le client
    client = MtgMeleeClientWithRounds()
    
    # Rechercher les tournois
    logger.info("\n🔍 Recherche des tournois...")
    entries = client.search_tournaments(start_date, end_date, formats)
    
    logger.info(f"\n✅ Trouvé {len(entries)} entrées de decklists")
    
    if entries:
        # Afficher le résumé par format
        format_counts = {}
        for entry in entries:
            fmt = client._get_format_key(entry.get("FormatDescription", ""))
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
        logger.info("\n📊 Résumé par format:")
        for fmt, count in sorted(format_counts.items()):
            logger.info(f"  {fmt}: {count} entrées")
        
        # Sauvegarder avec la nouvelle méthode
        saved = client.save_tournaments_with_rounds(entries)
        logger.info(f"\n✅ {saved} tournois sauvegardés avec round standings!")
    else:
        logger.warning("Aucun tournoi trouvé pour les critères spécifiés")


if __name__ == "__main__":
    main()