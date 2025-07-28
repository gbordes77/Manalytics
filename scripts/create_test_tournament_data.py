#!/usr/bin/env python3
"""
Create test tournament data for integration testing.
"""

import json
from pathlib import Path
from datetime import datetime

def create_test_tournament():
    """Create a test tournament file with ID 12801654"""
    
    # Create directories
    mtgo_dir = Path("data/raw/mtgo/standard")
    mtgo_dir.mkdir(parents=True, exist_ok=True)
    
    # Test tournament data
    tournament_data = {
        "Name": "Standard Challenge 32 (12801654)",
        "ID": 12801654,
        "Format": "Standard",
        "Date": "2025-07-05",
        "Platform": "MTGO",
        "Decklists": [
            {
                "Player": "Alice",
                "Rank": 1,
                "Mainboard": [
                    {"Count": 4, "Name": "Lightning Strike", "Types": ["Instant"]},
                    {"Count": 4, "Name": "Opt", "Types": ["Instant"]},
                    {"Count": 4, "Name": "Memory Deluge", "Types": ["Instant"]},
                    {"Count": 4, "Name": "Goldspan Dragon", "Types": ["Creature"]},
                    {"Count": 3, "Name": "Ledger Shredder", "Types": ["Creature"]},
                    {"Count": 2, "Name": "Chandra, Hope's Beacon", "Types": ["Planeswalker"]},
                    {"Count": 24, "Name": "Basic Lands", "Types": ["Land"]}
                ],
                "Sideboard": [
                    {"Count": 3, "Name": "Negate", "Types": ["Instant"]},
                    {"Count": 2, "Name": "Abrade", "Types": ["Instant"]}
                ]
            },
            {
                "Player": "Bob",
                "Rank": 2,
                "Mainboard": [
                    {"Count": 4, "Name": "Go for the Throat", "Types": ["Instant"]},
                    {"Count": 4, "Name": "Anoint with Affliction", "Types": ["Instant"]},
                    {"Count": 4, "Name": "Duress", "Types": ["Sorcery"]},
                    {"Count": 4, "Name": "Sheoldred, the Apocalypse", "Types": ["Creature"]},
                    {"Count": 3, "Name": "Cut Down", "Types": ["Instant"]},
                    {"Count": 2, "Name": "Invoke Despair", "Types": ["Sorcery"]},
                    {"Count": 24, "Name": "Basic Lands", "Types": ["Land"]}
                ],
                "Sideboard": [
                    {"Count": 3, "Name": "Duress", "Types": ["Sorcery"]},
                    {"Count": 2, "Name": "Negate", "Types": ["Instant"]}
                ]
            }
        ]
    }
    
    # Save file
    filename = f"Standard Challenge 32 (12801654)_{datetime(2025, 7, 5).strftime('%Y-%m-%d')}.json"
    filepath = mtgo_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(tournament_data, f, indent=2)
    
    print(f"Created test tournament: {filepath}")
    return filepath

if __name__ == "__main__":
    create_test_tournament()