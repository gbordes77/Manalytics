#!/usr/bin/env python3
"""Vérifier si Melee.gg est un site actif avec de vrais tournois."""
import requests
from bs4 import BeautifulSoup
import re

def check_melee_site():
    """Vérifier l'état du site Melee.gg."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("🔍 Vérification du site Melee.gg...")
    
    # 1. Page principale
    print("\n🏠 Page principale:")
    try:
        main_page = session.get("https://melee.gg")
        print(f"  Status: {main_page.status_code}")
        
        soup = BeautifulSoup(main_page.text, 'html.parser')
        
        # Chercher des mentions de dates récentes
        text = soup.get_text()
        recent_years = ['2024', '2025']
        for year in recent_years:
            count = text.count(year)
            if count > 0:
                print(f"  Mentions de {year}: {count}")
        
        # Chercher le titre et description
        title = soup.find('title')
        if title:
            print(f"  Titre: {title.get_text().strip()}")
        
        # Chercher des meta descriptions
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            print(f"  Description: {description.get('content', '')[:100]}...")
        
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # 2. Page "About" ou informations
    print("\n📋 Page About/Info:")
    about_pages = ['/About', '/Info', '/Home/About']
    
    for page in about_pages:
        try:
            response = session.get(f"https://melee.gg{page}")
            if response.status_code == 200:
                print(f"  {page}: Accessible")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Chercher des informations sur le site
                text = soup.get_text()
                if 'test' in text.lower() or 'demo' in text.lower():
                    print(f"    ⚠️  Site de test/démo détecté")
                
                # Chercher des dates de dernière mise à jour
                date_patterns = [
                    r'(updated|last|copyright).*?(\d{4})',
                    r'(\d{1,2}/\d{1,2}/\d{4})',
                    r'(\d{4}-\d{1,2}-\d{1,2})'
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        print(f"    Dates trouvées: {matches[:3]}")
                        break
            else:
                print(f"  {page}: {response.status_code}")
        except:
            continue
    
    # 3. Chercher des tournois publics (sans auth)
    print("\n🏆 Recherche de tournois publics:")
    
    public_pages = [
        '/Tournament',
        '/Tournaments', 
        '/Public/Tournaments',
        '/Home/Tournaments'
    ]
    
    for page in public_pages:
        try:
            response = session.get(f"https://melee.gg{page}")
            print(f"  {page}: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Chercher des liens vers des tournois
                tournament_links = soup.find_all('a', href=re.compile(r'/Tournament/\d+'))
                if tournament_links:
                    print(f"    {len(tournament_links)} liens de tournois trouvés")
                
                # Chercher des dates récentes dans le texte
                text = soup.get_text()
                recent_dates = re.findall(r'(2024|2025)', text)
                if recent_dates:
                    print(f"    Dates récentes: {len(recent_dates)} mentions")
        except:
            continue
    
    # 4. Vérifier les formats Magic supportés
    print("\n🎮 Formats Magic supportés:")
    
    try:
        # La page de recherche pourrait montrer les formats disponibles
        search_page = session.get("https://melee.gg/Tournament/Search")
        if search_page.status_code == 200:
            soup = BeautifulSoup(search_page.text, 'html.parser')
            
            # Chercher des options de format
            selects = soup.find_all('select')
            for select in selects:
                if 'format' in str(select).lower():
                    options = select.find_all('option')
                    if options:
                        print("  Formats trouvés:")
                        for option in options[:10]:  # Limiter à 10
                            value = option.get('value', '')
                            text = option.get_text().strip()
                            if text and text != 'Select...':
                                print(f"    - {text} (value: {value})")
        
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # 5. Test final: Chercher des indices que c'est un site de production
    print("\n🔍 Analyse finale:")
    
    production_indicators = [
        'production', 'live', 'official', 'tournament management',
        'mtg melee', 'magic tournament', 'organized play'
    ]
    
    test_indicators = [
        'test', 'demo', 'sample', 'alpha', 'beta', 'development'
    ]
    
    try:
        main_content = session.get("https://melee.gg").text.lower()
        
        prod_count = sum(main_content.count(indicator) for indicator in production_indicators)
        test_count = sum(main_content.count(indicator) for indicator in test_indicators)
        
        print(f"  Indicateurs de production: {prod_count}")
        print(f"  Indicateurs de test: {test_count}")
        
        if test_count > prod_count:
            print("  ⚠️  Site probablement de test/démo")
        elif prod_count > 0:
            print("  ✅ Site probablement de production")
        else:
            print("  ❓ Statut indéterminé")
        
    except Exception as e:
        print(f"  Erreur d'analyse: {e}")

if __name__ == "__main__":
    check_melee_site()