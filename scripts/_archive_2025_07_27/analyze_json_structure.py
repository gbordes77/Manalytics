#!/usr/bin/env python3
"""Analyse et compare la structure des données JSON MTGO vs Melee"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_mtgo():
    """Analyse la structure MTGO"""
    mtgo_path = Path('data/raw/mtgo')
    files = [f for f in mtgo_path.rglob('*.json') if '.processed' not in str(f)]
    
    if not files:
        return None
        
    # Prendre un fichier représentatif
    with open(files[0]) as f:
        sample = json.load(f)
    
    return {
        'total_files': len(files),
        'sample_file': files[0].name,
        'tournament_fields': list(sample.keys()),
        'deck_fields': list(sample['decks'][0].keys()) if sample.get('decks') else [],
        'card_fields': list(sample['decks'][0]['mainboard'][0].keys()) if sample.get('decks') and sample['decks'][0].get('mainboard') else []
    }

def analyze_melee():
    """Analyse la structure Melee"""
    melee_path = Path('data/raw/melee')
    files = list(melee_path.rglob('*.json'))
    
    if not files:
        return None
    
    # Chercher un fichier avec Mainboard/Sideboard
    for f in files:
        with open(f) as file:
            sample = json.load(file)
            if sample.get('Decks'):
                for deck in sample['Decks']:
                    if 'Mainboard' in deck:
                        return {
                            'total_files': len(files),
                            'sample_file': f.name,
                            'tournament_fields': list(sample.keys()),
                            'deck_fields': list(deck.keys()),
                            'card_fields': list(deck['Mainboard'][0].keys()) if deck.get('Mainboard') else []
                        }
    
    # Si pas trouvé, prendre le premier
    with open(files[0]) as f:
        sample = json.load(f)
    
    return {
        'total_files': len(files),
        'sample_file': files[0].name,
        'tournament_fields': list(sample.keys()),
        'deck_fields': list(sample['Decks'][0].keys()) if sample.get('Decks') else [],
        'card_fields': []
    }

def count_all_data():
    """Compte tous les decks et tournois"""
    stats = {
        'mtgo': {'tournaments': 0, 'decks': 0, 'formats': defaultdict(int)},
        'melee': {'tournaments': 0, 'decks': 0, 'formats': defaultdict(int)}
    }
    
    # MTGO
    mtgo_path = Path('data/raw/mtgo')
    for f in mtgo_path.rglob('*.json'):
        if '.processed' not in str(f):
            try:
                with open(f) as file:
                    data = json.load(file)
                    if isinstance(data, dict) and 'decks' in data:
                        stats['mtgo']['tournaments'] += 1
                        stats['mtgo']['decks'] += len(data['decks'])
                        stats['mtgo']['formats'][data.get('format', 'unknown')] += 1
            except:
                pass
    
    # Melee
    melee_path = Path('data/raw/melee')
    for f in melee_path.rglob('*.json'):
        try:
            with open(f) as file:
                data = json.load(file)
                if isinstance(data, dict) and 'Decks' in data:
                    stats['melee']['tournaments'] += 1
                    stats['melee']['decks'] += len(data['Decks'])
                    stats['melee']['formats'][data.get('FormatDescription', 'unknown')] += 1
        except:
            pass
    
    return stats

def main():
    print("=== ANALYSE COMPARATIVE MTGO vs MELEE ===\n")
    
    # Analyser les structures
    mtgo_structure = analyze_mtgo()
    melee_structure = analyze_melee()
    
    # Compter les données
    stats = count_all_data()
    
    # Afficher MTGO
    print("📊 MTGO DATA:")
    print(f"  - Fichiers JSON: {mtgo_structure['total_files']}")
    print(f"  - Tournois: {stats['mtgo']['tournaments']}")
    print(f"  - Decks totaux: {stats['mtgo']['decks']}")
    print(f"  - Moyenne decks/tournoi: {stats['mtgo']['decks']/stats['mtgo']['tournaments']:.1f}")
    print(f"  - Formats: {dict(stats['mtgo']['formats'])}")
    print(f"\n  Structure des données:")
    print(f"  - Champs tournoi: {mtgo_structure['tournament_fields']}")
    print(f"  - Champs deck: {mtgo_structure['deck_fields']}")
    print(f"  - Champs carte: {mtgo_structure['card_fields']}")
    
    # Afficher Melee
    print(f"\n📊 MELEE DATA:")
    print(f"  - Fichiers JSON: {melee_structure['total_files']}")
    print(f"  - Tournois: {stats['melee']['tournaments']}")
    print(f"  - Decks totaux: {stats['melee']['decks']}")
    print(f"  - Moyenne decks/tournoi: {stats['melee']['decks']/stats['melee']['tournaments']:.1f}")
    print(f"  - Formats: {dict(stats['melee']['formats'])}")
    print(f"\n  Structure des données:")
    print(f"  - Champs tournoi: {melee_structure['tournament_fields']}")
    print(f"  - Champs deck: {melee_structure['deck_fields']}")
    print(f"  - Champs carte: {melee_structure['card_fields']}")
    
    # Résumé
    print(f"\n📈 RÉSUMÉ:")
    print(f"  - Melee a {stats['melee']['decks'] - stats['mtgo']['decks']} decks de plus que MTGO")
    print(f"  - Melee a {stats['melee']['tournaments'] - stats['mtgo']['tournaments']} tournois de plus que MTGO")
    print(f"  - Total global: {stats['mtgo']['decks'] + stats['melee']['decks']} decks sur {stats['mtgo']['tournaments'] + stats['melee']['tournaments']} tournois")
    
    # Différences de structure
    print(f"\n🔍 DIFFÉRENCES CLÉS:")
    print(f"  - MTGO utilise 'decks' vs Melee utilise 'Decks'")
    print(f"  - MTGO a 'mainboard/sideboard' vs Melee a 'Mainboard/Sideboard'")
    print(f"  - MTGO a 'card_name' vs Melee a 'CardName'")
    print(f"  - MTGO a plus de métadonnées (standings, metagame_breakdown, metrics)")
    print(f"  - Melee a des IDs uniques (DeckId, DecklistId)")

if __name__ == "__main__":
    main()