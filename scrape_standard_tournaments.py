#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour scraper les tournois Standard MTGO et Melee
du 1er juillet 2025 à maintenant
"""

import json
import os
from datetime import datetime, timezone
from scrapers.clients.MTGOclient import TournamentList as MTGOTournamentList
from scrapers.clients.MtgMeleeClientV2 import TournamentList as MeleeTournamentList

def save_tournament_data(tournament_data, platform, date_str):
    """Sauvegarde les données d'un tournoi"""
    # Créer le répertoire si nécessaire
    output_dir = f"data/tournaments/{platform}/{date_str[:7]}"  # YYYY-MM
    os.makedirs(output_dir, exist_ok=True)
    
    # Nom du fichier
    filename = f"{date_str}_{tournament_data.tournament.name.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Convertir en dictionnaire pour la sérialisation
    data = {
        "tournament": {
            "name": tournament_data.tournament.name,
            "date": str(tournament_data.tournament.date),
            "uri": tournament_data.tournament.uri,
            "format": tournament_data.tournament.formats
        },
        "decks": [],
        "standings": [],
        "rounds": []
    }
    
    # Ajouter les decks
    if tournament_data.decks:
        for deck in tournament_data.decks:
            deck_dict = {
                "player": deck.player,
                "result": deck.result,
                "mainboard": [{"card_name": item.card_name, "count": item.count} for item in deck.mainboard],
                "sideboard": [{"card_name": item.card_name, "count": item.count} for item in deck.sideboard]
            }
            data["decks"].append(deck_dict)
    
    # Ajouter les standings
    if tournament_data.standings:
        for standing in tournament_data.standings:
            data["standings"].append({
                "rank": standing.rank,
                "player": standing.player,
                "points": standing.points,
                "wins": standing.wins,
                "losses": standing.losses,
                "draws": standing.draws
            })
    
    # Sauvegarder
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def scrape_mtgo_standard():
    """Scrape les tournois MTGO Standard"""
    print("=== Scraping MTGO Standard Tournaments ===")
    
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)
    
    print(f"Période: {start_date.date()} à {end_date.date()}")
    print("Récupération des tournois...")
    
    try:
        # Obtenir la liste des tournois
        all_tournaments = MTGOTournamentList.DL_tournaments(start_date, end_date)
        
        # Filtrer uniquement les tournois Standard
        standard_tournaments = [t for t in all_tournaments if t.formats == "Standard"]
        
        print(f"\nTrouvé {len(standard_tournaments)} tournois Standard sur {len(all_tournaments)} tournois totaux")
        
        # Traiter chaque tournoi
        tournament_loader = MTGOTournamentList()
        saved_count = 0
        
        for i, tournament in enumerate(standard_tournaments):
            print(f"\nTraitement {i+1}/{len(standard_tournaments)}: {tournament.name} ({tournament.date})")
            
            try:
                # Obtenir les détails
                details = tournament_loader.get_tournament_details(tournament)
                
                if details and details.decks:
                    # Sauvegarder les données
                    filepath = save_tournament_data(details, "mtgo", str(tournament.date))
                    print(f"  ✓ Sauvegardé: {filepath}")
                    print(f"    - {len(details.decks)} decks")
                    saved_count += 1
                else:
                    print(f"  ⚠ Pas de données de deck disponibles")
                    
            except Exception as e:
                print(f"  ✗ Erreur: {e}")
        
        print(f"\n✅ MTGO terminé: {saved_count} tournois sauvegardés")
        return saved_count
        
    except Exception as e:
        print(f"❌ Erreur MTGO: {e}")
        return 0

def scrape_melee_standard():
    """Scrape les tournois Melee Standard"""
    print("\n=== Scraping Melee Standard Tournaments ===")
    
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)
    
    print(f"Période: {start_date.date()} à {end_date.date()}")
    print("Récupération des tournois...")
    
    try:
        # Obtenir la liste des tournois
        all_tournaments = MeleeTournamentList.DL_tournaments(start_date, end_date)
        
        # Filtrer uniquement les tournois Standard
        standard_tournaments = [t for t in all_tournaments if t.formats == "Standard"]
        
        print(f"\nTrouvé {len(standard_tournaments)} tournois Standard sur {len(all_tournaments)} tournois totaux")
        
        # Traiter chaque tournoi
        tournament_loader = MeleeTournamentList()
        saved_count = 0
        
        for i, tournament in enumerate(standard_tournaments):
            print(f"\nTraitement {i+1}/{len(standard_tournaments)}: {tournament.name} ({tournament.date})")
            
            try:
                # Obtenir les détails
                details = tournament_loader.get_tournament_details(tournament)
                
                if details and details.decks:
                    # Sauvegarder les données
                    filepath = save_tournament_data(details, "melee", str(tournament.date.date()))
                    print(f"  ✓ Sauvegardé: {filepath}")
                    print(f"    - {len(details.decks)} decks")
                    if details.standings:
                        print(f"    - {len(details.standings)} standings")
                    saved_count += 1
                else:
                    print(f"  ⚠ Pas de données de deck disponibles")
                    
            except Exception as e:
                print(f"  ✗ Erreur: {e}")
        
        print(f"\n✅ Melee terminé: {saved_count} tournois sauvegardés")
        return saved_count
        
    except Exception as e:
        print(f"❌ Erreur Melee: {e}")
        return 0

def main():
    """Fonction principale"""
    print("🏁 Début du scraping des tournois Standard")
    print("=" * 50)
    
    # Scraper MTGO
    mtgo_count = scrape_mtgo_standard()
    
    # Scraper Melee  
    melee_count = scrape_melee_standard()
    
    print("\n" + "=" * 50)
    print(f"🎉 Scraping terminé!")
    print(f"   - MTGO: {mtgo_count} tournois")
    print(f"   - Melee: {melee_count} tournois")
    print(f"   - Total: {mtgo_count + melee_count} tournois Standard sauvegardés")

if __name__ == "__main__":
    main()