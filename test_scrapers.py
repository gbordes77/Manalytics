#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for MTG scrapers integration
"""

import json
from datetime import datetime, timezone
from scrapers.clients.MTGOclient import TournamentList as MTGOTournamentList
from scrapers.clients.MtgMeleeClientV2 import TournamentList as MeleeTournamentList

def test_mtgo_scraper():
    """Test MTGO scraper functionality"""
    print("=== Testing MTGO Scraper ===")
    
    # Define date range (last 7 days)
    end_date = datetime.now(timezone.utc)
    start_date = datetime(2025, 1, 20, tzinfo=timezone.utc)
    
    print(f"Fetching MTGO tournaments from {start_date.date()} to {end_date.date()}")
    
    try:
        # Get tournaments list
        tournaments = MTGOTournamentList.DL_tournaments(start_date, end_date)
        
        if tournaments:
            print(f"Found {len(tournaments)} MTGO tournaments")
            
            # Display first 3 tournaments
            for i, tournament in enumerate(tournaments[:3]):
                print(f"\nTournament {i+1}:")
                print(f"  Name: {tournament.name}")
                print(f"  Date: {tournament.date}")
                print(f"  Format: {tournament.formats}")
                print(f"  URL: {tournament.uri}")
                
            # Test getting details for the first tournament
            if tournaments:
                print("\n--- Fetching details for first tournament ---")
                tournament_loader = MTGOTournamentList()
                details = tournament_loader.get_tournament_details(tournaments[0])
                
                if details:
                    print(f"Tournament: {details.tournament.name}")
                    print(f"Number of decks: {len(details.decks) if details.decks else 0}")
                    if details.decks and len(details.decks) > 0:
                        print(f"Winner: {details.decks[0].player}")
                        print(f"Result: {details.decks[0].result}")
        else:
            print("No MTGO tournaments found in the specified date range")
            
    except Exception as e:
        print(f"Error testing MTGO scraper: {e}")

def test_melee_scraper():
    """Test MTG Melee scraper functionality"""
    print("\n\n=== Testing MTG Melee Scraper ===")
    
    # Define date range (last 7 days)
    end_date = datetime.now(timezone.utc)
    start_date = datetime(2025, 1, 20, tzinfo=timezone.utc)
    
    print(f"Fetching Melee tournaments from {start_date.date()} to {end_date.date()}")
    
    try:
        # Get tournaments list
        tournaments = MeleeTournamentList.DL_tournaments(start_date, end_date)
        
        if tournaments:
            print(f"Found {len(tournaments)} Melee tournaments")
            
            # Display first 3 tournaments
            for i, tournament in enumerate(tournaments[:3]):
                print(f"\nTournament {i+1}:")
                print(f"  Name: {tournament.name}")
                print(f"  Date: {tournament.date}")
                print(f"  Format: {tournament.formats}")
                print(f"  URL: {tournament.uri}")
                
            # Test getting details for the first tournament
            if tournaments:
                print("\n--- Fetching details for first tournament ---")
                tournament_loader = MeleeTournamentList()
                details = tournament_loader.get_tournament_details(tournaments[0])
                
                if details:
                    print(f"Tournament: {details.tournament.name}")
                    print(f"Number of decks: {len(details.decks) if details.decks else 0}")
                    if details.decks and len(details.decks) > 0:
                        print(f"Top player: {details.decks[0].player}")
                        print(f"Result: {details.decks[0].result}")
        else:
            print("No Melee tournaments found in the specified date range")
            
    except FileNotFoundError as e:
        print(f"Error: Missing credentials file - {e}")
        print("Please ensure api_credentials/melee_login.json exists with your login info")
    except Exception as e:
        print(f"Error testing Melee scraper: {e}")

def main():
    """Main function to run all tests"""
    print("Starting MTG Scrapers Test\n")
    
    # Test MTGO (no auth required)
    test_mtgo_scraper()
    
    # Test Melee (requires auth)
    test_melee_scraper()
    
    print("\n\nTest completed!")

if __name__ == "__main__":
    main()