#!/usr/bin/env python3
"""
Version avec COUVERTURE MAXIMALE - utilise listener + cache direct
pour matcher le maximum de tournois possibles
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple, Set
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


class MaximumCoverageAnalyzer:
    """Analyse avec couverture maximale des tournois"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        self.direct_cache_tournaments = {}  # Tournois du cache sans listener
        
    def extract_tournament_id(self, text: str) -> str:
        """Extraire l'ID numérique du tournoi depuis différents formats"""
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
        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs")
        return count
    
    def load_cache_data(self):
        """Charge TOUTES les données depuis le cache (pour couverture maximale)"""
        print("\n📋 Chargement des données du cache...")
        
        cache_json_path = Path("data/cache/decklists/2025-07.json")
        if cache_json_path.exists():
            with open(cache_json_path, 'r') as f:
                month_data = json.load(f)
            
            print(f"📁 Trouvé {len(month_data)} entrées dans le cache JSON")
            
            # Parser TOUTES les entrées Standard
            for key, data in month_data.items():
                # Vérifier que c'est un tournoi Standard
                if data.get('format', '').lower() == 'standard' or 'standard' in key.lower():
                    # Vérifier la date
                    date_str = data.get('date', '')
                    if date_str:
                        try:
                            date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                            if date.month == 7 and date.year == 2025 and 1 <= date.day <= 21:
                                # Extraire l'ID
                                tournament_id = self.extract_tournament_id(key)
                                if tournament_id:
                                    self.tournament_cache_data[tournament_id] = {
                                        'key': key,
                                        'data': data,
                                        'name': data.get('name', 'Unknown'),
                                        'date': date,
                                        'source': data.get('source', 'mtgo')
                                    }
                        except:
                            pass
        
        print(f"✅ Chargé {len(self.tournament_cache_data)} tournois Standard du cache (1-21 juillet)")
    
    def identify_coverage_gaps(self):
        """Identifie les tournois du cache sans données listener"""
        print("\n🔍 Analyse de la couverture...")
        
        # Tournois avec listener data
        listener_ids = set(self.listener_data.keys())
        
        # Tous les tournois du cache
        cache_ids = set(self.tournament_cache_data.keys())
        
        # Tournois cache sans listener
        cache_only_ids = cache_ids - listener_ids
        
        print(f"📊 Statistiques de couverture :")
        print(f"  - Tournois avec listener : {len(listener_ids)}")
        print(f"  - Tournois dans le cache : {len(cache_ids)}")
        print(f"  - Tournois cache sans listener : {len(cache_only_ids)}")
        
        # Stocker les tournois cache-only
        for tid in cache_only_ids:
            self.direct_cache_tournaments[tid] = self.tournament_cache_data[tid]
        
        # Afficher quelques exemples
        if cache_only_ids:
            print(f"\n📋 Exemples de tournois cache-only :")
            for tid in list(cache_only_ids)[:5]:
                info = self.tournament_cache_data[tid]
                print(f"  - {tid}: {info['name']} ({info['date'].strftime('%Y-%m-%d')}) - {info['source']}")
    
    def merge_and_analyze(self) -> Dict:
        """Merge TOUTES les sources et analyse par MATCHES + estimation pour cache-only"""
        print("\n🔄 Merge et analyse avec couverture maximale...")
        
        # Structure pour les matchups
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        archetype_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'decks': 0,
            'estimated_matches': 0,  # Pour les tournois cache-only
            'tournaments': set(),
            'players': set()
        })
        
        total_matches = 0
        matched_tournaments = 0
        cache_only_tournaments = 0
        tournament_list = []
        
        # 1. Traiter les tournois avec listener data (matchs réels)
        print("\n📊 Traitement des tournois avec listener data...")
        for listener_id, listener_tournament in self.listener_data.items():
            if listener_id in self.tournament_cache_data:
                matched_tournaments += 1
                cache_info = self.tournament_cache_data[listener_id]
                cache_data = cache_info['data']
                
                # Créer mapping player -> archetype
                player_archetypes = {}
                for deck in cache_data.get('decklists', []):
                    player = deck.get('player')
                    archetype = deck.get('archetype') or 'Unknown'
                    if player and archetype != 'Unknown':
                        player_archetypes[player] = archetype
                        archetype_stats[archetype]['decks'] += 1
                        archetype_stats[archetype]['tournaments'].add(listener_id)
                        archetype_stats[archetype]['players'].add(player)
                
                # Analyser les matchups réels
                match_count = 0
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
                            try:
                                p1_wins = int(parts[0])
                                p2_wins = int(parts[1])
                                
                                match_count += 1
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
                
                tournament_list.append({
                    'id': listener_id,
                    'name': listener_tournament['name'],
                    'date': listener_tournament['date'],
                    'matches': match_count,
                    'source': 'listener+cache',
                    'url': f"https://www.mtgo.com/decklist/{cache_info['key']}"
                })
        
        # 2. Traiter les tournois cache-only (estimation)
        print(f"\n📊 Traitement des {len(self.direct_cache_tournaments)} tournois cache-only...")
        for tid, cache_info in self.direct_cache_tournaments.items():
            cache_only_tournaments += 1
            cache_data = cache_info['data']
            
            # Compter les decks par archetype
            deck_count = len(cache_data.get('decklists', []))
            if deck_count > 0:
                # Estimation : ~45 matchs pour un Challenge 32, ~90 pour un Challenge 64
                estimated_matches = 45 if '32' in cache_info['name'] else 90 if '64' in cache_info['name'] else 30
                
                for deck in cache_data.get('decklists', []):
                    archetype = deck.get('archetype') or 'Unknown'
                    player = deck.get('player')
                    if archetype != 'Unknown':
                        archetype_stats[archetype]['decks'] += 1
                        archetype_stats[archetype]['tournaments'].add(tid)
                        archetype_stats[archetype]['estimated_matches'] += estimated_matches / deck_count
                        if player:
                            archetype_stats[archetype]['players'].add(player)
                
                tournament_list.append({
                    'id': tid,
                    'name': cache_info['name'],
                    'date': cache_info['date'],
                    'matches': 0,  # Pas de matchs réels
                    'estimated_matches': estimated_matches,
                    'source': 'cache-only',
                    'url': f"https://www.mtgo.com/decklist/{cache_info['key']}" if cache_info['source'] == 'mtgo' else '#'
                })
        
        print(f"\n📊 RÉSUMÉ DE LA COUVERTURE MAXIMALE:")
        print(f"✅ Tournois avec matchs réels : {matched_tournaments}")
        print(f"✅ Tournois cache-only : {cache_only_tournaments}")
        print(f"✅ Total tournois : {matched_tournaments + cache_only_tournaments}")
        print(f"✅ Matchs réels analysés : {total_matches}")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches,
            'matched_tournaments': matched_tournaments,
            'cache_only_tournaments': cache_only_tournaments,
            'tournament_list': tournament_list
        }
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec couverture maximale"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        self.identify_coverage_gaps()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Calculer les pourcentages
        meta_data = []
        total_coverage = analysis['total_matches']  # Pour les matchs réels uniquement
        
        for archetype, stats in analysis['archetype_stats'].items():
            # Pour le % du meta, utiliser uniquement les matchs réels
            percentage = (stats['matches'] / total_coverage * 100) if total_coverage > 0 else 0
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
                'estimated_matches': stats['estimated_matches'],
                'players': list(stats['players'])
            }))
        
        meta_data.sort(key=lambda x: x[1]['percentage'], reverse=True)
        
        # Générer HTML
        html = self._generate_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_maximum_coverage_analysis.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse complète générée avec couverture maximale!")
        print(f"📄 Fichier: {output_path}")
        
        # Auto-ouvrir le fichier
        import subprocess
        subprocess.run(['open', str(output_path)])
        
        return output_path
    
    def _generate_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML complet avec indicateurs de couverture"""
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
                margin: 0 0 10px 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .header p {
                margin: 5px 0;
                opacity: 0.9;
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
                transition: transform 0.2s;
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
                font-weight: 500;
            }
            .info-box {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }
            .info-box h2 {
                color: #333;
                margin-top: 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .coverage-indicator {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 600;
                margin-left: 10px;
            }
            .coverage-full {
                background: #4CAF50;
                color: white;
            }
            .coverage-partial {
                background: #FF9800;
                color: white;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 10px 12px;
                border-bottom: 1px solid #eee;
            }
            tr:hover {
                background: #f5f5f5;
            }
            a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
            a:hover {
                text-decoration: underline;
            }
            .meta-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.85em;
                margin-left: 8px;
                background: #e3f2fd;
                color: #1976d2;
            }
        </style>
        """
        
        # Créer les visualisations
        viz_html = []
        viz_html.append(self._create_pie_chart(meta_data))
        viz_html.append(self._create_bar_chart(meta_data))
        viz_html.append(self._create_winrate_chart(meta_data))
        viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data, analysis))
        viz_html.append(self._create_coverage_comparison_chart(meta_data))
        
        # Générer la liste des tournois
        tournaments_html = self._generate_tournaments_list(analysis)
        
        total_tournaments = analysis['matched_tournaments'] + analysis['cache_only_tournaments']
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Maximum Coverage Analysis (July 1-21, 2025)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Maximum Coverage Analysis</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 1.1em;">
                <strong>{analysis['total_matches']:,}</strong> real matches from <strong>{analysis['matched_tournaments']}</strong> tournaments
            </p>
            <p style="font-size: 0.95em; opacity: 0.8;">
                + {analysis['cache_only_tournaments']} additional tournaments from cache (deck lists only)
            </p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Real Matches Analyzed</div>
                <div class="summary-value">{analysis['total_matches']:,}</div>
            </div>
            <div class="summary-card" style="cursor: pointer;" onclick="document.getElementById('tournament-list').scrollIntoView({{behavior: 'smooth'}});">
                <div class="summary-label">Total Tournaments</div>
                <div class="summary-value">{total_tournaments}</div>
                <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">↓ Click for details</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Coverage Rate</div>
                <div class="summary-value">{(analysis['matched_tournaments'] / total_tournaments * 100):.0f}%</div>
                <div style="font-size: 0.8em; opacity: 0.7;">With match data</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Archetypes</div>
                <div class="summary-value">{len(analysis['archetype_stats'])}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Decks</div>
                <div class="summary-value">{sum(s['decks'] for s in analysis['archetype_stats'].values())}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Players</div>
                <div class="summary-value">{len(set().union(*[set(s.get('players', [])) for s in analysis['archetype_stats'].values()]))}</div>
            </div>
        </div>
        
        {''.join(viz_html)}
        
        {tournaments_html}
        
    </div>
