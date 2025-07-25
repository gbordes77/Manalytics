#!/usr/bin/env python3
"""
Scraping Standard du 1er juillet 2025 au 25 juillet 2025
Format: Standard uniquement
"""
from datetime import datetime, timezone, timedelta
from scrapers.mtgo_scraper_enhanced import MTGOEnhancedScraper, logger as mtgo_logger
from parse_melee_records import save_tournament_with_embedded_decklists
from scrape_melee_from_commit import MtgMeleeClient
import logging
import json
from pathlib import Path

# Configuration du logging principal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_mtgo_july():
    """Scraper MTGO Standard du 1er au 25 juillet 2025"""
    logger.info("\n" + "="*60)
    logger.info("🎯 MTGO - Standard - Juillet 2025")
    logger.info("="*60)
    
    # Dates fixes
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 25, 23, 59, 59, tzinfo=timezone.utc)
    
    logger.info(f"📅 Période: {start_date.date()} à {end_date.date()}")
    logger.info("🎮 Format: Standard")
    
    # Créer le scraper
    scraper = MTGOEnhancedScraper()
    
    # Scraper - skip_processed=False pour tout récupérer
    results = scraper.scrape_tournaments(
        start_date=start_date,
        end_date=end_date,
        format_filter="standard",
        skip_processed=False
    )
    
    logger.info(f"✅ {len(results)} tournois MTGO récupérés")
    
    # Sauvegarder
    saved_count = 0
    for cache_item in results:
        try:
            tournament = cache_item.tournament
            
            # Déterminer le dossier
            format_dir = Path("data/raw/mtgo/standard")
            if "challenge" in tournament.name.lower():
                format_dir = format_dir / "challenge"
            format_dir.mkdir(parents=True, exist_ok=True)
            
            # Créer le nom de fichier
            date_str = tournament.date.strftime("%Y-%m-%d")
            tournament_id = tournament.uri.split('/')[-1]
            filename = f"{date_str}_{tournament_id}.json"
            filepath = format_dir / filename
            
            # Préparer les données
            tournament_data = {
                "source": "mtgo",
                "format": "standard",
                "name": tournament.name,
                "date": date_str,
                "url": tournament.uri,
                "tournament_id": tournament_id,
                "tournament_type": tournament.tournament_type,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "total_players": tournament.metadata.total_players if tournament.metadata else len(cache_item.decks),
                "decks": []
            }
            
            # Ajouter les decklists
            for deck in cache_item.decks:
                deck_data = {
                    "player": deck.player,
                    "result": deck.result,
                    "mainboard": [
                        {"count": item.count, "card_name": item.card_name}
                        for item in deck.mainboard
                    ],
                    "sideboard": [
                        {"count": item.count, "card_name": item.card_name}
                        for item in deck.sideboard
                    ]
                }
                
                if deck.metrics:
                    deck_data["metrics"] = {
                        "total_cards": deck.metrics.total_cards,
                        "unique_cards": deck.metrics.unique_cards,
                        "color_identity": deck.metrics.color_identity,
                        "card_types": deck.metrics.card_types
                    }
                
                tournament_data["decks"].append(deck_data)
            
            # Standings
            if cache_item.standings:
                tournament_data["standings"] = [
                    {
                        "rank": s.rank,
                        "player": s.player,
                        "points": s.points,
                        "wins": s.wins,
                        "losses": s.losses,
                        "omwp": s.omwp,
                        "gwp": s.gwp,
                        "ogwp": s.ogwp
                    }
                    for s in cache_item.standings
                ]
            
            # Metagame
            if cache_item.metagame_breakdown:
                tournament_data["metagame_breakdown"] = cache_item.metagame_breakdown
            
            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament_data, f, indent=2, ensure_ascii=False)
            
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
    
    logger.info(f"💾 {saved_count} tournois MTGO sauvegardés")
    return saved_count


def scrape_melee_july():
    """Scraper Melee Standard du 1er au 25 juillet 2025"""
    logger.info("\n" + "="*60)
    logger.info("🎯 Melee - Standard - Juillet 2025")
    logger.info("="*60)
    
    # Dates fixes
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 25, 23, 59, 59)
    
    logger.info(f"📅 Période: {start_date.date()} à {end_date.date()}")
    logger.info("🎮 Format: Standard")
    
    # Créer le client
    client = MtgMeleeClient()
    client.ensure_authenticated()
    
    # Rechercher
    logger.info("🔍 Recherche des tournois Melee...")
    tournaments_data = client.search_tournaments(start_date, end_date)
    
    if tournaments_data:
        # Sauvegarder avec les decklists intégrées
        saved_files = save_tournament_with_embedded_decklists(tournaments_data, "Standard")
        logger.info(f"💾 {len(saved_files)} tournois Melee sauvegardés")
        return len(saved_files)
    else:
        logger.warning("Aucun tournoi Melee trouvé")
        return 0


def main():
    logger.info("🚀 SCRAPING COMPLET - STANDARD - JUILLET 2025")
    logger.info(f"📅 Du 1er juillet au 25 juillet 2025")
    logger.info(f"🎮 Format: Standard uniquement")
    logger.info("="*60)
    
    # Confirmation
    logger.info("\n📋 Résumé de la tâche:")
    logger.info("  - Plateformes: MTGO + Melee")
    logger.info("  - Format: Standard")
    logger.info("  - Période: 01/07/2025 - 25/07/2025 (25 jours)")
    logger.info("  - Decklists: Complètes (mainboard + sideboard)")
    
    # MTGO
    mtgo_count = scrape_mtgo_july()
    
    # Melee
    melee_count = scrape_melee_july()
    
    # Résumé final
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSUMÉ FINAL - JUILLET 2025")
    logger.info("="*60)
    logger.info(f"✅ MTGO: {mtgo_count} tournois Standard")
    logger.info(f"✅ Melee: {melee_count} tournois Standard")
    logger.info(f"✅ TOTAL: {mtgo_count + melee_count} tournois")
    logger.info("\n📁 Fichiers sauvegardés dans:")
    logger.info("  - data/raw/mtgo/standard/")
    logger.info("  - data/raw/melee/standard_complete/")
    

if __name__ == "__main__":
    main()