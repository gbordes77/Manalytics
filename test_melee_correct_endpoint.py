#!/usr/bin/env python3
"""Test Melee avec le bon endpoint TournamentSearch."""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def test_correct_endpoint():
    """Test avec le bon endpoint et format."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    email = creds['login'] 
    password = creds['mdp']
    
    print(f"📧 Email: {email}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    })
    
    # Login rapide
    print("\n🔐 Authentification...")
    login_page = session.get("https://melee.gg/Account/SignIn")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    
    login_response = session.post(
        "https://melee.gg/Account/SignInPassword",
        data={
            'Email': email,
            'Password': password,
            '__RequestVerificationToken': csrf_token
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print(f"✅ Authentifié! Cookies: {list(session.cookies.keys())}")
    
    # Test 1: Format basé sur getSearchState()
    print("\n🔍 Test 1: Format getSearchState...")
    search_url = "https://melee.gg/Tournament/TournamentSearch"
    
    search_data = {
        "ordering": "StartDate",
        "filters": [],
        "mode": "Table"
    }
    
    response = session.post(
        search_url,
        json=search_data,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    # Afficher la réponse même en cas d'erreur
    if response.status_code == 500:
        print(f"Erreur 500 - Contenu: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Réponse JSON!")
            print(f"Clés: {list(data.keys())}")
            if 'data' in data:
                print(f"Tournois trouvés: {len(data['data'])}")
                if data['data']:
                    first = data['data'][0]
                    print(f"\nPremier tournoi:")
                    for key in ['id', 'name', 'startDate', 'format']:
                        if key in first:
                            print(f"  - {key}: {first[key]}")
        except json.JSONDecodeError:
            print(f"❌ Pas JSON: {response.text[:500]}")
    
    # Test 2: Format avec variables DataTables
    print("\n🔍 Test 2: Format avec variables DataTables...")
    search_data_dt = {
        "ordering": "StartDate",
        "filters": [],
        "mode": "Table",
        "variables": {
            "draw": 1,
            "start": 0,
            "length": 25,
            "search": {"value": "", "regex": False}
        }
    }
    
    response2 = session.post(
        search_url,
        json=search_data_dt,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    )
    
    print(f"Status: {response2.status_code}")
    print(f"Content-Type: {response2.headers.get('content-type')}")
    
    if response2.status_code == 200:
        try:
            data = response2.json()
            print(f"✅ Réponse JSON!")
            print(f"Clés: {list(data.keys())}")
            
            # Afficher le format complet de la réponse
            print("\nFormat de réponse:")
            print(json.dumps(data, indent=2)[:1000])
            
        except json.JSONDecodeError:
            print(f"❌ Pas JSON: {response2.text[:500]}")
    
    # Test 3: Filtrer par format Standard
    print("\n🔍 Test 3: Filtrer par format Standard...")
    search_data_standard = {
        "ordering": "StartDate",
        "filters": ["Standard"],  # Essayer d'ajouter le filtre Standard
        "mode": "Table",
        "variables": {
            "draw": 1,
            "start": 0,
            "length": 50
        }
    }
    
    response3 = session.post(
        search_url,
        json=search_data_standard,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    )
    
    print(f"Status: {response3.status_code}")
    
    if response3.status_code == 200:
        try:
            data = response3.json()
            if 'data' in data:
                # Filtrer manuellement par Standard
                standard_count = 0
                for tournament in data['data']:
                    if tournament.get('format', '').lower() == 'standard':
                        standard_count += 1
                        if standard_count <= 3:
                            print(f"\n🏆 Tournoi Standard {standard_count}:")
                            print(f"  - ID: {tournament.get('id')}")
                            print(f"  - Nom: {tournament.get('name')}")
                            print(f"  - Date: {tournament.get('startDate')}")
                            print(f"  - Joueurs: {tournament.get('players')}")
                
                print(f"\n📊 Total tournois Standard trouvés: {standard_count}")
                
        except json.JSONDecodeError:
            print(f"❌ Pas JSON")

if __name__ == "__main__":
    test_correct_endpoint()