</body>
</html>"""
        
        return html
    
    def _create_pie_chart(self, meta_data: List) -> str:
        """Crée le pie chart du métagame (matchs réels uniquement)"""
        labels = []
        values = []
        colors = []
        
        other_pct = 0
        for i, (archetype, data) in enumerate(meta_data):
            if i < 10 and data['percentage'] > 1:
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
                'text': '📊 Metagame Distribution (Real Matches Only)',
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
        """Crée le bar chart avec indicateur de couverture"""
        top_15 = [(a, d) for a, d in meta_data if d['matches'] >= 5 or d['decks'] >= 3][:15]
        
        archetypes = [a[0] for a in top_15]
        percentages = [a[1]['percentage'] for a in top_15]
        has_matches = [a[1]['matches'] > 0 for a in top_15]
        
        colors = []
        for i, (archetype, _) in enumerate(top_15):
            arch_colors = get_archetype_colors(archetype)
            if len(arch_colors) == 1:
                base_color = MTG_COLORS.get(arch_colors[0], '#808080')
            else:
                base_color = blend_colors(
                    MTG_COLORS.get(arch_colors[0], '#808080'),
                    MTG_COLORS.get(arch_colors[1], '#404040'),
                    0.6
                )
            # Assombrir si pas de matchs réels
            if not has_matches[i]:
                base_color = blend_colors(base_color, '#666666', 0.5)
            colors.append(base_color)
        
        fig = go.Figure(data=[go.Bar(
            x=archetypes,
            y=percentages,
            marker=dict(
                color=colors,
                line=dict(color='black', width=1),
                pattern=dict(
                    shape=['.' if not has_match else '' for has_match in has_matches],
                    size=8,
                    solidity=0.3
                )
            ),
            text=[f"{p:.1f}%" if has_matches[i] else f"~{p:.1f}%" for i, p in enumerate(percentages)],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Presence: %{y:.1f}%<br>%{customdata}<extra></extra>',
            customdata=['Real matches' if hm else 'Deck lists only' for hm in has_matches]
        )])
        
        fig.update_layout(
            title={
                'text': '📈 Top Archetypes by Presence',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Archetype', tickangle=-45),
            yaxis=dict(title='Presence %', range=[0, max(percentages) * 1.15] if percentages else [0, 10]),
            width=1000,
            height=600,
            margin=dict(b=150),
            annotations=[{
                'text': '⚫ = Deck lists only (no match data)',
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.02,
                'y': 0.98,
                'font': {'size': 12, 'color': '#666'}
            }]
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="bar-chart")}</div>'
    
    def _create_winrate_chart(self, meta_data: List) -> str:
        """Crée le graphique des win rates (matchs réels uniquement)"""
        filtered = [(a, d) for a, d in meta_data if d['matches'] >= 10][:20]
        filtered.sort(key=lambda x: x[1]['win_rate'], reverse=True)
        
        if not filtered:
            return '<div class="visualization-container"><p>Not enough match data for win rate analysis</p></div>'
        
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
                size=[min(20, 8 + m/50) for m in match_counts],  # Taille selon nb matchs
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
                'text': '📊 Win Rates with 95% Confidence Intervals (Real Matches)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Win Rate %', range=[30, 70]),
            yaxis=dict(title='', autorange='reversed'),
            width=1000,
            height=max(600, len(archetypes) * 35),
            margin=dict(l=200),
            annotations=[{
                'text': 'Bubble size = number of matches',
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.02,
                'y': 0.02,
                'font': {'size': 11, 'color': '#666'}
            }]
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="winrate-chart")}</div>'
    
    def _create_matchup_matrix(self, matchup_data: Dict, meta_data: List, analysis: Dict = None) -> str:
        """Crée la matrice de matchups (matchs réels uniquement)"""
        # Top archetypes avec assez de matchs
        top_archetypes = [a[0] for a in meta_data[:12] if a[1]['matches'] >= 10]
        
        if len(top_archetypes) < 2:
            return '<div class="visualization-container"><p>Not enough match data for matchup matrix</p></div>'
        
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
                                f"Total Matches: {total}"
                            )
                            
                            # Annotations pour matchups significatifs
                            if total >= 5:
                                if win_rate > 65 or win_rate < 35:
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
                'text': f'🎲 Real Matchup Matrix from {analysis["total_matches"]} Matches',
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
    
    def _create_coverage_comparison_chart(self, meta_data: List) -> str:
        """Crée un graphique comparant la couverture par archetype"""
        top_10 = [(a, d) for a, d in meta_data[:10]]
        
        archetypes = [a[0] for a in top_10]
        real_matches = [a[1]['matches'] for a in top_10]
        estimated_matches = [a[1]['estimated_matches'] for a in top_10]
        
        fig = go.Figure()
        
        # Barres pour matchs réels
        fig.add_trace(go.Bar(
            name='Real Matches',
            x=archetypes,
            y=real_matches,
            marker_color='#4CAF50',
            hovertemplate='<b>%{x}</b><br>Real matches: %{y}<extra></extra>'
        ))
        
        # Barres pour matchs estimés (cache-only)
        fig.add_trace(go.Bar(
            name='Estimated (Cache-only)',
            x=archetypes,
            y=estimated_matches,
            marker_color='#FF9800',
            opacity=0.6,
            hovertemplate='<b>%{x}</b><br>Estimated: ~%{y:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '📊 Data Coverage by Archetype',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Archetype', tickangle=-45),
            yaxis=dict(title='Number of Matches'),
            barmode='stack',
            width=1000,
            height=600,
            margin=dict(b=150),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="coverage-chart")}</div>'
    
    def _generate_tournaments_list(self, analysis: Dict) -> str:
        """Génère la liste des tournois avec indicateurs de couverture"""
        tournament_list = sorted(analysis['tournament_list'], key=lambda x: x['date'])
        
        rows_html = []
        for i, t in enumerate(tournament_list, 1):
            coverage_badge = '<span class="coverage-indicator coverage-full">Full</span>' if t['source'] == 'listener+cache' else '<span class="coverage-indicator coverage-partial">Decks only</span>'
            
            matches_text = f"{t['matches']}" if t['matches'] > 0 else f"~{t.get('estimated_matches', 0)}"
            
            row = f"""
                <tr>
                    <td>{i}</td>
                    <td>{t['date'].strftime('%Y-%m-%d')}</td>
                    <td>
                        <a href="{t['url']}" target="_blank">{t['name']}</a>
                        {coverage_badge}
                    </td>
                    <td>{t['id']}</td>
                    <td>{matches_text}</td>
                </tr>
            """
            rows_html.append(row)
        
        total_real = sum(t['matches'] for t in tournament_list)
        total_estimated = sum(t.get('estimated_matches', 0) for t in tournament_list)
        
        html = f"""
        <div class="info-box" id="tournament-list">
            <h2>🏆 All Tournaments in Analysis</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Complete list of {len(tournament_list)} tournaments from July 1-21, 2025.
                <br>
                <strong style="color: #4CAF50;">● Full coverage</strong>: Tournaments with real match data (listener + cache)
                <br>
                <strong style="color: #FF9800;">● Partial coverage</strong>: Tournaments with deck lists only (cache-only)
            </p>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Date</th>
                        <th>Tournament Name</th>
                        <th>ID</th>
                        <th>Matches</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold; background: #f8f9fa;">
                        <td colspan="4">Total</td>
                        <td>{total_real} real + ~{total_estimated:.0f} estimated</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        
        return html


if __name__ == "__main__":
    analyzer = MaximumCoverageAnalyzer()
    analyzer.generate_complete_analysis()