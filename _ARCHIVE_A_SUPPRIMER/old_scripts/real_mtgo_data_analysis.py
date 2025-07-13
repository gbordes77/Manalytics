#!/usr/bin/env python3
"""
Analyseur de données MTGO réelles - Reproduction exacte du projet R-Meta-Analysis
Utilise les vraies données du MTGODecklistCache et MTGOFormatData
"""

import json
import os
import glob
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MTGOArchetypeParser:
    """Parser pour les données MTGOArchetypeParser - reproduction exacte"""
    
    def __init__(self, mtgo_cache_path="MTGODecklistCache", format_data_path="MTGOFormatData"):
        self.mtgo_cache_path = mtgo_cache_path
        self.format_data_path = format_data_path
        self.archetypes = {}
        self.fallbacks = {}
        self.metas = {}
        self.color_overrides = {}
        
    def load_format_data(self, format_name="Modern"):
        """Charge les données de format (archétypes, métas, etc.)"""
        format_path = os.path.join(self.format_data_path, "Formats", format_name)
        
        # Charger les métas
        metas_file = os.path.join(format_path, "metas.json")
        if os.path.exists(metas_file):
            with open(metas_file, 'r') as f:
                self.metas = json.load(f)
        
        # Charger les archétypes
        archetypes_path = os.path.join(format_path, "Archetypes")
        if os.path.exists(archetypes_path):
            for archetype_file in glob.glob(os.path.join(archetypes_path, "*.json")):
                try:
                    with open(archetype_file, 'r') as f:
                        archetype_data = json.load(f)
                        self.archetypes[archetype_data['Name']] = archetype_data
                except json.JSONDecodeError as e:
                    print(f"⚠️  Erreur JSON dans {os.path.basename(archetype_file)}: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️  Erreur lors du chargement de {os.path.basename(archetype_file)}: {e}")
                    continue
        
        # Charger les fallbacks
        fallbacks_path = os.path.join(format_path, "Fallbacks")
        if os.path.exists(fallbacks_path):
            for fallback_file in glob.glob(os.path.join(fallbacks_path, "*.json")):
                try:
                    with open(fallback_file, 'r') as f:
                        fallback_data = json.load(f)
                        self.fallbacks[fallback_data['Name']] = fallback_data
                except json.JSONDecodeError as e:
                    print(f"⚠️  Erreur JSON dans {os.path.basename(fallback_file)}: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️  Erreur lors du chargement de {os.path.basename(fallback_file)}: {e}")
                    continue
        
        print(f"✓ Chargé {len(self.archetypes)} archétypes et {len(self.fallbacks)} fallbacks pour {format_name}")
    
    def load_tournament_data(self, format_name="Modern", start_date="2024-06-01", end_date="2024-06-30"):
        """Charge les données de tournois MTGO pour une période donnée"""
        tournaments = []
        
        # Parcourir les fichiers de tournois
        tournaments_path = os.path.join(self.mtgo_cache_path, "Tournaments", "mtgo.com")
        
        for year_dir in os.listdir(tournaments_path):
            year_path = os.path.join(tournaments_path, year_dir)
            if not os.path.isdir(year_path):
                continue
                
            for month_dir in os.listdir(year_path):
                month_path = os.path.join(year_path, month_dir)
                if not os.path.isdir(month_path):
                    continue
                    
                for day_dir in os.listdir(month_path):
                    day_path = os.path.join(month_path, day_dir)
                    if not os.path.isdir(day_path):
                        continue
                    
                    # Vérifier la date
                    try:
                        date_str = f"{year_dir}-{month_dir.zfill(2)}-{day_dir.zfill(2)}"
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
                        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
                        
                        if not (start_obj <= date_obj <= end_obj):
                            continue
                    except:
                        continue
                    
                    # Charger les tournois du jour
                    for tournament_file in os.listdir(day_path):
                        if not tournament_file.endswith('.json'):
                            continue
                        
                        # Filtrer par format
                        if format_name.lower() not in tournament_file.lower():
                            continue
                        
                        # Exclure les leagues pour avoir des données plus propres
                        if 'league' in tournament_file.lower():
                            continue
                        
                        tournament_path = os.path.join(day_path, tournament_file)
                        try:
                            with open(tournament_path, 'r') as f:
                                tournament_data = json.load(f)
                                tournaments.append(tournament_data)
                        except Exception as e:
                            print(f"Erreur lors du chargement de {tournament_file}: {e}")
        
        print(f"✓ Chargé {len(tournaments)} tournois {format_name} entre {start_date} et {end_date}")
        return tournaments
    
    def detect_archetype(self, deck_cards):
        """Détecte l'archétype d'un deck selon les règles MTGOArchetypeParser"""
        mainboard_cards = [card['CardName'] for card in deck_cards.get('Mainboard', [])]
        sideboard_cards = [card['CardName'] for card in deck_cards.get('Sideboard', [])]
        all_cards = mainboard_cards + sideboard_cards
        
        # Tester chaque archétype
        for archetype_name, archetype_data in self.archetypes.items():
            if self._matches_conditions(archetype_data['Conditions'], mainboard_cards, sideboard_cards, all_cards):
                # Tester les variants
                for variant in archetype_data.get('Variants', []):
                    if self._matches_conditions(variant['Conditions'], mainboard_cards, sideboard_cards, all_cards):
                        return variant['Name']
                return archetype_name
        
        # Si aucun archétype ne match, essayer les fallbacks
        best_fallback = None
        best_match_count = 0
        
        for fallback_name, fallback_data in self.fallbacks.items():
            common_cards = fallback_data.get('CommonCards', [])
            match_count = sum(1 for card in common_cards if card in all_cards)
            
            # Règle des 10% minimum
            if match_count >= len(common_cards) * 0.1 and match_count > best_match_count:
                best_match_count = match_count
                best_fallback = fallback_name
        
        return best_fallback or "Unknown"
    
    def _matches_conditions(self, conditions, mainboard, sideboard, all_cards):
        """Vérifie si un deck match les conditions d'un archétype"""
        for condition in conditions:
            condition_type = condition['Type']
            cards = condition['Cards']
            
            if condition_type == "InMainboard":
                if not all(card in mainboard for card in cards):
                    return False
            elif condition_type == "InSideboard":
                if not all(card in sideboard for card in cards):
                    return False
            elif condition_type == "InMainOrSideboard":
                if not all(card in all_cards for card in cards):
                    return False
            elif condition_type == "OneOrMoreInMainboard":
                if not any(card in mainboard for card in cards):
                    return False
            elif condition_type == "OneOrMoreInSideboard":
                if not any(card in sideboard for card in cards):
                    return False
            elif condition_type == "OneOrMoreInMainOrSideboard":
                if not any(card in all_cards for card in cards):
                    return False
            elif condition_type == "TwoOrMoreInMainboard":
                if sum(1 for card in cards if card in mainboard) < 2:
                    return False
            elif condition_type == "TwoOrMoreInSideboard":
                if sum(1 for card in cards if card in sideboard) < 2:
                    return False
            elif condition_type == "TwoOrMoreInMainOrSideboard":
                if sum(1 for card in cards if card in all_cards) < 2:
                    return False
            elif condition_type == "DoesNotContain":
                if any(card in all_cards for card in cards):
                    return False
            elif condition_type == "DoesNotContainMainboard":
                if any(card in mainboard for card in cards):
                    return False
            elif condition_type == "DoesNotContainSideboard":
                if any(card in sideboard for card in cards):
                    return False
        
        return True

