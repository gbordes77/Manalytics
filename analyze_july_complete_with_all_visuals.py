#!/usr/bin/env python3
"""
Analyse juillet 1-21 avec TOUTES les visualisations comme analyze_july_complete_final.py
Mais en utilisant la méthode de comptage correcte (sans doubler les matches)
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import math
from collections import defaultdict
import re

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS, blend_colors
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class CompleteJulyAnalyzer:
    """Analyse complète avec toutes les visualisations"""
    
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
            
            if day_folder.exists():
                for file in day_folder.glob("*standard*.json"):
                    try:
                        with open(file, 'r') as f:
                            data = json.load(f)
                        
                        tournament_id = str(data['Tournament']['Id'])
                        match_count = sum(len(r.get('Matches', [])) for r in data.get('Rounds', []))
                        
                        self.listener_data[tournament_id] = {
                            'date': datetime.strptime(data['Tournament']['Date'][:10], '%Y-%m-%d'),
                            'name': data['Tournament']['Name'],
                            'rounds': data['Rounds'],
                            'file': str(file),
                            'match_count': match_count
                        }
                        count += 1
                        total_matches += match_count
                    except Exception as e:
                        print(f"⚠️ Erreur: {file.name}: {e}")
                        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs au total")
        
    def load_cache_data(self):
        """Charge les données depuis la DB et le cache JSON"""
        print("\n📋 Chargement des données du cache...")
        
        # DB tournaments
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21, 23, 59, 59)
        all_tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        
        # Filtrer compétitif
        EXCLUDED_PATTERNS = [
            "mosh pit", "creative", "летняя лига", "league",
            "casual", "fun", "test", "practice"
        ]
        
        competitive_tournaments = []
        for t in all_tournaments:
            name_lower = t.name.lower() if t.name else ""
            if any(pattern in name_lower for pattern in EXCLUDED_PATTERNS):
                continue
            if 'league' in t.type.lower():
                continue
            competitive_tournaments.append(t)
            
        print(f"✅ Trouvé {len(competitive_tournaments)} tournois compétitifs dans la DB")
        
        # JSON cache
        cache_count = 0
        decklists_path = Path("data/cache/decklists/2025-07.json")
        
        if decklists_path.exists():
            with open(decklists_path, 'r') as f:
                month_data = json.load(f)
            
            for tournament in competitive_tournaments:
                if tournament.id in month_data:
                    tid = self.extract_tournament_id(tournament.id)
                    if tid:
                        self.tournament_cache_data[tid] = {
                            'tournament': tournament,
                            'decklists': month_data[tournament.id].get('decklists', [])
                        }
                        cache_count += 1
                        
        print(f"📁 Trouvé {cache_count} entrées dans le cache JSON")
        print(f"✅ Chargé {len(self.tournament_cache_data)} tournois du cache avec IDs extraits")
        
    def merge_and_analyze(self):
        """Merge les données et extrait les matchs"""
        print("\n🔄 Merge et analyse des données...")
        
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        archetype_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'decks': set()
        })
        tournament_meta = defaultdict(lambda: defaultdict(int))
        
        matched_tournaments = 0
        total_matches = 0
        
        # Pour chaque tournoi listener
        for tid, listener_tourn in self.listener_data.items():
            if tid not in self.tournament_cache_data:
                continue
                
            matched_tournaments += 1
            cache_info = self.tournament_cache_data[tid]
            cache_data = cache_info['data']
            
            # Créer un mapping player -> archetype
            player_archetypes = {}
            for deck in cache_data.get('decklists', []):
                player = deck.get('player')
                archetype = deck.get('archetype') or 'Unknown'
                if player and archetype != 'Unknown':
                    player_archetypes[player] = archetype
                    archetype_stats[archetype]['decks'].add(player)
            
            # Analyser chaque round
            for round_data in listener_tourn['rounds']:
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
                                    p1_wins = int(parts[0])
                                    p2_wins = int(parts[1])
                                    
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
                            except ValueError:
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
    
    def create_summary_section(self, analysis: Dict) -> str:
        """Crée la section de résumé"""
        total_decks = sum(len(stats['decks']) for stats in analysis['archetype_stats'].values())
        total_archetypes = len(analysis['archetype_stats'])
        
        return f'''
        <!-- Summary Statistics -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Matches Analyzed</div>
                <div class="summary-value">{analysis['total_matches']:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Tournaments</div>
                <div class="summary-value">{analysis['matched_tournaments']}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Archetypes</div>
                <div class="summary-value">{total_archetypes}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Decks</div>
                <div class="summary-value">{total_decks}</div>
            </div>
        </div>
        '''
    
    def create_presence_chart(self, analysis: Dict) -> str:
        """Graphique 1: Presence by Archetype (Top 10)"""
        # Calculer la présence
        presence_data = []
        for archetype, stats in analysis['archetype_stats'].items():
            presence = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            if presence >= 1:  # Minimum 1%
                presence_data.append((archetype, presence, stats['matches']))
        
        # Trier et prendre top 10
        presence_data.sort(key=lambda x: x[1], reverse=True)
        top_10 = presence_data[:10]
        
        # Créer le graphique
        archetypes = [x[0] for x in top_10]
        presences = [x[1] for x in top_10]
        
        # Couleurs basées sur l'archétype
        colors = []
        for arch in archetypes:
            try:
                color = get_archetype_colors(arch)[0]
                if color and isinstance(color, str) and color.startswith('#'):
                    colors.append(color)
                else:
                    colors.append('#808080')
            except:
                colors.append('#808080')
        
        fig = go.Figure(data=[
            go.Bar(
                x=archetypes,
                y=presences,
                text=[f"{p:.1f}%" for p in presences],
                textposition='outside',
                marker_color=colors,
                marker_line_color='rgba(0,0,0,0.3)',
                marker_line_width=1
            )
        ])
        
        fig.update_layout(
            title={
                'text': 'Top 10 Archetypes by Presence',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Archetype', tickangle=-45),
            yaxis=dict(title='Presence %', range=[0, max(presences) * 1.2] if presences else [0, 1]),
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="presence-chart")
    
    def create_winrate_scatter(self, analysis: Dict) -> str:
        """Graphique 2: Win Rate vs Presence Scatter"""
        scatter_data = []
        
        for archetype, stats in analysis['archetype_stats'].items():
            presence = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            total_games = stats['wins'] + stats['losses']
            if total_games > 0:
                win_rate = (stats['wins'] / total_games) * 100
                scatter_data.append({
                    'archetype': archetype,
                    'presence': presence,
                    'win_rate': win_rate,
                    'matches': stats['matches']
                })
        
        # Filtrer les archétypes significatifs
        scatter_data = [d for d in scatter_data if d['matches'] >= 10]
        
        fig = go.Figure()
        
        # Ajouter les points
        for point in scatter_data:
            try:
                color = get_archetype_colors(point['archetype'])[0]
                if not color or not isinstance(color, str) or not color.startswith('#'):
                    color = '#808080'
            except:
                color = '#808080'
                
            fig.add_trace(go.Scatter(
                x=[point['presence']],
                y=[point['win_rate']],
                mode='markers+text',
                marker=dict(
                    size=math.sqrt(point['matches']) * 2,
                    color=color,
                    line=dict(color='rgba(0,0,0,0.3)', width=1)
                ),
                text=point['archetype'],
                textposition='top center',
                name=point['archetype'],
                hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Matches: ' + str(point['matches']) + '<extra></extra>'
            ))
        
        # Ligne à 50%
        fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': 'Win Rate vs Presence',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Presence %', range=[-1, max(d['presence'] for d in scatter_data) * 1.1] if scatter_data else [0, 10]),
            yaxis=dict(title='Win Rate %', range=[35, 65]),
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="winrate-scatter")
    
    def create_matchup_heatmap(self, analysis: Dict) -> str:
        """Graphique 3: Matchup Matrix (Top 8)"""
        # Prendre top 8 par présence
        sorted_archs = sorted(analysis['archetype_stats'].items(), 
                            key=lambda x: x[1]['matches'], 
                            reverse=True)[:8]
        
        archetypes = [x[0] for x in sorted_archs]
        n = len(archetypes)
        
        # Créer la matrice
        matrix = [[50.0 for _ in range(n)] for _ in range(n)]
        
        for i, (arch1, _) in enumerate(sorted_archs):
            for j, (arch2, _) in enumerate(sorted_archs):
                if i != j and arch1 in analysis['matchup_data'] and arch2 in analysis['matchup_data'][arch1]:
                    matchup = analysis['matchup_data'][arch1][arch2]
                    total = matchup['wins'] + matchup['losses']
                    if total > 0:
                        win_rate = (matchup['wins'] / total) * 100
                        matrix[i][j] = win_rate
        
        # Créer le heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=archetypes,
            y=archetypes,
            colorscale='RdBu',
            zmid=50,
            text=[[f"{val:.0f}%" for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate='%{y} vs %{x}<br>Win Rate: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Matchup Matrix - Top 8 Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(tickangle=-45),
            yaxis=dict(autorange='reversed'),
            template='plotly_white',
            height=700,
            width=800
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="matchup-heatmap")
    
    def create_performance_bars(self, analysis: Dict) -> str:
        """Graphique 4: Performance by Archetype (min 20 matches)"""
        perf_data = []
        
        for archetype, stats in analysis['archetype_stats'].items():
            total_games = stats['wins'] + stats['losses']
            if total_games >= 20:  # Minimum 20 matches
                win_rate = (stats['wins'] / total_games) * 100
                perf_data.append({
                    'archetype': archetype,
                    'win_rate': win_rate,
                    'matches': stats['matches'],
                    'wins': stats['wins'],
                    'losses': stats['losses']
                })
        
        # Trier par win rate
        perf_data.sort(key=lambda x: x['win_rate'], reverse=True)
        
        # Couleurs basées sur le win rate
        colors = []
        for d in perf_data:
            if d['win_rate'] > 52:
                colors.append('#4ade80')  # Vert
            elif d['win_rate'] < 48:
                colors.append('#f87171')  # Rouge
            else:
                colors.append('#60a5fa')  # Bleu
        
        fig = go.Figure(data=[
            go.Bar(
                x=[d['archetype'] for d in perf_data],
                y=[d['win_rate'] for d in perf_data],
                text=[f"{d['win_rate']:.1f}%" for d in perf_data],
                textposition='outside',
                marker_color=colors,
                customdata=[[d['wins'], d['losses'], d['matches']] for d in perf_data],
                hovertemplate='<b>%{x}</b><br>Win Rate: %{y:.1f}%<br>Record: %{customdata[0]}-%{customdata[1]}<br>Matches: %{customdata[2]}<extra></extra>'
            )
        ])
        
        # Ligne à 50%
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': 'Win Rates by Archetype (min 20 matches)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='', tickangle=-45),
            yaxis=dict(title='Win Rate %', range=[30, 70]),
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="performance-bars")
    
    def create_metagame_pie(self, analysis: Dict) -> str:
        """Graphique 5: Metagame Distribution Pie Chart"""
        # Calculer les parts
        pie_data = []
        for archetype, stats in analysis['archetype_stats'].items():
            share = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            if share >= 2:  # Minimum 2% pour apparaître
                pie_data.append({
                    'archetype': archetype,
                    'share': share
                })
        
        # Trier par share
        pie_data.sort(key=lambda x: x['share'], reverse=True)
        
        # Calculer "Others"
        others_share = 100 - sum(d['share'] for d in pie_data)
        if others_share > 0:
            pie_data.append({
                'archetype': 'Others',
                'share': others_share
            })
        
        # Couleurs
        colors = []
        for d in pie_data:
            if d['archetype'] == 'Others':
                colors.append('#e5e7eb')
            else:
                try:
                    color = get_archetype_colors(d['archetype'])[0]
                    if not color or not isinstance(color, str) or not color.startswith('#'):
                        color = '#808080'
                    colors.append(color)
                except:
                    colors.append('#808080')
        
        fig = go.Figure(data=[go.Pie(
            labels=[d['archetype'] for d in pie_data],
            values=[d['share'] for d in pie_data],
            marker_colors=colors,
            textfont_size=12,
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Share: %{value:.1f}%<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Metagame Distribution',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            template='plotly_white',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="metagame-pie")
    
    def create_trends_line(self, analysis: Dict) -> str:
        """Graphique 6: Meta Trends (placeholder)"""
        # Pour l'instant, un graphique simple montrant les top 5
        top_5 = sorted(analysis['archetype_stats'].items(), 
                      key=lambda x: x[1]['matches'], 
                      reverse=True)[:5]
        
        fig = go.Figure()
        
        for archetype, stats in top_5:
            # Simuler une tendance (à remplacer par des vraies données temporelles)
            x = list(range(1, 22))  # Jours 1-21
            y = [stats['matches'] / 21] * 21  # Moyenne constante pour l'instant
            
            try:
                color = get_archetype_colors(archetype)[0]
                if not color or not isinstance(color, str) or not color.startswith('#'):
                    color = '#808080'
            except:
                color = '#808080'
                
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=archetype,
                line=dict(color=color, width=3),
                hovertemplate='<b>%{fullData.name}</b><br>Day %{x}<br>Matches: %{y:.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': 'Meta Trends Over Time (Simulated)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Day', range=[1, 21]),
            yaxis=dict(title='Average Daily Matches'),
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="trends-line")
    
    def create_insights_section(self, analysis: Dict) -> str:
        """Crée la section des insights clés"""
        # Top 5 par présence
        presence_sorted = []
        for archetype, stats in analysis['archetype_stats'].items():
            presence = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            win_rate = (stats['wins'] / (stats['wins'] + stats['losses']) * 100) if (stats['wins'] + stats['losses']) > 0 else 0
            presence_sorted.append({
                'archetype': archetype,
                'presence': presence,
                'matches': stats['matches'],
                'win_rate': win_rate
            })
        
        presence_sorted.sort(key=lambda x: x['presence'], reverse=True)
        top_5_presence = presence_sorted[:5]
        
        # Top 5 par win rate (min 20 matches)
        wr_sorted = [x for x in presence_sorted if x['matches'] >= 20]
        wr_sorted.sort(key=lambda x: x['win_rate'], reverse=True)
        top_5_wr = wr_sorted[:5]
        
        insights_html = '''
        <div class="info-box">
            <h2>🔍 Key Insights</h2>
            <div class="insights-grid">
                <div class="insight-card">
                    <h3>📊 Top 5 by Presence</h3>
                    <ul style="list-style: none; padding: 0;">
        '''
        
        for i, data in enumerate(top_5_presence, 1):
            insights_html += f'''
                        <li style="padding: 5px 0;">
                            <strong>{i}. {data['archetype']}</strong><br>
                            {data['presence']:.1f}% ({data['matches']} matches, {data['win_rate']:.1f}% WR)
                        </li>
            '''
        
        insights_html += '''
                    </ul>
                </div>
                <div class="insight-card">
                    <h3>💪 Top 5 by Win Rate</h3>
                    <ul style="list-style: none; padding: 0;">
        '''
        
        for i, data in enumerate(top_5_wr, 1):
            insights_html += f'''
                        <li style="padding: 5px 0;">
                            <strong>{i}. {data['archetype']}</strong><br>
                            {data['win_rate']:.1f}% ({data['matches']} matches, {data['presence']:.1f}% share)
                        </li>
            '''
        
        insights_html += '''
                    </ul>
                </div>
            </div>
        </div>
        '''
        
        return insights_html
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec toutes les visualisations"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Générer toutes les visualisations
        summary_html = self.create_summary_section(analysis)
        presence_chart = self.create_presence_chart(analysis)
        winrate_scatter = self.create_winrate_scatter(analysis)
        matchup_heatmap = self.create_matchup_heatmap(analysis)
        performance_bars = self.create_performance_bars(analysis)
        metagame_pie = self.create_metagame_pie(analysis)
        trends_line = self.create_trends_line(analysis)
        insights_section = self.create_insights_section(analysis)
        
        # Créer le HTML complet
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Complete Standard Metagame Analysis (July 1-21, 2025)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
            }}
            .header p {{
                margin: 10px 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .visualization-container {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .summary-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }}
            .summary-card:hover {{
                transform: translateY(-5px);
            }}
            .summary-value {{
                font-size: 3em;
                font-weight: 700;
                margin: 10px 0;
            }}
            .summary-label {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .info-box {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .info-box h2 {{
                color: #667eea;
                margin-top: 0;
            }}
            .insights-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .insight-card {{
                background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }}
            .insight-card h3 {{
                margin-top: 0;
                color: #667eea;
            }}
            .methodology {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                border-left: 4px solid #667eea;
            }}
            .footer {{
                text-align: center;
                padding: 30px;
                margin-top: 50px;
                color: #6c757d;
                font-size: 0.9em;
            }}
        </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Complete Metagame Analysis</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Comprehensive analysis with all visualizations</p>
        </div>
        
        {summary_html}
        
        <!-- Visualization 1: Presence -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">📊 Archetype Presence Distribution</h2>
            {presence_chart}
        </div>
        
        <!-- Visualization 2: Win Rate vs Presence -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">📈 Win Rate vs Presence Analysis</h2>
            {winrate_scatter}
        </div>
        
        <!-- Visualization 3: Matchup Matrix -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">🎲 Matchup Matrix</h2>
            {matchup_heatmap}
        </div>
        
        <!-- Visualization 4: Performance -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">💪 Performance Analysis</h2>
            {performance_bars}
        </div>
        
        <!-- Visualization 5: Metagame Pie -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">🥧 Metagame Distribution</h2>
            {metagame_pie}
        </div>
        
        <!-- Visualization 6: Trends -->
        <div class="visualization-container">
            <h2 style="color: #667eea; margin-top: 0;">📊 Meta Trends</h2>
            {trends_line}
        </div>
        
        {insights_section}
        
        <!-- Methodology -->
        <div class="info-box methodology">
            <h2>📝 Methodology</h2>
            <ul>
                <li><strong>Data Source:</strong> MTGO Listener Data + Tournament Scraper Cache</li>
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
        console.log("Tournaments: {analysis['matched_tournaments']}");
        console.log("Unique Archetypes: {len(analysis['archetype_stats'])}");
    </script>
</body>
</html>'''
        
        # Sauvegarder
        output_path = Path("data/cache/july_1_21_complete_analysis_all_visuals.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("\n✅ Analyse complète générée!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        # Afficher les stats clés
        self.print_key_insights(analysis)
        
        return output_path
    
    def print_key_insights(self, analysis: Dict):
        """Affiche les insights clés dans la console"""
        total_decks = sum(len(stats['decks']) for stats in analysis['archetype_stats'].values())
        total_archetypes = len(analysis['archetype_stats'])
        
        print("\n" + "="*80)
        print("🔍 KEY INSIGHTS - STANDARD METAGAME JULY 1-21, 2025")
        print("="*80)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  • Total Matches: {analysis['total_matches']:,}")
        print(f"  • Tournaments: {analysis['matched_tournaments']}")
        print(f"  • Unique Archetypes: {total_archetypes}")
        print(f"  • Total Decks: {total_decks}")
        
        # Top 5 par présence
        presence_sorted = []
        for archetype, stats in analysis['archetype_stats'].items():
            presence = (stats['matches'] / analysis['total_matches'] * 100) if analysis['total_matches'] > 0 else 0
            win_rate = (stats['wins'] / (stats['wins'] + stats['losses']) * 100) if (stats['wins'] + stats['losses']) > 0 else 0
            presence_sorted.append((archetype, presence, stats['matches'], win_rate))
        
        presence_sorted.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 TOP 5 ARCHETYPES BY PRESENCE:")
        for i, (arch, pres, matches, wr) in enumerate(presence_sorted[:5], 1):
            print(f"  {i}. {arch}: {pres:.1f}% ({matches} matches, {wr:.1f}% WR)")
        
        # Top 5 par win rate
        wr_sorted = [(a, p, m, w) for a, p, m, w in presence_sorted if m >= 20]
        wr_sorted.sort(key=lambda x: x[3], reverse=True)
        
        print(f"\n💪 TOP 5 BY WIN RATE (min 20 matches):")
        for i, (arch, pres, matches, wr) in enumerate(wr_sorted[:5], 1):
            print(f"  {i}. {arch}: {wr:.1f}% ({matches} matches, {pres:.1f}% share)")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    import os
    
    analyzer = CompleteJulyAnalyzer()
    output_file = analyzer.generate_complete_analysis()
    
    # Auto-commit
    os.system(f'git add -A && git commit -m "auto: {datetime.now().strftime("%Y%m%d_%H%M%S")}"')
    
    # Ouvrir automatiquement
    os.system(f'open "{output_file}"')