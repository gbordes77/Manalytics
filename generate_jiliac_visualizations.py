#!/usr/bin/env python3
"""
Génère les 6 visualisations principales de Jiliac pour l'analyse MTG.
Basé sur https://github.com/Jiliac/R-Meta-Analysis/blob/master/Scripts/Executables/_main.R

Les 6 visualisations:
1. Metagame Pie Chart (présence par archétype)
2. Metagame Bar Chart (présence par archétype)
3. Win Rate Graph avec intervalles de confiance (Mustache Box)
4. Win Rate Box Plot
5. Tier Scatterplot (archétypes classés par score normalisé)
6. Winrate & Presence Scatterplot (2 versions: full + zoom)
+ Bonus: Matchup Matrix
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import math

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.manalytics.analyzers.matchup_calculator import MatchupCalculator
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class JiliacVisualizer:
    """Génère les visualisations à la Jiliac"""
    
    def __init__(self):
        self.db = CacheDatabase()
        self.reader = CacheReader()
        self.matchup_calc = MatchupCalculator()
        # self.plotly_viz = PlotlyVisualizer()  # Not needed, we'll create our own charts
        
    def get_july_data(self) -> Tuple[Dict[str, Dict], int]:
        """Récupère les données du 1-21 juillet avec analyse par MATCHES"""
        print("\n📊 Récupération des données juillet 1-21...")
        
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 21, 23, 59, 59)
        
        # Get tournaments
        all_tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        
        # Filter competitive only
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
        
        # Analyze by MATCHES (not decks)
        archetype_data = {}
        total_matches = 0
        
        for tournament in competitive_tournaments:
            month_key = tournament.date.strftime("%Y-%m")
            decklists_file = Path(f"data/cache/decklists/{month_key}.json")
            
            if decklists_file.exists():
                with open(decklists_file, 'r') as f:
                    month_data = json.load(f)
                
                if tournament.id in month_data:
                    decklists = month_data[tournament.id].get('decklists', [])
                    
                    for deck in decklists:
                        wins = deck.get('wins') or 0
                        losses = deck.get('losses') or 0
                        matches_played = wins + losses
                        
                        if matches_played > 0:
                            archetype = deck.get('archetype') or 'Unknown'
                            if not archetype:
                                archetype = 'Unknown'
                            
                            if archetype not in archetype_data:
                                archetype_data[archetype] = {
                                    'matches': 0,
                                    'wins': 0,
                                    'losses': 0,
                                    'decks': []
                                }
                            
                            archetype_data[archetype]['matches'] += matches_played
                            archetype_data[archetype]['wins'] += wins
                            archetype_data[archetype]['losses'] += losses
                            archetype_data[archetype]['decks'].append({
                                'wins': wins,
                                'losses': losses,
                                'player': deck.get('player', 'Unknown')
                            })
                            
                            total_matches += matches_played
        
        # Calculate percentages and win rates
        for archetype, data in archetype_data.items():
            data['presence_pct'] = (data['matches'] / total_matches * 100) if total_matches > 0 else 0
            total_games = data['wins'] + data['losses']
            data['win_rate'] = (data['wins'] / total_games * 100) if total_games > 0 else 50
            
            # Wilson confidence interval
            if total_games > 0:
                p = data['wins'] / total_games
                z = 1.96  # 95% confidence
                n = total_games
                
                denominator = 1 + z**2/n
                center = (p + z**2/(2*n)) / denominator
                margin = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denominator
                
                data['ci_lower'] = max(0, (center - margin) * 100)
                data['ci_upper'] = min(100, (center + margin) * 100)
            else:
                data['ci_lower'] = 0
                data['ci_upper'] = 100
        
        return archetype_data, total_matches
    
    def generate_1_pie_chart(self, archetype_data: Dict[str, Dict]) -> str:
        """1. Génère le Metagame Pie Chart"""
        # Sort by presence
        sorted_data = sorted(archetype_data.items(), 
                           key=lambda x: x[1]['presence_pct'], 
                           reverse=True)
        
        # Take top 10, group others
        labels = []
        values = []
        colors = []
        
        color_map = {
            'Mono White': '#FFFACD',
            'Domain': '#90EE90',
            'Esper': '#4169E1',
            'Boros': '#FFB6C1',
            'Izzet': '#FF69B4',
            'Gruul': '#FF6347',
            'Dimir': '#191970',
            'Azorius': '#87CEEB',
            'Rakdos': '#8B0000',
            'Golgari': '#556B2F'
        }
        
        other_pct = 0
        for i, (archetype, data) in enumerate(sorted_data):
            if i < 10:
                labels.append(f"{archetype} ({data['presence_pct']:.1f}%)")
                values.append(data['presence_pct'])
                
                # Find color
                color = '#808080'  # Default gray
                if archetype:  # Check if archetype is not None
                    for key, val in color_map.items():
                        if key.lower() in archetype.lower():
                            color = val
                            break
                colors.append(color)
            else:
                other_pct += data['presence_pct']
        
        if other_pct > 0:
            labels.append(f"Others ({other_pct:.1f}%)")
            values.append(other_pct)
            colors.append('#C0C0C0')
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textposition='inside',
            textinfo='label',
            hovertemplate='<b>%{label}</b><br>Matches: %{value:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '🥧 Metagame Distribution - Standard (July 1-21, 2025)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=False,
            width=800,
            height=800,
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="pie-chart")
    
    def generate_2_bar_chart(self, archetype_data: Dict[str, Dict]) -> str:
        """2. Génère le Metagame Bar Chart"""
        # Sort by presence
        sorted_data = sorted(archetype_data.items(), 
                           key=lambda x: x[1]['presence_pct'], 
                           reverse=True)[:15]  # Top 15
        
        archetypes = [a[0] for a in sorted_data]
        percentages = [a[1]['presence_pct'] for a in sorted_data]
        
        # Colors based on archetype
        colors = []
        for archetype in archetypes:
            if 'mono white' in archetype.lower():
                colors.append('#FFD700')
            elif 'domain' in archetype.lower():
                colors.append('#90EE90')
            elif 'esper' in archetype.lower():
                colors.append('#4169E1')
            elif 'boros' in archetype.lower():
                colors.append('#FF6347')
            elif 'izzet' in archetype.lower():
                colors.append('#FF1493')
            elif 'gruul' in archetype.lower():
                colors.append('#FF4500')
            elif 'dimir' in archetype.lower():
                colors.append('#483D8B')
            else:
                colors.append('#808080')
        
        fig = go.Figure(data=[go.Bar(
            x=archetypes,
            y=percentages,
            marker=dict(
                color=colors,
                line=dict(color='black', width=1)
            ),
            text=[f"{p:.1f}%" for p in percentages],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Presence: %{y:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '📊 Metagame Presence - Top 15 Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Archetype',
                tickangle=-45
            ),
            yaxis=dict(
                title='Presence %',
                range=[0, max(percentages) * 1.15]
            ),
            width=1000,
            height=600,
            margin=dict(b=150)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="bar-chart")
    
    def generate_3_winrate_mustache(self, archetype_data: Dict[str, Dict]) -> str:
        """3. Génère le Win Rate avec intervalles de confiance (Mustache Box)"""
        # Filter archetypes with enough data
        filtered_data = [(a, d) for a, d in archetype_data.items() 
                        if d['matches'] >= 20]
        
        # Sort by win rate
        sorted_data = sorted(filtered_data, 
                           key=lambda x: x[1]['win_rate'], 
                           reverse=True)[:20]
        
        archetypes = [a[0] for a in sorted_data]
        win_rates = [a[1]['win_rate'] for a in sorted_data]
        ci_lower = [a[1]['ci_lower'] for a in sorted_data]
        ci_upper = [a[1]['ci_upper'] for a in sorted_data]
        
        # Create figure
        fig = go.Figure()
        
        # Add confidence intervals
        for i, archetype in enumerate(archetypes):
            fig.add_trace(go.Scatter(
                x=[ci_lower[i], ci_upper[i]],
                y=[archetype, archetype],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add win rate points
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
        
        # Add 50% line
        fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '📈 Win Rates with 95% Confidence Intervals',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Win Rate %',
                range=[30, 70]
            ),
            yaxis=dict(
                title='',
                autorange='reversed'
            ),
            width=1000,
            height=800,
            margin=dict(l=200)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="mustache-chart")
    
    def generate_4_winrate_boxplot(self, archetype_data: Dict[str, Dict]) -> str:
        """4. Génère le Win Rate Box Plot"""
        # Create box plot data
        box_data = []
        
        for archetype, data in archetype_data.items():
            if data['matches'] >= 10:  # Minimum matches
                # Simulate individual match results for box plot
                wins = [1] * data['wins'] + [0] * data['losses']
                if wins:  # Only if there's data
                    box_data.append({
                        'archetype': archetype,
                        'win_rate': data['win_rate'],
                        'matches': data['matches'],
                        'values': wins
                    })
        
        # Sort by median win rate
        box_data.sort(key=lambda x: x['win_rate'], reverse=True)
        box_data = box_data[:15]  # Top 15
        
        fig = go.Figure()
        
        for item in box_data:
            fig.add_trace(go.Box(
                y=[v * 100 for v in item['values']],  # Convert to percentage
                name=f"{item['archetype']}<br>({item['matches']} matches)",
                boxpoints='outliers',
                marker_color='lightseagreen' if item['win_rate'] > 50 else 'lightcoral',
                showlegend=False
            ))
        
        # Add 50% line
        fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '📊 Win Rate Distribution by Archetype',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            yaxis=dict(
                title='Win Rate %',
                range=[0, 100]
            ),
            xaxis=dict(
                title='',
                tickangle=-45
            ),
            width=1200,
            height=600,
            margin=dict(b=150)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="boxplot-chart")
    
    def generate_5_tier_scatterplot(self, archetype_data: Dict[str, Dict]) -> str:
        """5. Génère le Tier Scatterplot (score normalisé)"""
        # Calculate normalized score
        for archetype, data in archetype_data.items():
            # Normalized score = (win_rate * presence) / 100
            # Adjusted to give more weight to presence for tier calculation
            presence_weight = min(data['presence_pct'] / 5, 1)  # Cap at 20% = 1
            win_rate_normalized = (data['win_rate'] - 50) / 10  # Normalize around 50%
            
            data['tier_score'] = presence_weight * (1 + win_rate_normalized)
        
        # Sort by tier score
        sorted_data = sorted(archetype_data.items(), 
                           key=lambda x: x[1]['tier_score'], 
                           reverse=True)
        
        # Assign tiers
        tiers = []
        tier_colors = []
        tier_labels = []
        
        for i, (archetype, data) in enumerate(sorted_data):
            if i < 3:
                tier = 'S'
                color = '#FFD700'  # Gold
            elif i < 8:
                tier = 'A'
                color = '#C0C0C0'  # Silver
            elif i < 15:
                tier = 'B'
                color = '#CD7F32'  # Bronze
            else:
                tier = 'C'
                color = '#808080'  # Gray
            
            tiers.append(tier)
            tier_colors.append(color)
            tier_labels.append(f"{archetype}<br>Tier {tier}")
            data['tier'] = tier
        
        # Create scatter plot
        fig = go.Figure()
        
        x_values = list(range(len(sorted_data)))
        y_values = [d[1]['tier_score'] for d in sorted_data]
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers+text',
            marker=dict(
                size=15,
                color=tier_colors,
                line=dict(color='black', width=2)
            ),
            text=tiers,
            textposition='middle center',
            hovertemplate='<b>%{customdata[0]}</b><br>Score: %{y:.2f}<br>Win Rate: %{customdata[1]:.1f}%<br>Presence: %{customdata[2]:.1f}%<extra></extra>',
            customdata=[(d[0], d[1]['win_rate'], d[1]['presence_pct']) for d in sorted_data]
        ))
        
        fig.update_layout(
            title={
                'text': '🏆 Archetype Tier Rankings',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Rank',
                tickmode='array',
                tickvals=x_values[:20],
                ticktext=[d[0] for d in sorted_data[:20]],
                tickangle=-45
            ),
            yaxis=dict(
                title='Normalized Score'
            ),
            width=1200,
            height=700,
            margin=dict(b=150)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="tier-chart")
    
    def generate_6_presence_winrate_scatter(self, archetype_data: Dict[str, Dict]) -> Tuple[str, str]:
        """6. Génère les 2 versions du Winrate & Presence Scatterplot"""
        
        # Prepare data
        plot_data = []
        for archetype, data in archetype_data.items():
            if data['matches'] >= 10:  # Minimum threshold
                plot_data.append({
                    'archetype': archetype,
                    'presence': data['presence_pct'],
                    'win_rate': data['win_rate'],
                    'matches': data['matches'],
                    'tier': data.get('tier', 'C')
                })
        
        # Sort by presence for consistent ordering
        plot_data.sort(key=lambda x: x['presence'], reverse=True)
        
        # Tier colors
        tier_color_map = {
            'S': '#FFD700',
            'A': '#C0C0C0', 
            'B': '#CD7F32',
            'C': '#808080'
        }
        
        colors = [tier_color_map.get(d['tier'], '#808080') for d in plot_data]
        
        # Version 1: Full scatter plot
        fig_full = go.Figure()
        
        fig_full.add_trace(go.Scatter(
            x=[d['presence'] for d in plot_data],
            y=[d['win_rate'] for d in plot_data],
            mode='markers',
            marker=dict(
                size=[math.sqrt(d['matches']) * 2 for d in plot_data],
                color=colors,
                line=dict(color='black', width=1),
                sizemode='diameter',
                sizeref=1
            ),
            text=[d['archetype'] for d in plot_data],
            hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Matches: %{customdata}<extra></extra>',
            customdata=[d['matches'] for d in plot_data]
        ))
        
        # Add reference lines
        fig_full.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.3)
        fig_full.add_vline(x=5, line_dash="dash", line_color="blue", opacity=0.3)
        
        fig_full.update_layout(
            title={
                'text': '🎯 Win Rate vs Presence - Full View',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Presence %', range=[0, max(d['presence'] for d in plot_data) * 1.1]),
            yaxis=dict(title='Win Rate %', range=[30, 70]),
            width=1000,
            height=700
        )
        
        # Version 2: Zoomed with labels
        top_archetypes = [d for d in plot_data if d['presence'] >= 3][:10]
        
        fig_zoom = go.Figure()
        
        fig_zoom.add_trace(go.Scatter(
            x=[d['presence'] for d in top_archetypes],
            y=[d['win_rate'] for d in top_archetypes],
            mode='markers+text',
            marker=dict(
                size=[math.sqrt(d['matches']) * 3 for d in top_archetypes],
                color=[tier_color_map.get(d['tier'], '#808080') for d in top_archetypes],
                line=dict(color='black', width=2),
                sizemode='diameter',
                sizeref=1
            ),
            text=[f"{d['archetype']}<br>Tier {d['tier']}" for d in top_archetypes],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Presence: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Matches: %{customdata}<extra></extra>',
            customdata=[d['matches'] for d in top_archetypes]
        ))
        
        # Add quadrant labels
        fig_zoom.add_annotation(
            text="High WR<br>Low Presence",
            x=2, y=58,
            showarrow=False,
            font=dict(size=12, color="gray"),
            opacity=0.7
        )
        
        fig_zoom.add_annotation(
            text="High WR<br>High Presence",
            x=12, y=58,
            showarrow=False,
            font=dict(size=12, color="gray"),
            opacity=0.7
        )
        
        fig_zoom.add_annotation(
            text="Low WR<br>Low Presence",
            x=2, y=42,
            showarrow=False,
            font=dict(size=12, color="gray"),
            opacity=0.7
        )
        
        fig_zoom.add_annotation(
            text="Low WR<br>High Presence",
            x=12, y=42,
            showarrow=False,
            font=dict(size=12, color="gray"),
            opacity=0.7
        )
        
        # Add reference lines
        fig_zoom.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.3)
        fig_zoom.add_vline(x=5, line_dash="dash", line_color="blue", opacity=0.3)
        
        fig_zoom.update_layout(
            title={
                'text': '🎯 Win Rate vs Presence - Top Archetypes with Tiers',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(title='Presence %', range=[0, 20]),
            yaxis=dict(title='Win Rate %', range=[40, 60]),
            width=1200,
            height=800
        )
        
        return fig_full.to_html(include_plotlyjs='cdn', div_id="scatter-full"), \
               fig_zoom.to_html(include_plotlyjs='cdn', div_id="scatter-zoom")
    
    def generate_bonus_matchup_matrix(self) -> str:
        """Bonus: Génère la matrice de matchups (si données disponibles)"""
        # For now, return a placeholder since we need listener data
        return """
        <div class="info-box">
            <h2>🎲 Matchup Matrix</h2>
            <p>La matrice de matchups nécessite les données du MTGO Listener (Phase 4).</p>
            <p>Une fois le listener implémenté, cette visualisation montrera les taux de victoire entre chaque archétype.</p>
        </div>
        """
    
    def generate_all_visualizations(self):
        """Génère toutes les visualisations et crée le HTML final"""
        print("\n🎨 Génération des visualisations Jiliac...")
        
        # Get data
        archetype_data, total_matches = self.get_july_data()
        
        print(f"✅ Données récupérées: {len(archetype_data)} archétypes, {total_matches} matches")
        
        # Generate each visualization
        viz1 = self.generate_1_pie_chart(archetype_data)
        viz2 = self.generate_2_bar_chart(archetype_data)
        viz3 = self.generate_3_winrate_mustache(archetype_data)
        viz4 = self.generate_4_winrate_boxplot(archetype_data)
        viz5 = self.generate_5_tier_scatterplot(archetype_data)
        viz6_full, viz6_zoom = self.generate_6_presence_winrate_scatter(archetype_data)
        viz_bonus = self.generate_bonus_matchup_matrix()
        
        # Read our reference template
        template_path = Path("data/cache/standard_analysis_no_leagues.html")
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Extract the header style from template
        header_start = template.find('<style>')
        header_end = template.find('</style>') + 8
        header_style = template[header_start:header_end]
        
        # Create final HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Jiliac-Style Analysis (July 1-21, 2025)</title>
    {header_style}
    <style>
        .visualization-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .viz-header {{
            font-size: 1.5em;
            font-weight: 700;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics - Jiliac-Style Analysis</h1>
        <p>Standard Format - July 1-21, 2025</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Based on competitive tournaments only (excluding leagues)</p>
    </div>
    
    <div class="container">
        <!-- Summary Stats -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Matches Analyzed</div>
                <div class="summary-value">{total_matches:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Archetypes</div>
                <div class="summary-value">{len(archetype_data)}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Analysis Period</div>
                <div class="summary-value">21 Days</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Competitive Tournaments</div>
                <div class="summary-value">{len([a for a in archetype_data.values() if a['matches'] > 0])}</div>
            </div>
        </div>
        
        <!-- Visualization 1: Pie Chart -->
        <div class="visualization-container">
            <div class="viz-header">1. Metagame Distribution - Pie Chart</div>
            {viz1}
        </div>
        
        <!-- Visualization 2: Bar Chart -->
        <div class="visualization-container">
            <div class="viz-header">2. Metagame Presence - Bar Chart</div>
            {viz2}
        </div>
        
        <!-- Visualization 3: Win Rate Mustache -->
        <div class="visualization-container">
            <div class="viz-header">3. Win Rates with Confidence Intervals</div>
            {viz3}
        </div>
        
        <!-- Visualization 4: Box Plot -->
        <div class="visualization-container">
            <div class="viz-header">4. Win Rate Distribution Box Plot</div>
            {viz4}
        </div>
        
        <!-- Visualization 5: Tier Scatter -->
        <div class="visualization-container">
            <div class="viz-header">5. Tier Rankings by Normalized Score</div>
            {viz5}
        </div>
        
        <!-- Visualization 6a: Full Scatter -->
        <div class="visualization-container">
            <div class="viz-header">6a. Win Rate vs Presence - Full View</div>
            {viz6_full}
        </div>
        
        <!-- Visualization 6b: Zoom Scatter -->
        <div class="visualization-container">
            <div class="viz-header">6b. Win Rate vs Presence - Top Archetypes</div>
            {viz6_zoom}
        </div>
        
        <!-- Bonus: Matchup Matrix -->
        <div class="visualization-container">
            <div class="viz-header">Bonus: Matchup Matrix</div>
            {viz_bonus}
        </div>
        
        <!-- Methodology -->
        <div class="info-box">
            <h2>📊 Methodology</h2>
            <ul>
                <li><strong>Period:</strong> July 1-21, 2025 (21 days)</li>
                <li><strong>Analysis Method:</strong> By MATCHES played (not by deck count)</li>
                <li><strong>Exclusions:</strong> Leagues, casual events, non-competitive tournaments</li>
                <li><strong>Confidence Intervals:</strong> 95% Wilson score intervals</li>
                <li><strong>Tier Calculation:</strong> Normalized score based on presence and win rate</li>
            </ul>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin: 40px 0; color: #666;">
            <p>Generated by Manalytics - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Based on Jiliac's R-Meta-Analysis visualization framework</p>
        </div>
    </div>
</body>
</html>"""
        
        # Save the file
        output_path = Path("data/cache/jiliac_analysis_july_1_21.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Visualisations générées avec succès!")
        print(f"📄 Fichier sauvegardé: {output_path}")
        
        return output_path


if __name__ == "__main__":
    visualizer = JiliacVisualizer()
    output_file = visualizer.generate_all_visualizations()
    
    print(f"\n🎉 Analyse complète terminée!")
    print(f"🌐 Ouvrez le fichier dans votre navigateur:")
    print(f"   file://{output_file.absolute()}")