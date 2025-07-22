#!/usr/bin/env python3
"""
Scraper direct des decklists Melee
Extraire directement depuis les URLs de decklists individuelles
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_decklist_direct(decklist_url, tournament_name, tournament_date):
    """Extrait directement une decklist depuis son URL"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"🔍 Extraction : {decklist_url}")

        response = requests.get(decklist_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Extraire le titre (nom du deck)
            title = soup.find("title")
            deck_name = title.get_text().strip() if title else "Unknown Deck"

            # Extraire le joueur
            player_name = "Unknown Player"

            # Chercher le nom du joueur dans différents éléments
            player_selectors = [
                'div[class*="player"]',
                'div[class*="user"]',
                'div[class*="author"]',
                'span[class*="player"]',
                'span[class*="user"]',
                'a[class*="player"]',
                'a[class*="user"]',
            ]

            for selector in player_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) < 50 and text != deck_name:
                        player_name = text
                        break
                if player_name != "Unknown Player":
                    break

            # Extraire les cartes
            cards = []

            # Différents sélecteurs pour les cartes
            card_selectors = [
                'div[class*="card"]',
                'div[class*="deck"]',
                'span[class*="card"]',
                'a[class*="card"]',
                'li[class*="card"]',
                ".card-name",
                ".deck-card",
            ]

            for selector in card_selectors:
                elements = soup.select(selector)
                for element in elements:
                    card_text = element.get_text().strip()
                    if card_text and len(card_text) > 0 and len(card_text) < 100:
                        # Nettoyer le texte de la carte
                        card_text = re.sub(
                            r"\s+", " ", card_text
                        )  # Normaliser les espaces
                        if card_text not in cards:
                            cards.append(card_text)

            # Si pas de cartes trouvées, essayer une approche plus large
            if not cards:
                # Chercher tous les éléments avec du texte qui pourrait être des cartes
                all_elements = soup.find_all(["div", "span", "a", "li"])
                for element in all_elements:
                    text = element.get_text().strip()
                    # Filtrer les textes qui ressemblent à des noms de cartes
                    if (
                        text
                        and len(text) > 2
                        and len(text) < 50
                        and not text.isdigit()
                        and not text.startswith("http")
                        and text not in ["Unknown Player", deck_name, "Melee"]
                    ):
                        cards.append(text)

            # Créer les données du deck
            deck_data = {
                "Player": player_name,
                "Archetype": deck_name,
                "Result": "Unknown",  # Pas d'information de résultat
                "Cards": cards[:20],  # Limiter à 20 cartes pour le test
                "DecklistUrl": decklist_url,
                "TournamentName": tournament_name,
                "TournamentDate": tournament_date,
            }

            print(f"   ✅ {player_name} - {deck_name} - {len(cards)} cartes")
            return deck_data

        else:
            print(f"   ❌ Erreur d'accès : {response.status_code}")
            return None

    except Exception as e:
        print(f"   ❌ Erreur extraction : {e}")
        return None


def scrape_melee_decklists_direct():
    """Scrape directement les decklists Melee"""

    print("🔍 SCRAPING DIRECT DES DECKLISTS MELEE")
    print("=" * 60)

    # Liste des decklists de la liste fournie
    decklists = [
        {
            "url": "https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58",
            "tournament": "TheGathering.gg Standard Post-BNR Celebration",
            "date": "2025-07-02",
        },
        {
            "url": "https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4",
            "tournament": "TheGathering.gg Standard Post-BNR Celebration #2",
            "date": "2025-07-02",
        },
        {
            "url": "https://melee.gg/Decklist/View/58391bb8-9d9a-4c34-98af-b31100d6d6ea",
            "tournament": "第2回シングルスター杯　サブイベント",
            "date": "2025-07-06",
        },
        {
            "url": "https://melee.gg/Decklist/View/ddae0ba9-a4d7-4708-9e0b-b2cc003d55e2",
            "tournament": "Jaffer's Tarkir Dragonstorm Mosh Pit",
            "date": "2025-07-06",
        },
        {
            "url": "https://melee.gg/Decklist/View/f9fbb177-1238-4e17-8146-b31201842d46",
            "tournament": "F2F Tour Red Deer - Sunday Super Qualifier",
            "date": "2025-07-06",
        },
        {
            "url": "https://melee.gg/Decklist/View/d11c46a4-4cdb-4603-bf82-b317008faa42",
            "tournament": "Valley Dasher's Bishkek Classic #1",
            "date": "2025-07-12",
        },
        {
            "url": "https://melee.gg/Decklist/View/07f0edf6-0180-447c-b258-b3190103047b",
            "tournament": "Jaffer's Final Fantasy Mosh Pit",
            "date": "2025-07-13",
        },
        {
            "url": "https://melee.gg/Decklist/View/e87b4ce1-7121-44ad-a9be-b31f00927479",
            "tournament": "Boa Qualifier #2 2025 (standard)",
            "date": "2025-07-19",
        },
    ]

    all_decks = []

    for i, decklist_info in enumerate(decklists, 1):
        print(f"\n🃏 Decklist {i}/{len(decklists)}")

        deck_data = extract_decklist_direct(
            decklist_info["url"], decklist_info["tournament"], decklist_info["date"]
        )

        if deck_data:
            all_decks.append(deck_data)

        time.sleep(2)  # Pause pour éviter le rate limiting

    # Grouper par tournoi
    tournaments = {}
    for deck in all_decks:
        tournament_key = f"{deck['TournamentName']}_{deck['TournamentDate']}"

        if tournament_key not in tournaments:
            tournaments[tournament_key] = {
                "tournament": {
                    "Name": deck["TournamentName"],
                    "Date": deck["TournamentDate"],
                    "Uri": f"https://melee.gg/Tournament/View/{deck['TournamentName']}",
                    "Format": "Standard",
                    "Source": "melee.gg",
                },
                "decks": [],
            }

        # Nettoyer les données du deck pour le format standard
        clean_deck = {
            "Player": deck["Player"],
            "Archetype": deck["Archetype"],
            "Result": deck["Result"],
            "Cards": deck["Cards"],
        }

        tournaments[tournament_key]["decks"].append(clean_deck)

    # Convertir en liste
    tournament_list = list(tournaments.values())

    # Sauvegarder les résultats
    output_file = Path("data/processed/melee_standard_july_2025_direct.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tournament_list, f, indent=2, ensure_ascii=False)

    print(f"\n✅ RÉSULTATS SAUVEGARDÉS :")
    print(f"   📁 Fichier : {output_file}")
    print(f"   🏆 Tournois : {len(tournament_list)}")

    total_decks = sum(len(t["decks"]) for t in tournament_list)
    print(f"   🃏 Decks totaux : {total_decks}")

    # Afficher le résumé
    for tournament in tournament_list:
        print(
            f"   📊 {tournament['tournament']['Name']}: {len(tournament['decks'])} decks"
        )

    return tournament_list


def main():
    """Fonction principale"""
    try:
        tournaments = scrape_melee_decklists_direct()

        if tournaments:
            print(
                f"\n🎯 SUCCÈS ! {len(tournaments)} tournois Melee avec {sum(len(t['decks']) for t in tournaments)} decks"
            )
        else:
            print(f"\n❌ Aucun deck Melee extrait")

    except Exception as e:
        print(f"❌ Erreur lors du scraping : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
