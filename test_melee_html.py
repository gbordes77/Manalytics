#!/usr/bin/env python3
"""Test de navigation sur Melee pour trouver les bons endpoints."""
import json
import requests
from bs4 import BeautifulSoup

def test_navigation():
    """Explorer la navigation sur Melee."""
    
    # Authentification (on sait que ça marche)
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    
    # Auth rapide
    print("🔐 Authentification...")
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
    
    login_submit = session.post(
        "https://melee.gg/Account/SignInPassword",
        data=form_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://melee.gg/Account/SignIn'
        }
    )
    
    print(f"Auth status: {login_submit.status_code}")
    print(f"Cookies: {len(session.cookies)}")
    
    # Explorer les pages disponibles
    pages_to_test = [
        "/Tournament",
        "/Tournament/Search",
        "/Tournaments",
        "/Decklist",
        "/Decklist/Search",
        "/Decklists"
    ]
    
    for page in pages_to_test:
        print(f"\n🔍 Test page: {page}")
        try:
            response = session.get(f"https://melee.gg{page}")
            print(f"  Status: {response.status_code}")
            print(f"  URL finale: {response.url}")
            
            if response.status_code == 200 and 'error' not in response.url.lower():
                print("  ✅ Page accessible")
                
                # Chercher des formulaires ou des scripts qui pourraient révéler des endpoints
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Chercher des scripts qui mentionnent des URLs
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        text = script.string
                        if 'Search' in text and ('Tournament' in text or 'Decklist' in text):
                            print(f"  🔍 Script mentionnant Search trouvé")
                            # Extraire les URLs
                            import re
                            urls = re.findall(r'["\'](/[^"\']*Search[^"\']*)["\']', text)
                            for url in urls:
                                print(f"    URL trouvée: {url}")
                
                # Chercher des formulaires
                forms = soup.find_all('form')
                if forms:
                    print(f"  📋 {len(forms)} formulaire(s) trouvé(s)")
                    for i, form in enumerate(forms):
                        action = form.get('action')
                        if action:
                            print(f"    Form {i+1} action: {action}")
            else:
                print("  ❌ Page inaccessible ou erreur")
        
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

if __name__ == "__main__":
    test_navigation()