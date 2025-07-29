#!/usr/bin/env python3
"""
Analyse CORRIGÉE avec méthode centralisée pour tous les calculs
Plus JAMAIS de calculs dupliqués !
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


class CentralizedAnalyzer:
    """Analyseur avec calculs CENTRALISÉS - une seule source de vérité"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        
    # =====================================================
    # MÉTHODES CENTRALISÉES - SINGLE SOURCE OF TRUTH
    # =====================================================
    
    def calculate_meta_percentage(self, archetype_match_count: int) -> float:
        """
        MÉTHODE UNIQUE pour calculer le % de métagame
        
        IMPORTANT: archetype_match_count compte chaque match 2 fois (1 par joueur)
        donc on divise par 2 pour avoir le VRAI nombre de matches
        """
        if not hasattr(self, '_total_unique_matches'):
            return 0.0
            
        unique_matches = archetype_match_count / 2  # Diviser par 2 car compté 2 fois
        return (unique_matches / self._total_unique_matches) * 100
    
    def calculate_win_rate(self, wins: int, total_matches: int) -> float:
        """
        MÉTHODE UNIQUE pour calculer le win rate
        """
        if total_matches == 0:
            return 50.0  # Default 50% si pas de données
        return (wins / total_matches) * 100
    
    def calculate_tier_score(self, win_rate: float, meta_share: float, total_matches: int) -> Tuple[float, str]:
        """
        MÉTHODE UNIQUE pour calculer le score et tier
        
        Returns: (score, tier)
        """
        # Score de base
        score = (win_rate * 0.6) + (meta_share * 0.4)
        
        # Modificateurs
        if total_matches >= 100:
            score += 5  # Bonus fiabilité
        elif total_matches < 20:
            score -= 10  # Malus petit échantillon
        elif total_matches < 10:
            score -= 15  # Malus extrême
        
        # Déterminer le tier
        if score >= 35 and total_matches >= 30 and win_rate >= 55 and meta_share >= 10:
            tier = 'S'
        elif score >= 30 and total_matches >= 20 and win_rate >= 52 and meta_share >= 5:
            tier = 'A'
        elif score >= 25 and total_matches >= 10 and win_rate >= 48:
            tier = 'B'
        elif score >= 20 and total_matches >= 5 and win_rate >= 45:
            tier = 'C'
        else:
            tier = 'D'
            
        # Règles spéciales
        if win_rate > 60 and meta_share < 2 and tier == 'S':
            tier = 'A'  # Glass cannon rule
        if meta_share > 15 and win_rate < 48:
            tier = 'C' if tier in ['A', 'B'] else tier  # Popular but bad
        if total_matches < 15:
            tier = 'B' if tier in ['S', 'A'] else tier  # New deck rule
            
        return score, tier
    
    def calculate_confidence_interval(self, wins: int, total: int) -> Tuple[float, float]:
        """
        MÉTHODE UNIQUE pour calculer l'intervalle de confiance Wilson
        """
        if total == 0:
            return 0, 100
            
        p = wins / total
        z = 1.96  # 95% confidence
        
        denominator = 1 + z**2/total
        center = (p + z**2/(2*total)) / denominator
        margin = z * math.sqrt(p*(1-p)/total + z**2/(4*total**2)) / denominator
        
        ci_lower = max(0, (center - margin) * 100)
        ci_upper = min(100, (center + margin) * 100)
        
        return ci_lower, ci_upper
    
    # =====================================================
    # MÉTHODES DE CHARGEMENT (inchangées)
    # =====================================================
    
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
                        print(f"⚠️ Erreur lecture {file}: {e}")
        
        print(f"✅ Chargé {count} tournois du listener avec {total_matches} matchs au total")
        return count
    
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
            'matches': 0,  # ATTENTION: compte 2x (1 par joueur)
            'wins': 0,
            'losses': 0,
            'decks': 0,
            'tournaments': set(),
            'players': set(),
            'sideboard_cards': defaultdict(int),
        })
        
        total_unique_matches = 0  # Compte UNIQUE des matches
        matched_tournaments = 0
        tournament_meta = defaultdict(lambda: defaultdict(int))
        
        # Pour chaque tournoi du listener
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
                
                # Analyser les matchups du listener
                for round_num, round_data in enumerate(listener_tournament['rounds'], 1):
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
                                
                                total_unique_matches += 1  # Compter UNE FOIS le match
                                
                                # Update stats (compte 2x car 1 par joueur)
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
        
        # Stocker le total pour les calculs centralisés
        self._total_unique_matches = total_unique_matches
        
        print(f"\n📊 RÉSUMÉ DU MATCHING:")
        print(f"✅ Matched {matched_tournaments}/{len(self.listener_data)} tournois")
        print(f"✅ Analysé {total_unique_matches} matches UNIQUES")
        
        return {
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_unique_matches,  # UNIQUE matches
            'matched_tournaments': matched_tournaments,
            'tournament_meta': dict(tournament_meta)
        }
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec calculs CENTRALISÉS"""
        # Charger toutes les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Calculer TOUTES les métriques avec les méthodes centralisées
        meta_data = []
        for archetype, stats in analysis['archetype_stats'].items():
            # Utiliser UNIQUEMENT les méthodes centralisées
            percentage = self.calculate_meta_percentage(stats['matches'])
            win_rate = self.calculate_win_rate(stats['wins'], stats['matches'])
            ci_lower, ci_upper = self.calculate_confidence_interval(stats['wins'], stats['matches'])
            score, tier = self.calculate_tier_score(win_rate, percentage, stats['matches'])
            
            meta_data.append((archetype, {
                'matches': stats['matches'],
                'unique_matches': stats['matches'] // 2,  # Le vrai nombre
                'percentage': percentage,
                'win_rate': win_rate,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'ci_width': ci_upper - ci_lower,
                'score': score,
                'tier': tier,
                'decks': stats['decks'],
                'tournaments': len(stats['tournaments']),
                'unique_players': len(stats['players']),
                'sideboard_cards': dict(stats['sideboard_cards']),
            }))
        
        # Trier par score composite
        meta_data.sort(key=lambda x: x[1]['score'], reverse=True)
        
        # Générer HTML
        html = self._generate_complete_html_report(analysis, meta_data)
        
        # Sauvegarder
        output_path = Path("data/cache/july_1_21_centralized_fix.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse CORRIGÉE avec calculs centralisés générée!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        # Afficher les insights
        self._print_key_insights(analysis, meta_data)
        
        return output_path
    
    def _generate_complete_html_report(self, analysis: Dict, meta_data: List) -> str:
        """Génère le rapport HTML avec TOUS les calculs centralisés"""
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
            .tier-badge {
                padding: 5px 12px;
                border-radius: 15px;
                font-weight: 600;
                color: white;
                display: inline-block;
            }
            .tier-S { background: #2e7d32; }
            .tier-A { background: #4CAF50; }
            .tier-B { background: #ff9800; }
            .tier-C { background: #ff5722; }
            .tier-D { background: #d32f2f; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            th {
                background: #f5f5f5;
                font-weight: 600;
                color: #667eea;
            }
            .method-note {
                background: #e8f5e9;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 20px 0;
                font-size: 0.95em;
            }
        </style>
        """
        
        viz_html = []
        
        # 1. Méthode de calcul (pour transparence)
        viz_html.append(self._create_methodology_box())
        
        # 2. Pie Chart CORRIGÉ
        viz_html.append(self._create_corrected_pie_chart(meta_data))
        
        # 3. Bar Chart CORRIGÉ avec tiers
        viz_html.append(self._create_corrected_bar_chart(meta_data))
        
        # 4. Tier Distribution
        viz_html.append(self._create_tier_table(meta_data))
        
        # 5. Win Rate par Tier
        viz_html.append(self._create_tiered_winrate_chart(meta_data))
        
        # 6. Matchup Matrix
        viz_html.append(self._create_matchup_matrix(analysis['matchup_data'], meta_data))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - CORRECTED Analysis with Centralized Calculations</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Corrected Metagame Analysis</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 1em; opacity: 0.8;">
                Using CENTRALIZED calculation methods - {analysis['total_matches']:,} unique matches analyzed
            </p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Unique Matches</div>
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
        
        <div class="info-box" style="text-align: center; color: #666;">
            <p>Generated by Manalytics v3.3.0 (FIXED) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="font-size: 0.9em;">✅ Using centralized calculation methods</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _create_methodology_box(self) -> str:
        """Explique la méthodologie de calcul"""
        return """
        <div class="info-box">
            <h2>📐 Calculation Methodology (CENTRALIZED)</h2>
            <div class="method-note">
                <strong>IMPORTANT:</strong> All percentages and statistics in this report use the SAME centralized calculation methods:
                <ul>
                    <li><strong>Meta Share %</strong> = (Archetype Matches ÷ 2) ÷ Total Unique Matches × 100</li>
                    <li><strong>Win Rate %</strong> = Wins ÷ Total Matches × 100</li>
                    <li><strong>Tier Score</strong> = (Win Rate × 0.6) + (Meta Share × 0.4) + Modifiers</li>
                    <li>Matches are divided by 2 because each match is counted twice (once per player)</li>
                </ul>
            </div>
        </div>
        """
    
    def _create_corrected_pie_chart(self, meta_data: List) -> str:
        """Pie chart avec calculs CORRECTS"""
        labels = []
        values = []
        colors = []
        text_info = []
        
        other_pct = 0
        other_count = 0
        other_matches = 0
        
        for i, (archetype, data) in enumerate(meta_data):
            if i < 10 and data['percentage'] > 2:
                labels.append(archetype)
                values.append(data['percentage'])  # Utilise le % centralisé
                text_info.append(
                    f"{archetype}<br>"
                    f"{data['percentage']:.1f}%<br>"
                    f"{data['unique_matches']} matches"
                )
                
                # Couleur
                arch_colors = get_archetype_colors(archetype)
                if len(arch_colors) == 1:
                    color = MTG_COLORS.get(arch_colors[0], '#808080')
                elif len(arch_colors) == 2:
                    color = blend_colors(
                        MTG_COLORS.get(arch_colors[0], '#808080'),
                        MTG_COLORS.get(arch_colors[1], '#404040'),
                        0.6
                    )
                else:
                    color = blend_colors(
                        MTG_COLORS.get(arch_colors[0], '#808080'),
                        MTG_COLORS.get(arch_colors[1], '#404040'),
                        0.5
                    )
                colors.append(color)
            else:
                other_pct += data['percentage']
                other_count += 1
                other_matches += data['unique_matches']
        
        if other_pct > 0:
            labels.append(f"Others ({other_count} archetypes)")
            values.append(other_pct)
            colors.append('#808080')
            text_info.append(f"Others<br>{other_pct:.1f}%<br>{other_matches} matches")
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textposition='inside',
            textinfo='percent',
            texttemplate='%{percent}',
            hovertemplate='<b>%{label}</b><br>Share: %{value:.1f}%<br>%{text}<extra></extra>',
            text=text_info,
            pull=[0.1 if v > 20 else 0 for v in values]
        )])
        
        fig.update_layout(
            title={
                'text': '📊 CORRECTED Metagame Distribution',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#333'}
            },
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            width=1000,
            height=600,
            margin=dict(t=100, b=50, r=250),
            annotations=[{
                'text': f'Based on {self._total_unique_matches} UNIQUE matches (not double-counted)',
                'showarrow': False,
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.1,
                'font': {'size': 12, 'color': '#666'}
            }]
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="pie-chart")}</div>'
    
    def _create_corrected_bar_chart(self, meta_data: List) -> str:
        """Bar chart avec tiers basés sur le score composite"""
        top_15 = meta_data[:15]
        
        archetypes = [a[0] for a in top_15]
        percentages = [a[1]['percentage'] for a in top_15]  # % centralisé
        win_rates = [a[1]['win_rate'] for a in top_15]
        tiers = [a[1]['tier'] for a in top_15]
        scores = [a[1]['score'] for a in top_15]
        
        # Couleurs par tier
        tier_colors = {
            'S': '#2e7d32',
            'A': '#4CAF50', 
            'B': '#ff9800',
            'C': '#ff5722',
            'D': '#d32f2f'
        }
        colors = [tier_colors[t] for t in tiers]
        
        fig = go.Figure()
        
        # Barres principales
        fig.add_trace(go.Bar(
            x=archetypes,
            y=percentages,
            marker=dict(color=colors, line=dict(color='black', width=1)),
            text=[f"{p:.1f}%<br>Tier {t}<br>Score: {s:.1f}" 
                  for p, t, s in zip(percentages, tiers, scores)],
            textposition='outside',
            name='Meta Share',
            hovertemplate=(
                '<b>%{x}</b><br>'
                'Meta Share: %{y:.1f}%<br>'
                '%{text}<extra></extra>'
            )
        ))
        
        # Win rate line
        fig.add_trace(go.Scatter(
            x=archetypes,
            y=[wr/2 for wr in win_rates],  # Scale for dual axis
            mode='lines+markers',
            name='Win Rate (÷2)',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Win Rate: %{customdata:.1f}%<extra></extra>',
            customdata=win_rates
        ))
        
        fig.update_layout(
            title={
                'text': '📈 Top 15 Archetypes - CORRECTED Meta Share with Composite Tiers',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#333'}
            },
            xaxis=dict(title='Archetype', tickangle=-45),
            yaxis=dict(title='Meta Share % (Corrected)', side='left'),
            yaxis2=dict(
                title='Win Rate % (scaled ÷2)',
                overlaying='y',
                side='right',
                range=[20, 35]
            ),
            width=1400,
            height=700,
            margin=dict(b=150),
            hovermode='x unified',
            legend=dict(x=0.02, y=0.98)
        )
        
        fig.add_hline(y=25, line_dash="dash", line_color="red", opacity=0.3, yref='y2')
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="bar-chart")}</div>'
    
    def _create_tier_table(self, meta_data: List) -> str:
        """Table détaillée des tiers"""
        html = """
        <div class="info-box">
            <h2>📊 Tier Distribution (Composite Score System)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Archetype</th>
                        <th>Tier</th>
                        <th>Score</th>
                        <th>Win Rate</th>
                        <th>Meta Share</th>
                        <th>Matches</th>
                        <th>95% CI</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, (arch, data) in enumerate(meta_data[:20], 1):
            tier_class = f"tier-{data['tier']}"
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{arch}</strong></td>
                    <td><span class="tier-badge {tier_class}">{data['tier']}</span></td>
                    <td>{data['score']:.1f}</td>
                    <td>{data['win_rate']:.1f}%</td>
                    <td>{data['percentage']:.1f}%</td>
                    <td>{data['unique_matches']}</td>
                    <td>[{data['ci_lower']:.1f}%, {data['ci_upper']:.1f}%]</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
            <p style="color: #666; font-size: 0.9em; margin-top: 15px;">
                💡 Score = (Win Rate × 0.6) + (Meta Share × 0.4) + Modifiers
            </p>
        </div>
        """
        
        return html
    
    def _create_tiered_winrate_chart(self, meta_data: List) -> str:
        """Win rate chart organisé par tiers"""
        # Grouper par tier
        tiers = {'S': [], 'A': [], 'B': [], 'C': [], 'D': []}
        
        for arch, data in meta_data:
            if data['unique_matches'] >= 10:  # Au moins 10 matches pour apparaître
                tiers[data['tier']].append((arch, data))
        
        # Trier chaque tier par win rate
        for tier in tiers:
            tiers[tier].sort(key=lambda x: x[1]['win_rate'], reverse=True)
        
        fig = go.Figure()
        
        y_position = 0
        annotations = []
        
        tier_colors = {
            'S': '#2e7d32',
            'A': '#4CAF50',
            'B': '#ff9800',
            'C': '#ff5722',
            'D': '#d32f2f'
        }
        
        for tier_name in ['S', 'A', 'B', 'C', 'D']:
            if tiers[tier_name]:
                # Label du tier
                annotations.append({
                    'x': 35,
                    'y': y_position - 0.5,
                    'text': f'<b>{tier_name} Tier ({len(tiers[tier_name])} archetypes)</b>',
                    'showarrow': False,
                    'font': {'size': 14, 'color': tier_colors[tier_name]},
                    'xanchor': 'left'
                })
                y_position -= 1
                
                for arch, data in tiers[tier_name]:
                    # CI lines
                    fig.add_trace(go.Scatter(
                        x=[data['ci_lower'], data['ci_upper']],
                        y=[y_position, y_position],
                        mode='lines',
                        line=dict(color=tier_colors[tier_name], width=3),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Point
                    fig.add_trace(go.Scatter(
                        x=[data['win_rate']],
                        y=[y_position],
                        mode='markers+text',
                        marker=dict(
                            size=10 + math.sqrt(data['unique_matches']),
                            color=tier_colors[tier_name],
                            line=dict(color='black', width=1)
                        ),
                        text=f"{arch} ({data['win_rate']:.1f}%, {data['percentage']:.1f}% meta)",
                        textposition='middle right',
                        showlegend=False,
                        hovertemplate=(
                            f'<b>{arch}</b><br>'
                            f'Tier: {tier_name}<br>'
                            f'Win Rate: {data["win_rate"]:.1f}%<br>'
                            f'Meta Share: {data["percentage"]:.1f}%<br>'
                            f'Score: {data["score"]:.1f}<br>'
                            f'Matches: {data["unique_matches"]}<extra></extra>'
                        )
                    ))
                    
                    y_position -= 1
                
                y_position -= 0.5
        
        fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '📊 Win Rates by Composite Tier',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#333'}
            },
            xaxis=dict(title='Win Rate %', range=[30, 75]),
            yaxis=dict(showticklabels=False, showgrid=False),
            width=1400,
            height=max(800, abs(y_position) * 35),
            annotations=annotations,
            showlegend=False,
            margin=dict(l=50, r=450)
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="winrate-tiers")}</div>'
    
    def _create_matchup_matrix(self, matchup_data: Dict, meta_data: List) -> str:
        """Matrice de matchups"""
        # Top 10 archétypes par score
        top_archetypes = [a[0] for a in meta_data[:10] if a[1]['unique_matches'] >= 20]
        
        if len(top_archetypes) < 3:
            return '<div class="visualization-container"><p>Not enough data for matchup matrix</p></div>'
        
        matrix = []
        hover_texts = []
        
        for i, arch1 in enumerate(top_archetypes):
            row = []
            hover_row = []
            
            for j, arch2 in enumerate(top_archetypes):
                if arch1 == arch2:
                    row.append(50)
                    hover_row.append(f"{arch1} vs {arch2}<br>Mirror: 50%")
                else:
                    if arch1 in matchup_data and arch2 in matchup_data[arch1]:
                        wins = matchup_data[arch1][arch2]['wins']
                        losses = matchup_data[arch1][arch2]['losses']
                        total = wins + losses
                        
                        if total > 0:
                            win_rate = self.calculate_win_rate(wins, total)
                            row.append(win_rate)
                            hover_row.append(
                                f"{arch1} vs {arch2}<br>"
                                f"Win Rate: {win_rate:.1f}%<br>"
                                f"Record: {wins}-{losses}"
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
            colorbar=dict(title='Win Rate %'),
            zmid=50
        ))
        
        fig.update_layout(
            title={
                'text': '🎲 Matchup Matrix - Top Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#333'}
            },
            xaxis=dict(title='Opponent', side='bottom', tickangle=-45),
            yaxis=dict(title='Your Deck', autorange='reversed'),
            width=1100,
            height=1100
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="matchup-matrix")}</div>'
    
    def _print_key_insights(self, analysis: Dict, meta_data: List):
        """Affiche les insights clés"""
        print("\n" + "="*80)
        print("🔍 CORRECTED ANALYSIS - STANDARD METAGAME JULY 1-21, 2025")
        print("="*80)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  • Total UNIQUE Matches: {analysis['total_matches']:,}")
        print(f"  • Tournaments: {analysis['matched_tournaments']}")
        print(f"  • Unique Archetypes: {len(analysis['archetype_stats'])}")
        
        print(f"\n🏆 TOP 5 BY COMPOSITE SCORE:")
        for i, (arch, data) in enumerate(meta_data[:5], 1):
            print(f"  {i}. {arch}: Score {data['score']:.1f} (Tier {data['tier']})")
            print(f"     → {data['percentage']:.1f}% meta, {data['win_rate']:.1f}% WR, {data['unique_matches']} matches")
        
        print(f"\n📊 TIER DISTRIBUTION:")
        tier_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for _, data in meta_data:
            tier_counts[data['tier']] += 1
        
        for tier in ['S', 'A', 'B', 'C', 'D']:
            if tier_counts[tier] > 0:
                print(f"  {tier} Tier: {tier_counts[tier]} archetypes")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    analyzer = CentralizedAnalyzer()
    analyzer.generate_complete_analysis()