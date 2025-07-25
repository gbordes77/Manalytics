#!/usr/bin/env python3
"""
Scraper Melee.gg simplifié et robuste
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional

class MeleeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.base_url = "https://melee.gg"
        self.token = None
        
    def get_csrf_token(self) -> Optional[str]:
        """Récupère le token CSRF depuis la page de login"""
        try:
            response = self.session.get(f"{self.base_url}/Account/SignIn")
            if response.status_code != 200:
                print(f"Erreur lors de la récupération de la page de login: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, "html.parser")
            token_input = soup.find("input", {"name": "__RequestVerificationToken"})
            
            if token_input:
                self.token = token_input.get("value")
                print(f"Token CSRF récupéré: {self.token[:20]}...")
                return self.token
            else:
                print("Token CSRF non trouvé dans la page")
                return None
                
        except Exception as e:
            print(f"Erreur lors de la récupération du token: {e}")
            return None
            
    def login(self, email: str, password: str) -> bool:
        """Se connecte à Melee.gg"""
        if not self.token:
            self.get_csrf_token()
            
        if not self.token:
            print("Impossible de se connecter sans token CSRF")
            return False
            
        login_data = {
            "email": email,
            "password": password,
            "__RequestVerificationToken": self.token
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/Account/SignInPassword",
                data=login_data,
                headers={
                    **self.session.headers,
                    "Origin": self.base_url,
                    "Referer": f"{self.base_url}/Account/SignIn"
                }
            )
            
            if response.status_code == 200:
                # Vérifier si on a le cookie d'authentification
                if ".AspNet.ApplicationCookie" in self.session.cookies:
                    print("Connexion réussie!")
                    return True
                else:
                    print("Connexion échouée - pas de cookie d'auth")
                    return False
            else:
                print(f"Erreur de connexion: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False
            
    def search_tournaments(self, start_date: datetime, end_date: datetime, format_filter: str = "") -> List[Dict]:
        """Recherche les tournois entre deux dates"""
        # S'assurer d'avoir un token CSRF
        if not self.token:
            self.get_csrf_token()
            
        tournaments = []
        draw = 1
        start = 0
        
        while True:
            payload = self._build_search_payload(start_date, end_date, draw, start)
            
            try:
                # Ajouter le token CSRF si on l'a
                if self.token:
                    payload["__RequestVerificationToken"] = self.token
                    
                response = self.session.post(
                    f"{self.base_url}/Decklist/SearchDecklists",
                    data=payload
                )
                
                if response.status_code != 200:
                    print(f"Erreur lors de la recherche: {response.status_code}")
                    print(f"Réponse: {response.text[:500]}")
                    break
                
                # Debug: afficher le début de la réponse
                if not response.text.strip():
                    print("Réponse vide reçue")
                    break
                    
                print(f"Réponse (premiers 200 caractères): {response.text[:200]}")
                    
                data = response.json()
                
                if "data" not in data or len(data["data"]) == 0:
                    break
                    
                # Filtrer par format si spécifié
                for item in data["data"]:
                    if not format_filter or format_filter.lower() in item.get("FormatDescription", "").lower():
                        tournaments.append(item)
                
                print(f"Récupéré {len(data['data'])} tournois (page {draw})")
                
                # Vérifier s'il y a plus de données
                if len(data["data"]) < 50:  # Moins d'une page complète
                    break
                    
                draw += 1
                start += 50
                time.sleep(0.5)  # Petit délai pour ne pas surcharger le serveur
                
            except Exception as e:
                print(f"Erreur lors de la recherche de tournois: {e}")
                break
                
        return tournaments
        
    def get_tournament_standings(self, tournament_id: str, round_id: str) -> List[Dict]:
        """Récupère les standings d'un tournoi"""
        standings = []
        start = 0
        
        while True:
            payload = {
                "draw": "1",
                "start": str(start),
                "length": "25",
                "roundId": round_id
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/Standing/GetRoundStandings",
                    data=payload
                )
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                
                if "data" not in data or len(data["data"]) == 0:
                    break
                    
                standings.extend(data["data"])
                
                if len(data["data"]) < 25:
                    break
                    
                start += 25
                
            except Exception as e:
                print(f"Erreur lors de la récupération des standings: {e}")
                break
                
        return standings
        
    def get_deck_details(self, deck_id: str) -> Optional[Dict]:
        """Récupère les détails d'un deck"""
        try:
            response = self.session.get(f"{self.base_url}/Decklist/View/{deck_id}")
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraire la decklist
            deck_text = soup.find("pre", id="decklist-text")
            if not deck_text:
                return None
                
            # Parser la decklist
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
                elif line in ["MainDeck", "Deck"]:
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
                    
            return {
                "DeckId": deck_id,
                "Mainboard": mainboard,
                "Sideboard": sideboard
            }
            
        except Exception as e:
            print(f"Erreur lors de la récupération du deck {deck_id}: {e}")
            return None
            
    def _build_search_payload(self, start_date: datetime, end_date: datetime, draw: int, start: int) -> Dict:
        """Construit le payload pour la recherche de tournois"""
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
    # Configuration
    OUTPUT_DIR = "data/raw/melee/standard"
    FORMAT = "Standard"
    
    # Créer le répertoire de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialiser le scraper
    scraper = MeleeScraper()
    
    # Charger les credentials et se connecter
    cred_file = "api_credentials/melee_login.json"
    if os.path.exists(cred_file):
        with open(cred_file, "r") as f:
            creds = json.load(f)
        
        # Se connecter
        print("Connexion à Melee.gg...")
        if scraper.login(creds["login"], creds["mdp"]):
            print("Connexion réussie!")
        else:
            print("Échec de la connexion, on continue quand même...")
    
    # Définir la période de recherche
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Recherche des tournois {FORMAT} du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}")
    
    # Rechercher les tournois
    tournaments = scraper.search_tournaments(start_date, end_date, FORMAT)
    
    print(f"\nTrouvé {len(tournaments)} entrées de tournois")
    
    # Grouper par tournoi
    tournaments_by_id = {}
    for item in tournaments:
        tournament_id = item.get("TournamentId")
        if tournament_id not in tournaments_by_id:
            tournaments_by_id[tournament_id] = {
                "id": tournament_id,
                "name": item.get("TournamentName"),
                "date": item.get("TournamentStartDate"),
                "organizer": item.get("OrganizationName"),
                "format": item.get("FormatDescription"),
                "entries": []
            }
        tournaments_by_id[tournament_id]["entries"].append(item)
    
    print(f"Nombre de tournois uniques: {len(tournaments_by_id)}")
    
    # Sauvegarder les données brutes
    for tournament_id, tournament_data in tournaments_by_id.items():
        # Parser la date
        date_str = tournament_data["date"]
        if date_str:
            # Enlever le 'Z' à la fin si présent
            date_str = date_str.rstrip("Z")
            try:
                date = datetime.fromisoformat(date_str)
                date_formatted = date.strftime("%Y-%m-%d")
            except:
                date_formatted = "unknown-date"
        else:
            date_formatted = "unknown-date"
        
        # Créer le nom de fichier
        tournament_name = tournament_data["name"].replace("/", "-").replace(":", "")
        filename = f"{date_formatted}_{tournament_name}_{tournament_id}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Sauvegarder
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tournament_data, f, indent=2, ensure_ascii=False)
        
        print(f"Sauvegardé: {filename}")
    
    print(f"\nTerminé! {len(tournaments_by_id)} tournois sauvegardés dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()