#!/usr/bin/env python3
"""
Scraper Melee.gg avec récupération des decklists complètes
"""
import json
import os
from datetime import datetime, timedelta
import time
from pathlib import Path
import logging

# Import du client existant
from scrape_melee_from_commit import MtgMeleeClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_tournament_with_decklists(client: MtgMeleeClient, tournament_data: dict, output_dir: Path):
    """Récupère un tournoi avec toutes ses decklists"""
    tournament_id = tournament_data.get('TournamentId')
    tournament_name = tournament_data.get('TournamentName', 'Unknown')
    tournament_date = tournament_data.get('TournamentStartDate', '')
    
    logger.info(f"📋 Traitement: {tournament_name} ({tournament_date})")
    
    # Récupérer les détails du tournoi
    try:
        # Récupérer tous les decks du tournoi
        decks = tournament_data.get('Decks', [])
        if not decks:
            logger.warning(f"  ⚠️ Aucun deck trouvé")
            return None
            
        logger.info(f"  📊 {len(decks)} decks trouvés")
        
        # Récupérer les decklists complètes
        complete_decks = []
        for i, deck_info in enumerate(decks):
            deck_id = deck_info.get('DecklistId')
            if not deck_id:
                continue
                
            # Afficher la progression
            if i % 10 == 0:
                logger.info(f"  ⏳ Progression: {i}/{len(decks)} decks...")
            
            # Récupérer la decklist complète
            deck_details = client.get_deck(deck_id)
            if deck_details:
                # Fusionner les infos
                complete_deck = {
                    **deck_info,
                    'Mainboard': deck_details.get('Mainboard', []),
                    'Sideboard': deck_details.get('Sideboard', []),
                    'Format': deck_details.get('Format', tournament_data.get('FormatDescription'))
                }
                complete_decks.append(complete_deck)
                
                # Petite pause pour éviter le rate limiting
                time.sleep(0.2)
            else:
                logger.warning(f"  ❌ Impossible de récupérer le deck {deck_id}")
        
        logger.info(f"  ✅ {len(complete_decks)}/{len(decks)} decklists récupérées")
        
        if not complete_decks:
            return None
            
        # Préparer les données du tournoi
        tournament_with_decklists = {
            'TournamentId': tournament_id,
            'TournamentName': tournament_name,
            'TournamentStartDate': tournament_date,
            'FormatDescription': tournament_data.get('FormatDescription'),
            'OrganizationName': tournament_data.get('OrganizationName'),
            'TotalPlayers': len(decks),
            'DecksWithLists': len(complete_decks),
            'Decks': complete_decks,
            'ScrapedAt': datetime.now().isoformat()
        }
        
        # Sauvegarder le fichier
        # Nettoyer le nom pour le fichier
        safe_name = tournament_name.replace('/', '-').replace('\\', '-').replace(':', '-')
        date_str = tournament_date.split('T')[0] if 'T' in tournament_date else tournament_date
        filename = f"{date_str}_{safe_name}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tournament_with_decklists, f, indent=2, ensure_ascii=False)
            
        logger.info(f"  💾 Sauvegardé: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"  ❌ Erreur: {e}")
        return None


def main():
    logger.info("🎯 Scraper Melee avec Decklists Complètes")
    logger.info("=" * 50)
    
    # Configuration
    days_back = 3  # Récupérer les tournois des 3 derniers jours
    format_filter = "Standard"  # Ou None pour tous les formats
    limit = 5  # Limiter à 5 tournois pour le test
    
    # Calculer les dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    logger.info(f"📅 Période: {start_date.date()} à {end_date.date()}")
    logger.info(f"🎮 Format: {format_filter or 'Tous'}")
    logger.info(f"🔢 Limite: {limit} tournois")
    
    # Créer le client
    client = MtgMeleeClient()
    
    # Rechercher les tournois
    logger.info("\n🔍 Recherche des tournois...")
    all_decklists = client.search_tournaments(start_date, end_date)
    
    # Grouper par tournoi
    tournaments = {}
    for deck in all_decklists:
        tournament_id = deck.get('TournamentId')
        if tournament_id not in tournaments:
            tournaments[tournament_id] = {
                'TournamentId': tournament_id,
                'TournamentName': deck.get('TournamentName'),
                'TournamentStartDate': deck.get('TournamentStartDate'),
                'FormatDescription': deck.get('FormatDescription'),
                'OrganizationName': deck.get('OrganizationName'),
                'Decks': []
            }
        tournaments[tournament_id]['Decks'].append(deck)
    
    logger.info(f"✅ {len(tournaments)} tournois trouvés")
    
    # Filtrer par format si nécessaire
    if format_filter:
        filtered = {
            tid: tdata for tid, tdata in tournaments.items()
            if format_filter.lower() in tdata.get('FormatDescription', '').lower()
        }
        logger.info(f"📊 {len(filtered)} tournois {format_filter}")
        tournaments = filtered
    
    # Limiter le nombre de tournois
    tournament_list = list(tournaments.values())[:limit]
    
    # Créer le dossier de sortie
    output_dir = Path("data/raw/melee/standard_with_decklists")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Traiter chaque tournoi
    logger.info(f"\n📥 Récupération des decklists pour {len(tournament_list)} tournois...")
    saved_files = []
    
    for i, tournament_data in enumerate(tournament_list):
        logger.info(f"\n[{i+1}/{len(tournament_list)}]")
        filepath = scrape_tournament_with_decklists(client, tournament_data, output_dir)
        if filepath:
            saved_files.append(filepath)
        
        # Pause entre les tournois
        if i < len(tournament_list) - 1:
            time.sleep(1)
    
    # Résumé
    logger.info("\n" + "=" * 50)
    logger.info("📊 Résumé:")
    logger.info(f"  - Tournois traités: {len(tournament_list)}")
    logger.info(f"  - Fichiers sauvegardés: {len(saved_files)}")
    
    if saved_files:
        logger.info("\n📁 Fichiers créés:")
        for f in saved_files:
            logger.info(f"  - {f}")


if __name__ == "__main__":
    main()