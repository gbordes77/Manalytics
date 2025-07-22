# -*- coding: utf-8 -*-
"""
MTGO Scraper Authentique - Reproduction fidèle de fbettega/mtg_decklist_scrapper
Récupère les vraies données depuis MTGO.com
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil.parser import isoparse

from .models.base_models import *


class MTGOSettings:
    LIST_URL = "https://www.mtgo.com/decklists/{year}/{month}"
    ROOT_URL = "https://www.mtgo.com"
    LEAGUE_REDOWNLOAD_DAYS = 3
    ValidFormats = [
        "Standard",
        "Modern",
        "Pioneer",
        "Legacy",
        "Vintage",
        "Pauper",
        "Commander",
    ]

    @staticmethod
    def format_url(url, **params):
        return url.format(**params)


class MTGOTournamentList:
    @staticmethod
    def increment_month(date: datetime) -> datetime:
        """Increment the month, rolling over to the next year if needed."""
        new_month = date.month + 1
        new_year = date.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        return date.replace(year=new_year, month=new_month, day=1)

    @staticmethod
    def DL_tournaments(
        start_date: datetime, end_date: datetime = None
    ) -> List[Tournament]:
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        results = []
        current_date = start_date

        while current_date <= end_date:
            tournament_list_url = MTGOSettings.LIST_URL.format(
                year=current_date.year, month=f"{current_date.month:02}"
            )

            response = requests.get(tournament_list_url)
            if response.status_code != 200:
                current_date = MTGOTournamentList.increment_month(current_date)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            tournament_nodes = soup.select("li.decklists-item")

            if not tournament_nodes:
                current_date = MTGOTournamentList.increment_month(current_date)
                continue

            for tournament_node in tournament_nodes:
                title = tournament_node.select_one("a > div > h3").text.strip()
                url = tournament_node.select_one("a")["href"]
                date_string = tournament_node.select_one("a > time")["datetime"]

                parsed_date = isoparse(date_string).date()
                url = urljoin(MTGOSettings.ROOT_URL, url)

                base_format_ite = title.split()[0]
                format_ite = (
                    "Commander" if base_format_ite == "Duel" else base_format_ite
                )

                results.append(
                    Tournament(
                        name=title,
                        date=parsed_date,
                        uri=url,
                        formats=format_ite
                        if format_ite in MTGOSettings.ValidFormats
                        else None,
                        json_file=os.path.splitext(os.path.basename(url))[0] + ".json",
                        force_redownload=(
                            "league" in title.lower()
                            and (datetime.now(timezone.utc).date() - parsed_date).days
                            < MTGOSettings.LEAGUE_REDOWNLOAD_DAYS
                        ),
                    )
                )

            current_date = MTGOTournamentList.increment_month(current_date)

        filtered_results = [
            t for t in results if start_date.date() <= t.date <= end_date.date()
        ]
        return sorted(filtered_results, key=lambda t: t.date, reverse=True)

    def get_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """
        Récupère les détails d'un tournoi en téléchargeant et analysant les données JSON intégrées dans la page HTML.
        """
        response = requests.get(tournament.uri)
        if response.status_code != 200:
            return None

        html_content = response.text
        html_rows = [line.strip() for line in html_content.splitlines()]

        # Trouver la ligne contenant les données JSON
        data_row = next(
            (
                line
                for line in html_rows
                if line.startswith("window.MTGO.decklists.data = ")
            ),
            None,
        )
        if not data_row:
            return None

        # Extraire la partie JSON
        json_data = data_row[
            29:-1
        ]  # Skip 29 caractères initiaux et retirer le dernier caractère
        event_json = json.loads(json_data)

        # Vérification des erreurs dans les données JSON
        if "errorCode" in event_json and event_json["errorCode"] == "SERVER_ERROR":
            return None

        # Déterminer le type d'événement
        event_type = "tournament" if "starttime" in event_json else "league"

        # Traiter les données pour un tournoi
        winloss = (
            MTGOTournamentLoader.parse_winloss(event_json)
            if event_type == "tournament"
            else None
        )
        standings = (
            MTGOTournamentLoader.parse_standing(event_json, winloss)
            if event_type == "tournament"
            else None
        )
        bracket = (
            MTGOTournamentLoader.parse_bracket(event_json)
            if event_type == "tournament"
            else None
        )

        # Parser les decks
        decks = MTGOTournamentLoader.parse_decks(
            tournament, event_type, winloss, event_json
        )

        # Réorganiser les decks si nécessaire
        if standings:
            decks = MTGOOrderNormalizer.reorder_decks(
                decks, standings, bracket, bracket is not None
            )

        return CacheItem(
            tournament=tournament, decks=decks, rounds=bracket, standings=standings
        )


class MTGOTournamentLoader:
    @staticmethod
    def parse_event_date(event_date_str):
        try:
            return datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(event_date_str, "%Y-%m-%d")

    @staticmethod
    def parse_winloss(event_json):
        """Parse les données de victoires/défaites pour chaque joueur à partir du JSON."""
        if "winloss" not in event_json:
            return None

        player_winloss = {}
        for winloss in event_json["winloss"]:
            player_id = winloss["loginid"]
            wins = winloss["wins"]
            losses = winloss["losses"]
            player_winloss[player_id] = f"{wins}-{losses}"

        return player_winloss if player_winloss else None

    @staticmethod
    def parse_decks(tournament, event_type, winloss, event_json):
        """Analyse les decks d'un tournoi à partir des données JSON."""
        event_date_str = (
            event_json.get("publish_date")
            if event_type == "league"
            else event_json.get("starttime")
        )
        event_date_naive = MTGOTournamentLoader.parse_event_date(event_date_str)
        event_date = event_date_naive.replace(tzinfo=timezone.utc)

        if "decklists" not in event_json:
            return None

        added_players = set()
        decks = []
        rank = 1

        for deck in event_json["decklists"]:
            mainboard = []
            sideboard = []
            player = deck.get("player")
            player_id = deck.get("loginid")

            if not player or player in added_players:
                continue

            added_players.add(player)

            # Parser le mainboard
            if "mainboard" in deck:
                for card in deck["mainboard"]:
                    mainboard.append(
                        DeckItem(
                            count=card.get("count", 1), card_name=card.get("name", "")
                        )
                    )

            # Parser le sideboard
            if "sideboard" in deck:
                for card in deck["sideboard"]:
                    sideboard.append(
                        DeckItem(
                            count=card.get("count", 1), card_name=card.get("name", "")
                        )
                    )

            # Déterminer le résultat
            result = "N/A"
            if winloss and player_id in winloss:
                result = winloss[player_id]
            elif "result" in deck:
                result = deck["result"]

            # Créer l'URI d'ancrage
            anchor_uri = f"{tournament.uri}#deck_{player}"

            decks.append(
                Deck(
                    date=event_date,
                    player=player,
                    result=result,
                    anchor_uri=anchor_uri,
                    mainboard=mainboard,
                    sideboard=sideboard,
                )
            )

        return decks

    @staticmethod
    def parse_standing(json_data, winloss):
        """Parse les standings du tournoi."""
        if "standings" not in json_data:
            return None

        standings = []
        for standing in json_data["standings"]:
            player = standing.get("player")
            rank = standing.get("rank")
            points = standing.get("points")
            wins = standing.get("wins")
            losses = standing.get("losses")
            draws = standing.get("draws")
            omwp = standing.get("omwp")
            gwp = standing.get("gwp")
            ogwp = standing.get("ogwp")

            standings.append(
                Standing(
                    rank=rank,
                    player=player,
                    points=points,
                    wins=wins,
                    losses=losses,
                    draws=draws,
                    omwp=omwp,
                    gwp=gwp,
                    ogwp=ogwp,
                )
            )

        return standings

    @staticmethod
    def parse_bracket(json_data):
        """Parse les données de bracket du tournoi."""
        if "bracket" not in json_data:
            return None

        rounds = []
        for round_data in json_data["bracket"]:
            round_name = round_data.get("round")
            matches = []

            for match in round_data.get("matches", []):
                player1 = match.get("player1")
                player2 = match.get("player2")
                result = match.get("result")
                match_id = match.get("id")

                if player1 and player2 and result:
                    matches.append(
                        RoundItem(
                            player1=player1, player2=player2, result=result, id=match_id
                        )
                    )

            if matches:
                rounds.append(Round(round_name, matches))

        return rounds


