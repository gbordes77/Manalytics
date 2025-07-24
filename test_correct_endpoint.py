#!/usr/bin/env python3
"""Test du bon endpoint /Tournament/SearchResults."""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def test_search_results():
    """Test le bon endpoint de recherche."""
    
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
    
    print("✅ Authentifié")
    
    # Test 1: GET simple sur SearchResults
    print("\n🧪 Test 1: GET sur /Tournament/SearchResults")
    
    get_response = session.get("https://melee.gg/Tournament/SearchResults")
    print(f"Status: {get_response.status_code}")
    print(f"Content-Type: {get_response.headers.get('content-type')}")
    
    if get_response.status_code == 200:
        try:
            data = get_response.json()
            print(f"✅ JSON! Tournois: {len(data.get('data', []))}")
            
            if data.get('data'):
                first = data['data'][0]
                print(f"Premier tournoi: {first.get('Name')} - {first.get('Format')}")
        except:
            print(f"❌ Pas JSON: {get_response.text[:200]}")
    
    # Test 2: GET avec paramètres de filtre
    print("\n🧪 Test 2: GET avec paramètres")
    
    params = {
        'formatId': '1',  # Standard selon les format IDs habituels
        'gameId': '1',    # Magic
        'startDate': (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y'),
        'endDate': datetime.now().strftime('%m/%d/%Y')
    }
    
    param_response = session.get("https://melee.gg/Tournament/SearchResults", params=params)
    print(f"Status: {param_response.status_code}")
    print(f"URL: {param_response.url}")
    
    if param_response.status_code == 200:
        try:
            data = param_response.json()
            print(f"✅ JSON! Tournois avec filtres: {len(data.get('data', []))}")
            
            # Filtrer par Standard
            standard_count = 0
            for tournament in data.get('data', []):
                format_name = str(tournament.get('Format', '')).lower()
                if 'standard' in format_name:
                    standard_count += 1
                    if standard_count <= 3:
                        print(f"  🏆 {tournament.get('Name')} - {tournament.get('Format')} - {tournament.get('StartDate')}")
            
            print(f"\n🎯 Total Standard: {standard_count}")
            
        except Exception as e:
            print(f"❌ Erreur JSON: {e}")
            print(f"Réponse: {param_response.text[:200]}")
    
    # Test 3: POST avec payload DataTables (au cas où)
    print("\n🧪 Test 3: POST DataTables")
    
    # Headers AJAX
    session.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    dt_payload = {
        "draw": "1",
        "start": "0", 
        "length": "25",
        "search[value]": "",
        "search[regex]": "false"
    }
    
    post_response = session.post(
        "https://melee.gg/Tournament/SearchResults",
        data=dt_payload
    )
    
    print(f"Status POST: {post_response.status_code}")
    
    if post_response.status_code == 200:
        try:
            data = post_response.json()
            print(f"✅ POST JSON! Tournois: {len(data.get('data', []))}")
        except:
            print(f"❌ POST pas JSON: {post_response.text[:200]}")

if __name__ == "__main__":
    test_search_results()