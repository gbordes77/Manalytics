#!/usr/bin/env python3
"""
Script pour tester l'authentification Melee.gg et extraire le token.
"""
import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def test_melee_authentication():
    """Test Selenium authentication and token extraction."""
    
    # Charger les credentials
    cred_file = "api_credentials/melee_login.json"
    if not os.path.exists(cred_file):
        print(f"❌ Fichier de credentials non trouvé: {cred_file}")
        return
        
    with open(cred_file, "r") as f:
        creds = json.load(f)
    
    email = creds["login"]
    password = creds["mdp"]
    
    print("🔐 Testing Melee.gg authentication...")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    
    options = webdriver.ChromeOptions()
    # Options pour Chrome
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        print("\n📡 Démarrage du navigateur...")
        # Utiliser Chrome local (pas Docker pour le moment)
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Aller sur la page d'accueil d'abord
        print("🌐 Navigation vers Melee.gg...")
        driver.get("https://melee.gg/")
        time.sleep(2)
        
        # Aller sur la page de login
        print("🌐 Navigation vers la page de login...")
        driver.get("https://melee.gg/Account/SignIn")
        time.sleep(2)
        
        # Attendre le formulaire
        wait = WebDriverWait(driver, 15)
        
        # Chercher le champ email par différents sélecteurs
        print("📝 Recherche du formulaire de login...")
        email_field = None
        
        # Essayer différents sélecteurs
        selectors = [
            (By.ID, "Email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name='email']"),
            (By.CSS_SELECTOR, "#Email")
        ]
        
        for by, selector in selectors:
            try:
                email_field = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"✅ Champ email trouvé avec le sélecteur: {by} = {selector}")
                break
            except:
                continue
                
        if not email_field:
            print("❌ Impossible de trouver le champ email")
            # Sauvegarder la page pour debug
            with open("login_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📄 Page HTML sauvegardée dans login_page.html")
            return
        
        print("📝 Remplissage du formulaire...")
        email_field.clear()
        email_field.send_keys(email)
        
        # Chercher le champ password
        password_field = driver.find_element(By.ID, "Password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Screenshot avant soumission
        driver.save_screenshot("before_login.png")
        print("📸 Screenshot sauvegardé: before_login.png")
        
        # Soumettre le formulaire
        print("🚀 Soumission du formulaire...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Attendre la redirection
        print("⏳ Attente de la connexion...")
        time.sleep(5)
        
        # Screenshot après login
        driver.save_screenshot("after_login.png")
        print("📸 Screenshot sauvegardé: after_login.png")
        
        current_url = driver.current_url
        print(f"📍 URL actuelle: {current_url}")
        
        if "signin" in current_url.lower() or "login" in current_url.lower():
            print("❌ Toujours sur la page de login - échec de connexion")
            # Chercher les messages d'erreur
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".validation-summary-errors, .text-danger, .error-message")
            for elem in error_elements:
                if elem.text:
                    print(f"⚠️ Erreur: {elem.text}")
        else:
            print("✅ Connexion réussie!")
            
            # Extraire les cookies
            print("\n🍪 Extraction des cookies...")
            cookies = driver.get_cookies()
            cookie_dict = {}
            
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
                print(f"  - {cookie['name']}: {cookie['value'][:20]}...")
            
            # Sauvegarder les cookies
            cookie_file = "api_credentials/melee_cookies.json"
            with open(cookie_file, "w") as f:
                json.dump({
                    "cookies": cookie_dict,
                    "_timestamp": time.time()
                }, f, indent=2)
            print(f"💾 Cookies sauvegardés dans {cookie_file}")
            
            # Tester l'accès API
            print("\n🧪 Test d'accès aux données...")
            driver.get("https://melee.gg/Decklist/TournamentSearch")
            time.sleep(3)
            
            # Vérifier si on peut voir des tournois
            if "login" not in driver.current_url.lower():
                print("✅ Accès aux tournois confirmé!")
                
                # Essayer de récupérer le token CSRF de la page
                try:
                    token_element = driver.find_element(By.NAME, "__RequestVerificationToken")
                    token = token_element.get_attribute("value")
                    print(f"🔑 Token CSRF trouvé: {token[:20]}...")
                    
                    # Sauvegarder le token avec les cookies
                    with open(cookie_file, "r") as f:
                        cookie_data = json.load(f)
                    cookie_data["csrf_token"] = token
                    with open(cookie_file, "w") as f:
                        json.dump(cookie_data, f, indent=2)
                    print("💾 Token CSRF ajouté aux cookies")
                    
                except:
                    print("⚠️ Token CSRF non trouvé sur cette page")
            else:
                print("❌ Redirigé vers login - les cookies ne suffisent pas")
        
        print("\n✅ Test terminé!")
        
        # Attendre un peu avant de fermer
        time.sleep(3)
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ Erreur pendant l'authentification: {e}")
        import traceback
        traceback.print_exc()
        
        # Sauvegarder la page actuelle pour debug
        try:
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📄 Page d'erreur sauvegardée dans error_page.html")
            driver.save_screenshot("error_screenshot.png")
            print("📸 Screenshot d'erreur: error_screenshot.png")
        except:
            pass
            
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_melee_authentication()