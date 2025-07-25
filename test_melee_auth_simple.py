#!/usr/bin/env python3
"""
Test simple de l'authentification Melee.gg avec requests
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os

def test_melee_auth():
    """Test de connexion Melee.gg avec requests (comme le code original)"""
    
    # Session requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    print("🔐 Test d'authentification Melee.gg avec requests...")
    
    # Étape 1: Récupérer la page de login pour obtenir le token CSRF
    print("\n1️⃣ Récupération du token CSRF...")
    login_page = session.get("https://melee.gg/Account/SignIn")
    print(f"   Status: {login_page.status_code}")
    
    if login_page.status_code != 200:
        print(f"❌ Erreur: impossible d'accéder à la page de login")
        return False
        
    # Parser le HTML pour trouver le token
    soup = BeautifulSoup(login_page.text, "html.parser")
    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    
    if not token_input:
        print("❌ Token CSRF non trouvé dans la page")
        # Sauvegarder la page pour debug
        with open("login_page_debug.html", "w", encoding="utf-8") as f:
            f.write(login_page.text)
        print("   Page sauvegardée dans login_page_debug.html")
        return False
        
    token = token_input.get("value")
    print(f"✅ Token trouvé: {token[:20]}...")
    
    # Étape 2: Se connecter
    print("\n2️⃣ Tentative de connexion...")
    
    # Charger les credentials
    cred_file = "api_credentials/melee_login.json"
    with open(cred_file, "r") as f:
        creds = json.load(f)
    
    # Headers AJAX pour la connexion
    ajax_headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://melee.gg",
        "Referer": "https://melee.gg/Account/SignIn"
    }
    
    login_data = {
        "email": creds["login"],
        "password": creds["mdp"],
        "__RequestVerificationToken": token
    }
    
    # POST login
    response = session.post(
        "https://melee.gg/Account/SignInPassword",
        headers=ajax_headers,
        data=login_data
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    # Vérifier si on a le cookie d'auth
    if ".AspNet.ApplicationCookie" in session.cookies:
        print("✅ Cookie d'authentification présent!")
        
        # Sauvegarder les cookies
        cookies_to_save = {
            "cookies": session.cookies.get_dict(),
            "_timestamp": time.time()
        }
        
        os.makedirs("api_credentials", exist_ok=True)
        with open("api_credentials/melee_cookies.json", "w") as f:
            json.dump(cookies_to_save, f, indent=2)
        print("💾 Cookies sauvegardés dans api_credentials/melee_cookies.json")
        
        # Étape 3: Tester l'accès aux tournois
        print("\n3️⃣ Test de recherche de tournois...")
        
        # Payload de test pour chercher des tournois
        test_payload = {
            "draw": "1",
            "columns[0][data]": "DecklistName",
            "columns[1][data]": "Game",
            "columns[1][search][value]": "MagicTheGathering",
            "columns[6][data]": "SortDate",
            "columns[6][search][value]": "2025-07-01|2025-07-25",
            "order[0][column]": "6",
            "order[0][dir]": "desc",
            "start": "0",
            "length": "10",
            "__RequestVerificationToken": token  # Inclure le token
        }
        
        search_response = session.post(
            "https://melee.gg/Decklist/SearchDecklists",
            data=test_payload
        )
        
        print(f"   Status: {search_response.status_code}")
        
        if search_response.status_code == 200 and search_response.text.strip():
            try:
                data = search_response.json()
                if "data" in data:
                    print(f"✅ Recherche réussie! {len(data['data'])} résultats")
                    if data['data']:
                        print("\n📋 Premier tournoi trouvé:")
                        first = data['data'][0]
                        print(f"   - Nom: {first.get('TournamentName')}")
                        print(f"   - Date: {first.get('TournamentStartDate')}")
                        print(f"   - Format: {first.get('FormatDescription')}")
                else:
                    print("⚠️ Réponse JSON mais pas de données")
            except json.JSONDecodeError:
                print("❌ Réponse non-JSON")
                print(f"   Début de la réponse: {search_response.text[:200]}")
        else:
            print("❌ Échec de la recherche")
            
        return True
        
    else:
        print("❌ Pas de cookie d'authentification - échec de connexion")
        return False

if __name__ == "__main__":
    success = test_melee_auth()
    if success:
        print("\n✅ Test réussi! L'authentification fonctionne.")
        print("\n🎯 Prochaine étape: utiliser le scraper avec les cookies sauvegardés")
    else:
        print("\n❌ Test échoué. Vérifier les credentials et la connexion internet.")