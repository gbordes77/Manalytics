#!/usr/bin/env python3
"""
Générateur de graphiques pour métagame MTG
Génère des graphiques pour un format donné depuis une date spécifique
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
from typing import Dict, List, Optional
import argparse
import json

# Configuration du style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class MetagameGraphGenerator:
    """Générateur de graphiques pour le métagame"""
    
    def __init__(self):
        self.colors = {
            'Aggro': '#e74c3c',
            'Control': '#3498db', 
            'Combo': '#9b59b6',
            'Midrange': '#27ae60',
            'Tempo': '#f39c12',
            'Ramp': '#2ecc71',
            'Prison': '#95a5a6',
            'Tribal': '#e67e22'
        }
        
    def generate_sample_data(self, format_name: str, start_date: datetime, days: int = 30) -> pd.DataFrame:
        """Générer des données d'exemple pour le métagame"""
        
        # Archétypes selon le format
        archetypes = {
            'Standard': ['Aggro', 'Control', 'Combo', 'Midrange', 'Tempo'],
            'Modern': ['Aggro', 'Control', 'Combo', 'Midrange', 'Tempo', 'Ramp'],
            'Legacy': ['Combo', 'Control', 'Aggro', 'Prison', 'Tempo'],
            'Pioneer': ['Aggro', 'Control', 'Combo', 'Midrange', 'Tribal'],
            'Vintage': ['Combo', 'Control', 'Prison', 'Aggro'],
            'Pauper': ['Aggro', 'Control', 'Combo', 'Tempo']
        }
        
        format_archetypes = archetypes.get(format_name, ['Aggro', 'Control', 'Combo', 'Midrange'])
        
        # Générer les données
        data = []
        current_date = start_date
        
        # Parts de marché initiales
        base_shares = {}
        total_share = 1.0
        for i, archetype in enumerate(format_archetypes):
            if i == len(format_archetypes) - 1:
                base_shares[archetype] = total_share
            else:
                share = np.random.uniform(0.1, 0.3)
                base_shares[archetype] = share
                total_share -= share
        
        # Normaliser
        total = sum(base_shares.values())
        for archetype in base_shares:
            base_shares[archetype] /= total
            
        for day in range(days):
            date = current_date + timedelta(days=day)
            
            for archetype in format_archetypes:
                # Simuler l'évolution avec tendances
                base_share = base_shares[archetype]
                
                # Ajouter des tendances et du bruit
                trend = np.sin(day * 0.1) * 0.05  # Tendance cyclique
                noise = np.random.normal(0, 0.02)  # Bruit aléatoire
                
                share = max(0.01, base_share + trend + noise)
                winrate = np.random.normal(0.5, 0.05)  # Winrate autour de 50%
                winrate = max(0.3, min(0.7, winrate))  # Limiter entre 30% et 70%
                
                # Popularité corrélée à la part de marché
                popularity = share * np.random.uniform(0.8, 1.2)
                
                data.append({
                    'date': date,
                    'archetype': archetype,
                    'share': share,
                    'winrate': winrate,
                    'popularity': popularity,
                    'format': format_name
                })
                
        return pd.DataFrame(data)
    
    def create_share_evolution_graph(self, df: pd.DataFrame, format_name: str, start_date: datetime):
        """Créer un graphique d'évolution des parts de marché"""
        
        plt.figure(figsize=(14, 8))
        
        # Préparer les données
        pivot_data = df.pivot(index='date', columns='archetype', values='share')
        
        # Créer le graphique
        for archetype in pivot_data.columns:
            color = self.colors.get(archetype, np.random.choice(list(self.colors.values())))
            plt.plot(pivot_data.index, pivot_data[archetype], 
                    label=archetype, linewidth=2.5, color=color, marker='o', markersize=4)
        
        # Formatage
        plt.title(f'Évolution des Parts de Marché - {format_name}\nDepuis le {start_date.strftime("%d/%m/%Y")}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Part de Marché (%)', fontsize=12)
        
        # Formatter l'axe Y en pourcentage
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Formatter l'axe X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(pivot_data) // 10)))
        plt.xticks(rotation=45)
        
        # Légende et grille
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Sauvegarder
        filename = f'metagame_shares_{format_name}_{start_date.strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {filename}")
        
        return filename
    
    def create_winrate_analysis_graph(self, df: pd.DataFrame, format_name: str, start_date: datetime):
        """Créer un graphique d'analyse des winrates"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Graphique 1: Évolution des winrates
        pivot_winrate = df.pivot(index='date', columns='archetype', values='winrate')
        
        for archetype in pivot_winrate.columns:
            color = self.colors.get(archetype, np.random.choice(list(self.colors.values())))
            ax1.plot(pivot_winrate.index, pivot_winrate[archetype], 
                    label=archetype, linewidth=2, color=color, alpha=0.8)
        
        ax1.set_title(f'Évolution des Winrates - {format_name}', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Winrate (%)')
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Ligne de référence à 50%
        ax1.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='50% (Équilibre)')
        
        # Graphique 2: Winrates moyens par archétype
        avg_winrates = df.groupby('archetype')['winrate'].mean().sort_values(ascending=False)
        
        bars = ax2.bar(range(len(avg_winrates)), avg_winrates.values, 
                      color=[self.colors.get(arch, '#95a5a6') for arch in avg_winrates.index])
        
        ax2.set_title('Winrates Moyens par Archétype', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Archétype')
        ax2.set_ylabel('Winrate Moyen (%)')
        ax2.set_xticks(range(len(avg_winrates)))
        ax2.set_xticklabels(avg_winrates.index, rotation=45)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Ajouter les valeurs sur les barres
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # Ligne de référence à 50%
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        
        plt.suptitle(f'Analyse des Winrates - {format_name}\nDepuis le {start_date.strftime("%d/%m/%Y")}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Sauvegarder
        filename = f'winrate_analysis_{format_name}_{start_date.strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {filename}")
        
        return filename
    
    def create_popularity_heatmap(self, df: pd.DataFrame, format_name: str, start_date: datetime):
        """Créer une heatmap de popularité"""
        
        plt.figure(figsize=(14, 8))
        
        # Préparer les données pour la heatmap
        pivot_popularity = df.pivot(index='date', columns='archetype', values='popularity')
        
        # Créer la heatmap
        sns.heatmap(pivot_popularity.T, 
                   cmap='YlOrRd', 
                   annot=False, 
                   fmt='.2f',
                   cbar_kws={'label': 'Popularité'})
        
        plt.title(f'Heatmap de Popularité - {format_name}\nDepuis le {start_date.strftime("%d/%m/%Y")}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Archétype', fontsize=12)
        
        # Formatter l'axe X - version simplifiée
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Sauvegarder
        filename = f'popularity_heatmap_{format_name}_{start_date.strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {filename}")
        
        return filename
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame, format_name: str, start_date: datetime):
        """Créer un dashboard complet"""
        
        fig = plt.figure(figsize=(20, 12))
        
        # Layout du dashboard
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Évolution des parts de marché
        ax1 = fig.add_subplot(gs[0, :])
        pivot_share = df.pivot(index='date', columns='archetype', values='share')
        
        for archetype in pivot_share.columns:
            color = self.colors.get(archetype, np.random.choice(list(self.colors.values())))
            ax1.plot(pivot_share.index, pivot_share[archetype], 
                    label=archetype, linewidth=2, color=color, marker='o', markersize=3)
        
        ax1.set_title('Évolution des Parts de Marché', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Part de Marché (%)')
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Winrates moyens
        ax2 = fig.add_subplot(gs[1, 0])
        avg_winrates = df.groupby('archetype')['winrate'].mean().sort_values(ascending=False)
        bars = ax2.bar(range(len(avg_winrates)), avg_winrates.values,
                      color=[self.colors.get(arch, '#95a5a6') for arch in avg_winrates.index])
        ax2.set_title('Winrates Moyens', fontsize=12, fontweight='bold')
        ax2.set_xticks(range(len(avg_winrates)))
        ax2.set_xticklabels(avg_winrates.index, rotation=45)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        
        # 3. Distribution des parts actuelles (camembert)
        ax3 = fig.add_subplot(gs[1, 1])
        latest_shares = df[df['date'] == df['date'].max()].groupby('archetype')['share'].mean()
        colors_pie = [self.colors.get(arch, '#95a5a6') for arch in latest_shares.index]
        ax3.pie(latest_shares.values, labels=latest_shares.index, autopct='%1.1f%%', 
               colors=colors_pie, startangle=90)
        ax3.set_title('Parts Actuelles', fontsize=12, fontweight='bold')
        
        # 4. Tendances (variation sur la période)
        ax4 = fig.add_subplot(gs[1, 2])
        first_day = df[df['date'] == df['date'].min()].groupby('archetype')['share'].mean()
        last_day = df[df['date'] == df['date'].max()].groupby('archetype')['share'].mean()
        trends = ((last_day - first_day) / first_day * 100).sort_values(ascending=False)
        
        colors_trend = ['green' if x > 0 else 'red' for x in trends.values]
        bars = ax4.bar(range(len(trends)), trends.values, color=colors_trend, alpha=0.7)
        ax4.set_title('Tendances (%)', fontsize=12, fontweight='bold')
        ax4.set_xticks(range(len(trends)))
        ax4.set_xticklabels(trends.index, rotation=45)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.set_ylabel('Variation (%)')
        
        # 5. Heatmap de corrélation
        ax5 = fig.add_subplot(gs[2, :2])
        corr_data = df.pivot_table(index='date', columns='archetype', values='share').corr()
        sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax5, fmt='.2f')
        ax5.set_title('Corrélations entre Archétypes', fontsize=12, fontweight='bold')
        
        # 6. Statistiques résumées
        ax6 = fig.add_subplot(gs[2, 2])
        ax6.axis('off')
        
        # Calculer les statistiques
        stats_text = f"""
