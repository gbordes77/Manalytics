#!/usr/bin/env python3
"""
Script simple pour tester le nombre de tournois disponibles
"""

import glob
import json
import os
from datetime import datetime

import pandas as pd


def load_processed_data():
    """Charge les données processed disponibles"""

    print("🔍 Recherche des données processed...")

    # Charger les données MTGO de juillet 2025
    mtgo_file = "data/processed/mtgo_standard_july_2025.json"
    if os.path.exists(mtgo_file):
        print(f"📁 Chargement de {mtgo_file}")
        with open(mtgo_file, "r") as f:
            mtgo_data = json.load(f)

        print(f"✅ MTGO: {len(mtgo_data)} tournois trouvés")

        # Analyser la structure
        total_decks = 0
        tournament_names = set()
        dates = set()

        for tournament in mtgo_data:
            tournament_info = tournament.get("tournament", {})
            decks = tournament.get("decks", [])

            tournament_names.add(tournament_info.get("Name", "Unknown"))
            dates.add(tournament_info.get("Date", "Unknown"))
            total_decks += len(decks)

        print(f"📊 Résumé MTGO:")
        print(f"   - Tournois: {len(mtgo_data)}")
        print(f"   - Decks: {total_decks}")
        print(f"   - Dates: {len(dates)} dates différentes")
        print(f"   - Types de tournois: {len(tournament_names)}")

        # Afficher quelques exemples de tournois
        print(f"\n🏆 Exemples de tournois:")
        for i, tournament in enumerate(mtgo_data[:5]):
            tournament_info = tournament.get("tournament", {})
            decks = tournament.get("decks", [])
            print(
                f"   {i+1}. {tournament_info.get('Name', 'Unknown')} - {tournament_info.get('Date', 'Unknown')} ({len(decks)} decks)"
            )

        if len(mtgo_data) > 5:
            print(f"   ... et {len(mtgo_data) - 5} autres tournois")

    # Charger le résumé de scraping
    summary_file = "data/processed/scraping_summary_standard_july_2025.json"
    if os.path.exists(summary_file):
        print(f"\n📋 Chargement du résumé: {summary_file}")
        with open(summary_file, "r") as f:
            summary = json.load(f)

        print(f"📊 Résumé du scraping:")
        print(
            f"   - Période: {summary['periode']['debut']} à {summary['periode']['fin']}"
        )
        print(f"   - Format: {summary['format']}")
        print(f"   - Sources:")
        for source, data in summary["sources"].items():
            print(
                f"     * {source}: {data['tournois']} tournois, {data['decks']} decks"
            )
        print(
            f"   - Total: {summary['total']['tournois']} tournois, {summary['total']['decks']} decks"
        )


def check_cache_files():
    """Vérifie les fichiers de cache disponibles"""

    print("\n🔍 Vérification du cache fbettega...")

    cache_files = glob.glob("data/raw/fbettega_cache/*.json")
    print(f"📁 Fichiers de cache trouvés: {len(cache_files)}")

    for cache_file in cache_files:
        print(f"   - {os.path.basename(cache_file)}")
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            print(f"     * Tournois: {cache_data.get('tournament_count', 0)}")
            print(f"     * Decks: {cache_data.get('total_decks', 0)}")
            print(
                f"     * Période: {cache_data.get('start_date', 'Unknown')} à {cache_data.get('end_date', 'Unknown')}"
            )
        except Exception as e:
            print(f"     * Erreur de lecture: {e}")


def main():
    """Fonction principale"""
    print("🚀 TEST DU NOMBRE DE TOURNOIS DISPONIBLES")
    print("=" * 50)

    load_processed_data()
    check_cache_files()

    print("\n" + "=" * 50)
    print("✅ Test terminé!")


if __name__ == "__main__":
    main()
