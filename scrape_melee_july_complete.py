#!/usr/bin/env python3
"""
Scraper Melee complet pour juillet 2025
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MeleeJulyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.cookie_file = Path("api_credentials/melee_cookies.json")
        self.authenticated = False
        
    def authenticate(self):
        """Authenticate with Melee"""
        email = os.getenv('MELEE_EMAIL')
        password = os.getenv('MELEE_PASSWORD')
        
        if not email or not password:
            print("❌ MELEE_EMAIL and MELEE_PASSWORD must be set in .env")
            return False
            
        print("🔐 Authenticating...")
        
        # Get login page
        login_page = self.session.get("https://melee.gg/Account/SignIn")
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            print("❌ Could not find CSRF token")
            return False
            
        csrf_token = token_input["value"]
        
        # Submit login
        login_data = {
            "Email": email,
            "Password": password,
            "__RequestVerificationToken": csrf_token
        }
        
        response = self.session.post(
            "https://melee.gg/Account/SignInPassword",
            data=login_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://melee.gg/Account/SignIn'
            }
        )
        
        if response.status_code == 200 and ".AspNet.ApplicationCookie" in self.session.cookies:
            print("✅ Authentication successful!")
            self.authenticated = True
            
            # Save cookies
            self.cookie_file.parent.mkdir(exist_ok=True)
            cookies_to_save = {
                "cookies": self.session.cookies.get_dict(),
                "_timestamp": time.time()
            }
            with open(self.cookie_file, "w") as f:
                json.dump(cookies_to_save, f, indent=2)
            
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    def load_cookies(self):
        """Load cookies if valid"""
        if not self.cookie_file.exists():
            return False
            
        try:
            with open(self.cookie_file, "r") as f:
                data = json.load(f)
                timestamp = data.get("_timestamp", 0)
                age = time.time() - timestamp
                
                if age < 21 * 24 * 60 * 60:  # 21 days
                    self.session.cookies.update(data.get("cookies", {}))
                    print("✅ Loaded valid cookies")
                    self.authenticated = True
                    return True
        except Exception:
            pass
            
        return False
        
    def search_all_july_tournaments(self):
        """Search ALL tournaments from July 1st to today"""
        if not self.authenticated:
            if not self.load_cookies():
                if not self.authenticate():
                    return []
                    
        start_date = datetime(2025, 7, 1)
        end_date = datetime.now()
        
        print(f"\n🔍 Searching ALL tournaments from {start_date.date()} to {end_date.date()}")
        
        all_results = []
        draw = 1
        start = 0
        
        while True:
            payload = self._build_payload(start_date, end_date, draw, start)
            
            try:
                response = self.session.post(
                    "https://melee.gg/Decklist/DecklistSearch",
                    data=payload
                )
                
                if response.status_code != 200:
                    print(f"❌ Error status: {response.status_code}")
                    break
                    
                data = response.json()
                
                if "data" not in data:
                    break
                    
                new_entries = data.get("data", [])
                
                if not new_entries:
                    print(f"📊 No more data at page {draw}")
                    break
                
                all_results.extend(new_entries)
                
                print(f"📊 Page {draw}: {len(new_entries)} entries found (total: {len(all_results)})")
                
                # Check if we got all records
                records_total = data.get("recordsTotal", 0)
                if len(all_results) >= records_total:
                    print(f"✅ Got all {records_total} records")
                    break
                
                # Continue to next page
                draw += 1
                start += 50
                time.sleep(0.5)  # Rate limit
                
            except Exception as e:
                print(f"❌ Error: {e}")
                break
                
        print(f"\n✅ Found {len(all_results)} total decklist entries")
        
        # Group by tournament and format
        tournaments_by_format = {}
        
        for entry in all_results:
            format_name = entry.get("FormatDescription", "Unknown").lower()
            tournament_id = entry.get("TournamentId")
            
            if format_name not in tournaments_by_format:
                tournaments_by_format[format_name] = {}
                
            if tournament_id not in tournaments_by_format[format_name]:
                tournaments_by_format[format_name][tournament_id] = {
                    "TournamentId": tournament_id,
                    "TournamentName": entry.get("TournamentName"),
                    "TournamentStartDate": entry.get("TournamentStartDate"),
                    "OrganizationName": entry.get("OrganizationName"),
                    "FormatDescription": entry.get("FormatDescription"),
                    "Decks": []
                }
                
            deck_entry = {
                "DecklistId": entry.get("Guid"),
                "PlayerName": entry.get("OwnerDisplayName"),
                "DeckName": entry.get("DecklistName"),
                "Rank": entry.get("TeamRank"),
                "Wins": entry.get("TeamMatchWins"),
                "IsValid": entry.get("IsValid")
            }
            tournaments_by_format[format_name][tournament_id]["Decks"].append(deck_entry)
            
        return tournaments_by_format
        
    def _build_payload(self, start_date, end_date, draw, start):
        """Build the search payload"""
        date_filter = f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}"
        
        return {
            "draw": str(draw),
            "columns[0][data]": "DecklistName",
            "columns[0][name]": "DecklistName",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "Game",
            "columns[1][name]": "Game",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "MagicTheGathering",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "FormatId",
            "columns[2][name]": "FormatId",
            "columns[2][searchable]": "true",
            "columns[2][orderable]": "false",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "FormatName",
            "columns[3][name]": "FormatName",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "OwnerDisplayName",
            "columns[4][name]": "OwnerDisplayName",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "columns[5][data]": "TournamentName",
            "columns[5][name]": "TournamentName",
            "columns[5][searchable]": "true",
            "columns[5][orderable]": "true",
            "columns[5][search][value]": "",
            "columns[5][search][regex]": "false",
            "columns[6][data]": "SortDate",
            "columns[6][name]": "SortDate",
            "columns[6][searchable]": "true",
            "columns[6][orderable]": "true",
            "columns[6][search][value]": date_filter,
            "columns[6][search][regex]": "false",
            "columns[7][data]": "TeamRank",
            "columns[7][name]": "TeamRank",
            "columns[7][searchable]": "false",
            "columns[7][orderable]": "true",
            "columns[7][search][value]": "",
            "columns[7][search][regex]": "false",
            "columns[8][data]": "TeamMatchWins",
            "columns[8][name]": "TeamMatchWins",
            "columns[8][searchable]": "false",
            "columns[8][orderable]": "false",
            "columns[8][search][value]": "",
            "columns[8][search][regex]": "false",
            "columns[9][data]": "OrganizationName",
            "columns[9][name]": "OrganizationName",
            "columns[9][searchable]": "true",
            "columns[9][orderable]": "true",
            "columns[9][search][value]": "",
            "columns[9][search][regex]": "false",
            "columns[10][data]": "Records",
            "columns[10][name]": "Records",
            "columns[10][searchable]": "true",
            "columns[10][orderable]": "false",
            "columns[10][search][value]": "",
            "columns[10][search][regex]": "false",
            "columns[11][data]": "Archetypes",
            "columns[11][name]": "Archetypes",
            "columns[11][searchable]": "true",
            "columns[11][orderable]": "false",
            "columns[11][search][value]": "",
            "columns[11][search][regex]": "false",
            "columns[12][data]": "TournamentTags",
            "columns[12][name]": "TournamentTags",
            "columns[12][searchable]": "true",
            "columns[12][orderable]": "false",
            "columns[12][search][value]": "",
            "columns[12][search][regex]": "false",
            "columns[13][data]": "LeaderName",
            "columns[13][name]": "LeaderName",
            "columns[13][searchable]": "true",
            "columns[13][orderable]": "false",
            "columns[13][search][value]": "",
            "columns[13][search][regex]": "false",
            "columns[14][data]": "SecondaryName",
            "columns[14][name]": "SecondaryName",
            "columns[14][searchable]": "true",
            "columns[14][orderable]": "false",
            "columns[14][search][value]": "",
            "columns[14][search][regex]": "false",
            "order[0][column]": "6",
            "order[0][dir]": "desc",
            "start": str(start),
            "length": "50",
            "search[value]": "",
            "search[regex]": "false"
        }
        
    def save_tournaments(self, tournaments_by_format):
        """Save all tournaments organized by format"""
        base_dir = Path("data/raw/melee")
        
        total_saved = 0
        
        for format_name, tournaments in tournaments_by_format.items():
            if not tournaments:
                continue
                
            # Create format directory
            format_dir = base_dir / format_name
            format_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📁 Saving {len(tournaments)} {format_name} tournaments...")
            
            for tournament in tournaments.values():
                # Parse date
                date_str = tournament["TournamentStartDate"]
                if date_str:
                    date_str = date_str.rstrip("Z")
                    try:
                        date = datetime.fromisoformat(date_str)
                        date_formatted = date.strftime("%Y-%m-%d")
                    except:
                        date_formatted = "unknown"
                else:
                    date_formatted = "unknown"
                    
                # Clean name
                name_clean = re.sub(r'[^\w\s-]', '', tournament["TournamentName"])
                name_clean = re.sub(r'[-\s]+', '-', name_clean)[:50]
                filename = f"{date_formatted}_{name_clean}.json"
                filepath = format_dir / filename
                
                # Save
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(tournament, f, indent=2, ensure_ascii=False)
                
                total_saved += 1
                
            print(f"✅ Saved {len(tournaments)} {format_name} tournaments")
            
        return total_saved


def main():
    scraper = MeleeJulyScraper()
    
    print("🎯 Scraping ALL Melee.gg tournaments for July 2025")
    print("=" * 50)
    
    # Search all tournaments
    tournaments_by_format = scraper.search_all_july_tournaments()
    
    # Show summary
    print("\n📊 Summary by format:")
    total_tournaments = 0
    total_decks = 0
    
    for format_name, tournaments in tournaments_by_format.items():
        format_decks = sum(len(t["Decks"]) for t in tournaments.values())
        total_tournaments += len(tournaments)
        total_decks += format_decks
        print(f"  {format_name}: {len(tournaments)} tournaments, {format_decks} decks")
    
    print(f"\n📊 TOTAL: {total_tournaments} tournaments, {total_decks} decks")
    
    # Save all
    if tournaments_by_format:
        saved = scraper.save_tournaments(tournaments_by_format)
        print(f"\n✅ Saved {saved} tournament files total")
    else:
        print("\n⚠️  No tournaments found")


if __name__ == "__main__":
    main()