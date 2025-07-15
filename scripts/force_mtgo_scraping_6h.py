#!/usr/bin/env python3
"""
🎯 SCRIPT DE SCRAPING AUTOMATIQUE MTGO - TOUTES LES 6 HEURES
Force le scraping de TOUS les types de tournois MTGO
"""

import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
# noqa: E402

from python.scraper.mtgo_scraper import MTGOScraper  # noqa: E402


class MTGOScrapingForcer:
    """Force le scraping complet de tous les tournois MTGO"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.cache_folder = "MTGODecklistCache"
        self.api_config = {}

    def _setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("mtgo_scraping_6h.log"),
            ],
        )
        return logging.getLogger(__name__)

    async def force_scrape_all_mtgo_tournaments(self):
        """Force le scraping de TOUS les tournois MTGO"""
        try:
            self.logger.info("🚀 DÉMARRAGE SCRAPING FORCÉ MTGO - TOUS TYPES DE TOURNOIS")

            # Date range for scraping (last 7 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            self.logger.info(f"📅 Période de scraping: {start_date} à {end_date}")

            formats = ["Standard", "Modern", "Pioneer", "Legacy", "Pauper"]

            total_tournaments = 0

            # Use context manager to properly initialize session
            async with MTGOScraper(self.cache_folder, self.api_config) as scraper:

                for format_name in formats:
                    self.logger.info(f"🎯 SCRAPING FORMAT: {format_name}")

                    # Search ALL tournament types
                    tournament_ids = await scraper.search_tournaments(
                        format_name, start_date, end_date
                    )

                    self.logger.info(
                        f"🔍 Trouvé {len(tournament_ids)} tournois {format_name}"
                    )

                    # Fetch each tournament
                    for tournament_id in tournament_ids:
                        try:
                            tournament_data = await scraper.fetch_tournament(
                                tournament_id
                            )
                            if tournament_data:
                                # Save to cache
                                await self._save_tournament_to_cache(
                                    tournament_data, format_name
                                )
                                total_tournaments += 1
                                self.logger.info(
                                    f"✅ Scraped: {tournament_data.get('name')}"
                                )
                            else:
                                self.logger.warning(
                                    f"❌ Failed to fetch: {tournament_id}"
                                )

                        except Exception as e:
                            self.logger.error(f"❌ Error fetching {tournament_id}: {e}")

                self.logger.info(
                    f"🎉 SCRAPING FORCÉ TERMINÉ: {total_tournaments} tournois récupérés"
                )

            return total_tournaments

        except Exception as e:
            self.logger.error(f"❌ ERREUR CRITIQUE SCRAPING: {e}")
            return 0

    async def _save_tournament_to_cache(self, tournament_data, format_name):
        """Sauvegarde le tournoi dans le cache"""
        try:
            # Determine cache path
            date_str = tournament_data.get("date", datetime.now().isoformat())[:10]
            year, month, day = date_str.split("-")

            cache_path = (
                Path(self.cache_folder)
                / "Tournaments"
                / "mtgo.com"
                / year
                / month
                / day
            )
            cache_path.mkdir(parents=True, exist_ok=True)

            # Save tournament
            tournament_id = tournament_data.get("id", f"tournament_{int(time.time())}")
            file_path = cache_path / f"{tournament_id}.json"

            import json

            with open(file_path, "w") as f:
                json.dump(tournament_data, f, indent=2)

            self.logger.info(f"💾 Saved: {file_path}")

        except Exception as e:
            self.logger.error(f"❌ Failed to save tournament: {e}")

    async def run_continuous_scraping(self):
        """Lance le scraping en continu toutes les 6 heures"""
        self.logger.info("🔄 DÉMARRAGE SCRAPING CONTINU - TOUTES LES 6 HEURES")

        while True:
            try:
                # Run scraping
                tournaments_scraped = await self.force_scrape_all_mtgo_tournaments()

                self.logger.info(f"🎯 Cycle terminé: {tournaments_scraped} tournois")
                self.logger.info("⏰ Prochaine exécution dans 6 heures...")

                # Wait 6 hours (21600 seconds)
                await asyncio.sleep(21600)

            except KeyboardInterrupt:
                self.logger.info("⛔ Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur dans le cycle: {e}")
                self.logger.info("⏳ Attente 30 minutes avant retry...")
                await asyncio.sleep(1800)  # Wait 30 minutes on error

    async def run_single_scraping(self):
        """Lance un seul cycle de scraping"""
        tournaments_scraped = await self.force_scrape_all_mtgo_tournaments()
        self.logger.info(f"🎯 SCRAPING UNIQUE TERMINÉ: {tournaments_scraped} tournois")
        return tournaments_scraped


async def main():
    """Point d'entrée principal"""
    forcer = MTGOScrapingForcer()

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Mode continu (toutes les 6 heures)
        await forcer.run_continuous_scraping()
    else:
        # Mode unique
        await forcer.run_single_scraping()


if __name__ == "__main__":
    print("🎯 MANALYTICS - FORCE MTGO SCRAPING")
    print("Usage:")
    print("  python scripts/force_mtgo_scraping_6h.py           # Scraping unique")
    print("  python scripts/force_mtgo_scraping_6h.py --continuous  # 6h auto")
    print()

    asyncio.run(main())
