# -*- coding: utf-8 -*-
"""
Melee Scraper Authentique - Reproduction fidèle de fbettega/mtg_decklist_scrapper
Récupère les vraies données depuis melee.gg via API
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .models.base_models import *


class MtgMeleeConstants:
    """Constantes pour le scraper Melee - reproduction fidèle de l'original"""

    # URL templates for various pages
    DECK_PAGE = "https://melee.gg/Decklist/View/{deckId}"
    PLAYER_DETAILS_PAGE = "https://melee.gg/Player/GetPlayerDetails?id={playerId}"
    TOURNAMENT_PAGE = "https://melee.gg/Tournament/View/{tournamentId}"
    TOURNAMENT_LIST_PAGE = "https://melee.gg/Decklist/TournamentSearch"
    ROUND_PAGE = "https://melee.gg/Standing/GetRoundStandings"

    # Parameters for the Tournament List page (DataTables format)
    TOURNAMENT_LIST_PARAMETERS = (
        "draw=1&columns%5B0%5D%5Bdata%5D=ID&columns%5B0%5D%5Bname%5D=ID&columns%5B0%5D%5Bsearchable%5D=false&"
        "columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B1%5D%5Bdata%5D=Name&columns%5B1%5D%5Bname%5D=Name&columns%5B1%5D%5Bsearchable%5D=true&"
        "columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B2%5D%5Bdata%5D=StartDate&columns%5B2%5D%5Bname%5D=StartDate&columns%5B2%5D%5Bsearchable%5D=false&"
        "columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B3%5D%5Bdata%5D=Status&columns%5B3%5D%5Bname%5D=Status&columns%5B3%5D%5Bsearchable%5D=true&"
        "columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B4%5D%5Bdata%5D=Format&columns%5B4%5D%5Bname%5D=Format&columns%5B4%5D%5Bsearchable%5D=true&"
        "columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B5%5D%5Bdata%5D=OrganizationName&columns%5B5%5D%5Bname%5D=OrganizationName&columns%5B5%5D%5Bsearchable%5D=true&"
        "columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B6%5D%5Bdata%5D=Decklists&columns%5B6%5D%5Bname%5D=Decklists&columns%5B6%5D%5Bsearchable%5D=true&"
        "columns%5B6%5D%5Borderable%5D=true&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=desc&"
        "start={offset}&length=25&search%5Bvalue%5D=&search%5Bregex%5D=false&q=&"
        "startDate={startDate}T00%3A00%3A00.000Z&endDate={endDate}T23%3A59%3A59.999Z"
    )

    # Parameters for the Round Page
    ROUND_PAGE_PARAMETERS = (
        "draw=1&columns%5B0%5D%5Bdata%5D=Rank&columns%5B0%5D%5Bname%5D=Rank&columns%5B0%5D%5Bsearchable%5D=true&"
        "columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B1%5D%5Bdata%5D=Player&columns%5B1%5D%5Bname%5D=Player&columns%5B1%5D%5Bsearchable%5D=false&"
        "columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B2%5D%5Bdata%5D=Decklists&columns%5B2%5D%5Bname%5D=Decklists&columns%5B2%5D%5Bsearchable%5D=false&"
        "columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B3%5D%5Bdata%5D=MatchRecord&columns%5B3%5D%5Bname%5D=MatchRecord&columns%5B3%5D%5Bsearchable%5D=false&"
        "columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B4%5D%5Bdata%5D=GameRecord&columns%5B4%5D%5Bname%5D=GameRecord&columns%5B4%5D%5Bsearchable%5D=false&"
        "columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B5%5D%5Bdata%5D=Points&columns%5B5%5D%5Bname%5D=Points&columns%5B5%5D%5Bsearchable%5D=true&"
        "columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B6%5D%5Bdata%5D=OpponentMatchWinPercentage&columns%5B6%5D%5Bname%5D=OpponentMatchWinPercentage&"
        "columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&"
        "columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=TeamGameWinPercentage&"
        "columns%5B7%5D%5Bname%5D=TeamGameWinPercentage&columns%5B7%5D%5Bsearchable%5D=false&"
        "columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B8%5D%5Bdata%5D=OpponentGameWinPercentage&columns%5B8%5D%5Bname%5D=OpponentGameWinPercentage&"
        "columns%5B8%5D%5Bsearchable%5D=false&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&"
        "columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=FinalTiebreaker&"
        "columns%5B9%5D%5Bname%5D=FinalTiebreaker&columns%5B9%5D%5Bsearchable%5D=true&"
        "columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&"
        "columns%5B10%5D%5Bdata%5D=OpponentCount&columns%5B10%5D%5Bname%5D=OpponentCount&"
        "columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&"
        "columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&"
        "order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start={start}&length=25&"
        "search%5Bvalue%5D=&search%5Bregex%5D=false&roundId={roundId}"
    )

    # Configuration
    MaxDaysBeforeTournamentMarkedAsEnded = 30
    VALID_DECKLIST_THRESHOLD = 0.5
    Min_number_of_valid_decklists = 5

    @staticmethod
    def format_url(url, **params):
        return url.format(**params)


