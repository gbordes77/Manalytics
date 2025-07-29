#!/usr/bin/env python3
"""
Intègre les données MTGO de mtg_decklistcache dans le cache principal
"""

import json
from pathlib import Path
import logging
import sys

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.manalytics.parsers.archetype_parser import ArchetypeParser

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def process_mtgo_data():
    """Intègre les données MTGO dans le cache"""
    logger.info("📦 INTÉGRATION DES DONNÉES MTGO DANS LE CACHE")
    logger.info("=" * 60)
    
    # Chemins
    mtgo_dir = Path("data/mtg_decklistcache/standard")
    cache_file = Path("data/cache/decklists/2025-07.json")
    
    # Charger le cache existant
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        logger.info(f"✅ Cache existant chargé: {len(cache_data)} entrées")
    else:
        cache_data = {}
        logger.info("📝 Création d'un nouveau cache")
    
    # Parser d'archétypes
    parser = ArchetypeParser()
    
    # Traiter chaque fichier MTGO
    mtgo_count = 0
    total_decks = 0
    
    for json_file in sorted(mtgo_dir.glob("*.json")):
        logger.info(f"\n📄 Traitement de {json_file.name}...")
        
        with open(json_file, 'r') as f:
            tournament_data = json.load(f)
        
        # Créer la clé du cache
        tournament_id = tournament_data.get('tournament_id', '')
        tournament_name = tournament_data['name'].lower().replace(' ', '-').replace(':', '')
        date = tournament_data['date']
        
        # Clé unique pour le cache
        cache_key = f"mtgo-{tournament_name}-{date}{tournament_id}"
        
        # Préparer les decklists avec archétypes
        processed_decklists = []
        
        for deck in tournament_data.get('decklists', []):
            # Extraire toutes les cartes du mainboard pour l'identification
            all_cards = []
            for card in deck.get('mainboard', []):
                all_cards.extend([card['name']] * card['quantity'])
            
            # Identifier l'archétype
            archetype = parser.identify_archetype(all_cards, 'standard')
            
            # Créer l'entrée de decklist
            processed_deck = {
                'player': deck.get('player', 'Unknown'),
                'archetype': archetype,
                'mainboard': deck.get('mainboard', []),
                'sideboard': deck.get('sideboard', []),
                'result': deck.get('result'),
                'place': deck.get('place')
            }
            
            # Ajouter les IDs si disponibles
            if 'login_id' in deck:
                processed_deck['login_id'] = deck['login_id']
            if 'decktournamentid' in deck:
                processed_deck['decktournamentid'] = deck['decktournamentid']
            
            processed_decklists.append(processed_deck)
        
        # Créer l'entrée du tournoi pour le cache
        cache_entry = {
            'source': 'mtgo',
            'format': tournament_data.get('format', 'standard'),
            'name': tournament_data['name'],
            'date': tournament_data['date'],
            'url': tournament_data.get('url', ''),
            'tournament_id': tournament_id,
            'event_id': tournament_data.get('event_id'),
            'description': tournament_data.get('description', tournament_data['name']),
            'decklists': processed_decklists
        }
        
        # Ajouter au cache
        cache_data[cache_key] = cache_entry
        
        mtgo_count += 1
        total_decks += len(processed_decklists)
        
        logger.info(f"  ✅ {len(processed_decklists)} decks traités")
        logger.info(f"  📊 Archétypes: {len(set(d['archetype'] for d in processed_decklists if d['archetype']))} différents")
    
    # Sauvegarder le cache mis à jour
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✨ INTÉGRATION TERMINÉE!")
    logger.info(f"📊 Tournois MTGO ajoutés: {mtgo_count}")
    logger.info(f"🎴 Total decks MTGO: {total_decks}")
    logger.info(f"📁 Cache sauvegardé: {cache_file}")
    
    # Statistiques finales
    mtgo_entries = sum(1 for k in cache_data if k.startswith('mtgo-'))
    melee_entries = sum(1 for k in cache_data if 'melee' in k.lower() or 'TheGathering' in k)
    
    logger.info(f"\n📈 CACHE FINAL:")
    logger.info(f"  - Tournois MTGO: {mtgo_entries}")
    logger.info(f"  - Tournois Melee: {melee_entries}")
    logger.info(f"  - TOTAL: {len(cache_data)} tournois")

if __name__ == "__main__":
    process_mtgo_data()