#!/usr/bin/env python3
"""
🎯 DÉMONSTRATION STEP 2: DATA TREATMENT
Montre le MTGOArchetypeParser en action sur des données réelles
"""

import json
import sys
from collections import Counter

import pandas as pd

sys.path.append("src")

from orchestrator import ManalyticsOrchestrator
from python.classifier.mtgo_archetype_parser import MTGOArchetypeParser


def test_step2_demo():
    """Démonstration complète de la Step 2"""

    print("🎯 STEP 2: DATA TREATMENT - DÉMONSTRATION")
    print("=" * 60)

    # Initialiser les composants
    orchestrator = ManalyticsOrchestrator()
    parser = MTGOArchetypeParser()

    # Afficher les formats disponibles
    print("\n📋 FORMATS DISPONIBLES:")
    formats = parser.get_available_formats()
    for fmt in formats:
        stats = parser.get_format_statistics(fmt)
        print(
            f"  - {fmt}: {stats['archetypes']} archétypes, {stats['fallbacks']} fallbacks"
        )

    # Charger un tournoi Modern
    tournament_file = "./temp_fbettega/MTG_decklistcache/Tournaments/MTGmelee/2025/06/30/1o-torneio-13a-liga-arena-guardians-modern-332615-2025-06-30.json"

    try:
        with open(tournament_file, "r") as f:
            tournament_data = json.load(f)

        print(f"\n📊 ANALYSE TOURNOI:")
        print(f"  - Nombre de decks: {len(tournament_data.get('Decks', []))}")
        print(f"  - Format: Modern")

        # Analyser tous les decks
        archetype_results = []
        orchestrator.format = "Modern"

        for i, deck in enumerate(tournament_data.get("Decks", [])):
            mainboard = deck.get("Mainboard", [])
            if mainboard:
                # Step 2: Classification d'archétype
                archetype = orchestrator._classify_archetype(mainboard)

                result = {
                    "deck_id": i + 1,
                    "player": deck.get("PlayerName", f"Player {i+1}"),
                    "archetype": archetype,
                    "mainboard_cards": len(mainboard),
                    "key_cards": [card.get("CardName", "") for card in mainboard[:5]],
                }
                archetype_results.append(result)

        # Créer un DataFrame pour l'analyse
        df = pd.DataFrame(archetype_results)

        print(f"\n🎯 RÉSULTATS STEP 2 - CLASSIFICATION D'ARCHÉTYPES:")
        print("=" * 60)

        # Afficher quelques exemples
        print("\n📋 EXEMPLES DE CLASSIFICATION:")
        for _, row in df.head(5).iterrows():
            print(f"  Deck {row['deck_id']}: {row['player']}")
            print(f"    → Archétype: {row['archetype']}")
            print(f"    → Cartes clés: {', '.join(row['key_cards'])}")
            print()

        # Statistiques des archétypes
        archetype_counts = df["archetype"].value_counts()
        print("📊 RÉPARTITION DES ARCHÉTYPES:")
        print("-" * 40)
        for archetype, count in archetype_counts.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"  {archetype}: {count} decks ({percentage:.1f}%)")

        # Métriques de diversité
        total_archetypes = len(archetype_counts)
        most_common_archetype = archetype_counts.iloc[0]
        diversity_score = (total_archetypes / len(df)) * 100

        print(f"\n📈 MÉTRIQUES DE DIVERSITÉ:")
        print(f"  - Nombre total d'archétypes: {total_archetypes}")
        print(
            f"  - Archétype le plus joué: {archetype_counts.index[0]} ({most_common_archetype} decks)"
        )
        print(f"  - Score de diversité: {diversity_score:.1f}%")

        # Test avec différents formats
        print(f"\n🎯 TEST MULTI-FORMATS:")
        test_deck = [
            {"CardName": "Monastery Swiftspear", "Count": 4},
            {"CardName": "Lightning Bolt", "Count": 4},
            {"CardName": "Lava Spike", "Count": 4},
            {"CardName": "Mountain", "Count": 20},
        ]

        for format_name in ["Standard", "Modern", "Pioneer"]:
            orchestrator.format = format_name
            archetype = orchestrator._classify_archetype(test_deck)
            print(f"  {format_name}: {archetype}")

        print(f"\n✅ STEP 2 TERMINÉE AVEC SUCCÈS!")
        print(f"📋 {len(df)} decks classifiés")
        print(f"🎯 {total_archetypes} archétypes différents identifiés")

        return df

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


if __name__ == "__main__":
    test_step2_demo()
