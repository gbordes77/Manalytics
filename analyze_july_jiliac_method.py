#!/usr/bin/env python3
"""
Analyse avec la méthode EXACTE de Jiliac
Implémentation Python fidèle du code R
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import math
import numpy as np
from collections import defaultdict
import re
from scipy import stats

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS, blend_colors
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class JiliacMethodAnalyzer:
    """Analyseur utilisant EXACTEMENT la méthode de Jiliac"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.listener_data = {}
        self.tournament_cache_data = {}
        self.CI_PERCENT = 0.95  # Comme dans Parameters.R
        
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
        
        # Structure pour les données (comme dans le R)
        archetype_stats = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'draws': 0,  # On garde les draws même s'ils ne comptent pas dans le WR
            'copies': 0,  # Nombre de fois que l'archétype apparaît
            'players': set(),
            'matches': 0,  # wins + losses + draws
            'tournaments': set(),
        })
        
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        total_matches_played = 0  # Total des matches JOUÉS par tous les archétypes
        matched_tournaments = 0
        
        # Pour chaque tournoi du listener
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
                        archetype_stats[archetype]['copies'] += 1
                        archetype_stats[archetype]['players'].add(player)
                        archetype_stats[archetype]['tournaments'].add(listener_id)
                
                # Analyser les matchups
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
                                draws = int(parts[2]) if len(parts) > 2 else 0
                                
                                # Chaque archétype joue 1 match
                                archetype_stats[arch1]['matches'] += 1
                                archetype_stats[arch2]['matches'] += 1
                                total_matches_played += 2  # 2 archétypes jouent
                                
                                if p1_wins > p2_wins:
                                    archetype_stats[arch1]['wins'] += 1
                                    archetype_stats[arch2]['losses'] += 1
                                    matchup_data[arch1][arch2]['wins'] += 1
                                    matchup_data[arch2][arch1]['losses'] += 1
                                elif p2_wins > p1_wins:
                                    archetype_stats[arch1]['losses'] += 1
                                    archetype_stats[arch2]['wins'] += 1
                                    matchup_data[arch1][arch2]['losses'] += 1
                                    matchup_data[arch2][arch1]['wins'] += 1
                                else:
                                    # Match nul
                                    archetype_stats[arch1]['draws'] += draws
                                    archetype_stats[arch2]['draws'] += draws
                            except ValueError:
                                continue
        
        print(f"\n📊 RÉSUMÉ DU MATCHING:")
        print(f"✅ Matched {matched_tournaments}/{len(self.listener_data)} tournois")
        print(f"✅ Total matches joués (somme pour tous les archétypes): {total_matches_played}")
        
        return {
            'archetype_stats': dict(archetype_stats),
            'matchup_data': dict(matchup_data),
            'total_matches_played': total_matches_played,
            'matched_tournaments': matched_tournaments
        }
    
    def archetype_metrics(self, analysis: Dict) -> List[Tuple[str, Dict]]:
        """
        Implémente archetype_metrics() de Jiliac (ligne 182 du R)
        Calcule presence, win rate et CI pour chaque archétype
        """
        metric_data = []
        total_matches_played = analysis['total_matches_played']
        
        for archetype, stats in analysis['archetype_stats'].items():
            # Ligne 221 : Matches = Wins + Draws + Defeats
            matches = stats['matches']
            
            # Ligne 224 : Presence = 100 * matches / sum(all_matches)
            presence = (matches / total_matches_played) * 100 if total_matches_played > 0 else 0
            
            # Ligne 227-228 : Win Rate = Wins * 100 / (Wins + Defeats)
            # IMPORTANT: Les draws ne comptent PAS dans le calcul du win rate !
            total_games = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] * 100 / total_games) if total_games > 0 else 50.0
            
            # Calcul de l'intervalle de confiance (Wilson pour être cohérent)
            ci_lower, ci_upper = self.calculate_wilson_ci(stats['wins'], total_games)
            
            metric_data.append((archetype, {
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats['draws'],
                'copies': stats['copies'],
                'players': len(stats['players']),
                'matches': matches,
                'presence': presence,
                'measured_win_rate': win_rate,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'tournaments': len(stats['tournaments'])
            }))
        
        return metric_data
    
    def calculate_wilson_ci(self, wins: int, total: int) -> Tuple[float, float]:
        """Calcule l'intervalle de confiance Wilson à 95%"""
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
    
    def archetype_normalized_sum(self, metric_data: List, stat_share: float) -> List:
        """
        Implémente archetype_normalized_sum() de Jiliac (ligne 324)
        Normalise presence et win rate, calcule la somme
        """
        # Ligne 329 : Garder seulement les decks au-dessus de stat_share
        filtered_data = [(arch, data) for arch, data in metric_data if data['presence'] > stat_share]
        
        if not filtered_data:
            return filtered_data
        
        # Ligne 333-335 : Normaliser la présence avec LOG
        presences = [data['presence'] for _, data in filtered_data]
        min_presence = min(presences)
        log_presences = [np.log(p) - np.log(min_presence) for p in presences]
        max_log_presence = max(log_presences) if max(log_presences) > 0 else 1
        
        # Ligne 337-339 : Normaliser le win rate (sans log)
        win_rates = [data['measured_win_rate'] for _, data in filtered_data]
        min_wr = min(win_rates)
        normalized_wrs = [wr - min_wr for wr in win_rates]
        max_normalized_wr = max(normalized_wrs) if max(normalized_wrs) > 0 else 1
        
        # Appliquer les normalisations
        result = []
        for i, (arch, data) in enumerate(filtered_data):
            # Ligne 344-346 et 349-350 : Diviser par max pour avoir [0,1]
            normalized_presence = log_presences[i] / max_log_presence
            normalized_wr = normalized_wrs[i] / max_normalized_wr
            
            # Ligne 354-356 : Somme normalisée
            normalized_sum = normalized_presence + normalized_wr
            
            data_copy = data.copy()
            data_copy.update({
                'normalized_presence': normalized_presence,
                'normalized_win_rate': normalized_wr,
                'normalized_sum': normalized_sum
            })
            result.append((arch, data_copy))
        
        return result
    
    def archetype_tiers(self, normalized_data: List) -> Tuple[List, float, float]:
        """
        Implémente archetype_tiers() de Jiliac (ligne 376)
        Assigne les tiers basés sur la borne inférieure de l'IC
        """
        if not normalized_data:
            return normalized_data, 0, 0
        
        # Ligne 417-418 : Trier par Lower Bound CI décroissant
        sorted_by_ci = sorted(normalized_data, key=lambda x: x[1]['ci_lower'], reverse=True)
        
        # Ligne 424-425 : Calculer moyenne et écart-type
        ci_lowers = [data['ci_lower'] for _, data in sorted_by_ci]
        mean_ci = np.mean(ci_lowers)
        sd_ci = np.std(ci_lowers, ddof=1)  # ddof=1 pour l'écart-type échantillon
        
        # Assigner les tiers (lignes 427-445)
        result = []
        for i, (arch, data) in enumerate(sorted_by_ci):
            ci_lower = data['ci_lower']
            
            # Déterminer le tier selon les seuils de Jiliac
            if ci_lower >= mean_ci + 3 * sd_ci:
                tier = "0"
            elif ci_lower >= mean_ci + 2 * sd_ci:
                tier = "0.5"
            elif ci_lower >= mean_ci + 1 * sd_ci:
                tier = "1"
            elif ci_lower >= mean_ci:
                tier = "1.5"
            elif ci_lower >= mean_ci - 1 * sd_ci:
                tier = "2"
            elif ci_lower >= mean_ci - 2 * sd_ci:
                tier = "2.5"
            elif ci_lower >= mean_ci - 3 * sd_ci:
                tier = "3"
            else:
                tier = "Other"
            
            data_copy = data.copy()
            data_copy['tier'] = tier
            data_copy['rank_ci'] = i + 1
            result.append((arch, data_copy))
        
        # Retourner aussi par somme normalisée décroissante (ligne 380-381)
        result.sort(key=lambda x: x[1]['normalized_sum'], reverse=True)
        for i, (arch, data) in enumerate(result):
            data['rank_sum'] = i + 1
        
        return result, mean_ci, sd_ci
    
    def generate_complete_analysis(self):
        """Génère l'analyse complète avec la méthode de Jiliac"""
        # Charger les données
        self.load_listener_data()
        self.load_cache_data()
        
        # Analyser
        analysis = self.merge_and_analyze()
        
        # Appliquer la pipeline de Jiliac
        # 1. archetype_metrics
        metric_data = self.archetype_metrics(analysis)
        
        # 2. Définir stat_share (2% par défaut comme ChartShare)
        stat_share = 2.0
        
        # 3. archetype_normalized_sum
        normalized_data = self.archetype_normalized_sum(metric_data, stat_share)
        
        # 4. archetype_tiers
        tiered_data, mean_ci, sd_ci = self.archetype_tiers(normalized_data)
        
        # Générer HTML
        html = self._generate_jiliac_html_report(analysis, tiered_data, mean_ci, sd_ci)
        
        # Sauvegarder
        output_path = Path("data/cache/july_1_21_jiliac_method.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Analyse avec méthode Jiliac générée!")
        print(f"📄 Fichier: {output_path}")
        print(f"🌐 Ouvrir: file://{output_path.absolute()}")
        
        # Afficher les insights
        self._print_jiliac_insights(tiered_data, mean_ci, sd_ci)
        
        return output_path
    
    def _generate_jiliac_html_report(self, analysis: Dict, tiered_data: List, mean_ci: float, sd_ci: float) -> str:
        """Génère le rapport HTML dans le style Jiliac"""
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
            .method-box {
                background: #e8f5e9;
                border-left: 4px solid #4CAF50;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }
            .tier-badge {
                padding: 6px 15px;
                border-radius: 20px;
                font-weight: 600;
                color: white;
                display: inline-block;
                margin: 2px;
            }
            .tier-0 { background: #1b5e20; }
            .tier-0\\.5 { background: #2e7d32; }
            .tier-1 { background: #388e3c; }
            .tier-1\\.5 { background: #43a047; }
            .tier-2 { background: #fb8c00; }
            .tier-2\\.5 { background: #ff6f00; }
            .tier-3 { background: #e53935; }
            .tier-Other { background: #757575; }
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
            tr:hover {
                background: #f9f9f9;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-card {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: 700;
                color: #667eea;
            }
            .stat-label {
                font-size: 0.9em;
                color: #666;
            }
        </style>
        """
        
        # Calculer les stats globales
        total_unique_matches = sum(d['matches'] for _, d in tiered_data) // 2
        
        viz_html = []
        
        # 1. Méthode Jiliac expliquée
        viz_html.append(self._create_jiliac_methodology())
        
        # 2. Stats sur les tiers
        viz_html.append(self._create_tier_statistics(tiered_data, mean_ci, sd_ci))
        
        # 3. Table détaillée comme Jiliac
        viz_html.append(self._create_jiliac_archetype_table(tiered_data))
        
        # 4. Pie chart (méthode Jiliac)
        viz_html.append(self._create_jiliac_pie_chart(tiered_data))
        
        # 5. Bar chart avec presence et win rate
        viz_html.append(self._create_jiliac_bar_chart(tiered_data))
        
        # 6. Win rate mustache plot (avec CI)
        viz_html.append(self._create_jiliac_winrate_plot(tiered_data))
        
        # 7. Scatter plot presence vs win rate avec tiers
        viz_html.append(self._create_jiliac_scatter_plot(tiered_data))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Analysis using Jiliac's R Method</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Jiliac Method Analysis</h1>
            <p>Standard Format - July 1-21, 2025</p>
            <p style="font-size: 1em; opacity: 0.8;">
                Using exact methodology from R-Meta-Analysis by Jiliac
            </p>
        </div>
        
        {''.join(viz_html)}
        
        <div class="visualization-container" style="text-align: center; color: #666;">
            <p>Generated by Manalytics v3.4.0 (Jiliac Method) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="font-size: 0.9em;">📊 Based on R-Meta-Analysis methodology</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _create_jiliac_methodology(self) -> str:
        """Explique la méthode Jiliac"""
        return """
        <div class="visualization-container">
            <h2>📐 Jiliac's R-Meta-Analysis Methodology</h2>
            <div class="method-box">
                <h3>Key Calculations:</h3>
                <ul>
                    <li><strong>Presence %</strong> = (Archetype Matches / Total Matches) × 100</li>
                    <li><strong>Win Rate %</strong> = Wins × 100 / (Wins + Losses) <em>(draws excluded)</em></li>
                    <li><strong>Normalized Presence</strong> = [log(Presence) - log(min)] / max</li>
                    <li><strong>Normalized Win Rate</strong> = [WR - min(WR)] / max</li>
                    <li><strong>Composite Score</strong> = Normalized Presence + Normalized Win Rate</li>
                </ul>
                <h3>Tier System (based on CI lower bound):</h3>
                <ul>
                    <li><span class="tier-badge tier-0">Tier 0</span> CI lower ≥ mean + 3σ</li>
                    <li><span class="tier-badge tier-0.5">Tier 0.5</span> CI lower ≥ mean + 2σ</li>
                    <li><span class="tier-badge tier-1">Tier 1</span> CI lower ≥ mean + 1σ</li>
                    <li><span class="tier-badge tier-1.5">Tier 1.5</span> CI lower ≥ mean</li>
                    <li><span class="tier-badge tier-2">Tier 2</span> CI lower ≥ mean - 1σ</li>
                    <li><span class="tier-badge tier-2.5">Tier 2.5</span> CI lower ≥ mean - 2σ</li>
                    <li><span class="tier-badge tier-3">Tier 3</span> CI lower ≥ mean - 3σ</li>
                </ul>
            </div>
        </div>
        """
    
    def _create_tier_statistics(self, tiered_data: List, mean_ci: float, sd_ci: float) -> str:
        """Statistiques sur les tiers"""
        tier_counts = {}
        for _, data in tiered_data:
            tier = data['tier']
            if tier not in tier_counts:
                tier_counts[tier] = 0
            tier_counts[tier] += 1
        
        html = f"""
        <div class="visualization-container">
            <h2>📊 Tier Distribution Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{mean_ci:.1f}%</div>
                    <div class="stat-label">Mean CI Lower</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">±{sd_ci:.1f}%</div>
                    <div class="stat-label">Std Deviation</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(tiered_data)}</div>
                    <div class="stat-label">Archetypes Analyzed</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
        """
        
        # Afficher le compte par tier
        for tier in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "Other"]:
            if tier in tier_counts:
                html += f'<span class="tier-badge tier-{tier}">{tier}: {tier_counts[tier]} archetypes</span> '
        
        html += """
            </div>
        </div>
        """
        return html
    
    def _create_jiliac_archetype_table(self, tiered_data: List) -> str:
        """Table détaillée style Jiliac"""
        html = """
        <div class="visualization-container">
            <h2>📋 Archetype Metrics (Jiliac Method)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Archetype</th>
                        <th>Tier</th>
                        <th>Presence %</th>
                        <th>Win Rate %</th>
                        <th>CI Lower</th>
                        <th>CI Upper</th>
                        <th>Matches</th>
                        <th>Norm. Score</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, (arch, data) in enumerate(tiered_data[:20], 1):
            tier_class = f"tier-{data['tier'].replace('.', '\\.')}"
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{arch}</strong></td>
                    <td><span class="tier-badge {tier_class}">{data['tier']}</span></td>
                    <td>{data['presence']:.1f}%</td>
                    <td>{data['measured_win_rate']:.1f}%</td>
                    <td>{data['ci_lower']:.1f}%</td>
                    <td>{data['ci_upper']:.1f}%</td>
                    <td>{data['matches']}</td>
                    <td>{data['normalized_sum']:.3f}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _create_jiliac_pie_chart(self, tiered_data: List) -> str:
        """Pie chart style Jiliac (avec seuil à 2%)"""
        # Filtrer < 2% dans "Others"
        labels = []
        values = []
        colors = []
        
        other_pct = 0
        other_count = 0
        
        for arch, data in tiered_data:
            if data['presence'] >= 2.0:  # Seuil de 2%
                labels.append(arch)
                values.append(data['presence'])
                
                # Couleur MTG
                arch_colors = get_archetype_colors(arch)
                if len(arch_colors) == 1:
                    color = MTG_COLORS.get(arch_colors[0], '#808080')
                else:
                    color = blend_colors(
                        MTG_COLORS.get(arch_colors[0], '#808080'),
                        MTG_COLORS.get(arch_colors[1], '#404040'),
                        0.6
                    )
                colors.append(color)
            else:
                other_pct += data['presence']
                other_count += 1
        
        if other_pct > 0:
            labels.append(f"Other (each < 2%)")
            values.append(other_pct)
            colors.append('#808080')
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textposition='inside',
            textinfo='percent',
            texttemplate='%{percent}',
            hovertemplate='<b>%{label}</b><br>Presence: %{value:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Metagame Distribution (Jiliac Method)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#333'}
            },
            width=900,
            height=600,
            showlegend=True
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="jiliac-pie")}</div>'
    
    def _create_jiliac_bar_chart(self, tiered_data: List) -> str:
        """Bar chart avec presence et win rate (style Jiliac)"""
        # Top 15 avec > 2% presence
        top_data = [(a, d) for a, d in tiered_data if d['presence'] >= 2.0][:15]
        
        archetypes = [a for a, _ in top_data]
        presences = [d['presence'] for _, d in top_data]
        win_rates = [d['measured_win_rate'] for _, d in top_data]
        tiers = [d['tier'] for _, d in top_data]
        
        # Couleurs par tier
        tier_colors = {
            '0': '#1b5e20',
            '0.5': '#2e7d32',
            '1': '#388e3c',
            '1.5': '#43a047',
            '2': '#fb8c00',
            '2.5': '#ff6f00',
            '3': '#e53935',
            'Other': '#757575'
        }
        colors = [tier_colors.get(t, '#808080') for t in tiers]
        
        fig = go.Figure()
        
        # Barres de présence
        fig.add_trace(go.Bar(
            x=archetypes,
            y=presences,
            name='Presence %',
            marker=dict(color=colors, line=dict(color='black', width=1)),
            text=[f"{p:.1f}%<br>Tier {t}" for p, t in zip(presences, tiers)],
            textposition='outside'
        ))
        
        # Ligne de win rate
        fig.add_trace(go.Scatter(
            x=archetypes,
            y=[wr/2 for wr in win_rates],  # Diviser pour l'échelle
            mode='lines+markers',
            name='Win Rate (÷2)',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Presence Bar Chart (Jiliac Method)',
            xaxis=dict(tickangle=-45),
            yaxis=dict(title='Presence %'),
            yaxis2=dict(
                title='Win Rate % (÷2)',
                overlaying='y',
                side='right',
                range=[20, 35]
            ),
            width=1200,
            height=600,
            margin=dict(b=150)
        )
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="jiliac-bar")}</div>'
    
    def _create_jiliac_winrate_plot(self, tiered_data: List) -> str:
        """Win rate mustache plot avec CI (style Jiliac)"""
        # Filtrer les archétypes avec assez de données
        plot_data = [(a, d) for a, d in tiered_data if d['matches'] >= 20]
        plot_data.sort(key=lambda x: x[1]['ci_lower'], reverse=True)
        
        fig = go.Figure()
        
        y_pos = list(range(len(plot_data)))
        
        for i, (arch, data) in enumerate(plot_data):
            # Ligne CI
            fig.add_trace(go.Scatter(
                x=[data['ci_lower'], data['ci_upper']],
                y=[i, i],
                mode='lines',
                line=dict(color='#667eea', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Point central
            fig.add_trace(go.Scatter(
                x=[data['measured_win_rate']],
                y=[i],
                mode='markers',
                marker=dict(size=10, color='#667eea'),
                showlegend=False,
                hovertemplate=(
                    f'<b>{arch}</b><br>'
                    f'Win Rate: {data["measured_win_rate"]:.1f}%<br>'
                    f'95% CI: [{data["ci_lower"]:.1f}%, {data["ci_upper"]:.1f}%]<br>'
                    f'Tier: {data["tier"]}<extra></extra>'
                )
            ))
        
        # Labels
        fig.update_layout(
            title='Win Rate with Confidence Intervals (Jiliac Method)',
            xaxis=dict(title='Win Rate %', range=[30, 70]),
            yaxis=dict(
                tickmode='array',
                tickvals=y_pos,
                ticktext=[a for a, _ in plot_data],
                autorange='reversed'
            ),
            width=1000,
            height=max(600, len(plot_data) * 30),
            margin=dict(l=200)
        )
        
        # Ligne 50%
        fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5)
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="jiliac-mustache")}</div>'
    
    def _create_jiliac_scatter_plot(self, tiered_data: List) -> str:
        """Scatter plot presence vs win rate avec tiers"""
        fig = go.Figure()
        
        # Grouper par tier
        tier_colors = {
            '0': '#1b5e20',
            '0.5': '#2e7d32',
            '1': '#388e3c',
            '1.5': '#43a047',
            '2': '#fb8c00',
            '2.5': '#ff6f00',
            '3': '#e53935',
            'Other': '#757575'
        }
        
        for tier, color in tier_colors.items():
            tier_data = [(a, d) for a, d in tiered_data if d['tier'] == tier]
            if tier_data:
                fig.add_trace(go.Scatter(
                    x=[d['presence'] for _, d in tier_data],
                    y=[d['measured_win_rate'] for _, d in tier_data],
                    mode='markers+text',
                    name=f'Tier {tier}',
                    marker=dict(
                        size=[10 + math.sqrt(d['matches']) for _, d in tier_data],
                        color=color,
                        line=dict(color='black', width=1)
                    ),
                    text=[a if d['presence'] > 5 else '' for a, d in tier_data],
                    textposition='top center',
                    hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<extra></extra>'
                ))
        
        fig.update_layout(
            title='Win Rate & Presence Scatterplot (Jiliac Method)',
            xaxis=dict(title='Presence %', type='log', range=[-0.5, 2]),
            yaxis=dict(title='Win Rate %', range=[30, 70]),
            width=1200,
            height=700
        )
        
        # Lignes de référence
        fig.add_hline(y=50, line_dash="dash", line_color="black", opacity=0.3)
        
        return f'<div class="visualization-container">{fig.to_html(include_plotlyjs=False, div_id="jiliac-scatter")}</div>'
    
    def _print_jiliac_insights(self, tiered_data: List, mean_ci: float, sd_ci: float):
        """Affiche les insights style Jiliac"""
        print("\n" + "="*80)
        print("🔍 JILIAC METHOD ANALYSIS - STANDARD METAGAME JULY 1-21, 2025")
        print("="*80)
        
        print(f"\n📊 TIER STATISTICS:")
        print(f"  • Mean CI Lower Bound: {mean_ci:.1f}%")
        print(f"  • Std Deviation: {sd_ci:.1f}%")
        print(f"  • Archetypes above 2% threshold: {len([d for _, d in tiered_data if d['presence'] >= 2])}")
        
        print(f"\n🏆 TOP TIERS (0-1):")
        top_tiers = [(a, d) for a, d in tiered_data if d['tier'] in ['0', '0.5', '1']]
        for arch, data in top_tiers[:5]:
            print(f"  • {arch}: Tier {data['tier']}")
            print(f"    → {data['presence']:.1f}% presence, {data['measured_win_rate']:.1f}% WR")
            print(f"    → CI: [{data['ci_lower']:.1f}%, {data['ci_upper']:.1f}%]")
        
        print(f"\n📈 HIGHEST WIN RATES (min 20 matches):")
        by_wr = [(a, d) for a, d in tiered_data if d['matches'] >= 20]
        by_wr.sort(key=lambda x: x[1]['measured_win_rate'], reverse=True)
        for arch, data in by_wr[:3]:
            print(f"  • {arch}: {data['measured_win_rate']:.1f}% ({data['matches']} matches)")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    analyzer = JiliacMethodAnalyzer()
    analyzer.generate_complete_analysis()