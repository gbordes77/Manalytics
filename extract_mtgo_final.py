import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

async def extract_mtgo_decklists():
    """Final extraction method for MTGO decklists."""
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        url = 'https://www.mtgo.com/decklist/standard-league-2025-07-249382'
        print(f"Fetching: {url}")
        
        resp = await client.get(url)
        if resp.status_code != 200:
            print(f"Error: Status {resp.status_code}")
            return
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        scripts = soup.find_all('script')
        
        # Find the script with window. assignment
        for script in scripts:
            if script.string and 'window.' in script.string:
                # Look for window.DECKLISTS or similar
                matches = re.findall(r'window\.(\w+)\s*=\s*({[\s\S]+?});', script.string)
                
                for var_name, json_content in matches:
                    try:
                        # Try to parse as JSON
                        data = json.loads(json_content)
                        
                        # Check if this contains deck data
                        if isinstance(data, dict):
                            # Look for decklists in the object
                            for key, value in data.items():
                                if 'deck' in key.lower() and isinstance(value, list):
                                    print(f"\nFound decklists in window.{var_name}.{key}")
                                    print(f"Number of decks: {len(value)}")
                                    
                                    # Process first deck
                                    if value:
                                        first_deck = value[0]
                                        print(f"\nFirst deck structure:")
                                        print(f"  Keys: {list(first_deck.keys())}")
                                        
                                        # Extract player info
                                        player = first_deck.get('loginName') or first_deck.get('player') or 'Unknown'
                                        print(f"  Player: {player}")
                                        
                                        # Extract cards
                                        if 'cards' in first_deck:
                                            cards = first_deck['cards']
                                            mainboard = [c for c in cards if not c.get('sideboard', False)]
                                            sideboard = [c for c in cards if c.get('sideboard', False)]
                                            
                                            print(f"  Mainboard: {len(mainboard)} cards")
                                            print(f"  Sideboard: {len(sideboard)} cards")
                                            
                                            # Show first card structure
                                            if mainboard:
                                                card = mainboard[0]
                                                print(f"\n  First card structure:")
                                                print(f"    {card}")
                                    
                                    return value  # Return the decklists
                        
                        elif isinstance(data, list) and data and 'player' in str(data[0]):
                            print(f"\nFound decklist array in window.{var_name}")
                            print(f"Number of decks: {len(data)}")
                            return data
                    
                    except json.JSONDecodeError:
                        # Try to extract array directly
                        array_match = re.search(r'window\.\w+\s*=\s*(\[[\s\S]+?\]);', script.string)
                        if array_match:
                            try:
                                data = json.loads(array_match.group(1))
                                if isinstance(data, list):
                                    print(f"\nFound array with {len(data)} items")
                                    return data
                            except:
                                pass
        
        print("\nNo decklists found in scripts")
        return None

if __name__ == "__main__":
    decklists = asyncio.run(extract_mtgo_decklists())
    
    if decklists:
        print(f"\n\nSuccessfully extracted {len(decklists)} decklists!")
        
        # Convert to our format
        converted = []
        for deck in decklists[:3]:  # First 3 as example
            player = deck.get('loginName') or deck.get('player') or 'Unknown'
            
            mainboard = []
            sideboard = []
            
            if 'cards' in deck:
                for card in deck['cards']:
                    card_data = {
                        "quantity": card.get('quantity', 1),
                        "name": card.get('cardName', '')
                    }
                    
                    if card.get('sideboard', False):
                        sideboard.append(card_data)
                    else:
                        mainboard.append(card_data)
            
            converted.append({
                "player": player,
                "mainboard": mainboard,
                "sideboard": sideboard
            })
        
        print("\nConverted format:")
        for i, deck in enumerate(converted):
            print(f"\nDeck {i+1}:")
            print(f"  Player: {deck['player']}")
            print(f"  Mainboard: {len(deck['mainboard'])} cards")
            print(f"  Sideboard: {len(deck['sideboard'])} cards")