class MTGOOrderNormalizer:
    @staticmethod
    def reorder_decks(decks, standings, bracket, has_bracket):
        """Réorganise les decks selon les standings et bracket."""
        if not standings:
            return decks

        # Créer un mapping joueur -> rank
        player_rank = {standing.player: standing.rank for standing in standings}

        # Trier les decks par rank
        sorted_decks = []
        for standing in standings:
            player_deck = next(
                (deck for deck in decks if deck.player == standing.player), None
            )
            if player_deck:
                sorted_decks.append(player_deck)

        # Ajouter les decks sans standings à la fin
        for deck in decks:
            if deck.player not in player_rank:
                sorted_decks.append(deck)

        return sorted_decks


class MTGOScraper:
    """Scraper MTGO authentique basé sur fbettega/mtg_decklist_scrapper"""

    def __init__(self, cache_folder: str):
        self.cache_folder = cache_folder
        self.tournament_list = MTGOTournamentList()

    def fetch_tournaments(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tournament]:
        """Récupère la liste des tournois MTGO dans une période donnée"""
        return self.tournament_list.DL_tournaments(start_date, end_date)

    def fetch_tournament_details(self, tournament: Tournament) -> Optional[CacheItem]:
        """Récupère les détails complets d'un tournoi"""
        return self.tournament_list.get_tournament_details(tournament)

    def save_tournament(self, cache_item: CacheItem, target_folder: str):
        """Sauvegarde un tournoi au format JSON"""
        os.makedirs(target_folder, exist_ok=True)

        target_file = os.path.join(target_folder, cache_item.tournament.json_file)

        # Éviter les caractères invalides dans le nom de fichier
        target_file = re.sub(r'[<>:"/\\|?*]', "", target_file)

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(cache_item.to_dict(), f, ensure_ascii=False, indent=2)

        return target_file
