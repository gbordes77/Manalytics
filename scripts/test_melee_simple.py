"""
Test simple pour Melee comme fbettega le fait.
"""
import json
import requests
from datetime import datetime, timedelta

# Credentials
MELEE_EMAIL = "gbordes64@gmail.com"
MELEE_PASSWORD = "Ctr0Dur!"

def test_melee():
    """Test Melee authentication and search."""
    
    print("🔐 Testing Melee.gg authentication...")
    
    # Create session
    session = requests.Session()
    
    # Headers like a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    # Step 1: Login
    login_url = "https://melee.gg/Auth/Login"
    login_data = {
        "Email": MELEE_EMAIL,
        "Password": MELEE_PASSWORD,
        "RememberMe": "false"
    }
    
    print("📤 Sending login request...")
    response = session.post(login_url, data=login_data)
    print(f"Login response: {response.status_code}")
    
    # Check cookies
    print("\n🍪 Cookies after login:")
    for cookie in session.cookies:
        print(f"  - {cookie.name}: {cookie.value[:20]}...")
    
    # Step 2: Test tournament search
    print("\n🔍 Testing tournament search...")
    
    # Search payload (comme fbettega)
    search_url = "https://melee.gg/Tournament/SearchTournaments"
    search_data = {
        "draw": "1",
        "columns[0][data]": "ID",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "Name",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "StartDate",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "Status",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "Format",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "OrganizationName",
        "columns[5][name]": "",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "true",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "Decklists",
        "columns[6][name]": "",
        "columns[6][searchable]": "false",
        "columns[6][orderable]": "false",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "columns[7][data]": "Description",
        "columns[7][name]": "",
        "columns[7][searchable]": "false",
        "columns[7][orderable]": "false",
        "columns[7][search][value]": "",
        "columns[7][search][regex]": "false",
        "order[0][column]": "2",
        "order[0][dir]": "desc",
        "start": "0",
        "length": "25",
        "search[value]": "",
        "search[regex]": "false",
        "startDate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000Z"),
        "endDate": datetime.now().strftime("%Y-%m-%dT23:59:59.999Z")
    }
    
    response = session.post(search_url, data=search_data)
    print(f"Search response: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ Success! Found {len(data.get('data', []))} tournaments")
            
            # Show first tournament
            if data.get('data'):
                first = data['data'][0]
                print(f"\nFirst tournament:")
                print(f"  - ID: {first.get('ID')}")
                print(f"  - Name: {first.get('Name')}")
                print(f"  - Format: {first.get('Format')}")
                print(f"  - Date: {first.get('StartDate')}")
        except json.JSONDecodeError:
            print(f"\n❌ Not JSON. Response: {response.text[:500]}")
    else:
        print(f"\n❌ Error {response.status_code}: {response.text[:500]}")
    
    # Step 3: Test standings endpoint
    print("\n📊 Testing standings endpoint...")
    
    # Use a known tournament ID (you'll need to get this from search results)
    tournament_id = "12345"  # Replace with actual ID
    standings_url = f"https://melee.gg/Round/GetRoundStandings"
    
    standings_data = {
        "draw": "1",
        "columns[0][data]": "Rank",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "Player",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "Decklists",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "false",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "MatchRecord",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "GameRecord",
        "columns[4][name]": "",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "Points",
        "columns[5][name]": "",
        "columns[5][searchable]": "false",
        "columns[5][orderable]": "true",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "OpponentMatchWinPercentage",
        "columns[6][name]": "",
        "columns[6][searchable]": "false",
        "columns[6][orderable]": "true",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "columns[7][data]": "TeamGamesWinPercentage",
        "columns[7][name]": "",
        "columns[7][searchable]": "false",
        "columns[7][orderable]": "true",
        "columns[7][search][value]": "",
        "columns[7][search][regex]": "false",
        "columns[8][data]": "OpponentGameWinPercentage",
        "columns[8][name]": "",
        "columns[8][searchable]": "false",
        "columns[8][orderable]": "true",
        "columns[8][search][value]": "",
        "columns[8][search][regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "start": "0",
        "length": "25",
        "search[value]": "",
        "search[regex]": "false",
        "roundId": tournament_id
    }
    
    response = session.post(standings_url, data=standings_data)
    print(f"Standings response: {response.status_code}")

if __name__ == "__main__":
    test_melee()