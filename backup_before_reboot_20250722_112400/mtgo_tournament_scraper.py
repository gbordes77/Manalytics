#!/usr/bin/env python3
"""
Scraper MTGO Tournois Spécialisé - Récupère les vraies données de tournois

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé

URLs spécialisées découvertes :
- https://www.mtgo.com/decklists (page principale decklists)
- https://www.mtgo.com/en/MTGO/content/magic-online-constructed-events
- https://www.mtgo.com/en/MTGO/content/magic-online-limited-events
- https://www.mtgo.com/news (actualités et annonces)
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


class MTGOTournamentScraper:
    """Scraper spécialisé pour les tournois MTGO"""

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

        # URLs spécialisées pour les tournois
        self.tournament_urls = [
            "https://www.mtgo.com/decklists",
            "https://www.mtgo.com/en/MTGO/content/magic-online-constructed-events",
            "https://www.mtgo.com/en/MTGO/content/magic-online-limited-events",
            "https://www.mtgo.com/news",
            "https://www.mtgo.com/en/mtgo/news",
        ]

        # URLs par format (si elles existent)
        self.format_urls = {
            "modern": [
                "https://www.mtgo.com/en/mtgo/tournaments/modern",
                "https://www.mtgo.com/en/mtgo/decklists/modern",
            ],
            "standard": [
                "https://www.mtgo.com/en/mtgo/tournaments/standard",
                "https://www.mtgo.com/en/mtgo/decklists/standard",
            ],
            "legacy": [
                "https://www.mtgo.com/en/mtgo/tournaments/legacy",
                "https://www.mtgo.com/en/mtgo/decklists/legacy",
            ],
            "pioneer": [
                "https://www.mtgo.com/en/mtgo/tournaments/pioneer",
                "https://www.mtgo.com/en/mtgo/decklists/pioneer",
            ],
            "vintage": [
                "https://www.mtgo.com/en/mtgo/tournaments/vintage",
                "https://www.mtgo.com/en/mtgo/decklists/vintage",
            ],
            "pauper": [
                "https://www.mtgo.com/en/mtgo/tournaments/pauper",
                "https://www.mtgo.com/en/mtgo/decklists/pauper",
            ],
        }

    def scrape_all_tournaments(self):
        """Scrape tous les tournois MTGO"""
        self.logger.info("🚀 Début du scraping des tournois MTGO")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        all_tournaments = []

        # 1. Scraper les URLs principales de tournois
        self.logger.info("📡 Étape 1: Scraping des URLs principales de tournois")
        for url in self.tournament_urls:
            tournaments = self.scrape_tournament_page(url)
            all_tournaments.extend(tournaments)
            time.sleep(2)

        # 2. Scraper par format
        self.logger.info("📡 Étape 2: Scraping par format")
        for format_name, urls in self.format_urls.items():
            self.logger.info(f"📡 Scraping format: {format_name}")
            for url in urls:
                tournaments = self.scrape_tournament_page(url, format_name)
                all_tournaments.extend(tournaments)
                time.sleep(2)

        # 3. Chercher des liens de tournois spécifiques
        self.logger.info("📡 Étape 3: Recherche de liens de tournois spécifiques")
        specific_links = self.find_tournament_specific_links(all_tournaments)
        for link in specific_links:
            tournaments = self.scrape_tournament_page(
                link["url"], link.get("format", "Unknown")
            )
            all_tournaments.extend(tournaments)
            time.sleep(1)

        # 4. Sauvegarder toutes les données
        if all_tournaments:
            self.save_tournament_data(all_tournaments)
        else:
            self.logger.warning("⚠️ Aucun tournoi trouvé")

        # Vérifier le cache APRÈS sauvegarde
        final_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(
            f"📁 Cache final : {len(final_files)} fichiers (préserver + ajout)"
        )
        self.logger.info(
            f"✅ RÈGLE RESPECTÉE : {len(final_files) - len(existing_files)} nouveaux fichiers ajoutés"
        )

    def scrape_tournament_page(self, url: str, format_name: str = "Unknown") -> list:
        """Scrape une page de tournois spécifique"""
        tournaments = []

        try:
            self.logger.info(f"📡 Scraping tournois: {url}")

            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                # Extraire les tournois selon le type de page
                if "decklists" in url:
                    tournaments = self.extract_decklist_tournaments(
                        response.text, url, format_name
                    )
                elif "constructed" in url:
                    tournaments = self.extract_constructed_tournaments(
                        response.text, url, format_name
                    )
                elif "limited" in url:
                    tournaments = self.extract_limited_tournaments(
                        response.text, url, format_name
                    )
                elif "news" in url:
                    tournaments = self.extract_news_tournaments(
                        response.text, url, format_name
                    )
                else:
                    tournaments = self.extract_general_tournaments(
                        response.text, url, format_name
                    )

                self.logger.info(f"✅ {len(tournaments)} tournois trouvés sur {url}")
            else:
                self.logger.warning(f"❌ Erreur {response.status_code} pour {url}")

        except Exception as e:
            self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        return tournaments

    def extract_decklist_tournaments(
        self, html_content: str, source_url: str, format_name: str
    ) -> list:
        """Extrait les tournois depuis les decklists"""
        tournaments = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les éléments de decklists
        deck_elements = soup.find_all(
            ["div", "article", "section", "p"],
            class_=re.compile(r"deck|list|tournament|challenge|league", re.IGNORECASE),
        )

        for element in deck_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est un tournoi
            if self.is_tournament_content(text):
                tournament = self.create_tournament_item(
                    element, text, source_url, format_name
                )
                if tournament:
                    tournaments.append(tournament)

        return tournaments

    def extract_constructed_tournaments(
        self, html_content: str, source_url: str, format_name: str
    ) -> list:
        """Extrait les tournois constructed"""
        tournaments = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les éléments de tournois constructed
        constructed_elements = soup.find_all(
            ["div", "article", "section", "p"],
            class_=re.compile(
                r"constructed|tournament|challenge|league", re.IGNORECASE
            ),
        )

        for element in constructed_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est un tournoi
            if self.is_tournament_content(text):
                tournament = self.create_tournament_item(
                    element, text, source_url, format_name
                )
                if tournament:
                    tournaments.append(tournament)

        return tournaments

    def extract_limited_tournaments(
        self, html_content: str, source_url: str, format_name: str
    ) -> list:
        """Extrait les tournois limited"""
        tournaments = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les éléments de tournois limited
        limited_elements = soup.find_all(
            ["div", "article", "section", "p"],
            class_=re.compile(r"limited|draft|sealed|tournament", re.IGNORECASE),
        )

        for element in limited_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est un tournoi
            if self.is_tournament_content(text):
                tournament = self.create_tournament_item(
                    element, text, source_url, format_name
                )
                if tournament:
                    tournaments.append(tournament)

        return tournaments

    def extract_news_tournaments(
        self, html_content: str, source_url: str, format_name: str
    ) -> list:
        """Extrait les tournois depuis les actualités"""
        tournaments = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les éléments d'actualités de tournois
        news_elements = soup.find_all(
            ["div", "article", "section", "p"],
            class_=re.compile(
                r"news|announcement|tournament|challenge|league", re.IGNORECASE
            ),
        )

        for element in news_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est un tournoi
            if self.is_tournament_content(text):
                tournament = self.create_tournament_item(
                    element, text, source_url, format_name
                )
                if tournament:
                    tournaments.append(tournament)

        return tournaments

    def extract_general_tournaments(
        self, html_content: str, source_url: str, format_name: str
    ) -> list:
        """Extrait les tournois généraux"""
        tournaments = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher tous les éléments potentiels de tournois
        all_elements = soup.find_all(
            ["div", "article", "section", "p", "h1", "h2", "h3", "h4", "h5", "h6"]
        )

        for element in all_elements:
            text = element.get_text(strip=True)

            # Vérifier si c'est un tournoi
            if self.is_tournament_content(text):
                tournament = self.create_tournament_item(
                    element, text, source_url, format_name
                )
                if tournament:
                    tournaments.append(tournament)

        return tournaments

    def is_tournament_content(self, text: str) -> bool:
        """Vérifie si le texte contient des informations de tournois"""
        tournament_keywords = [
            "challenge",
            "league",
            "preliminary",
            "showcase",
            "qualifier",
            "tournament",
            "event",
            "competition",
            "match",
            "game",
            "winner",
            "finalist",
            "result",
            "standing",
            "ranking",
            "modern",
            "standard",
            "legacy",
            "pioneer",
            "vintage",
            "pauper",
            "constructed",
            "limited",
            "draft",
            "sealed",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in tournament_keywords)

    def create_tournament_item(
        self, element, text: str, source_url: str, format_name: str
    ) -> dict:
        """Crée un élément de tournoi"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher le type de tournoi
        tournament_type = self.detect_tournament_type(text)

        # Chercher le format (priorité au format détecté)
        detected_format = self.detect_format(text)
        final_format = detected_format if detected_format != "Unknown" else format_name

        # Chercher des informations spécifiques
        tournament_info = self.extract_tournament_info(text)

        return {
            "type": "tournament",
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": final_format,
            "tournament_type": tournament_type,
            "source_url": source_url,
            "extracted_at": datetime.now().isoformat(),
            "tournament_info": tournament_info,
        }

    def extract_date(self, text: str) -> str:
        """Extrait une date du texte"""
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})",
            r"(\w+ \d{1,2},? \d{4})",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
        ]

        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            if date_matches:
                try:
                    date_str = date_matches[0]
                    if "/" in date_str:
                        if len(date_str.split("/")[2]) == 2:
                            found_date = datetime.strptime(date_str, "%m/%d/%y")
                        else:
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
        elif "constructed" in text_lower:
            return "Constructed"
        elif "limited" in text_lower:
            return "Limited"
        elif "draft" in text_lower:
            return "Draft"
        elif "sealed" in text_lower:
            return "Sealed"
        else:
            return "Unknown"

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

    def extract_tournament_info(self, text: str) -> dict:
        """Extrait des informations spécifiques du tournoi"""
        info = {}

        # Chercher des nombres (participants, prix, etc.)
        numbers = re.findall(r"\b\d+\b", text)
        if numbers:
            info["numbers_found"] = numbers[:5]  # Limiter à 5 nombres

        # Chercher des mots-clés spécifiques
        keywords = []
        if "winner" in text.lower():
            keywords.append("winner")
        if "finalist" in text.lower():
            keywords.append("finalist")
        if "prize" in text.lower():
            keywords.append("prize")
        if "participant" in text.lower():
            keywords.append("participant")

        if keywords:
            info["keywords"] = keywords

        return info

    def find_tournament_specific_links(self, tournaments: list) -> list:
        """Trouve des liens spécifiques de tournois"""
        links = []

        # Chercher des liens dans les données de tournois
        for tournament in tournaments:
            if "source_url" in tournament:
                # Analyser l'URL pour trouver des patterns de tournois
                url = tournament["source_url"]
                if any(
                    keyword in url.lower()
                    for keyword in ["tournament", "challenge", "league", "event"]
                ):
                    links.append(
                        {"url": url, "format": tournament.get("format", "Unknown")}
                    )

        return links[:10]  # Limiter à 10 liens

    def save_tournament_data(self, tournaments: list):
        """Sauvegarde les données de tournois (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_tournaments_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = self.cache_dir / f"mtgo_tournaments_{timestamp}_{counter}.json"
            counter += 1

        # Sauvegarder en JSON (AJOUT SEULEMENT)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "total_tournaments": len(tournaments),
                    "tournaments": tournaments,
                    "cache_rule": "PRESERVED_EXISTING_ADDED_NEW_ONLY",
                    "git_rule": "CACHE_NOT_COMMITTED",
                },
                f,
                indent=2,
            )

        self.logger.info(
            f"💾 {len(tournaments)} tournois sauvegardés dans {json_file} (AJOUT SEULEMENT)"
        )

        # Organiser par date si disponible (AJOUT SEULEMENT)
        dated_tournaments = [t for t in tournaments if t.get("date")]
        if dated_tournaments:
            self.organize_by_date(dated_tournaments)

    def organize_by_date(self, dated_tournaments: list):
        """Organise les tournois par date (AJOUT SEULEMENT)"""
        for tournament in dated_tournaments:
            try:
                tournament_date = datetime.fromisoformat(tournament["date"])
                year_month_dir = (
                    self.cache_dir
                    / str(tournament_date.year)
                    / f"{tournament_date.month:02d}"
                )
                year_month_dir.mkdir(parents=True, exist_ok=True)

                # RÈGLE ABSOLUE : Nom de fichier unique pour éviter l'écrasement
                timestamp = datetime.now().strftime("%H%M%S_%f")[
                    :-3
                ]  # Microsecondes pour unicité
                filename = f"mtgo_tournament_{tournament_date.strftime('%Y%m%d')}_{timestamp}.json"

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_tournament_{tournament_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
                    file_path = year_month_dir / filename
                    counter += 1

                # Sauvegarder (AJOUT SEULEMENT)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            **tournament,
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
    scraper = MTGOTournamentScraper()

    print("🎯 SCRAPER MTGO TOURNOIS SPÉCIALISÉ")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 50)
    print("📡 Fonctionnalités :")
    print("   - Decklists MTGO")
    print("   - Tournois Constructed")
    print("   - Tournois Limited")
    print("   - Actualités de tournois")
    print("   - Par format (Modern, Standard, etc.)")
    print("=" * 50)

    scraper.scrape_all_tournaments()

    print("\n✅ Scraping des tournois terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    main()
