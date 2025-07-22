#!/usr/bin/env python3
"""
Vérification des doublons dans les Challenges
Analyse si des Challenges sont dupliquées
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def check_challenge_duplicates():
    """Vérifie les doublons dans les Challenges"""

    # Charger les données MTGO
    mtgo_file = Path("data/processed/mtgo_standard_july_2025.json")
    with open(mtgo_file, "r", encoding="utf-8") as f:
        mtgo_data = json.load(f)

    print("🔍 VÉRIFICATION DES DOUBLONS DANS LES CHALLENGES")
    print("=" * 60)

    # Extraire tous les Challenges
    challenges = []
    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")

        if "Challenge" in name:
            challenges.append(
                {
                    "name": name,
                    "date": tournament.get("Date", ""),
                    "uri": tournament.get("Uri", ""),
                    "deck_count": len(tournament_entry.get("decks", [])),
                    "decks": tournament_entry.get("decks", []),
                    "raw_entry": tournament_entry,
                }
            )

    print(f"📊 TOTAL CHALLENGES TROUVÉES : {len(challenges)}")
    print()

    # Analyser les doublons par nom et date
    print("📋 ANALYSE PAR NOM ET DATE :")
    name_date_groups = defaultdict(list)

    for challenge in challenges:
        key = f"{challenge['name']}_{challenge['date']}"
        name_date_groups[key].append(challenge)

    duplicates_found = False

    for key, group in name_date_groups.items():
        if len(group) > 1:
            duplicates_found = True
            print(f"🚨 DOUBLONS DÉTECTÉS : {key}")
            print(f"   Nombre d'occurrences : {len(group)}")

            for i, challenge in enumerate(group, 1):
                print(f"   {i}. URI: {challenge['uri']}")
                print(f"      Decks: {challenge['deck_count']}")

                # Vérifier si les decks sont identiques
                deck_hashes = []
                for deck in challenge["decks"]:
                    # Créer un hash simple du deck
                    deck_str = f"{deck.get('Player', '')}_{deck.get('Result', '')}_{deck.get('Archetype', '')}"
                    deck_hashes.append(hash(deck_str))

                print(f"      Hash des decks: {hash(tuple(deck_hashes))}")
            print()

    if not duplicates_found:
        print("✅ AUCUN DOUBLON DÉTECTÉ PAR NOM ET DATE")
    print()

    # Analyser les doublons par URI
    print("🔗 ANALYSE PAR URI :")
    uri_groups = defaultdict(list)

    for challenge in challenges:
        uri = challenge["uri"]
        uri_groups[uri].append(challenge)

    uri_duplicates = False

    for uri, group in uri_groups.items():
        if len(group) > 1:
            uri_duplicates = True
            print(f"🚨 DOUBLONS URI : {uri}")
            print(f"   Nombre d'occurrences : {len(group)}")

            for i, challenge in enumerate(group, 1):
                print(f"   {i}. Nom: {challenge['name']}")
                print(f"      Date: {challenge['date']}")
                print(f"      Decks: {challenge['deck_count']}")
            print()

    if not uri_duplicates:
        print("✅ AUCUN DOUBLON DÉTECTÉ PAR URI")
    print()

    # Analyser les patterns de noms
    print("📝 ANALYSE DES PATTERNS DE NOMS :")
    name_patterns = defaultdict(list)

    for challenge in challenges:
        name_patterns[challenge["name"]].append(challenge)

    for name, group in name_patterns.items():
        if len(group) > 1:
            print(f"📋 Nom répété : {name}")
            print(f"   Occurrences : {len(group)}")

            # Grouper par date
            date_groups = defaultdict(list)
            for challenge in group:
                date_groups[challenge["date"]].append(challenge)

            for date, date_group in date_groups.items():
                if len(date_group) > 1:
                    print(f"   🚨 Même date ({date}) : {len(date_group)} fois")
                else:
                    print(f"   ✅ Date unique ({date})")
            print()

    # Vérifier la cohérence des données
    print("🎯 VÉRIFICATION DE COHÉRENCE :")

    # Compter les Challenges par jour
    daily_challenges = defaultdict(int)
    for challenge in challenges:
        date = challenge["date"]
        daily_challenges[date] += 1

    print("📅 Challenges par jour :")
    for date in sorted(daily_challenges.keys()):
        count = daily_challenges[date]
        print(f"   {date}: {count} Challenge(s)")

        if count > 2:
            print(f"      ⚠️ Nombre élevé de Challenges ce jour-là")

    # Vérifier les Challenges 32 vs 64
    challenge_32_count = sum(1 for c in challenges if "32" in c["name"])
    challenge_64_count = sum(1 for c in challenges if "64" in c["name"])

    print(f"\n📊 RÉPARTITION :")
    print(f"   • Challenges 32: {challenge_32_count}")
    print(f"   • Challenges 64: {challenge_64_count}")

    return duplicates_found or uri_duplicates


def main():
    """Fonction principale"""
    try:
        has_duplicates = check_challenge_duplicates()

        if has_duplicates:
            print("\n🔄 RECOMMANDATIONS :")
            print("   • Nettoyer les doublons avant analyse")
            print("   • Vérifier la logique de scraping")
            print("   • S'assurer qu'un tournoi = une entrée unique")
        else:
            print("\n✅ AUCUN DOUBLON DÉTECTÉ")
            print("   • Données propres pour l'analyse")

    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
