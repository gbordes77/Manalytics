#!/usr/bin/env python3
"""Test Melee avec form-encoded comme la page web."""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def test_form_encoded():
    """Test avec form-encoded."""
    
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
    
    print(f"✅ Authentifié!")
    
    # Récupérer la page de recherche pour avoir le bon token
    print("\n📄 Récupération page de recherche...")
    search_page = session.get("https://melee.gg/Tournament/Index")
    soup = BeautifulSoup(search_page.text, 'html.parser')
    
    # Chercher un token dans la page
    search_token = soup.find('input', {'name': '__RequestVerificationToken'})
    if search_token:
        token_value = search_token.get('value')
        print(f"✅ Token trouvé: {token_value[:20]}...")
    else:
        token_value = None
        print("⚠️ Pas de token trouvé")
    
    # Test 1: Format simple form-encoded
    print("\n🔍 Test 1: Form-encoded simple...")
    search_url = "https://melee.gg/Tournament/TournamentSearch"
    
    form_data = {
        "ordering": "StartDate",
        "filters": "",
        "mode": "Table"
    }
    
    if token_value:
        form_data["__RequestVerificationToken"] = token_value
    
    response = session.post(
        search_url,
        data=form_data,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://melee.gg/Tournament/Index'
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 500:
        print(f"Erreur 500: {response.text}")
    elif response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Success! Clés: {list(data.keys())}")
            if 'data' in data:
                print(f"Tournois: {len(data['data'])}")
        except:
            print(f"Réponse: {response.text[:500]}")
    
    # Test 2: Avec les paramètres DataTables
    print("\n🔍 Test 2: Avec paramètres DataTables...")
    
    form_data_dt = {
        "ordering": "StartDate",
        "filters": "",
        "mode": "Table",
        "variables[draw]": "1",
        "variables[start]": "0",
        "variables[length]": "25",
        "variables[search][value]": "",
        "variables[search][regex]": "false"
    }
    
    if token_value:
        form_data_dt["__RequestVerificationToken"] = token_value
    
    response2 = session.post(
        search_url,
        data=form_data_dt,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://melee.gg/Tournament/Index'
        }
    )
    
    print(f"Status: {response2.status_code}")
    
    if response2.status_code == 200:
        try:
            data = response2.json()
            print(f"✅ Success!")
            if 'data' in data:
                print(f"Tournois trouvés: {len(data['data'])}")
                
                # Filtrer les tournois Standard
                standard_tournaments = []
                for t in data['data']:
                    if 'format' in t and t['format'].lower() == 'standard':
                        standard_tournaments.append(t)
                
                print(f"\n🎯 Tournois Standard: {len(standard_tournaments)}")
                for i, t in enumerate(standard_tournaments[:5]):
                    print(f"\n{i+1}. {t.get('name')}")
                    print(f"   Date: {t.get('startDate')}")
                    print(f"   ID: {t.get('id')}")
                    
        except Exception as e:
            print(f"Erreur: {e}")
            print(f"Réponse: {response2.text[:500]}")
    
    # Test 3: Récupérer les standings d'un tournoi
    print("\n🔍 Test 3: Test GetRoundStandings...")
    
    standings_url = "https://melee.gg/Round/GetRoundStandings"
    standings_data = {
        "draw": "1",
        "columns[0][data]": "Rank",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[1][data]": "Player",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[2][data]": "Decklists",
        "columns[2][name]": "",
        "columns[2][searchable]": "false",
        "columns[2][orderable]": "false",
        "columns[3][data]": "MatchRecord",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[4][data]": "GameRecord",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[5][data]": "Points",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "true",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "start": "0",
        "length": "25",
        "search[value]": "",
        "search[regex]": "false",
        "roundId": "191434"  # ID exemple d'un round
    }
    
    response3 = session.post(
        standings_url,
        data=standings_data,
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
    )
    
    print(f"Status standings: {response3.status_code}")
    if response3.status_code == 200:
        try:
            data = response3.json()
            print(f"✅ Standings OK! Clés: {list(data.keys())}")
        except:
            print(f"Réponse: {response3.text[:200]}")

if __name__ == "__main__":
    test_form_encoded()