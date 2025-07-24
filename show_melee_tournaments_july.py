#!/usr/bin/env python3
"""Afficher les tournois Melee depuis le 1er juillet 2025."""
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

async def show_melee_tournaments():
    """Afficher les tournois Melee récents."""
    
    # Charger credentials
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    print("🔍 Recherche des tournois Melee depuis le 1er juillet 2025...")
    print(f"📧 Authentification avec: {creds['login']}")
    
    # Date de référence : 1er juillet 2025
    july_1st = datetime(2025, 7, 1)
    today = datetime.now()
    
    print(f"📅 Période: {july_1st.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}")
    
    async with httpx.AsyncClient() as client:
        
        # Authentification (flow validé)
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
        
        print("\n🔐 Authentification...")
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
        
        login_submit = auth_session.post(
            "https://melee.gg/Account/SignInPassword",
            data=form_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://melee.gg/Account/SignIn'
            },
            allow_redirects=True
        )
        
        if login_submit.status_code == 200 and len(auth_session.cookies) > 0:
            print("✅ Authentification réussie")
        else:
            print("❌ Échec authentification")
            return
        
        # Transférer cookies
        for cookie in auth_session.cookies:
            client.cookies.set(cookie.name, cookie.value)
        
        # Headers AJAX
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://melee.gg/Tournament/Search'
        })
        
        # Récupérer tous les tournois
        search_payload = {
            "draw": "1",
            "start": "0", 
            "length": "1000",  # Plus de tournois
            "search[value]": "",
            "search[regex]": "false"
        }
        
        print("\n📡 Requête API Melee...")
        response = await client.post(
            "https://melee.gg/Tournament/SearchResults",
            data=search_payload
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return
        
        try:
            data = response.json()
        except:
            print("❌ Réponse non-JSON")
            return
        
        if not isinstance(data, list):
            print(f"❌ Format inattendu: {type(data)}")
            return
        
        print(f"✅ {len(data)} tournois récupérés depuis l'API")
        
        # Filtrer par date (depuis le 1er juillet 2025)
        recent_tournaments = []
        
        for tournament in data:
            try:
                # Parser la date du tournoi
                start_date_str = tournament.get('startDate', '')
                if not start_date_str:
                    continue
                
                # Formats possibles: "2025-07-15T19:00:00Z" ou "2025-07-15T19:00:00"
                start_date_str = start_date_str.replace('Z', '').split('T')[0]
                tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                
                # Vérifier si le tournoi est depuis le 1er juillet 2025
                if tournament_date >= july_1st:
                    recent_tournaments.append({
                        'id': tournament.get('id'),
                        'name': tournament.get('name'),
                        'date': tournament_date,
                        'date_str': tournament_date.strftime('%d/%m/%Y'),
                        'organization': tournament.get('organizationName', 'N/A'),
                        'game': tournament.get('gameDescription', ''),
                        'url': f"https://melee.gg/Tournament/{tournament.get('id')}"
                    })
            except Exception as e:
                continue
        
        # Trier par date (plus récent d'abord)
        recent_tournaments.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"\n🎯 Tournois Magic depuis le 1er juillet 2025: {len(recent_tournaments)}")
        print("=" * 80)
        
        if not recent_tournaments:
            print("❌ Aucun tournoi trouvé depuis le 1er juillet 2025")
            
            # Afficher quelques tournois récents pour debug
            print("\n🔍 Derniers tournois disponibles:")
            sample_tournaments = []
            for tournament in data[:10]:
                try:
                    start_date_str = tournament.get('startDate', '')
                    if start_date_str:
                        start_date_str = start_date_str.replace('Z', '').split('T')[0]
                        tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        sample_tournaments.append({
                            'name': tournament.get('name'),
                            'date': tournament_date.strftime('%d/%m/%Y')
                        })
                except:
                    continue
            
            for i, t in enumerate(sample_tournaments[:5]):
                print(f"  {i+1}. {t['name']} - {t['date']}")
        else:
            # Afficher les tournois trouvés
            for i, tournament in enumerate(recent_tournaments):
                print(f"\n🏆 {i+1}. {tournament['name']}")
                print(f"   📅 Date: {tournament['date_str']}")
                print(f"   🏢 Organisation: {tournament['organization']}")
                print(f"   🎮 Jeu: {tournament['game']}")
                print(f"   🔗 URL: {tournament['url']}")
        
        # Statistiques par mois
        if recent_tournaments:
            print(f"\n📊 Statistiques par mois:")
            monthly_counts = {}
            for tournament in recent_tournaments:
                month_key = tournament['date'].strftime('%Y-%m')
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            
            for month, count in sorted(monthly_counts.items()):
                month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                print(f"   {month_name}: {count} tournois")

if __name__ == "__main__":
    asyncio.run(show_melee_tournaments())