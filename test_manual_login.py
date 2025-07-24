#!/usr/bin/env python3
"""Test manuel de l'authentification Melee avec requests."""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Ajouter le projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def test_manual_login():
    """Test d'authentification manuelle avec requests."""
    print("🧪 Testing manual Melee.gg authentication...")
    print(f"Email: {settings.MELEE_EMAIL}")
    print(f"Password: {'*' * len(settings.MELEE_PASSWORD)}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        # Étape 1: Aller sur la page principale
        print("📡 Getting main page...")
        main_response = session.get("https://melee.gg")
        print(f"Main page status: {main_response.status_code}")
        print(f"Cookies after main: {len(session.cookies)}")
        
        for cookie in session.cookies:
            print(f"  Cookie: {cookie.name} = {cookie.value[:20]}...")
        
        # Étape 2: Aller sur la page de login (CORRECT ENDPOINT)
        print("📝 Getting login page...")
        login_response = session.get("https://melee.gg/Account/SignIn")
        print(f"Login page status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login page returned {login_response.status_code}")
            print(f"Response: {login_response.text[:500]}")
            return
        
        # Étape 3: Parser le formulaire de login pour les tokens CSRF
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Chercher le token de vérification ASP.NET
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if not token_input:
            print("❌ No CSRF token found!")
            return
            
        csrf_token = token_input.get('value')
        print(f"Found CSRF token: {csrf_token[:20]}...")
        
        form_data = {
            'Email': settings.MELEE_EMAIL,
            'Password': settings.MELEE_PASSWORD,
            '__RequestVerificationToken': csrf_token
        }
        
        # Étape 4: Soumettre le formulaire (CORRECT ENDPOINT)
        print("🚀 Submitting login form...")
        login_submit = session.post(
            "https://melee.gg/Account/SignInPassword",
            data=form_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://melee.gg/Account/SignIn'
            },
            allow_redirects=True
        )
        
        print(f"Login submit status: {login_submit.status_code}")
        print(f"Final URL: {login_submit.url}")
        print(f"Cookies after login: {len(session.cookies)}")
        
        # Vérifier si on est connecté
        if "login" not in login_submit.url.lower() and "error" not in login_submit.url.lower():
            print("✅ Login seems successful!")
            
            # Tester un appel API
            print("🧪 Testing API call...")
            api_response = session.get("https://melee.gg/Tournament/Search")
            print(f"API status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                print("✅ API access works!")
            else:
                print(f"❌ API returned {api_response.status_code}")
        else:
            print("❌ Login failed - still on login/error page")
            print(f"Response: {login_submit.text[:500]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_login()