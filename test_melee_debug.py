#!/usr/bin/env python3
"""Debug pour trouver le bon endpoint et format pour Melee."""
import requests
import json
from urllib.parse import urljoin

def test_login_endpoint():
    """Test différents endpoints de login."""
    
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    email = creds['login'] 
    password = creds['mdp']
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    
    # Test 1: GET sur la page de login pour voir la structure
    print("🔍 Test 1: GET /Auth/Login")
    try:
        login_page = session.get("https://melee.gg/Auth/Login")
        print(f"Status: {login_page.status_code}")
        print(f"URL finale: {login_page.url}")
        print(f"Cookies: {len(session.cookies)}")
        
        if login_page.status_code == 200:
            # Chercher des indices dans le HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Chercher des formulaires
            forms = soup.find_all('form')
            print(f"Formulaires trouvés: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"  Form {i+1}:")
                print(f"    Action: {form.get('action')}")
                print(f"    Method: {form.get('method')}")
                
                # Chercher les inputs
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"    Input: {inp.get('name')} = {inp.get('type')}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: Essayer différents endpoints
    endpoints = [
        "/Auth/Login",
        "/Account/Login", 
        "/Account/SignIn",
        "/Login"
    ]
    
    login_data = {
        'Email': email,
        'Password': password,
        'RememberMe': 'false'
    }
    
    for endpoint in endpoints:
        print(f"🧪 Test endpoint: {endpoint}")
        
        try:
            url = f"https://melee.gg{endpoint}"
            response = session.post(url, data=login_data)
            
            print(f"  Status: {response.status_code}")
            print(f"  URL finale: {response.url}")
            print(f"  Redirection: {'Oui' if response.url != url else 'Non'}")
            print(f"  Cookies: {len(session.cookies)}")
            
            # Si on a des cookies, c'est peut-être bon
            if len(session.cookies) > 0:
                print("  ✅ Cookies reçus!")
                for cookie in session.cookies:
                    print(f"    {cookie.name}: {cookie.value[:20]}...")
            
            # Vérifier si on est sur une page d'erreur
            if 'error' in response.url.lower():
                print("  ❌ Redirection vers page d'erreur")
            elif response.status_code == 200 and 'login' not in response.url.lower():
                print("  ✅ Possible succès (pas sur page login)")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            print()

if __name__ == "__main__":
    test_login_endpoint()