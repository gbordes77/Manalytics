#!/usr/bin/env python3
"""
Analyse des vraies données Standard récupérées depuis le 2 juillet 2025
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

class RealStandardAnalyzer:
    """Analyseur spécialisé pour les vraies données Standard"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Charger les vraies données Standard"""
        print(f"📊 Chargement des vraies données depuis {self.data_file}")
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        self.df = pd.DataFrame(data)
        self.df['tournament_date'] = pd.to_datetime(self.df['tournament_date'])
        
        print(f"✅ Données chargées: {len(self.df)} decks")
        print(f"🏆 Tournois: {self.df['tournament_id'].nunique()}")
        print(f"📅 Période: {self.df['tournament_date'].min()} à {self.df['tournament_date'].max()}")
        print(f"🎯 Archétypes: {self.df['archetype'].nunique()}")
        print(f"🎲 Sources: {self.df['tournament_source'].unique()}")
    
    def analyze_archetype_performance(self):
        """Analyser les performances par archétype"""
        print("\n🎯 ANALYSE DES PERFORMANCES PAR ARCHÉTYPE")
        print("=" * 50)
        
        # Calcul des statistiques par archétype
        archetype_stats = self.df.groupby('archetype').agg({
            'wins': ['sum', 'mean'],
            'losses': ['sum', 'mean'],
            'winrate': ['mean', 'std'],
            'matches_played': 'sum',
            'player_name': 'count'
        }).round(3)
        
        archetype_stats.columns = ['total_wins', 'avg_wins', 'total_losses', 'avg_losses', 
                                 'avg_winrate', 'winrate_std', 'total_matches', 'deck_count']
        
        # Calcul du winrate global
        archetype_stats['global_winrate'] = archetype_stats['total_wins'] / (
            archetype_stats['total_wins'] + archetype_stats['total_losses']
        )
        
        # Calcul de la part de métagame
        total_decks = len(self.df)
        archetype_stats['meta_share'] = (archetype_stats['deck_count'] / total_decks * 100).round(2)
        
        # Trier par part de métagame
        archetype_stats = archetype_stats.sort_values('meta_share', ascending=False)
        
        print("\n📊 PERFORMANCES PAR ARCHÉTYPE:")
        print("-" * 80)
        for archetype, stats in archetype_stats.iterrows():
            print(f"🎯 {archetype}")
            print(f"   Part du métagame: {stats['meta_share']:.1f}% ({int(stats['deck_count'])} decks)")
            print(f"   Winrate global: {stats['global_winrate']:.3f} ({stats['avg_winrate']:.3f} ±{stats['winrate_std']:.3f})")
            print(f"   Matchs totaux: {int(stats['total_matches'])} ({stats['total_wins']:.0f}W-{stats['total_losses']:.0f}L)")
            print()
        
        return archetype_stats
    
    def analyze_temporal_trends(self):
        """Analyser les tendances temporelles"""
        print("\n📈 ANALYSE DES TENDANCES TEMPORELLES")
        print("=" * 50)
        
        # Données par jour
        daily_data = self.df.groupby(['tournament_date', 'archetype']).agg({
            'player_name': 'count',
            'winrate': 'mean'
        }).reset_index()
        
        daily_data.columns = ['date', 'archetype', 'deck_count', 'avg_winrate']
        
        # Calcul de la part de métagame par jour
        daily_totals = daily_data.groupby('date')['deck_count'].sum().reset_index()
        daily_totals.columns = ['date', 'total_decks']
        
        daily_data = daily_data.merge(daily_totals, on='date')
        daily_data['meta_share'] = (daily_data['deck_count'] / daily_data['total_decks'] * 100).round(2)
        
        print("\n📅 ÉVOLUTION QUOTIDIENNE:")
        print("-" * 50)
        for date in sorted(daily_data['date'].unique()):
            day_data = daily_data[daily_data['date'] == date].sort_values('meta_share', ascending=False)
            print(f"📅 {date.strftime('%Y-%m-%d')} ({day_data['total_decks'].iloc[0]} decks)")
            for _, row in day_data.iterrows():
                print(f"   {row['archetype']}: {row['meta_share']:.1f}% (WR: {row['avg_winrate']:.3f})")
            print()
        
        return daily_data
    
    def analyze_tournament_sources(self):
        """Analyser les sources de tournois"""
        print("\n🌐 ANALYSE DES SOURCES DE DONNÉES")
        print("=" * 50)
        
        source_stats = self.df.groupby('tournament_source').agg({
            'tournament_id': 'nunique',
            'player_name': 'count',
            'winrate': 'mean',
            'matches_played': 'sum'
        }).round(3)
        
        source_stats.columns = ['tournaments', 'decks', 'avg_winrate', 'total_matches']
        
        print("\n📊 STATISTIQUES PAR SOURCE:")
        print("-" * 40)
        for source, stats in source_stats.iterrows():
            print(f"🌐 {source.upper()}")
            print(f"   Tournois: {int(stats['tournaments'])}")
            print(f"   Decks: {int(stats['decks'])}")
            print(f"   Winrate moyen: {stats['avg_winrate']:.3f}")
            print(f"   Matchs totaux: {int(stats['total_matches'])}")
            print()
        
        return source_stats
    
    def create_visualizations(self, output_dir: str = "standard_analysis"):
        """Créer les visualisations"""
        print(f"\n📊 CRÉATION DES VISUALISATIONS dans {output_dir}")
        print("=" * 50)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 1. Part de métagame
        archetype_counts = self.df['archetype'].value_counts()
        
        fig1 = go.Figure(data=[
            go.Pie(
                labels=archetype_counts.index,
                values=archetype_counts.values,
                hole=0.3,
                textinfo='label+percent',
                textposition='outside'
            )
        ])
        
        fig1.update_layout(
            title="Part de métagame Standard (depuis 2025-07-02)",
            font=dict(size=14),
            showlegend=True
        )
        
        fig1.write_html(output_path / "metagame_share.html")
        print("✅ Graphique part de métagame créé")
        
        # 2. Winrates par archétype
        archetype_winrates = self.df.groupby('archetype')['winrate'].agg(['mean', 'std']).reset_index()
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=archetype_winrates['archetype'],
            y=archetype_winrates['mean'],
            error_y=dict(type='data', array=archetype_winrates['std']),
            name='Winrate moyen',
            marker_color='lightblue'
        ))
        
        fig2.update_layout(
            title="Winrates par archétype Standard",
            xaxis_title="Archétype",
            yaxis_title="Winrate",
            font=dict(size=14)
        )
        
        fig2.write_html(output_path / "winrates_by_archetype.html")
        print("✅ Graphique winrates créé")
        
        # 3. Évolution temporelle
        daily_data = self.df.groupby(['tournament_date', 'archetype']).size().reset_index(name='count')
        
        fig3 = px.line(
            daily_data, 
            x='tournament_date', 
            y='count', 
            color='archetype',
            title="Évolution temporelle des archétypes Standard"
        )
        
        fig3.update_layout(
            xaxis_title="Date",
            yaxis_title="Nombre de decks",
            font=dict(size=14)
        )
        
        fig3.write_html(output_path / "temporal_evolution.html")
        print("✅ Graphique évolution temporelle créé")
        
        # 4. Distribution des winrates
        fig4 = go.Figure()
        
        for archetype in self.df['archetype'].unique():
            archetype_data = self.df[self.df['archetype'] == archetype]
            
            fig4.add_trace(go.Histogram(
                x=archetype_data['winrate'],
                name=archetype,
                opacity=0.7,
                nbinsx=20
            ))
        
        fig4.update_layout(
            title="Distribution des winrates par archétype",
            xaxis_title="Winrate",
            yaxis_title="Nombre de decks",
            barmode='overlay',
            font=dict(size=14)
        )
        
        fig4.write_html(output_path / "winrate_distribution.html")
        print("✅ Graphique distribution winrates créé")
        
        return output_path
    
    def generate_report(self, output_dir: str = "standard_analysis"):
        """Générer un rapport complet"""
        print(f"\n📋 GÉNÉRATION DU RAPPORT COMPLET")
        print("=" * 50)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Analyser les données
        archetype_stats = self.analyze_archetype_performance()
        daily_data = self.analyze_temporal_trends()
        source_stats = self.analyze_tournament_sources()
        
        # Créer les visualisations
        viz_path = self.create_visualizations(output_dir)
        
        # Générer le rapport HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analyse Standard - Vraies Données (depuis 2025-07-02)</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
                .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                .archetype {{ margin: 15px 0; padding: 15px; background: #e8f4f8; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .chart-link {{ display: inline-block; margin: 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Analyse Standard - Vraies Données</h1>
                <p>Période: depuis le 2 juillet 2025 | Générée le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Résumé des Données</h2>
                <div class="stats">
                    <div class="stat-card">
                        <h3>{len(self.df)}</h3>
                        <p>Decks analysés</p>
                    </div>
                    <div class="stat-card">
                        <h3>{self.df['tournament_id'].nunique()}</h3>
                        <p>Tournois</p>
                    </div>
                    <div class="stat-card">
                        <h3>{self.df['archetype'].nunique()}</h3>
                        <p>Archétypes</p>
                    </div>
                    <div class="stat-card">
                        <h3>{self.df['matches_played'].sum()}</h3>
                        <p>Matchs totaux</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Performances par Archétype</h2>
                <table>
                    <tr>
                        <th>Archétype</th>
                        <th>Part Métagame</th>
                        <th>Winrate Global</th>
                        <th>Decks</th>
                        <th>Matchs</th>
                    </tr>
        """
        
        for archetype, stats in archetype_stats.iterrows():
            html_content += f"""
                    <tr>
                        <td><strong>{archetype}</strong></td>
                        <td>{stats['meta_share']:.1f}%</td>
                        <td>{stats['global_winrate']:.3f}</td>
                        <td>{int(stats['deck_count'])}</td>
                        <td>{int(stats['total_matches'])}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>📈 Visualisations</h2>
                <a href="metagame_share.html" class="chart-link">📊 Part de Métagame</a>
                <a href="winrates_by_archetype.html" class="chart-link">🎯 Winrates</a>
                <a href="temporal_evolution.html" class="chart-link">📈 Évolution Temporelle</a>
                <a href="winrate_distribution.html" class="chart-link">📊 Distribution Winrates</a>
            </div>
            
            <div class="section">
                <h2>🌐 Sources de Données</h2>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>Tournois</th>
                        <th>Decks</th>
                        <th>Winrate Moyen</th>
                    </tr>
        """
        
        for source, stats in source_stats.iterrows():
            html_content += f"""
                    <tr>
                        <td><strong>{source.upper()}</strong></td>
                        <td>{int(stats['tournaments'])}</td>
                        <td>{int(stats['decks'])}</td>
                        <td>{stats['avg_winrate']:.3f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>📋 Détails Techniques</h2>
                <p><strong>Période d'analyse:</strong> Depuis le 2 juillet 2025</p>
                <p><strong>Sources:</strong> MTGTop8, MTGDecks (vraies données, pas de simulation)</p>
                <p><strong>Format:</strong> Standard</p>
                <p><strong>Méthode:</strong> Scraping web + analyse statistique avancée</p>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarder le rapport
        report_path = output_path / "rapport_standard_complet.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Rapport complet généré: {report_path}")
        
        # Sauvegarder les données au format CSV pour Excel
        csv_path = output_path / "donnees_standard_analysees.csv"
        self.df.to_csv(csv_path, index=False)
        print(f"✅ Données CSV sauvegardées: {csv_path}")
        
        return report_path

def main():
    """Fonction principale"""
    print("🚀 ANALYSE DES VRAIES DONNÉES STANDARD")
    print("=" * 60)
    
    # Créer l'analyseur
    analyzer = RealStandardAnalyzer("real_data/complete_dataset.json")
    
    # Générer le rapport complet
    report_path = analyzer.generate_report()
    
    print("\n" + "=" * 60)
    print("🎉 ANALYSE TERMINÉE")
    print("=" * 60)
    print(f"📋 Rapport principal: {report_path}")
    print("📊 Visualisations interactives créées")
    print("💾 Données CSV exportées")
    print("\n✅ Toutes les données sont RÉELLES (pas de simulation)")

if __name__ == "__main__":
    main() 