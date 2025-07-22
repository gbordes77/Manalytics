#!/usr/bin/env python3
"""
🎯 TEST INTÉGRATION STEP 2 - Template Principal
Teste l'intégration du graphique de classification détaillée dans le template principal
"""

import asyncio
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.append("src")

from orchestrator import ManalyticsOrchestrator
from python.visualizations.metagame_charts import MetagameChartsGenerator


def test_step2_integration():
    """Teste l'intégration de la Step 2 dans le template principal"""

    print("🎯 TEST INTÉGRATION STEP 2 - Template Principal")
    print("=" * 60)

    # Initialiser l'orchestrator
    orchestrator = ManalyticsOrchestrator()

    # Charger un tournoi Standard existant
    tournament_file = (
        "./Analyses/standard_analysis_2025-07-01_2025-07-07/decklists_detailed.json"
    )

    try:
        with open(tournament_file, "r") as f:
            tournament_data = json.load(f)

        print(f"📋 Analyse: Standard 2025-07-01 à 2025-07-07")
        print(f"📅 Période: 2025-07-01 à 2025-07-07")
        print(f"🎯 Format: Standard")

        # Traiter les decks avec la Step 2
        processed_decks = []
        orchestrator.format = "Standard"

        # Adapter au format des données d'analyse
        if isinstance(tournament_data, list):
            decks = tournament_data
        else:
            decks = tournament_data.get("decks", [])

        for i, deck in enumerate(decks):
            if isinstance(deck, dict):
                mainboard = deck.get("mainboard", [])
                if mainboard:
                    # Step 2: Classification d'archétype
                    archetype = orchestrator._classify_archetype(mainboard)

                    # Extraire les cartes clés
                    key_cards = [
                        card.get("CardName", card.get("name", ""))
                        for card in mainboard[:5]
                    ]

                    processed_deck = {
                        "deck_id": i + 1,
                        "player_name": deck.get("player_name", "Unknown"),
                        "archetype": archetype,
                        "mainboard_cards": len(mainboard),
                        "key_cards": key_cards,
                        "tournament_name": "Standard Analysis",
                        "result": deck.get("result", "N/A"),
                        "tournament_source": "Standard Analysis",
                        "tournament_id": f"standard_{i}",
                        "winrate": deck.get("winrate", 0.5),
                        "wins": deck.get("wins", 0),
                        "losses": deck.get("losses", 0),
                        "matches_played": deck.get("matches_played", 0),
                        "tournament_date": pd.to_datetime("2025-07-01"),
                        "mainboard": mainboard,
                        "sideboard": deck.get("sideboard", []),
                    }
                    processed_decks.append(processed_deck)

        # Créer un DataFrame
        df = pd.DataFrame(processed_decks)

        print(f"✅ {len(df)} decks traités avec la Step 2")

        # Générer les visualisations avec le nouveau graphique
        charts_generator = MetagameChartsGenerator()

        # Créer le dossier de sortie
        output_dir = "test_step2_integration_output"
        Path(output_dir).mkdir(exist_ok=True)

        # Générer tous les graphiques (incluant le nouveau)
        charts_result = charts_generator.generate_all_charts(df, output_dir)

        print(f"📊 Graphiques générés dans: {output_dir}")
        print(f"🎯 Graphiques créés: {list(charts_result['charts'].keys())}")

        # Vérifier que le nouveau graphique est présent
        if "step2_classification_table" in charts_result["charts"]:
            print("✅ Graphique Step 2 intégré avec succès!")
        else:
            print("❌ Graphique Step 2 manquant!")

        # Générer le dashboard principal avec le nouveau graphique
        dashboard_path = orchestrator.generate_dashboard(output_dir, df)

        print(f"🎯 Dashboard principal généré: {dashboard_path}")

        # Afficher quelques statistiques
        print(f"\n📈 STATISTIQUES:")
        print(f"  - Decks analysés: {len(df)}")
        print(f"  - Archétypes identifiés: {df['archetype'].nunique()}")
        print(
            f"  - Score de diversité: {(df['archetype'].nunique() / len(df)) * 100:.1f}%"
        )

        # Afficher les archétypes trouvés
        archetype_counts = df["archetype"].value_counts()
        print(f"\n🎯 ARCHÉTYPES IDENTIFIÉS:")
        for archetype, count in archetype_counts.head(5).items():
            percentage = (count / len(df)) * 100
            print(f"  - {archetype}: {count} decks ({percentage:.1f}%)")

        print(f"\n✅ TEST TERMINÉ AVEC SUCCÈS!")
        print(f"📁 Résultats dans: {output_dir}")

        return df, charts_result

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, None


if __name__ == "__main__":
    test_step2_integration()
