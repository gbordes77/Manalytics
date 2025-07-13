#!/usr/bin/env python3
"""
Script pour générer le graphique d'évolution temporelle des archétypes Standard
"""

import json
import pandas as pd
from src.python.visualizations.metagame_charts import MetagameChartsGenerator

def main():
    # Charger les données
    print("Chargement des données...")
    with open('real_data/complete_dataset.json', 'r') as f:
        data = json.load(f)
    
    # Créer le générateur de graphiques
    generator = MetagameChartsGenerator()
    
    # Générer le graphique d'évolution temporelle
    print("Génération du graphique d'évolution temporelle...")
    fig = generator.create_archetype_evolution_chart(data)
    
    # Sauvegarder le graphique
    output_file = "analysis_output/archetype_evolution_chart.html"
    fig.write_html(output_file)
    print(f"Graphique sauvegardé: {output_file}")
    
    # Afficher les statistiques
    df = pd.DataFrame(data)
    df['tournament_date'] = pd.to_datetime(df['tournament_date'])
    df['date'] = df['tournament_date'].dt.date
    
    print("\nStatistiques par archétype:")
    archetype_stats = df['archetype'].value_counts()
    for arch, count in archetype_stats.items():
        print(f"  {arch}: {count} decks")
    
    print(f"\nPériode analysée: {df['date'].min()} à {df['date'].max()}")
    print(f"Nombre de jours: {len(df['date'].unique())}")
    
    # Statistiques par jour
    daily_stats = df.groupby('date').size()
    print(f"Moyenne de decks par jour: {daily_stats.mean():.1f}")
    print(f"Maximum de decks en une journée: {daily_stats.max()}")

if __name__ == "__main__":
    main() 