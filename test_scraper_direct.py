#!/usr/bin/env python3
"""Test direct du scraper sans dépendances."""
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

async def test_melee_direct():
    """Test direct de l'API Melee."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    email = creds['login']
    password = creds['mdp']
    
    print(f"🔐 Email: {email}")
    
    # Créer un client httpx comme le scraper
    async with httpx.AsyncClient() as client:
        
        # Étape 1: Auth avec requests synchrone (comme le scraper)
        import requests
        auth_session = requests.Session()
        auth_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Auth flow exact du scraper
        main_response = auth_session.get("https://melee.gg")
        login_response = auth_session.get("https://melee.gg/Account/SignIn")
        
        soup = BeautifulSoup(login_response.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        csrf_token = token_input.get('value')
        
        form_data = {
            'Email': email,
            'Password': password,
            '__RequestVerificationToken': csrf_token
        }
        
        login_submit = auth_session.post(
            "https://melee.gg/Account/SignInPassword",
            data=form_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://melee.gg/Account/SignIn'
            },
            allow_redirects=True
        )
        
        print(f"✅ Auth status: {login_submit.status_code}")
        print(f"✅ Cookies: {len(auth_session.cookies)}")
        
        # Transférer cookies vers httpx client
        for cookie in auth_session.cookies:
            client.cookies.set(cookie.name, cookie.value)
        
        # Headers AJAX comme le scraper
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://melee.gg/Tournament/Search'
        })
        
        # Payload exact du scraper
        search_payload = {
            "draw": "1",
            "start": "0", 
            "length": "100",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        print("\n🔍 Requête API...")
        response = await client.post(
            "https://melee.gg/Tournament/SearchResults",
            data=search_payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON valide!")
                
                if isinstance(data, list):
                    print(f"🏆 Tournois trouvés: {len(data)}")
                    
                    # Filtrer Magic
                    magic_tournaments = []
                    for tournament in data:
                        game_desc = tournament.get("gameDescription", "")
                        if "Magic" in game_desc:
                            magic_tournaments.append(tournament)
                    
                    print(f"🎮 Tournois Magic: {len(magic_tournaments)}")
                    
                    # Afficher les 3 premiers
                    for i, tournament in enumerate(magic_tournaments[:3]):
                        print(f"\n🏆 Tournoi {i+1}:")
                        print(f"  - ID: {tournament.get('id')}")
                        print(f"  - Nom: {tournament.get('name')}")
                        print(f"  - Jeu: {tournament.get('gameDescription')}")
                        print(f"  - Date: {tournament.get('startDate')}")
                        print(f"  - Organisation: {tournament.get('organizationName')}")
                        
                        # Test récupération des decklists pour ce tournoi
                        tournament_id = tournament.get('id')
                        if tournament_id:
                            print(f"  📋 Test decklists pour tournoi {tournament_id}...")
                            
                            # Essayer d'aller sur la page du tournoi
                            tournament_page = await client.get(f"https://melee.gg/Tournament/{tournament_id}")
                            print(f"    Page tournoi: {tournament_page.status_code}")
                            
                            if tournament_page.status_code == 200:
                                print("    ✅ Page tournoi accessible")
                else:
                    print(f"Format inattendu: {type(data)}")
                    print(f"Clés: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON: {e}")
                print(f"Réponse: {response.text[:300]}")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Réponse: {response.text[:300]}")

if __name__ == "__main__":
    asyncio.run(test_melee_direct())