#!/usr/bin/env python3
"""
Scraping Standard du 1er juillet au 20 juillet 2025 21h
Utilise le code original de fbettega pour Melee et MTGO
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.fbettega_clients.melee_client import (
    MtgMeleeAnalyzer,
    MtgMeleeClient,
)
from scraper.fbettega_clients.melee_client import TournamentList as MeleeTournamentList
from scraper.fbettega_clients.mtgo_client import TournamentList as MTGOTournamentList


def save_to_cache(data, filename, data_type):
    """Sauvegarde les données dans le cache"""
    cache_dir = Path("data/processed")
    cache_dir.mkdir(parents=True, exist_ok=True)

    filepath = cache_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ {data_type} sauvegardé : {filepath} ({len(data)} éléments)")
    return filepath


def scrape_melee_standard(start_date, end_date):
    """Scraping Melee pour Standard"""
    print("🔍 Scraping Melee Standard...")

    client = MtgMeleeClient()
    analyzer = MtgMeleeAnalyzer()

    # Récupérer les tournois
    tournaments_info = client.get_tournaments(start_date, end_date)
    print(f"📊 {len(tournaments_info)} tournois Melee récupérés")

    standard_tournaments = []
    all_decks = []

    for tournament_info in tournaments_info:
        # Filtrer pour Standard uniquement
        if tournament_info.formats != "Standard":
            continue

        # Analyser le tournoi
        melee_tournaments = analyzer.get_scraper_tournaments(tournament_info)
        if not melee_tournaments:
            continue

        for melee_tournament in melee_tournaments:
            if melee_tournament.formats != "Standard":
                continue

            print(f"  📋 Traitement: {melee_tournament.name}")

            # Récupérer les détails
            tournament_list = MeleeTournamentList()
            details = tournament_list.get_tournament_details(melee_tournament)

            if details and details.decks:
                tournament_data = {
                    "tournament": melee_tournament.to_dict(),
                    "decks": [deck.to_dict() for deck in details.decks],
                    "standings": [standing.to_dict() for standing in details.standings]
                    if details.standings
                    else [],
                    "rounds": [round_info.to_dict() for round_info in details.rounds]
                    if details.rounds
                    else [],
                }
                standard_tournaments.append(tournament_data)
                all_decks.extend(details.decks)
                print(f"    ✅ {len(details.decks)} decks récupérés")

    return standard_tournaments, all_decks


def scrape_mtgo_standard(start_date, end_date):
    """Scraping MTGO pour Standard"""
    print("🔍 Scraping MTGO Standard...")

    # Récupérer les tournois
    tournaments = MTGOTournamentList.DL_tournaments(start_date, end_date)
    print(f"📊 {len(tournaments)} tournois MTGO récupérés")

    standard_tournaments = []
    all_decks = []

    for tournament in tournaments:
        # Filtrer pour Standard uniquement
        if tournament.formats != "Standard":
            continue

        print(f"  📋 Traitement: {tournament.name}")

        # Récupérer les détails
        tournament_list = MTGOTournamentList()
        details = tournament_list.get_tournament_details(tournament)

        if details and details.decks:
            tournament_data = {
                "tournament": tournament.to_dict(),
                "decks": [deck.to_dict() for deck in details.decks],
                "standings": [standing.to_dict() for standing in details.standings]
                if details.standings
                else [],
                "rounds": [round_info.to_dict() for round_info in details.rounds]
                if details.rounds
                else [],
            }
            standard_tournaments.append(tournament_data)
            all_decks.extend(details.decks)
            print(f"    ✅ {len(details.decks)} decks récupérés")

    return standard_tournaments, all_decks


def main():
    """Fonction principale"""
    print("🚀 SCRAPING STANDARD - 1er juillet au 20 juillet 2025 21h")
    print("=" * 70)

    # Définir les dates
    start_date = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 20, 21, 0, 0, tzinfo=timezone.utc)

    print(f"📅 Période: {start_date} à {end_date}")
    print(f"🎯 Format: Standard uniquement")
    print(f"🔗 Sources: Melee + MTGO (données Jiliac)")
    print()

    all_melee_tournaments = []
    all_mtgo_tournaments = []
    all_decks = []

    try:
        # Scraping Melee
        melee_tournaments, melee_decks = scrape_melee_standard(start_date, end_date)
        all_melee_tournaments.extend(melee_tournaments)
        all_decks.extend(melee_decks)

        # Scraping MTGO
        mtgo_tournaments, mtgo_decks = scrape_mtgo_standard(start_date, end_date)
        all_mtgo_tournaments.extend(mtgo_tournaments)
        all_decks.extend(mtgo_decks)

        # Sauvegarde dans le cache
        print("\n💾 SAUVEGARDE DANS LE CACHE...")

        if all_melee_tournaments:
            save_to_cache(
                all_melee_tournaments,
                "melee_standard_july_2025.json",
                "Tournois Melee Standard",
            )

        if all_mtgo_tournaments:
            save_to_cache(
                all_mtgo_tournaments,
                "mtgo_standard_july_2025.json",
                "Tournois MTGO Standard",
            )

        # Résumé global
        summary = {
            "periode": {"debut": start_date.isoformat(), "fin": end_date.isoformat()},
            "format": "Standard",
            "sources": {
                "melee": {
                    "tournois": len(all_melee_tournaments),
                    "decks": len(melee_decks),
                },
                "mtgo": {
                    "tournois": len(all_mtgo_tournaments),
                    "decks": len(mtgo_decks),
                },
            },
            "total": {
                "tournois": len(all_melee_tournaments) + len(all_mtgo_tournaments),
                "decks": len(all_decks),
            },
        }

        save_to_cache(
            summary, "scraping_summary_standard_july_2025.json", "Résumé du scraping"
        )

        print("\n" + "=" * 70)
        print("✅ SCRAPING TERMINÉ !")
        print(f"📊 Résumé :")
        print(
            f"   • Melee: {len(all_melee_tournaments)} tournois, {len(melee_decks)} decks"
        )
        print(
            f"   • MTGO: {len(all_mtgo_tournaments)} tournois, {len(mtgo_decks)} decks"
        )
        print(
            f"   • TOTAL: {len(all_melee_tournaments) + len(all_mtgo_tournaments)} tournois, {len(all_decks)} decks"
        )

    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
