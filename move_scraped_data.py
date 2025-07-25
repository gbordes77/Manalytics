#!/usr/bin/env python3
"""
Déplace les données scrapées vers le bon emplacement
"""

import os
import shutil
from pathlib import Path

def move_tournament_data():
    """Déplace les données de data/tournaments/ vers data/raw/"""
    
    # Chemins source et destination
    source_base = Path("data/tournaments")
    dest_base = Path("data/raw")
    
    # Déplacer les données Melee
    melee_source = source_base / "melee" / "2025-07"
    melee_dest = dest_base / "melee" / "standard"
    
    if melee_source.exists():
        # Créer le dossier destination
        melee_dest.mkdir(parents=True, exist_ok=True)
        
        # Déplacer chaque fichier
        for file in melee_source.glob("*.json"):
            dest_file = melee_dest / file.name
            print(f"Déplacement: {file} -> {dest_file}")
            shutil.move(str(file), str(dest_file))
        
        print(f"\n✅ {len(list(melee_source.glob('*.json')))} fichiers Melee déplacés")
    
    # Nettoyer les dossiers vides
    if melee_source.exists() and not any(melee_source.iterdir()):
        melee_source.rmdir()
        print("🧹 Dossier source vidé et supprimé")

if __name__ == "__main__":
    print("🔄 Déplacement des données vers data/raw/...\n")
    move_tournament_data()
    print("\n✅ Terminé ! Les données sont maintenant au bon endroit.")