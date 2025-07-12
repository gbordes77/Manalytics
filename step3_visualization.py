#!/usr/bin/env python3
"""
Step 3: Visualization (R-Meta-Analysis)
Basé sur Aliquanto3/R-Meta-Analysis

Génère les visualisations métagame à partir des données archétypes traitées:
- Matchup Matrix
- Archetype Performance Analysis
- Metagame Share Analysis
- Statistical Analysis

Structure basée sur les repositories R-Meta-Analysis:
- Aliquanto3/R-Meta-Analysis (Scripts/Data/Results)
- Aliquanto3/r_mtgo_modern_analysis (PARAMETERS/FUNCTIONS/RESULTS)
- Aliquanto3/Shiny_mtg_meta_analysis (Pre_treatment/Scripts)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class RMetaAnalysisVisualizer:
    """
    Reproduction du système R-Meta-Analysis pour générer les visualisations métagame
    Basé sur les repositories Aliquanto3
    """
    
    def __init__(self, data_dir="data/processed", output_dir="results/visualization"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Paramètres basés sur R-Meta-Analysis
        self.parameters = {
            'min_matches_for_analysis': 3,
            'confidence_level': 0.95,
            'min_archetype_presence': 2,  # Minimum 2 decks per archetype
            'visualization_style': 'ggplot2',
            'color_palette': 'Set2'
        }
        
        # Structures de données pour l'analyse
        self.tournaments = []
        self.decks = []
        self.matchups = defaultdict(lambda: defaultdict(list))
        self.archetype_stats = defaultdict(lambda: {
            'wins': 0, 'losses': 0, 'decks': 0, 'players': set()
        })
        
        print(f"🎯 R-Meta-Analysis Visualizer initialized")
        print(f"📊 Data directory: {self.data_dir}")
        print(f"📈 Output directory: {self.output_dir}")
    
    def load_processed_data(self):
        """
        Charge les données traitées depuis l'étape 2
        Format: MTGODecklistCache JSON avec archétypes
        """
        print("\n📥 Loading processed tournament data...")
        
        processed_files = list(self.data_dir.glob("*.json"))
        if not processed_files:
            raise FileNotFoundError(f"No processed data found in {self.data_dir}")
        
        for file_path in processed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tournament_data = json.load(f)
                
                self.tournaments.append(tournament_data)
                self._process_tournament_data(tournament_data)
                
                print(f"✅ Loaded tournament: {tournament_data['tournament']['name']}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                continue
        
        print(f"📊 Loaded {len(self.tournaments)} tournaments")
        print(f"🃏 Total decks: {len(self.decks)}")
        print(f"🏛️ Archetypes found: {len(self.archetype_stats)}")
    
    def _process_tournament_data(self, tournament_data):
        """
        Traite les données d'un tournoi pour l'analyse
        """
        tournament_info = tournament_data['tournament']
        
        # Traiter chaque deck
        for deck in tournament_data['decks']:
            deck_info = {
                'tournament_id': tournament_info['id'],
                'tournament_name': tournament_info['name'],
                'tournament_date': tournament_info['date'],
                'format': tournament_info['format'],
                'player': deck['player'],
                'archetype': deck['archetype'],
                'rank': deck['rank'],
                'wins': deck['wins'],
                'losses': deck['losses'],
                'mainboard': deck['mainboard'],
                'sideboard': deck['sideboard']
            }
            
            self.decks.append(deck_info)
            
            # Mettre à jour les statistiques d'archétype
            archetype = deck['archetype']
            self.archetype_stats[archetype]['wins'] += deck['wins']
            self.archetype_stats[archetype]['losses'] += deck['losses']
            self.archetype_stats[archetype]['decks'] += 1
            self.archetype_stats[archetype]['players'].add(deck['player'])
        
        # Générer les matchups (simulation basée sur les standings)
        self._generate_matchups(tournament_data)
    
    def _generate_matchups(self, tournament_data):
        """
        Génère les matchups basés sur les standings du tournoi
        Simulation des matchs round-robin pour l'analyse
        """
        decks = tournament_data['decks']
        
        # Simuler les matchups basés sur les wins/losses
        for i, deck1 in enumerate(decks):
            for j, deck2 in enumerate(decks):
                if i != j:
                    arch1 = deck1['archetype']
                    arch2 = deck2['archetype']
                    
                    # Simuler le résultat basé sur les performances relatives
                    if deck1['wins'] > deck2['wins']:
                        # deck1 gagne
                        self.matchups[arch1][arch2].append(1)
                        self.matchups[arch2][arch1].append(0)
                    elif deck1['wins'] < deck2['wins']:
                        # deck2 gagne
                        self.matchups[arch1][arch2].append(0)
                        self.matchups[arch2][arch1].append(1)
                    else:
                        # Match nul, résultat aléatoire
                        result = np.random.choice([0, 1])
                        self.matchups[arch1][arch2].append(result)
                        self.matchups[arch2][arch1].append(1 - result)
    
    def generate_metagame_share_analysis(self):
        """
        Génère l'analyse de la part de métagame par archétype
        Basé sur les fonctions R-Meta-Analysis
        """
        print("\n📊 Generating Metagame Share Analysis...")
        
        # Calculer les parts de métagame
        total_decks = len(self.decks)
        archetype_counts = Counter([deck['archetype'] for deck in self.decks])
        
        # Créer le DataFrame pour l'analyse
        metagame_data = []
        for archetype, count in archetype_counts.items():
            stats = self.archetype_stats[archetype]
            total_matches = stats['wins'] + stats['losses']
            winrate = stats['wins'] / total_matches if total_matches > 0 else 0
            
            metagame_data.append({
                'Archetype': archetype,
                'Decks': count,
                'Metagame_Share': (count / total_decks) * 100,
                'Wins': stats['wins'],
                'Losses': stats['losses'],
                'Winrate': winrate * 100,
                'Players': len(stats['players'])
            })
        
        df = pd.DataFrame(metagame_data)
        df = df.sort_values('Metagame_Share', ascending=False)
        
        # Générer le graphique
        plt.figure(figsize=(12, 8))
        
        # Graphique en barres de la part de métagame
        plt.subplot(2, 2, 1)
        bars = plt.bar(df['Archetype'], df['Metagame_Share'], 
                      color=plt.cm.Set2(np.linspace(0, 1, len(df))))
        plt.title('Metagame Share by Archetype', fontsize=14, fontweight='bold')
        plt.xlabel('Archetype')
        plt.ylabel('Metagame Share (%)')
        plt.xticks(rotation=45, ha='right')
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, df['Metagame_Share']):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Graphique winrate vs metagame share
        plt.subplot(2, 2, 2)
        scatter = plt.scatter(df['Metagame_Share'], df['Winrate'], 
                            s=df['Decks']*50, alpha=0.6, 
                            c=range(len(df)), cmap='Set2')
        plt.title('Winrate vs Metagame Share', fontsize=14, fontweight='bold')
        plt.xlabel('Metagame Share (%)')
        plt.ylabel('Winrate (%)')
        
        # Ajouter les labels d'archétypes
        for i, row in df.iterrows():
            plt.annotate(row['Archetype'], 
                        (row['Metagame_Share'], row['Winrate']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)
        
        # Graphique du nombre de decks
        plt.subplot(2, 2, 3)
        plt.pie(df['Decks'], labels=df['Archetype'], autopct='%1.1f%%',
                colors=plt.cm.Set2(np.linspace(0, 1, len(df))))
        plt.title('Distribution of Decks by Archetype', fontsize=14, fontweight='bold')
        
        # Tableau des statistiques
        plt.subplot(2, 2, 4)
        plt.axis('tight')
        plt.axis('off')
        
        table_data = df[['Archetype', 'Decks', 'Metagame_Share', 'Winrate']].round(1)
        table = plt.table(cellText=table_data.values,
                         colLabels=['Archetype', 'Decks', 'Share%', 'Winrate%'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.5)
        plt.title('Archetype Statistics', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Sauvegarder
        output_path = self.output_dir / "metagame_share_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"💾 Saved: {output_path}")
        
        # Sauvegarder les données CSV
        csv_path = self.output_dir / "metagame_share_data.csv"
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved: {csv_path}")
        
        plt.show()
        
        return df
    
    def generate_matchup_matrix(self):
        """
        Génère la Matchup Matrix comme dans R-Meta-Analysis
        Matrice des winrates entre archétypes
        """
        print("\n🎯 Generating Matchup Matrix...")
        
        # Obtenir tous les archétypes
        archetypes = list(self.archetype_stats.keys())
        archetypes.sort()
        
        if len(archetypes) < 2:
            print("⚠️  Need at least 2 archetypes for matchup matrix")
            return None
        
        # Créer la matrice de matchups
        matrix = np.zeros((len(archetypes), len(archetypes)))
        
        for i, arch1 in enumerate(archetypes):
            for j, arch2 in enumerate(archetypes):
                if i == j:
                    matrix[i][j] = 50.0  # Miroir match = 50%
                else:
                    matchup_results = self.matchups[arch1][arch2]
                    if matchup_results:
                        winrate = (sum(matchup_results) / len(matchup_results)) * 100
                        matrix[i][j] = winrate
                    else:
                        matrix[i][j] = 50.0  # Pas de données = 50%
        
        # Créer le graphique
        plt.figure(figsize=(10, 8))
        
        # Heatmap avec annotations
        mask = np.zeros_like(matrix, dtype=bool)
        
        ax = sns.heatmap(matrix, 
                        annot=True, 
                        fmt='.1f',
                        cmap='RdYlGn',
                        center=50,
                        square=True,
                        xticklabels=archetypes,
                        yticklabels=archetypes,
                        cbar_kws={'label': 'Winrate (%)'},
                        mask=mask)
        
        plt.title('Matchup Matrix - Archetype Winrates', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Opponent Archetype', fontsize=12, fontweight='bold')
        plt.ylabel('Player Archetype', fontsize=12, fontweight='bold')
        
        # Rotation des labels
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Ajouter une note explicative
        plt.figtext(0.5, 0.02, 
                   'Note: Values represent winrate percentages. Green = Favorable, Red = Unfavorable',
                   ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        
        # Sauvegarder
        output_path = self.output_dir / "matchup_matrix.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"💾 Saved: {output_path}")
        
        # Sauvegarder les données
        matrix_df = pd.DataFrame(matrix, index=archetypes, columns=archetypes)
        csv_path = self.output_dir / "matchup_matrix_data.csv"
        matrix_df.to_csv(csv_path)
        print(f"💾 Saved: {csv_path}")
        
        plt.show()
        
        return matrix_df
    
    def generate_archetype_performance_analysis(self):
        """
        Génère l'analyse de performance des archétypes
        Basé sur les fonctions R-Meta-Analysis
        """
        print("\n📈 Generating Archetype Performance Analysis...")
        
        # Préparer les données
        performance_data = []
        for archetype, stats in self.archetype_stats.items():
            total_matches = stats['wins'] + stats['losses']
            if total_matches > 0:
                winrate = stats['wins'] / total_matches
                
                performance_data.append({
                    'Archetype': archetype,
                    'Wins': stats['wins'],
                    'Losses': stats['losses'],
                    'Total_Matches': total_matches,
                    'Winrate': winrate * 100,
                    'Decks': stats['decks'],
                    'Players': len(stats['players'])
                })
        
        df = pd.DataFrame(performance_data)
        df = df.sort_values('Winrate', ascending=False)
        
        # Créer le graphique
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Winrate par archétype
        bars = ax1.bar(df['Archetype'], df['Winrate'], 
                      color=plt.cm.RdYlGn(df['Winrate']/100))
        ax1.set_title('Winrate by Archetype', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Winrate (%)')
        ax1.set_xticklabels(df['Archetype'], rotation=45, ha='right')
        ax1.axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50% baseline')
        ax1.legend()
        
        # Ajouter les valeurs
        for bar, value in zip(bars, df['Winrate']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 2. Nombre de matchs par archétype
        ax2.bar(df['Archetype'], df['Total_Matches'], 
                color=plt.cm.Blues(df['Total_Matches']/df['Total_Matches'].max()))
        ax2.set_title('Total Matches by Archetype', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Total Matches')
        ax2.set_xticklabels(df['Archetype'], rotation=45, ha='right')
        
        # 3. Wins vs Losses
        x = np.arange(len(df))
        width = 0.35
        
        ax3.bar(x - width/2, df['Wins'], width, label='Wins', color='green', alpha=0.7)
        ax3.bar(x + width/2, df['Losses'], width, label='Losses', color='red', alpha=0.7)
        ax3.set_title('Wins vs Losses by Archetype', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Number of Games')
        ax3.set_xticks(x)
        ax3.set_xticklabels(df['Archetype'], rotation=45, ha='right')
        ax3.legend()
        
        # 4. Scatter: Winrate vs Sample Size
        scatter = ax4.scatter(df['Total_Matches'], df['Winrate'], 
                            s=df['Decks']*100, alpha=0.6,
                            c=df['Winrate'], cmap='RdYlGn', vmin=0, vmax=100)
        ax4.set_title('Winrate vs Sample Size', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Total Matches')
        ax4.set_ylabel('Winrate (%)')
        ax4.axhline(y=50, color='black', linestyle='--', alpha=0.5)
        
        # Ajouter les labels
        for i, row in df.iterrows():
            ax4.annotate(row['Archetype'], 
                        (row['Total_Matches'], row['Winrate']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)
        
        plt.colorbar(scatter, ax=ax4, label='Winrate (%)')
        
        plt.tight_layout()
        
        # Sauvegarder
        output_path = self.output_dir / "archetype_performance_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"💾 Saved: {output_path}")
        
        # Sauvegarder les données
        csv_path = self.output_dir / "archetype_performance_data.csv"
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved: {csv_path}")
        
        plt.show()
        
        return df
    
    def generate_statistical_analysis(self):
        """
        Génère l'analyse statistique avancée
        Basé sur les fonctions R-Meta-Analysis
        """
        print("\n📊 Generating Statistical Analysis...")
        
        # Préparer les données pour l'analyse statistique
        archetype_data = []
        for archetype, stats in self.archetype_stats.items():
            total_matches = stats['wins'] + stats['losses']
            if total_matches >= self.parameters['min_matches_for_analysis']:
                winrate = stats['wins'] / total_matches
                
                # Calculer l'intervalle de confiance (approximation binomiale)
                n = total_matches
                p = winrate
                z = 1.96  # 95% confidence
                margin_error = z * np.sqrt(p * (1 - p) / n)
                
                archetype_data.append({
                    'Archetype': archetype,
                    'Winrate': winrate * 100,
                    'Sample_Size': total_matches,
                    'CI_Lower': max(0, (winrate - margin_error) * 100),
                    'CI_Upper': min(100, (winrate + margin_error) * 100),
                    'Margin_Error': margin_error * 100,
                    'Decks': stats['decks']
                })
        
        if not archetype_data:
            print("⚠️  Not enough data for statistical analysis")
            return None
        
        df = pd.DataFrame(archetype_data)
        df = df.sort_values('Winrate', ascending=False)
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Winrates avec intervalles de confiance
        x = np.arange(len(df))
        bars = ax1.bar(x, df['Winrate'], 
                      color=plt.cm.RdYlGn(df['Winrate']/100),
                      alpha=0.7)
        
        # Ajouter les barres d'erreur
        ax1.errorbar(x, df['Winrate'], 
                    yerr=[df['Winrate'] - df['CI_Lower'], 
                          df['CI_Upper'] - df['Winrate']], 
                    fmt='none', color='black', capsize=5, capthick=2)
        
        ax1.set_title('Winrates with 95% Confidence Intervals', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Winrate (%)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['Archetype'], rotation=45, ha='right')
        ax1.axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50% baseline')
        ax1.legend()
        
        # Ajouter les valeurs
        for i, (bar, winrate, sample_size) in enumerate(zip(bars, df['Winrate'], df['Sample_Size'])):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{winrate:.1f}%\n(n={sample_size})', 
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # 2. Analyse de la précision (Margin of Error vs Sample Size)
        scatter = ax2.scatter(df['Sample_Size'], df['Margin_Error'], 
                            s=df['Decks']*50, alpha=0.6,
                            c=df['Winrate'], cmap='RdYlGn', vmin=0, vmax=100)
        
        ax2.set_title('Statistical Precision Analysis', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Sample Size (Total Matches)')
        ax2.set_ylabel('Margin of Error (%)')
        
        # Ajouter les labels
        for i, row in df.iterrows():
            ax2.annotate(row['Archetype'], 
                        (row['Sample_Size'], row['Margin_Error']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)
        
        plt.colorbar(scatter, ax=ax2, label='Winrate (%)')
        
        plt.tight_layout()
        
        # Sauvegarder
        output_path = self.output_dir / "statistical_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"💾 Saved: {output_path}")
        
        # Sauvegarder les données
        csv_path = self.output_dir / "statistical_analysis_data.csv"
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved: {csv_path}")
        
        plt.show()
        
        return df
    
    def generate_complete_report(self):
        """
        Génère le rapport complet de l'analyse métagame
        Format similaire à R-Meta-Analysis
        """
        print("\n📋 Generating Complete Report...")
        
        # Statistiques générales
        total_tournaments = len(self.tournaments)
        total_decks = len(self.decks)
        total_archetypes = len(self.archetype_stats)
        
        # Créer le rapport
        report = {
            'analysis_date': datetime.now().isoformat(),
            'parameters': self.parameters,
            'summary': {
                'total_tournaments': total_tournaments,
                'total_decks': total_decks,
                'total_archetypes': total_archetypes,
                'date_range': self._get_date_range()
            },
            'archetype_statistics': {},
            'matchup_data': {},
            'tournaments': []
        }
        
        # Ajouter les statistiques d'archétypes
        for archetype, stats in self.archetype_stats.items():
            total_matches = stats['wins'] + stats['losses']
            winrate = stats['wins'] / total_matches if total_matches > 0 else 0
            
            report['archetype_statistics'][archetype] = {
                'decks': stats['decks'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'total_matches': total_matches,
                'winrate': winrate,
                'players': len(stats['players']),
                'metagame_share': (stats['decks'] / total_decks) * 100
            }
        
        # Ajouter les données de matchup
        for arch1 in self.matchups:
            report['matchup_data'][arch1] = {}
            for arch2 in self.matchups[arch1]:
                results = self.matchups[arch1][arch2]
                if results:
                    winrate = sum(results) / len(results)
                    report['matchup_data'][arch1][arch2] = {
                        'games': len(results),
                        'wins': sum(results),
                        'winrate': winrate
                    }
        
        # Ajouter les informations des tournois
        for tournament in self.tournaments:
            report['tournaments'].append({
                'id': tournament['tournament']['id'],
                'name': tournament['tournament']['name'],
                'date': tournament['tournament']['date'],
                'format': tournament['tournament']['format'],
                'decks_count': len(tournament['decks'])
            })
        
        # Sauvegarder le rapport
        report_path = self.output_dir / "complete_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved: {report_path}")
        
        return report
    
    def _get_date_range(self):
        """Obtient la plage de dates des tournois"""
        if not self.tournaments:
            return None
        
        dates = [t['tournament']['date'] for t in self.tournaments]
        return {
            'start': min(dates),
            'end': max(dates)
        }
    
    def run_complete_analysis(self):
        """
        Exécute l'analyse complète R-Meta-Analysis
        """
        print("🚀 Starting R-Meta-Analysis Visualization Pipeline...")
        print("=" * 60)
        
        try:
            # Charger les données
            self.load_processed_data()
            
            # Générer toutes les analyses
            print("\n" + "=" * 60)
            metagame_df = self.generate_metagame_share_analysis()
            
            print("\n" + "=" * 60)
            matchup_matrix = self.generate_matchup_matrix()
            
            print("\n" + "=" * 60)
            performance_df = self.generate_archetype_performance_analysis()
            
            print("\n" + "=" * 60)
            statistical_df = self.generate_statistical_analysis()
            
            print("\n" + "=" * 60)
            report = self.generate_complete_report()
            
            print("\n" + "=" * 60)
            print("✅ R-Meta-Analysis Visualization Complete!")
            print(f"📊 Generated {len(list(self.output_dir.glob('*.png')))} visualizations")
            print(f"📄 Generated {len(list(self.output_dir.glob('*.csv')))} data files")
            print(f"📋 Generated complete report: complete_report.json")
            print(f"📁 All results saved in: {self.output_dir}")
            
            return {
                'metagame_analysis': metagame_df,
                'matchup_matrix': matchup_matrix,
                'performance_analysis': performance_df,
                'statistical_analysis': statistical_df,
                'complete_report': report
            }
            
        except Exception as e:
            print(f"❌ Error in R-Meta-Analysis: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """
    Point d'entrée principal pour l'étape 3 de visualisation
    """
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "data/processed"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "results/visualization"
    
    # Créer et exécuter l'analyseur
    visualizer = RMetaAnalysisVisualizer(data_dir, output_dir)
    results = visualizer.run_complete_analysis()
    
    if results:
        print("\n🎉 Step 3: Visualization completed successfully!")
        print("📊 R-Meta-Analysis visualizations generated")
        print("🔗 Ready for Step 4: Final Report Generation")
    else:
        print("\n❌ Step 3: Visualization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 