class MtgMeleeClient:
    """Client HTTP pour Melee - reproduction fidèle de l'original"""

    @staticmethod
    def get_client():
        """Crée une session HTTP avec les headers appropriés"""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        return session

    @staticmethod
    def normalize_spaces(data):
        """Normalise les espaces dans les chaînes de caractères"""
        return re.sub(r"\s+", " ", data).strip()

    def get_players(self, uri, max_players=None):
        """Récupère les joueurs d'un tournoi via l'API"""
        result = []

        # Récupérer la page du tournoi pour obtenir les round IDs
        page_content = self.get_client().get(uri).text
        soup = BeautifulSoup(page_content, "html.parser")

        # Trouver les rounds complétés
        round_nodes = soup.select(
            'button.btn.btn-gray.round-selector[data-is-completed="True"]'
        )

        if not round_nodes:
            return None

        round_ids = [node["data-id"] for node in round_nodes]
        round_id = round_ids[-1]  # Utiliser le dernier round

        offset = 0
        while True:
            has_data = False
            round_parameters = MtgMeleeConstants.ROUND_PAGE_PARAMETERS.replace(
                "{start}", str(offset)
            ).replace("{roundId}", round_id)

            response = self.get_client().post(
                MtgMeleeConstants.ROUND_PAGE, data=round_parameters
            )
            round_data = json.loads(response.text)

            if len(round_data["data"]) == 0 and offset == 0:
                if len(round_ids) > 1:
                    round_ids = round_ids[:-1]
                    round_id = round_ids[-1]
                    has_data = True
                    continue
                else:
                    break

            for entry in round_data["data"]:
                has_data = True
                player_name = entry["Team"]["Players"][0]["DisplayName"]
                if not player_name:
                    continue

                player_name = self.normalize_spaces(player_name)
                user_name = entry["Team"]["Players"][0]["Username"]
                player_points = entry["Points"]
                omwp = entry["OpponentMatchWinPercentage"]
                gwp = entry["TeamGameWinPercentage"]
                ogwp = entry["OpponentGameWinPercentage"]
                player_position = entry["Rank"]
                wins = entry["MatchWins"]
                losses = entry["MatchLosses"]
                draws = entry["MatchDraws"]
                nb_of_oppo = entry["OpponentCount"]

                standing = Standing(
                    player=player_name,
                    rank=player_position,
                    points=player_points,
                    omwp=omwp,
                    gwp=gwp,
                    ogwp=ogwp,
                    wins=wins,
                    losses=losses,
                    draws=draws,
                )

                # Récupérer les decklists du joueur
                player_decks = []
                for decklist in entry["Decklists"]:
                    deck_list_id = decklist["DecklistId"]
                    if not deck_list_id:
                        continue
                    decklist_format = decklist["Format"]
                    player_decks.append(
                        {
                            "deck_id": deck_list_id,
                            "uri": MtgMeleeConstants.format_url(
                                MtgMeleeConstants.DECK_PAGE, deckId=deck_list_id
                            ),
                            "format": decklist_format,
                        }
                    )

                result.append(
                    {
                        "username": user_name,
                        "player_name": player_name,
                        "result": f"{wins}-{losses}-{draws}",
                        "standing": standing,
                        "decks": player_decks if player_decks else [],
                        "nb_of_oppo": nb_of_oppo,
                    }
                )

            offset += 25
            if not has_data or (max_players is not None and offset >= max_players):
                break

        return result

    def get_deck(self, uri, players, skip_round_data=False):
        """Récupère les détails d'un deck"""
        deck_page_content = self.get_client().get(uri).text
        deck_soup = BeautifulSoup(deck_page_content, "html.parser")

        # Extraire le texte du decklist
        deck_text = deck_soup.select_one("pre#decklist-text")
        if not deck_text:
            return None

        card_list = deck_text.text.split("\r\n")

        # Extraire les informations du joueur
        player_link_element = deck_soup.select_one("a.text-nowrap.text-muted")
        if not player_link_element:
            return None

        player_url = player_link_element["href"]
        player_raw = player_link_element.select_one("span.text-nowrap").text.strip()
        player_name = self.get_player_name(player_raw, player_url, players)

        # Extraire la date
        date_element = deck_soup.select_one('span[data-toggle="date"]')
        if date_element:
            date_string = date_element["data-value"].strip()
            date_tournament = datetime.strptime(date_string, "%m/%d/%Y %I:%M:%S %p")
        else:
            date_tournament = datetime.now()

        # Extraire le format
        format_div = deck_soup.select_one(
            ".d-flex.flex-row.gap-8px .text-nowrap:last-of-type"
        )
        format_name = format_div.text.strip() if format_div else "Unknown"

        # Parser les cartes
        main_board = []
        side_board = []
        inside_sideboard = inside_companion = inside_commander = False

        for card in card_list:
            if card in ["MainDeck", "Companion", "Sideboard", "Commander", ""]:
                if card == "Commander":
                    inside_commander = True
                else:
                    inside_companion = card == "Companion"
                    inside_sideboard = card == "Sideboard"
                if inside_commander:
                    inside_sideboard = True
                if card == "Deck" and inside_commander:
                    inside_sideboard = False
                    inside_commander = False
                    inside_companion = False
            else:
                if inside_companion and not inside_commander:
                    continue
                try:
                    count, name = card.split(" ", 1)
                    count = int(count)
                    name = self.normalize_card_name(name)

                    if inside_sideboard:
                        side_board.append(DeckItem(card_name=name, count=count))
                    else:
                        main_board.append(DeckItem(card_name=name, count=count))
                except (ValueError, IndexError):
                    continue

        # Récupérer les rounds si nécessaire
        rounds = []
        if not skip_round_data:
            decklist_guid = uri.split("/")[-1]
            api_url = f"https://melee.gg/Decklist/GetTournamentViewData/{decklist_guid}"

            try:
                response = self.get_client().get(api_url)
                if response.status_code == 200:
                    match_data = response.json()
                    if "Json" in match_data and match_data["Json"]:
                        inner_data = json.loads(match_data["Json"])
                        # Parser les rounds depuis les données JSON
                        # TODO: Implémenter le parsing des rounds
                        pass
            except Exception:
                pass

        return {
            "date": date_tournament,
            "deck_uri": uri,
            "player": player_name,
            "format": format_name,
            "mainboard": main_board,
            "sideboard": side_board,
            "rounds": rounds,
        }

    def get_player_name(self, player_name_raw, profile_url, players):
        """Normalise le nom du joueur"""
        if not players:
            return self.normalize_spaces(player_name_raw) if player_name_raw else "-"

        player_id = profile_url.split("/")[-1] if profile_url else None
        if player_id:
            for player in players:
                if player.get("username") == player_id:
                    return player.get("player_name", player_name_raw)

        return self.normalize_spaces(player_name_raw) if player_name_raw else "-"

    @staticmethod
    def normalize_card_name(name):
        """Normalise le nom d'une carte"""
        # TODO: Implémenter la normalisation des noms de cartes
        return name.strip()

    def get_tournaments(self, start_date, end_date):
        """Récupère la liste des tournois via l'API"""
        offset = 0
        limit = -1
        result = []

        while True:
            # Utiliser le format JSON au lieu de URL-encoded
            params = {
                "draw": "1",
                "columns[0][data]": "ID",
                "columns[1][data]": "Name",
                "columns[2][data]": "StartDate",
                "columns[3][data]": "Status",
                "columns[4][data]": "Format",
                "columns[5][data]": "OrganizationName",
                "columns[6][data]": "Decklists",
                "order[0][column]": "2",
                "order[0][dir]": "desc",
                "start": str(offset),
                "length": "25",
                "search[value]": "",
                "search[regex]": "false",
                "q": "",
                "startDate": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
                "endDate": f"{end_date.strftime('%Y-%m-%d')}T23:59:59.999Z",
            }

            response = self.get_client().post(
                MtgMeleeConstants.TOURNAMENT_LIST_PAGE, data=params
            )
            tournament_data = json.loads(response.text)

            limit = tournament_data["recordsTotal"]
            for item in tournament_data["data"]:
                offset += 1
                tournament = {
                    "tournament_id": item["ID"],
                    "date": datetime.strptime(item["StartDate"], "%Y-%m-%dT%H:%M:%SZ"),
                    "name": self.normalize_spaces(item["Name"]),
                    "organizer": self.normalize_spaces(item["OrganizationName"]),
                    "formats": self.normalize_spaces(item["FormatDescription"]),
                    "uri": MtgMeleeConstants.format_url(
                        MtgMeleeConstants.TOURNAMENT_PAGE, tournamentId=item["ID"]
                    ),
                    "decklists": item["Decklists"],
                    "status": item["StatusDescription"],
                }
                result.append(tournament)

            if offset >= limit:
                break

        return result


