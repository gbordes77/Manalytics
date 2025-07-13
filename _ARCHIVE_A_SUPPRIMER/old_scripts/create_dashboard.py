#!/usr/bin/env python3
"""
Générateur de tableau de bord HTML complet
Combine toutes les visualisations Manalytics en un seul rapport
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def create_dashboard_html():
    """Crée le tableau de bord HTML complet"""
    
    # Charger les métadonnées
    try:
        with open('real_data/complete_dataset.json', 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        # Statistiques générales
        total_tournaments = df['tournament_id'].nunique()
        total_players = len(df)
        total_matches = df['matches_played'].sum()
        archetypes = sorted(df['archetype'].unique())
        
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return
    
    # Template HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Tableau de Bord Standard</title>
    <style>
        :root {{
            /* Palette heatmap */
            --c-50: #762a83;
            --c-40: #8e4d99;
            --c-30: #a66fb0;
            --c-20: #be91c7;
            --c-10: #d6b3de;
            --c0: #f7f7f7;
            --c10: #c7e9c0;
            --c20: #a1d99b;
            --c30: #7bc87c;
            --c40: #4eb265;
            --c50: #1b7837;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--c-50) 0%, var(--c50) 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--c-50);
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .visualization-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }}
        
        .viz-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .viz-header {{
            background: var(--c0);
            padding: 1.5rem;
            border-bottom: 1px solid #eee;
        }}
        
        .viz-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--c-50);
            margin: 0;
        }}
        
        .viz-description {{
            color: #666;
            margin: 0.5rem 0 0 0;
            font-size: 0.95rem;
        }}
        
        .viz-content {{
            padding: 0;
            height: 600px;
        }}
        
        .viz-iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .archetype-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .archetype-tag {{
            background: var(--c10);
            color: var(--c-50);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        .export-links {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .export-link {{
            background: var(--c50);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }}
        
        .export-link:hover {{
            background: var(--c40);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics</h1>
        <p>Analyse complète du métagame Standard - Données réelles de tournois</p>
    </div>
    
    <div class="container">
        <!-- Statistiques générales -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_tournaments}</div>
                <div class="stat-label">Tournois</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_players}</div>
                <div class="stat-label">Joueurs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_matches}</div>
                <div class="stat-label">Matchs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(archetypes)}</div>
                <div class="stat-label">Archétypes</div>
            </div>
        </div>
        
        <!-- Archétypes détectés -->
        <div class="viz-card">
            <div class="viz-header">
                <h3 class="viz-title">Archétypes Détectés</h3>
                <p class="viz-description">Classification automatique des decks basée sur les données réelles</p>
            </div>
            <div style="padding: 1.5rem;">
                <div class="archetype-list">
                    {' '.join([f'<span class="archetype-tag">{arch}</span>' for arch in archetypes])}
                </div>
            </div>
        </div>
        
        <!-- Visualisations -->
        <div class="visualization-grid">
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">📊 Matrice de Matchups</h3>
                    <p class="viz-description">Heatmap interactive des matchups avec intervalles de confiance 95%</p>
                    <div class="export-links">
                        <a href="matchup_matrix.csv" class="export-link">📄 CSV</a>
                        <a href="matchup_matrix.json" class="export-link">📋 JSON</a>
                    </div>
                </div>
                <div class="viz-content">
                    <iframe src="matchup_matrix.html" class="viz-iframe"></iframe>
                </div>
            </div>
            
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">📈 Part de Métagame</h3>
                    <p class="viz-description">Répartition des archétypes dans le métagame Standard</p>
                    <div class="export-links">
                        <a href="archetype_stats.csv" class="export-link">📄 CSV</a>
                        <a href="archetype_stats.json" class="export-link">📋 JSON</a>
                    </div>
                </div>
                <div class="viz-content">
                    <iframe src="metagame_share.html" class="viz-iframe"></iframe>
                </div>
            </div>
            
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🎯 Winrates avec Intervalles de Confiance</h3>
                    <p class="viz-description">Performance des archétypes avec barres d'erreur (IC 95%)</p>
                </div>
                <div class="viz-content">
                    <iframe src="winrate_confidence.html" class="viz-iframe"></iframe>
                </div>
            </div>
            
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🏆 Classification par Tiers</h3>
                    <p class="viz-description">Scatter plot des archétypes classés par performance (borne inférieure IC)</p>
                </div>
                <div class="viz-content">
                    <iframe src="tiers_scatter.html" class="viz-iframe"></iframe>
                </div>
            </div>
            
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">💫 Winrate vs Présence</h3>
                    <p class="viz-description">Bubble chart montrant la relation performance/popularité</p>
                </div>
                <div class="viz-content">
                    <iframe src="bubble_winrate_presence.html" class="viz-iframe"></iframe>
                </div>
            </div>
            
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🌟 Top Archétypes Performants</h3>
                    <p class="viz-description">Archétypes avec les meilleures performances</p>
                    <div class="export-links">
                        <a href="top_performers.csv" class="export-link">📄 CSV</a>
                        <a href="top_performers.json" class="export-link">📋 JSON</a>
                    </div>
                </div>
                <div class="viz-content">
                    <iframe src="top_5_0.html" class="viz-iframe"></iframe>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        <p>Données 100% réelles • Intervalles de confiance Wilson • Palette heatmap violet→vert</p>
        <p>Sources: melee.gg, mtgo.com, topdeck.gg</p>
    </div>
</body>
</html>
    """
    
    # Sauvegarder le tableau de bord
    output_path = Path("analysis_output/dashboard_complete.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Tableau de bord créé: {output_path}")
    return output_path

if __name__ == "__main__":
    dashboard_path = create_dashboard_html()
    print(f"🚀 Ouvrir le tableau de bord: {dashboard_path}") 