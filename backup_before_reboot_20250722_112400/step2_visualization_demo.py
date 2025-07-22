#!/usr/bin/env python3
"""
🎯 STEP 2 VISUALIZATION - Démonstration visuelle de la Step 2
Génère des graphiques pour montrer les résultats de la classification d'archétypes
"""

import json
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append("src")

from orchestrator import ManalyticsOrchestrator


def create_step2_visualizations():
    """Crée des visualisations pour la Step 2"""

    print("🎯 STEP 2: DATA TREATMENT - VISUALISATIONS")
    print("=" * 60)

    # Initialiser l'orchestrator
    orchestrator = ManalyticsOrchestrator()

    # Charger un tournoi Modern
    tournament_file = "./temp_fbettega/MTG_decklistcache/Tournaments/MTGmelee/2025/06/30/1o-torneio-13a-liga-arena-guardians-modern-332615-2025-06-30.json"

    try:
        with open(tournament_file, "r") as f:
            tournament_data = json.load(f)

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

        # Créer un DataFrame
        df = pd.DataFrame(archetype_results)

        # 1. Graphique en camembert des archétypes
        archetype_counts = df["archetype"].value_counts()

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=archetype_counts.index,
                    values=archetype_counts.values,
                    hole=0.3,
                    textinfo="label+percent",
                    textposition="inside",
                )
            ]
        )

        fig_pie.update_layout(
            title="🎯 STEP 2: Répartition des Archétypes (Modern)",
            title_x=0.5,
            width=800,
            height=600,
            showlegend=True,
        )

        # 2. Graphique en barres des archétypes
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    x=archetype_counts.index,
                    y=archetype_counts.values,
                    text=archetype_counts.values,
                    textposition="auto",
                    marker_color="lightblue",
                )
            ]
        )

        fig_bar.update_layout(
            title="📊 STEP 2: Nombre de Decks par Archétype",
            title_x=0.5,
            xaxis_title="Archétype",
            yaxis_title="Nombre de Decks",
            width=1000,
            height=600,
            xaxis={"tickangle": 45},
        )

        # 3. Graphique de diversité
        diversity_data = {
            "Métrique": ["Archétypes Uniques", "Decks Classifiés", "Diversité (%)"],
            "Valeur": [
                len(archetype_counts),
                len(df),
                (len(archetype_counts) / len(df)) * 100,
            ],
        }

        fig_diversity = go.Figure(
            data=[
                go.Bar(
                    x=diversity_data["Métrique"],
                    y=diversity_data["Valeur"],
                    text=[f"{v:.1f}" for v in diversity_data["Valeur"]],
                    textposition="auto",
                    marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1"],
                )
            ]
        )

        fig_diversity.update_layout(
            title="📈 STEP 2: Métriques de Diversité",
            title_x=0.5,
            yaxis_title="Valeur",
            width=600,
            height=400,
        )

        # 4. Tableau des résultats
        fig_table = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "Deck ID",
                            "Joueur",
                            "Archétype",
                            "Cartes",
                            "Cartes Clés",
                        ],
                        fill_color="paleturquoise",
                        align="left",
                        font=dict(size=12),
                    ),
                    cells=dict(
                        values=[
                            df["deck_id"].tolist(),
                            df["player"].tolist(),
                            df["archetype"].tolist(),
                            df["mainboard_cards"].tolist(),
                            [" | ".join(cards) for cards in df["key_cards"]],
                        ],
                        fill_color="lavender",
                        align="left",
                        font=dict(size=10),
                    ),
                )
            ]
        )

        fig_table.update_layout(
            title="📋 STEP 2: Résultats de Classification",
            title_x=0.5,
            width=1200,
            height=600,
        )

        # Sauvegarder les graphiques
        output_dir = "step2_demo_output"
        import os

        os.makedirs(output_dir, exist_ok=True)

        fig_pie.write_html(f"{output_dir}/step2_archetype_pie.html")
        fig_bar.write_html(f"{output_dir}/step2_archetype_bar.html")
        fig_diversity.write_html(f"{output_dir}/step2_diversity_metrics.html")
        fig_table.write_html(f"{output_dir}/step2_classification_table.html")

        # Créer un rapport HTML complet
        create_step2_report(df, archetype_counts, output_dir)

        print(f"✅ Visualisations créées dans le dossier: {output_dir}")
        print(f"📊 {len(df)} decks analysés")
        print(f"🎯 {len(archetype_counts)} archétypes identifiés")

        return df

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def create_step2_report(df, archetype_counts, output_dir):
    """Crée un rapport HTML complet pour la Step 2"""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 STEP 2: DATA TREATMENT - Rapport</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            .archetype-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }}
            .archetype-item {{ padding: 10px; border: 1px solid #eee; border-radius: 5px; }}
            iframe {{ width: 100%; height: 600px; border: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 STEP 2: DATA TREATMENT</h1>
            <h2>Classification d'Archétypes MTGO</h2>
            <p>Rapport généré automatiquement par Manalytics</p>
        </div>

        <div class="section">
            <h3>📊 Résumé de l'Analyse</h3>
            <div class="metric">
                <strong>Decks Analysés:</strong> {len(df)}
            </div>
            <div class="metric">
                <strong>Archétypes Identifiés:</strong> {len(archetype_counts)}
            </div>
            <div class="metric">
                <strong>Score de Diversité:</strong> {(len(archetype_counts) / len(df)) * 100:.1f}%
            </div>
        </div>

        <div class="section">
            <h3>📈 Visualisations</h3>
            <iframe src="step2_archetype_pie.html"></iframe>
            <iframe src="step2_archetype_bar.html"></iframe>
            <iframe src="step2_diversity_metrics.html"></iframe>
        </div>

        <div class="section">
            <h3>🎯 Répartition des Archétypes</h3>
            <div class="archetype-list">
    """

    for archetype, count in archetype_counts.items():
        percentage = (count / len(df)) * 100
        html_content += f"""
                <div class="archetype-item">
                    <strong>{archetype}</strong><br>
                    {count} decks ({percentage:.1f}%)
                </div>
        """

    html_content += """
            </div>
        </div>

        <div class="section">
            <h3>📋 Détails de Classification</h3>
            <iframe src="step2_classification_table.html"></iframe>
        </div>

        <div class="section">
            <h3>🔧 Composants de la Step 2</h3>
            <ul>
                <li><strong>MTGOArchetypeParser:</strong> Classifieur principal basé sur MTGOFormatData</li>
                <li><strong>ArchetypeEngine:</strong> Classifieur de fallback</li>
                <li><strong>MTGOClassifier:</strong> Classifieur de dernier recours</li>
                <li><strong>Color Integration:</strong> Ajout automatique des couleurs aux archétypes</li>
            </ul>
        </div>
    </body>
    </html>
    """

    with open(f"{output_dir}/step2_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    create_step2_visualizations()
