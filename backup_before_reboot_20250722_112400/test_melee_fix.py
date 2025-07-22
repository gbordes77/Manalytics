#!/usr/bin/env python3
"""
Test et correction du problème Melee
Corriger les URLs et tester le scraping
"""

import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Ajouter le chemin pour les imports
sys.path.append(
    os.path.join(os.getcwd(), "src", "python", "scraper", "fbettega_clients")
)


def test_melee_tournament_urls():
    """Test avec les vraies URLs de tournois Melee"""

    print("🔍 TEST DES VRAIES URLS DE TOURNOIS MELEE")
    print("=" * 60)

    # URLs de tournois (pas de decklists)
    tournament_urls = [
        "https://melee.gg/Tournament/View/standard",
        "https://melee.gg/Tournament/View/",
        "https://melee.gg/Tournaments",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for url in tournament_urls:
        print(f"\n🔗 Test de : {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   📡 Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Chercher les tournois
                tournaments = soup.find_all("a", href=re.compile(r"/Tournament/"))
                print(f"   🏆 Tournois trouvés : {len(tournaments)}")

                # Afficher quelques exemples
                for i, tournament in enumerate(tournaments[:5]):
                    print(f"      {i+1}. {tournament.get_text().strip()}")
                    print(f"         URL: {tournament.get('href')}")

                # Chercher les tournois Standard
                standard_tournaments = []
                for tournament in tournaments:
                    text = tournament.get_text().lower()
                    if "standard" in text:
                        standard_tournaments.append(tournament)

                print(f"   🎯 Tournois Standard : {len(standard_tournaments)}")

            else:
                print(f"   ❌ Erreur d'accès")

        except Exception as e:
            print(f"   ❌ Erreur : {e}")


def test_melee_api():
    """Test de l'API Melee si elle existe"""

    print("\n🌐 TEST DE L'API MELEE")
    print("=" * 40)

    # URLs d'API possibles
    api_urls = [
        "https://melee.gg/api/tournaments",
        "https://melee.gg/api/v1/tournaments",
        "https://melee.gg/api/tournaments/standard",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
    }

    for url in api_urls:
        print(f"\n🔗 Test API : {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   📡 Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON valide")
                    print(f"   📊 Type de données : {type(data)}")

                    if isinstance(data, list):
                        print(f"   📋 Nombre d'éléments : {len(data)}")
                        if data:
                            print(f"   📝 Premier élément : {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"   📋 Clés disponibles : {list(data.keys())}")

                except json.JSONDecodeError:
                    print(f"   ❌ Pas de JSON valide")
            else:
                print(f"   ❌ Erreur d'accès")

        except Exception as e:
            print(f"   ❌ Erreur : {e}")


def test_melee_search():
    """Test de recherche sur Melee"""

    print("\n🔍 TEST DE RECHERCHE MELEE")
    print("=" * 40)

    # Test de recherche Standard
    search_url = "https://melee.gg/Tournament/Search"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"📡 Status recherche : {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Chercher les formulaires de recherche
            forms = soup.find_all("form")
            print(f"📋 Formulaires trouvés : {len(forms)}")

            # Chercher les champs de recherche
            inputs = soup.find_all("input")
            print(f"🔍 Champs de saisie : {len(inputs)}")

            for input_field in inputs[:5]:
                input_type = input_field.get("type", "unknown")
                input_name = input_field.get("name", "no-name")
                print(f"   📝 {input_name} ({input_type})")

    except Exception as e:
        print(f"❌ Erreur recherche : {e}")


def test_melee_decklist_extraction():
    """Test d'extraction de decklists depuis les URLs fournies"""

    print("\n🃏 TEST D'EXTRACTION DE DECKLISTS")
    print("=" * 50)

    # URLs de decklists de la liste
    decklist_urls = [
        "https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58",
        "https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for url in decklist_urls:
        print(f"\n🔗 Test decklist : {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   📡 Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Chercher les informations du deck
                title = soup.find("title")
                if title:
                    print(f"   📋 Titre: {title.get_text().strip()}")

                # Chercher les cartes
                cards = soup.find_all("div", class_=re.compile(r"card|deck"))
                print(f"   🃏 Éléments de cartes trouvés : {len(cards)}")

                # Chercher les liens vers le tournoi
                tournament_links = soup.find_all("a", href=re.compile(r"/Tournament/"))
                print(f"   🏆 Liens vers tournois : {len(tournament_links)}")

                for link in tournament_links[:3]:
                    print(f"      🔗 {link.get('href')}")

                # Chercher les informations du joueur
                player_info = soup.find_all("div", class_=re.compile(r"player|user"))
                print(f"   👤 Éléments joueur : {len(player_info)}")

            else:
                print(f"   ❌ Erreur d'accès")

        except Exception as e:
            print(f"   ❌ Erreur : {e}")


def fix_melee_client():
    """Corriger le client Melee"""

    print("\n🔧 CORRECTION DU CLIENT MELEE")
    print("=" * 40)

    melee_client_file = Path("src/python/scraper/fbettega_clients/melee_client.py")

    if melee_client_file.exists():
        print(f"✅ Fichier client trouvé : {melee_client_file}")

        # Lire le contenu
        with open(melee_client_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Vérifier les imports relatifs
        if "from ." in content or "import ." in content:
            print("   ⚠️ Imports relatifs détectés")

            # Corriger les imports
            content = content.replace("from .", "from ")
            content = content.replace("import .", "import ")

            # Sauvegarder la version corrigée
            fixed_file = Path("melee_client_fixed.py")
            with open(fixed_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"   ✅ Version corrigée sauvegardée : {fixed_file}")

        else:
            print("   ✅ Pas d'imports relatifs détectés")

    else:
        print(f"❌ Fichier client non trouvé")


def main():
    """Fonction principale"""
    try:
        # Tests complets
        test_melee_tournament_urls()
        test_melee_api()
        test_melee_search()
        test_melee_decklist_extraction()
        fix_melee_client()

        print("\n🎯 CONCLUSIONS :")
        print("   1. Melee a probablement changé sa structure")
        print("   2. Les URLs fournies pointent vers des decklists individuelles")
        print("   3. Il faut trouver les vraies URLs de tournois")
        print("   4. Le client Melee a des problèmes d'imports")
        print("   5. Il faudrait peut-être utiliser une approche différente")

    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
