#!/usr/bin/env python3
"""
Analyse détaillée du Challenge manquant
Comprendre pourquoi nous avons un Challenge en moins
"""

import json
import re
from datetime import datetime
from pathlib import Path


def analyze_missing_challenge():
    """Analyse le Challenge manquant en détail"""

    print("🔍 ANALYSE DÉTAILLÉE DU CHALLENGE MANQUANT")
    print("=" * 60)

    # Liste fournie par l'utilisateur
    liste_challenges = [
        "Standard Challenge 64 2025-07-01 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0112801190",
        "Standard Challenge 32 2025-07-03 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0312801623",
        "Standard Challenge 32 2025-07-04 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0412801637",
        "Standard Challenge 32 2025-07-05 - https://www.mtgo.com/decklist/standard-challenge-32-2025-05-2512801654",
        "Standard Challenge 32 2025-07-06 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0612801677",
        "Standard Challenge 64 2025-07-07 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0712801688",
        "Standard Challenge 64 2025-07-08 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0812801696",
        "Standard Challenge 32 2025-07-10 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1012802771",
        "Standard Challenge 32 2025-07-11 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1112802789",
        "Standard Challenge 32 2025-07-12 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1212802811",
        "Standard Challenge 32 2025-07-13 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1312802841",
        "Standard Challenge 64 2025-07-14 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1412802856",
        "Standard Challenge 64 2025-07-15 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1512802868",
        "Standard Challenge 32 2025-07-17 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1712803657",
        "Standard Challenge 32 2025-07-18 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1812803671",
        "Standard Challenge 32 2025-07-19 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1912803688",
    ]

    # Charger nos données scrapées
    mtgo_file = Path("data/processed/mtgo_standard_july_2025.json")
    with open(mtgo_file, "r", encoding="utf-8") as f:
        mtgo_data = json.load(f)

    # Extraire les Challenges de la liste
    liste_parsed = []
    for line in liste_challenges:
        match = re.match(
            r"(Standard Challenge \d+) (\d{4}-\d{2}-\d{2}) - (https://www\.mtgo\.com/decklist/.*?)(\d+)$",
            line,
        )
        if match:
            name = match.group(1)
            date = match.group(2)
            url = match.group(3) + match.group(4)
            id_num = match.group(4)

            liste_parsed.append({"name": name, "date": date, "url": url, "id": id_num})

    # Extraire nos Challenges scrapées
    scraped_challenges = []
    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")

        if "Challenge" in name:
            uri = tournament.get("Uri", "")
            id_match = re.search(r"(\d+)$", uri)
            id_num = id_match.group(1) if id_match else "unknown"

            scraped_challenges.append(
                {
                    "name": name,
                    "date": tournament.get("Date", ""),
                    "url": uri,
                    "id": id_num,
                    "deck_count": len(tournament_entry.get("decks", [])),
                    "raw_entry": tournament_entry,
                }
            )

    print(f"📊 TOTAUX :")
    print(f"   • Liste fournie : {len(liste_parsed)} Challenges")
    print(f"   • Scraped : {len(scraped_challenges)} Challenges")
    print()

    # Créer des sets pour comparaison
    liste_ids = {c["id"] for c in liste_parsed}
    scraped_ids = {c["id"] for c in scraped_challenges}

    print(f"🔍 ANALYSE PAR ID :")
    print(f"   • IDs dans liste : {len(liste_ids)}")
    print(f"   • IDs scrapés : {len(scraped_ids)}")
    print()

    # Trouver les différences
    missing_in_scraped = liste_ids - scraped_ids
    extra_in_scraped = scraped_ids - liste_ids

    if missing_in_scraped:
        print(f"❌ IDS MANQUANTS DANS SCRAPED ({len(missing_in_scraped)}) :")
        for missing_id in missing_in_scraped:
            # Trouver les détails dans la liste
            for challenge in liste_parsed:
                if challenge["id"] == missing_id:
                    print(f"   🚨 ID: {missing_id}")
                    print(f"      Nom: {challenge['name']}")
                    print(f"      Date: {challenge['date']}")
                    print(f"      URL: {challenge['url']}")
                    print()
                    break

    if extra_in_scraped:
        print(f"➕ IDS EN PLUS DANS SCRAPED ({len(extra_in_scraped)}) :")
        for extra_id in extra_in_scraped:
            # Trouver les détails dans scraped
            for challenge in scraped_challenges:
                if challenge["id"] == extra_id:
                    print(f"   ✅ ID: {extra_id}")
                    print(f"      Nom: {challenge['name']}")
                    print(f"      Date: {challenge['date']}")
                    print(f"      Decks: {challenge['deck_count']}")
                    print(f"      URL: {challenge['url']}")
                    print()
                    break

    # Analyser par date
    print(f"📅 ANALYSE PAR DATE :")
    liste_by_date = {}
    scraped_by_date = {}

    for challenge in liste_parsed:
        date = challenge["date"]
        if date not in liste_by_date:
            liste_by_date[date] = []
        liste_by_date[date].append(challenge)

    for challenge in scraped_challenges:
        date = challenge["date"]
        if date not in scraped_by_date:
            scraped_by_date[date] = []
        scraped_by_date[date].append(challenge)

    all_dates = set(liste_by_date.keys()) | set(scraped_by_date.keys())

    for date in sorted(all_dates):
        liste_count = len(liste_by_date.get(date, []))
        scraped_count = len(scraped_by_date.get(date, []))

        print(f"   📅 {date}:")
        print(f"      Liste: {liste_count} Challenge(s)")
        print(f"      Scraped: {scraped_count} Challenge(s)")

        if liste_count != scraped_count:
            print(f"      ⚠️ DIFFÉRENCE DÉTECTÉE !")

            # Détails des Challenges de la liste
            if date in liste_by_date:
                print(f"      Liste IDs: {[c['id'] for c in liste_by_date[date]]}")

            # Détails des Challenges scrapées
            if date in scraped_by_date:
                print(f"      Scraped IDs: {[c['id'] for c in scraped_by_date[date]]}")

        print()

    # Vérifier les URLs spécifiques
    print(f"🔗 VÉRIFICATION DES URLS :")
    liste_urls = {c["url"] for c in liste_parsed}
    scraped_urls = {c["url"] for c in scraped_challenges}

    missing_urls = liste_urls - scraped_urls
    if missing_urls:
        print(f"   ❌ URLs manquantes dans scraped :")
        for url in missing_urls:
            print(f"      {url}")

    extra_urls = scraped_urls - liste_urls
    if extra_urls:
        print(f"   ✅ URLs en plus dans scraped :")
        for url in extra_urls:
            print(f"      {url}")

    return missing_in_scraped, extra_in_scraped


def main():
    """Fonction principale"""
    try:
        missing, extra = analyze_missing_challenge()

        print("\n🎯 CONCLUSIONS :")
        if missing:
            print(f"   • {len(missing)} Challenge(s) manquante(s) dans nos données")
            print(f"   • Problème potentiel de scraping ou de filtrage")
        else:
            print(f"   • Aucune Challenge manquante détectée")

        if extra:
            print(f"   • {len(extra)} Challenge(s) supplémentaire(s) trouvée(s)")
            print(f"   • Notre scraper est plus complet que la liste")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
