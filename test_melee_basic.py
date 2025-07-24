#!/usr/bin/env python3
"""Test basique pour Melee en utilisant exactement le même format que fbettega."""
import json
import requests
from datetime import datetime, timedelta

def main():
    """Test authentification Melee basique."""
    
    # Charger les credentials depuis le fichier JSON
    try:
        with open('Api_token_and_login/melee_login.json', 'r') as f:
            creds = json.load(f)
            email = creds['login']
            password = creds['mdp']
    except Exception as e:
        print(f"❌ Erreur lecture credentials: {e}")
        return
    
    print(f"📧 Email: {email}")
    print(f"🔐 Password: {'*' * len(password)}")
    
    session = requests.Session()
    
    # Headers exactement comme fbettega
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    print("\n🌐 Test 1: Page principale...")
    try:
        main_response = session.get("https://melee.gg")
        print(f"Status: {main_response.status_code}")
        print(f"Cookies après page principale: {len(session.cookies)}")
        for cookie in session.cookies:
            print(f"  - {cookie.name}: {cookie.value[:30]}...")
    except Exception as e:
        print(f"❌ Erreur page principale: {e}")
        return
    
    print("\n🔐 Test 2: Authentification...")
    login_data = {
        'Email': email,
        'Password': password,
        'RememberMe': 'false'
    }
    
    # Headers pour la requête de login
    login_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        login_response = session.post(
            "https://melee.gg/Auth/Login",
            data=login_data,
            headers=login_headers
        )
        
        print(f"Status login: {login_response.status_code}")
        print(f"URL finale: {login_response.url}")
        print(f"Content-Type: {login_response.headers.get('content-type')}")
        print(f"Cookies après login: {len(session.cookies)}")
        
        for cookie in session.cookies:
            print(f"  - {cookie.name}: {cookie.value[:30]}...")
        
        # Examiner la réponse
        try:
            response_json = login_response.json()
            print(f"Réponse JSON: {response_json}")
        except:
            print(f"Réponse text (200 premiers chars): {login_response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Erreur login: {e}")
        return
    
    # Si pas de cookies, on ne peut pas continuer
    if len(session.cookies) == 0:
        print("❌ Pas de cookies reçus - authentification échouée")
        return
    
    print("\n🔍 Test 3: Recherche tournois...")
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
    
    try:
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
                
                if data.get('data'):
                    first = data['data'][0]
                    print(f"\nPremier tournoi:")
                    print(f"  - ID: {first.get('ID')}")
                    print(f"  - Nom: {first.get('Name')}")
                    print(f"  - Format: {first.get('Format')}")
                    print(f"  - Date: {first.get('StartDate')}")
            except json.JSONDecodeError:
                print(f"❌ Pas JSON. Réponse: {search_response.text[:300]}")
        else:
            print(f"❌ Erreur {search_response.status_code}: {search_response.text[:300]}")
    
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")

if __name__ == "__main__":
    main()