#!/usr/bin/env python3
"""
Version CORRIGÉE de l'analyse juillet 1-21 avec :
1. Bon path vers MTGOData
2. Meilleur matching d'IDs
3. Debug détaillé
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


class FixedJulyAnalyzer:
    """Analyse corrigée avec le bon path et matching amélioré"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        
    def extract_tournament_id(self, text: str) -> str:
        """Extraire l'ID numérique du tournoi depuis différents formats"""
        # Chercher spécifiquement les 8 derniers chiffres
        # Formats possibles:
        # - "standard-challenge-32-2025-07-0412801637" -> 12801637
        # - "2012803712" -> 12803712
        # - "(12801654)" -> 12801654
        
        # D'abord essayer de trouver 8 chiffres à la fin
        match = re.search(r'(\d{8})(?:\D|$)', str(text))
        if match:
            return match.group(1)
            
        # Si pas trouvé, chercher n'importe quel nombre de 8 chiffres
        match = re.search(r'(\d{8})', str(text))
        if match:
            return match.group(1)
            
        return None
        
    def load_listener_data(self):
        """Charge les données listener depuis data/MTGOData"""
        print("📊 Chargement des données listener depuis data/MTGOData...")
        
        # CORRECTION: Utiliser le bon path
        mtgo_path = Path("data/MTGOData/2025/07")
        count = 0
        total_matches = 0
        
        # Parcourir les dossiers par jour
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
                        print(f"⚠️ Erreur lecture {file}: {e}")
        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs au total")
        
        # Debug: afficher quelques tournois listener
        print("\nExemples de tournois listener:")
        for tid, data in list(self.listener_data.items())[:5]:
            print(f"  - ID: {tid}, Name: {data['name']}, Date: {data['date'].strftime('%Y-%m-%d')}, Matchs: {data['match_count']}")
        
        return count
    
    def load_cache_data(self):
        """Charge les données depuis notre cache"""
        print("\n📋 Chargement des données du cache...")
        
        # Charger depuis la base de données
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21, 23, 59, 59)
        
        tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        
        # Exclure les leagues
        competitive_tournaments = []
        for t in tournaments:
            if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower():
                competitive_tournaments.append(t)
        
        print(f"✅ Trouvé {len(competitive_tournaments)} tournois compétitifs dans la DB")
        
        # Charger aussi depuis les fichiers JSON du cache pour avoir tous les IDs possibles
        cache_json_path = Path("data/cache/decklists/2025-07.json")
        if cache_json_path.exists():
            with open(cache_json_path, 'r') as f:
                month_data = json.load(f)
            
            print(f"📁 Trouvé {len(month_data)} entrées dans le cache JSON")
            
            # Parser chaque entrée - FILTRER UNIQUEMENT STANDARD
            for key, data in month_data.items():
                # Vérifier que c'est un tournoi Standard
                if data.get('format', '').lower() == 'standard' or 'standard' in key.lower():
                    # Extraire l'ID du key
                    tournament_id = self.extract_tournament_id(key)
                    if tournament_id:
                        self.tournament_cache_data[tournament_id] = {
                            'key': key,
                            'data': data,
                            'name': data.get('name', 'Unknown'),
                            'date': data.get('date', 'Unknown')
                        }
        
        print(f"✅ Chargé {len(self.tournament_cache_data)} tournois du cache avec IDs extraits")
        
        # Debug: afficher quelques exemples
        print("\nExemples de tournois cache:")
        for tid, info in list(self.tournament_cache_data.items())[:5]:
            print(f"  - ID: {tid}, Key: {info['key']}, Name: {info['name']}")
    
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
        unmatched_listener = []
        unmatched_cache = []
        
        # Pour chaque tournoi du listener
        for listener_id, listener_tournament in self.listener_data.items():
            matched = False
            
            # Chercher dans le cache par ID extrait
            if listener_id in self.tournament_cache_data:
                matched = True
                matched_tournaments += 1
                cache_info = self.tournament_cache_data[listener_id]
                cache_data = cache_info['data']
                
                print(f"✅ Matched: Listener {listener_id} → Cache {cache_info['key']}")
                
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
                            try:
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
                            except ValueError:
                                continue
            else:
                unmatched_listener.append({
                    'id': listener_id,
                    'name': listener_tournament['name'],
                    'date': listener_tournament['date'],
                    'matches': listener_tournament['match_count']
                })
        
        # Lister les tournois cache non matchés
        matched_listener_ids = set(str(tid) for tid, _ in 
                                  [(lid, lt) for lid, lt in self.listener_data.items() 
                                   if lid in self.tournament_cache_data])
        
        for cache_id in self.tournament_cache_data:
            if cache_id not in matched_listener_ids:
                unmatched_cache.append({
                    'id': cache_id,
                    'key': self.tournament_cache_data[cache_id]['key']
                })
        
        print(f"\n📊 RÉSUMÉ DU MATCHING:")
        print(f"✅ Matched {matched_tournaments}/{len(self.listener_data)} tournois")
        print(f"✅ Analysé {total_matches} matches au total")
        
        if unmatched_listener:
            print(f"\n❌ Tournois listener non-matchés ({len(unmatched_listener)}):")
            for t in unmatched_listener[:5]:
                print(f"  - {t['date'].strftime('%Y-%m-%d')} | {t['name']} | ID: {t['id']} | {t['matches']} matchs")
            if len(unmatched_listener) > 5:
                print(f"  ... et {len(unmatched_listener) - 5} autres")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches,
            'matched_tournaments': matched_tournaments,
            'unmatched_listener': unmatched_listener,
            'unmatched_cache': unmatched_cache
        }
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec toutes les visualisations"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Si peu de matchs, afficher plus de debug
        if analysis['total_matches'] < 100:
            print("\n⚠️ PEU DE MATCHS TROUVÉS - DEBUG ADDITIONNEL:")
            print(f"Tournois listener: {len(self.listener_data)}")
            print(f"Tournois cache: {len(self.tournament_cache_data)}")
            print(f"Tournois matchés: {analysis['matched_tournaments']}")
            
            # Vérifier quelques IDs
            print("\nPremiers IDs listener:", list(self.listener_data.keys())[:5])
            print("Premiers IDs cache:", list(self.tournament_cache_data.keys())[:5])
        
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
        
        # Générer HTML
        html = self._generate_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_fixed_analysis.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse complète générée!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        return output_path
    
    def _generate_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML complet"""
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
            .warning-box {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                color: #856404;
            }
        </style>
        """
        
        # Créer les visualisations seulement si on a assez de données
        viz_html = []
        if analysis['total_matches'] > 0:
            viz_html.append(self._create_pie_chart(meta_data))
            viz_html.append(self._create_bar_chart(meta_data))
            if analysis['total_matches'] > 50:
                viz_html.append(self._create_winrate_chart(meta_data))
                viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data))
        
        # Warning si peu de données
        warning_html = ""
        if analysis['total_matches'] < 100:
            warning_html = f"""
            <div class="warning-box">
                <h3>⚠️ Données limitées</h3>
                <p>Seulement {analysis['total_matches']} matchs analysés sur {analysis['matched_tournaments']} tournois matchés.</p>
                <p>Les statistiques peuvent ne pas être représentatives.</p>
                <p>Tournois non-matchés : {len(analysis.get('unmatched_listener', []))}</p>
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Fixed Analysis with MTGOData</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Fixed Analysis with MTGOData</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Real matchup data from {analysis['matched_tournaments']} tournaments</p>
        </div>
        
        {warning_html}
        
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
        top_15 = [(a, d) for a, d in meta_data if d['matches'] >= 5][:15]
        
        if not top_15:
            return '<div class="visualization-container"><p>Not enough data for bar chart</p></div>'
        
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
        """Crée le graphique des win rates avec CI"""
        filtered = [(a, d) for a, d in meta_data if d['matches'] >= 10][:20]
        filtered.sort(key=lambda x: x[1]['win_rate'], reverse=True)
        
        if not filtered:
            return '<div class="visualization-container"><p>Not enough data for win rate analysis</p></div>'
        
        archetypes = [a[0] for a in filtered]
        win_rates = [a[1]['win_rate'] for a in filtered]
        ci_lower = [a[1]['ci_lower'] for a in filtered]
        ci_upper = [a[1]['ci_upper'] for a in filtered]
        
        fig = go.Figure()
        
        for i, archetype in enumerate(archetypes):
            fig.add_trace(go.Scatter(
                x=[ci_lower[i], ci_upper[i]],
                y=[archetype, archetype],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
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
        top_archetypes = [a[0] for a in meta_data[:10] if a[1]['matches'] >= 10]
        
        if len(top_archetypes) < 2:
            return '<div class="visualization-container"><p>Not enough data for matchup matrix</p></div>'
        
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
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=top_archetypes,
            y=top_archetypes,
            colorscale=[
                [0, '#d32f2f'],
                [0.4, '#ff9800'],
                [0.5, '#ffeb3b'],
                [0.6, '#8bc34a'],
                [1, '#2e7d32']
            ],
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            colorbar=dict(title='Win Rate %')
        ))
        
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
            height=1000
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="matchup-matrix")}</div>'


if __name__ == "__main__":
    analyzer = FixedJulyAnalyzer()
    analyzer.generate_complete_analysis()