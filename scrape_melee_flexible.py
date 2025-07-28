#!/usr/bin/env python3
"""
Scraper Melee.gg Flexible - Support multi-formats et dates personnalisables
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional, Set
import re
import argparse
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Formats supportés (mapping Melee.gg)
MELEE_FORMATS = {
    'standard': 'Standard',
    'modern': 'Modern',
    'legacy': 'Legacy',
    'vintage': 'Vintage',
    'pioneer': 'Pioneer',
    'pauper': 'Pauper',
    'commander': 'Commander',
    'duel-commander': 'Duel Commander',
    'limited': 'Limited'
}


class MtgMeleeClientFlexible:
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
        if self._cookies_valid():
            self._load_cookies()
            logger.info("✅ Cookies valides chargés")
        else:
            logger.info("🔄 Authentification nécessaire...")
            self._refresh_cookies()
            
    def _cookies_valid(self) -> bool:
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
                return age < timedelta(days=21)
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
        
        response = self.session.post(
            "https://melee.gg/Account/SignInPassword",
            headers=ajax_headers,
            data=login_data
        )
        
        if response.status_code != 200 or ".AspNet.ApplicationCookie" not in self.session.cookies:
            raise Exception("Échec de connexion")
            
        logger.info("✅ Connexion réussie!")
        
        # Sauvegarder les cookies
        cookies_to_save = {
            "cookies": self.session.cookies.get_dict(),
            "_timestamp": time.time()
        }
        with open(self.cookie_file, "w") as f:
            json.dump(cookies_to_save, f, indent=2)
            
    def search_tournaments(self, start_date: datetime, end_date: datetime, formats: Set[str]) -> List[Dict]:
        """Rechercher les tournois pour les formats spécifiés"""
        self.ensure_authenticated()
        
        result = []
        
        # Rechercher pour chaque format demandé
        for format_key in formats:
            if format_key == 'all':
                # Rechercher tous les formats
                search_formats = list(MELEE_FORMATS.keys())
            else:
                search_formats = [format_key]
            
            for fmt in search_formats:
                if fmt not in MELEE_FORMATS:
                    continue
                    
                logger.info(f"\n🔍 Recherche format: {MELEE_FORMATS[fmt]}")
                format_results = self._search_format(start_date, end_date, MELEE_FORMATS[fmt])
                result.extend(format_results)
                
        return result
        
    def _search_format(self, start_date: datetime, end_date: datetime, format_name: str) -> List[Dict]:
        """Rechercher les tournois pour un format spécifique"""
        results = []
        draw = 1
        start = 0
        seen_ids = set()
        
        while True:
            payload = self._build_payload(start_date, end_date, draw, start, format_name)
            
            if self.token:
                payload["__RequestVerificationToken"] = self.token
                
            try:
                response = self.session.post(
                    "https://melee.gg/Decklist/SearchDecklists",
                    data=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Erreur status: {response.status_code}")
                    break
                    
                if not response.text.strip():
                    break
                    
                if response.text.startswith('<!DOCTYPE'):
                    logger.warning("⚠️ Réponse HTML au lieu de JSON - réessai avec authentification")
                    self._refresh_cookies()
                    continue
                    
                data = response.json()
                
                if "data" not in data:
                    break
                    
                new_entries = data.get("data", [])
                
                # Filtrer et ajouter uniquement les nouveaux
                for entry in new_entries:
                    entry_id = entry.get('Guid')
                    if entry_id not in seen_ids:
                        # Vérifier que c'est bien le bon format
                        if format_name.lower() in entry.get("FormatDescription", "").lower():
                            results.append(entry)
                            seen_ids.add(entry_id)
                        
                logger.info(f"Page {draw}: {len(new_entries)} entrées trouvées")
                
                # Vérifier s'il y a plus de données
                if len(new_entries) < 50 or len(results) >= data.get("recordsFiltered", 0):
                    break
                    
                draw += 1
                start += 50
                time.sleep(0.5)
                
            except json.JSONDecodeError as e:
                logger.error(f"Erreur JSON: {e}")
                break
            except Exception as e:
                logger.error(f"Erreur: {e}")
                break
                
        return results
        
    def get_deck(self, deck_id: str) -> Optional[Dict]:
        """Récupérer les détails d'un deck (optionnel)"""
        try:
            url = f"https://melee.gg/Decklist/View/{deck_id}"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            deck_text = soup.select_one("pre#decklist-text")
            if not deck_text:
                return None
                
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
                    
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    count = int(parts[0])
                    card_name = parts[1]
                    current_section.append({
                        "Count": count,
                        "CardName": card_name
                    })
                    
            player_link = soup.select_one("a.text-nowrap.text-muted span.text-nowrap")
            player_name = player_link.text.strip() if player_link else "Unknown"
            
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
            logger.error(f"Erreur récupération deck {deck_id}: {e}")
            return None
    
    def get_round_standings(self, tournament_id: int, round_id: int) -> Optional[List[Dict]]:
        """Récupérer les standings d'un round spécifique"""
        try:
            payload = {
                "draw": "1",
                "columns[0][data]": "Rank",
                "columns[0][name]": "Rank",
                "columns[0][searchable]": "true",
                "columns[0][orderable]": "true",
                "columns[0][search][value]": "",
                "columns[0][search][regex]": "false",
                "columns[1][data]": "Player",
                "columns[1][name]": "Player",
                "columns[1][searchable]": "true",
                "columns[1][orderable]": "true",
                "columns[1][search][value]": "",
                "columns[1][search][regex]": "false",
                "columns[2][data]": "Decklists",
                "columns[2][name]": "Decklists",
                "columns[2][searchable]": "true",
                "columns[2][orderable]": "true",
                "columns[2][search][value]": "",
                "columns[2][search][regex]": "false",
                "columns[3][data]": "MatchRecord",
                "columns[3][name]": "MatchRecord",
                "columns[3][searchable]": "true",
                "columns[3][orderable]": "true",
                "columns[3][search][value]": "",
                "columns[3][search][regex]": "false",
                "columns[4][data]": "GameRecord",
                "columns[4][name]": "GameRecord",
                "columns[4][searchable]": "true",
                "columns[4][orderable]": "true",
                "columns[4][search][value]": "",
                "columns[4][search][regex]": "false",
                "columns[5][data]": "Points",
                "columns[5][name]": "Points",
                "columns[5][searchable]": "true",
                "columns[5][orderable]": "true",
                "columns[5][search][value]": "",
                "columns[5][search][regex]": "false",
                "columns[6][data]": "OpponentMatchWinPercentage",
                "columns[6][name]": "OpponentMatchWinPercentage",
                "columns[6][searchable]": "true",
                "columns[6][orderable]": "true",
                "columns[6][search][value]": "",
                "columns[6][search][regex]": "false",
                "columns[7][data]": "TeamGamesWinPercentage",
                "columns[7][name]": "TeamGamesWinPercentage",
                "columns[7][searchable]": "true",
                "columns[7][orderable]": "true",
                "columns[7][search][value]": "",
                "columns[7][search][regex]": "false",
                "columns[8][data]": "OpponentGameWinPercentage",
                "columns[8][name]": "OpponentGameWinPercentage",
                "columns[8][searchable]": "true",
                "columns[8][orderable]": "true",
                "columns[8][search][value]": "",
                "columns[8][search][regex]": "false",
                "start": "0",
                "length": "100",
                "search[value]": "",
                "search[regex]": "false",
                "tournamentId": str(tournament_id),
                "roundId": str(round_id)
            }
            
            if self.token:
                payload["__RequestVerificationToken"] = self.token
            
            response = self.session.post(
                "https://melee.gg/Standing/GetRoundStandings",
                data=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur standings: {response.status_code}")
                return None
                
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Erreur récupération standings: {e}")
            return None
            
    def _build_payload(self, start_date: datetime, end_date: datetime, draw: int, start: int, format_filter: str = "") -> Dict:
        """Construire le payload pour la recherche"""
        date_filter = f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}"
        
        payload = {
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
            "columns[3][search][value]": format_filter,
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
        
        return payload
    
    def save_tournaments(self, entries: List[Dict], get_decks: bool = False, get_rounds: bool = False) -> int:
        """Sauvegarder les tournois par format"""
        # Grouper par tournoi et format
        tournaments_by_format = {}
        
        for entry in entries:
            format_key = self._get_format_key(entry.get("FormatDescription", ""))
            tournament_id = entry.get("TournamentId")
            
            if format_key not in tournaments_by_format:
                tournaments_by_format[format_key] = {}
                
            if tournament_id not in tournaments_by_format[format_key]:
                tournaments_by_format[format_key][tournament_id] = {
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
            tournaments_by_format[format_key][tournament_id]["Decks"].append(deck_entry)
        
        # Sauvegarder par format
        saved_count = 0
        
        for format_key, tournaments in tournaments_by_format.items():
            output_dir = Path(f"data/raw/melee/{format_key}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
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
                filepath = output_dir / filename
                
                logger.info(f"📥 {format_key}: {tournament_data['TournamentName']}")
                logger.info(f"   {len(tournament_data['Decks'])} decks trouvés")
                
                # Optionnel: récupérer quelques decks
                if get_decks:
                    top_decks = sorted(tournament_data['Decks'], key=lambda x: x.get('Rank', 999))[:5]
                    for deck_info in top_decks:
                        deck_id = deck_info['DecklistId']
                        if deck_id:
                            deck_details = self.get_deck(deck_id)
                            if deck_details:
                                deck_info['Details'] = deck_details
                                logger.info(f"   ✅ Deck récupéré: {deck_details['Player']}")
                
                # Récupérer les round standings si demandé
                if get_rounds:
                    logger.info(f"   🎲 Récupération des round standings...")
                    round_standings = []
                    
                    # Essayer de récupérer les standings pour les 15 premiers rounds
                    for round_num in range(1, 16):
                        standings = self.get_round_standings(tournament_id, round_num)
                        if standings:
                            logger.info(f"      Round {round_num}: {len(standings)} joueurs")
                            round_standings.append({
                                'round': round_num,
                                'standings': standings
                            })
                        else:
                            # Si pas de standings, on suppose qu'il n'y a plus de rounds
                            break
                    
                    if round_standings:
                        tournament_data['RoundStandings'] = round_standings
                        tournament_data['TotalRounds'] = len(round_standings)
                        logger.info(f"   📊 {len(round_standings)} rounds récupérés")
                
                # Sauvegarder
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(tournament_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"   💾 Sauvegardé: {filename}")
                saved_count += 1
                
        return saved_count
    
    def _get_format_key(self, format_description: str) -> str:
        """Convertir la description du format en clé"""
        desc_lower = format_description.lower()
        
        for key, name in MELEE_FORMATS.items():
            if name.lower() in desc_lower:
                return key
                
        return 'other'


def main():
    parser = argparse.ArgumentParser(description='Scrape Melee.gg tournaments flexibly')
    
    # Arguments de date
    parser.add_argument('--start-date', type=str,
                       help='Date de début (YYYY-MM-DD). Par défaut: 7 jours avant')
    parser.add_argument('--end-date', type=str,
                       help='Date de fin (YYYY-MM-DD). Par défaut: aujourd\'hui')
    parser.add_argument('--days', type=int,
                       help='Alternative: nombre de jours à partir d\'aujourd\'hui')
    
    # Arguments de format
    parser.add_argument('--format', type=str, nargs='+',
                       choices=list(MELEE_FORMATS.keys()) + ['all'],
                       default=['standard'],
                       help='Format(s) à scraper. Par défaut: standard')
    
    # Options supplémentaires
    parser.add_argument('--get-decks', action='store_true',
                       help='Récupérer les détails des decks (plus lent)')
    parser.add_argument('--get-rounds', action='store_true',
                       help='Récupérer les round standings pour la matrice de matchups')
    parser.add_argument('--incremental', action='store_true',
                       help='Mode incrémental: scraper seulement les nouveaux tournois')
    
    args = parser.parse_args()
    
    # Déterminer les dates
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    elif args.days:
        start_date = end_date - timedelta(days=args.days)
    else:
        start_date = end_date - timedelta(days=7)
    
    # Formats à scraper
    formats = set(args.format)
    
    logger.info("🎯 Melee.gg Flexible Scraper")
    logger.info("=" * 50)
    logger.info(f"📅 Période: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🎮 Formats: {', '.join(formats)}")
    if args.get_decks:
        logger.info("📝 Récupération des decks activée")
    if args.get_rounds:
        logger.info("🎲 Récupération des round standings activée")
    
    # Initialiser le client
    client = MtgMeleeClientFlexible()
    
    # Rechercher les tournois
    logger.info("\n🔍 Recherche des tournois...")
    entries = client.search_tournaments(start_date, end_date, formats)
    
    logger.info(f"\n✅ Trouvé {len(entries)} entrées de decklists")
    
    if entries:
        # Afficher le résumé par format
        format_counts = {}
        for entry in entries:
            fmt = client._get_format_key(entry.get("FormatDescription", ""))
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
        logger.info("\n📊 Résumé par format:")
        for fmt, count in sorted(format_counts.items()):
            logger.info(f"  {fmt}: {count} entrées")
        
        # Sauvegarder
        saved = client.save_tournaments(entries, get_decks=args.get_decks, get_rounds=args.get_rounds)
        logger.info(f"\n✅ {saved} tournois sauvegardés")
        
        if args.incremental:
            logger.info("💡 Mode incrémental activé - seuls les nouveaux tournois ont été sauvés")
    else:
        logger.warning("Aucun tournoi trouvé pour les critères spécifiés")


if __name__ == "__main__":
    main()