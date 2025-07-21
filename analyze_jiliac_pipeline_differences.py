#!/usr/bin/env python3
"""
Analyse des différences potentielles entre notre pipeline et celui de Jiliac
Hypothèses sur pourquoi certaines Challenges sont absentes chez Jiliac
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path


def analyze_pipeline_differences():
    """Analyse les différences potentielles de pipeline"""

    print("🔍 ANALYSE DES DIFFÉRENCES DE PIPELINE AVEC JILIAC")
    print("=" * 70)

    # Charger nos données
    mtgo_file = Path("data/processed/mtgo_standard_july_2025.json")
    with open(mtgo_file, "r", encoding="utf-8") as f:
        mtgo_data = json.load(f)

    # Analyser les Challenges "en plus" que nous avons
    extra_challenges = [
        "0412801647",  # 2025-07-04
        "0512801654",  # 2025-07-05
        "1112802801",  # 2025-07-11
        "1212802816",  # 2025-07-12
        "1912803693",  # 2025-07-19
        "1812803681",  # 2025-07-18
        "0512801659",  # 2025-07-05
    ]

    print("📊 ANALYSE DES CHALLENGES 'EN PLUS' :")
    print()

    # Analyser chaque Challenge en détail
    for extra_id in extra_challenges:
        print(f"🔍 CHALLENGE ID: {extra_id}")

        # Trouver les détails dans nos données
        challenge_details = None
        for tournament_entry in mtgo_data:
            tournament = tournament_entry.get("tournament", {})
            uri = tournament.get("Uri", "")
            if extra_id in uri:
                challenge_details = {
                    "name": tournament.get("Name", ""),
                    "date": tournament.get("Date", ""),
                    "uri": uri,
                    "deck_count": len(tournament_entry.get("decks", [])),
                    "decks": tournament_entry.get("decks", []),
                }
                break

        if challenge_details:
            print(f"   📅 Date: {challenge_details['date']}")
            print(f"   🏆 Nom: {challenge_details['name']}")
            print(f"   🃏 Decks: {challenge_details['deck_count']}")
            print(f"   🔗 URI: {challenge_details['uri']}")

            # Analyser les caractéristiques spéciales
            analyze_challenge_characteristics(challenge_details)
            print()

    # Analyser les patterns temporels
    print("⏰ ANALYSE DES PATTERNS TEMPORELS :")
    analyze_temporal_patterns(mtgo_data)

    # Analyser les caractéristiques des decks
    print("🎴 ANALYSE DES CARACTÉRISTIQUES DES DECKS :")
    analyze_deck_characteristics(mtgo_data)

    # Générer les hypothèses
    print("🤔 HYPOTHÈSES POUR JILIAC :")
    generate_hypotheses()


def analyze_challenge_characteristics(challenge):
    """Analyse les caractéristiques d'une Challenge"""

    decks = challenge["decks"]
    if not decks:
        print("   ⚠️ Aucun deck trouvé")
        return

    # Analyser les résultats
    results = [deck.get("Result", "") for deck in decks]
    unique_results = set(results)

    print(f"   📊 Résultats: {list(unique_results)[:5]}...")

    # Vérifier si c'est une Challenge "normale"
    has_place_results = any("Place" in r for r in unique_results)
    has_win_loss_results = any(re.match(r"\d+-\d+", r) for r in unique_results)

    if has_place_results:
        print("   ✅ Challenge avec résultats de placement")
    elif has_win_loss_results:
        print("   📈 Challenge avec résultats wins-losses")
    else:
        print("   ❓ Format de résultats inconnu")

    # Analyser les archétypes
    archetypes = [deck.get("Archetype", "") for deck in decks]
    unique_archetypes = set(archetypes)
    print(f"   🎭 Archétypes uniques: {len(unique_archetypes)}")

    # Vérifier la cohérence des données
    players = [deck.get("Player", "") for deck in decks]
    unique_players = set(players)
    print(f"   👥 Joueurs uniques: {len(unique_players)}")


def analyze_temporal_patterns(mtgo_data):
    """Analyse les patterns temporels"""

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
                }
            )

    # Grouper par date
    by_date = {}
    for challenge in challenges:
        date = challenge["date"]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(challenge)

    print("   📅 Challenges par jour :")
    for date in sorted(by_date.keys()):
        count = len(by_date[date])
        challenges_info = by_date[date]

        print(f"      {date}: {count} Challenge(s)")

        if count > 1:
            print(
                f"         ⚠️ MULTIPLE CHALLENGES - IDs: {[c['uri'].split('/')[-1] for c in challenges_info]}"
            )

            # Analyser l'heure de publication
            for challenge in challenges_info:
                uri = challenge["uri"]
                # Extraire l'heure si possible
                print(f"         🔗 {challenge['name']}: {uri}")


