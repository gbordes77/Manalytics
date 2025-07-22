#!/usr/bin/env python3
"""
Génération d'un rapport HTML des tournois scrapés
Affiche tous les tournois par source avec liens cliquables
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_scraped_data():
    """Charge les données scrapées depuis le cache"""
    data_dir = Path("data/processed")

    # Charger le résumé
    summary_file = data_dir / "scraping_summary_standard_july_2025.json"
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Charger les données MTGO
    mtgo_file = data_dir / "mtgo_standard_july_2025.json"
    mtgo_data = []
    if mtgo_file.exists():
        with open(mtgo_file, "r", encoding="utf-8") as f:
            mtgo_data = json.load(f)

    # Charger les données Melee (si elles existent)
    melee_file = data_dir / "melee_standard_july_2025.json"
    melee_data = []
    if melee_file.exists():
        with open(melee_file, "r", encoding="utf-8") as f:
            melee_data = json.load(f)

    return summary, mtgo_data, melee_data


def categorize_mtgo_tournaments(mtgo_data):
    """Catégorise les tournois MTGO"""
    leagues_5_0 = []
    challenges = []
    autres = []

    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")
        decks = tournament_entry.get("decks", [])

        # Vérifier si c'est une League 5-0
        if "League" in name:
            # Vérifier s'il y a au moins un deck 5-0
            has_5_0 = any(deck.get("Result") == "5-0" for deck in decks)
            if has_5_0:
                leagues_5_0.append(tournament_entry)
            else:
                autres.append(tournament_entry)
        elif "Challenge" in name:
            challenges.append(tournament_entry)
        else:
            autres.append(tournament_entry)

    return leagues_5_0, challenges, autres


def generate_html_report(summary, mtgo_data, melee_data):
    """Génère le rapport HTML"""

    # Catégoriser les tournois MTGO
    leagues_5_0, challenges, autres_mtgo = categorize_mtgo_tournaments(mtgo_data)

    # Compter les totaux
    total_tournaments = len(mtgo_data) + len(melee_data)
    total_melee = len(melee_data)
    total_leagues_5_0 = len(leagues_5_0)
    total_challenges = len(challenges)
    total_autres_mtgo = len(autres_mtgo)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Tournois Standard - Juillet 2025</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary h2 {{
            color: #34495e;
            margin-top: 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-card {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2980b9;
        }}
        .stat-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .tournament-list {{
            display: grid;
            gap: 15px;
        }}
        .tournament-card {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .tournament-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .tournament-name {{
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .tournament-name a {{
            color: #2980b9;
            text-decoration: none;
        }}
        .tournament-name a:hover {{
            text-decoration: underline;
        }}
        .tournament-info {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .deck-count {{
            background-color: #3498db;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            display: inline-block;
            margin-top: 5px;
        }}
        .empty-section {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-radius: 8px;
            font-style: italic;
        }}
        .melee-card {{ border-left: 4px solid #e74c3c; }}
        .league-card {{ border-left: 4px solid #27ae60; }}
        .challenge-card {{ border-left: 4px solid #f39c12; }}
        .other-card {{ border-left: 4px solid #9b59b6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Rapport Tournois Standard - Juillet 2025</h1>

        <div class="summary">
            <h2>📊 Résumé du Scraping</h2>
            <p><strong>Période :</strong> {summary['periode']['debut'][:10]} au {summary['periode']['fin'][:10]}</p>
            <p><strong>Format :</strong> {summary['format']}</p>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_tournaments}</div>
                    <div class="stat-label">Total Tournois</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_melee}</div>
                    <div class="stat-label">Melee.gg</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_leagues_5_0}</div>
                    <div class="stat-label">MTGO League 5-0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_challenges}</div>
                    <div class="stat-label">MTGO Challenges</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_autres_mtgo}</div>
                    <div class="stat-label">MTGO Autres</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{summary['total']['decks']}</div>
                    <div class="stat-label">Total Decks</div>
                </div>
            </div>
        </div>
"""

    # Section Melee.gg
    html += """
        <div class="section">
            <h3>🎯 Tournois Melee.gg</h3>
"""
    if melee_data:
        html += '<div class="tournament-list">'
        for tournament_entry in melee_data:
            tournament = tournament_entry.get("tournament", {})
            name = tournament.get("Name", "Nom non disponible")
            uri = tournament.get("Uri", "#")
            date = tournament.get("Date", "")
            deck_count = len(tournament_entry.get("decks", []))

            html += f"""
                <div class="tournament-card melee-card">
                    <div class="tournament-name">
                        <a href="{uri}" target="_blank">{name}</a>
                    </div>
                    <div class="tournament-info">
                        📅 {date} | 🌐 Melee.gg
                        <span class="deck-count">{deck_count} decks</span>
                    </div>
                </div>
            """
        html += "</div>"
    else:
        html += (
            '<div class="empty-section">Aucun tournoi Melee.gg dans cette période</div>'
        )

    html += "</div>"

    # Section MTGO League 5-0
    html += """
        <div class="section">
            <h3>🏅 MTGO League 5-0</h3>
"""
    if leagues_5_0:
        html += '<div class="tournament-list">'
        for tournament_entry in leagues_5_0:
            tournament = tournament_entry.get("tournament", {})
            name = tournament.get("Name", "Nom non disponible")
            uri = tournament.get("Uri", "#")
            date = tournament.get("Date", "")
            deck_count = len(tournament_entry.get("decks", []))

            html += f"""
                <div class="tournament-card league-card">
                    <div class="tournament-name">
                        <a href="{uri}" target="_blank">{name}</a>
                    </div>
                    <div class="tournament-info">
                        📅 {date} | 🥇 MTGO League
                        <span class="deck-count">{deck_count} decks</span>
                    </div>
                </div>
            """
        html += "</div>"
    else:
        html += '<div class="empty-section">Aucune League 5-0 dans cette période</div>'

    html += "</div>"

    # Section MTGO Challenges
    html += """
        <div class="section">
            <h3>⚔️ MTGO Challenges</h3>
"""
    if challenges:
        html += '<div class="tournament-list">'
        for tournament_entry in challenges:
            tournament = tournament_entry.get("tournament", {})
            name = tournament.get("Name", "Nom non disponible")
            uri = tournament.get("Uri", "#")
            date = tournament.get("Date", "")
            deck_count = len(tournament_entry.get("decks", []))

            html += f"""
                <div class="tournament-card challenge-card">
                    <div class="tournament-name">
                        <a href="{uri}" target="_blank">{name}</a>
                    </div>
                    <div class="tournament-info">
                        📅 {date} | ⚔️ MTGO Challenge
                        <span class="deck-count">{deck_count} decks</span>
                    </div>
                </div>
            """
        html += "</div>"
    else:
        html += '<div class="empty-section">Aucun Challenge dans cette période</div>'

    html += "</div>"

    # Section MTGO Autres
    html += """
        <div class="section">
            <h3>🎲 MTGO Autres Tournois</h3>
"""
    if autres_mtgo:
        html += '<div class="tournament-list">'
        for tournament_entry in autres_mtgo:
            tournament = tournament_entry.get("tournament", {})
            name = tournament.get("Name", "Nom non disponible")
            uri = tournament.get("Uri", "#")
            date = tournament.get("Date", "")
            deck_count = len(tournament_entry.get("decks", []))

            html += f"""
                <div class="tournament-card other-card">
                    <div class="tournament-name">
                        <a href="{uri}" target="_blank">{name}</a>
                    </div>
                    <div class="tournament-info">
                        📅 {date} | 🎲 MTGO Autre
                        <span class="deck-count">{deck_count} decks</span>
                    </div>
                </div>
            """
        html += "</div>"
    else:
        html += '<div class="empty-section">Aucun autre tournoi MTGO dans cette période</div>'

    html += "</div>"

    # Footer
    html += f"""
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d;">
            <p>📊 Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            <p>🔗 Sources: Melee.gg + MTGO | 🎯 Format: Standard | 📅 Période: 1er-20 juillet 2025</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def main():
    """Fonction principale"""
    print("🚀 Génération du rapport HTML des tournois...")

    try:
        # Charger les données
        summary, mtgo_data, melee_data = load_scraped_data()

        # Générer le HTML
        html_content = generate_html_report(summary, mtgo_data, melee_data)

        # Sauvegarder le fichier
        output_file = Path("rapport_tournois_standard_juillet_2025.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Rapport généré avec succès : {output_file}")
        print(f"📊 Résumé :")
        print(f"   • Total tournois : {summary['total']['tournois']}")
        print(f"   • Total decks : {summary['total']['decks']}")
        print(f"   • Melee : {summary['sources']['melee']['tournois']} tournois")
        print(f"   • MTGO : {summary['sources']['mtgo']['tournois']} tournois")

    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
