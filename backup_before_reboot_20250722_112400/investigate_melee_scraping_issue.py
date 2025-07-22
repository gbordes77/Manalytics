#!/usr/bin/env python3
"""
Investigation du problème de scraping Melee
Pourquoi aucun deck Melee n'a été récupéré
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def investigate_melee_issue():
    """Investigue le problème de scraping Melee"""

    print("🔍 INVESTIGATION DU PROBLÈME MELEE")
    print("=" * 60)

    # Vérifier les données scrapées
    melee_file = Path("data/processed/melee_standard_july_2025.json")

    if melee_file.exists():
        with open(melee_file, "r", encoding="utf-8") as f:
            melee_data = json.load(f)
        print(f"📊 Données Melee trouvées : {len(melee_data)} entrées")
    else:
        print("❌ Fichier Melee non trouvé")
        melee_data = []

    # Vérifier les données brutes
    raw_melee_dir = Path("data/raw/melee/2025")
    if raw_melee_dir.exists():
        print(f"📁 Dossier raw Melee trouvé : {raw_melee_dir}")
        raw_files = list(raw_melee_dir.rglob("*.json"))
        print(f"   Fichiers raw : {len(raw_files)}")

        for file in raw_files[:5]:  # Afficher les 5 premiers
            print(f"   📄 {file.name}")
    else:
        print("❌ Dossier raw Melee non trouvé")

    # Analyser le script de scraping
    print("\n🔧 ANALYSE DU SCRIPT DE SCRAPING :")
    analyze_scraping_script()

    # Tester le scraping Melee en direct
    print("\n🌐 TEST DE SCRAPING MELEE EN DIRECT :")
    test_melee_scraping()

    # Vérifier les tournois Melee dans la liste fournie
    print("\n📋 ANALYSE DES TOURNOIS MELEE DE LA LISTE :")
    analyze_melee_tournaments_from_list()


def analyze_scraping_script():
    """Analyse le script de scraping"""

    # Vérifier le client Melee
    melee_client_file = Path("src/python/scraper/fbettega_clients/melee_client.py")
    if melee_client_file.exists():
        print(f"✅ Client Melee trouvé : {melee_client_file}")

        # Lire le contenu pour vérifier la configuration
        with open(melee_client_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Vérifier les paramètres importants
        if "Standard" in content:
            print("   ✅ Filtre Standard présent")
        else:
            print("   ❌ Filtre Standard manquant")

        if "2025-07-01" in content or "2025-07-20" in content:
            print("   ✅ Période de date configurée")
        else:
            print("   ❌ Période de date non trouvée")

    else:
        print(f"❌ Client Melee non trouvé : {melee_client_file}")

    # Vérifier le script de scraping
    scraping_script = Path("scrape_standard_july.py")
    if scraping_script.exists():
        print(f"✅ Script de scraping trouvé : {scraping_script}")

        with open(scraping_script, "r", encoding="utf-8") as f:
            content = f.read()

        if "melee" in content.lower():
            print("   ✅ Melee inclus dans le script")
        else:
            print("   ❌ Melee non inclus dans le script")
    else:
        print(f"❌ Script de scraping non trouvé : {scraping_script}")


def test_melee_scraping():
    """Test de scraping Melee en direct"""

    print("   🔍 Test de connexion à Melee...")

    try:
        # Test de base
        url = "https://melee.gg/Tournament/View/standard"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(f"   📡 Status code: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Connexion réussie")

            # Analyser le contenu
            soup = BeautifulSoup(response.content, "html.parser")

            # Chercher les tournois
            tournaments = soup.find_all("a", href=re.compile(r"/Tournament/View/"))
            print(f"   🏆 Tournois trouvés : {len(tournaments)}")

            # Chercher les tournois Standard
            standard_tournaments = []
            for tournament in tournaments:
                text = tournament.get_text().lower()
                if "standard" in text:
                    standard_tournaments.append(tournament)

            print(f"   🎯 Tournois Standard trouvés : {len(standard_tournaments)}")

            # Afficher quelques exemples
            for i, tournament in enumerate(standard_tournaments[:3]):
                print(f"      {i+1}. {tournament.get_text().strip()}")
                print(f"         URL: {tournament.get('href')}")

        else:
            print(f"   ❌ Erreur de connexion : {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erreur lors du test : {e}")


def analyze_melee_tournaments_from_list():
    """Analyse les tournois Melee de la liste fournie"""

    # Liste des tournois Melee de la liste fournie
    melee_tournaments = [
        "TheGathering.gg Standard Post-BNR Celebration 2025-07-02 - https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58",
        "TheGathering.gg Standard Post-BNR Celebration #2 2025-07-02 - https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4",
        "第2回シングルスター杯　サブイベント 2025-07-06 - https://melee.gg/Decklist/View/58391bb8-9d9a-4c34-98af-b31100d6d6ea",
        "Jaffer's Tarkir Dragonstorm Mosh Pit 2025-07-06 - https://melee.gg/Decklist/View/ddae0ba9-a4d7-4708-9e0b-b2cc003d55e2",
        "F2F Tour Red Deer - Sunday Super Qualifier 2025-07-06 - https://melee.gg/Decklist/View/f9fbb177-1238-4e17-8146-b31201842d46",
        "Valley Dasher's Bishkek Classic #1 2025-07-12 - https://melee.gg/Decklist/View/d11c46a4-4cdb-4603-bf82-b317008faa42",
        "Jaffer's Final Fantasy Mosh Pit 2025-07-13 - https://melee.gg/Decklist/View/07f0edf6-0180-447c-b258-b3190103047b",
        "Boa Qualifier #2 2025 (standard) 2025-07-19 - https://melee.gg/Decklist/View/e87b4ce1-7121-44ad-a9be-b31f00927479",
    ]

    print(f"   📊 Tournois Melee dans la liste : {len(melee_tournaments)}")

    # Analyser chaque tournoi
    for i, tournament in enumerate(melee_tournaments, 1):
        print(f"\n   🏆 Tournoi {i}:")

        # Extraire les informations
        match = re.match(
            r"(.*?) (\d{4}-\d{2}-\d{2}) - (https://melee\.gg/Decklist/View/.*)",
            tournament,
        )
        if match:
            name = match.group(1)
            date = match.group(2)
            url = match.group(3)

            print(f"      📝 Nom: {name}")
            print(f"      📅 Date: {date}")
            print(f"      🔗 URL: {url}")

            # Tester l'accès au tournoi
            test_tournament_access(url, name)
        else:
            print(f"      ❌ Format non reconnu: {tournament}")


def test_tournament_access(url, name):
    """Test l'accès à un tournoi spécifique"""

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"      ✅ Accès réussi")

            # Analyser le contenu
            soup = BeautifulSoup(response.content, "html.parser")

            # Chercher les decklists
            decklists = soup.find_all("a", href=re.compile(r"/Decklist/View/"))
            print(f"      🃏 Decklists trouvées : {len(decklists)}")

            # Chercher les informations du tournoi
            tournament_info = soup.find("h1") or soup.find("title")
            if tournament_info:
                print(f"      📋 Titre: {tournament_info.get_text().strip()}")

        else:
            print(f"      ❌ Erreur d'accès : {response.status_code}")

    except Exception as e:
        print(f"      ❌ Erreur lors du test : {e}")


