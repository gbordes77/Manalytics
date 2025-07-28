#!/usr/bin/env python3
"""
Rechercher les credentials Melee existants dans le projet
"""

import os
import json
from pathlib import Path

def find_credentials():
    """Chercher les credentials dans différents emplacements possibles"""
    
    # Emplacements possibles
    possible_locations = [
        # Emplacements standards
        "api_credentials/melee_login.json",
        "Api_token_and_login/melee_login.json",
        "melee_login.json",
        ".env",
        
        # Emplacements de cookies
        "api_credentials/melee_cookies.json",
        "melee_cookies.json",
        
        # Autres possibilités
        "config/melee.json",
        "credentials/melee.json",
        ".melee",
        "scrapers/credentials/melee_login.json",
        "src/scrapers/credentials/melee_login.json",
        
        # Anciens emplacements possibles
        "mtg_decklist_scrapper/Api_token_and_login/melee_login.json",
        "jiliac_pipeline/Api_token_and_login/melee_login.json"
    ]
    
    found = []
    
    print("🔍 Recherche des credentials Melee...")
    print("=" * 50)
    
    for location in possible_locations:
        path = Path(location)
        if path.exists():
            print(f"✅ Trouvé: {location}")
            
            # Essayer de lire le contenu
            try:
                if location.endswith('.json'):
                    with open(path, 'r') as f:
                        data = json.load(f)
                        if 'login' in data or 'email' in data:
                            print(f"   → Contient des credentials!")
                            found.append(location)
                        elif 'cookies' in data:
                            print(f"   → Contient des cookies!")
                            found.append(location)
                elif location == '.env':
                    with open(path, 'r') as f:
                        content = f.read()
                        if 'MELEE' in content:
                            print(f"   → Contient des configs Melee!")
                            found.append(location)
            except Exception as e:
                print(f"   ⚠️ Erreur lecture: {e}")
    
    # Recherche plus large
    print("\n🔎 Recherche étendue...")
    
    # Chercher tous les fichiers JSON contenant 'melee'
    for root, dirs, files in os.walk('.'):
        # Ignorer certains dossiers
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv']):
            continue
            
        for file in files:
            if file.endswith('.json') and 'melee' in file.lower():
                filepath = os.path.join(root, file)
                print(f"📄 Fichier JSON Melee trouvé: {filepath}")
                found.append(filepath)
    
    print("\n" + "=" * 50)
    if found:
        print(f"✅ {len(found)} fichier(s) potentiel(s) trouvé(s):")
        for f in found:
            print(f"   - {f}")
    else:
        print("❌ Aucun fichier de credentials trouvé")
        print("\n💡 Vous devez créer: api_credentials/melee_login.json")
        print('   Format: {"login": "email@example.com", "mdp": "password"}')
    
    return found


if __name__ == "__main__":
    find_credentials()