#!/usr/bin/env python3
"""
Génère l'analyse finale avec les mêmes graphiques que Jiliac.
Utilise les données fusionnées listener + scrapers pour une comparaison exacte.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict
from scipy import stats
import sys
sys.path.append(str(Path(__file__).parent))

from src.parsers.archetype_parser import ArchetypeParser

# Utilisons le parser d'archétypes
class ArchetypeDetector:
    def __init__(self):
        self.parser = ArchetypeParser()
    
    def detect_archetype(self, mainboard, format_name):
        # Convertir le mainboard si nécessaire
        if isinstance(mainboard, list) and mainboard and isinstance(mainboard[0], dict):
            # Déjà au bon format
            pass
        else:
            # Format simple, convertir
            mainboard_formatted = []
            for card in mainboard:
                if isinstance(card, str):
                    parts = card.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        mainboard_formatted.append({
                            'Count': int(parts[0]),
                            'Name': parts[1]
                        })
            mainboard = mainboard_formatted
        
        return self.parser.detect_archetype(mainboard, [], format_name)

class JiliacFinalAnalyzer:
    def __init__(self):
        self.detector = ArchetypeDetector()
        self.matchups = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        self.archetype_counts = defaultdict(int)
        self.archetype_performance = defaultdict(lambda: {'wins': 0, 'losses': 0})
        
    def load_and_analyze_merged_data(self):
        """Charge et analyse les données fusionnées avec la méthode exacte de Jiliac."""
        merged_dir = Path("data/merged_tournaments/standard")
        
        all_decks = []
        tournament_count = 0
        total_matches_from_rounds = 0
        
        print("\n📊 Analyse des tournois fusionnés...")
        
        for json_file in sorted(merged_dir.glob("*.json")):
            try:
                with open(json_file, 'r') as f:
                    tournament = json.load(f)
                    tournament_count += 1
                    
                # Détection des archétypes pour chaque deck
                decks_with_archetypes = {}
                for deck in tournament.get('Decks', []):
                    # Convertir le format des cartes
                    mainboard_formatted = []
                    for card in deck.get('Mainboard', []):
                        if 'Card' in card and 'Count' in card:
                            mainboard_formatted.append({
                                'Count': card['Count'],
                                'Name': card['Card']
                            })
                    
                    archetype = self.detector.detect_archetype(mainboard_formatted, 'standard')
                    decks_with_archetypes[deck['Player']] = {
                        'deck': deck,
                        'archetype': archetype,
                        'wins': 0,
                        'losses': 0,
                        'opponents': []
                    }
                
                # Analyse des rounds pour les matchups exacts
                for round_data in tournament.get('Rounds', []):
                    for table in round_data.get('Matches', []):
                        player1 = table.get('Player1', {}).get('Name')
                        player2 = table.get('Player2', {}).get('Name')
                        result = table.get('Result', '')
                        
                        if player1 in decks_with_archetypes and player2 in decks_with_archetypes:
                            arch1 = decks_with_archetypes[player1]['archetype']
                            arch2 = decks_with_archetypes[player2]['archetype']
                            
                            # Compter seulement les matchs terminés
                            if '2-0' in result or '2-1' in result or '0-2' in result or '1-2' in result:
                                total_matches_from_rounds += 1
                                
                                if result.startswith('2'):  # Player1 wins
                                    self.matchups[arch1][arch2]['wins'] += 1
                                    self.matchups[arch2][arch1]['losses'] += 1
                                    decks_with_archetypes[player1]['wins'] += 1
                                    decks_with_archetypes[player2]['losses'] += 1
                                    decks_with_archetypes[player1]['opponents'].append(arch2)
                                    decks_with_archetypes[player2]['opponents'].append(arch1)
                                elif result.endswith('2'):  # Player2 wins
                                    self.matchups[arch2][arch1]['wins'] += 1
                                    self.matchups[arch1][arch2]['losses'] += 1
                                    decks_with_archetypes[player2]['wins'] += 1
                                    decks_with_archetypes[player1]['losses'] += 1
                                    decks_with_archetypes[player1]['opponents'].append(arch2)
                                    decks_with_archetypes[player2]['opponents'].append(arch1)
                
                # Collecter les decks avec leurs performances
                for player, data in decks_with_archetypes.items():
                    matches_played = data['wins'] + data['losses']
                    if matches_played > 0:  # Seulement les decks qui ont joué
                        deck_data = data['deck'].copy()
                        deck_data['Archetype'] = data['archetype']
                        deck_data['Wins'] = data['wins']
                        deck_data['Losses'] = data['losses']
                        deck_data['Opponents'] = data['opponents']
                        all_decks.append(deck_data)
                        
                        self.archetype_counts[data['archetype']] += 1
                        self.archetype_performance[data['archetype']]['wins'] += data['wins']
                        self.archetype_performance[data['archetype']]['losses'] += data['losses']
                    
            except Exception as e:
                print(f"⚠️ Erreur avec {json_file.name}: {e}")
        
        print(f"✅ {tournament_count} tournois analysés")
        print(f"✅ {total_matches_from_rounds} matchs extraits des rounds")
        print(f"✅ {len(all_decks)} decks avec performances")
        
        return all_decks, total_matches_from_rounds
    
    def calculate_metagame_metrics(self):
        """Calcule les métriques avec la méthode Jiliac exacte."""
        total_decks = sum(self.archetype_counts.values())
        total_matches = sum(perf['wins'] + perf['losses'] for perf in self.archetype_performance.values()) // 2
        
        metrics = {}
        
        for archetype, count in self.archetype_counts.items():
            perf = self.archetype_performance[archetype]
            matches = perf['wins'] + perf['losses']
            
            # Calculs exacts Jiliac
            deck_share = (count / total_decks * 100) if total_decks > 0 else 0
            match_share = (matches / (total_matches * 2) * 100) if total_matches > 0 else 0
            
            # Winrate avec Wilson CI 90%
            if matches > 0:
                wr = perf['wins'] / matches
                ci_low, ci_high = self._wilson_ci_90(perf['wins'], matches)
            else:
                wr = 0.5
                ci_low, ci_high = 0, 1
            
            metrics[archetype] = {
                'deck_count': count,
                'deck_share': deck_share,
                'match_share': match_share,
                'matches': matches,
                'wins': perf['wins'],
                'losses': perf['losses'],
                'winrate': wr * 100,
                'ci_low': ci_low * 100,
                'ci_high': ci_high * 100
            }
        
        return metrics, total_matches
    
    def _wilson_ci_90(self, wins, total):
        """Wilson score interval avec 90% de confiance (comme Jiliac)."""
        if total == 0:
            return 0, 1
            
        p = wins / total
        z = 1.645  # 90% confidence (comme Jiliac)
        
        denominator = 1 + z**2 / total
        center = (p + z**2 / (2 * total)) / denominator
        margin = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
        
        return max(0, center - margin), min(1, center + margin)
    
    def generate_visualizations(self, metrics, total_matches):
        """Génère les 6 visualisations standards de Jiliac."""
        output_dir = Path("data/cache")
        output_dir.mkdir(exist_ok=True)
        
        # Filtrer avec le seuil de 1.2%
        significant_archetypes = {k: v for k, v in metrics.items() 
                                 if v['match_share'] >= 1.2}
        
        # Trier par match share
        sorted_archetypes = sorted(significant_archetypes.items(), 
                                  key=lambda x: x[1]['match_share'], 
                                  reverse=True)
        
        # HTML structure
        html_parts = []
        html_parts.append(self._generate_html_header(total_matches, len(metrics)))
        
        # 1. Metagame Pie Chart
        print("📊 Génération: Metagame Pie Chart...")
        self._create_metagame_pie(sorted_archetypes)
        html_parts.append(self._add_chart_section("1. Metagame Distribution (Match Share)", 
                                                  "jiliac_1_metagame_pie.png"))
        
        # 2. Performance Bar Chart avec CI
        print("📊 Génération: Performance Bar Chart...")
        self._create_performance_bars(sorted_archetypes)
        html_parts.append(self._add_chart_section("2. Archetype Performance (90% CI)", 
                                                  "jiliac_2_performance_bars.png"))
        
        # 3. Matchup Matrix
        print("📊 Génération: Matchup Matrix...")
        self._create_matchup_matrix(sorted_archetypes)
        html_parts.append(self._add_chart_section("3. Matchup Matrix", 
                                                  "jiliac_3_matchup_matrix.png"))
        
        # 4. Win Rate vs Presence Scatter
        print("📊 Génération: Win Rate vs Presence...")
        self._create_winrate_presence_scatter(sorted_archetypes)
        html_parts.append(self._add_chart_section("4. Win Rate vs Presence", 
                                                  "jiliac_4_winrate_presence.png"))
        
        # 5. Deck Share Distribution
        print("📊 Génération: Deck Share Distribution...")
        self._create_deck_share_bars(sorted_archetypes)
        html_parts.append(self._add_chart_section("5. Deck Share Distribution", 
                                                  "jiliac_5_deck_share.png"))
        
        # 6. Combined Analysis
        print("📊 Génération: Combined Analysis...")
        self._create_combined_analysis(sorted_archetypes)
        html_parts.append(self._add_chart_section("6. Combined Analysis", 
                                                  "jiliac_6_combined.png"))
        
        # Ajouter les statistiques détaillées
        html_parts.append(self._generate_stats_table(sorted_archetypes))
        
        # Footer
        html_parts.append(self._generate_html_footer())
        
        # Sauvegarder le HTML
        html_content = ''.join(html_parts)
        output_file = output_dir / "jiliac_final_complete_analysis.html"
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n✅ Analyse complète générée: {output_file}")
        
        # Afficher la comparaison avec Jiliac
        print("\n🎯 COMPARAISON AVEC JILIAC:")
        print(f"Total matchs analysés: {total_matches}")
        print(f"\nTop 5 archétypes (Match Share):")
        for arch, data in sorted_archetypes[:5]:
            print(f"  {arch}: {data['match_share']:.1f}% (WR: {data['winrate']:.1f}%)")
        
        # Recherche spécifique d'Izzet Cauldron
        for arch, data in metrics.items():
            if 'izzet' in arch.lower() and 'cauldron' in arch.lower():
                print(f"\n⚠️ Izzet Cauldron trouvé: {data['match_share']:.1f}% (vs 20.4% Jiliac)")
                break
        
        return output_file
    
    def _create_metagame_pie(self, sorted_archetypes):
        """Crée le pie chart du métagame."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Données pour le pie
        labels = []
        sizes = []
        colors = []
        
        # Palette de couleurs MTG
        color_palette = {
            'mono white': '#FFFACD',
            'azorius': '#87CEEB',
            'dimir': '#191970',
            'rakdos': '#8B0000',
            'gruul': '#FF6347',
            'selesnya': '#90EE90',
            'orzhov': '#696969',
            'izzet': '#FF69B4',
            'golgari': '#556B2F',
            'boros': '#FFB6C1',
            'simic': '#20B2AA',
            'esper': '#4169E1',
            'grixis': '#8B008B',
            'jund': '#8B4513',
            'naya': '#FFE4B5',
            'bant': '#E0FFFF',
            'domain': '#9370DB'
        }
        
        other_share = 0
        for i, (arch, data) in enumerate(sorted_archetypes):
            if i < 10 and data['match_share'] >= 1.2:
                labels.append(f"{arch}\n{data['match_share']:.1f}%")
                sizes.append(data['match_share'])
                
                # Trouver la couleur
                color = '#808080'
                for key, col in color_palette.items():
                    if key in arch.lower():
                        color = col
                        break
                colors.append(color)
            else:
                other_share += data['match_share']
        
        if other_share > 0:
            labels.append(f"Other\n{other_share:.1f}%")
            sizes.append(other_share)
            colors.append('#C0C0C0')
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='', startangle=90,
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        ax.set_title('Standard Metagame Distribution\n(July 1-21, 2025)', 
                     fontsize=16, weight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_1_metagame_pie.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_performance_bars(self, sorted_archetypes):
        """Crée le bar chart des performances avec IC 90%."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Filtrer et trier par winrate
        filtered = [(a, d) for a, d in sorted_archetypes if d['matches'] >= 20]
        filtered.sort(key=lambda x: x[1]['winrate'], reverse=True)
        
        if len(filtered) > 15:
            filtered = filtered[:15]
        
        archetypes = [a for a, _ in filtered]
        winrates = [d['winrate'] for _, d in filtered]
        ci_low = [d['ci_low'] for _, d in filtered]
        ci_high = [d['ci_high'] for _, d in filtered]
        
        # Positions
        y_pos = np.arange(len(archetypes))
        
        # Barres
        bars = ax.barh(y_pos, winrates, color='#3b82f6', alpha=0.8)
        
        # Intervalles de confiance
        for i in range(len(archetypes)):
            ax.plot([ci_low[i], ci_high[i]], [i, i], 'k-', linewidth=2)
            ax.plot([ci_low[i]], [i], 'k|', markersize=8)
            ax.plot([ci_high[i]], [i], 'k|', markersize=8)
        
        # Ligne à 50%
        ax.axvline(x=50, color='red', linestyle='--', alpha=0.5)
        
        # Labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(archetypes)
        ax.set_xlabel('Win Rate (%)', fontsize=12)
        ax.set_title('Archetype Performance with 90% Confidence Intervals\nStandard - July 1-21, 2025',
                     fontsize=16, weight='bold', pad=20)
        ax.set_xlim(30, 70)
        ax.grid(axis='x', alpha=0.3)
        
        # Ajouter les valeurs
        for i, (bar, wr) in enumerate(zip(bars, winrates)):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{wr:.1f}%', va='center')
        
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_2_performance_bars.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_matchup_matrix(self, sorted_archetypes):
        """Crée la matrice de matchups."""
        # Top 10 archétypes
        top_archs = [a for a, _ in sorted_archetypes[:10]]
        
        # Créer la matrice
        matrix = np.zeros((len(top_archs), len(top_archs)))
        
        for i, arch1 in enumerate(top_archs):
            for j, arch2 in enumerate(top_archs):
                if i != j:
                    wins = self.matchups[arch1][arch2]['wins']
                    losses = self.matchups[arch1][arch2]['losses']
                    total = wins + losses
                    if total > 0:
                        matrix[i, j] = wins / total * 100
                    else:
                        matrix[i, j] = 50
                else:
                    matrix[i, j] = 50  # Mirror
        
        # Heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(matrix, annot=True, fmt='.0f', cmap='RdBu_r', center=50,
                    xticklabels=top_archs, yticklabels=top_archs,
                    cbar_kws={'label': 'Win Rate (%)'}, vmin=20, vmax=80,
                    square=True, linewidths=0.5)
        
        ax.set_title('Matchup Matrix - Top 10 Archetypes\nStandard - July 1-21, 2025',
                     fontsize=16, weight='bold', pad=20)
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_3_matchup_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_winrate_presence_scatter(self, sorted_archetypes):
        """Crée le scatter plot winrate vs presence."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if not sorted_archetypes:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            plt.tight_layout()
            plt.savefig('data/cache/jiliac_4_winrate_presence.png', dpi=150, bbox_inches='tight')
            plt.close()
            return
        
        # Données
        x = [d['match_share'] for _, d in sorted_archetypes]
        y = [d['winrate'] for _, d in sorted_archetypes]
        sizes = [np.sqrt(d['matches']) * 5 for _, d in sorted_archetypes]
        labels = [a for a, _ in sorted_archetypes]
        
        # Scatter plot
        scatter = ax.scatter(x, y, s=sizes, alpha=0.6, c=y, cmap='RdYlGn', 
                           vmin=40, vmax=60, edgecolors='black', linewidth=1)
        
        # Ajouter les labels pour les top archétypes
        for i, (arch, data) in enumerate(sorted_archetypes[:10]):
            ax.annotate(arch, (data['match_share'], data['winrate']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.8)
        
        # Lignes de référence
        ax.axhline(y=50, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=5, color='blue', linestyle='--', alpha=0.5)
        
        # Labels et titre
        ax.set_xlabel('Match Share (%)', fontsize=12)
        ax.set_ylabel('Win Rate (%)', fontsize=12)
        ax.set_title('Win Rate vs Match Share\nStandard - July 1-21, 2025',
                     fontsize=16, weight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-1, max(x) * 1.1)
        ax.set_ylim(35, 65)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Win Rate (%)')
        
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_4_winrate_presence.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_deck_share_bars(self, sorted_archetypes):
        """Crée le bar chart de la distribution des decks."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Top 15 par deck share
        top_15 = sorted_archetypes[:15]
        
        archetypes = [a for a, _ in top_15]
        deck_shares = [d['deck_share'] for _, d in top_15]
        
        # Couleurs basées sur le winrate
        colors = []
        for _, d in top_15:
            if d['winrate'] > 52:
                colors.append('#4ade80')  # Vert
            elif d['winrate'] < 48:
                colors.append('#f87171')  # Rouge
            else:
                colors.append('#60a5fa')  # Bleu
        
        bars = ax.bar(range(len(archetypes)), deck_shares, color=colors, alpha=0.8)
        
        # Labels
        ax.set_xticks(range(len(archetypes)))
        ax.set_xticklabels(archetypes, rotation=45, ha='right')
        ax.set_ylabel('Deck Share (%)', fontsize=12)
        ax.set_title('Deck Share Distribution - Top 15\nStandard - July 1-21, 2025',
                     fontsize=16, weight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        # Valeurs sur les barres
        for bar, share in zip(bars, deck_shares):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{share:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_5_deck_share.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_combined_analysis(self, sorted_archetypes):
        """Crée une analyse combinée avec plusieurs métriques."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Top 10 pour la lisibilité
        top_10 = sorted_archetypes[:10]
        archetypes = [a for a, _ in top_10]
        
        # 1. Match Share vs Deck Share
        match_shares = [d['match_share'] for _, d in top_10]
        deck_shares = [d['deck_share'] for _, d in top_10]
        
        x = np.arange(len(archetypes))
        width = 0.35
        
        ax1.bar(x - width/2, match_shares, width, label='Match Share', alpha=0.8)
        ax1.bar(x + width/2, deck_shares, width, label='Deck Share', alpha=0.8)
        ax1.set_xticks(x)
        ax1.set_xticklabels(archetypes, rotation=45, ha='right')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_title('Match Share vs Deck Share')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Win/Loss Distribution
        wins = [d['wins'] for _, d in top_10]
        losses = [d['losses'] for _, d in top_10]
        
        ax2.bar(x - width/2, wins, width, label='Wins', color='green', alpha=0.8)
        ax2.bar(x + width/2, losses, width, label='Losses', color='red', alpha=0.8)
        ax2.set_xticks(x)
        ax2.set_xticklabels(archetypes, rotation=45, ha='right')
        ax2.set_ylabel('Number of Matches')
        ax2.set_title('Wins vs Losses by Archetype')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Confidence Interval Range
        ci_ranges = [d['ci_high'] - d['ci_low'] for _, d in top_10]
        winrates = [d['winrate'] for _, d in top_10]
        
        bars = ax3.bar(range(len(archetypes)), ci_ranges, color='orange', alpha=0.8)
        ax3_twin = ax3.twinx()
        ax3_twin.plot(range(len(archetypes)), winrates, 'ko-', markersize=8)
        
        ax3.set_xticks(range(len(archetypes)))
        ax3.set_xticklabels(archetypes, rotation=45, ha='right')
        ax3.set_ylabel('CI Range (%)', color='orange')
        ax3_twin.set_ylabel('Win Rate (%)', color='black')
        ax3.set_title('Confidence Interval Range vs Win Rate')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Performance Summary
        ax4.axis('tight')
        ax4.axis('off')
        
        summary_data = []
        for arch, data in top_10:
            summary_data.append([
                arch,
                f"{data['deck_count']}",
                f"{data['matches']}",
                f"{data['winrate']:.1f}%",
                f"[{data['ci_low']:.1f}%, {data['ci_high']:.1f}%]"
            ])
        
        table = ax4.table(cellText=summary_data,
                         colLabels=['Archetype', 'Decks', 'Matches', 'Win Rate', '90% CI'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Style de la table
        for i in range(len(summary_data) + 1):
            for j in range(5):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor('#667eea')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f3f4f6' if i % 2 == 0 else 'white')
        
        ax4.set_title('Performance Summary - Top 10', pad=20, fontsize=14, weight='bold')
        
        plt.suptitle('Combined Analysis - Standard July 1-21, 2025', 
                     fontsize=18, weight='bold')
        plt.tight_layout()
        plt.savefig('data/cache/jiliac_6_combined.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _generate_html_header(self, total_matches, total_archetypes):
        """Génère l'en-tête HTML."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jiliac Final Analysis - Standard (July 1-21, 2025)</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0f172a;
            color: #e2e8f0;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        .header .subtitle {{
            margin-top: 1rem;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border: 1px solid #334155;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #60a5fa;
            margin: 0.5rem 0;
        }}
        .stat-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .chart-section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }}
        .chart-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #f1f5f9;
            border-bottom: 2px solid #334155;
            padding-bottom: 0.5rem;
        }}
        .chart-container {{
            text-align: center;
            padding: 1rem 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        .methodology {{
            background: #334155;
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem 0;
        }}
        .methodology h2 {{
            color: #60a5fa;
            margin-bottom: 1rem;
        }}
        .methodology ul {{
            list-style: none;
            padding: 0;
        }}
        .methodology li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid #475569;
        }}
        .methodology li:last-child {{
            border-bottom: none;
        }}
        .stats-table {{
            background: #1e293b;
            border-radius: 12px;
            padding: 2rem;
            margin-top: 2rem;
            overflow-x: auto;
        }}
        .stats-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .stats-table th {{
            background: #334155;
            color: #f1f5f9;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #60a5fa;
        }}
        .stats-table td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #334155;
        }}
        .stats-table tr:hover {{
            background: #334155;
        }}
        .warning-box {{
            background: #fbbf24;
            color: #111827;
            border-radius: 8px;
            padding: 1rem;
            margin: 2rem 0;
            font-weight: 600;
            text-align: center;
        }}
        .success-box {{
            background: #34d399;
            color: #111827;
            border-radius: 8px;
            padding: 1rem;
            margin: 2rem 0;
            font-weight: 600;
            text-align: center;
        }}
        footer {{
            text-align: center;
            padding: 3rem 0;
            color: #64748b;
            border-top: 1px solid #334155;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Jiliac Method Final Analysis</h1>
        <p class="subtitle">Standard Format - July 1-21, 2025</p>
        <p class="subtitle">Using Merged Listener + Scraper Data</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Matches Analyzed</div>
                <div class="stat-value">{total_matches:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Unique Archetypes</div>
                <div class="stat-value">{total_archetypes}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Analysis Period</div>
                <div class="stat-value">21 Days</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Data Sources</div>
                <div class="stat-value">Merged</div>
            </div>
        </div>
'''
    
    def _add_chart_section(self, title, filename):
        """Ajoute une section de graphique au HTML."""
        return f'''
        <div class="chart-section">
            <h2 class="chart-title">{title}</h2>
            <div class="chart-container">
                <img src="{filename}" alt="{title}">
            </div>
        </div>
'''
    
    def _generate_stats_table(self, sorted_archetypes):
        """Génère le tableau de statistiques détaillées."""
        html = '''
        <div class="stats-table">
            <h2 class="chart-title">Detailed Statistics - All Archetypes</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Archetype</th>
                        <th>Decks</th>
                        <th>Deck Share</th>
                        <th>Matches</th>
                        <th>Match Share</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Win Rate</th>
                        <th>90% CI</th>
                    </tr>
                </thead>
                <tbody>
'''
        
        for i, (arch, data) in enumerate(sorted_archetypes):
            html += f'''
                    <tr>
                        <td>{i+1}</td>
                        <td><strong>{arch}</strong></td>
                        <td>{data['deck_count']}</td>
                        <td>{data['deck_share']:.2f}%</td>
                        <td>{data['matches']}</td>
                        <td>{data['match_share']:.2f}%</td>
                        <td>{data['wins']}</td>
                        <td>{data['losses']}</td>
                        <td style="color: {'#34d399' if data['winrate'] > 52 else '#f87171' if data['winrate'] < 48 else '#60a5fa'}">
                            {data['winrate']:.2f}%
                        </td>
                        <td>[{data['ci_low']:.1f}%, {data['ci_high']:.1f}%]</td>
                    </tr>
'''
        
        html += '''
                </tbody>
            </table>
        </div>
'''
        return html
    
    def _generate_html_footer(self):
        """Génère le footer HTML."""
        return f'''
        <div class="methodology">
            <h2>📊 Methodology</h2>
            <ul>
                <li><strong>Data Source:</strong> Merged MTGO Listener + Scraper data</li>
                <li><strong>Period:</strong> July 1-21, 2025 (21 days)</li>
                <li><strong>Analysis Method:</strong> By MATCHES (Jiliac method)</li>
                <li><strong>Confidence Intervals:</strong> 90% Wilson score intervals</li>
                <li><strong>Minimum Threshold:</strong> 1.2% match share for main visualizations</li>
                <li><strong>Exclusions:</strong> Leagues, casual events</li>
            </ul>
        </div>
        
        <footer>
            <p>Generated by Manalytics - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Based on Jiliac's R-Meta-Analysis methodology</p>
            <p>Pipeline: Listener + Scrapers → Merged Data → Archetype Detection → Analysis</p>
        </footer>
    </div>
</body>
</html>
'''


if __name__ == "__main__":
    analyzer = JiliacFinalAnalyzer()
    
    # Analyser les données fusionnées
    decks, total_matches = analyzer.load_and_analyze_merged_data()
    
    # Calculer les métriques
    metrics, _ = analyzer.calculate_metagame_metrics()
    
    # Générer les visualisations
    output_file = analyzer.generate_visualizations(metrics, total_matches)
    
    # Auto-commit
    os.system(f'git add -A && git commit -m "auto: {datetime.now().strftime("%Y%m%d_%H%M%S")}"')
    
    # Ouvrir automatiquement
    os.system(f'open "{output_file}"')