class RMetaAnalysisReproducer:
    """Reproduction exacte de la méthodologie R-Meta-Analysis"""
    
    def __init__(self):
        self.parser = MTGOArchetypeParser()
        self.deck_results = []
        self.archetype_stats = {}
        
    def analyze_tournaments(self, format_name="Modern", start_date="2024-06-01", end_date="2024-06-30"):
        """Analyse les tournois selon la méthodologie R-Meta-Analysis"""
        print(f"=== ANALYSE R-META-ANALYSIS - {format_name} ===")
        print(f"Période: {start_date} à {end_date}")
        print()
        
        # Charger les données
        self.parser.load_format_data(format_name)
        tournaments = self.parser.load_tournament_data(format_name, start_date, end_date)
        
        if not tournaments:
            print("❌ Aucun tournoi trouvé pour cette période")
            return
        
        # Analyser chaque deck
        print("🔍 Analyse des decks...")
        for tournament in tournaments:
            tournament_info = tournament.get('Tournament', {})
            tournament_name = tournament_info.get('Name', 'Unknown')
            tournament_date = tournament_info.get('Date', 'Unknown')
            
            for deck in tournament.get('Decks', []):
                # Détecter l'archétype
                archetype = self.parser.detect_archetype(deck)
                
                # Extraire les résultats
                result = deck.get('Result', '0-0')
                player = deck.get('Player', 'Unknown')
                
                # Calculer wins/losses
                if '-' in result:
                    try:
                        wins, losses = map(int, result.split('-'))
                    except:
                        wins, losses = 0, 0
                else:
                    wins, losses = 0, 0
                
                deck_result = {
                    'tournament': tournament_name,
                    'date': tournament_date,
                    'player': player,
                    'archetype': archetype,
                    'result': result,
                    'wins': wins,
                    'losses': losses,
                    'matches': wins + losses,
                    'winrate': wins / (wins + losses) if (wins + losses) > 0 else 0
                }
                
                self.deck_results.append(deck_result)
        
        print(f"✓ Analysé {len(self.deck_results)} decks")
        
        # Calculer les statistiques par archétype
        self._calculate_archetype_stats()
        
        # Générer les graphiques R-style
        self._generate_r_style_charts()
        
        # Générer le rapport
        self._generate_report()
    
    def _calculate_archetype_stats(self):
        """Calcule les statistiques par archétype avec intervalles de confiance"""
        archetype_data = defaultdict(lambda: {
            'decks': [],
            'total_matches': 0,
            'total_wins': 0,
            'total_losses': 0
        })
        
        # Agréger les données
        for deck in self.deck_results:
            archetype = deck['archetype']
            archetype_data[archetype]['decks'].append(deck)
            archetype_data[archetype]['total_matches'] += deck['matches']
            archetype_data[archetype]['total_wins'] += deck['wins']
            archetype_data[archetype]['total_losses'] += deck['losses']
        
        # Calculer les statistiques
        total_decks = len(self.deck_results)
        
        for archetype, data in archetype_data.items():
            deck_count = len(data['decks'])
            total_matches = data['total_matches']
            total_wins = data['total_wins']
            
            # Métagame share
            metagame_share = (deck_count / total_decks) * 100
            
            # Winrate
            winrate = (total_wins / total_matches) * 100 if total_matches > 0 else 0
            
            # Intervalle de confiance 95% (méthode Wilson)
            if total_matches > 0:
                p = total_wins / total_matches
                n = total_matches
                z = 1.96  # 95% confidence
                
                denominator = 1 + (z**2 / n)
                center = (p + (z**2 / (2*n))) / denominator
                margin = z * np.sqrt((p * (1-p) / n) + (z**2 / (4*n**2))) / denominator
                
                ci_lower = max(0, (center - margin) * 100)
                ci_upper = min(100, (center + margin) * 100)
            else:
                ci_lower = ci_upper = 0
            
            # Classification par tier selon CI lower bound
            if ci_lower >= 55:
                tier = "S"
            elif ci_lower >= 52:
                tier = "A"
            elif ci_lower >= 50:
                tier = "B"
            elif ci_lower >= 45:
                tier = "C"
            else:
                tier = "D"
            
            self.archetype_stats[archetype] = {
                'deck_count': deck_count,
                'metagame_share': metagame_share,
                'total_matches': total_matches,
                'total_wins': total_wins,
                'total_losses': data['total_losses'],
                'winrate': winrate,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'tier': tier
            }
    
    def _generate_r_style_charts(self):
        """Génère les graphiques dans le style exact du projet R"""
        print("📊 Génération des graphiques R-style...")
        
        # Filtrer les archétypes avec assez de données
        significant_archetypes = {k: v for k, v in self.archetype_stats.items() 
                                if v['deck_count'] >= 3 and k != "Unknown"}
        
        if not significant_archetypes:
            print("❌ Pas assez de données pour générer les graphiques")
            return
        
        # Style R
        plt.style.use('default')
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })
        
        # 1. Graphique de part de métagame (horizontal bars)
        fig, ax = plt.subplots(figsize=(10, 8))
        
        archetypes = list(significant_archetypes.keys())
        shares = [significant_archetypes[arch]['metagame_share'] for arch in archetypes]
        
        # Trier par share décroissant
        sorted_data = sorted(zip(archetypes, shares), key=lambda x: x[1], reverse=True)
        archetypes, shares = zip(*sorted_data)
        
        bars = ax.barh(range(len(archetypes)), shares, color='lightblue', edgecolor='black')
        
        # Ajouter les pourcentages
        for i, (bar, share) in enumerate(zip(bars, shares)):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{share:.1f}%', va='center', fontweight='bold')
        
        ax.set_yticks(range(len(archetypes)))
        ax.set_yticklabels(archetypes)
        ax.set_xlabel('Metagame Share (%)')
        ax.set_title('Modern Metagame Breakdown\n(MTGO Data)', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('metagame_share_r_style.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Winrates avec intervalles de confiance
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Trier par winrate décroissant
        sorted_data = sorted(significant_archetypes.items(), 
                           key=lambda x: x[1]['winrate'], reverse=True)
        
        archetypes = [item[0] for item in sorted_data]
        winrates = [item[1]['winrate'] for item in sorted_data]
        ci_lowers = [item[1]['ci_lower'] for item in sorted_data]
        ci_uppers = [item[1]['ci_upper'] for item in sorted_data]
        
        # Calculer les erreurs pour errorbar
        yerr_lower = [wr - ci_l for wr, ci_l in zip(winrates, ci_lowers)]
        yerr_upper = [ci_u - wr for wr, ci_u in zip(winrates, ci_uppers)]
        
        bars = ax.bar(range(len(archetypes)), winrates, 
                     yerr=[yerr_lower, yerr_upper], capsize=5,
                     color='lightcoral', edgecolor='black', alpha=0.7)
        
        # Ligne de référence à 50%
        ax.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% Baseline')
        
        # Ajouter les valeurs
        for i, (bar, wr, ci_l, ci_u) in enumerate(zip(bars, winrates, ci_lowers, ci_uppers)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f'{wr:.1f}%\n[{ci_l:.1f}-{ci_u:.1f}]', 
                   ha='center', va='bottom', fontsize=8)
        
        ax.set_xticks(range(len(archetypes)))
        ax.set_xticklabels(archetypes, rotation=45, ha='right')
        ax.set_ylabel('Winrate (%)')
        ax.set_title('Archetype Winrates with 95% Confidence Intervals\n(MTGO Data)', fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('winrates_confidence_intervals_r_style.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Scatter plot Winrate vs Presence
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x_values = [stats['metagame_share'] for stats in significant_archetypes.values()]
        y_values = [stats['winrate'] for stats in significant_archetypes.values()]
        sizes = [stats['total_matches'] * 2 for stats in significant_archetypes.values()]  # Taille = nombre de matches
        colors = [stats['ci_lower'] for stats in significant_archetypes.values()]
        
        scatter = ax.scatter(x_values, y_values, s=sizes, c=colors, alpha=0.7, 
                           cmap='RdYlBu_r', edgecolors='black')
        
        # Lignes de référence
        ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Winrate')
        ax.axvline(x=np.mean(x_values), color='blue', linestyle='--', alpha=0.5, label='Avg Presence')
        
        # Annotations
        for i, (arch, stats) in enumerate(significant_archetypes.items()):
            ax.annotate(arch, (stats['metagame_share'], stats['winrate']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_xlabel('Metagame Share (%)')
        ax.set_ylabel('Winrate (%)')
        ax.set_title('Winrate vs Presence\n(Bubble size = Total matches, Color = CI Lower Bound)', fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('CI Lower Bound (%)')
        
        plt.tight_layout()
        plt.savefig('winrate_vs_presence_r_style.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Tier Classification Scatter
        fig, ax = plt.subplots(figsize=(12, 8))
        
        tier_colors = {'S': 'gold', 'A': 'silver', 'B': 'orange', 'C': 'lightcoral', 'D': 'lightgray'}
        
        for tier in ['S', 'A', 'B', 'C', 'D']:
            tier_archetypes = {k: v for k, v in significant_archetypes.items() if v['tier'] == tier}
            if tier_archetypes:
                x_vals = [stats['metagame_share'] for stats in tier_archetypes.values()]
                y_vals = [stats['ci_lower'] for stats in tier_archetypes.values()]
                ax.scatter(x_vals, y_vals, c=tier_colors[tier], label=f'Tier {tier}', 
                          s=100, alpha=0.8, edgecolors='black')
        
        # Lignes de séparation des tiers
        ax.axhline(y=55, color='gold', linestyle='-', alpha=0.5, label='Tier S (55%+)')
        ax.axhline(y=52, color='silver', linestyle='-', alpha=0.5, label='Tier A (52%+)')
        ax.axhline(y=50, color='orange', linestyle='-', alpha=0.5, label='Tier B (50%+)')
        ax.axhline(y=45, color='lightcoral', linestyle='-', alpha=0.5, label='Tier C (45%+)')
        
        # Annotations
        for arch, stats in significant_archetypes.items():
            ax.annotate(arch, (stats['metagame_share'], stats['ci_lower']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_xlabel('Metagame Share (%)')
        ax.set_ylabel('CI Lower Bound (%)')
        ax.set_title('Tier Classification\n(Based on 95% CI Lower Bound)', fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('tier_classification_r_style.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Graphiques générés:")
        print("  - metagame_share_r_style.png")
        print("  - winrates_confidence_intervals_r_style.png") 
        print("  - winrate_vs_presence_r_style.png")
        print("  - tier_classification_r_style.png")
    
    def _generate_report(self):
        """Génère un rapport textuel dans le style R-Meta-Analysis"""
        print("\n" + "="*60)
        print("RAPPORT D'ANALYSE R-META-ANALYSIS")
        print("="*60)
        
        # Statistiques générales
        total_decks = len(self.deck_results)
        total_matches = sum(deck['matches'] for deck in self.deck_results)
        
        print(f"\n📊 STATISTIQUES GÉNÉRALES")
        print(f"Nombre total de decks analysés: {total_decks}")
        print(f"Nombre total de matches: {total_matches}")
        print(f"Nombre d'archétypes détectés: {len(self.archetype_stats)}")
        
        # Top archétypes par présence
        print(f"\n🏆 TOP ARCHÉTYPES PAR PRÉSENCE")
        top_presence = sorted(self.archetype_stats.items(), 
                            key=lambda x: x[1]['metagame_share'], reverse=True)[:10]
        
        for i, (archetype, stats) in enumerate(top_presence, 1):
            print(f"{i:2d}. {archetype:<20} {stats['metagame_share']:6.1f}% ({stats['deck_count']} decks)")
        
        # Top archétypes par winrate
        print(f"\n🎯 TOP ARCHÉTYPES PAR WINRATE")
        significant_archetypes = {k: v for k, v in self.archetype_stats.items() 
                                if v['deck_count'] >= 3 and k != "Unknown"}
        top_winrate = sorted(significant_archetypes.items(), 
                           key=lambda x: x[1]['winrate'], reverse=True)[:10]
        
        for i, (archetype, stats) in enumerate(top_winrate, 1):
            print(f"{i:2d}. {archetype:<20} {stats['winrate']:6.1f}% "
                  f"[{stats['ci_lower']:.1f}-{stats['ci_upper']:.1f}] "
                  f"({stats['total_matches']} matches)")
        
        # Classification par tiers
        print(f"\n🏅 CLASSIFICATION PAR TIERS")
        tiers = defaultdict(list)
        for archetype, stats in significant_archetypes.items():
            tiers[stats['tier']].append((archetype, stats))
        
        for tier in ['S', 'A', 'B', 'C', 'D']:
            if tier in tiers:
                print(f"\nTier {tier}:")
                for archetype, stats in sorted(tiers[tier], key=lambda x: x[1]['winrate'], reverse=True):
                    print(f"  • {archetype:<20} {stats['winrate']:6.1f}% "
                          f"[{stats['ci_lower']:.1f}-{stats['ci_upper']:.1f}] "
                          f"({stats['metagame_share']:.1f}% meta)")
        
        print(f"\n📈 MÉTHODOLOGIE")
        print("• Données sources: MTGODecklistCache (vraies données MTGO)")
        print("• Détection archétypes: MTGOArchetypeParser rules")
        print("• Intervalles de confiance: Méthode Wilson (95%)")
        print("• Classification tiers: Basée sur CI lower bound")
        print("• Filtrage: Archétypes avec ≥3 decks uniquement")
        
        print("\n" + "="*60)

def main():
    """Fonction principale - reproduction exacte R-Meta-Analysis"""
    analyzer = RMetaAnalysisReproducer()
    
    # Analyser les données Modern les plus récentes disponibles (juin 2024)
    # Note: MTGODecklistCache a été archivé, données jusqu'en juin 2024 seulement
    analyzer.analyze_tournaments(
        format_name="Modern",
        start_date="2024-06-01", 
        end_date="2024-06-30"
    )

if __name__ == "__main__":
    main() 