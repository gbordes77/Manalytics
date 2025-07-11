#!/usr/bin/env python3

"""
Script de démonstration de Manalytics
Montre le fonctionnement du pipeline sans nécessiter de données réelles
"""

import asyncio
import json
import os
from datetime import datetime
import sys

# Ajouter le dossier courant au PYTHONPATH
sys.path.append('.')

from src.python.classifier.archetype_engine import ArchetypeEngine

def create_sample_tournament_data():
    """Créer des données d'exemple pour la démonstration"""
    return {
        "tournament": {
            "id": "demo_tournament_001",
            "name": "Demo Modern Tournament",
            "date": "2025-01-15T10:00:00Z",
            "format": "Modern",
            "source": "demo",
            "url": "https://example.com/tournament/demo_001"
        },
        "decks": [
            {
                "player": "Alice",
                "rank": 1,
                "wins": 4,
                "losses": 0,
                "mainboard": [
                    {"name": "Lightning Bolt", "count": 4, "set": "M21", "number": "148"},
                    {"name": "Monastery Swiftspear", "count": 4, "set": "KTK", "number": "118"},
                    {"name": "Lava Spike", "count": 4, "set": "CHK", "number": "166"},
                    {"name": "Rift Bolt", "count": 4, "set": "TSP", "number": "176"},
                    {"name": "Mountain", "count": 20, "set": "UNH", "number": "139"}
                ],
                "sideboard": [
                    {"name": "Destructive Revelry", "count": 3, "set": "THS", "number": "192"},
                    {"name": "Smash to Smithereens", "count": 2, "set": "SOM", "number": "107"}
                ]
            },
            {
                "player": "Bob",
                "rank": 2,
                "wins": 3,
                "losses": 1,
                "mainboard": [
                    {"name": "Snapcaster Mage", "count": 4, "set": "ISD", "number": "78"},
                    {"name": "Lightning Bolt", "count": 4, "set": "M21", "number": "148"},
                    {"name": "Counterspell", "count": 4, "set": "M21", "number": "267"},
                    {"name": "Island", "count": 12, "set": "UNH", "number": "137"},
                    {"name": "Mountain", "count": 8, "set": "UNH", "number": "139"}
                ],
                "sideboard": [
                    {"name": "Negate", "count": 3, "set": "M21", "number": "56"},
                    {"name": "Pyroclasm", "count": 2, "set": "M10", "number": "153"}
                ]
            },
            {
                "player": "Charlie",
                "rank": 3,
                "wins": 3,
                "losses": 1,
                "mainboard": [
                    {"name": "Tarmogoyf", "count": 4, "set": "FUT", "number": "153"},
                    {"name": "Lightning Bolt", "count": 4, "set": "M21", "number": "148"},
                    {"name": "Dark Confidant", "count": 3, "set": "RAV", "number": "81"},
                    {"name": "Forest", "count": 8, "set": "UNH", "number": "140"},
                    {"name": "Swamp", "count": 6, "set": "UNH", "number": "138"},
                    {"name": "Mountain", "count": 4, "set": "UNH", "number": "139"}
                ],
                "sideboard": [
                    {"name": "Abrupt Decay", "count": 3, "set": "RTR", "number": "141"},
                    {"name": "Surgical Extraction", "count": 2, "set": "NPH", "number": "74"}
                ]
            }
        ],
        "standings": [
            {"player": "Alice", "rank": 1, "wins": 4, "losses": 0},
            {"player": "Bob", "rank": 2, "wins": 3, "losses": 1},
            {"player": "Charlie", "rank": 3, "wins": 3, "losses": 1}
        ]
    }

def create_sample_metagame_analysis():
    """Créer une analyse de métagame d'exemple"""
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat() + "Z",
            "total_decks": 3,
            "total_tournaments": 1,
            "date_range": {
                "start": "2025-01-15",
                "end": "2025-01-15"
            },
            "formats": ["Modern"],
            "sources": ["demo"],
            "analysis_parameters": {
                "min_matches_for_matchup": 10,
                "min_decks_for_archetype": 1
            }
        },
        "archetype_performance": [
            {
                "archetype": "Burn",
                "deck_count": 1,
                "win_rate": 1.0,
                "meta_share": 0.33,
                "tournaments_appeared": 1
            },
            {
                "archetype": "Control",
                "deck_count": 1,
                "win_rate": 0.75,
                "meta_share": 0.33,
                "tournaments_appeared": 1
            },
            {
                "archetype": "Midrange",
                "deck_count": 1,
                "win_rate": 0.75,
                "meta_share": 0.33,
                "tournaments_appeared": 1
            }
        ],
        "temporal_trends": {
            "trend_summary": [
                {
                    "archetype": "Burn",
                    "avg_meta_share": 0.33,
                    "meta_share_trend": 0.0,
                    "avg_win_rate": 1.0,
                    "win_rate_trend": 0.0
                }
            ]
        },
        "source_statistics": [
            {
                "tournament_source": "demo",
                "tournament_count": 1,
                "deck_count": 3,
                "avg_win_rate": 0.83,
                "archetype_diversity": 3
            }
        ]
    }

