#!/usr/bin/env python3
"""
Scraper MTGO Complet et Efficace - Récupère TOUTES les données MTGO

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé

Fonctionnalités :
- Challenges (tous formats)
- Leagues 5-0 (tous formats)
- Preliminaries
- Showcase Challenges
- Super Qualifiers
- Decklists publiques
- Résultats de tournois
- Standings
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MTGOCompleteScraper:
    """Scraper MTGO complet qui récupère toutes les données"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        self.cache_dir = Path("data/raw/mtgo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE
        self.logger.info("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
        self.logger.info("📋 Seulement AJOUTER de nouvelles données")

        # URLs principales MTGO
        self.base_url = "https://www.mtgo.com"
        self.main_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
            "https://www.mtgo.com/en/mtgo/decklists",
        ]

        # URLs par format
        self.format_urls = {
            "modern": [
                "https://www.mtgo.com/en/mtgo/tournaments/modern-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/modern-league",
                "https://www.mtgo.com/en/mtgo/decklists/modern",
            ],
            "standard": [
                "https://www.mtgo.com/en/mtgo/tournaments/standard-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/standard-league",
                "https://www.mtgo.com/en/mtgo/decklists/standard",
            ],
            "legacy": [
                "https://www.mtgo.com/en/mtgo/tournaments/legacy-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/legacy-league",
                "https://www.mtgo.com/en/mtgo/decklists/legacy",
            ],
            "pioneer": [
                "https://www.mtgo.com/en/mtgo/tournaments/pioneer-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/pioneer-league",
                "https://www.mtgo.com/en/mtgo/decklists/pioneer",
            ],
            "vintage": [
                "https://www.mtgo.com/en/mtgo/tournaments/vintage-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/vintage-league",
                "https://www.mtgo.com/en/mtgo/decklists/vintage",
            ],
            "pauper": [
                "https://www.mtgo.com/en/mtgo/tournaments/pauper-challenge",
                "https://www.mtgo.com/en/mtgo/tournaments/pauper-league",
                "https://www.mtgo.com/en/mtgo/decklists/pauper",
            ],
        }

    def scrape_all_mtgo_data(self):
        """Scrape TOUTES les données MTGO"""
        self.logger.info("🚀 Début du scraping MTGO COMPLET")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        all_data = []

        # 1. Scraper les pages principales
        self.logger.info("📡 Étape 1: Scraping des pages principales")
        for url in self.main_urls:
            data = self.scrape_page(url, "main")
            all_data.extend(data)
            time.sleep(2)  # Pause pour éviter d'être bloqué

        # 2. Scraper par format
        self.logger.info("📡 Étape 2: Scraping par format")
        for format_name, urls in self.format_urls.items():
            self.logger.info(f"📡 Scraping format: {format_name}")
            for url in urls:
                data = self.scrape_page(url, format_name)
                all_data.extend(data)
                time.sleep(2)

        # 3. Suivre les liens internes
        self.logger.info("📡 Étape 3: Suivi des liens internes")
        internal_links = self.extract_internal_links(all_data)
        for link in internal_links[:20]:  # Limiter à 20 liens pour éviter l'infini
            data = self.scrape_page(link, "internal")
            all_data.extend(data)
            time.sleep(1)

        # 4. Sauvegarder toutes les données
        if all_data:
            self.save_complete_data(all_data)
        else:
            self.logger.warning("⚠️ Aucune donnée trouvée")

        # Vérifier le cache APRÈS sauvegarde
        final_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(
            f"📁 Cache final : {len(final_files)} fichiers (préserver + ajout)"
        )
        self.logger.info(
            f"✅ RÈGLE RESPECTÉE : {len(final_files) - len(existing_files)} nouveaux fichiers ajoutés"
        )

    def scrape_page(self, url: str, source_type: str) -> list:
        """Scrape une page spécifique"""
        data = []

        try:
            self.logger.info(f"📡 Scraping: {url}")

            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                # Extraire les données selon le type de page
                if "decklists" in url:
                    data = self.extract_decklist_data(response.text, url, source_type)
                elif "tournaments" in url:
                    data = self.extract_tournament_data(response.text, url, source_type)
                elif "results" in url or "standings" in url:
                    data = self.extract_results_data(response.text, url, source_type)
                else:
                    data = self.extract_general_data(response.text, url, source_type)

                self.logger.info(f"✅ {len(data)} éléments trouvés sur {url}")
            else:
                self.logger.warning(f"❌ Erreur {response.status_code} pour {url}")

        except Exception as e:
            self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        return data

    def extract_decklist_data(
        self, html_content: str, source_url: str, source_type: str
    ) -> list:
        """Extrait les données de decklists"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les decklists
        deck_elements = soup.find_all(
            ["div", "article", "section"],
            class_=re.compile(r"deck|list|card", re.IGNORECASE),
        )

        for element in deck_elements:
            text = element.get_text(strip=True)

            # Chercher des informations de deck
            if any(
                keyword in text.lower()
                for keyword in ["deck", "list", "card", "mainboard", "sideboard"]
            ):
                deck_info = self.extract_deck_info(
                    element, text, source_url, source_type
                )
                if deck_info:
                    data.append(deck_info)

        return data

    def extract_tournament_data(
        self, html_content: str, source_url: str, source_type: str
    ) -> list:
        """Extrait les données de tournois"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les tournois
        tournament_elements = soup.find_all(
            ["div", "article", "section"],
            class_=re.compile(
                r"tournament|challenge|league|preliminary", re.IGNORECASE
            ),
        )

        for element in tournament_elements:
            text = element.get_text(strip=True)

            # Chercher des informations de tournois
            if any(
                keyword in text.lower()
                for keyword in [
                    "challenge",
                    "league",
                    "preliminary",
                    "showcase",
                    "qualifier",
                ]
            ):
                tournament_info = self.extract_tournament_info(
                    element, text, source_url, source_type
                )
                if tournament_info:
                    data.append(tournament_info)

        return data

    def extract_results_data(
        self, html_content: str, source_url: str, source_type: str
    ) -> list:
        """Extrait les données de résultats"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les résultats
        result_elements = soup.find_all(
            ["div", "article", "section"],
            class_=re.compile(r"result|standing|ranking", re.IGNORECASE),
        )

        for element in result_elements:
            text = element.get_text(strip=True)

            # Chercher des informations de résultats
            if any(
                keyword in text.lower()
                for keyword in ["result", "standing", "ranking", "winner", "finalist"]
            ):
                result_info = self.extract_result_info(
                    element, text, source_url, source_type
                )
                if result_info:
                    data.append(result_info)

        return data

    def extract_general_data(
        self, html_content: str, source_url: str, source_type: str
    ) -> list:
        """Extrait les données générales"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher tous les éléments pertinents
        all_elements = soup.find_all(["div", "article", "section", "a"])

        for element in all_elements:
            text = element.get_text(strip=True)

            # Chercher des informations MTG
            if any(
                keyword in text.lower()
                for keyword in [
                    "modern",
                    "standard",
                    "legacy",
                    "pioneer",
                    "vintage",
                    "pauper",
                    "challenge",
                    "league",
                    "tournament",
                    "deck",
                    "card",
                ]
            ):
                general_info = self.extract_general_info(
                    element, text, source_url, source_type
                )
                if general_info:
                    data.append(general_info)

        return data

    def extract_deck_info(
        self, element, text: str, source_url: str, source_type: str
    ) -> dict:
        """Extrait les informations de deck"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher des cartes
        cards = self.extract_cards(text)

        # Chercher le format
        detected_format = self.detect_format(text)

        return {
            "type": "decklist",
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": detected_format,
            "source_url": source_url,
            "source_type": source_type,
            "extracted_at": datetime.now().isoformat(),
            "cards_found": len(cards),
            "sample_cards": cards[:10] if cards else [],
        }

    def extract_tournament_info(
        self, element, text: str, source_url: str, source_type: str
    ) -> dict:
        """Extrait les informations de tournois"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher le type de tournoi
        tournament_type = self.detect_tournament_type(text)

        # Chercher le format
        detected_format = self.detect_format(text)

        return {
            "type": "tournament",
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": detected_format,
            "tournament_type": tournament_type,
            "source_url": source_url,
            "source_type": source_type,
            "extracted_at": datetime.now().isoformat(),
        }

    def extract_result_info(
        self, element, text: str, source_url: str, source_type: str
    ) -> dict:
        """Extrait les informations de résultats"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher le format
        detected_format = self.detect_format(text)

        return {
            "type": "result",
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": detected_format,
            "source_url": source_url,
            "source_type": source_type,
            "extracted_at": datetime.now().isoformat(),
        }

    def extract_general_info(
        self, element, text: str, source_url: str, source_type: str
    ) -> dict:
        """Extrait les informations générales"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher le format
        detected_format = self.detect_format(text)

        return {
            "type": "general",
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": detected_format,
            "source_url": source_url,
            "source_type": source_type,
            "extracted_at": datetime.now().isoformat(),
        }

    def extract_date(self, text: str) -> str:
        """Extrait une date du texte"""
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})",
            r"(\w+ \d{1,2},? \d{4})",
        ]

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
                    return found_date.isoformat()
                except ValueError:
                    continue
        return None

    def extract_cards(self, text: str) -> list:
        """Extrait les cartes du texte"""
        card_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
        potential_cards = re.findall(card_pattern, text)

        # Filtrer les cartes probables
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
        return cards

    def detect_format(self, text: str) -> str:
        """Détecte le format du tournoi"""
        text_lower = text.lower()
        format_keywords = {
            "modern": "Modern",
            "standard": "Standard",
            "legacy": "Legacy",
            "pioneer": "Pioneer",
            "vintage": "Vintage",
            "pauper": "Pauper",
        }

        for keyword, format_name in format_keywords.items():
            if keyword in text_lower:
                return format_name
        return "Unknown"

    def detect_tournament_type(self, text: str) -> str:
        """Détecte le type de tournoi"""
        text_lower = text.lower()
        if "challenge" in text_lower:
            return "Challenge"
        elif "league" in text_lower:
            return "League"
        elif "preliminary" in text_lower:
            return "Preliminary"
        elif "showcase" in text_lower:
            return "Showcase"
        elif "qualifier" in text_lower:
            return "Qualifier"
        else:
            return "Unknown"

    def extract_internal_links(self, data: list) -> list:
        """Extrait les liens internes des données"""
        links = []
        for item in data:
            if "source_url" in item:
                links.append(item["source_url"])
        return list(set(links))  # Supprimer les doublons

    def save_complete_data(self, data: list):
        """Sauvegarde toutes les données (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_complete_data_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = (
                self.cache_dir / f"mtgo_complete_data_{timestamp}_{counter}.json"
            )
            counter += 1

        # Sauvegarder en JSON (AJOUT SEULEMENT)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "total_items": len(data),
                    "data": data,
                    "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                    "git_rule": "CACHE_NOT_COMMITTED",
                },
                f,
                indent=2,
            )

        self.logger.info(
            f"💾 {len(data)} éléments sauvegardés dans {json_file} (AJOUT SEULEMENT)"
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
                    f"mtgo_complete_{item_date.strftime('%Y%m%d')}_{timestamp}.json"
                )

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_complete_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
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
    scraper = MTGOCompleteScraper()

    print("🎯 SCRAPER MTGO COMPLET ET EFFICACE")
    print("=" * 60)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 60)
    print("📡 Fonctionnalités :")
    print("   - Challenges (tous formats)")
    print("   - Leagues 5-0 (tous formats)")
    print("   - Preliminaries")
    print("   - Showcase Challenges")
    print("   - Super Qualifiers")
    print("   - Decklists publiques")
    print("   - Résultats de tournois")
    print("   - Standings")
    print("=" * 60)

    scraper.scrape_all_mtgo_data()

    print("\n✅ Scraping MTGO complet terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    main()