STATISTIQUES RÉSUMÉES

Période: {start_date.strftime('%d/%m/%Y')} - {df['date'].max().strftime('%d/%m/%Y')}
Nombre de jours: {len(df['date'].unique())}

ARCHÉTYPE DOMINANT:
{avg_winrates.index[0]} ({avg_winrates.iloc[0]:.1%} winrate)

PLUS GRANDE VARIATION:
{trends.index[0]} ({trends.iloc[0]:+.1f}%)

MÉTA LE PLUS STABLE:
{trends.index[-1]} ({trends.iloc[-1]:+.1f}%)

DIVERSITÉ:
{len(df['archetype'].unique())} archétypes actifs
        """
        
        ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # Titre général
        fig.suptitle(f'Dashboard Métagame - {format_name}\nDepuis le {start_date.strftime("%d/%m/%Y")}', 
                    fontsize=18, fontweight='bold')
        
        # Sauvegarder
        filename = f'dashboard_{format_name}_{start_date.strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Dashboard sauvegardé: {filename}")
        
        return filename
    
    def generate_all_graphs(self, format_name: str, start_date: datetime, days: int = 30):
        """Générer tous les graphiques pour un format et une date donnés"""
        
        print(f"🎯 Génération des graphiques pour {format_name} depuis le {start_date.strftime('%d/%m/%Y')}")
        print("=" * 80)
        
        # Générer les données
        print("📊 Génération des données...")
        df = self.generate_sample_data(format_name, start_date, days)
        
        # Créer les graphiques
        files_created = []
        
        print("\n📈 Création des graphiques...")
        files_created.append(self.create_share_evolution_graph(df, format_name, start_date))
        files_created.append(self.create_winrate_analysis_graph(df, format_name, start_date))
        files_created.append(self.create_popularity_heatmap(df, format_name, start_date))
        files_created.append(self.create_comprehensive_dashboard(df, format_name, start_date))
        
        print(f"\n🎉 Génération terminée! {len(files_created)} graphiques créés:")
        for file in files_created:
            print(f"   📁 {file}")
        
        return files_created

def main():
    """Fonction principale avec interface en ligne de commande"""
    parser = argparse.ArgumentParser(description='Générateur de graphiques métagame MTG')
    parser.add_argument('format', help='Format MTG (Standard, Modern, Legacy, Pioneer, Vintage, Pauper)')
    parser.add_argument('date', help='Date de début (format: YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=30, help='Nombre de jours à analyser (défaut: 30)')
    
    args = parser.parse_args()
    
    try:
        start_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("❌ Format de date invalide. Utilisez YYYY-MM-DD (ex: 2024-01-15)")
        return
    
    # Vérifier que la date n'est pas dans le futur
    if start_date > datetime.now():
        print("❌ La date ne peut pas être dans le futur")
        return
    
    # Créer le générateur et générer les graphiques
    generator = MetagameGraphGenerator()
    generator.generate_all_graphs(args.format, start_date, args.days)

if __name__ == "__main__":
    main() 