def analyze_deck_characteristics(mtgo_data):
    """Analyse les caractéristiques des decks"""

    all_decks = []
    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")
        if "Challenge" in name:
            decks = tournament_entry.get("decks", [])
            for deck in decks:
                deck["tournament_name"] = name
                deck["tournament_date"] = tournament.get("Date", "")
                all_decks.append(deck)

    if not all_decks:
        print("   ⚠️ Aucun deck trouvé")
        return

    # Analyser les résultats
    results = [deck.get("Result", "") for deck in all_decks]
    result_counts = {}
    for result in results:
        result_counts[result] = result_counts.get(result, 0) + 1

    print("   📊 Distribution des résultats :")
    for result, count in sorted(
        result_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]:
        print(f"      {result}: {count} decks")

    # Analyser les archétypes
    archetypes = [deck.get("Archetype", "") for deck in all_decks]
    archetype_counts = {}
    for archetype in archetypes:
        archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

    print("   🎭 Top archétypes :")
    for archetype, count in sorted(
        archetype_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"      {archetype}: {count} decks")


def generate_hypotheses():
    """Génère des hypothèses pour expliquer les différences"""

    print()
    print("🤔 HYPOTHÈSES POUR EXPLIQUER LES DIFFÉRENCES :")
    print()

    hypotheses = [
        {
            "title": "⏰ Différence de timing de scraping",
            "description": "Jiliac scrape peut-être à des moments différents, manquant les Challenges publiées plus tard",
            "probability": "Élevée",
            "evidence": "Les Challenges 'en plus' pourraient être publiées à des heures différentes",
        },
        {
            "title": "🔍 Filtrage différent des résultats",
            "description": "Jiliac pourrait filtrer les Challenges avec certains critères (nombre de decks, résultats, etc.)",
            "probability": "Moyenne",
            "evidence": "Certaines Challenges pourraient avoir des caractéristiques spéciales",
        },
        {
            "title": "📅 Différence de période de scraping",
            "description": "Jiliac pourrait utiliser une période légèrement différente ou des intervalles différents",
            "probability": "Moyenne",
            "evidence": "Les Challenges manquantes pourraient être à la limite de la période",
        },
        {
            "title": "🔄 Différence de fréquence de scraping",
            "description": "Jiliac pourrait scraper moins fréquemment, manquant les Challenges publiées entre deux runs",
            "probability": "Élevée",
            "evidence": "MTGO publie parfois plusieurs Challenges par jour",
        },
        {
            "title": "🚫 Filtrage des doublons",
            "description": "Jiliac pourrait avoir une logique de déduplication qui élimine certaines Challenges",
            "probability": "Moyenne",
            "evidence": "Nous avons des Challenges avec des IDs très similaires",
        },
        {
            "title": "⚙️ Configuration différente du scraper",
            "description": "Jiliac pourrait utiliser des paramètres différents (timeout, retry, etc.)",
            "probability": "Élevée",
            "evidence": "Certaines Challenges pourraient être plus difficiles à scraper",
        },
        {
            "title": "🌐 Différence de source de données",
            "description": "Jiliac pourrait utiliser une API ou un endpoint différent",
            "probability": "Faible",
            "evidence": "Nous utilisons le même code de base",
        },
    ]

    for i, hypothesis in enumerate(hypotheses, 1):
        print(f"{i}. {hypothesis['title']}")
        print(f"   📝 {hypothesis['description']}")
        print(f"   📊 Probabilité: {hypothesis['probability']}")
        print(f"   🔍 Évidence: {hypothesis['evidence']}")
        print()

    print("🎯 RECOMMANDATIONS POUR JILIAC :")
    print("   1. Vérifier la fréquence de scraping (toutes les heures vs quotidien)")
    print("   2. Comparer les paramètres de configuration du scraper")
    print("   3. Vérifier s'il y a des filtres sur les résultats")
    print("   4. Analyser les logs de scraping pour voir les erreurs")
    print("   5. Tester avec une période de scraping plus large")
    print("   6. Vérifier la logique de déduplication des tournois")


def main():
    """Fonction principale"""
    try:
        analyze_pipeline_differences()

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
