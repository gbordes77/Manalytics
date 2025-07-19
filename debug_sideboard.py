#!/usr/bin/env python3
"""
Debug de l'extraction des sideboards
"""

import json


def debug_sideboard():
    """Debug l'extraction des sideboards"""

    print("🔍 Debug des sideboards:")

    # Charger les données JSON
    with open("mtgo_decklist_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Analyser le premier deck
    first_deck = data["decklists"][0]
    print(f"   Premier deck: {first_deck['player']}")

    main_deck = first_deck["main_deck"]
    print(f"   Total cartes dans main_deck: {len(main_deck)}")

    # Compter mainboard vs sideboard
    mainboard_count = 0
    sideboard_count = 0

    for card in main_deck:
        is_sideboard = card.get("sideboard", "false").lower() == "true"
        if is_sideboard:
            sideboard_count += 1
        else:
            mainboard_count += 1

    print(f"   Cartes mainboard: {mainboard_count}")
    print(f"   Cartes sideboard: {sideboard_count}")

    # Afficher quelques exemples de sideboard
    print(f"   Exemples de sideboard:")
    sideboard_examples = []
    for card in main_deck:
        if card.get("sideboard", "false").lower() == "true":
            card_name = card["card_attributes"]["card_name"]
            qty = card["qty"]
            sideboard_examples.append(f"     {qty}x {card_name}")
            if len(sideboard_examples) >= 5:
                break

    for example in sideboard_examples:
        print(example)

    if not sideboard_examples:
        print("     Aucune carte de sideboard trouvée dans le premier deck")

        # Chercher dans d'autres decks
        for i, deck in enumerate(data["decklists"][:5]):
            deck_sideboard = [
                card
                for card in deck["main_deck"]
                if card.get("sideboard", "false").lower() == "true"
            ]
            if deck_sideboard:
                print(
                    f"   Deck {i+1} ({deck['player']}): {len(deck_sideboard)} cartes de sideboard"
                )
                for card in deck_sideboard[:3]:
                    card_name = card["card_attributes"]["card_name"]
                    qty = card["qty"]
                    print(f"     {qty}x {card_name}")
                break


if __name__ == "__main__":
    debug_sideboard()
