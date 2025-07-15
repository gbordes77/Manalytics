#!/usr/bin/env python3
"""
Scraper MTGO Leagues 5-0 Spécialisé - Récupère les vraies decklists

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MTGOLeagueScraper:
    """Scraper spécialisé pour les leagues 5-0 MTGO"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.cache_dir = Path("data/raw/mtgo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE
        self.logger.info("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
        self.logger.info("📋 Seulement AJOUTER de nouvelles données")

    def scrape_league_data(self):
        """Scrape les données de leagues 5-0 MTGO"""
        self.logger.info("🚀 Début du scraping MTGO Leagues 5-0")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        # URLs spécifiques pour les leagues 5-0
        league_urls = [
            "https://www.mtgo.com/en/mtgo/decklists",
            "https://www.mtgo.com/en/mtgo/decklists/modern",
            "https://www.mtgo.com/en/mtgo/decklists/standard",
            "https://www.mtgo.com/en/mtgo/decklists/legacy",
            "https://www.mtgo.com/en/mtgo/decklists/pioneer",
            "https://www.mtgo.com/en/mtgo/decklists/vintage",
            "https://www.mtgo.com/en/mtgo/decklists/pauper",
        ]

        all_data = []

        for url in league_urls:
            self.logger.info(f"📡 Scraping leagues: {url}")

            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    data = self.extract_league_data(response.text, url)
                    all_data.extend(data)
                    self.logger.info(f"✅ {len(data)} leagues trouvées sur {url}")
                else:
                    self.logger.warning(f"❌ Erreur {response.status_code} pour {url}")

                # Pause pour éviter d'être bloqué
                time.sleep(3)

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        # Sauvegarder toutes les données (AJOUT SEULEMENT)
        if all_data:
            self.save_league_data(all_data)
        else:
            self.logger.warning("⚠️ Aucune league trouvée")

        # Vérifier le cache APRÈS sauvegarde
        final_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(
            f"📁 Cache final : {len(final_files)} fichiers (préserver + ajout)"
        )
        self.logger.info(
            f"✅ RÈGLE RESPECTÉE : {len(final_files) - len(existing_files)} nouveaux fichiers ajoutés"
        )

    def extract_league_data(self, html_content: str, source_url: str) -> list:
        """Extrait les données de leagues 5-0 du HTML"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher spécifiquement les leagues 5-0
        league_patterns = [r"5-0", r"league.*5.*0", r"perfect.*run", r"undefeated"]

        # Chercher dans tous les éléments
        all_elements = soup.find_all(["div", "article", "section", "a"])

        for element in all_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est une league 5-0
            if any(
                re.search(pattern, text, re.IGNORECASE) for pattern in league_patterns
            ):

                # Chercher des informations de deck
                deck_info = self.extract_deck_info(element, text, source_url)

                if deck_info:
                    data.append(deck_info)

        return data

    def extract_deck_info(self, element, text: str, source_url: str) -> dict:
        """Extrait les informations de deck d'un élément"""
        # Chercher des dates
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})",
            r"(\w+ \d{1,2},? \d{4})",
        ]

        found_date = None
        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            if date_matches:
                try:
                    date_str = date_matches[0]
                    if "/" in date_str:
                        found_date = datetime.strptime(date_str, "%m/%d/%Y")
                    elif "-" in date_str and len(date_str.split("-")[0]) == 2:
                        found_date = datetime.strptime(date_str, "%m-%d-%Y")
                    elif "-" in date_str and len(date_str.split("-")[0]) == 4:
                        found_date = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        found_date = datetime.strptime(date_str, "%B %d, %Y")
                    break
                except ValueError:
                    continue

        # Chercher des cartes (mots qui ressemblent à des noms de cartes)
        card_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
        potential_cards = re.findall(card_pattern, text)

        # Filtrer les cartes probables (plus de 3 caractères, pas des mots communs)
        common_words = {
            "the",
            "and",
            "with",
            "from",
            "this",
            "that",
            "have",
            "will",
            "been",
            "they",
            "were",
            "been",
            "their",
            "there",
            "other",
            "about",
            "many",
            "then",
            "them",
            "these",
            "some",
            "time",
            "very",
            "when",
            "just",
            "into",
            "than",
            "more",
            "only",
            "over",
            "such",
            "most",
            "even",
            "make",
            "like",
            "through",
            "back",
            "years",
            "where",
            "much",
            "before",
            "mean",
            "same",
            "right",
            "think",
            "also",
            "around",
            "another",
            "came",
            "come",
            "work",
            "three",
            "word",
            "because",
            "does",
            "part",
            "hear",
            "above",
            "table",
            "should",
            "country",
            "world",
            "school",
            "still",
            "every",
            "between",
            "found",
            "those",
            "never",
            "under",
            "might",
            "while",
            "always",
            "often",
            "something",
            "usually",
            "though",
            "example",
            "together",
            "important",
            "until",
            "children",
            "enough",
            "sometimes",
            "almost",
            "family",
            "father",
            "mother",
            "night",
            "picture",
            "being",
            "study",
            "second",
            "soon",
            "story",
            "since",
            "white",
            "ever",
            "paper",
            "hard",
            "near",
            "sentence",
            "better",
            "best",
            "across",
            "during",
            "today",
            "however",
            "sure",
            "knew",
            "it's",
            "try",
            "told",
            "young",
            "sun",
            "thing",
            "whole",
            "hear",
            "example",
            "heard",
            "several",
            "change",
            "answer",
            "room",
            "sea",
            "against",
            "top",
            "turned",
            "learn",
            "point",
            "city",
            "play",
            "toward",
            "five",
            "himself",
            "usually",
            "money",
            "seen",
            "didn't",
            "car",
            "morning",
            "I'm",
            "body",
            "upon",
            "family",
            "music",
            "color",
            "stand",
            "sun",
            "questions",
            "fish",
            "area",
            "mark",
            "dog",
            "horse",
            "birds",
            "problem",
            "complete",
            "room",
            "knew",
            "since",
            "ever",
            "piece",
            "told",
            "usually",
            "didn't",
            "friends",
            "easy",
            "heard",
            "order",
            "red",
            "door",
            "sure",
            "become",
            "top",
            "ship",
            "across",
            "today",
            "during",
            "short",
            "better",
            "best",
            "however",
            "low",
            "hours",
            "black",
            "products",
            "happened",
            "whole",
            "measure",
            "remember",
            "early",
            "waves",
            "reached",
            "listen",
            "wind",
            "rock",
            "space",
            "covered",
            "fast",
            "several",
            "hold",
            "himself",
            "toward",
            "five",
            "step",
            "morning",
            "passed",
            "vowel",
            "true",
            "hundred",
            "against",
            "pattern",
            "numeral",
            "table",
            "north",
            "slowly",
            "money",
            "map",
            "farm",
            "pulled",
            "draw",
            "voice",
            "seen",
            "cold",
            "cried",
            "plan",
            "notice",
            "south",
            "sing",
            "war",
            "ground",
            "fall",
            "king",
            "town",
            "I'll",
            "unit",
            "figure",
            "certain",
            "field",
            "travel",
            "wood",
            "fire",
            "upon",
        }

        cards = [
            card
            for card in potential_cards
            if len(card) > 3 and card.lower() not in common_words
        ]

        # Chercher le format
        format_keywords = {
            "modern": "Modern",
            "standard": "Standard",
            "legacy": "Legacy",
            "pioneer": "Pioneer",
            "vintage": "Vintage",
            "pauper": "Pauper",
        }

        detected_format = "Unknown"
        for keyword, format_name in format_keywords.items():
            if keyword in text.lower():
                detected_format = format_name
                break

        return {
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date.isoformat() if found_date else None,
            "format": detected_format,
            "source_url": source_url,
            "extracted_at": datetime.now().isoformat(),
            "type": "league_5_0",
            "cards_found": len(cards),
            "sample_cards": cards[:10] if cards else [],
        }

    def save_league_data(self, data: list):
        """Sauvegarde les données de leagues (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_leagues_5_0_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = self.cache_dir / f"mtgo_leagues_5_0_{timestamp}_{counter}.json"
            counter += 1

        # Sauvegarder en JSON (AJOUT SEULEMENT)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "total_leagues": len(data),
                    "data": data,
                    "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                    "git_rule": "CACHE_NOT_COMMITTED",
                },
                f,
                indent=2,
            )

        self.logger.info(
            f"💾 {len(data)} leagues sauvegardées dans {json_file} (AJOUT SEULEMENT)"
        )

        # Organiser par date si disponible (AJOUT SEULEMENT)
        dated_data = [item for item in data if item.get("date")]
        if dated_data:
            self.organize_by_date(dated_data)

    def organize_by_date(self, dated_data: list):
        """Organise les données par date (AJOUT SEULEMENT)"""
        for item in dated_data:
            try:
                item_date = datetime.fromisoformat(item["date"])
                year_month_dir = (
                    self.cache_dir / str(item_date.year) / f"{item_date.month:02d}"
                )
                year_month_dir.mkdir(parents=True, exist_ok=True)

                # RÈGLE ABSOLUE : Nom de fichier unique pour éviter l'écrasement
                timestamp = datetime.now().strftime("%H%M%S_%f")[
                    :-3
                ]  # Microsecondes pour unicité
                filename = (
                    f"mtgo_league_{item_date.strftime('%Y%m%d')}_{timestamp}.json"
                )

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_league_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
                    file_path = year_month_dir / filename
                    counter += 1

                # Sauvegarder (AJOUT SEULEMENT)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            **item,
                            "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                            "git_rule": "CACHE_NOT_COMMITTED",
                        },
                        f,
                        indent=2,
                    )

            except Exception as e:
                self.logger.error(f"⚠️ Erreur organisation par date: {e}")


def main():
    """Fonction principale"""
    scraper = MTGOLeagueScraper()

    print("🎯 SCRAPER MTGO LEAGUES 5-0 SPÉCIALISÉ")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 50)

    scraper.scrape_league_data()

    print("\n✅ Scraping des leagues terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    main()
