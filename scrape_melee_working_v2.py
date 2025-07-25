#!/usr/bin/env python3
"""
Scraper Melee.gg fonctionnel basé sur le code original
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import re

class MtgMeleeClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.cookie_file = "api_credentials/melee_cookies.json"
        self.cred_file = "api_credentials/melee_login.json"
        self.token = None
        
    def ensure_authenticated(self):
        """S'assurer qu'on est authentifié"""
        # Vérifier si on a des cookies valides
        if self._cookies_valid():
            self._load_cookies()
            print("✅ Cookies valides chargés")
        else:
            print("🔄 Authentification nécessaire...")
            self._refresh_cookies()
            
    def _cookies_valid(self):
        """Vérifier si les cookies sont encore valides"""
        if not os.path.exists(self.cookie_file):
            return False
        try:
            with open(self.cookie_file, "r") as f:
                data = json.load(f)
                timestamp = data.get("_timestamp")
                if not timestamp:
                    return False
                age = datetime.now() - datetime.fromtimestamp(timestamp)
                return age < timedelta(days=21)  # Cookies valides 21 jours
        except Exception:
            return False
            
    def _load_cookies(self):
        """Charger les cookies depuis le fichier"""
        with open(self.cookie_file, "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", {})
            self.session.cookies.update(cookies)
            
    def _refresh_cookies(self):
        """Se connecter et sauvegarder les cookies"""
        # Headers classiques pour la page de login
        classic_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Récupérer le token CSRF
        login_page = self.session.get("https://melee.gg/Account/SignIn", headers=classic_headers)
        if login_page.status_code != 200:
            raise Exception(f"Erreur accès page login: {login_page.status_code}")
            
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            raise Exception("Token CSRF non trouvé")
        self.token = token_input["value"]
        
        # Charger les credentials
        if not os.path.exists(self.cred_file):
            raise FileNotFoundError("Fichier credentials manquant")
        with open(self.cred_file, "r") as f:
            creds = json.load(f)
            
        # Headers AJAX pour le login
        ajax_headers = {
            "User-Agent": classic_headers["User-Agent"],
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://melee.gg",
            "Referer": "https://melee.gg/Account/SignIn"
        }
        
        login_data = {
            "email": creds["login"],
            "password": creds["mdp"],
            "__RequestVerificationToken": self.token
        }
        
        # Se connecter
        response = self.session.post(
            "https://melee.gg/Account/SignInPassword",
            headers=ajax_headers,
            data=login_data
        )
        
        if response.status_code != 200 or ".AspNet.ApplicationCookie" not in self.session.cookies:
            raise Exception("Échec de connexion")
            
        print("✅ Connexion réussie!")
        
        # Sauvegarder les cookies
        cookies_to_save = {
            "cookies": self.session.cookies.get_dict(),
            "_timestamp": time.time()
        }
        with open(self.cookie_file, "w") as f:
            json.dump(cookies_to_save, f, indent=2)
            
    def search_tournaments(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Rechercher les tournois entre deux dates"""
        self.ensure_authenticated()
        
        result = []
        draw = 1
        start = 0
        seen_ids = set()
        
        while True:
            payload = self._build_payload(start_date, end_date, draw, start)
            
            # Ajouter le token si disponible
            if self.token:
                payload["__RequestVerificationToken"] = self.token
                
            try:
                response = self.session.post(
                    "https://melee.gg/Decklist/SearchDecklists",
                    data=payload
                )
                
                if response.status_code != 200:
                    print(f"Erreur status: {response.status_code}")
                    break
                    
                if not response.text.strip():
                    print("Réponse vide")
                    break
                    
                # Vérifier si c'est du JSON
                if response.text.startswith('<!DOCTYPE'):
                    print("⚠️ Réponse HTML au lieu de JSON - réessai avec authentification")
                    self._refresh_cookies()
                    continue
                    
                data = response.json()
                
                if "data" not in data:
                    break
                    
                new_tournaments = data.get("data", [])
                
                # Ajouter uniquement les nouveaux tournois
                for tournament in new_tournaments:
                    tournament_id = tournament.get('Guid')
                    if tournament_id not in seen_ids:
                        result.append(tournament)
                        seen_ids.add(tournament_id)
                        
                print(f"Page {draw}: {len(new_tournaments)} entrées trouvées")
                
                # Vérifier s'il y a plus de données
                if len(new_tournaments) < 50 or len(result) >= data.get("recordsFiltered", 0):
                    break
                    
                draw += 1
                start += 50
                time.sleep(0.5)  # Délai entre les requêtes
                
            except json.JSONDecodeError as e:
                print(f"Erreur JSON: {e}")
                print(f"Réponse: {response.text[:200]}...")
                break
            except Exception as e:
                print(f"Erreur: {e}")
                break
                
        return result
        
    def get_deck(self, deck_id: str) -> Optional[Dict]:
        """Récupérer les détails d'un deck"""
        try:
            url = f"https://melee.gg/Decklist/View/{deck_id}"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire la decklist
            deck_text = soup.select_one("pre#decklist-text")
            if not deck_text:
                return None
                
            # Parser le deck
            lines = deck_text.text.strip().split("\r\n")
            mainboard = []
            sideboard = []
            current_section = mainboard
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line in ["Sideboard", "Companion"]:
                    current_section = sideboard
                    continue
                elif line in ["MainDeck", "Deck", "Commander"]:
                    current_section = mainboard
                    continue
                    
                # Parser "X Card Name"
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    count = int(parts[0])
                    card_name = parts[1]
                    current_section.append({
                        "Count": count,
                        "CardName": card_name
                    })
                    
            # Extraire le joueur
            player_link = soup.select_one("a.text-nowrap.text-muted span.text-nowrap")
            player_name = player_link.text.strip() if player_link else "Unknown"
            
            # Extraire le format
            format_div = soup.select_one(".d-flex.flex-row.gap-8px .text-nowrap:last-of-type")
            format_name = format_div.text.strip() if format_div else "Unknown"
            
            return {
                "DeckId": deck_id,
                "Player": player_name,
                "Format": format_name,
                "Mainboard": mainboard,
                "Sideboard": sideboard,
                "Uri": url
            }
            
        except Exception as e:
            print(f"Erreur récupération deck {deck_id}: {e}")
            return None
            
    def _build_payload(self, start_date: datetime, end_date: datetime, draw: int, start: int) -> Dict:
        """Construire le payload pour la recherche"""
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