class MtgMeleeTournamentList:
    """Liste des tournois Melee - reproduction fidèle de l'original"""

    @classmethod
    def DL_tournaments(
        cls, start_date: datetime, end_date: datetime = None
    ) -> List[Tournament]:
        """Récupère la liste des tournois Melee dans une période donnée"""
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        client = MtgMeleeClient()
        tournaments_data = client.get_tournaments(start_date, end_date)

        results = []
        for item in tournaments_data:
            # Filtrer les tournois selon les critères de l'original
            if item["status"] != "Ended":
                continue

            # Skip tournaments with blacklisted terms
            blacklisted_terms = ["Team "]
            if any(term.lower() in item["name"].lower() for term in blacklisted_terms):
                continue

            # Skip tournaments with weird formats
            valid_formats = [
                "Standard",
                "Modern",
                "Pioneer",
                "Legacy",
                "Vintage",
                "Pauper",
                "Commander",
                "Premodern",
            ]
            if item["formats"] not in valid_formats:
                continue

            # Skip tournaments not ended
            if (
                item["date"].replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
            ) < timedelta(days=5):
                continue

            results.append(
                Tournament(
                    name=item["name"],
                    date=item["date"].date(),
                    uri=item["uri"],
                    formats=item["formats"],
                    json_file=f"{item['name'].lower().replace(' ', '-')}-{item['tournament_id']}-{item['date'].strftime('%Y-%m-%d')}.json",
                )
            )

        return sorted(results, key=lambda t: t.date, reverse=True)

    def get_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """Récupère les détails complets d'un tournoi Melee"""
        client = MtgMeleeClient()
        players = client.get_players(tournament.uri)

        if not players:
            return None

        decks = []
        standings = []

        for player in players:
            standings.append(player["standing"])

            if player["decks"]:
                # Prendre le dernier deck du joueur
                deck_info = player["decks"][-1]
                deck = client.get_deck(deck_info["uri"], players)

                if deck:
                    decks.append(
                        Deck(
                            date=deck["date"],
                            player=deck["player"],
                            result=player["result"],
                            anchor_uri=deck["deck_uri"],
                            mainboard=deck["mainboard"],
                            sideboard=deck["sideboard"],
                        )
                    )

        return CacheItem(
            tournament=tournament,
            decks=decks,
            rounds=[],  # TODO: Implémenter les rounds
            standings=standings,
        )


class MtgMeleeScraper:
    """Scraper Melee authentique basé sur fbettega/mtg_decklist_scrapper"""

    def __init__(self, cache_folder: str):
        self.cache_folder = cache_folder
        self.tournament_list = MtgMeleeTournamentList()

    def fetch_tournaments(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tournament]:
        """Récupère la liste des tournois Melee dans une période donnée"""
        return self.tournament_list.DL_tournaments(start_date, end_date)

    def fetch_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """Récupère les détails complets d'un tournoi"""
        return self.tournament_list.get_tournament_details(tournament)

    def save_tournament(self, cache_item: CacheItem, target_folder: str):
        """Sauvegarde un tournoi au format JSON"""
        os.makedirs(target_folder, exist_ok=True)

        target_file = os.path.join(target_folder, cache_item.tournament.json_file)
        target_file = re.sub(r'[<>:"/\\|?*]', "", target_file)

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(cache_item.to_dict(), f, ensure_ascii=False, indent=2)

        return target_file
