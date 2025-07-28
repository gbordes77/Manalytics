#!/usr/bin/env python3
"""
Analyse complète juillet 1-21 en utilisant :
1. Les données du cache (déjà processées)
2. Les données listener de Jiliac
3. Analyse par MATCHES (pas par decks)
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import math
from collections import defaultdict

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS, blend_colors
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class CompleteJulyAnalyzer:
    """Analyse complète avec cache + listener"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        
    def load_listener_data(self):
        """Charge les données listener de Jiliac"""
        print("📊 Chargement des données listener...")
        
        listener_path = Path("jiliaclistener")
        count = 0
        
        for day_folder in listener_path.iterdir():
            if day_folder.is_dir() and day_folder.name.isdigit():
                day = int(day_folder.name)
                if 1 <= day <= 21:  # Juillet 1-21
                    for file in day_folder.glob("*standard*.json"):
                        with open(file, 'r') as f:
                            data = json.load(f)
                        
                        tournament_id = data['Tournament']['Id']
                        self.listener_data[tournament_id] = {
                            'date': datetime.strptime(data['Tournament']['Date'][:10], '%Y-%m-%d'),
                            'name': data['Tournament']['Name'],
                            'rounds': data['Rounds']
                        }
                        count += 1
        
        print(f"✅ Chargé {count} tournois du listener")
        
        # Debug: afficher quelques tournois listener
        print("\nExemples de tournois listener:")
        for tid, data in list(self.listener_data.items())[:5]:
            print(f"  - ID: {tid}, Name: {data['name']}, Date: {data['date'].strftime('%Y-%m-%d')}")
        
        return count
    
    def load_cache_data(self):
        """Charge les données depuis notre cache"""
        print("\n📋 Chargement des données du cache...")
        
        # Charger les tournois de juillet 1-21
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21, 23, 59, 59)
        
        # Récupérer depuis le cache
        tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        
        # Exclure les leagues
        competitive_tournaments = []
        for t in tournaments:
            if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower():
                competitive_tournaments.append(t)
        
        print(f"✅ Trouvé {len(competitive_tournaments)} tournois compétitifs dans le cache")
        
        # Charger les decklists pour chaque tournoi
        for tournament in competitive_tournaments:
            month_key = tournament.date.strftime("%Y-%m")
            decklists_file = Path(f"data/cache/decklists/{month_key}.json")
            
            if decklists_file.exists():
                with open(decklists_file, 'r') as f:
                    month_data = json.load(f)
                
                # Chercher par ID string ou nom
                for key in month_data:
                    if (str(tournament.id) in key or 
                        tournament.name.lower() in key.lower() or
                        (hasattr(tournament, 'source_id') and str(tournament.source_id) in key)):
                        self.tournament_cache_data[tournament.id] = month_data[key]
                        break
        
        print(f"✅ Chargé les decklists pour {len(self.tournament_cache_data)} tournois")
        
        # Debug: afficher les tournois du cache
        print("\nTournois dans le cache:")
        for tid, data in self.tournament_cache_data.items():
            print(f"  - ID: {tid}, Name: {data.get('name', 'N/A')}, Date: {data.get('date', 'N/A')}")
    
    def merge_and_analyze(self) -> Dict:
        """Merge les données cache + listener et analyse par MATCHES"""
        print("\n🔄 Merge et analyse des données...")
        
        # Structure pour les matchups
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        archetype_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'decks': 0,
            'tournaments': set()
        })
        
        total_matches = 0
        matched_tournaments = 0
        
        # Pour chaque tournoi du listener
        for listener_id, listener_tournament in self.listener_data.items():
            matched = False
            
            # Chercher le tournoi correspondant dans le cache
            for cache_id, cache_data in self.tournament_cache_data.items():
                # Match par ID dans le cache_id
                # Les IDs du cache peuvent être : "1812803681" ou "standard-challenge-32-2025-07-1812803681"
                if (str(listener_id) in cache_id or 
                    (str(listener_id)[:4] in cache_id and cache_id.endswith(str(listener_id)))):
                    
                    matched = True
                    matched_tournaments += 1
                    
                    print(f"✅ Matched: Listener {listener_id} → Cache {cache_id}")
                    
                    # Créer mapping player -> archetype
                    player_archetypes = {}
                    for deck in cache_data.get('decklists', []):
                        player = deck.get('player')
                        archetype = deck.get('archetype') or 'Unknown'
                        if player and archetype != 'Unknown':
                            player_archetypes[player] = archetype
                            archetype_stats[archetype]['decks'] += 1
                            archetype_stats[archetype]['tournaments'].add(listener_id)
                    
                    # Analyser les matchups du listener
                    for round_data in listener_tournament['rounds']:
                        for match in round_data['Matches']:
                            player1 = match['Player1']
                            player2 = match['Player2']
                            result = match['Result']
                            
                            if player2 == "BYE" or not result or result == "0-0-0":
                                continue
                            
                            arch1 = player_archetypes.get(player1, 'Unknown')
                            arch2 = player_archetypes.get(player2, 'Unknown')
                            
                            if arch1 == 'Unknown' or arch2 == 'Unknown':
                                continue
                            
                            # Parse result
                            parts = result.split('-')
                            if len(parts) >= 2:
                                p1_wins = int(parts[0])
                                p2_wins = int(parts[1])
                                
                                total_matches += 1
                                
                                # Update stats
                                archetype_stats[arch1]['matches'] += 1
                                archetype_stats[arch2]['matches'] += 1
                                
                                if p1_wins > p2_wins:
                                    matchup_data[arch1][arch2]['wins'] += 1
                                    matchup_data[arch2][arch1]['losses'] += 1
                                    archetype_stats[arch1]['wins'] += 1
                                    archetype_stats[arch2]['losses'] += 1
                                else:
                                    matchup_data[arch1][arch2]['losses'] += 1
                                    matchup_data[arch2][arch1]['wins'] += 1
                                    archetype_stats[arch1]['losses'] += 1
                                    archetype_stats[arch2]['wins'] += 1
                    break
        
        print(f"✅ Matched {matched_tournaments}/{len(self.listener_data)} tournois")
        print(f"✅ Analysé {total_matches} matches")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches,
            'matched_tournaments': matched_tournaments
        }
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec toutes les visualisations"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Calculer les pourcentages
        meta_data = []
        for archetype, stats in analysis['archetype_stats'].items():
            percentage = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            win_rate = (stats['wins'] / stats['matches'] * 100) if stats['matches'] > 0 else 50
            
            # Wilson CI
            if stats['matches'] > 0:
                p = stats['wins'] / stats['matches']
                z = 1.96
                n = stats['matches']
                
                denominator = 1 + z**2/n
                center = (p + z**2/(2*n)) / denominator
                margin = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denominator
                
                ci_lower = max(0, (center - margin) * 100)
                ci_upper = min(100, (center + margin) * 100)
            else:
                ci_lower, ci_upper = 0, 100
            
            meta_data.append((archetype, {
                'matches': stats['matches'],
                'percentage': percentage,
                'win_rate': win_rate,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'decks': stats['decks'],
                'tournaments': len(stats['tournaments'])
            }))
        
        meta_data.sort(key=lambda x: x[1]['percentage'], reverse=True)
        
        # Générer HTML avec le bon template
        html = self._generate_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_complete_analysis_with_matchups.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse complète générée!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        return output_path
    
    def _generate_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML complet avec toutes les visualisations"""
        # Utiliser le template de référence
        template_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .visualization-container {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .summary-value {
                font-size: 3em;
                font-weight: 700;
                margin: 10px 0;
            }
            .summary-label {
                font-size: 1.1em;
                opacity: 0.9;
            }
            .info-box {
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
        </style>
        """
        
        # Créer les visualisations
        viz_html = []
        
        # 1. Pie Chart
        viz_html.append(self._create_pie_chart(meta_data))
        
        # 2. Bar Chart  
        viz_html.append(self._create_bar_chart(meta_data))
        
        # 3. Win Rate avec CI
        viz_html.append(self._create_winrate_chart(meta_data))
        
        # 4. Matchup Matrix
        viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data))
        
        # 5. Scatter Win Rate vs Presence
        viz_html.append(self._create_scatter_chart(meta_data))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Complete July Analysis with Real Matchups</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Complete Analysis with Cache + Listener Data</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Real matchup data from {analysis['matched_tournaments']} tournaments</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Matches Analyzed</div>
                <div class="summary-value">{analysis['total_matches']:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Matched Tournaments</div>
                <div class="summary-value">{analysis['matched_tournaments']}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Archetypes</div>
                <div class="summary-value">{len(analysis['archetype_stats'])}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Decks</div>
                <div class="summary-value">{sum(s['decks'] for s in analysis['archetype_stats'].values())}</div>
            </div>
        </div>
        
        {''.join(viz_html)}
        
        <div class="info-box">
            <h2>📊 Top 5 Archetypes</h2>
            <ol>
                {"".join(f'<li><strong>{arch}</strong> - {data["percentage"]:.1f}% ({data["matches"]} matches, {data["win_rate"]:.1f}% WR)</li>' for arch, data in meta_data[:5])}
            </ol>
        </div>
        
        <div class="info-box">
            <h2>📋 Methodology</h2>
            <ul>
                <li><strong>Data Sources:</strong> Cache (processed decklists) + Listener (match results)</li>
                <li><strong>Analysis Method:</strong> By MATCHES (not by decks)</li>
                <li><strong>Period:</strong> July 1-21, 2025</li>
                <li><strong>Exclusions:</strong> Leagues and casual events</li>
                <li><strong>Confidence Intervals:</strong> Wilson score method (95%)</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _create_pie_chart(self, meta_data: List) -> str:
        """Crée le pie chart du métagame"""
        # Top 10 + Others
        labels = []
        values = []
        colors = []
        
        other_pct = 0
        for i, (archetype, data) in enumerate(meta_data):
            if i < 10 and data['percentage'] > 1:  # Au moins 1%
                labels.append(f"{archetype} ({data['percentage']:.1f}%)")
                values.append(data['percentage'])
                
                # Couleur MTG
                arch_colors = get_archetype_colors(archetype)
                if len(arch_colors) == 1:
                    color = MTG_COLORS.get(arch_colors[0], '#808080')
                else:
                    color = blend_colors(
                        MTG_COLORS.get(arch_colors[0], '#808080'),
                        MTG_COLORS.get(arch_colors[1], '#404040'),
                        0.7
                    )
                colors.append(color)
            else:
                other_pct += data['percentage']
        
        if other_pct > 0:
            labels.append(f"Others ({other_pct:.1f}%)")
            values.append(other_pct)
            colors.append('#808080')
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textposition='inside',
            textinfo='label',
            hovertemplate='<b>%{label}</b><br>Share: %{value:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '📊 Metagame Distribution (by Matches)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=False,
            width=800,
            height=600,
            margin=dict(t=100, b=50)
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="pie-chart")}</div>'
    
    def _create_bar_chart(self, meta_data: List) -> str:
        """Crée le bar chart des top archétypes"""
        # Top 15
        top_15 = [(a, d) for a, d in meta_data if d['matches'] >= 10][:15]
        
        archetypes = [a[0] for a in top_15]
        percentages = [a[1]['percentage'] for a in top_15]
        
        # Couleurs
        colors = []
        for archetype, _ in top_15:
            arch_colors = get_archetype_colors(archetype)
            if len(arch_colors) == 1:
                color = MTG_COLORS.get(arch_colors[0], '#808080')
            else:
                color = blend_colors(
                    MTG_COLORS.get(arch_colors[0], '#808080'),
                    MTG_COLORS.get(arch_colors[1], '#404040'),
                    0.6
                )
            colors.append(color)
        
        fig = go.Figure(data=[go.Bar(
            x=archetypes,
            y=percentages,
            marker=dict(color=colors, line=dict(color='black', width=1)),
            text=[f"{p:.1f}%" for p in percentages],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Presence: %{y:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '📈 Top 15 Archetypes by Match Presence',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Archetype', tickangle=-45),
            yaxis=dict(title='Presence %', range=[0, max(percentages) * 1.15] if percentages else [0, 10]),
            width=1000,
            height=600,
            margin=dict(b=150)
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="bar-chart")}</div>'
    
    def _create_winrate_chart(self, meta_data: List) -> str:
        """Crée le graphique des win rates avec CI"""
        # Filtrer archétypes avec assez de données
        filtered = [(a, d) for a, d in meta_data if d['matches'] >= 20][:20]
        filtered.sort(key=lambda x: x[1]['win_rate'], reverse=True)
        
        if not filtered:
            return '<div class="visualization-container"><p>Not enough data for win rate analysis</p></div>'
        
        archetypes = [a[0] for a in filtered]
        win_rates = [a[1]['win_rate'] for a in filtered]
        ci_lower = [a[1]['ci_lower'] for a in filtered]
        ci_upper = [a[1]['ci_upper'] for a in filtered]
        
        fig = go.Figure()
        
        # CI lines
        for i, archetype in enumerate(archetypes):
            fig.add_trace(go.Scatter(
                x=[ci_lower[i], ci_upper[i]],
                y=[archetype, archetype],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Points
        fig.add_trace(go.Scatter(
            x=win_rates,
            y=archetypes,
            mode='markers',
            marker=dict(
                size=10,
                color=win_rates,
                colorscale='RdYlGn',
                cmin=40,
                cmax=60,
                colorbar=dict(title="Win Rate %"),
                line=dict(color='black', width=1)
            ),
            text=[f"{wr:.1f}%" for wr in win_rates],
            hovertemplate='<b>%{y}</b><br>Win Rate: %{x:.1f}%<br>CI: [%{customdata[0]:.1f}%, %{customdata[1]:.1f}%]<extra></extra>',
            customdata=list(zip(ci_lower, ci_upper))
        ))
        
        fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '📊 Win Rates with 95% Confidence Intervals',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Win Rate %', range=[30, 70]),
            yaxis=dict(title='', autorange='reversed'),
            width=1000,
            height=max(600, len(archetypes) * 35),
            margin=dict(l=200)
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="winrate-chart")}</div>'
    
    def _create_matchup_matrix(self, matchup_data: Dict, meta_data: List) -> str:
        """Crée la matrice de matchups"""
        # Top 10 archétypes
        top_archetypes = [a[0] for a in meta_data[:10] if a[1]['matches'] >= 20]
        
        if len(top_archetypes) < 2:
            return '<div class="visualization-container"><p>Not enough data for matchup matrix</p></div>'
        
        # Créer matrice
        matrix = []
        hover_texts = []
        
        for arch1 in top_archetypes:
            row = []
            hover_row = []
            
            for arch2 in top_archetypes:
                if arch1 == arch2:
                    row.append(50)
                    hover_row.append(f"{arch1} vs {arch2}<br>Mirror Match: 50%")
                else:
                    if arch1 in matchup_data and arch2 in matchup_data[arch1]:
                        wins = matchup_data[arch1][arch2]['wins']
                        losses = matchup_data[arch1][arch2]['losses']
                        total = wins + losses
                        
                        if total > 0:
                            win_rate = (wins / total) * 100
                            row.append(win_rate)
                            hover_row.append(
                                f"{arch1} vs {arch2}<br>"
                                f"Win Rate: {win_rate:.1f}%<br>"
                                f"Matches: {total}"
                            )
                        else:
                            row.append(None)
                            hover_row.append(f"{arch1} vs {arch2}<br>No data")
                    else:
                        row.append(None)
                        hover_row.append(f"{arch1} vs {arch2}<br>No data")
            
            matrix.append(row)
            hover_texts.append(hover_row)
        
        # Créer heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=top_archetypes,
            y=top_archetypes,
            colorscale=[
                [0, '#d32f2f'],      # Red
                [0.4, '#ff9800'],    # Orange
                [0.5, '#ffeb3b'],    # Yellow
                [0.6, '#8bc34a'],    # Light green
                [1, '#2e7d32']       # Dark green
            ],
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            colorbar=dict(title='Win Rate %')
        ))
        
        # Annotations pour matchups extrêmes
        annotations = []
        for i, arch1 in enumerate(top_archetypes):
            for j, arch2 in enumerate(top_archetypes):
                if matrix[i][j] is not None and i != j:
                    value = matrix[i][j]
                    if value < 35 or value > 65:
                        annotations.append(
                            dict(
                                x=j,
                                y=i,
                                text=f"{value:.0f}",
                                showarrow=False,
                                font=dict(color='white', size=12)
                            )
                        )
        
        fig.update_layout(
            title={
                'text': '🎲 Real Matchup Matrix from Match Data',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Opponent', side='bottom', tickangle=-45),
            yaxis=dict(title='Your Deck', autorange='reversed'),
            width=1000,
            height=1000,
            annotations=annotations
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="matchup-matrix")}</div>'
    
    def _create_scatter_chart(self, meta_data: List) -> str:
        """Crée le scatter plot win rate vs presence"""
        # Filtrer archétypes avec assez de données
        plot_data = [(a, d) for a, d in meta_data if d['matches'] >= 10]
        
        if not plot_data:
            return '<div class="visualization-container"><p>Not enough data for scatter plot</p></div>'
        
        fig = go.Figure()
        
        for archetype, data in plot_data:
            # Couleur
            arch_colors = get_archetype_colors(archetype)
            if len(arch_colors) == 1:
                color = MTG_COLORS.get(arch_colors[0], '#808080')
            else:
                color = blend_colors(
                    MTG_COLORS.get(arch_colors[0], '#808080'),
                    MTG_COLORS.get(arch_colors[1], '#404040'),
                    0.7
                )
            
            fig.add_trace(go.Scatter(
                x=[data['percentage']],
                y=[data['win_rate']],
                mode='markers+text',
                marker=dict(
                    size=math.sqrt(data['matches']) * 3,
                    color=color,
                    line=dict(color='black', width=1)
                ),
                text=archetype if data['percentage'] > 3 else '',
                textposition='top center',
                name=archetype,
                hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Matches: %{customdata}<extra></extra>',
                customdata=[data['matches']]
            ))
        
        # Lignes de référence
        fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.3)
        fig.add_vline(x=5, line_dash="dash", line_color="blue", opacity=0.3)
        
        fig.update_layout(
            title={
                'text': '🎯 Win Rate vs Presence Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Presence %'),
            yaxis=dict(title='Win Rate %', range=[35, 65]),
            width=1200,
            height=800,
            showlegend=False
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="scatter-chart")}</div>'


if __name__ == "__main__":
    analyzer = CompleteJulyAnalyzer()
    analyzer.generate_complete_analysis()