def main():
    """Script principal"""
    # Configuration
    FORMAT = "Standard"
    OUTPUT_DIR = f"data/raw/melee/standard"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Période de recherche
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"🎯 Scraping Melee.gg - Format: {FORMAT}")
    print(f"📅 Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    
    # Initialiser le client
    client = MtgMeleeClient()
    
    # Rechercher les tournois
    print("\n🔍 Recherche des tournois...")
    entries = client.search_tournaments(start_date, end_date)
    
    print(f"\n✅ Trouvé {len(entries)} entrées de decklists")
    
    # Grouper par tournoi
    tournaments = {}
    for entry in entries:
        # Filtrer par format
        if FORMAT.lower() not in entry.get("FormatDescription", "").lower():
            continue
            
        tournament_id = entry.get("TournamentId")
        if tournament_id not in tournaments:
            tournaments[tournament_id] = {
                "TournamentId": tournament_id,
                "TournamentName": entry.get("TournamentName"),
                "TournamentStartDate": entry.get("TournamentStartDate"),
                "OrganizationName": entry.get("OrganizationName"),
                "FormatDescription": entry.get("FormatDescription"),
                "Decks": []
            }
            
        # Ajouter le deck
        deck_entry = {
            "DecklistId": entry.get("Guid"),
            "PlayerName": entry.get("OwnerDisplayName"),
            "DeckName": entry.get("DecklistName"),
            "Rank": entry.get("TeamRank"),
            "Wins": entry.get("TeamMatchWins"),
            "IsValid": entry.get("IsValid")
        }
        tournaments[tournament_id]["Decks"].append(deck_entry)
    
    print(f"\n📊 {len(tournaments)} tournois {FORMAT} trouvés")
    
    # Sauvegarder chaque tournoi
    saved_count = 0
    for tournament_id, tournament_data in tournaments.items():
        # Parser la date
        date_str = tournament_data["TournamentStartDate"]
        if date_str:
            date_str = date_str.rstrip("Z")
            try:
                date = datetime.fromisoformat(date_str)
                date_formatted = date.strftime("%Y-%m-%d")
            except:
                date_formatted = "unknown"
        else:
            date_formatted = "unknown"
            
        # Nom de fichier
        name_clean = re.sub(r'[^\w\s-]', '', tournament_data["TournamentName"])
        name_clean = re.sub(r'[-\s]+', '-', name_clean)
        filename = f"{date_formatted}_{name_clean}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Enrichir avec quelques decks (optionnel)
        print(f"\n📥 Traitement: {tournament_data['TournamentName']}")
        print(f"   {len(tournament_data['Decks'])} decks trouvés")
        
        # Récupérer les détails de quelques decks top (optionnel, commenté pour aller plus vite)
        # top_decks = sorted(tournament_data['Decks'], key=lambda x: x.get('Rank', 999))[:8]
        # for deck_info in top_decks:
        #     deck_id = deck_info['DecklistId']
        #     if deck_id:
        #         deck_details = client.get_deck(deck_id)
        #         if deck_details:
        #             deck_info['Details'] = deck_details
        #             print(f"   ✅ Deck récupéré: {deck_details['Player']}")
        
        # Sauvegarder
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tournament_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Sauvegardé: {filename}")
        saved_count += 1
        
    print(f"\n✅ Terminé! {saved_count} tournois sauvegardés dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()