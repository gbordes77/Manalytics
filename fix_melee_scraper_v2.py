#!/usr/bin/env python3
"""
Scraper Melee basé sur la méthode fbettega avec API publique
Utilise les payloads DataTables pour récupérer TOUS les decks
"""

import json
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
from dateutil import parser


class MtgMeleeConstants:
    """Constantes pour l'API Melee basées sur fbettega"""

    TOURNAMENT_LIST_URL = "https://melee.gg/Decklist/SearchDecklists"
    TOURNAMENT_PAGE = "https://melee.gg/Tournament/View/{tournamentId}"

    @staticmethod
    def build_magic_payload(
        start_date: datetime,
        end_date: datetime,
        length: int = 500,
        draw: int = 1,
        start: int = 0,
    ):
        """Construit le payload DataTables pour la recherche de tournois"""
        return {
            "draw": str(draw),
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
            "startDate": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
            "endDate": f"{end_date.strftime('%Y-%m-%d')}T23:59:59.999Z",
        }


class MtgMeleeClientV2:
    """Client Melee basé sur la méthode fbettega"""

    def __init__(self):
        self.session = self._get_client()

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

    def get_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Récupère tous les tournois avec l'API publique"""
        print(
            f"🔍 Récupération des tournois Melee du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        )

        length_tournament_page = 500
        result = []
        draw = 1
        starting_point = 0
        seen_ids = set()

        while True:
            payload = MtgMeleeConstants.build_magic_payload(
                start_date,
                end_date,
                length=length_tournament_page,
                draw=draw,
                start=starting_point,
            )

            # Appel API avec retry
            MAX_RETRIES = 3
            DELAY_SECONDS = 2

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = self.session.post(
                        MtgMeleeConstants.TOURNAMENT_LIST_URL, data=payload
                    )
                    if response.status_code == 200 and response.text.strip():
                        tournament_data = json.loads(response.text)
                        break
                    else:
                        print(
                            f"❌ Tentative {attempt}: Réponse vide ou erreur {response.status_code}"
                        )
                except json.JSONDecodeError:
                    print(f"❌ Tentative {attempt}: Erreur JSON")

                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_SECONDS)
            else:
                print("❌ Échec après toutes les tentatives")
                return []

            # Traitement des résultats
            new_tournaments = tournament_data.get("data", [])
            for tournament in new_tournaments:
                tournament_id = tournament.get("Guid")
                if tournament_id not in seen_ids:
                    result.append(tournament)
                    seen_ids.add(tournament_id)

            print(
                f"📊 Tournois trouvés: {len(result)}/{tournament_data.get('recordsFiltered', 0)}"
            )

            # Vérification de fin
            if tournament_data.get("recordsFiltered", 0) == len(result):
                break
            if ((draw - 1) * length_tournament_page) >= tournament_data.get(
                "recordsFiltered", 0
            ):
                break

            draw += 1
            starting_point += length_tournament_page

        print(f"✅ Récupération terminée: {len(result)} tournois")
        return result

    def extract_decklist_data(self, tournament_data: Dict) -> Dict:
        """Extrait les données de decklist depuis la réponse API"""
        return {
            "date": parser.parse(tournament_data["TournamentStartDate"]),
            "TournamentId": tournament_data["TournamentId"],
            "Valid": tournament_data.get("IsValid", True),
            "OwnerDisplayName": tournament_data.get("OwnerDisplayName", ""),
            "OwnerUsername": tournament_data.get("OwnerUsername", "UnknownPlayer"),
            "Guid": tournament_data.get("Guid", ""),
            "DecklistName": tournament_data.get("DecklistName", ""),
            "Records": tournament_data.get("Records", []),
            "FormatDescription": tournament_data.get("FormatDescription", ""),
        }


def scrape_melee_standard_july_2025():
    """Scraper principal pour Standard juillet 2025"""
    print("🚀 SCRAPING MELEE STANDARD - 1er juillet au 20 juillet 2025")
    print("=" * 70)

    # Configuration
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 20, tzinfo=timezone.utc)

    # Client Melee
    client = MtgMeleeClientV2()

    # Récupération des tournois
    tournaments = client.get_tournaments(start_date, end_date)

    if not tournaments:
        print("❌ Aucun tournoi trouvé")
        return []

    # Filtrage Standard
    standard_tournaments = []
    for tournament in tournaments:
        format_desc = tournament.get("FormatDescription", "").lower()
        if "standard" in format_desc:
            standard_tournaments.append(tournament)

    print(f"🏆 Tournois Standard trouvés: {len(standard_tournaments)}")

    # Groupement par tournoi
    tournaments_by_id = {}
    for tournament in standard_tournaments:
        tournament_id = tournament["TournamentId"]
        if tournament_id not in tournaments_by_id:
            tournaments_by_id[tournament_id] = {
                "tournament": {
                    "Name": tournament.get("TournamentName", "Unnamed Tournament"),
                    "Date": parser.parse(tournament["TournamentStartDate"]).strftime(
                        "%Y-%m-%d"
                    ),
                    "Uri": MtgMeleeConstants.TOURNAMENT_PAGE.replace(
                        "{tournamentId}", str(tournament_id)
                    ),
                    "Format": "Standard",
                    "Source": "melee.gg",
                },
                "decks": [],
            }

        # Extraction des données de deck
        deck_data = client.extract_decklist_data(tournament)

        # Création du deck
        deck = {
            "Player": deck_data["OwnerUsername"],
            "Archetype": f"Standard | Melee",
            "Result": f"Standard Tournament",
            "Cards": deck_data["Records"] if deck_data["Records"] else [],
        }

        tournaments_by_id[tournament_id]["decks"].append(deck)

    # Conversion en liste
    result = []
    for tournament_id, data in tournaments_by_id.items():
        result.append(data)

    # Sauvegarde
    output_file = "data/processed/melee_standard_july_2025_fixed.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"💾 Sauvegardé: {output_file}")
    print(f"📊 Résumé:")
    print(f"  • Tournois Standard: {len(result)}")
    total_decks = sum(len(t["decks"]) for t in result)
    print(f"  • Total decks: {total_decks}")

    return result


if __name__ == "__main__":
    scrape_melee_standard_july_2025()
