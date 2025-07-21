#!/usr/bin/env python3
"""
Vérification de la classification des tournois
Analyse si des Leagues ont été mal classées dans les Challenges
"""

import json
from collections import defaultdict
from pathlib import Path


def analyze_tournament_classification():
    """Analyse la classification des tournois MTGO"""

    # Charger les données MTGO
    mtgo_file = Path("data/processed/mtgo_standard_july_2025.json")
    with open(mtgo_file, "r", encoding="utf-8") as f:
        mtgo_data = json.load(f)

    print("🔍 ANALYSE DE LA CLASSIFICATION DES TOURNOIS")
    print("=" * 60)

    # Analyser tous les noms de tournois
    all_tournaments = []
    leagues = []
    challenges = []
    autres = []

    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")
        uri = tournament.get("Uri", "")
        date = tournament.get("Date", "")
        deck_count = len(tournament_entry.get("decks", []))
        decks = tournament_entry.get("decks", [])

        tournament_info = {
            "name": name,
            "uri": uri,
            "date": date,
            "deck_count": deck_count,
            "decks": decks,
        }

        all_tournaments.append(tournament_info)

        # Classification actuelle
        if "League" in name:
            leagues.append(tournament_info)
        elif "Challenge" in name:
            challenges.append(tournament_info)
        else:
            autres.append(tournament_info)

    print(f"📊 TOTAUX :")
    print(f"   • Total tournois : {len(all_tournaments)}")
    print(f"   • Leagues : {len(leagues)}")
    print(f"   • Challenges : {len(challenges)}")
    print(f"   • Autres : {len(autres)}")
    print()

    # Analyser les noms de tournois par catégorie
    print("🏅 LEAGUES DÉTECTÉES :")
    for league in leagues:
        has_5_0 = any(deck.get("Result") == "5-0" for deck in league["decks"])
        print(
            f"   • {league['name']} ({league['date']}) - {league['deck_count']} decks - 5-0: {'Oui' if has_5_0 else 'Non'}"
        )
    print()

    print("⚔️ CHALLENGES DÉTECTÉES :")
    suspicious_challenges = []
    for challenge in challenges:
        print(
            f"   • {challenge['name']} ({challenge['date']}) - {challenge['deck_count']} decks"
        )

        # Vérifier si c'est suspect (contient League dans le nom)
        if "League" in challenge["name"]:
            suspicious_challenges.append(challenge)
    print()

    print("🎲 AUTRES TOURNOIS :")
    for autre in autres:
        print(f"   • {autre['name']} ({autre['date']}) - {autre['deck_count']} decks")
    print()

    # Alertes
    if suspicious_challenges:
        print("⚠️ ALERTES - CHALLENGES SUSPECTS (contiennent 'League') :")
        for suspect in suspicious_challenges:
            print(f"   🚨 {suspect['name']} - Peut-être mal classifié ?")
        print()

    # Analyser les patterns de noms
    print("📋 ANALYSE DES PATTERNS DE NOMS :")
    name_patterns = defaultdict(int)
    for tournament in all_tournaments:
        # Extraire le type principal (premier mot)
        words = tournament["name"].split()
        if words:
            pattern = words[0]
            name_patterns[pattern] += 1

    for pattern, count in sorted(
        name_patterns.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   • {pattern}: {count} tournois")
    print()

    # Vérifier la cohérence des résultats
    print("🎯 ANALYSE DES RÉSULTATS :")
    for tournament in all_tournaments:
        results = [deck.get("Result", "") for deck in tournament["decks"]]
        unique_results = set(results)

        if "League" in tournament["name"]:
            # Les Leagues devraient avoir principalement des 5-0, 4-1, 3-2
            league_results = ["5-0", "4-1", "3-2", "2-3", "1-4", "0-5"]
            non_league_results = [
                r for r in unique_results if r not in league_results and r != ""
            ]
            if non_league_results:
                print(
                    f"   ⚠️ League avec résultats non-standards : {tournament['name']}"
                )
                print(f"      Résultats inattendus : {non_league_results}")

        elif "Challenge" in tournament["name"]:
            # Les Challenges devraient avoir des positions (1st Place, 2nd Place, etc.)
            place_results = [r for r in unique_results if "Place" in r]
            if not place_results and unique_results:
                print(
                    f"   ⚠️ Challenge sans résultats de placement : {tournament['name']}"
                )
                print(f"      Résultats : {list(unique_results)[:5]}...")

    return leagues, challenges, autres, suspicious_challenges


def main():
    """Fonction principale"""
    try:
        leagues, challenges, autres, suspicious = analyze_tournament_classification()

        if suspicious:
            print("\n🔄 RECOMMANDATIONS :")
            print("   • Vérifier la logique de classification")
            print("   • Certains tournois peuvent être mal catégorisés")
            print("   • Revoir les critères de distinction League/Challenge")
        else:
            print("\n✅ CLASSIFICATION SEMBLE CORRECTE")
            print("   • Aucun tournoi suspect détecté")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
