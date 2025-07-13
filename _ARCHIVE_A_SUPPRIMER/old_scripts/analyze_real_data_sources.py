#!/usr/bin/env python3
"""
Script pour analyser la répartition réelle des sources de données
"""

import os
import json
from pathlib import Path
from src.python.visualizations.metagame_charts import MetagameChartsGenerator
import plotly.graph_objects as go

def analyze_tournament_cache():
    """Analyse la répartition des sources dans le cache de tournois"""
    cache_dir = Path("MTGODecklistCache/Tournaments")
    
    source_counts = {}
    tournament_counts = {}
    
    # Parcourir tous les répertoires de sources
    for source_dir in cache_dir.iterdir():
        if source_dir.is_dir():
            source_name = source_dir.name
            source_counts[source_name] = 0
            tournament_counts[source_name] = 0
            
            # Compter les fichiers JSON (tournois)
            for json_file in source_dir.rglob("*.json"):
                tournament_counts[source_name] += 1
                
                # Essayer de lire le fichier pour compter les participants
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'Decks' in data:
                            source_counts[source_name] += len(data['Decks'])
                        else:
                            source_counts[source_name] += 1
                except:
                    source_counts[source_name] += 1
    
    return source_counts, tournament_counts

def create_enhanced_pie_chart(source_counts, tournament_counts):
    """Crée un graphique en secteurs amélioré"""
    
    # Mapper les sources vers des noms d'affichage
    source_mapping = {
        'mtgo.com': 'MTGO',
        'melee.gg': 'Melee.gg',
        'topdeck.gg': 'TopDeck.gg',
        'manatraders.com': 'Manatraders',
        'mtgo.com_limited_data': 'MTGO Limited'
    }
    
    # Préparer les données
    labels = []
    values = []
    hover_text = []
    colors = ['#FFD700', '#6495ED', '#9932CC', '#FF6347', '#32CD32', '#FF69B4', '#20B2AA', '#FFA500']
    
    total_decks = sum(source_counts.values())
    
    for source, deck_count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        display_name = source_mapping.get(source, source)
        labels.append(display_name)
        values.append(deck_count)
        
        tournament_count = tournament_counts.get(source, 0)
        percentage = (deck_count / total_decks) * 100
        hover_text.append(f"{display_name}<br>Decks: {deck_count:,}<br>Tournois: {tournament_count:,}<br>Pourcentage: {percentage:.1f}%")
    
    # Créer le graphique
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=colors[:len(labels)], line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='%{text}<extra></extra>',
        text=hover_text,
        textfont=dict(size=12)
    )])
    
    fig.update_layout(
        title={
            'text': 'Répartition des Sources de Données<br><sub>Basé sur les données historiques du cache</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        font=dict(size=14),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=12)
        ),
        margin=dict(l=20, r=150, t=80, b=20),
        width=900,
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def main():
    print("Analyse des sources de données du cache...")
    
    # Analyser le cache
    source_counts, tournament_counts = analyze_tournament_cache()
    
    # Afficher les statistiques
    print("\nRépartition des sources de données:")
    print("=" * 50)
    
    total_decks = sum(source_counts.values())
    total_tournaments = sum(tournament_counts.values())
    
    for source, deck_count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        tournament_count = tournament_counts.get(source, 0)
        percentage = (deck_count / total_decks) * 100
        print(f"{source:20} : {deck_count:6,} decks ({percentage:5.1f}%) - {tournament_count:4,} tournois")
    
    print("=" * 50)
    print(f"{'TOTAL':20} : {total_decks:6,} decks (100.0%) - {total_tournaments:4,} tournois")
    
    # Créer le graphique
    if total_decks > 0:
        print("\nGénération du graphique...")
        fig = create_enhanced_pie_chart(source_counts, tournament_counts)
        
        # Sauvegarder
        output_file = "analysis_output/real_data_sources_distribution.html"
        fig.write_html(output_file)
        print(f"Graphique sauvegardé: {output_file}")
    else:
        print("Aucune donnée trouvée dans le cache.")

if __name__ == "__main__":
    main() 