"""
Dashboard Generator module for Manalytics
Génère des tableaux de bord et visualisations pour le métagame
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class DashboardGenerator:
    """Générateur de tableaux de bord pour le métagame"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialise le générateur de dashboard
        
        Args:
            output_dir: Répertoire de sortie (optionnel)
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_metagame_pie_chart(self, metagame_data: Dict) -> go.Figure:
        """
        Génère un graphique en secteurs de la répartition du métagame
        
        Args:
            metagame_data: Données de répartition du métagame
            
        Returns:
            Figure Plotly
        """
        labels = list(metagame_data.keys())
        values = [data['percentage'] for data in metagame_data.values()]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            textposition='auto',
            hole=0.3
        )])
        
        fig.update_layout(
            title="Répartition du Métagame",
            font=dict(size=12),
            showlegend=True
        )
        
        return fig
    
    def generate_winrate_bar_chart(self, winrate_data: Dict) -> go.Figure:
        """
        Génère un graphique en barres des taux de victoire
        
        Args:
            winrate_data: Données des taux de victoire
            
        Returns:
            Figure Plotly
        """
        archetypes = list(winrate_data.keys())
        winrates = [data['win_rate'] * 100 for data in winrate_data.values()]
        
        fig = go.Figure(data=[go.Bar(
            x=archetypes,
            y=winrates,
            text=[f"{wr:.1f}%" for wr in winrates],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Taux de Victoire par Archétype",
            xaxis_title="Archétype",
            yaxis_title="Taux de Victoire (%)",
            xaxis_tickangle=-45
        )
        
        return fig
    
    def generate_temporal_evolution(self, temporal_data: List[Dict]) -> go.Figure:
        """
        Génère un graphique d'évolution temporelle
        
        Args:
            temporal_data: Données temporelles
            
        Returns:
            Figure Plotly
        """
        fig = go.Figure()
        
        # Grouper par archétype
        archetypes = {}
        for entry in temporal_data:
            archetype = entry.get('archetype', 'Unknown')
            date = entry.get('date', datetime.now().isoformat())
            
            if archetype not in archetypes:
                archetypes[archetype] = {'dates': [], 'counts': []}
            
            archetypes[archetype]['dates'].append(date)
            archetypes[archetype]['counts'].append(entry.get('count', 1))
        
        # Ajouter les traces
        for archetype, data in archetypes.items():
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['counts'],
                mode='lines+markers',
                name=archetype,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Évolution Temporelle des Archétypes",
            xaxis_title="Date",
            yaxis_title="Nombre de Decks",
            hovermode='x unified'
        )
        
        return fig
    
    def generate_tier_distribution(self, metagame_data: Dict) -> go.Figure:
        """
        Génère un graphique de distribution par tier
        
        Args:
            metagame_data: Données du métagame
            
        Returns:
            Figure Plotly
        """
        tier_counts = {}
        for archetype, data in metagame_data.items():
            tier = data.get('tier', 'Tier 4')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        tiers = list(tier_counts.keys())
        counts = list(tier_counts.values())
        
        fig = go.Figure(data=[go.Bar(
            x=tiers,
            y=counts,
            text=counts,
            textposition='auto',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )])
        
        fig.update_layout(
            title="Distribution des Archétypes par Tier",
            xaxis_title="Tier",
            yaxis_title="Nombre d'Archétypes"
        )
        
        return fig
    
    def generate_comprehensive_dashboard(self, analysis_data: Dict) -> str:
        """
        Génère un dashboard complet avec tous les graphiques
        
        Args:
            analysis_data: Données d'analyse complètes
            
        Returns:
            Chemin du fichier HTML généré
        """
        # Créer les sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Répartition du Métagame', 'Taux de Victoire', 
                          'Distribution par Tier', 'Évolution Temporelle'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        metagame_share = analysis_data.get('metagame_share', {})
        win_rates = analysis_data.get('win_rates', {})
        
        # Graphique en secteurs
        if metagame_share:
            labels = list(metagame_share.keys())
            values = [data['percentage'] for data in metagame_share.values()]
            
            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                name="Métagame"
            ), row=1, col=1)
        
        # Graphique des taux de victoire
        if win_rates:
            archetypes = list(win_rates.keys())
            winrates = [data['win_rate'] * 100 for data in win_rates.values()]
            
            fig.add_trace(go.Bar(
                x=archetypes,
                y=winrates,
                name="Taux de Victoire"
            ), row=1, col=2)
        
        # Distribution par tier
        if metagame_share:
            tier_counts = {}
            for data in metagame_share.values():
                tier = data.get('tier', 'Tier 4')
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            fig.add_trace(go.Bar(
                x=list(tier_counts.keys()),
                y=list(tier_counts.values()),
                name="Distribution Tier"
            ), row=2, col=1)
        
        # Évolution temporelle (exemple)
        fig.add_trace(go.Scatter(
            x=['2025-01-01', '2025-01-15', '2025-01-30'],
            y=[10, 15, 20],
            mode='lines+markers',
            name="Évolution"
        ), row=2, col=2)
        
        fig.update_layout(
            height=800,
            title_text="Dashboard Métagame Complet",
            showlegend=False
        )
        
        # Sauvegarder
        output_path = self.output_dir / "dashboard_complet.html"
        fig.write_html(str(output_path))
        
        return str(output_path)
    
    def generate_summary_html(self, analysis_data: Dict) -> str:
        """
        Génère un résumé HTML des analyses
        
        Args:
            analysis_data: Données d'analyse
            
        Returns:
            Chemin du fichier HTML généré
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rapport Métagame - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #4ECDC4; color: white; padding: 20px; border-radius: 10px; }}
                .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .archetype {{ background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Rapport Métagame</h1>
                <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
            
            <div class="metric">
                <h2>📈 Métriques Générales</h2>
                <p><strong>Total decks analysés:</strong> {analysis_data.get('total_decks_analyzed', 0)}</p>
                <p><strong>Nombre d'archétypes:</strong> {analysis_data.get('diversity_metrics', {}).get('archetype_count', 0)}</p>
                <p><strong>Indice de diversité:</strong> {analysis_data.get('diversity_metrics', {}).get('diversity_index', 0)}</p>
            </div>
            
            <div class="metric">
                <h2>🏆 Top Archétypes</h2>
        """
        
        top_archetypes = analysis_data.get('top_archetypes', [])
        for archetype in top_archetypes:
            html_content += f"""
                <div class="archetype">
                    <strong>{archetype['archetype']}</strong> - {archetype['percentage']}% ({archetype['tier']})
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        output_path = self.output_dir / "rapport_resume.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def export_json_report(self, analysis_data: Dict) -> str:
        """
        Exporte le rapport en format JSON
        
        Args:
            analysis_data: Données d'analyse
            
        Returns:
            Chemin du fichier JSON généré
        """
        output_path = self.output_dir / "rapport_complet.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(output_path) 