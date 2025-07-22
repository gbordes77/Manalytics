#!/usr/bin/env python3
"""
Scraper MTGO Simple et Efficace - Récupère les vraies données de tournois

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


class SimpleMTGOScraper:
    """Scraper MTGO simple qui récupère les vraies données"""

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

    def scrape_mtgo_data(self):
        """Scrape les données MTGO de manière simple et efficace"""
        self.logger.info("🚀 Début du scraping MTGO simple")

        # Vérifier le cache existant AVANT de commencer
        existing_files = list(self.cache_dir.rglob("*.json"))
        self.logger.info(f"📁 Cache existant : {len(existing_files)} fichiers préservés")

        # URLs directes des tournois MTGO
        tournament_urls = [
            "https://www.mtgo.com/en/mtgo/tournaments/modern-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/standard-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/legacy-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/pioneer-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/vintage-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/pauper-challenge",
            "https://www.mtgo.com/en/mtgo/tournaments/modern-league",
            "https://www.mtgo.com/en/mtgo/tournaments/standard-league",
            "https://www.mtgo.com/en/mtgo/tournaments/legacy-league",
            "https://www.mtgo.com/en/mtgo/tournaments/pioneer-league",
        ]

        all_data = []

        for url in tournament_urls:
            self.logger.info(f"📡 Scraping: {url}")

            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    data = self.extract_tournament_data(response.text, url)
                    all_data.extend(data)
                    self.logger.info(f"✅ {len(data)} tournois trouvés sur {url}")
                else:
                    self.logger.warning(f"❌ Erreur {response.status_code} pour {url}")

                # Pause pour éviter d'être bloqué
                time.sleep(2)

            except Exception as e:
                self.logger.error(f"⚠️ Erreur avec {url}: {e}")

        # Sauvegarder toutes les données (AJOUT SEULEMENT)
        if all_data:
            self.save_all_data(all_data)
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

    def extract_tournament_data(self, html_content: str, source_url: str) -> list:
        """Extrait les données de tournois du HTML"""
        data = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher les éléments de tournois
        tournament_elements = soup.find_all(
            ["div", "article", "section"],
            class_=re.compile(r"tournament|challenge|league|result", re.IGNORECASE),
        )

        if not tournament_elements:
            # Chercher dans tout le contenu
            tournament_elements = soup.find_all(["div", "article", "section"])

        for element in tournament_elements:
            text = element.get_text(strip=True)

            # Chercher des informations de tournois
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
                ]
            ):

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
                                # Format "Month Day, Year"
                                found_date = datetime.strptime(date_str, "%B %d, %Y")
                            break
                        except ValueError:
                            continue

                # Créer l'élément de données
                data_item = {
                    "title": text[:200] + "..." if len(text) > 200 else text,
                    "date": found_date.isoformat() if found_date else None,
                    "source_url": source_url,
                    "extracted_at": datetime.now().isoformat(),
                    "format": self.detect_format(text),
                }
                data.append(data_item)

        return data

    def detect_format(self, text: str) -> str:
        """Détecte le format du tournoi"""
        text_lower = text.lower()
        if "modern" in text_lower:
            return "Modern"
        elif "standard" in text_lower:
            return "Standard"
        elif "legacy" in text_lower:
            return "Legacy"
        elif "pioneer" in text_lower:
            return "Pioneer"
        elif "vintage" in text_lower:
            return "Vintage"
        elif "pauper" in text_lower:
            return "Pauper"
        else:
            return "Unknown"

    def save_all_data(self, data: list):
        """Sauvegarde toutes les données trouvées (AJOUT SEULEMENT)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # RÈGLE ABSOLUE : Vérifier que le fichier n'existe pas déjà
        json_file = self.cache_dir / f"mtgo_simple_data_{timestamp}.json"

        # Si le fichier existe, ajouter un suffixe unique
        counter = 1
        while json_file.exists():
            json_file = self.cache_dir / f"mtgo_simple_data_{timestamp}_{counter}.json"
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
                    f"mtgo_simple_{item_date.strftime('%Y%m%d')}_{timestamp}.json"
                )

                # Vérifier que le fichier n'existe pas déjà
                file_path = year_month_dir / filename
                counter = 1
                while file_path.exists():
                    filename = f"mtgo_simple_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
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
    scraper = SimpleMTGOScraper()

    print("🎯 SCRAPER MTGO SIMPLE ET EFFICACE")
    print("=" * 50)
    print("🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT")
    print("📋 Seulement AJOUTER de nouvelles données")
    print("🚫 Aucune suppression, remplacement ou écrasement autorisé")
    print("=" * 50)

    scraper.scrape_mtgo_data()

    print("\n✅ Scraping terminé!")
    print("✅ RÈGLE RESPECTÉE : Cache existant préservé")


if __name__ == "__main__":
    main()
