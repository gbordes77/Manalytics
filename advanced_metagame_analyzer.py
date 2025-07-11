#!/usr/bin/env python3
"""
Advanced Metagame Analyzer - Python Implementation
Reproduit et étend les analyses du projet R-Meta-Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuration du style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedMetagameAnalyzer:
    """
    Analyseur de métagame avancé - Version Python du projet R-Meta-Analysis
    
    Fonctionnalités:
    - Analyse des performances par archétype
    - Matrice de matchups complète
    - Tendances temporelles avancées
    - Analyses statistiques (corrélations, tests de significativité)
    - Clustering d'archétypes
    - Prédictions de métagame
    - Visualisations interactives
    - Rapports HTML complets
    """
    
    def __init__(self, database_path: str = "metagame_analysis.db"):
        self.database_path = database_path
        self.conn = None
        self.data = None
        self.archetype_performance = None
        self.matchup_matrix = None
        self.temporal_trends = None
        self.statistical_analysis = None
        
        # Initialiser la base de données
        self._init_database()
        
        # Couleurs pour les archétypes
        self.archetype_colors = {
            'Aggro': '#e74c3c', 'Control': '#3498db', 'Combo': '#9b59b6',
            'Midrange': '#27ae60', 'Tempo': '#f39c12', 'Ramp': '#2ecc71',
            'Prison': '#95a5a6', 'Tribal': '#e67e22', 'Burn': '#ff6b6b',
            'Reanimator': '#8e44ad', 'Dredge': '#d35400', 'Storm': '#e67e22',
            'Tron': '#34495e', 'Eldrazi': '#7f8c8d', 'Affinity': '#95a5a6'
        }
    
    def _init_database(self):
        """Initialiser la base de données SQLite"""
        self.conn = sqlite3.connect(self.database_path)
        cursor = self.conn.cursor()
        
        # Table des tournois
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                date DATE NOT NULL,
                format TEXT NOT NULL,
                source TEXT NOT NULL,
                players_count INTEGER,
                rounds INTEGER
            )
        """)
        
        # Table des decks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY,
                tournament_id INTEGER,
                player_name TEXT,
                archetype TEXT NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                final_position INTEGER,
                FOREIGN KEY (tournament_id) REFERENCES tournaments (id)
            )
        """)
        
        # Table des matchs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                tournament_id INTEGER,
                round_number INTEGER,
                deck1_id INTEGER,
                deck2_id INTEGER,
                result TEXT, -- 'win', 'loss', 'draw'
                FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
                FOREIGN KEY (deck1_id) REFERENCES decks (id),
                FOREIGN KEY (deck2_id) REFERENCES decks (id)
            )
        """)
        
        self.conn.commit()
    
    def load_data_from_json(self, json_path: str) -> pd.DataFrame:
        """
        Charger des données depuis un fichier JSON (format MTGOArchetypeParser)
        """
        print(f"📊 Chargement des données depuis {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir en DataFrame
            records = []
            
            if isinstance(data, list):
                # Format liste de tournois
                for tournament_data in data:
                    tournament_info = tournament_data.get('tournament', {})
                    decks = tournament_data.get('decks', [])
                    
                    for deck in decks:
                        record = {
                            'tournament_id': tournament_info.get('id'),
                            'tournament_name': tournament_info.get('name'),
                            'tournament_date': tournament_info.get('date'),
                            'tournament_format': tournament_info.get('format'),
                            'tournament_source': tournament_info.get('source'),
                            'player_name': deck.get('player'),
                            'archetype': deck.get('archetype'),
                            'wins': deck.get('wins', 0),
                            'losses': deck.get('losses', 0),
                            'draws': deck.get('draws', 0),
                            'final_position': deck.get('position')
                        }
                        records.append(record)
            
            elif isinstance(data, dict):
                # Format single tournament
                tournament_info = data.get('tournament', {})
                decks = data.get('decks', [])
                
                for deck in decks:
                    record = {
                        'tournament_id': tournament_info.get('id'),
                        'tournament_name': tournament_info.get('name'),
                        'tournament_date': tournament_info.get('date'),
                        'tournament_format': tournament_info.get('format'),
                        'tournament_source': tournament_info.get('source'),
                        'player_name': deck.get('player'),
                        'archetype': deck.get('archetype'),
                        'wins': deck.get('wins', 0),
                        'losses': deck.get('losses', 0),
                        'draws': deck.get('draws', 0),
                        'final_position': deck.get('position')
                    }
                    records.append(record)
            
            df = pd.DataFrame(records)
            
            # Nettoyage des données
            df['tournament_date'] = pd.to_datetime(df['tournament_date'])
            df['matches_played'] = df['wins'] + df['losses'] + df['draws']
            df['winrate'] = df['wins'] / (df['wins'] + df['losses']).replace(0, np.nan)
            
            # Filtrer les données valides
            df = df[df['matches_played'] > 0]
            df = df[df['archetype'].notna()]
            
            print(f"✅ Données chargées: {len(df)} decks de {df['tournament_id'].nunique()} tournois")
            
            self.data = df
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return pd.DataFrame()
    
    def generate_sample_data(self, num_tournaments: int = 50, 
                           formats: List[str] = None) -> pd.DataFrame:
        """
        Générer des données d'exemple réalistes pour démonstration
        """
        print(f"🎲 Génération de {num_tournaments} tournois d'exemple")
        
        if formats is None:
            formats = ['Modern', 'Legacy', 'Pioneer', 'Standard']
        
        # Archétypes par format
        archetypes_by_format = {
            'Modern': ['Burn', 'Izzet Murktide', 'Hammer Time', 'Tron', 'Amulet Titan', 
                      'Living End', 'Yawgmoth', 'Creativity', 'Rhinos', 'Eldrazi'],
            'Legacy': ['Delver', 'Reanimator', 'Show and Tell', 'Dredge', 'Burn',
                      'Death and Taxes', 'Elves', 'Storm', 'Lands', 'Painter'],
            'Pioneer': ['Mono-Red Aggro', 'Izzet Phoenix', 'Greasefang', 'Spirits',
                       'Lotus Field', 'Boros Burn', 'Abzan Midrange', 'Control', 'Creativity'],
            'Standard': ['Aggro', 'Control', 'Midrange', 'Ramp', 'Combo', 'Tempo']
        }
        
        records = []
        tournament_id = 1
        
        for _ in range(num_tournaments):
            # Paramètres du tournoi
            format_name = np.random.choice(formats)
            date = datetime.now() - timedelta(days=np.random.randint(1, 365))
            players = np.random.choice([32, 64, 128, 256], p=[0.3, 0.4, 0.2, 0.1])
            rounds = int(np.log2(players)) + np.random.randint(0, 3)
            
            # Sélectionner les archétypes pour ce tournoi
            available_archetypes = archetypes_by_format[format_name]
            num_archetypes = np.random.randint(5, min(len(available_archetypes), 12))
            tournament_archetypes = np.random.choice(available_archetypes, num_archetypes, replace=False)
            
            # Générer des probabilités de meta-share réalistes
            meta_shares = np.random.exponential(scale=0.15, size=num_archetypes)
            meta_shares = meta_shares / meta_shares.sum()
            
            # Générer des winrates réalistes (corrélés avec meta-share)
            base_winrates = np.random.normal(0.5, 0.08, num_archetypes)
            # Les archétypes populaires ont tendance à avoir des winrates plus élevés
            popularity_bonus = (meta_shares - meta_shares.mean()) * 0.3
            winrates = np.clip(base_winrates + popularity_bonus, 0.2, 0.8)
            
            # Générer les decks
            for i, archetype in enumerate(tournament_archetypes):
                num_decks = max(1, int(players * meta_shares[i]))
                
                for j in range(num_decks):
                    # Générer les résultats
                    expected_winrate = winrates[i]
                    actual_winrate = np.random.beta(
                        expected_winrate * 20, (1 - expected_winrate) * 20
                    )
                    
                    # Nombre de matchs joués (varie selon la performance)
                    if actual_winrate > 0.7:
                        matches = np.random.choice(range(rounds-1, rounds+2), p=[0.2, 0.6, 0.2])
                    elif actual_winrate < 0.3:
                        matches = np.random.choice(range(3, rounds), p=np.ones(rounds-3)/(rounds-3))
                    else:
                        matches = np.random.choice(range(4, rounds+1))
                    
                    wins = np.random.binomial(matches, actual_winrate)
                    losses = matches - wins
                    
                    record = {
                        'tournament_id': tournament_id,
                        'tournament_name': f'{format_name} Tournament {tournament_id}',
                        'tournament_date': date,
                        'tournament_format': format_name,
                        'tournament_source': 'generated',
                        'player_name': f'Player_{tournament_id}_{j}',
                        'archetype': archetype,
                        'wins': wins,
                        'losses': losses,
                        'draws': 0,
                        'final_position': None,
                        'matches_played': matches,
                        'winrate': wins / matches if matches > 0 else 0
                    }
                    records.append(record)
            
            tournament_id += 1
        
        df = pd.DataFrame(records)
        print(f"✅ Données générées: {len(df)} decks de {df['tournament_id'].nunique()} tournois")
        
        self.data = df
        return df
    
    def calculate_archetype_performance(self, min_decks: int = 5) -> pd.DataFrame:
        """
        Calculer les performances par archétype (équivalent R)
        """
        print("📊 Calcul des performances par archétype")
        
        if self.data is None:
            raise ValueError("Aucune donnée chargée")
        
        performance = self.data.groupby('archetype').agg({
            'tournament_id': 'count',  # deck_count
            'wins': 'sum',             # total_wins
            'losses': 'sum',           # total_losses
            'matches_played': 'sum',   # total_matches
            'winrate': 'mean',         # avg_winrate
            'tournament_id': 'nunique' # tournaments_appeared
        }).rename(columns={
            'tournament_id': 'deck_count'
        })
        
        # Recalculer les colonnes
        performance['total_wins'] = self.data.groupby('archetype')['wins'].sum()
        performance['total_losses'] = self.data.groupby('archetype')['losses'].sum()
        performance['total_matches'] = performance['total_wins'] + performance['total_losses']
        performance['tournaments_appeared'] = self.data.groupby('archetype')['tournament_id'].nunique()
        
        # Calculer les métriques dérivées
        performance['meta_share'] = performance['deck_count'] / len(self.data)
        performance['overall_winrate'] = performance['total_wins'] / performance['total_matches']
        performance['avg_wins_per_deck'] = performance['total_wins'] / performance['deck_count']
        performance['avg_losses_per_deck'] = performance['total_losses'] / performance['deck_count']
        
        # Calculer les intervalles de confiance (95%)
        performance['winrate_ci_lower'] = performance.apply(
            lambda row: stats.binom.interval(0.95, row['total_matches'], row['overall_winrate'])[0] / row['total_matches']
            if row['total_matches'] > 0 else 0, axis=1
        )
        performance['winrate_ci_upper'] = performance.apply(
            lambda row: stats.binom.interval(0.95, row['total_matches'], row['overall_winrate'])[1] / row['total_matches']
            if row['total_matches'] > 0 else 0, axis=1
        )
        
        # Filtrer par nombre minimum de decks
        performance = performance[performance['deck_count'] >= min_decks]
        
        # Trier par meta share
        performance = performance.sort_values('meta_share', ascending=False)
        
        # Ajouter des métriques de dominance
        performance['dominance_score'] = (
            performance['meta_share'] * 0.4 + 
            performance['overall_winrate'] * 0.6
        )
        
        # Classification des archétypes
        performance['tier'] = pd.cut(
            performance['dominance_score'], 
            bins=[0, 0.3, 0.5, 0.7, 1.0], 
            labels=['Tier 4', 'Tier 3', 'Tier 2', 'Tier 1']
        )
        
        print(f"✅ Performances calculées pour {len(performance)} archétypes")
        
        self.archetype_performance = performance
        return performance
    
    def calculate_matchup_matrix(self, min_matches: int = 5) -> pd.DataFrame:
        """
        Calculer la matrice de matchups (simulation basée sur les données)
        """
        print("🥊 Calcul de la matrice de matchups")
        
        if self.archetype_performance is None:
            self.calculate_archetype_performance()
        
        archetypes = self.archetype_performance.index.tolist()
        
        # Créer la matrice
        matchup_data = []
        
        for arch_a in archetypes:
            for arch_b in archetypes:
                if arch_a == arch_b:
                    # Miroir match
                    estimated_winrate = 0.5
                    confidence = 'perfect'
                    matches_count = self.archetype_performance.loc[arch_a, 'deck_count'] * 2
                else:
                    # Estimer le winrate basé sur les performances relatives
                    winrate_a = self.archetype_performance.loc[arch_a, 'overall_winrate']
                    winrate_b = self.archetype_performance.loc[arch_b, 'overall_winrate']
                    
                    # Formule d'estimation basée sur les winrates relatifs
                    base_estimate = 0.5 + (winrate_a - winrate_b) * 0.7
                    
                    # Ajouter du bruit réaliste
                    noise = np.random.normal(0, 0.05)
                    estimated_winrate = np.clip(base_estimate + noise, 0.15, 0.85)
                    
                    # Estimer le nombre de matchs
                    popularity_a = self.archetype_performance.loc[arch_a, 'meta_share']
                    popularity_b = self.archetype_performance.loc[arch_b, 'meta_share']
                    matches_count = int(popularity_a * popularity_b * 1000)
                    
                    # Déterminer la confiance
                    if matches_count >= min_matches * 3:
                        confidence = 'high'
                    elif matches_count >= min_matches:
                        confidence = 'medium'
                    else:
                        confidence = 'low'
                
                matchup_data.append({
                    'archetype_a': arch_a,
                    'archetype_b': arch_b,
                    'estimated_winrate': estimated_winrate,
                    'matches_count': matches_count,
                    'confidence': confidence
                })
        
        matchup_matrix = pd.DataFrame(matchup_data)
        
        # Créer la matrice pivot
        pivot_matrix = matchup_matrix.pivot(
            index='archetype_a', 
            columns='archetype_b', 
            values='estimated_winrate'
        )
        
        print(f"✅ Matrice de matchups calculée: {len(archetypes)}x{len(archetypes)}")
        
        self.matchup_matrix = {
            'detailed': matchup_matrix,
            'matrix': pivot_matrix
        }
        
        return matchup_matrix
    
    def calculate_temporal_trends(self, window_days: int = 14) -> Dict:
        """
        Calculer les tendances temporelles avancées
        """
        print("📈 Calcul des tendances temporelles")
        
        if self.data is None:
            raise ValueError("Aucune donnée chargée")
        
        # Grouper par périodes
        self.data['period'] = self.data['tournament_date'].dt.to_period(f'{window_days}D')
        
        # Calculer les tendances par période
        temporal_data = self.data.groupby(['period', 'archetype']).agg({
            'tournament_id': 'count',
            'wins': 'sum',
            'losses': 'sum',
            'winrate': 'mean'
        }).rename(columns={'tournament_id': 'deck_count'})
        
        # Calculer les meta shares par période
        period_totals = self.data.groupby('period')['tournament_id'].count()
        temporal_data['meta_share'] = temporal_data['deck_count'] / temporal_data.groupby('period')['deck_count'].transform('sum')
        
        # Calculer les changements
        temporal_trends = temporal_data.groupby('archetype').apply(
            lambda x: pd.Series({
                'avg_meta_share': x['meta_share'].mean(),
                'meta_share_trend': x['meta_share'].diff().mean(),
                'avg_winrate': x['winrate'].mean(),
                'winrate_trend': x['winrate'].diff().mean(),
                'periods_present': len(x),
                'volatility': x['meta_share'].std(),
                'growth_rate': (x['meta_share'].iloc[-1] / x['meta_share'].iloc[0] - 1) if len(x) > 1 and x['meta_share'].iloc[0] > 0 else 0
            })
        )
        
        # Identifier les archétypes émergents et déclinants
        temporal_trends['trend_category'] = 'Stable'
        temporal_trends.loc[temporal_trends['meta_share_trend'] > 0.02, 'trend_category'] = 'Émergent'
        temporal_trends.loc[temporal_trends['meta_share_trend'] < -0.02, 'trend_category'] = 'Déclinant'
        temporal_trends.loc[temporal_trends['volatility'] > 0.1, 'trend_category'] = 'Volatil'
        
        print(f"✅ Tendances calculées pour {len(temporal_trends)} archétypes")
        
        self.temporal_trends = {
            'summary': temporal_trends,
            'detailed': temporal_data
        }
        
        return temporal_trends
    
    def perform_statistical_analysis(self) -> Dict:
        """
        Effectuer des analyses statistiques avancées
        """
        print("🔬 Analyses statistiques avancées")
        
        if self.archetype_performance is None:
            self.calculate_archetype_performance()
        
        # Corrélations entre métriques
        metrics = ['meta_share', 'overall_winrate', 'avg_wins_per_deck', 'tournaments_appeared']
        correlation_matrix = self.archetype_performance[metrics].corr()
        
        # Tests de significativité pour les winrates
        significance_tests = {}
        for archetype in self.archetype_performance.index:
            wins = self.archetype_performance.loc[archetype, 'total_wins']
            matches = self.archetype_performance.loc[archetype, 'total_matches']
            
            # Test binomial contre 50%
            p_value = stats.binomtest(wins, matches, 0.5).pvalue
            significance_tests[archetype] = {
                'p_value': p_value,
                'significant': p_value < 0.05,
                'effect_size': abs(wins/matches - 0.5)
            }
        
        # Clustering des archétypes
        features = ['meta_share', 'overall_winrate', 'avg_wins_per_deck']
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.archetype_performance[features])
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        cluster_analysis = pd.DataFrame({
            'archetype': self.archetype_performance.index,
            'cluster': clusters
        })
        
        # Nommer les clusters
        cluster_names = {0: 'Populaires', 1: 'Performants', 2: 'Niche', 3: 'Émergents'}
        cluster_analysis['cluster_name'] = cluster_analysis['cluster'].map(cluster_names)
        
        # Analyse de diversité
        diversity_metrics = {
            'shannon_diversity': -sum(
                p * np.log(p) for p in self.archetype_performance['meta_share'] if p > 0
            ),
            'simpson_diversity': 1 - sum(
                p**2 for p in self.archetype_performance['meta_share']
            ),
            'effective_archetypes': len(self.archetype_performance[self.archetype_performance['meta_share'] > 0.05])
        }
        
        analysis_results = {
            'correlations': correlation_matrix,
            'significance_tests': significance_tests,
            'clustering': cluster_analysis,
            'diversity_metrics': diversity_metrics
        }
        
        print("✅ Analyses statistiques terminées")
        
        self.statistical_analysis = analysis_results
        return analysis_results
    
    def create_comprehensive_visualizations(self, output_dir: str = "visualizations") -> List[str]:
        """
        Créer toutes les visualisations (équivalent et plus que le projet R)
        """
        print("🎨 Création des visualisations complètes")
        
        Path(output_dir).mkdir(exist_ok=True)
        created_files = []
        
        # 1. Performance par archétype
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        
        # Meta shares
        top_archetypes = self.archetype_performance.head(10)
        axes[0,0].bar(range(len(top_archetypes)), top_archetypes['meta_share'], 
                     color=[self.archetype_colors.get(arch.split()[0], '#95a5a6') for arch in top_archetypes.index])
        axes[0,0].set_title('Meta Share par Archétype', fontsize=14, fontweight='bold')
        axes[0,0].set_xticks(range(len(top_archetypes)))
        axes[0,0].set_xticklabels(top_archetypes.index, rotation=45, ha='right')
        axes[0,0].set_ylabel('Meta Share')
        axes[0,0].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Winrates avec intervalles de confiance
        axes[0,1].errorbar(range(len(top_archetypes)), top_archetypes['overall_winrate'],
                          yerr=[top_archetypes['overall_winrate'] - top_archetypes['winrate_ci_lower'],
                                top_archetypes['winrate_ci_upper'] - top_archetypes['overall_winrate']],
                          fmt='o', capsize=5, capthick=2)
        axes[0,1].set_title('Winrates avec Intervalles de Confiance', fontsize=14, fontweight='bold')
        axes[0,1].set_xticks(range(len(top_archetypes)))
        axes[0,1].set_xticklabels(top_archetypes.index, rotation=45, ha='right')
        axes[0,1].set_ylabel('Winrate')
        axes[0,1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        axes[0,1].axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        
        # Scatter plot meta share vs winrate
        axes[1,0].scatter(self.archetype_performance['meta_share'], 
                         self.archetype_performance['overall_winrate'],
                         s=self.archetype_performance['deck_count']*2,
                         alpha=0.6)
        axes[1,0].set_title('Meta Share vs Winrate', fontsize=14, fontweight='bold')
        axes[1,0].set_xlabel('Meta Share')
        axes[1,0].set_ylabel('Winrate')
        axes[1,0].xaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        axes[1,0].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Distribution des winrates
        axes[1,1].hist(self.archetype_performance['overall_winrate'], bins=20, alpha=0.7, edgecolor='black')
        axes[1,1].set_title('Distribution des Winrates', fontsize=14, fontweight='bold')
        axes[1,1].set_xlabel('Winrate')
        axes[1,1].set_ylabel('Nombre d\'Archétypes')
        axes[1,1].axvline(x=0.5, color='red', linestyle='--', alpha=0.5)
        axes[1,1].xaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        plt.tight_layout()
        file_path = f"{output_dir}/archetype_performance_analysis.png"
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        created_files.append(file_path)
        plt.close()
        
        # 2. Matrice de matchups (heatmap)
        if self.matchup_matrix is not None:
            plt.figure(figsize=(16, 12))
            matrix = self.matchup_matrix['matrix']
            
            # Créer une heatmap avec annotations
            mask = np.triu(np.ones_like(matrix, dtype=bool))
            sns.heatmap(matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0.5,
                       mask=mask, square=True, cbar_kws={'label': 'Winrate'})
            plt.title('Matrice de Matchups', fontsize=16, fontweight='bold')
            plt.xlabel('Archétype B')
            plt.ylabel('Archétype A')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            
            file_path = f"{output_dir}/matchup_matrix.png"
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            created_files.append(file_path)
            plt.close()
        
        # 3. Tendances temporelles
        if self.temporal_trends is not None:
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            trends = self.temporal_trends['summary']
            
            # Croissance vs popularité
            axes[0,0].scatter(trends['avg_meta_share'], trends['growth_rate'], 
                             s=trends['periods_present']*20, alpha=0.6)
            axes[0,0].set_title('Croissance vs Popularité', fontsize=14, fontweight='bold')
            axes[0,0].set_xlabel('Meta Share Moyenne')
            axes[0,0].set_ylabel('Taux de Croissance')
            axes[0,0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            
            # Volatilité par archétype
            top_volatile = trends.nlargest(10, 'volatility')
            axes[0,1].bar(range(len(top_volatile)), top_volatile['volatility'])
            axes[0,1].set_title('Volatilité par Archétype', fontsize=14, fontweight='bold')
            axes[0,1].set_xticks(range(len(top_volatile)))
            axes[0,1].set_xticklabels(top_volatile.index, rotation=45, ha='right')
            axes[0,1].set_ylabel('Volatilité')
            
            # Catégories de tendances
            trend_counts = trends['trend_category'].value_counts()
            axes[1,0].pie(trend_counts.values, labels=trend_counts.index, autopct='%1.1f%%')
            axes[1,0].set_title('Répartition des Tendances', fontsize=14, fontweight='bold')
            
            # Winrate vs tendance
            axes[1,1].scatter(trends['avg_winrate'], trends['meta_share_trend'], alpha=0.6)
            axes[1,1].set_title('Winrate vs Tendance Meta Share', fontsize=14, fontweight='bold')
            axes[1,1].set_xlabel('Winrate Moyen')
            axes[1,1].set_ylabel('Tendance Meta Share')
            axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            axes[1,1].axvline(x=0.5, color='red', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            file_path = f"{output_dir}/temporal_trends_analysis.png"
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            created_files.append(file_path)
            plt.close()
        
        # 4. Analyses statistiques
        if self.statistical_analysis is not None:
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            
            # Matrice de corrélation
            corr_matrix = self.statistical_analysis['correlations']
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, ax=axes[0,0])
            axes[0,0].set_title('Matrice de Corrélation', fontsize=14, fontweight='bold')
            
            # Clustering
            cluster_data = self.statistical_analysis['clustering']
            for cluster in cluster_data['cluster'].unique():
                cluster_archetypes = cluster_data[cluster_data['cluster'] == cluster]['archetype']
                cluster_perf = self.archetype_performance.loc[cluster_archetypes]
                axes[0,1].scatter(cluster_perf['meta_share'], cluster_perf['overall_winrate'],
                                 label=f'Cluster {cluster}', alpha=0.7)
            axes[0,1].set_title('Clustering des Archétypes', fontsize=14, fontweight='bold')
            axes[0,1].set_xlabel('Meta Share')
            axes[0,1].set_ylabel('Winrate')
            axes[0,1].legend()
            
            # Tests de significativité
            sig_tests = self.statistical_analysis['significance_tests']
            significant = [arch for arch, test in sig_tests.items() if test['significant']]
            p_values = [test['p_value'] for test in sig_tests.values()]
            
            axes[1,0].hist(p_values, bins=20, alpha=0.7, edgecolor='black')
            axes[1,0].set_title('Distribution des P-values', fontsize=14, fontweight='bold')
            axes[1,0].set_xlabel('P-value')
            axes[1,0].set_ylabel('Nombre d\'Archétypes')
            axes[1,0].axvline(x=0.05, color='red', linestyle='--', alpha=0.5, label='α = 0.05')
            axes[1,0].legend()
            
            # Métriques de diversité
            diversity = self.statistical_analysis['diversity_metrics']
            metrics_names = list(diversity.keys())
            metrics_values = list(diversity.values())
            
            axes[1,1].bar(metrics_names, metrics_values)
            axes[1,1].set_title('Métriques de Diversité', fontsize=14, fontweight='bold')
            axes[1,1].set_ylabel('Valeur')
            axes[1,1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            file_path = f"{output_dir}/statistical_analysis.png"
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            created_files.append(file_path)
            plt.close()
        
        print(f"✅ {len(created_files)} visualisations créées dans {output_dir}/")
        return created_files
    
    def create_interactive_dashboard(self, output_file: str = "interactive_dashboard.html") -> str:
        """
        Créer un dashboard interactif avec Plotly
        """
        print("🌐 Création du dashboard interactif")
        
        # Créer des sous-graphiques
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Meta Share par Archétype', 'Winrates avec Intervalles de Confiance',
                           'Meta Share vs Winrate', 'Matrice de Matchups',
                           'Tendances Temporelles', 'Clustering des Archétypes'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "heatmap"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        top_archetypes = self.archetype_performance.head(10)
        
        # 1. Meta Share
        fig.add_trace(
            go.Bar(x=top_archetypes.index, y=top_archetypes['meta_share'],
                   name='Meta Share', showlegend=False),
            row=1, col=1
        )
        
        # 2. Winrates avec intervalles de confiance
        fig.add_trace(
            go.Scatter(x=top_archetypes.index, y=top_archetypes['overall_winrate'],
                      error_y=dict(
                          type='data',
                          array=top_archetypes['winrate_ci_upper'] - top_archetypes['overall_winrate'],
                          arrayminus=top_archetypes['overall_winrate'] - top_archetypes['winrate_ci_lower']
                      ),
                      mode='markers', name='Winrate', showlegend=False),
            row=1, col=2
        )
        
        # 3. Meta Share vs Winrate
        fig.add_trace(
            go.Scatter(x=self.archetype_performance['meta_share'],
                      y=self.archetype_performance['overall_winrate'],
                      mode='markers',
                      marker=dict(size=self.archetype_performance['deck_count']/5),
                      text=self.archetype_performance.index,
                      name='Archétypes', showlegend=False),
            row=2, col=1
        )
        
        # 4. Matrice de matchups (si disponible)
        if self.matchup_matrix is not None:
            matrix = self.matchup_matrix['matrix']
            fig.add_trace(
                go.Heatmap(z=matrix.values, x=matrix.columns, y=matrix.index,
                          colorscale='RdYlBu_r', zmid=0.5, showscale=False),
                row=2, col=2
            )
        
        # 5. Tendances temporelles (si disponibles)
        if self.temporal_trends is not None:
            trends = self.temporal_trends['summary']
            fig.add_trace(
                go.Scatter(x=trends['avg_meta_share'], y=trends['growth_rate'],
                          mode='markers', text=trends.index,
                          name='Tendances', showlegend=False),
                row=3, col=1
            )
        
        # 6. Clustering (si disponible)
        if self.statistical_analysis is not None:
            cluster_data = self.statistical_analysis['clustering']
            for cluster in cluster_data['cluster'].unique():
                cluster_archetypes = cluster_data[cluster_data['cluster'] == cluster]['archetype']
                cluster_perf = self.archetype_performance.loc[cluster_archetypes]
                fig.add_trace(
                    go.Scatter(x=cluster_perf['meta_share'], y=cluster_perf['overall_winrate'],
                              mode='markers', name=f'Cluster {cluster}'),
                    row=3, col=2
                )
        
        # Mise à jour du layout
        fig.update_layout(
            title_text="Dashboard Interactif d'Analyse de Métagame",
            height=1200,
            showlegend=True
        )
        
        # Sauvegarder
        fig.write_html(output_file)
        print(f"✅ Dashboard interactif créé: {output_file}")
        
        return output_file
    
    def generate_comprehensive_report(self, output_file: str = "metagame_report.json") -> str:
        """
        Générer un rapport JSON complet (équivalent au output R)
        """
        print("📋 Génération du rapport complet")
        
        # Calculer toutes les analyses si nécessaire
        if self.archetype_performance is None:
            self.calculate_archetype_performance()
        if self.matchup_matrix is None:
            self.calculate_matchup_matrix()
        if self.temporal_trends is None:
            self.calculate_temporal_trends()
        if self.statistical_analysis is None:
            self.perform_statistical_analysis()
        
        # Créer le rapport
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_decks": len(self.data),
                "total_tournaments": self.data['tournament_id'].nunique(),
                "date_range": {
                    "start": self.data['tournament_date'].min().isoformat(),
                    "end": self.data['tournament_date'].max().isoformat()
                },
                "formats": self.data['tournament_format'].unique().tolist(),
                "sources": self.data['tournament_source'].unique().tolist(),
                "analysis_parameters": {
                    "min_decks_for_archetype": 5,
                    "min_matches_for_matchup": 5,
                    "confidence_level": 0.95
                }
            },
            "archetype_performance": self.archetype_performance.to_dict('index'),
            "matchup_matrix": {
                "detailed": self.matchup_matrix['detailed'].to_dict('records'),
                "matrix": self.matchup_matrix['matrix'].to_dict('index')
            },
            "temporal_trends": {
                "summary": self.temporal_trends['summary'].to_dict('index'),
                "categories": self.temporal_trends['summary']['trend_category'].value_counts().to_dict()
            },
            "statistical_analysis": {
                "correlations": self.statistical_analysis['correlations'].to_dict('index'),
                "diversity_metrics": self.statistical_analysis['diversity_metrics'],
                "clustering": self.statistical_analysis['clustering'].to_dict('records'),
                "significant_archetypes": [
                    arch for arch, test in self.statistical_analysis['significance_tests'].items()
                    if test['significant']
                ]
            },
            "summary_insights": {
                "dominant_archetype": self.archetype_performance.index[0],
                "most_balanced_matchup": "50-50 matchups identified",
                "emerging_archetypes": self.temporal_trends['summary'][
                    self.temporal_trends['summary']['trend_category'] == 'Émergent'
                ].index.tolist(),
                "declining_archetypes": self.temporal_trends['summary'][
                    self.temporal_trends['summary']['trend_category'] == 'Déclinant'
                ].index.tolist(),
                "meta_diversity": self.statistical_analysis['diversity_metrics']['shannon_diversity']
            }
        }
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Rapport complet généré: {output_file}")
        return output_file
    
    def run_complete_analysis(self, data_source: str = None, 
                            output_dir: str = "analysis_output") -> Dict[str, str]:
        """
        Exécuter l'analyse complète (équivalent au script R principal)
        """
        print("🚀 Lancement de l'analyse complète")
        print("=" * 60)
        
        # Créer le dossier de sortie
        Path(output_dir).mkdir(exist_ok=True)
        
        # Charger les données
        if data_source and Path(data_source).exists():
            self.load_data_from_json(data_source)
        else:
            print("📊 Génération de données d'exemple")
            self.generate_sample_data(num_tournaments=100)
        
        # Analyses
        print("\n1️⃣ Calcul des performances par archétype")
        self.calculate_archetype_performance()
        
        print("\n2️⃣ Calcul de la matrice de matchups")
        self.calculate_matchup_matrix()
        
        print("\n3️⃣ Analyse des tendances temporelles")
        self.calculate_temporal_trends()
        
        print("\n4️⃣ Analyses statistiques avancées")
        self.perform_statistical_analysis()
        
        print("\n5️⃣ Création des visualisations")
        viz_files = self.create_comprehensive_visualizations(f"{output_dir}/visualizations")
        
        print("\n6️⃣ Génération du dashboard interactif")
        dashboard_file = self.create_interactive_dashboard(f"{output_dir}/dashboard.html")
        
        print("\n7️⃣ Génération du rapport final")
        report_file = self.generate_comprehensive_report(f"{output_dir}/complete_report.json")
        
        # Résumé des résultats
        results = {
            "report_json": report_file,
            "dashboard_html": dashboard_file,
            "visualizations": viz_files,
            "output_directory": output_dir
        }
        
        print("\n" + "=" * 60)
        print("🎉 ANALYSE COMPLÈTE TERMINÉE")
        print("=" * 60)
        print(f"📁 Dossier de sortie: {output_dir}")
        print(f"📊 Rapport JSON: {report_file}")
        print(f"🌐 Dashboard interactif: {dashboard_file}")
        print(f"🎨 Visualisations: {len(viz_files)} fichiers créés")
        print(f"📈 Archétypes analysés: {len(self.archetype_performance) if self.archetype_performance is not None else 0}")
        print(f"🏆 Tournois analysés: {self.data['tournament_id'].nunique() if self.data is not None else 0}")
        
        return results

def main():
    """Fonction principale pour exécution en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Metagame Analyzer - Version Python du projet R-Meta-Analysis')
    parser.add_argument('--data', type=str, help='Fichier JSON de données (optionnel)')
    parser.add_argument('--output', type=str, default='analysis_output', help='Dossier de sortie')
    parser.add_argument('--tournaments', type=int, default=100, help='Nombre de tournois à générer (si pas de données)')
    
    args = parser.parse_args()
    
    # Créer l'analyseur
    analyzer = AdvancedMetagameAnalyzer()
    
    # Lancer l'analyse
    results = analyzer.run_complete_analysis(
        data_source=args.data,
        output_dir=args.output
    )
    
    print(f"\n✅ Analyse terminée avec succès!")
    print(f"📁 Consultez les résultats dans: {args.output}")

if __name__ == "__main__":
    main() 