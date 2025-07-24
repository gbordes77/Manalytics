#!/usr/bin/env python3
"""Explorer les données Melee plus en détail."""
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from collections import Counter

async def explore_melee_data():
    """Explorer les données Melee en détail."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    async with httpx.AsyncClient() as client:
        
        # Authentification rapide
        import requests
        auth_session = requests.Session()
        auth_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        main_response = auth_session.get("https://melee.gg")
        login_response = auth_session.get("https://melee.gg/Account/SignIn")
        
        soup = BeautifulSoup(login_response.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        csrf_token = token_input.get('value')
        
        form_data = {
            'Email': creds['login'],
            'Password': creds['mdp'],
            '__RequestVerificationToken': csrf_token
        }
        
        auth_session.post(
            "https://melee.gg/Account/SignInPassword",
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        # Transférer cookies
        for cookie in auth_session.cookies:
            client.cookies.set(cookie.name, cookie.value)
        
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        
        print("🔍 Exploration détaillée des données Melee...")
        
        # Test 1: Récupérer tous les tournois avec pagination
        all_tournaments = []
        
        for page in range(0, 5):  # 5 pages
            start = page * 50
            search_payload = {
                "draw": f"{page + 1}",
                "start": str(start),
                "length": "50",
                "search[value]": "",
                "search[regex]": "false"
            }
            
            response = await client.post(
                "https://melee.gg/Tournament/SearchResults",
                data=search_payload
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and data:
                        all_tournaments.extend(data)
                        print(f"  Page {page + 1}: +{len(data)} tournois")
                    else:
                        break
                except:
                    break
            else:
                break
        
        print(f"\n📊 Total tournois récupérés: {len(all_tournaments)}")
        
        if not all_tournaments:
            print("❌ Aucun tournoi trouvé")
            return
        
        # Analyse des dates
        print("\n📅 Analyse des dates:")
        dates = []
        date_errors = 0
        
        for tournament in all_tournaments:
            try:
                start_date_str = tournament.get('startDate', '')
                if start_date_str:
                    start_date_str = start_date_str.replace('Z', '').split('T')[0]
                    tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    dates.append(tournament_date)
            except:
                date_errors += 1
        
        if dates:
            dates.sort()
            print(f"  📅 Premier tournoi: {dates[0].strftime('%d/%m/%Y')}")
            print(f"  📅 Dernier tournoi: {dates[-1].strftime('%d/%m/%Y')}")
            print(f"  📅 Erreurs de parsing: {date_errors}")
            
            # Distribution par année
            year_counts = Counter(d.year for d in dates)
            print(f"\n  📊 Distribution par année:")
            for year in sorted(year_counts.keys()):
                print(f"    {year}: {year_counts[year]} tournois")
        
        # Analyse des organisations
        print("\n🏢 Analyse des organisations:")
        orgs = [t.get('organizationName', 'N/A') for t in all_tournaments]
        org_counts = Counter(orgs)
        
        print("  Top 10 organisations:")
        for org, count in org_counts.most_common(10):
            print(f"    {org}: {count} tournois")
        
        # Analyse des jeux
        print("\n🎮 Analyse des jeux:")
        games = [t.get('gameDescription', 'N/A') for t in all_tournaments]
        game_counts = Counter(games)
        
        for game, count in game_counts.most_common():
            print(f"    {game}: {count} tournois")
        
        # Chercher des tournois avec des noms récents
        print("\n🔍 Recherche de tournois avec dates récentes dans le nom:")
        recent_keywords = ['2024', '2025', 'July', 'June', 'May']
        
        recent_name_tournaments = []
        for tournament in all_tournaments:
            name = tournament.get('name', '')
            if any(keyword in name for keyword in recent_keywords):
                recent_name_tournaments.append(tournament)
        
        if recent_name_tournaments:
            print(f"  Trouvé {len(recent_name_tournaments)} tournois avec mots-clés récents:")
            for t in recent_name_tournaments[:10]:
                print(f"    - {t.get('name')} ({t.get('startDate', 'N/A')})")
        else:
            print("  Aucun tournoi avec mots-clés récents trouvé")
        
        # Test 2: Explorer l'endpoint Decklist pour voir s'il y a des données plus récentes
        print("\n🃏 Test de l'endpoint Decklist...")
        
        decklist_payload = {
            "draw": "1",
            "start": "0",
            "length": "25",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        # Essayer différents endpoints de decklist
        decklist_endpoints = [
            "/Decklist/SearchDecklists",
            "/Decklists/Search",
            "/Decklist"
        ]
        
        for endpoint in decklist_endpoints:
            try:
                response = await client.post(f"https://melee.gg{endpoint}", data=decklist_payload)
                print(f"  {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'data' in data:
                            print(f"    Decklists trouvées: {len(data['data'])}")
                            
                            # Regarder la première decklist
                            if data['data']:
                                first = data['data'][0]
                                print(f"    Exemple: {first.get('Tournament', 'N/A')} - {first.get('Date', 'N/A')}")
                        elif isinstance(data, list):
                            print(f"    Liste de {len(data)} éléments")
                    except:
                        print(f"    Réponse non-JSON")
            except Exception as e:
                print(f"  {endpoint}: Erreur - {e}")

if __name__ == "__main__":
    asyncio.run(explore_melee_data())