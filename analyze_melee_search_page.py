#!/usr/bin/env python3
"""Analyser la page de recherche Melee pour comprendre le format exact."""
import json
import requests
from bs4 import BeautifulSoup
import re

def analyze_search_page():
    """Analyser la page de recherche après authentification."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    email = creds['login'] 
    password = creds['mdp']
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    })
    
    # Login rapide
    login_page = session.get("https://melee.gg/Account/SignIn")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    
    session.post(
        "https://melee.gg/Account/SignInPassword",
        data={
            'Email': email,
            'Password': password,
            '__RequestVerificationToken': csrf_token
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print("✅ Authentifié!")
    
    # Récupérer la page de recherche de tournois
    print("\n📄 Récupération de la page de recherche...")
    search_page = session.get("https://melee.gg/Tournament/Index")
    
    if search_page.status_code != 200:
        print(f"❌ Erreur {search_page.status_code}")
        return
    
    soup = BeautifulSoup(search_page.text, 'html.parser')
    
    # Chercher les scripts JavaScript
    print("\n🔍 Analyse des scripts JavaScript...")
    scripts = soup.find_all('script')
    
    for i, script in enumerate(scripts):
        if script.string:
            content = script.string
            
            # Chercher les patterns DataTables ou AJAX
            if any(pattern in content for pattern in ['SearchTournaments', 'ajax:', 'DataTable', 'serverSide', 'columns:']):
                print(f"\n--- Script {i} (pertinent) ---")
                
                # Extraire les configurations AJAX
                ajax_match = re.search(r'ajax:\s*{([^}]+)}', content, re.DOTALL)
                if ajax_match:
                    print("Configuration AJAX trouvée:")
                    print(ajax_match.group(0))
                
                # Extraire l'URL
                url_match = re.search(r'url:\s*["\']([^"\']+)["\']', content)
                if url_match:
                    print(f"URL trouvée: {url_match.group(1)}")
                
                # Extraire le type de requête
                type_match = re.search(r'type:\s*["\']([^"\']+)["\']', content)
                if type_match:
                    print(f"Type de requête: {type_match.group(1)}")
                
                # Extraire data function
                data_match = re.search(r'data:\s*function\s*\([^)]*\)\s*{([^}]+)}', content, re.DOTALL)
                if data_match:
                    print("Fonction data trouvée:")
                    print(data_match.group(0))
                
                # Chercher les colonnes
                columns_match = re.search(r'columns:\s*\[([^\]]+)\]', content, re.DOTALL)
                if columns_match:
                    print("\nConfiguration des colonnes trouvée")
                
                # Afficher un extrait du script
                print("\nExtrait du script:")
                # Chercher autour de SearchTournaments
                idx = content.find('SearchTournaments')
                if idx != -1:
                    print(content[max(0, idx-200):idx+200])
    
    # Chercher les formulaires
    print("\n🔍 Analyse des formulaires...")
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        if 'tournament' in action.lower():
            print(f"\nFormulaire trouvé: {action}")
            inputs = form.find_all('input')
            for inp in inputs[:5]:
                print(f"  - {inp.get('name')}: {inp.get('type')}")
    
    # Chercher les tables DataTables
    print("\n🔍 Analyse des tables...")
    tables = soup.find_all('table')
    for table in tables:
        table_id = table.get('id', '')
        classes = table.get('class', [])
        if table_id or 'datatable' in ' '.join(classes).lower():
            print(f"\nTable trouvée: ID={table_id}, Classes={classes}")
    
    # Sauvegarder la page pour analyse manuelle
    with open('melee_search_page.html', 'w', encoding='utf-8') as f:
        f.write(search_page.text)
    print("\n💾 Page sauvegardée dans melee_search_page.html")

if __name__ == "__main__":
    analyze_search_page()