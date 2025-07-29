#!/usr/bin/env python3
"""
Reconstruit le cache avec les nouvelles données MTGO et lance l'analyse complète
"""

import sys
from pathlib import Path
import json
import logging
from datetime import datetime
import subprocess

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.cache_builder import CacheBuilder
from src.parsers.archetype_parser import ArchetypeParser

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def rebuild_cache():
    """Reconstruit le cache avec toutes les données"""
    logger.info("🔨 RECONSTRUCTION DU CACHE")
    logger.info("=" * 60)
    
    # 1. D'abord, intégrer les nouvelles données MTGO
    logger.info("\n📦 Intégration des données MTGO...")
    
    # Lire les données depuis mtg_decklistcache
    mtgo_path = Path("data/mtg_decklistcache/standard")
    mtgo_count = 0
    
    # Charger le cache existant (avec Melee)
    cache_path = Path("data/cache/decklists/2025-07.json")
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
    else:
        cache_data = {}
    
    # Parser d'archétypes
    parser = ArchetypeParser()
    
    # Ajouter chaque tournoi MTGO
    for json_file in mtgo_path.glob("*.json"):
        with open(json_file, 'r') as f:
            tournament_data = json.load(f)
        
        # Créer la clé du cache
        tournament_id = tournament_data['tournament_id']
        tournament_name = tournament_data['name'].lower().replace(' ', '-')
        date = tournament_data['date']
        cache_key = f"mtgo-{tournament_name}-{date}-{tournament_id}"
        
        # Convertir les decklists au format cache
        decklists = []
        for deck in tournament_data['decklists']:
            # Déterminer l'archétype
            cards = []
            for card in deck['mainboard']:
                cards.extend([card['name']] * card['quantity'])
            
            archetype = parser.identify_archetype(cards, 'standard')
            
            decklist = {
                'player': deck['player'],
                'archetype': archetype,
                'mainboard': deck['mainboard'],
                'sideboard': deck['sideboard']
            }
            decklists.append(decklist)
        
        # Ajouter au cache
        cache_data[cache_key] = {
            'source': 'mtgo',
            'format': 'standard',
            'name': tournament_data['name'],
            'date': tournament_data['date'],
            'url': tournament_data.get('url', ''),
            'tournament_id': tournament_id,
            'decklists': decklists
        }
        
        mtgo_count += 1
        logger.info(f"✅ Ajouté: {tournament_data['name']} - {len(decklists)} decks")
    
    # Sauvegarder le cache mis à jour
    with open(cache_path, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    logger.info(f"\n✨ Cache reconstruit!")
    logger.info(f"📊 Total tournois MTGO ajoutés: {mtgo_count}")
    logger.info(f"📊 Total tournois dans le cache: {len(cache_data)}")
    
    return len(cache_data)

def run_analysis():
    """Lance l'analyse complète avec le nouveau cache"""
    logger.info("\n🎯 LANCEMENT DE L'ANALYSE COMPLÈTE")
    logger.info("=" * 60)
    
    # Utiliser analyze_july_complete_final.py
    cmd = ["python3", "analyze_july_complete_final.py"]
    
    logger.info("🚀 Exécution de l'analyse...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        logger.info("✅ Analyse terminée avec succès!")
        
        # Ouvrir automatiquement le résultat
        analysis_file = Path("data/cache/july_complete_analysis.html")
        if analysis_file.exists():
            logger.info(f"\n📊 Ouverture de l'analyse...")
            subprocess.run(["open", str(analysis_file)])
    else:
        logger.error(f"❌ Erreur lors de l'analyse:")
        logger.error(result.stderr)

def main():
    logger.info("🎮 MANALYTICS - Reconstruction et Analyse")
    logger.info("Période: 1er au 21 juillet 2025")
    logger.info("")
    
    # 1. Reconstruire le cache
    total_tournaments = rebuild_cache()
    
    if total_tournaments > 0:
        # 2. Lancer l'analyse
        run_analysis()
    else:
        logger.error("❌ Aucun tournoi trouvé dans le cache!")

if __name__ == "__main__":
    main()