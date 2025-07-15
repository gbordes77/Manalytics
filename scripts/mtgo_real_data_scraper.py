#!/usr/bin/env python3
"""
Scraper MTGO Données Réelles - Récupère les vraies données avec la nouvelle structure

RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé

Analyse de la nouvelle structure MTGO :
- Les pages principales sont des pages de présentation
- Les vraies données sont dans des URLs spécifiques
- Recherche des vraies URLs de données
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


class MTGORealDataScraper:
    """Scraper qui trouve les vraies données MTGO"""

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

        # URLs à explorer pour trouver les vraies données
        self.exploration_urls = [
            "https://www.mtgo.com",
            "https://www.mtgo.com/en/mtgo",
            "https://www.mtgo.com/en/mtgo/tournaments",
            "https://www.mtgo.com/en/mtgo/decklists",
            "https://www.mtgo.com/en/mtgo/results",
            "https://www.mtgo.com/en/mtgo/standings",
            "https://www.mtgo.com/en/mtgo/news",
            "https://www.mtgo.com/en/mtgo/events",
        ]

    def find_real_data_urls(self):
        """Trouve les vraies URLs de données MTGO"""
        self.logger.info("🔍 Recherche des vraies URLs de données MTGO")

        all_links = []

        for url in self.exploration_urls:
            try:
                self.logger.info(f"🔍 Exploration: {url}")

                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    links = self.extract_potential_data_links(response.text, url)
                    all_links.extend(links)
                    self.logger.info(
                        f"✅ {len(links)} liens potentiels trouvés sur {url}"
                    )
                else:
                    self.logger.warning(f"❌ Erreur {response.status_code} pour {url}")

                time.sleep(2)

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        # Filtrer les liens pertinents
        data_links = self.filter_data_links(all_links)

        self.logger.info(f"🎯 {len(data_links)} URLs de données identifiées")
        return data_links

    def extract_potential_data_links(self, html_content: str, source_url: str) -> list:
        """Extrait tous les liens potentiels d'une page"""
        links = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher tous les liens
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Construire l'URL complète
            if href.startswith("/"):
                full_url = f"https://www.mtgo.com{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                full_url = f"https://www.mtgo.com/{href}"

            links.append({"url": full_url, "text": text, "source": source_url})

        return links

    def filter_data_links(self, all_links: list) -> list:
        """Filtre les liens pour ne garder que ceux qui contiennent des données"""
        data_links = []

        # Mots-clés pour identifier les liens de données
        data_keywords = [
            "decklist",
            "tournament",
            "challenge",
            "league",
            "preliminary",
            "showcase",
            "qualifier",
            "result",
            "standing",
            "ranking",
            "modern",
            "standard",
            "legacy",
            "pioneer",
            "vintage",
            "pauper",
            "event",
            "competition",
            "match",
            "game",
            "player",
            "winner",
        ]

        for link_info in all_links:
            url_lower = link_info["url"].lower()
            text_lower = link_info["text"].lower()

            # Vérifier si le lien contient des mots-clés de données
            if any(
                keyword in url_lower or keyword in text_lower
                for keyword in data_keywords
            ):
                # Éviter les liens de navigation génériques
                if not any(
                    exclude in url_lower
                    for exclude in ["#", "javascript:", "mailto:", "tel:"]
                ):
                    data_links.append(link_info)

        return data_links

    def scrape_real_data(self, data_links: list):
        """Scrape les vraies données depuis les URLs identifiées"""
        self.logger.info("🚀 Début du scraping des vraies données MTGO")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        all_data = []

        for link_info in data_links:
            try:
                self.logger.info(
                    f"📡 Scraping: {link_info['text']} -> {link_info['url']}"
                )

                response = self.session.get(link_info["url"], timeout=30)
                if response.status_code == 200:
                    data = self.extract_data_from_page(response.text, link_info)
                    all_data.extend(data)
                    self.logger.info(
                        f"✅ {len(data)} éléments trouvés sur {link_info['url']}"
                    )
                else:
                    self.logger.warning(
                        f"❌ Erreur {response.status_code} pour {link_info['url']}"
                    )

                time.sleep(2)  # Pause pour éviter d'être bloqué

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec {link_info['url']}: {e}")

        # Sauvegarder toutes les données
        if all_data:
            self.save_real_data(all_data)
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

    def extract_data_from_page(self, html_content: str, link_info: dict) -> list:
        """Extrait les données d'une page spécifique"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher tous les éléments de contenu
        content_elements = soup.find_all(
            ["div", "article", "section", "p", "h1", "h2", "h3", "h4", "h5", "h6"]
        )

        for element in content_elements:
            text = element.get_text(strip=True)

            # Vérifier si le contenu contient des informations MTG
            if self.is_mtg_content(text):
                item_data = self.create_data_item(element, text, link_info)
                if item_data:
                    data.append(item_data)

        return data

    def is_mtg_content(self, text: str) -> bool:
        """Vérifie si le texte contient des informations MTG"""
        mtg_keywords = [
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
            "player",
            "winner",
            "finalist",
            "result",
            "standing",
            "ranking",
            "magic",
            "mtg",
            "mtgo",
            "constructed",
            "limited",
            "draft",
            "sealed",
            "swiss",
            "elimination",
            "bracket",
            "round",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in mtg_keywords)

    def create_data_item(self, element, text: str, link_info: dict) -> dict:
        """Crée un élément de données"""
        # Chercher des dates
        found_date = self.extract_date(text)

        # Chercher le format
        detected_format = self.detect_format(text)

        # Chercher le type de contenu
        content_type = self.detect_content_type(text)

        return {
            "type": content_type,
            "title": text[:200] + "..." if len(text) > 200 else text,
            "date": found_date,
            "format": detected_format,
            "source_url": link_info["url"],
            "source_text": link_info["text"],
            "extracted_at": datetime.now().isoformat(),
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

    def detect_content_type(self, text: str) -> str:
        """Détecte le type de contenu"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in ["deck", "list", "card"]):
            return "decklist"
        elif any(
            keyword in text_lower
            for keyword in ["tournament", "challenge", "league", "preliminary"]
        ):
            return "tournament"
        elif any(
            keyword in text_lower
            for keyword in ["result", "standing", "ranking", "winner"]
        ):
            return "result"
        elif any(
            keyword in text_lower for keyword in ["news", "announcement", "update"]
        ):
            return "news"
        else:
            return "general"

    def save_real_data(self, data: list):
        """Sauvegarde les vraies données (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_real_data_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = self.cache_dir / f"mtgo_real_data_{timestamp}_{counter}.json"
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
                filename = f"mtgo_real_{item_date.strftime('%Y%m%d')}_{timestamp}.json"

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_real_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
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
    scraper = MTGORealDataScraper()

    print("🎯 SCRAPER MTGO DONNÉES RÉELLES")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 50)
    print("🔍 Stratégie :")
    print("   1. Explorer toutes les pages MTGO")
    print("   2. Identifier les vraies URLs de données")
    print("   3. Scraper les données réelles")
    print("=" * 50)

    # Étape 1: Trouver les vraies URLs de données
    data_links = scraper.find_real_data_urls()

    # Étape 2: Scraper les vraies données
    if data_links:
        scraper.scrape_real_data(data_links)
    else:
        print("❌ Aucune URL de données trouvée")

    print("\n✅ Scraping des données réelles terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    main()
