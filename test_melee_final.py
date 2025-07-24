#!/usr/bin/env python3
"""Test final pour Melee avec le bon endpoint."""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def test_complete_flow():
    """Test complet du flow Melee."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    email = creds['login'] 
    password = creds['mdp']
    
    print(f"📧 Email: {email}")
    print(f"🔐 Password: {'*' * len(password)}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    # Étape 1: Page principale
    print("\n🌐 Étape 1: Page principale...")
    main_response = session.get("https://melee.gg")
    print(f"Status: {main_response.status_code}")
    
    # Étape 2: Page de login pour obtenir le token CSRF  
    print("\n🔐 Étape 2: Page de login...")
    login_page = session.get("https://melee.gg/Account/SignIn")
    print(f"Status: {login_page.status_code}")
    print(f"Cookies: {len(session.cookies)}")
    
    # Extraire le token CSRF
    soup = BeautifulSoup(login_page.text, 'html.parser')
    token_input = soup.find('input', {'name': '__RequestVerificationToken'})
    
    if not token_input:
        print("❌ Pas de token CSRF trouvé")
        return
    
    csrf_token = token_input.get('value')
    print(f"✅ Token CSRF trouvé: {csrf_token[:20]}...")
    
    # Étape 3: Soumission du formulaire de login
    print("\n🚀 Étape 3: Soumission login...")
    
    form_data = {
        'Email': email,
        'Password': password,
        '__RequestVerificationToken': csrf_token
    }
    
    login_submit = session.post(
        "https://melee.gg/Account/SignInPassword",
        data=form_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://melee.gg/Account/SignIn'
        },
        allow_redirects=True
    )
    
    print(f"Status login: {login_submit.status_code}")
    print(f"URL finale: {login_submit.url}")
    print(f"Cookies après login: {len(session.cookies)}")
    
    for cookie in session.cookies:
        print(f"  - {cookie.name}: {cookie.value[:30]}...")
    
    # Vérifier si l'authentification a réussi
    if 'error' in login_submit.url.lower() or 'login' in login_submit.url.lower():
        print("❌ Authentification échouée")
        return
    
    print("✅ Authentification réussie!")
    
    # Étape 4: Test recherche de tournois
    print("\n🔍 Étape 4: Recherche tournois...")
    
    # Headers pour les requêtes AJAX
    session.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    # Payload de recherche selon les docs fbettega (mais pour tournois, pas decklists)
    search_data = {
        "draw": "1",
        "columns[0][data]": "ID",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "Name",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "StartDate",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "Status",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "Format",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "OrganizationName",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "true",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "Decklists",
        "columns[6][name]": "",
        "columns[6][searchable]": "false",
        "columns[6][orderable]": "false",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "columns[7][data]": "Description",
        "columns[7][name]": "",
        "columns[7][searchable]": "false",
        "columns[7][orderable]": "false",
        "columns[7][search][value]": "",
        "columns[7][search][regex]": "false",
        "order[0][column]": "2",
        "order[0][dir]": "desc",
        "start": "0",
        "length": "10",
        "search[value]": "",
        "search[regex]": "false",
        "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00.000Z"),
        "endDate": datetime.now().strftime("%Y-%m-%dT23:59:59.999Z")
    }
    
    search_response = session.post(
        "https://melee.gg/Tournament/SearchTournaments",
        data=search_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print(f"Status search: {search_response.status_code}")
    print(f"Content-Type: {search_response.headers.get('content-type')}")
    
    if search_response.status_code == 200:
        try:
            data = search_response.json()
            print(f"✅ JSON valide! Tournois trouvés: {len(data.get('data', []))}")
            
            # Filtrer par Standard
            standard_tournaments = []
            for tournament in data.get('data', []):
                format_name = str(tournament.get('Format', '')).lower()
                if 'standard' in format_name:
                    standard_tournaments.append(tournament)
            
            print(f"🎯 Tournois Standard: {len(standard_tournaments)}")
            
            # Afficher les premiers
            for i, tournament in enumerate(standard_tournaments[:3]):
                print(f"\n🏆 Tournoi {i+1}:")
                print(f"  - ID: {tournament.get('ID')}")
                print(f"  - Nom: {tournament.get('Name')}")
                print(f"  - Format: {tournament.get('Format')}")
                print(f"  - Date: {tournament.get('StartDate')}")
                print(f"  - Status: {tournament.get('Status')}")
                
        except json.JSONDecodeError:
            print(f"❌ Pas JSON. Réponse: {search_response.text[:500]}")
    else:
        print(f"❌ Erreur {search_response.status_code}: {search_response.text[:300]}")

if __name__ == "__main__":
    test_complete_flow()