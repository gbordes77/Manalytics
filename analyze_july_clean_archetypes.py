#!/usr/bin/env python3
"""
Analyse juillet avec SEULEMENT les matchs où les deux joueurs ont un archétype connu
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


class CleanArchetypeAnalyzer:
    """Analyse avec seulement les archétypes connus"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        
    def extract_tournament_id(self, text: str) -> str:
        """Extraire l'ID numérique du tournoi"""
        match = re.search(r'(\d{8})(?:\D|$)', str(text))
        if match:
            return match.group(1)
        return None
        
    def load_listener_data(self):
        """Charge les données listener depuis data/MTGOData"""
        print("📊 Chargement des données listener...")
        
        mtgo_path = Path("data/MTGOData/2025/07")
        count = 0
        total_matches = 0
        
        for day in range(1, 22):
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
                        print(f"⚠️ Erreur lecture {file}: {e}")
        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs au total")
        return count
    
    def load_cache_data(self):
        """Charge les données depuis le cache"""
        print("\n📋 Chargement des données du cache...")
        
        cache_json_path = Path("data/cache/decklists/2025-07.json")
        if cache_json_path.exists():
            with open(cache_json_path, 'r') as f:
                month_data = json.load(f)
            
            # Parser uniquement Standard juillet 1-21
            for key, data in month_data.items():
                if data.get('format', '').lower() == 'standard' or 'standard' in key.lower():
                    date_str = data.get('date', '')
                    if date_str and '2025-07' in date_str:
                        try:
                            date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                            if 1 <= date.day <= 21:
                                tournament_id = self.extract_tournament_id(key)
                                if tournament_id:
                                    self.tournament_cache_data[tournament_id] = {
                                        'key': key,
                                        'data': data,
                                        'name': data.get('name', 'Unknown'),
                                        'date': date
                                    }
                        except:
                            pass
        
        print(f"✅ Chargé {len(self.tournament_cache_data)} tournois du cache")
    
    def merge_and_analyze(self) -> Dict:
        """Merge et analyse SEULEMENT les matchs avec archétypes connus"""
        print("\n🔄 Merge et analyse (archétypes connus uniquement)...")
        
        # Structure pour les matchups
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        archetype_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'decks': 0,
            'tournaments': set(),
            'players': set()
        })
        
        total_matches = 0
        skipped_matches = 0
        matched_tournaments = 0
        tournament_list = []
        
        # Pour chaque tournoi du listener
        for listener_id, listener_tournament in self.listener_data.items():
            if listener_id in self.tournament_cache_data:
                matched_tournaments += 1
                cache_info = self.tournament_cache_data[listener_id]
                cache_data = cache_info['data']
                
                # Créer mapping player -> archetype (SEULEMENT si archetype connu)
                player_archetypes = {}
                for deck in cache_data.get('decklists', []):
                    player = deck.get('player')
                    archetype = deck.get('archetype')
                    # IMPORTANT: Ignorer None, 'Unknown', et chaînes vides
                    if player and archetype and archetype not in ['Unknown', 'None', None, '']:
                        player_archetypes[player] = archetype
                        archetype_stats[archetype]['decks'] += 1
                        archetype_stats[archetype]['tournaments'].add(listener_id)
                        archetype_stats[archetype]['players'].add(player)
                
                # Analyser les matchups
                tournament_matches = 0
                tournament_skipped = 0
                
                for round_data in listener_tournament['rounds']:
                    for match in round_data['Matches']:
                        player1 = match['Player1']
                        player2 = match['Player2']
                        result = match['Result']
                        
                        if player2 == "BYE" or not result or result == "0-0-0":
                            continue
                        
                        arch1 = player_archetypes.get(player1)
                        arch2 = player_archetypes.get(player2)
                        
                        # SKIP si un des archétypes est inconnu
                        if not arch1 or not arch2:
                            tournament_skipped += 1
                            skipped_matches += 1
                            continue
                        
                        # Parse result
                        parts = result.split('-')
                        if len(parts) >= 2:
                            try:
                                p1_wins = int(parts[0])
                                p2_wins = int(parts[1])
                                
                                tournament_matches += 1
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
                            except ValueError:
                                continue
                
                if tournament_matches > 0:
                    tournament_list.append({
                        'id': listener_id,
                        'name': listener_tournament['name'],
                        'date': listener_tournament['date'],
                        'matches': tournament_matches,
                        'skipped': tournament_skipped,
                        'url': f"https://www.mtgo.com/decklist/{cache_info['key']}"
                    })
        
        print(f"\n📊 RÉSUMÉ DE L'ANALYSE:")
        print(f"✅ Tournois matchés : {matched_tournaments}")
        print(f"✅ Matchs avec archétypes connus : {total_matches}")
        print(f"⚠️ Matchs ignorés (archétype inconnu) : {skipped_matches}")
        print(f"📈 Taux d'utilisation : {(total_matches / (total_matches + skipped_matches) * 100):.1f}%")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches,
            'skipped_matches': skipped_matches,
            'matched_tournaments': matched_tournaments,
            'tournament_list': tournament_list
        }
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec données propres"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        if analysis['total_matches'] == 0:
            print("❌ ERREUR : Aucun match avec archétypes connus trouvé!")
            return
        
        # Calculer les pourcentages
        meta_data = []
        for archetype, stats in analysis['archetype_stats'].items():
            percentage = (stats['matches'] / analysis['total_matches'] * 100)
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
                'players': list(stats['players'])
            }))
        
        meta_data.sort(key=lambda x: x[1]['percentage'], reverse=True)
        
        # Générer HTML
        html = self._generate_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_clean_archetypes_analysis.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse générée avec archétypes propres!")
        print(f"📄 Fichier: {output_path}")
        
        # Auto-ouvrir
        import subprocess
        subprocess.run(['open', str(output_path)])
        
        return output_path
    
    def _generate_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML avec données propres"""
        # Style template
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
                margin: 0 0 10px 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .warning-box {
                background: #fff3cd;
                border: 2px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                color: #856404;
            }
            .visualization-container {
                background: white;
                border-radius: 15px;
                padding: 30px;
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
        </style>
        """
        
        # Warning sur les données
        warning_html = f"""
        <div class="warning-box">
            <h3>⚠️ Analyse avec Archétypes Connus Uniquement</h3>
            <p>Cette analyse utilise SEULEMENT les matchs où les deux joueurs ont un archétype identifié.</p>
            <p><strong>{analysis['total_matches']}</strong> matchs analysés sur <strong>{analysis['total_matches'] + analysis['skipped_matches']}</strong> matchs totaux 
               ({(analysis['total_matches'] / (analysis['total_matches'] + analysis['skipped_matches']) * 100):.1f}% d'utilisation)</p>
            <p>Les {analysis['skipped_matches']} matchs avec archétypes inconnus ont été exclus pour garantir la précision.</p>
        </div>
        """
        
        # Créer visualisations
        viz_html = []
        viz_html.append(self._create_pie_chart(meta_data))
        viz_html.append(self._create_bar_chart(meta_data))
        viz_html.append(self._create_winrate_chart(meta_data))
        viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data))
        
        # Générer liste des tournois
        tournaments_html = self._generate_tournaments_list(analysis)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Clean Archetypes Analysis (July 1-21, 2025)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Clean Archetypes Analysis</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 1.1em;">
                Analysis of <strong>{analysis['total_matches']:,}</strong> matches with known archetypes
            </p>
        </div>
        
        {warning_html}
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Clean Matches Analyzed</div>
                <div class="summary-value">{analysis['total_matches']:,}</div>
            </div>
            <div class="summary-card" style="cursor: pointer;" onclick="document.getElementById('tournament-list').scrollIntoView({{behavior: 'smooth'}});">
                <div class="summary-label">Tournaments Used</div>
                <div class="summary-value">{len(analysis['tournament_list'])}</div>
                <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">↓ Click for details</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Data Utilization</div>
                <div class="summary-value">{(analysis['total_matches'] / (analysis['total_matches'] + analysis['skipped_matches']) * 100):.1f}%</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Known Archetypes</div>
                <div class="summary-value">{len(analysis['archetype_stats'])}</div>
            </div>
        </div>
        
        {''.join(viz_html)}
        
        {tournaments_html}
        
    </div>
