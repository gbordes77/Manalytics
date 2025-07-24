import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

async def debug_javascript_extraction():
    """Debug the JavaScript extraction from MTGO pages."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test with a known working URL
        url = 'https://www.mtgo.com/decklist/standard-league-2025-07-249382'
        print(f"Fetching: {url}")
        
        response = await client.get(url)
        if response.status_code != 200:
            print(f"Error: Got status {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        print(f"\nFound {len(scripts)} script tags")
        
        # Look for the script with the most player data
        best_script = None
        max_players = 0
        
        for i, script in enumerate(scripts):
            if script.string:
                # Count player mentions
                player_count = script.string.count('"player"')
                if player_count > max_players:
                    max_players = player_count
                    best_script = (i, script.string)
        
        if best_script:
            script_idx, script_content = best_script
            print(f"\nBest script is #{script_idx} with {max_players} player mentions")
            
            # Try to extract the data
            print("\nAttempting to extract deck data...")
            
            # Method 1: Look for window.__INITIAL_STATE__ or similar
            state_match = re.search(r'window\.__\w+__\s*=\s*({[\s\S]+?});', script_content)
            if state_match:
                print("Found window.__INITIAL_STATE__ pattern")
                try:
                    state_data = json.loads(state_match.group(1))
                    print(f"Successfully parsed state data with {len(state_data)} keys")
                    
                    # Look for decklist data in the state
                    for key in state_data:
                        if 'deck' in key.lower() or 'list' in key.lower():
                            print(f"  Found potential deck data in key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse state data: {e}")
            
            # Method 2: Look for array of deck objects
            # Pattern: Find JSON arrays containing player data
            array_pattern = r'\[(\{[^\[\]]*"player"[^\[\]]*\}(?:,\s*\{[^\[\]]*\})*)\]'
            array_matches = re.findall(array_pattern, script_content)
            
            if array_matches:
                print(f"\nFound {len(array_matches)} potential deck arrays")
                for i, match in enumerate(array_matches):
                    try:
                        # Wrap in brackets and parse
                        json_str = '[' + match + ']'
                        decks = json.loads(json_str)
                        print(f"\nArray {i}: Successfully parsed {len(decks)} decks")
                        
                        # Show first deck as example
                        if decks:
                            first_deck = decks[0]
                            print(f"  First player: {first_deck.get('player', 'Unknown')}")
                            if 'mainboard' in first_deck:
                                print(f"  Mainboard cards: {len(first_deck['mainboard'])}")
                            if 'sideboard' in first_deck:
                                print(f"  Sideboard cards: {len(first_deck['sideboard'])}")
                    except json.JSONDecodeError:
                        print(f"Array {i}: Failed to parse as JSON")
            
            # Method 3: Extract individual player/deck entries
            print("\nLooking for individual player entries...")
            player_pattern = r'"player"\s*:\s*"([^"]+)"'
            players = re.findall(player_pattern, script_content)
            print(f"Found {len(players)} player names: {players[:5]}...")
            
            # Show a sample of the script content around a player entry
            if players:
                first_player = players[0]
                player_index = script_content.find(f'"player":"{first_player}"')
                if player_index > -1:
                    start = max(0, player_index - 200)
                    end = min(len(script_content), player_index + 500)
                    sample = script_content[start:end]
                    print(f"\nSample around first player '{first_player}':")
                    print("=" * 60)
                    print(sample)
                    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_javascript_extraction())