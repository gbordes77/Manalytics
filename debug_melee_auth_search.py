#!/usr/bin/env python3
"""Debug Melee auth + search pour identifier l'erreur 500."""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def debug_auth_and_search():
    """Debug complet du flow Melee."""
    
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
    print(f"Cookies avant login: {list(session.cookies.keys())}")
    
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
    print(f"Cookies après login: {list(session.cookies.keys())}")
    
    # Vérifier si l'authentification a réussi
    if 'error' in login_submit.url.lower() or 'login' in login_submit.url.lower():
        print("❌ Authentification échouée")
        return
    
    print("✅ Authentification réussie!")
    
    # Étape 4: Test recherche avec différents formats
    print("\n🔍 Étape 4: Test différents formats de requête...")
    
    # Format 1: Comme dans test_melee_final.py (form-encoded)
    print("\n--- Format 1: Form-encoded (comme test_melee_final.py) ---")
    search_data_form = {
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
    
    # Headers pour les requêtes AJAX
    ajax_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response1 = session.post(
        "https://melee.gg/Tournament/SearchTournaments",
        data=search_data_form,
        headers=ajax_headers
    )
    
    print(f"Status: {response1.status_code}")
    print(f"Content-Type: {response1.headers.get('content-type')}")
    if response1.status_code == 200:
        if 'application/json' in response1.headers.get('content-type', ''):
            data = response1.json()
            print(f"✅ JSON! Données: {list(data.keys())}")
            if 'data' in data:
                print(f"Tournois trouvés: {len(data['data'])}")
        else:
            print(f"❌ HTML retourné: {response1.text[:500]}")
    
    # Format 2: JSON (comme debug_melee_api.py)
    print("\n--- Format 2: JSON ---")
    search_data_json = {
        "draw": "1",
        "columns": [
            {"data": "ID", "name": "", "searchable": True, "orderable": True},
            {"data": "Name", "name": "", "searchable": True, "orderable": True},
            {"data": "StartDate", "name": "", "searchable": True, "orderable": True},
            {"data": "Status", "name": "", "searchable": True, "orderable": True},
            {"data": "Format", "name": "", "searchable": True, "orderable": True},
            {"data": "OrganizationName", "name": "", "searchable": True, "orderable": True},
            {"data": "Decklists", "name": "", "searchable": False, "orderable": False},
            {"data": "Description", "name": "", "searchable": False, "orderable": False}
        ],
        "order": [{"column": 2, "dir": "desc"}],
        "start": 0,
        "length": 10,
        "search": {"value": "", "regex": False},
        "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00.000Z"),
        "endDate": datetime.now().strftime("%Y-%m-%dT23:59:59.999Z")
    }
    
    json_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }
    
    response2 = session.post(
        "https://melee.gg/Tournament/SearchTournaments",
        json=search_data_json,
        headers=json_headers
    )
    
    print(f"Status: {response2.status_code}")
    print(f"Content-Type: {response2.headers.get('content-type')}")
    if response2.status_code == 200:
        if 'application/json' in response2.headers.get('content-type', ''):
            data = response2.json()
            print(f"✅ JSON! Données: {list(data.keys())}")
        else:
            print(f"❌ HTML retourné: {response2.text[:500]}")
    
    # Format 3: Sans dates (peut-être obligatoires?)
    print("\n--- Format 3: Sans dates ---")
    search_data_no_dates = {
        "draw": "1",
        "columns[0][data]": "ID",
        "columns[1][data]": "Name",
        "columns[2][data]": "StartDate",
        "columns[3][data]": "Status",
        "columns[4][data]": "Format",
        "columns[5][data]": "OrganizationName",
        "columns[6][data]": "Decklists",
        "columns[7][data]": "Description",
        "order[0][column]": "2",
        "order[0][dir]": "desc",
        "start": "0",
        "length": "10",
        "search[value]": "",
        "search[regex]": "false"
    }
    
    response3 = session.post(
        "https://melee.gg/Tournament/SearchTournaments",
        data=search_data_no_dates,
        headers=ajax_headers
    )
    
    print(f"Status: {response3.status_code}")
    print(f"Content-Type: {response3.headers.get('content-type')}")
    
    # Étape 5: Vérifier si on peut accéder à la page de recherche directement
    print("\n🔍 Étape 5: Accès direct à la page de recherche...")
    search_page = session.get("https://melee.gg/Tournament/Index")
    print(f"Status page de recherche: {search_page.status_code}")
    if search_page.status_code == 200:
        # Chercher des indices dans la page
        soup = BeautifulSoup(search_page.text, 'html.parser')
        
        # Chercher un token CSRF pour la recherche
        search_token = soup.find('input', {'name': '__RequestVerificationToken'})
        if search_token:
            print(f"✅ Token CSRF pour recherche trouvé: {search_token.get('value', '')[:20]}...")
            
            # Essayer avec le token
            print("\n--- Format 4: Avec token CSRF ---")
            search_data_with_token = search_data_form.copy()
            search_data_with_token['__RequestVerificationToken'] = search_token.get('value')
            
            response4 = session.post(
                "https://melee.gg/Tournament/SearchTournaments",
                data=search_data_with_token,
                headers=ajax_headers
            )
            
            print(f"Status: {response4.status_code}")
            print(f"Content-Type: {response4.headers.get('content-type')}")
            if response4.status_code == 200 and 'application/json' in response4.headers.get('content-type', ''):
                data = response4.json()
                print(f"✅ SUCCESS! Tournois trouvés: {len(data.get('data', []))}")
                if data.get('data'):
                    print(f"\nPremier tournoi:")
                    first = data['data'][0]
                    print(f"  - ID: {first.get('ID')}")
                    print(f"  - Nom: {first.get('Name')}")
                    print(f"  - Format: {first.get('Format')}")

if __name__ == "__main__":
    debug_auth_and_search()