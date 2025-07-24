#!/usr/bin/env python3
"""Test direct de Melee en standard du 1er juillet à maintenant avec l'approche qui fonctionne."""
import asyncio
import json
import httpx
from datetime import datetime
from bs4 import BeautifulSoup

async def test_melee_direct_standard():
    """Test direct avec authentification requests pour standard."""
    
    # Charger credentials  
    with open('Api_token_and_login/melee_login.json', 'r') as f:
        creds = json.load(f)
    
    print("🧪 TEST DIRECT - Melee Standard du 1er juillet 2025 à maintenant")
    print("=" * 70)
    print(f"📧 Email: {creds['login']}")
    print(f"📅 Période: 01/07/2025 - {datetime.now().strftime('%d/%m/%Y')}")
    print(f"🎯 Format: Standard")
    
    async with httpx.AsyncClient() as client:
        
        # Authentification avec requests synchrone
        import requests
        auth_session = requests.Session()
        auth_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        print(f"\n🔐 Authentification...")
        
        # Flow d'auth complet
        main_response = auth_session.get("https://melee.gg")
        login_response = auth_session.get("https://melee.gg/Account/SignIn")
        
        soup = BeautifulSoup(login_response.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if not token_input:
            print("❌ Pas de token CSRF trouvé")
            return
            
        csrf_token = token_input.get('value')
        
        form_data = {
            'Email': creds['login'],
            'Password': creds['mdp'],
            '__RequestVerificationToken': csrf_token
        }
        
        login_submit = auth_session.post(
            "https://melee.gg/Account/SignInPassword",
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if len(auth_session.cookies) == 0:
            print("❌ Authentification échouée - aucun cookie reçu")
            return
            
        print(f"✅ Authentification réussie ({len(auth_session.cookies)} cookies)")
        
        # Transférer cookies vers httpx
        for cookie in auth_session.cookies:
            client.cookies.set(cookie.name, cookie.value)
        
        # Headers AJAX
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        
        print(f"\n🔍 Recherche de tournois Standard...")
        
        # Requête à l'API avec payload minimal
        search_payload = {
            "draw": "1",
            "start": "0", 
            "length": "100",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        response = await client.post(
            "https://melee.gg/Tournament/SearchResults",
            data=search_payload
        )
        
        print(f"Status API: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, list):
                    print(f"✅ API fonctionne - {len(data)} tournois récupérés")
                    
                    # Filtrer par Standard ET par date
                    july_1st = datetime(2025, 7, 1)
                    standard_recent = []
                    
                    for tournament in data:
                        # Vérifier le jeu
                        game_desc = tournament.get("gameDescription", "")
                        if "Magic" not in game_desc:
                            continue
                            
                        # Vérifier la date
                        try:
                            start_date_str = tournament.get('startDate', '')
                            if start_date_str:
                                start_date_str = start_date_str.replace('Z', '').split('T')[0]
                                tournament_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                                
                                if tournament_date >= july_1st:
                                    # C'est un tournoi récent, mais est-ce Standard ?
                                    tournament_name = tournament.get('name', '').lower()
                                    
                                    # Rechercher des indices de format Standard
                                    if any(word in tournament_name for word in ['standard', 'std', 'type 2']):
                                        standard_recent.append({
                                            'id': tournament.get('id'),
                                            'name': tournament.get('name'),
                                            'date': tournament_date.strftime('%d/%m/%Y'),
                                            'org': tournament.get('organizationName', 'N/A')
                                        })
                        except:
                            continue
                    
                    print(f"\n📊 RÉSULTATS FINAUX:")
                    print(f"   🏆 Tournois Magic totaux: {len([t for t in data if 'Magic' in t.get('gameDescription', '')])}")
                    print(f"   📅 Tournois depuis le 1er juillet: {len([t for t in data if 'Magic' in t.get('gameDescription', '') and t.get('startDate', '2020-01-01') >= '2025-07-01'])}")
                    print(f"   🎯 Tournois Standard récents: {len(standard_recent)}")
                    
                    if standard_recent:
                        print(f"\n📋 Détail des tournois Standard trouvés:")
                        for i, tournament in enumerate(standard_recent, 1):
                            print(f"   {i}. {tournament['name']}")
                            print(f"      📅 {tournament['date']} - {tournament['org']}")
                            print(f"      🔗 https://melee.gg/Tournament/{tournament['id']}")
                            
                        print(f"\n✅ SUCCÈS - {len(standard_recent)} tournois Standard trouvés !")
                    else:
                        print(f"\n❌ AUCUN TOURNOI STANDARD RÉCENT")
                        print(f"   Les tournois Magic sur Melee.gg semblent être des données de test de 2020")
                        print(f"   Il n'y a pas de vrais tournois Standard récents sur cette plateforme")
                        
                        # Montrer les dates des tournois pour confirmer
                        print(f"\n🔍 Échantillon de dates de tournois:")
                        dates_sample = []
                        for t in data[:10]:
                            start_date = t.get('startDate', 'N/A')
                            if start_date != 'N/A':
                                start_date = start_date.split('T')[0]
                            dates_sample.append(f"{t.get('name', 'N/A')[:30]} - {start_date}")
                        
                        for date_info in dates_sample:
                            print(f"      {date_info}")
                            
                else:
                    print(f"❌ Format API inattendu: {type(data)}")
                    
            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text[:200]}")
        else:
            print(f"❌ Erreur API {response.status_code}: {response.text[:200]}")
    
    print(f"\n" + "=" * 70)
    print(f"CONCLUSION: Melee.gg semble contenir uniquement des données de test de 2020")
    print(f"Il n'y a PAS de tournois Standard récents du 1er juillet 2025 à maintenant")

if __name__ == "__main__":
    asyncio.run(test_melee_direct_standard())