def check_melee_client_configuration():
    """Vérifie la configuration du client Melee"""

    print("\n⚙️ VÉRIFICATION DE LA CONFIGURATION MELEE :")

    try:
        # Importer le client Melee
        import sys

        sys.path.append("src/python/scraper/fbettega_clients")

        from melee_client import MtgMeleeClient

        # Créer une instance du client
        client = MtgMeleeClient()

        print("   ✅ Client Melee importé avec succès")

        # Vérifier les méthodes disponibles
        methods = [method for method in dir(client) if not method.startswith("_")]
        print(f"   📋 Méthodes disponibles : {len(methods)}")

        # Chercher les méthodes importantes
        important_methods = ["get_tournaments", "get_decklists", "scrape"]
        for method in important_methods:
            if method in methods:
                print(f"      ✅ {method}")
            else:
                print(f"      ❌ {method} manquant")

    except ImportError as e:
        print(f"   ❌ Erreur d'import : {e}")
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification : {e}")


def main():
    """Fonction principale"""
    try:
        investigate_melee_issue()

        # Vérification supplémentaire de la configuration
        check_melee_client_configuration()

        print("\n🎯 CONCLUSIONS ET RECOMMANDATIONS :")
        print("   1. Vérifier si le client Melee est correctement configuré")
        print("   2. Tester l'accès aux URLs Melee spécifiques")
        print("   3. Vérifier les filtres de format et de date")
        print("   4. Analyser les logs d'erreur du scraping")
        print("   5. Comparer avec la configuration de fbettega originale")

    except Exception as e:
        print(f"❌ Erreur lors de l'investigation : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
