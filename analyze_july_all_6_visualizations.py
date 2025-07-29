#!/usr/bin/env python3
"""
Analyse complète avec TOUTES les 6 visualisations standards
Basé sur analyze_july_complete_final.py avec ajout des visualisations manquantes
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import re
import math

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS, blend_colors
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class CompleteJulyAnalyzer:
    """Analyse complète avec les 6 visualisations standards"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        
    def extract_tournament_id(self, text: str) -> str:
        """Extraire l'ID numérique du tournoi depuis différents formats"""
        match = re.search(r'(\d{8})(?:\D|$)', str(text))
        if match:
            return match.group(1)
        match = re.search(r'(\d{8})', str(text))
        if match:
            return match.group(1)
        return None
        
    def load_listener_data(self):
        """Charge les données listener depuis data/MTGOData"""
        print("📊 Chargement des données listener depuis data/MTGOData...")
        
        mtgo_path = Path("data/MTGOData/2025/07")
        count = 0
        total_matches = 0
        
        for day in range(1, 22):  # Juillet 1-21
            day_folder = mtgo_path / f"{day:02d}"
            if not day_folder.exists():
                continue
                
            for json_file in day_folder.glob("*.json"):
                if 'standard' not in json_file.name.lower():
                    continue
                    
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                if data.get('Tournament') and data.get('Rounds'):
                    tournament_id = self.extract_tournament_id(data['Tournament'].get('Id', ''))
                    if tournament_id:
                        self.listener_data[tournament_id] = {
                            'tournament': data['Tournament'],
                            'rounds': data['Rounds'],
                            'date': datetime.fromisoformat(data['Tournament']['Date'].replace('Z', '+00:00'))
                        }
                        count += 1
                        
                        # Compter les matches
                        for round_data in data['Rounds']:
                            total_matches += len(round_data.get('Matches', []))
        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs au total")
    
    def load_cache_data(self):
        """Charge les données depuis notre cache"""
        print("\n📋 Chargement des données du cache...")
        
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21, 23, 59, 59)
        
        tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        
        competitive_tournaments = []
        for t in tournaments:
            if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower():
                competitive_tournaments.append(t)
        
        print(f"✅ Trouvé {len(competitive_tournaments)} tournois compétitifs dans la DB")
        
        cache_json_path = Path("data/cache/decklists/2025-07.json")
        if cache_json_path.exists():
            with open(cache_json_path, 'r') as f:
                month_data = json.load(f)
            
            print(f"📁 Trouvé {len(month_data)} entrées dans le cache JSON")
            
            for key, data in month_data.items():
                if data.get('format', '').lower() == 'standard' or 'standard' in key.lower():
                    tournament_id = self.extract_tournament_id(key)
                    if tournament_id:
                        self.tournament_cache_data[tournament_id] = {
                            'key': key,
                            'data': data,
                            'name': data.get('name', 'Unknown'),
                            'date': data.get('date', 'Unknown')
                        }
        
        print(f"✅ Chargé {len(self.tournament_cache_data)} tournois du cache avec IDs extraits")
    
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
            'tournaments': set(),
            'players': set(),
            'sideboard_cards': defaultdict(int)
        })
        
        matched_tournaments = 0
        total_matches = 0
        tournament_meta = defaultdict(lambda: defaultdict(int))
        
        # Pour chaque tournoi listener
        for listener_id, listener_tournament in self.listener_data.items():
            matched = False
            
            # Chercher dans le cache par ID extrait
            if listener_id in self.tournament_cache_data:
                matched = True
                matched_tournaments += 1
                cache_info = self.tournament_cache_data[listener_id]
                cache_data = cache_info['data']
                
                # Créer mapping player -> archetype et analyser les decks
                player_archetypes = {}
                for deck in cache_data.get('decklists', []):
                    player = deck.get('player')
                    archetype = deck.get('archetype') or 'Unknown'
                    if player and archetype != 'Unknown':
                        player_archetypes[player] = archetype
                        archetype_stats[archetype]['decks'] += 1
                        archetype_stats[archetype]['tournaments'].add(listener_id)
                        archetype_stats[archetype]['players'].add(player)
                        
                        # Analyser le sideboard
                        for card in deck.get('sideboard', []):
                            card_name = card.get('card_name', 'Unknown')
                            quantity = card.get('quantity', 1)
                            archetype_stats[archetype]['sideboard_cards'][card_name] += quantity
                
                # Compter le meta par tournoi
                tournament_date = listener_tournament['date']
                for archetype in set(player_archetypes.values()):
                    tournament_meta[tournament_date.strftime('%Y-%m-%d')][archetype] += 1
                
                # Analyser chaque round
                for round_data in listener_tournament['rounds']:
                    for match in round_data.get('Matches', []):
                        # Handle both formats: string players and object players
                        player1_data = match.get('Player1', '')
                        player2_data = match.get('Player2', '')
                        
                        if isinstance(player1_data, dict):
                            player1 = player1_data.get('Name', '')
                        else:
                            player1 = player1_data
                            
                        if isinstance(player2_data, dict):
                            player2 = player2_data.get('Name', '')
                        else:
                            player2 = player2_data
                            
                        result = match.get('Result', '')
                        
                        # Vérifier si on a les archétypes des deux joueurs
                        if player1 in player_archetypes and player2 in player_archetypes:
                            arch1 = player_archetypes[player1]
                            arch2 = player_archetypes[player2]
                            total_matches += 1
                            
                            # Analyser le résultat
                            if result:
                                try:
                                    # Extraire les scores
                                    parts = result.split('-')
                                    if len(parts) == 2:
                                        wins1 = int(parts[0])
                                        wins2 = int(parts[1])
                                    elif len(parts) == 3:  # Format avec draws
                                        wins1 = int(parts[0])
                                        wins2 = int(parts[1])
                                    else:
                                        continue
                                    
                                    # Enregistrer les résultats par archétype
                                    archetype_stats[arch1]['matches'] += 1
                                    archetype_stats[arch2]['matches'] += 1
                                    
                                    if wins1 > wins2:
                                        archetype_stats[arch1]['wins'] += 1
                                        archetype_stats[arch2]['losses'] += 1
                                        matchup_data[arch1][arch2]['wins'] += 1
                                        matchup_data[arch2][arch1]['losses'] += 1
                                    elif wins2 > wins1:
                                        archetype_stats[arch2]['wins'] += 1
                                        archetype_stats[arch1]['losses'] += 1
                                        matchup_data[arch2][arch1]['wins'] += 1
                                        matchup_data[arch1][arch2]['losses'] += 1
                                    
                                except (ValueError, IndexError):
                                    continue
        
        print(f"\n📊 RÉSUMÉ DU MATCHING:")
        print(f"✅ Matched {matched_tournaments}/{len(self.listener_data)} tournois")
        print(f"✅ Analysé {total_matches} matches au total")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches,
            'matched_tournaments': matched_tournaments,
            'tournament_meta': dict(tournament_meta)
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
                'tournaments': len(stats['tournaments']),
                'unique_players': len(stats['players']),
                'sideboard_cards': dict(stats['sideboard_cards']),
            }))
        
        meta_data.sort(key=lambda x: x[1]['percentage'], reverse=True)
        
        # Générer HTML avec les 6 visualisations standards
        html = self._generate_complete_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_1_21_complete_analysis_all_6_visuals.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse complète générée avec les 6 visualisations!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        # Afficher les insights clés
        self._print_key_insights(analysis, meta_data)
        
        return output_path
    
    def _generate_complete_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML avec les 6 visualisations standards"""
        # Style template de référence
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
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .header p {
                margin: 10px 0;
                font-size: 1.2em;
                opacity: 0.9;
            }
            .visualization-container {
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            .visualization-title {
                text-align: center;
                font-size: 1.8em;
                color: #333;
                margin-bottom: 20px;
                font-weight: 600;
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
                transition: transform 0.3s ease;
            }
            .summary-card:hover {
                transform: translateY(-5px);
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
            .info-box h2 {
                color: #667eea;
                margin-top: 0;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                padding: 20px;
                color: #666;
                font-size: 0.9em;
            }
        </style>
        """
        
        # Créer les 6 visualisations standards
        viz_html = []
        
        # 1. Presence by Archetype (Bar chart)
        viz_html.append(self._create_presence_bar_chart(meta_data[:15]))
        
        # 2. Win Rate vs Presence (Scatter plot)
        viz_html.append(self._create_winrate_vs_presence_scatter(meta_data))
        
        # 3. Matchup Matrix (Heatmap)
        viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data[:10]))
        
        # 4. Performance Analysis (Bar chart with win rates)
        viz_html.append(self._create_performance_bar_chart(meta_data[:15]))
        
        # 5. Metagame Distribution (Pie chart)
        viz_html.append(self._create_metagame_pie_chart(meta_data))
        
        # 6. Meta Trends (Line chart)
        viz_html.append(self._create_meta_trends_line_chart(analysis['tournament_meta'], meta_data[:8]))
        
        # Générer le HTML complet
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Complete Standard Analysis with All 6 Visualizations</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Complete Standard Metagame Analysis</h1>
            <p>July 1-21, 2025 | All 6 Standard Visualizations</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Matches</div>
                <div class="summary-value">{analysis['total_matches']:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Tournaments</div>
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
            <h2>📋 Analysis Methodology</h2>
            <ul>
                <li><strong>Data Sources:</strong> MTGO listener data + cached decklists</li>
                <li><strong>Period:</strong> July 1-21, 2025 (21 days)</li>
                <li><strong>Analysis Method:</strong> Match-based analysis (not deck-based)</li>
                <li><strong>Exclusions:</strong> Leagues, casual tournaments, non-competitive events</li>
                <li><strong>Minimum Thresholds:</strong> 20 matches for win rate analysis, 1% for presence</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by Manalytics v3.3.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>© 2025 Manalytics - MTG Competitive Intelligence</p>
        </div>
    </div>
    
    <script>
        // Print key stats to console
        console.log("=== MANALYTICS KEY STATS ===");
        console.log("Total Matches: {analysis['total_matches']}");
        console.log("Top Archetype: {meta_data[0][0] if meta_data else 'N/A'}");
        console.log("Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}");
    </script>
</body>
</html>"""
        
        return html
    
    def _create_presence_bar_chart(self, meta_data: List) -> str:
        """Visualization #1: Presence by Archetype (bar chart)"""
        if not meta_data:
            return '<div class="visualization-container"><p>No data available</p></div>'
            
        archetypes = [d[0] for d in meta_data]
        percentages = [d[1]['percentage'] for d in meta_data]
        # Get colors for each archetype
        colors = []
        for arch in archetypes:
            color_codes = get_archetype_colors(arch)
            if color_codes:
                # Blend colors if multiple
                if len(color_codes) == 1:
                    colors.append(MTG_COLORS.get(color_codes[0], '#666'))
                else:
                    blended = blend_colors([MTG_COLORS.get(c, '#666') for c in color_codes])
                    colors.append(blended)
            else:
                colors.append('#666')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=archetypes,
            y=percentages,
            text=[f'{p:.1f}%' for p in percentages],
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(color='black', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Presence: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='📊 Visualization #1: Presence by Archetype',
            xaxis_title='Archetype',
            yaxis_title='Meta Share (%)',
            height=500,
            margin=dict(b=100),
            xaxis=dict(tickangle=-45),
            template='plotly_white'
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _create_winrate_vs_presence_scatter(self, meta_data: List) -> str:
        """Visualization #2: Win Rate vs Presence (scatter plot)"""
        # Filter archetypes with at least 20 matches
        filtered_data = [(arch, stats) for arch, stats in meta_data if stats['matches'] >= 20]
        
        if not filtered_data:
            return '<div class="visualization-container"><p>No data available</p></div>'
        
        archetypes = [d[0] for d in filtered_data]
        x_values = [d[1]['percentage'] for d in filtered_data]
        y_values = [d[1]['win_rate'] for d in filtered_data]
        sizes = [min(d[1]['matches'], 100) for d in filtered_data]
        # Get colors for each archetype
        colors = []
        for arch in archetypes:
            color_codes = get_archetype_colors(arch)
            if color_codes:
                # Blend colors if multiple
                if len(color_codes) == 1:
                    colors.append(MTG_COLORS.get(color_codes[0], '#666'))
                else:
                    blended = blend_colors([MTG_COLORS.get(c, '#666') for c in color_codes])
                    colors.append(blended)
            else:
                colors.append('#666')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers+text',
            text=archetypes,
            textposition='top center',
            marker=dict(
                size=[s/2 for s in sizes],
                color=colors,
                line=dict(color='black', width=1),
                sizemode='diameter'
            ),
            hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<extra></extra>'
        ))
        
        # Add reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title='📈 Visualization #2: Win Rate vs Presence',
            xaxis_title='Meta Share (%)',
            yaxis_title='Win Rate (%)',
            height=600,
            yaxis=dict(range=[35, 65]),
            template='plotly_white'
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _create_matchup_matrix(self, matchup_data: Dict, top_archetypes: List) -> str:
        """Visualization #3: Matchup Matrix (heatmap)"""
        if not top_archetypes:
            return '<div class="visualization-container"><p>No data available</p></div>'
            
        archetypes = [d[0] for d in top_archetypes]
        n = len(archetypes)
        
        # Create matrix
        z_values = []
        hover_text = []
        
        for arch1 in archetypes:
            row_values = []
            row_hover = []
            for arch2 in archetypes:
                if arch1 == arch2:
                    row_values.append(50)
                    row_hover.append('Mirror Match')
                else:
                    matchup = matchup_data.get(arch1, {}).get(arch2, {'wins': 0, 'losses': 0})
                    total = matchup['wins'] + matchup['losses']
                    if total > 0:
                        win_rate = (matchup['wins'] / total) * 100
                        row_values.append(win_rate)
                        row_hover.append(f'{matchup["wins"]}-{matchup["losses"]} ({win_rate:.1f}%)')
                    else:
                        row_values.append(50)
                        row_hover.append('No data')
            z_values.append(row_values)
            hover_text.append(row_hover)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=archetypes,
            y=archetypes,
            text=hover_text,
            hovertemplate='%{y} vs %{x}<br>%{text}<extra></extra>',
            colorscale='RdBu_r',
            zmid=50,
            zmin=30,
            zmax=70,
            colorbar=dict(title='Win %')
        ))
        
        fig.update_layout(
            title='🔥 Visualization #3: Matchup Matrix',
            height=700,
            xaxis=dict(tickangle=-45, side='bottom'),
            yaxis=dict(autorange='reversed'),
            template='plotly_white'
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _create_performance_bar_chart(self, meta_data: List) -> str:
        """Visualization #4: Performance Analysis (bar chart with win rates)"""
        if not meta_data:
            return '<div class="visualization-container"><p>No data available</p></div>'
            
        archetypes = [d[0] for d in meta_data]
        win_rates = [d[1]['win_rate'] for d in meta_data]
        matches = [d[1]['matches'] for d in meta_data]
        
        # Color based on performance
        colors = []
        for wr in win_rates:
            if wr >= 55:
                colors.append('#2e7d32')  # Dark green
            elif wr >= 50:
                colors.append('#66bb6a')  # Light green
            elif wr >= 45:
                colors.append('#ff9800')  # Orange
            else:
                colors.append('#d32f2f')  # Red
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=archetypes,
            y=win_rates,
            text=[f'{wr:.1f}%<br>({m} matches)' for wr, m in zip(win_rates, matches)],
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(color='black', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<br>%{text}<extra></extra>'
        ))
        
        # Add 50% reference line
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title='💪 Visualization #4: Performance Analysis',
            xaxis_title='Archetype',
            yaxis_title='Win Rate (%)',
            height=600,
            margin=dict(b=100),
            xaxis=dict(tickangle=-45),
            yaxis=dict(range=[0, 70]),
            template='plotly_white'
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _create_metagame_pie_chart(self, meta_data: List) -> str:
        """Visualization #5: Metagame Distribution (pie chart)"""
        # Top 10 + Others
        top_10 = meta_data[:10]
        others_pct = sum(d[1]['percentage'] for d in meta_data[10:])
        
        labels = [d[0] for d in top_10]
        values = [d[1]['percentage'] for d in top_10]
        
        if others_pct > 0:
            labels.append(f'Others ({len(meta_data) - 10} archetypes)')
            values.append(others_pct)
        
        # Get colors for each archetype
        colors = []
        for arch in labels[:-1]:
            color_codes = get_archetype_colors(arch)
            if color_codes:
                # Blend colors if multiple
                if len(color_codes) == 1:
                    colors.append(MTG_COLORS.get(color_codes[0], '#666'))
                else:
                    blended = blend_colors([MTG_COLORS.get(c, '#666') for c in color_codes])
                    colors.append(blended)
            else:
                colors.append('#666')
        colors.append('#808080')  # Gray for others
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Share: %{value:.1f}%<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='🥧 Visualization #5: Metagame Distribution',
            height=600,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            margin=dict(r=200)
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _create_meta_trends_line_chart(self, tournament_meta: Dict, top_archetypes: List) -> str:
        """Visualization #6: Meta Trends (line chart)"""
        if not tournament_meta or not top_archetypes:
            return '<div class="visualization-container"><p>No data available</p></div>'
            
        # Get dates and sort them
        dates = sorted(tournament_meta.keys())
        
        fig = go.Figure()
        
        # Add line for each top archetype
        for arch, _ in top_archetypes:
            y_values = []
            for date in dates:
                count = tournament_meta[date].get(arch, 0)
                total = sum(tournament_meta[date].values())
                percentage = (count / total * 100) if total > 0 else 0
                y_values.append(percentage)
            
            color_codes = get_archetype_colors(arch)
            if color_codes:
                # Blend colors if multiple
                if len(color_codes) == 1:
                    color = MTG_COLORS.get(color_codes[0], '#666')
                else:
                    color = blend_colors([MTG_COLORS.get(c, '#666') for c in color_codes])
            else:
                color = '#666'
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=y_values,
                name=arch,
                mode='lines+markers',
                line=dict(color=color, width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Share: %{y:.1f}%<extra></extra>'
            ))
        
        fig.update_layout(
            title='📈 Visualization #6: Meta Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Meta Share (%)',
            height=600,
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=1.02),
            margin=dict(r=200),
            template='plotly_white'
        )
        
        return f'<div class="visualization-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    
    def _print_key_insights(self, analysis: Dict, meta_data: List):
        """Affiche les insights clés dans la console"""
        print("\n" + "="*80)
        print("🔍 KEY INSIGHTS - STANDARD METAGAME JULY 1-21, 2025")
        print("="*80)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  • Total Matches: {analysis['total_matches']:,}")
        print(f"  • Tournaments: {analysis['matched_tournaments']}")
        print(f"  • Unique Archetypes: {len(analysis['archetype_stats'])}")
        print(f"  • Total Decks: {sum(s['decks'] for s in analysis['archetype_stats'].values())}")
        
        print(f"\n🏆 TOP 5 ARCHETYPES BY PRESENCE:")
        for i, (arch, stats) in enumerate(meta_data[:5]):
            print(f"  {i+1}. {arch}: {stats['percentage']:.1f}% ({stats['matches']} matches, {stats['win_rate']:.1f}% WR)")
        
        print(f"\n💪 TOP 5 BY WIN RATE (min 20 matches):")
        wr_sorted = sorted([(a, s) for a, s in meta_data if s['matches'] >= 20], key=lambda x: x[1]['win_rate'], reverse=True)
        for i, (arch, stats) in enumerate(wr_sorted[:5]):
            print(f"  {i+1}. {arch}: {stats['win_rate']:.1f}% ({stats['matches']} matches, {stats['percentage']:.1f}% share)")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    analyzer = CompleteJulyAnalyzer()
    output_file = analyzer.generate_complete_analysis()