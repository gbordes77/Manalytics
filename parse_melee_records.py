#!/usr/bin/env python3
"""
Parser pour extraire les decklists depuis les Records Melee
"""
from scrape_melee_from_commit import MtgMeleeClient
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_decklist_from_records(records):
    """Parse les Records pour extraire mainboard et sideboard"""
    mainboard = []
    sideboard = []
    
    for card in records:
        # c = 0 pour mainboard, c = 99 pour sideboard
        is_sideboard = card.get('c', 0) == 99
        
        card_entry = {
            'Count': card.get('q', 0),
            'CardName': card.get('n', '')
        }
        
        if is_sideboard:
            sideboard.append(card_entry)
        else:
            mainboard.append(card_entry)
    
    return mainboard, sideboard


def save_tournament_with_embedded_decklists(tournaments_data, format_filter="Standard"):
    """Sauvegarde les tournois avec leurs decklists déjà incluses"""
    
    # Grouper par tournoi
    tournaments = defaultdict(list)
    
    for deck_data in tournaments_data:
        tournament_id = deck_data.get('TournamentId')
        tournaments[tournament_id].append(deck_data)
    
    logger.info(f"📊 {len(tournaments)} tournois trouvés")
    
    # Filtrer par format
    filtered_tournaments = {}
    for tid, decks in tournaments.items():
        if decks and format_filter:
            format_desc = decks[0].get('FormatDescription', '')
            if format_filter.lower() in format_desc.lower():
                filtered_tournaments[tid] = decks
        else:
            filtered_tournaments[tid] = decks
    
    logger.info(f"🎮 {len(filtered_tournaments)} tournois {format_filter}")
    
    # Créer le dossier
    output_dir = Path("data/raw/melee/standard_complete")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    # Traiter chaque tournoi
    for tournament_id, deck_list in filtered_tournaments.items():
        if not deck_list:
            continue
            
        # Infos du tournoi depuis le premier deck
        first_deck = deck_list[0]
        tournament_name = first_deck.get('TournamentName', 'Unknown')
        tournament_date = first_deck.get('TournamentStartDate', '')
        format_desc = first_deck.get('FormatDescription', 'Unknown')
        organization = first_deck.get('OrganizationName', 'Unknown')
        
        logger.info(f"\n📋 {tournament_name} ({tournament_date})")
        logger.info(f"   📍 {organization}")
        logger.info(f"   🎮 {format_desc}")
        logger.info(f"   👥 {len(deck_list)} joueurs")
        
        # Parser les decklists
        complete_decks = []
        for deck_data in deck_list:
            records = deck_data.get('Records', [])
            if records:
                mainboard, sideboard = parse_decklist_from_records(records)
                
                complete_deck = {
                    'DeckId': deck_data.get('Guid'),
                    'PlayerName': deck_data.get('OwnerDisplayName'),
                    'DeckName': deck_data.get('DecklistName'),
                    'Rank': deck_data.get('TeamRank'),
                    'Wins': deck_data.get('TeamMatchWins'),
                    'Losses': deck_data.get('TeamMatchLosses'),
                    'Mainboard': mainboard,
                    'Sideboard': sideboard,
                    'Attributes': deck_data.get('Attributes', [])
                }
                complete_decks.append(complete_deck)
        
        logger.info(f"   ✅ {len(complete_decks)} decklists complètes")
        
        # Préparer le fichier
        tournament_data = {
            'TournamentId': tournament_id,
            'TournamentName': tournament_name,
            'TournamentStartDate': tournament_date,
            'FormatDescription': format_desc,
            'OrganizationName': organization,
            'TotalPlayers': len(deck_list),
            'Decks': complete_decks,
            'ScrapedAt': datetime.now().isoformat()
        }
        
        # Sauvegarder
        safe_name = tournament_name.replace('/', '-').replace('\\', '-').replace(':', '-')
        date_str = tournament_date.split('T')[0] if 'T' in tournament_date else tournament_date
        filename = f"{date_str}_{safe_name}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tournament_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"   💾 Sauvé: {filepath.name}")
        saved_files.append(filepath)
    
    return saved_files


def main():
    logger.info("🎯 Extraction des Decklists Melee depuis Records")
    logger.info("=" * 50)
    
    # Configuration
    days_back = 7
    format_filter = "Standard"
    
    # Dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    logger.info(f"📅 Période: {start_date.date()} à {end_date.date()}")
    logger.info(f"🎮 Format: {format_filter}")
    
    # Créer le client
    client = MtgMeleeClient()
    client.ensure_authenticated()
    
    # Rechercher
    logger.info("\n🔍 Recherche des tournois...")
    tournaments_data = client.search_tournaments(start_date, end_date)
    
    if tournaments_data:
        # Sauvegarder avec les decklists intégrées
        saved_files = save_tournament_with_embedded_decklists(tournaments_data, format_filter)
        
        # Résumé
        logger.info("\n" + "=" * 50)
        logger.info("📊 Résumé:")
        logger.info(f"  - Fichiers sauvegardés: {len(saved_files)}")
        
        # Vérifier un fichier
        if saved_files:
            test_file = saved_files[0]
            with open(test_file, 'r') as f:
                data = json.load(f)
                deck = data['Decks'][0] if data['Decks'] else None
                if deck:
                    logger.info(f"\n🔍 Exemple de deck ({deck['DeckName']}):")
                    logger.info(f"   Mainboard: {len(deck['Mainboard'])} cartes")
                    logger.info(f"   Sideboard: {len(deck['Sideboard'])} cartes")
                    
                    # Afficher quelques cartes
                    for card in deck['Mainboard'][:3]:
                        logger.info(f"   - {card['Count']}x {card['CardName']}")
    else:
        logger.info("❌ Aucun tournoi trouvé")


if __name__ == "__main__":
    main()