</body>
</html>"""
        
        return html
    
    def _create_pie_chart(self, meta_data: List) -> str:
        """Crée le pie chart du métagame avec données propres"""
        labels = []
        values = []
        colors = []
        
        other_pct = 0
        for i, (archetype, data) in enumerate(meta_data):
            if i < 10 and data['percentage'] > 2:
                labels.append(f"{archetype} ({data['percentage']:.1f}%)")
                values.append(data['percentage'])
                
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
                'text': '📊 Clean Metagame Distribution (Known Archetypes Only)',
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
        top_15 = [(a, d) for a, d in meta_data if d['matches'] >= 5][:15]
        
        archetypes = [a[0] for a in top_15]
        percentages = [a[1]['percentage'] for a in top_15]
        
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
                'text': '📈 Top Archetypes by Match Presence',
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
        """Crée le graphique des win rates"""
        filtered = [(a, d) for a, d in meta_data if d['matches'] >= 10][:20]
        filtered.sort(key=lambda x: x[1]['win_rate'], reverse=True)
        
        if not filtered:
            return '<div class="visualization-container"><p>Not enough data for win rate analysis</p></div>'
        
        archetypes = [a[0] for a in filtered]
        win_rates = [a[1]['win_rate'] for a in filtered]
        ci_lower = [a[1]['ci_lower'] for a in filtered]
        ci_upper = [a[1]['ci_upper'] for a in filtered]
        match_counts = [a[1]['matches'] for a in filtered]
        
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
            mode='markers+text',
            marker=dict(
                size=[min(20, 8 + m/50) for m in match_counts],
                color=win_rates,
                colorscale='RdYlGn',
                cmin=40,
                cmax=60,
                colorbar=dict(title="Win Rate %"),
                line=dict(color='black', width=1)
            ),
            text=[f"{wr:.1f}%" for wr in win_rates],
            textposition='middle right',
            hovertemplate='<b>%{y}</b><br>Win Rate: %{x:.1f}%<br>CI: [%{customdata[0]:.1f}%, %{customdata[1]:.1f}%]<br>Matches: %{customdata[2]}<extra></extra>',
            customdata=list(zip(ci_lower, ci_upper, match_counts))
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
        top_archetypes = [a[0] for a in meta_data[:10] if a[1]['matches'] >= 10]
        
        if len(top_archetypes) < 2:
            return '<div class="visualization-container"><p>Not enough data for matchup matrix</p></div>'
        
        matrix = []
        hover_texts = []
        annotations = []
        
        for i, arch1 in enumerate(top_archetypes):
            row = []
            hover_row = []
            
            for j, arch2 in enumerate(top_archetypes):
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
                                f"Record: {wins}-{losses}<br>"
                                f"Total: {total}"
                            )
                            
                            if total >= 5 and (win_rate > 65 or win_rate < 35):
                                annotations.append({
                                    'x': j, 'y': i,
                                    'text': f"{win_rate:.0f}%",
                                    'showarrow': False,
                                    'font': {'color': 'white', 'size': 12, 'weight': 'bold'}
                                })
                        else:
                            row.append(None)
                            hover_row.append(f"{arch1} vs {arch2}<br>No data")
                    else:
                        row.append(None)
                        hover_row.append(f"{arch1} vs {arch2}<br>No data")
            
            matrix.append(row)
            hover_texts.append(hover_row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=top_archetypes,
            y=top_archetypes,
            colorscale=[
                [0, '#b71c1c'],
                [0.3, '#ef5350'],
                [0.4, '#ff9800'],
                [0.5, '#ffeb3b'],
                [0.6, '#8bc34a'],
                [0.8, '#4CAF50'],
                [1, '#1b5e20']
            ],
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            colorbar=dict(
                title='Win Rate %',
                tickmode='array',
                tickvals=[20, 35, 50, 65, 80],
                ticktext=['20%', '35%', '50%', '65%', '80%']
            ),
            zmid=50
        ))
        
        fig.update_layout(
            title={
                'text': f'🎲 Clean Matchup Matrix ({sum(sum(1 for v in row if v is not None) for row in matrix)} matchups)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#333'}
            },
            xaxis=dict(title='Opponent', side='bottom', tickangle=-45),
            yaxis=dict(title='Your Deck', autorange='reversed'),
            width=1100,
            height=1100,
            annotations=annotations
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="matchup-matrix")}</div>'
    
    def _generate_tournaments_list(self, analysis: Dict) -> str:
        """Génère la liste des tournois avec stats"""
        tournament_list = sorted(analysis['tournament_list'], key=lambda x: x['date'])
        
        rows_html = []
        for i, t in enumerate(tournament_list, 1):
            utilization = (t['matches'] / (t['matches'] + t['skipped']) * 100) if (t['matches'] + t['skipped']) > 0 else 0
            
            row = f"""
                <tr>
                    <td>{i}</td>
                    <td>{t['date'].strftime('%Y-%m-%d')}</td>
                    <td><a href="{t['url']}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">{t['name']}</a></td>
                    <td>{t['matches']}</td>
                    <td>{t['skipped']}</td>
                    <td>{utilization:.1f}%</td>
                </tr>
            """
            rows_html.append(row)
        
        html = f"""
        <div class="info-box" id="tournament-list" style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 15px; padding: 30px; margin: 30px 0;">
            <h2>🏆 Tournaments Used in Clean Analysis</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Only tournaments with matches between known archetypes are included.
            </p>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <th style="padding: 12px; text-align: left;">#</th>
                        <th style="padding: 12px; text-align: left;">Date</th>
                        <th style="padding: 12px; text-align: left;">Tournament Name</th>
                        <th style="padding: 12px; text-align: left;">Clean Matches</th>
                        <th style="padding: 12px; text-align: left;">Skipped</th>
                        <th style="padding: 12px; text-align: left;">Utilization</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold; background: #f8f9fa;">
                        <td colspan="3" style="padding: 12px;">Total</td>
                        <td style="padding: 12px;">{analysis['total_matches']}</td>
                        <td style="padding: 12px;">{analysis['skipped_matches']}</td>
                        <td style="padding: 12px;">{(analysis['total_matches'] / (analysis['total_matches'] + analysis['skipped_matches']) * 100):.1f}%</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        
        return html


if __name__ == "__main__":
    analyzer = CleanArchetypeAnalyzer()
    analyzer.generate_complete_analysis()