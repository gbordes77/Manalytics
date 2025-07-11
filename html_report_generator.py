#!/usr/bin/env python3
"""
HTML Report Generator - Générateur de rapports HTML sophistiqués
Créé des rapports complets avec graphiques interactifs et design moderne
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from jinja2 import Template
import base64
import io

class HTMLReportGenerator:
    """
    Générateur de rapports HTML sophistiqués
    
    Fonctionnalités:
    - Rapports HTML complets avec CSS moderne
    - Graphiques interactifs Plotly
    - Tableaux de données avec tri et filtrage
    - Export PDF
    - Design responsive
    - Thèmes personnalisables
    """
    
    def __init__(self, theme: str = "modern"):
        self.theme = theme
        self.colors = self._get_theme_colors()
        
        # Templates HTML
        self.templates = {
            'base': self._get_base_template(),
            'section': self._get_section_template(),
            'table': self._get_table_template(),
            'chart': self._get_chart_template()
        }
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """Obtenir les couleurs du thème"""
        themes = {
            'modern': {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'accent': '#e74c3c',
                'background': '#ecf0f1',
                'surface': '#ffffff',
                'text': '#2c3e50',
                'text_light': '#7f8c8d',
                'success': '#27ae60',
                'warning': '#f39c12',
                'error': '#e74c3c'
            },
            'dark': {
                'primary': '#1a1a1a',
                'secondary': '#4a90e2',
                'accent': '#ff6b6b',
                'background': '#121212',
                'surface': '#1e1e1e',
                'text': '#ffffff',
                'text_light': '#b0b0b0',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336'
            },
            'mtg': {
                'primary': '#0d1b2a',
                'secondary': '#415a77',
                'accent': '#e9c46a',
                'background': '#f1faee',
                'surface': '#ffffff',
                'text': '#0d1b2a',
                'text_light': '#457b9d',
                'success': '#2a9d8f',
                'warning': '#f4a261',
                'error': '#e76f51'
            }
        }
        return themes.get(self.theme, themes['modern'])
    
    def _get_base_template(self) -> str:
        """Template HTML de base"""
        return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: {{ colors.background }};
            color: {{ colors.text }};
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, {{ colors.primary }}, {{ colors.secondary }});
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: {{ colors.surface }};
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .icon {
            font-size: 2.5em;
            color: {{ colors.secondary }};
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: {{ colors.primary }};
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            color: {{ colors.text_light }};
            font-size: 0.9em;
        }
        
        .section {
            background: {{ colors.surface }};
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: {{ colors.primary }};
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: 500;
        }
        
        .section-content {
            padding: 25px;
        }
        
        .chart-container {
            margin: 20px 0;
            min-height: 400px;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: {{ colors.surface }};
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: {{ colors.primary }};
            color: white;
            font-weight: 500;
            position: sticky;
            top: 0;
        }
        
        tr:hover {
            background: {{ colors.background }};
        }
        
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .badge-tier1 { background: {{ colors.success }}; color: white; }
        .badge-tier2 { background: {{ colors.warning }}; color: white; }
        .badge-tier3 { background: {{ colors.error }}; color: white; }
        .badge-tier4 { background: {{ colors.text_light }}; color: white; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: {{ colors.secondary }};
            transition: width 0.3s ease;
        }
        
        .insights {
            background: linear-gradient(135deg, {{ colors.accent }}, {{ colors.warning }});
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .insights h3 {
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .insights ul {
            list-style: none;
        }
        
        .insights li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .insights li::before {
            content: "✓";
            position: absolute;
            left: 0;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: {{ colors.text_light }};
            border-top: 1px solid #ddd;
            margin-top: 50px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> {{ title }}</h1>
            <p>{{ subtitle }}</p>
        </div>
        
        {{ content }}
        
        <div class="footer">
            <p>Rapport généré le {{ generation_date }} par Manalytics Advanced Analyzer</p>
            <p><i class="fas fa-magic"></i> Analyse de métagame MTG - Version Python du projet R-Meta-Analysis</p>
        </div>
    </div>
    
    <script>
        // Animation des cartes de stats
        document.addEventListener('DOMContentLoaded', function() {
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                }, index * 100);
            });
        });
    </script>
</body>
</html>
        """
    
    def _get_section_template(self) -> str:
        """Template pour une section"""
        return """
        <div class="section">
            <div class="section-header">
                <i class="{{ icon }}"></i> {{ title }}
            </div>
            <div class="section-content">
                {{ content }}
            </div>
        </div>
        """
    
    def _get_table_template(self) -> str:
        """Template pour un tableau"""
        return """
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        {% for header in headers %}
                        <th>{{ header }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        {% for cell in row %}
                        <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        """
    
    def _get_chart_template(self) -> str:
        """Template pour un graphique"""
        return """
        <div class="chart-container">
            <div id="{{ chart_id }}"></div>
        </div>
        <script>
            {{ chart_script }}
        </script>
        """
    
    def create_plotly_chart(self, data: Dict, chart_type: str, chart_id: str) -> str:
        """Créer un graphique Plotly"""
        
        if chart_type == 'meta_share_bar':
            fig = go.Figure(data=[
                go.Bar(
                    x=data['archetypes'],
                    y=data['meta_shares'],
                    marker_color=self.colors['secondary'],
                    text=[f"{x:.1%}" for x in data['meta_shares']],
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title="Parts de Marché par Archétype",
                xaxis_title="Archétype",
                yaxis_title="Part de Marché",
                template="plotly_white"
            )
            
        elif chart_type == 'winrate_scatter':
            fig = go.Figure(data=[
                go.Scatter(
                    x=data['meta_shares'],
                    y=data['winrates'],
                    mode='markers',
                    marker=dict(
                        size=data['deck_counts'],
                        sizemode='diameter',
                        sizeref=max(data['deck_counts'])/50,
                        color=self.colors['accent'],
                        opacity=0.7
                    ),
                    text=data['archetypes'],
                    textposition='top center'
                )
            ])
            fig.update_layout(
                title="Meta Share vs Winrate",
                xaxis_title="Meta Share",
                yaxis_title="Winrate",
                template="plotly_white"
            )
            
        elif chart_type == 'matchup_heatmap':
            fig = go.Figure(data=[
                go.Heatmap(
                    z=data['matrix'],
                    x=data['archetypes'],
                    y=data['archetypes'],
                    colorscale='RdYlBu_r',
                    zmid=0.5,
                    text=[[f"{val:.1%}" for val in row] for row in data['matrix']],
                    texttemplate="%{text}",
                    textfont={"size": 10}
                )
            ])
            fig.update_layout(
                title="Matrice de Matchups",
                template="plotly_white"
            )
            
        elif chart_type == 'temporal_trends':
            fig = go.Figure()
            for i, archetype in enumerate(data['archetypes']):
                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['trends'][i],
                    mode='lines+markers',
                    name=archetype,
                    line=dict(width=2)
                ))
            fig.update_layout(
                title="Évolution Temporelle des Parts de Marché",
                xaxis_title="Date",
                yaxis_title="Part de Marché",
                template="plotly_white"
            )
        
        # Convertir en HTML
        chart_html = fig.to_html(include_plotlyjs=False, div_id=chart_id)
        return chart_html
    
    def format_table_data(self, df: pd.DataFrame, format_rules: Dict = None) -> Dict:
        """Formater les données de tableau"""
        if format_rules is None:
            format_rules = {}
        
        headers = df.columns.tolist()
        rows = []
        
        for _, row in df.iterrows():
            formatted_row = []
            for col in headers:
                value = row[col]
                
                # Appliquer les règles de formatage
                if col in format_rules:
                    rule = format_rules[col]
                    if rule == 'percentage':
                        value = f"{value:.1%}"
                    elif rule == 'integer':
                        value = f"{int(value)}"
                    elif rule == 'float':
                        value = f"{value:.2f}"
                    elif rule == 'badge_tier':
                        badge_class = f"badge-{value.lower().replace(' ', '')}"
                        value = f'<span class="badge {badge_class}">{value}</span>'
                
                formatted_row.append(value)
            rows.append(formatted_row)
        
        return {'headers': headers, 'rows': rows}
    
    def generate_insights(self, data: Dict) -> List[str]:
        """Générer des insights automatiques"""
        insights = []
        
        # Analyse des performances
        if 'archetype_performance' in data:
            perf = data['archetype_performance']
            
            # Archétype dominant
            dominant = max(perf.keys(), key=lambda x: perf[x]['meta_share'])
            insights.append(f"**{dominant}** domine le métagame avec {perf[dominant]['meta_share']:.1%} de parts de marché")
            
            # Meilleur winrate
            best_wr = max(perf.keys(), key=lambda x: perf[x]['overall_winrate'])
            insights.append(f"**{best_wr}** affiche le meilleur winrate ({perf[best_wr]['overall_winrate']:.1%})")
            
            # Diversité
            num_viable = sum(1 for arch, stats in perf.items() if stats['meta_share'] > 0.05)
            insights.append(f"**{num_viable}** archétypes viables (>5% de parts de marché)")
        
        # Analyse des tendances
        if 'temporal_trends' in data:
            trends = data['temporal_trends']['summary']
            
            # Archétypes émergents
            emerging = [arch for arch, stats in trends.items() if stats.get('trend_category') == 'Émergent']
            if emerging:
                insights.append(f"Archétypes émergents: **{', '.join(emerging)}**")
            
            # Archétypes déclinants
            declining = [arch for arch, stats in trends.items() if stats.get('trend_category') == 'Déclinant']
            if declining:
                insights.append(f"Archétypes en déclin: **{', '.join(declining)}**")
        
        # Analyse statistique
        if 'statistical_analysis' in data:
            stats = data['statistical_analysis']
            diversity = stats['diversity_metrics']['shannon_diversity']
            insights.append(f"Indice de diversité Shannon: **{diversity:.2f}** (plus élevé = plus diversifié)")
        
        return insights
    
    def generate_comprehensive_report(self, data_path: str, output_path: str) -> str:
        """Générer un rapport HTML complet"""
        print("📋 Génération du rapport HTML complet")
        
        # Charger les données
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Préparer les données pour les graphiques
        archetype_perf = data['archetype_performance']
        archetypes = list(archetype_perf.keys())
        meta_shares = [archetype_perf[arch]['meta_share'] for arch in archetypes]
        winrates = [archetype_perf[arch]['overall_winrate'] for arch in archetypes]
        deck_counts = [archetype_perf[arch]['deck_count'] for arch in archetypes]
        
        # Créer les graphiques
        charts = []
        
        # 1. Graphique des parts de marché
        meta_chart_data = {
            'archetypes': archetypes[:10],  # Top 10
            'meta_shares': meta_shares[:10],
            'winrates': winrates[:10],
            'deck_counts': deck_counts[:10]
        }
        charts.append(self.create_plotly_chart(meta_chart_data, 'meta_share_bar', 'meta_share_chart'))
        
        # 2. Scatter plot meta share vs winrate
        scatter_data = {
            'archetypes': archetypes,
            'meta_shares': meta_shares,
            'winrates': winrates,
            'deck_counts': deck_counts
        }
        charts.append(self.create_plotly_chart(scatter_data, 'winrate_scatter', 'winrate_scatter_chart'))
        
        # 3. Matrice de matchups (si disponible)
        if 'matchup_matrix' in data and data['matchup_matrix']['matrix']:
            matrix_data = data['matchup_matrix']['matrix']
            matchup_archetypes = list(matrix_data.keys())
            matrix_values = [[matrix_data[arch_a][arch_b] for arch_b in matchup_archetypes] 
                           for arch_a in matchup_archetypes]
            
            heatmap_data = {
                'archetypes': matchup_archetypes,
                'matrix': matrix_values
            }
            charts.append(self.create_plotly_chart(heatmap_data, 'matchup_heatmap', 'matchup_heatmap_chart'))
        
        # Créer les tableaux
        tables = []
        
        # Tableau des performances
        perf_df = pd.DataFrame(archetype_perf).T
        perf_df = perf_df.sort_values('meta_share', ascending=False)
        
        format_rules = {
            'meta_share': 'percentage',
            'overall_winrate': 'percentage',
            'deck_count': 'integer',
            'tier': 'badge_tier'
        }
        
        perf_table = self.format_table_data(perf_df[['meta_share', 'overall_winrate', 'deck_count', 'tier']], format_rules)
        tables.append(('Performance par Archétype', perf_table))
        
        # Générer les insights
        insights = self.generate_insights(data)
        
        # Préparer les statistiques globales
        metadata = data['metadata']
        stats_cards = [
            {'icon': 'fas fa-trophy', 'value': metadata['total_tournaments'], 'label': 'Tournois Analysés'},
            {'icon': 'fas fa-users', 'value': metadata['total_decks'], 'label': 'Decks Analysés'},
            {'icon': 'fas fa-layer-group', 'value': len(archetypes), 'label': 'Archétypes Identifiés'},
            {'icon': 'fas fa-calendar', 'value': len(metadata['formats']), 'label': 'Formats Couverts'}
        ]
        
        # Construire le contenu HTML
        content_sections = []
        
        # Section statistiques
        stats_html = '<div class="stats-grid">'
        for stat in stats_cards:
            stats_html += f'''
            <div class="stat-card">
                <div class="icon"><i class="{stat['icon']}"></i></div>
                <div class="value">{stat['value']}</div>
                <div class="label">{stat['label']}</div>
            </div>
            '''
        stats_html += '</div>'
        content_sections.append(stats_html)
        
        # Section insights
        insights_html = '''
        <div class="insights">
            <h3><i class="fas fa-lightbulb"></i> Insights Clés</h3>
            <ul>
        '''
        for insight in insights:
            insights_html += f'<li>{insight}</li>'
        insights_html += '</ul></div>'
        content_sections.append(insights_html)
        
        # Sections graphiques
        chart_titles = [
            'Parts de Marché par Archétype',
            'Relation Meta Share - Winrate',
            'Matrice de Matchups'
        ]
        
        for i, chart in enumerate(charts):
            if i < len(chart_titles):
                section_html = f'''
                <div class="section">
                    <div class="section-header">
                        <i class="fas fa-chart-bar"></i> {chart_titles[i]}
                    </div>
                    <div class="section-content">
                        {chart}
                    </div>
                </div>
                '''
                content_sections.append(section_html)
        
        # Sections tableaux
        for title, table_data in tables:
            table_html = f'''
            <div class="section">
                <div class="section-header">
                    <i class="fas fa-table"></i> {title}
                </div>
                <div class="section-content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    {"".join(f"<th>{header}</th>" for header in table_data['headers'])}
                                </tr>
                            </thead>
                            <tbody>
                                {"".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in table_data['rows'])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            '''
            content_sections.append(table_html)
        
        # Assembler le rapport final
        template = Template(self.templates['base'])
        
        html_content = template.render(
            title="Rapport d'Analyse de Métagame",
            subtitle=f"Analyse complète - {', '.join(metadata['formats'])}",
            colors=self.colors,
            content='\n'.join(content_sections),
            generation_date=datetime.now().strftime('%d/%m/%Y à %H:%M')
        )
        
        # Sauvegarder
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Rapport HTML généré: {output_path}")
        return str(output_path)

def main():
    """Fonction principale pour génération de rapport"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HTML Report Generator - Générateur de rapports HTML')
    parser.add_argument('--data', type=str, required=True, help='Fichier JSON de données d\'analyse')
    parser.add_argument('--output', type=str, default='report.html', help='Fichier de sortie HTML')
    parser.add_argument('--theme', type=str, default='modern', choices=['modern', 'dark', 'mtg'], help='Thème du rapport')
    
    args = parser.parse_args()
    
    # Créer le générateur
    generator = HTMLReportGenerator(theme=args.theme)
    
    # Générer le rapport
    report_path = generator.generate_comprehensive_report(args.data, args.output)
    
    print(f"\n✅ Rapport généré avec succès!")
    print(f"📁 Fichier: {report_path}")
    print(f"🌐 Ouvrez le fichier dans votre navigateur pour voir le rapport")

if __name__ == "__main__":
    main() 