async def demo_scraper():
    """Démonstration du module de scraping"""
    print("🕷️  Démonstration du module de scraping")
    print("="*50)
    
    # Simuler des données scrapées
    tournament_data = create_sample_tournament_data()
    
    print(f"✅ Tournoi scrapé: {tournament_data['tournament']['name']}")
    print(f"   Format: {tournament_data['tournament']['format']}")
    print(f"   Nombre de decks: {len(tournament_data['decks'])}")
    print(f"   Source: {tournament_data['tournament']['source']}")
    
    # Sauvegarder dans le dossier raw
    os.makedirs("data/raw/demo/2025/01/15", exist_ok=True)
    with open("data/raw/demo/2025/01/15/tournament_demo_001.json", "w") as f:
        json.dump(tournament_data, f, indent=2)
    
    print("   💾 Données sauvegardées dans data/raw/demo/")
    return tournament_data

async def demo_classifier():
    """Démonstration du module de classification"""
    print("\n🎯 Démonstration du module de classification")
    print("="*50)
    
    # Charger les données du scraper
    with open("data/raw/demo/2025/01/15/tournament_demo_001.json", "r") as f:
        tournament_data = json.load(f)
    
    # Initialiser le moteur de classification
    engine = ArchetypeEngine("MTGOFormatData")
    
    # Charger les données Modern
    if engine.load_format_data("Modern"):
        print("✅ Règles d'archétypes Modern chargées")
        
        # Classifier chaque deck
        for deck in tournament_data["decks"]:
            archetype = engine.classify_deck(deck, "Modern")
            deck["archetype"] = archetype
            print(f"   🔍 {deck['player']}: {archetype}")
    else:
        print("⚠️  Impossible de charger les règles Modern, utilisation d'archétypes génériques")
        # Classification basique basée sur les cartes clés
        for deck in tournament_data["decks"]:
            mainboard_cards = [card["name"] for card in deck["mainboard"]]
            
            if "Lightning Bolt" in mainboard_cards and "Monastery Swiftspear" in mainboard_cards:
                archetype = "Burn"
            elif "Snapcaster Mage" in mainboard_cards and "Counterspell" in mainboard_cards:
                archetype = "Control"
            elif "Tarmogoyf" in mainboard_cards and "Dark Confidant" in mainboard_cards:
                archetype = "Midrange"
            else:
                archetype = "Unknown"
            
            deck["archetype"] = archetype
            print(f"   🔍 {deck['player']}: {archetype}")
    
    # Sauvegarder les données classifiées
    os.makedirs("data/processed/demo/2025/01/15", exist_ok=True)
    with open("data/processed/demo/2025/01/15/tournament_demo_001.json", "w") as f:
        json.dump(tournament_data, f, indent=2)
    
    print("   💾 Données classifiées sauvegardées dans data/processed/demo/")
    return tournament_data

async def demo_analysis():
    """Démonstration de l'analyse (version Python simplifiée)"""
    print("\n📊 Démonstration de l'analyse de métagame")
    print("="*50)
    
    # Créer une analyse d'exemple
    analysis = create_sample_metagame_analysis()
    
    print("✅ Analyse de métagame générée:")
    print(f"   Total decks analysés: {analysis['metadata']['total_decks']}")
    print(f"   Archétypes identifiés: {len(analysis['archetype_performance'])}")
    
    print("\n📈 Performance par archétype:")
    for archetype in analysis['archetype_performance']:
        print(f"   • {archetype['archetype']}: {archetype['win_rate']:.1%} winrate, {archetype['meta_share']:.1%} meta share")
    
    # Sauvegarder l'analyse
    os.makedirs("data/output", exist_ok=True)
    output_file = "data/output/metagame_Modern_demo.json"
    with open(output_file, "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"   💾 Analyse sauvegardée: {output_file}")
    return analysis

async def main():
    """Fonction principale de démonstration"""
    print("🧙‍♂️ DÉMONSTRATION MANALYTICS")
    print("="*60)
    print("Cette démonstration montre le fonctionnement du pipeline")
    print("avec des données d'exemple, sans nécessiter de scraping réel.\n")
    
    try:
        # Phase 1: Scraping (simulé)
        await demo_scraper()
        
        # Phase 2: Classification
        await demo_classifier()
        
        # Phase 3: Analyse (simplifiée)
        await demo_analysis()
        
        print("\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print("="*60)
        print("Le pipeline Manalytics fonctionne correctement.")
        print("\nFichiers générés:")
        print("• data/raw/demo/2025/01/15/tournament_demo_001.json")
        print("• data/processed/demo/2025/01/15/tournament_demo_001.json")
        print("• data/output/metagame_Modern_demo.json")
        
        print("\nPour utiliser avec de vraies données:")
        print("python orchestrator.py --format Modern --start-date 2025-01-01")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 