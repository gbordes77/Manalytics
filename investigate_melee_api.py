#!/usr/bin/env python3
"""
Investiguer l'API Melee pour comprendre comment récupérer les Round Standings
"""

import requests
from bs4 import BeautifulSoup
import json
from scrape_melee_flexible import MtgMeleeClientFlexible

def investigate_tournament_page():
    """Aller sur la page d'un tournoi pour comprendre la structure"""
    
    client = MtgMeleeClientFlexible()
    client.ensure_authenticated()
    
    # Tournoi Boa avec 16 joueurs
    tournament_id = 304273
    tournament_url = f"https://melee.gg/Tournament/View/{tournament_id}"
    
    print(f"🔍 Investigation du tournoi {tournament_id}")
    print(f"URL: {tournament_url}")
    print("=" * 60)
    
    # Récupérer la page du tournoi
    response = client.session.get(tournament_url)
    
    if response.status_code != 200:
        print(f"❌ Erreur: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Chercher les liens vers les standings
    print("\n📋 Recherche des liens standings...")
    
    # Chercher tous les liens qui contiennent "Standing" ou "Round"
    standing_links = soup.find_all('a', href=lambda x: x and ('Standing' in x or 'Round' in x))
    
    if standing_links:
        print(f"✅ {len(standing_links)} liens trouvés:")
        for link in standing_links[:10]:  # Afficher les 10 premiers
            href = link.get('href', '')
            text = link.text.strip()
            print(f"   - {text}: {href}")
    else:
        print("❌ Aucun lien standings trouvé")
    
    # Chercher les éléments data-* qui pourraient contenir des IDs
    print("\n🔍 Recherche d'éléments avec data-roundid...")
    elements_with_data = soup.find_all(attrs={"data-roundid": True})
    
    if elements_with_data:
        print(f"✅ {len(elements_with_data)} éléments trouvés:")
        for elem in elements_with_data[:5]:
            round_id = elem.get('data-roundid')
            print(f"   - Round ID: {round_id}")
    
    # Chercher dans les scripts JavaScript
    print("\n💻 Recherche dans les scripts JavaScript...")
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string and 'roundId' in script.string:
            print("✅ Script contenant 'roundId' trouvé:")
            # Extraire les lignes pertinentes
            lines = script.string.split('\n')
            for line in lines:
                if 'roundId' in line:
                    print(f"   {line.strip()[:100]}...")
    
    # Sauvegarder la page pour analyse manuelle
    with open('melee_tournament_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\n💾 Page sauvegardée dans melee_tournament_page.html pour analyse")
    
    # Tester différents formats de round ID
    print("\n🧪 Test de différents formats de Round ID...")
    
    # Format 1: Simple numéro
    test_round_id(client, tournament_id, 1)
    
    # Format 2: Tournament ID + Round Number
    test_round_id(client, tournament_id, f"{tournament_id}_1")
    
    # Format 3: Un ID aléatoire plus grand
    test_round_id(client, tournament_id, 1000000)


def test_round_id(client, tournament_id, round_id):
    """Tester un format de round ID"""
    print(f"\n   Test avec roundId = {round_id}")
    
    standings = client.get_round_standings(tournament_id, round_id)
    if standings:
        print(f"   ✅ Succès! {len(standings)} résultats")
    else:
        print(f"   ❌ Pas de données")


if __name__ == "__main__":
    investigate_tournament_page()