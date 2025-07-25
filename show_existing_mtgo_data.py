#!/usr/bin/env python3
"""
Affiche les données MTGO existantes pour juillet 2025
"""

import json
import os
from datetime import datetime

def show_mtgo_data():
    mtgo_dir = "data/raw/mtgo/standard"
    
    print("=== Données MTGO Standard existantes (Juillet 2025) ===\n")
    
    # Lister tous les fichiers
    files = sorted([f for f in os.listdir(mtgo_dir) if f.startswith("2025-07")])
    
    print(f"Total: {len(files)} tournois MTGO trouvés\n")
    
    # Analyser quelques tournois
    total_decks = 0
    tournaments_by_type = {}
    
    for filename in files:
        filepath = os.path.join(mtgo_dir, filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Extraire le type de tournoi
        if "league" in filename:
            tournament_type = "League"
        elif "challenge_64" in filename:
            tournament_type = "Challenge 64"
        elif "challenge_32" in filename:
            tournament_type = "Challenge 32"
        elif "rc_qualifier" in filename:
            tournament_type = "RC Qualifier"
        else:
            tournament_type = "Other"
            
        tournaments_by_type[tournament_type] = tournaments_by_type.get(tournament_type, 0) + 1
        
        # Compter les decks
        num_decks = len(data.get("decks", []))
        total_decks += num_decks
        
        # Afficher les 5 premiers
        if len(files) <= 5 or files.index(filename) < 5:
            date = filename.split('_')[0]
            print(f"📄 {filename}")
            print(f"   Date: {date}")
            print(f"   Type: {tournament_type}")
            print(f"   Decks: {num_decks}")
            if num_decks > 0:
                print(f"   Winner: {data['decks'][0]['player']}")
            print()
    
    print("\n📊 Résumé par type:")
    for t_type, count in sorted(tournaments_by_type.items()):
        print(f"   - {t_type}: {count} tournois")
    
    print(f"\n🎯 Total: {total_decks} decks dans {len(files)} tournois")
    
    # Vérifier la structure
    if files:
        print("\n🔍 Exemple de structure (premier tournoi):")
        with open(os.path.join(mtgo_dir, files[0]), 'r') as f:
            data = json.load(f)
            
        print(f"   - Clés disponibles: {list(data.keys())}")
        if data.get("decks"):
            deck = data["decks"][0]
            print(f"   - Clés d'un deck: {list(deck.keys())}")
            print(f"   - Exemple mainboard: {len(deck.get('mainboard', []))} cartes")
            print(f"   - Exemple sideboard: {len(deck.get('sideboard', []))} cartes")

if __name__ == "__main__":
    show_mtgo_data()