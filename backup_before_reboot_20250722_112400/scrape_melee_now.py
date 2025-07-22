#!/usr/bin/env python3
"""
Scraper Melee pour récupérer TOUS les tournois du 1er juillet à maintenant
Basé sur l'API publique qui fonctionne
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List

import requests
from dateutil import parser


class MeleeScraperNow:
    """Scraper Melee pour récupérer tous les tournois récents"""

    def __init__(self):
        self.session = self._get_client()
        self.base_url = "https://melee.gg/Decklist/TournamentSearch"

    def _get_client(self):
        """Configure la session requests"""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        return session

    def build_payload(
        self,
        start_date: datetime,
        end_date: datetime,
        start: int = 0,
        length: int = 100,
    ):
        """Construit le payload pour l'API"""
        return {
            "draw": "1",
            "columns[0][data]": "ID",
            "columns[0][name]": "ID",
            "columns[0][searchable]": "false",
            "columns[0][orderable]": "false",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "Name",
            "columns[1][name]": "Name",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "StartDate",
            "columns[2][name]": "StartDate",
            "columns[2][searchable]": "false",
            "columns[2][orderable]": "true",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "Status",
            "columns[3][name]": "Status",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "Format",
            "columns[4][name]": "Format",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "columns[5][data]": "OrganizationName",
            "columns[5][name]": "OrganizationName",
            "columns[5][searchable]": "true",
            "columns[5][orderable]": "true",
            "columns[5][search][value]": "",
            "columns[5][search][regex]": "false",
            "columns[6][data]": "Decklists",
            "columns[6][name]": "Decklists",
            "columns[6][searchable]": "true",
            "columns[6][orderable]": "true",
            "columns[6][search][value]": "",
            "columns[6][search][regex]": "false",
            "order[0][column]": "2",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "q": "",
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }

    def get_all_tournaments(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Récupère TOUS les tournois avec pagination complète"""
        print(
            f"🔍 Récupération de TOUS les tournois Melee du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        )

        all_tournaments = []
        start = 0
        length = 100  # Maximum par page
        total_expected = None

        while True:
            payload = self.build_payload(start_date, end_date, start, length)

            print(
                f"📡 Page {start//length + 1}: Récupération de {start} à {start + length}..."
            )

            # Appel API avec retry
            MAX_RETRIES = 3
            DELAY_SECONDS = 2

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = self.session.post(self.base_url, data=payload)
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        break
                    else:
                        print(
                            f"❌ Tentative {attempt}: Erreur HTTP {response.status_code}"
                        )
                except Exception as e:
                    print(f"❌ Tentative {attempt}: Erreur {e}")

                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_SECONDS)
            else:
                print("❌ Échec après toutes les tentatives")
                break

            # Traitement des résultats
            tournaments = data.get("data", [])
            if not tournaments:
                print("✅ Aucun tournoi supplémentaire trouvé")
                break

            all_tournaments.extend(tournaments)

            # Affichage du premier tournoi de cette page
            if tournaments:
                first_tournament = tournaments[0]
                print(
                    f"  📋 Exemple: {first_tournament.get('Name', 'Unknown')} - {first_tournament.get('FormatDescription', 'Unknown')}"
                )

            # Mise à jour du total attendu
            if total_expected is None:
                total_expected = data.get("recordsFiltered", 0)
                print(f"📊 Total attendu: {total_expected} tournois")

            print(f"📊 Tournois récupérés: {len(all_tournaments)}/{total_expected}")

            # Vérification de fin
            if len(all_tournaments) >= total_expected:
                print("✅ Tous les tournois récupérés")
                break
            if start + length >= total_expected:
                print("✅ Pagination terminée")
                break

            start += length
            time.sleep(1)  # Pause entre les requêtes

        print(f"🎯 Récupération terminée: {len(all_tournaments)} tournois au total")
        return all_tournaments

    def analyze_formats(self, tournaments: List[Dict]):
        """Analyse les formats trouvés"""
        formats = {}
        for tournament in tournaments:
            format_desc = tournament.get("FormatDescription", "Unknown")
            if format_desc not in formats:
                formats[format_desc] = 0
            formats[format_desc] += 1

        print(f"\n📊 ANALYSE DES FORMATS:")
        for format_name, count in sorted(
            formats.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  • {format_name}: {count} tournois")

        return formats


def scrape_melee_all_formats():
    """Scraper principal pour TOUS les formats"""
    print("🚀 SCRAPING MELEE - TOUS LES FORMATS")
    print("=" * 60)

    # Configuration - du 1er juillet à maintenant
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)

    print(
        f"📅 Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
    )

    # Scraper Melee
    scraper = MeleeScraperNow()

    # Récupération de TOUS les tournois
    tournaments = scraper.get_all_tournaments(start_date, end_date)

    if not tournaments:
        print("❌ Aucun tournoi trouvé")
        return []

    # Analyse des formats
    formats = scraper.analyze_formats(tournaments)

    # Sauvegarde des données brutes
    output_file = "data/processed/melee_all_formats_july_2025.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tournaments, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n💾 Données brutes sauvegardées: {output_file}")

    # Affichage des premiers tournois
    print(f"\n📋 PREMIERS TOURNOIS:")
    for i, tournament in enumerate(tournaments[:10]):
        print(f"  {i+1}. {tournament.get('Name', 'Unknown')}")
        print(f"     Format: {tournament.get('FormatDescription', 'Unknown')}")
        print(f"     Date: {tournament.get('StartDate', 'Unknown')}")
        print(f"     Decks: {tournament.get('Decklists', 0)}")
        print()

    return tournaments


if __name__ == "__main__":
    scrape_melee_all_formats()
