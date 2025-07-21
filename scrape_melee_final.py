#!/usr/bin/env python3
"""
Scraper Melee final basé sur l'API publique qui fonctionne
Utilise l'endpoint TournamentSearch avec pagination
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List

import requests
from dateutil import parser


class MeleeScraper:
    """Scraper Melee basé sur l'API publique"""

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
        self, start_date: datetime, end_date: datetime, start: int = 0, length: int = 25
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

    def get_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Récupère tous les tournois avec pagination"""
        print(
            f"🔍 Récupération des tournois Melee du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        )

        all_tournaments = []
        start = 0
        length = 100  # Plus de résultats par page

        while True:
            payload = self.build_payload(start_date, end_date, start, length)

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
                break

            all_tournaments.extend(tournaments)
            print(
                f"📊 Tournois trouvés: {len(all_tournaments)}/{data.get('recordsFiltered', 0)}"
            )

            # Vérification de fin
            if len(all_tournaments) >= data.get("recordsFiltered", 0):
                break
            if start + length >= data.get("recordsFiltered", 0):
                break

            start += length
            time.sleep(1)  # Pause entre les requêtes

        print(f"✅ Récupération terminée: {len(all_tournaments)} tournois")
        return all_tournaments

    def get_tournament_decks(self, tournament_id: int) -> List[Dict]:
        """Récupère les decks d'un tournoi spécifique"""
        # URL pour les decks d'un tournoi
        url = f"https://melee.gg/Decklist/Tournament/{tournament_id}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                # Parse la page HTML pour extraire les decks
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")

                decks = []
                # Chercher les liens vers les decks
                deck_links = soup.find_all(
                    "a", href=lambda x: x and "/Decklist/View/" in x
                )

                for link in deck_links:
                    deck_id = link["href"].split("/")[-1]
                    deck_url = f"https://melee.gg/Decklist/View/{deck_id}"

                    # Récupérer les détails du deck
                    deck_response = self.session.get(deck_url)
                    if deck_response.status_code == 200:
                        deck_soup = BeautifulSoup(deck_response.text, "html.parser")

                        # Extraire le nom du joueur
                        player_name = "Unknown Player"
                        player_elem = deck_soup.find(
                            "a", href=lambda x: x and "/Player/" in x
                        )
                        if player_elem:
                            player_name = player_elem.get_text(strip=True)

                        # Extraire les cartes (simplifié)
                        cards = []
                        card_elems = deck_soup.find_all("div", class_="card-name")
                        for card_elem in card_elems:
                            card_name = card_elem.get_text(strip=True)
                            if card_name:
                                cards.append(card_name)

                        deck = {
                            "Player": player_name,
                            "Archetype": f"Standard | Melee",
                            "Result": f"Standard Tournament",
                            "Cards": cards,
                            "DeckUrl": deck_url,
                        }
                        decks.append(deck)

                return decks
        except Exception as e:
            print(f"❌ Erreur récupération decks tournoi {tournament_id}: {e}")

        return []


def scrape_melee_standard_july_2025():
    """Scraper principal pour Standard juillet 2025"""
    print("🚀 SCRAPING MELEE STANDARD - 1er juillet au 20 juillet 2025")
    print("=" * 70)

    # Configuration
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 20, tzinfo=timezone.utc)

    # Scraper Melee
    scraper = MeleeScraper()

    # Récupération des tournois
    tournaments = scraper.get_tournaments(start_date, end_date)

    if not tournaments:
        print("❌ Aucun tournoi trouvé")
        return []

    # Filtrage Standard
    standard_tournaments = []
    for tournament in tournaments:
        format_desc = str(tournament.get("FormatDescription", "")).lower()
        if "standard" in format_desc:
            standard_tournaments.append(tournament)

    print(f"🏆 Tournois Standard trouvés: {len(standard_tournaments)}")

    # Récupération des decks pour chaque tournoi Standard
    result = []
    for tournament in standard_tournaments:
        tournament_id = tournament["ID"]
        tournament_name = tournament.get("Name", "Unnamed Tournament")
        tournament_date = parser.parse(tournament["StartDate"]).strftime("%Y-%m-%d")

        print(f"📋 Récupération des decks pour: {tournament_name}")

        # Récupération des decks
        decks = scraper.get_tournament_decks(tournament_id)

        if decks:
            tournament_data = {
                "tournament": {
                    "Name": tournament_name,
                    "Date": tournament_date,
                    "Uri": f"https://melee.gg/Tournament/View/{tournament_id}",
                    "Format": "Standard",
                    "Source": "melee.gg",
                },
                "decks": decks,
            }
            result.append(tournament_data)
            print(f"  ✅ {len(decks)} decks récupérés")
        else:
            print(f"  ⚠️ Aucun deck trouvé")

    # Sauvegarde
    output_file = "data/processed/melee_standard_july_2025_final.json"
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
