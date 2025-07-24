#!/usr/bin/env python3
"""Analyser la page Tournament/Search pour trouver l'endpoint API."""
import json
import requests
import re
from bs4 import BeautifulSoup

def analyze_search_page():
    """Analyser la page de recherche de tournois."""
    
    # Auth rapide
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    })
    
    # Auth
    main_response = session.get("https://melee.gg")
    login_page = session.get("https://melee.gg/Account/SignIn")
    
    soup = BeautifulSoup(login_page.text, 'html.parser')
    token_input = soup.find('input', {'name': '__RequestVerificationToken'})
    csrf_token = token_input.get('value')
    
    form_data = {
        'Email': creds['login'],
        'Password': creds['mdp'],
        '__RequestVerificationToken': csrf_token
    }
    
    session.post(
        "https://melee.gg/Account/SignInPassword",
        data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    # Récupérer la page de recherche
    print("🔍 Analyse de /Tournament/Search...")
    search_page = session.get("https://melee.gg/Tournament/Search")
    
    if search_page.status_code == 200:
        print("✅ Page accessible")
        
        # Sauvegarder le HTML pour analyse
        with open('tournament_search_page.html', 'w', encoding='utf-8') as f:
            f.write(search_page.text)
        print("📄 HTML sauvegardé dans tournament_search_page.html")
        
        soup = BeautifulSoup(search_page.text, 'html.parser')
        
        # Chercher des scripts avec des URLs d'API
        print("\n🔍 Recherche d'endpoints dans les scripts...")
        scripts = soup.find_all('script')
        
        api_endpoints = set()
        
        for i, script in enumerate(scripts):
            if script.string:
                text = script.string
                
                # Chercher des patterns d'URL
                url_patterns = [
                    r'["\']([^"\']*Tournament[^"\']*Search[^"\']*)["\']',
                    r'["\']([^"\']*Search[^"\']*Tournament[^"\']*)["\']',
                    r'url:\s*["\']([^"\']+)["\']',
                    r'ajax\([^)]*url:\s*["\']([^"\']+)["\']',
                    r'/[A-Za-z]+/[A-Za-z]*Search[A-Za-z]*',
                    r'/Search[A-Za-z]*'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        if 'search' in match.lower() or 'tournament' in match.lower():
                            api_endpoints.add(match)
                
                # Chercher du code DataTables (très commun pour ce type de site)
                if 'DataTable' in text or 'dataTables' in text:
                    print(f"  📊 Script {i+1} utilise DataTables")
                    
                    # Extraire l'URL ajax
                    ajax_matches = re.findall(r'ajax[:\s]*["\']([^"\']+)["\']', text, re.IGNORECASE)
                    for match in ajax_matches:
                        api_endpoints.add(match)
                        print(f"    Ajax URL trouvée: {match}")
        
        # Afficher tous les endpoints trouvés
        print(f"\n🎯 Endpoints potentiels trouvés: {len(api_endpoints)}")
        for endpoint in sorted(api_endpoints):
            print(f"  - {endpoint}")
        
        # Chercher des éléments avec des data-attributes
        print("\n🏷️ Recherche d'attributs data-*...")
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        
        for elem in elements_with_data[:10]:  # Limiter à 10
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            if data_attrs:
                print(f"  {elem.name}: {data_attrs}")
    
    else:
        print(f"❌ Erreur {search_page.status_code}")

if __name__ == "__main__":
    analyze_search_page()