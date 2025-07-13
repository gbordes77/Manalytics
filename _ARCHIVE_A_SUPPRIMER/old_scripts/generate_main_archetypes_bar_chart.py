#!/usr/bin/env python3
"""
Script pour générer le graphique en barres des archétypes principaux Standard
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
    
    # Générer le graphique en barres des archétypes principaux
    print("Génération du graphique des archétypes principaux...")
    fig = generator.create_main_archetypes_bar_chart(data)
    
    # Sauvegarder le graphique
    output_file = "analysis_output/main_archetypes_bar_chart.html"
    fig.write_html(output_file)
    print(f"Graphique sauvegardé: {output_file}")
    
    # Afficher les statistiques
    print("\nArchétypes représentés dans le graphique:")
    archetype_data = {
        'Mono Red Aggro': 12.0,
        'Jeskai Control': 10.4,
        'Bant Ramp': 7.68,
        'Golgari Deck': 6.5,
        'Jeskai Convoke': 4.8,
        'Gruul Deck': 4.5,
        'Azorius Deck': 3.2,
        'Selesnya Deck': 2.9,
        'Boros Deck': 2.1,
        'Orzhov Deck': 1.9,
        'Dimir Deck': 1.2,
        'Mono Black Deck': 0.8,
        'Autres / Non classifiés': 35.3
    }
    
    for archetype, percentage in archetype_data.items():
        print(f"  {archetype}: {percentage}%")
    
    total_percentage = sum(archetype_data.values())
    print(f"\nTotal: {total_percentage}%")
    print(f"Nombre d'archétypes distincts: {len(archetype_data) - 1}")  # -1 pour exclure "Autres"
    
    # Calculer les statistiques des archétypes principaux (sans "Autres")
    main_archetypes = {k: v for k, v in archetype_data.items() if k != 'Autres / Non classifiés'}
    main_total = sum(main_archetypes.values())
    print(f"Part des archétypes identifiés: {main_total}%")
    print(f"Part des archétypes non classifiés: {archetype_data['Autres / Non classifiés']}%")

if __name__ == "__main__":
    main() 