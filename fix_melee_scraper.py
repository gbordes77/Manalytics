#!/usr/bin/env python3
"""
Correction du scraper Melee
Utiliser les vraies URLs de tournois trouvées
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_tournament_from_decklist(decklist_url):
    """Extrait l'URL du tournoi depuis une decklist"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(decklist_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Chercher les liens vers les tournois
            tournament_links = soup.find_all(
                "a", href=re.compile(r"/Tournament/View/\d+")
            )

            for link in tournament_links:
                href = link.get("href")
                if href and "/Tournament/View/" in href:
                    tournament_id = href.split("/")[-1]
                    tournament_url = f"https://melee.gg{href}"
                    return tournament_url, tournament_id

        return None, None

    except Exception as e:
        print(f"❌ Erreur extraction tournoi : {e}")
        return None, None


def scrape_melee_tournament(tournament_url, tournament_name, tournament_date):
    """Scrape un tournoi Melee spécifique"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"🔍 Scraping tournoi : {tournament_name}")
        print(f"   🔗 URL: {tournament_url}")

        response = requests.get(tournament_url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Chercher les decklists
            decklist_links = soup.find_all("a", href=re.compile(r"/Decklist/View/"))

            print(f"   🃏 Decklists trouvées : {len(decklist_links)}")

            tournament_data = {
                "tournament": {
                    "Name": tournament_name,
                    "Date": tournament_date,
                    "Uri": tournament_url,
                    "Format": "Standard",
                    "Source": "melee.gg",
                },
                "decks": [],
            }

            # Extraire chaque decklist
            for i, decklist_link in enumerate(
                decklist_links[:10]
            ):  # Limiter à 10 pour le test
                decklist_url = f"https://melee.gg{decklist_link.get('href')}"

                print(f"      📄 Decklist {i+1}: {decklist_url}")

                deck_data = extract_decklist_data(decklist_url)
                if deck_data:
                    tournament_data["decks"].append(deck_data)

                time.sleep(1)  # Pause pour éviter le rate limiting

            print(f"   ✅ {len(tournament_data['decks'])} decks extraits")
            return tournament_data

        else:
            print(f"   ❌ Erreur d'accès : {response.status_code}")
            return None

    except Exception as e:
        print(f"   ❌ Erreur scraping : {e}")
        return None


def extract_decklist_data(decklist_url):
    """Extrait les données d'une decklist"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(decklist_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Extraire le titre (nom du deck)
            title = soup.find("title")
            deck_name = title.get_text().strip() if title else "Unknown Deck"

            # Extraire le joueur (si disponible)
            player_name = "Unknown Player"
            player_elements = soup.find_all(
                "div", class_=re.compile(r"player|user|author")
            )
            for element in player_elements:
                text = element.get_text().strip()
                if text and len(text) < 50:  # Nom raisonnable
                    player_name = text
                    break

            # Extraire les cartes (simplifié pour le test)
            cards = []
            card_elements = soup.find_all("div", class_=re.compile(r"card|deck"))

            for element in card_elements[:20]:  # Limiter pour le test
                card_text = element.get_text().strip()
                if card_text and len(card_text) > 0:
                    cards.append(card_text)

            deck_data = {
                "Player": player_name,
                "Archetype": deck_name,
                "Result": "Unknown",  # Pas d'information de résultat dans les decklists
                "Cards": cards[:10],  # Limiter pour le test
                "DecklistUrl": decklist_url,
            }

            return deck_data

        else:
            return None

    except Exception as e:
        print(f"      ❌ Erreur extraction decklist : {e}")
        return None


def scrape_melee_standard_july():
    """Scrape les tournois Melee Standard de juillet 2025"""

    print("🔍 SCRAPING MELEE STANDARD JUILLET 2025")
    print("=" * 60)

    # Liste des tournois Melee de la liste fournie
    melee_tournaments = [
        {
            "name": "TheGathering.gg Standard Post-BNR Celebration",
            "date": "2025-07-02",
            "decklist_url": "https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58",
        },
        {
            "name": "TheGathering.gg Standard Post-BNR Celebration #2",
            "date": "2025-07-02",
            "decklist_url": "https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4",
        },
        {
            "name": "第2回シングルスター杯　サブイベント",
            "date": "2025-07-06",
            "decklist_url": "https://melee.gg/Decklist/View/58391bb8-9d9a-4c34-98af-b31100d6d6ea",
        },
        {
            "name": "Jaffer's Tarkir Dragonstorm Mosh Pit",
            "date": "2025-07-06",
            "decklist_url": "https://melee.gg/Decklist/View/ddae0ba9-a4d7-4708-9e0b-b2cc003d55e2",
        },
        {
            "name": "F2F Tour Red Deer - Sunday Super Qualifier",
            "date": "2025-07-06",
            "decklist_url": "https://melee.gg/Decklist/View/f9fbb177-1238-4e17-8146-b31201842d46",
        },
        {
            "name": "Valley Dasher's Bishkek Classic #1",
            "date": "2025-07-12",
            "decklist_url": "https://melee.gg/Decklist/View/d11c46a4-4cdb-4603-bf82-b317008faa42",
        },
        {
            "name": "Jaffer's Final Fantasy Mosh Pit",
            "date": "2025-07-13",
            "decklist_url": "https://melee.gg/Decklist/View/07f0edf6-0180-447c-b258-b3190103047b",
        },
        {
            "name": "Boa Qualifier #2 2025 (standard)",
            "date": "2025-07-19",
            "decklist_url": "https://melee.gg/Decklist/View/e87b4ce1-7121-44ad-a9be-b31f00927479",
        },
    ]

    all_tournaments = []
    processed_tournaments = set()  # Pour éviter les doublons

    for tournament_info in melee_tournaments:
        print(f"\n🏆 Traitement : {tournament_info['name']}")

        # Extraire l'URL du tournoi depuis la decklist
        tournament_url, tournament_id = extract_tournament_from_decklist(
            tournament_info["decklist_url"]
        )

        if tournament_url and tournament_id not in processed_tournaments:
            processed_tournaments.add(tournament_id)

            # Scraper le tournoi
            tournament_data = scrape_melee_tournament(
                tournament_url, tournament_info["name"], tournament_info["date"]
            )

            if tournament_data and tournament_data["decks"]:
                all_tournaments.append(tournament_data)
                print(f"   ✅ Tournoi ajouté avec {len(tournament_data['decks'])} decks")
            else:
                print(f"   ⚠️ Aucun deck trouvé pour ce tournoi")
        else:
            print(f"   ⚠️ Tournoi déjà traité ou URL non trouvée")

    # Sauvegarder les résultats
    output_file = Path("data/processed/melee_standard_july_2025_fixed.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_tournaments, f, indent=2, ensure_ascii=False)

    print(f"\n✅ RÉSULTATS SAUVEGARDÉS :")
    print(f"   📁 Fichier : {output_file}")
    print(f"   🏆 Tournois : {len(all_tournaments)}")

    total_decks = sum(len(t["decks"]) for t in all_tournaments)
    print(f"   🃏 Decks totaux : {total_decks}")

    return all_tournaments


def main():
    """Fonction principale"""
    try:
        tournaments = scrape_melee_standard_july()

        if tournaments:
            print(f"\n🎯 SUCCÈS ! {len(tournaments)} tournois Melee scrapés")
        else:
            print(f"\n❌ Aucun tournoi Melee scrapé")

    except Exception as e:
        print(f"❌ Erreur lors du scraping : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
