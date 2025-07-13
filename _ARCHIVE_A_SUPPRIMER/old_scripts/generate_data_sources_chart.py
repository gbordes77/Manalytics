#!/usr/bin/env python3
"""
Script pour générer le graphique en secteurs de la répartition des sources de données
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
    
    # Générer le graphique des sources de données
    print("Génération du graphique des sources de données...")
    fig = generator.create_data_sources_pie_chart(data)
    
    # Sauvegarder le graphique
    output_file = "analysis_output/data_sources_pie_chart.html"
    fig.write_html(output_file)
    print(f"Graphique sauvegardé: {output_file}")
    
    # Afficher les statistiques
    source_counts = {}
    for entry in data:
        source = entry.get('tournament_source', 'Unknown')
        if source not in source_counts:
            source_counts[source] = 0
        source_counts[source] += 1
    
    print("\nRépartition des sources de données:")
    total = sum(source_counts.values())
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"  {source}: {count} entrées ({percentage:.1f}%)")
    
    print(f"\nTotal: {total} entrées")

if __name__ == "__main__":
    main() 