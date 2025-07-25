#!/usr/bin/env python3
"""
MTGO Scraper avec Decklists - Utilise le scraper amélioré pour récupérer les listes complètes
"""

from datetime import datetime, timezone, timedelta
from scrapers.mtgo_scraper_enhanced import MTGOEnhancedScraper, logger
import json
from pathlib import Path
import sys


def save_tournament_with_decklists(cache_item, base_dir="data/raw/mtgo"):
    """Sauvegarde un tournoi avec toutes ses decklists"""
    tournament = cache_item.tournament
    
    # Déterminer le dossier
    format_name = tournament.formats.lower() if tournament.formats else "other"
    format_dir = Path(base_dir) / format_name
    
    # Créer sous-dossier pour challenges si nécessaire
    if "challenge" in tournament.name.lower():
        format_dir = format_dir / "challenge"
    
    format_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer le nom de fichier
    date_str = tournament.date.strftime("%Y-%m-%d")
    # Extraire l'ID depuis l'URL
    tournament_id = tournament.uri.split('/')[-1]
    filename = f"{date_str}_{tournament_id}.json"
    filepath = format_dir / filename
    
    # Préparer les données du tournoi
    tournament_data = {
        "source": "mtgo",
        "format": format_name,
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
                {
                    "count": item.count,
                    "card_name": item.card_name
                }
                for item in deck.mainboard
            ],
            "sideboard": [
                {
                    "count": item.count,
                    "card_name": item.card_name
                }
                for item in deck.sideboard
            ]
        }
        
        # Ajouter les métriques si disponibles
        if deck.metrics:
            deck_data["metrics"] = {
                "total_cards": deck.metrics.total_cards,
                "unique_cards": deck.metrics.unique_cards,
                "color_identity": deck.metrics.color_identity,
                "card_types": deck.metrics.card_types
            }
        
        tournament_data["decks"].append(deck_data)
    
    # Ajouter les standings si disponibles
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
    
    # Ajouter la répartition du métagame si disponible
    if cache_item.metagame_breakdown:
        tournament_data["metagame_breakdown"] = cache_item.metagame_breakdown
    
    # Sauvegarder
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tournament_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Sauvegardé: {filepath} ({len(cache_item.decks)} decks)")
    return filepath


def main():
    logger.info("🎯 MTGO Scraper avec Decklists Complètes")
    logger.info("=" * 50)
    
    # Configuration
    days_back = 7  # Récupérer les tournois des 7 derniers jours
    format_filter = "standard"  # Ou None pour tous les formats
    
    # Calculer les dates
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    
    logger.info(f"📅 Période: {start_date.date()} à {end_date.date()}")
    logger.info(f"🎮 Format: {format_filter or 'Tous'}")
    
    # Créer le scraper
    scraper = MTGOEnhancedScraper()
    
    # Scraper les tournois
    try:
        results = scraper.scrape_tournaments(
            start_date=start_date,
            end_date=end_date,
            format_filter=format_filter,
            skip_processed=False  # Pour tester, on retraite même les déjà processés
        )
        
        logger.info(f"\n✅ Récupéré {len(results)} tournois avec decklists")
        
        # Sauvegarder chaque tournoi
        saved_files = []
        for cache_item in results:
            try:
                filepath = save_tournament_with_decklists(cache_item)
                saved_files.append(filepath)
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde: {e}")
        
        # Résumé
        logger.info("\n📊 Résumé:")
        logger.info(f"  - Tournois récupérés: {len(results)}")
        logger.info(f"  - Fichiers sauvegardés: {len(saved_files)}")
        
        if saved_files:
            logger.info("\n📁 Fichiers créés:")
            for f in saved_files[:5]:  # Afficher les 5 premiers
                logger.info(f"  - {f}")
            if len(saved_files) > 5:
                logger.info(f"  ... et {len(saved_files) - 5} autres")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()