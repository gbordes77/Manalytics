# -*- coding: utf-8 -*-
"""
Copie directe du code de fbettega/mtg_decklist_scrapper/Client/MtgMeleeClient.py
Code original qui fonctionne déjà - pas de réinvention
"""
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser

# Import des modèles de fbettega
from .models.base_models import *


# Constantes Melee copiées depuis fbettega
class MtgMeleeConstants:
    # URL templates for various pages
    DECK_PAGE = "https://melee.gg/Decklist/View/{deckId}"
    PLAYER_DETAILS_PAGE = "https://melee.gg/Player/GetPlayerDetails?id={playerId}"
    TOURNAMENT_PAGE = "https://melee.gg/Tournament/View/{tournamentId}"
    TOURNAMENT_LIST_PAGE = "https://melee.gg/Decklist/TournamentSearch"
    ROUND_PAGE = "https://melee.gg/Standing/GetRoundStandings"
    # Parameters for the Tournament List page
    TOURNAMENT_LIST_PARAMETERS = "draw=1&columns%5B0%5D%5Bdata%5D=ID&columns%5B0%5D%5Bname%5D=ID&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=Name&columns%5B1%5D%5Bname%5D=Name&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=StartDate&columns%5B2%5D%5Bname%5D=StartDate&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=Status&columns%5B3%5D%5Bname%5D=Status&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=Format&columns%5B4%5D%5Bname%5D=Format&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=OrganizationName&columns%5B5%5D%5Bname%5D=OrganizationName&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=Decklists&columns%5B6%5D%5Bname%5D=Decklists&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=desc&start={offset}&length=25&search%5Bvalue%5D=&search%5Bregex%5D=false&q=&startDate={startDate}T00%3A00%3A00.000Z&endDate={endDate}T23%3A59%3A59.999Z"
    # Parameters for the Round Page
    ROUND_PAGE_PARAMETERS = "draw=1&columns%5B0%5D%5Bdata%5D=Rank&columns%5B0%5D%5Bname%5D=Rank&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=Player&columns%5B1%5D%5Bname%5D=Player&columns%5B1%5D%5Bsearchable%5D=false&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=Decklists&columns%5B2%5D%5Bname%5D=Decklists&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=MatchRecord&columns%5B3%5D%5Bname%5D=MatchRecord&columns%5B3%5D%5Bsearchable%5D=false&columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=GameRecord&columns%5B4%5D%5Bname%5D=GameRecord&columns%5B4%5D%5Bsearchable%5D=false&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=Points&columns%5B5%5D%5Bname%5D=Points&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=OpponentMatchWinPercentage&columns%5B6%5D%5Bname%5D=OpponentMatchWinPercentage&columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=TeamGameWinPercentage&columns%5B7%5D%5Bname%5D=TeamGameWinPercentage&columns%5B7%5D%5Bsearchable%5D=false&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=OpponentGameWinPercentage&columns%5B8%5D%5Bname%5D=OpponentGameWinPercentage&columns%5B8%5D%5Bsearchable%5D=false&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=FinalTiebreaker&columns%5B9%5D%5Bname%5D=FinalTiebreaker&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=OpponentCount&columns%5B10%5D%5Bname%5D=OpponentCount&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start={start}&length=25&search%5Bvalue%5D=&search%5Bregex%5D=false&roundId={roundId}"

    @staticmethod
    def format_url(url, **params):
        return url.format(**params)


# Classes modèles copiées depuis fbettega
class MtgMeleePlayerDeck:
    def __init__(self, deck_id, format, uri):
        self.deck_id = deck_id
        self.format = format
        self.uri = uri


class MtgMeleePlayerInfo:
    def __init__(self, username, player_name, result, standing, decks, nb_of_oppo):
        self.username = username
        self.player_name = player_name
        self.result = result
        self.standing = standing
        self.decks = decks
        self.nb_of_oppo = nb_of_oppo


class MtgMeleeDeckInfo:
    def __init__(
        self,
        date,
        deck_uri,
        player,
        format,
        mainboard,
        sideboard,
        rounds=None,
        result=None,
    ):
        self.date = date
        self.deck_uri = deck_uri
        self.player = player
        self.format = format
        self.mainboard = mainboard
        self.sideboard = sideboard
        self.rounds = rounds
        self.result = result

    def to_dict(self):
        return {
            "Date": self.date,
            "Player": self.player,
            "Result": self.result,
            "AnchorUri": self.deck_uri,
            "Mainboard": [item.to_dict() for item in self.mainboard],
            "Sideboard": [item.to_dict() for item in self.sideboard],
        }


class MtgMeleeRoundInfo:
    def __init__(self, round_name, match):
        self.round_name = round_name
        self.match = match


class MtgMeleeTournamentInfo:
    def __init__(
        self, tournament_id, date, name, organizer, formats, uri, decklists, statut
    ):
        self.tournament_id = tournament_id
        self.date = date
        self.name = name
        self.organizer = organizer
        self.formats = formats
        self.uri = uri
        self.decklists = decklists
        self.statut = statut


class MtgMeleeTournament:
    def __init__(
        self,
        uri,
        date,
        name,
        formats,
        json_file,
        deck_offset=None,
        expected_decks=None,
        fix_behavior=None,
        excluded_rounds=None,
    ):
        self.uri = uri
        self.date = date
        self.name = name
        self.formats = formats
        self.json_file = json_file
        self.deck_offset = deck_offset
        self.expected_decks = expected_decks
        self.fix_behavior = fix_behavior
        self.excluded_rounds = excluded_rounds

    def to_dict(self):
        return {
            "Date": self.date.isoformat() if self.date else None,
            "Name": self.name,
            "Uri": self.uri,
            "Formats": self.formats if self.formats else [],
        }


# Classe CardNameNormalizer simulée
class CardNameNormalizer:
    @staticmethod
    def initialize():
        pass

    @staticmethod
    def normalize(name):
        return name.strip()


# COPIE DIRECTE DU CODE DE FBETTEGA
class MtgMeleeClient:
    @staticmethod
    def get_client():
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
        return re.sub(r"\s+", " ", data).strip()

    def get_players(self, uri, max_players=None):
        result = []
        page_content = MtgMeleeClient.get_client().get(uri).text
        soup = BeautifulSoup(page_content, "html.parser")

        round_nodes = soup.select(
            'button.btn.btn-gray.round-selector[data-is-completed="True"]'
        )

        if not round_nodes:
            return None

        round_ids = [node["data-id"] for node in round_nodes]

        has_data = True
        offset = 0
        round_id = round_ids[-1]

        while True:
            has_data = False
            round_parameters = MtgMeleeConstants.ROUND_PAGE_PARAMETERS.replace(
                "{start}", str(offset)
            ).replace("{roundId}", round_id)
            round_url = MtgMeleeConstants.ROUND_PAGE
            response = MtgMeleeClient.get_client().post(
                round_url, data=round_parameters
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

                player_decks = []
                for decklist in entry["Decklists"]:
                    deck_list_id = decklist["DecklistId"]
                    if not deck_list_id:
                        continue
                    decklist_format = decklist["Format"]
                    player_decks.append(
                        MtgMeleePlayerDeck(
                            deck_id=deck_list_id,
                            format=decklist_format,
                            uri=MtgMeleeConstants.format_url(
                                MtgMeleeConstants.DECK_PAGE, deckId=deck_list_id
                            ),
                        )
                    )

                result.append(
                    MtgMeleePlayerInfo(
                        username=user_name,
                        player_name=player_name,
                        result=f"{wins}-{losses}-{draws}",
                        standing=standing,
                        decks=player_decks if player_decks else None,
                        nb_of_oppo=nb_of_oppo,
                    )
                )

            offset += 25
            if not has_data or (max_players is not None and offset >= max_players):
                break
        return result

    def get_deck(self, uri, players, skip_round_data=False):
        deck_page_content = self.get_client().get(uri).text
        deck_soup = BeautifulSoup(deck_page_content, "html.parser")

        deck_text = deck_soup.select_one("pre#decklist-text")
        card_list = deck_text.text.split("\r\n")

        player_link_element = deck_soup.select_one("a.text-nowrap.text-muted")

        player_url = player_link_element["href"]
        player_raw = player_link_element.select_one("span.text-nowrap").text.strip()

        player_name = self.get_player_name(player_raw, player_url, players)

        date_string = deck_soup.select_one('span[data-toggle="date"]')[
            "data-value"
        ].strip()
        date_tournament = datetime.strptime(date_string, "%m/%d/%Y %I:%M:%S %p")

        format_div = deck_soup.select_one(
            ".d-flex.flex-row.gap-8px .text-nowrap:last-of-type"
        )
        format = format_div.text.strip()

        main_board = []
        side_board = []
        inside_sideboard = inside_companion = inside_commander = False
        CardNameNormalizer.initialize()
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
                count, name = card.split(" ", 1)
                count = int(count)
                name = CardNameNormalizer.normalize(name)

                if inside_sideboard:
                    side_board.append(DeckItem(card_name=name, count=count))
                else:
                    main_board.append(DeckItem(card_name=name, count=count))
        rounds = []

        return MtgMeleeDeckInfo(
            date=None,
            deck_uri=uri,
            player=player_name,
            format=format,
            mainboard=main_board,
            sideboard=side_board,
            rounds=rounds if rounds else None,
        )

    def get_player_name(self, player_name_raw, profile_url, players):
        player_id = profile_url.split("/")[-1]
        if player_id:
            player_info = next((p for p in players if p.username == player_id), None)
            if player_info:
                return player_info.player_name
            elif player_name_raw:
                return self.normalize_spaces(player_name_raw)
        return "-"

    def get_tournaments(self, start_date, end_date):
        offset = 0
        limit = -1
        result = []

        while True:
            tournament_list_parameters = (
                MtgMeleeConstants.TOURNAMENT_LIST_PARAMETERS.replace(
                    "{offset}", str(offset)
                )
                .replace("{startDate}", start_date.strftime("%Y-%m-%d"))
                .replace("{endDate}", end_date.strftime("%Y-%m-%d"))
            )
            tournament_list_url = MtgMeleeConstants.TOURNAMENT_LIST_PAGE
            response = self.get_client().post(
                tournament_list_url, data=tournament_list_parameters
            )
            tournament_data = json.loads(response.text)

            limit = tournament_data["recordsTotal"]
            for item in tournament_data["data"]:
                offset += 1
                tournament = MtgMeleeTournamentInfo(
                    tournament_id=item["ID"],
                    date=datetime.strptime(item["StartDate"], "%Y-%m-%dT%H:%M:%SZ"),
                    name=self.normalize_spaces(item["Name"]),
                    organizer=self.normalize_spaces(item["OrganizationName"]),
                    formats=self.normalize_spaces(item["FormatDescription"]),
                    uri=MtgMeleeConstants.TOURNAMENT_PAGE.replace(
                        "{tournamentId}", str(item["ID"])
                    ),
                    decklists=item["Decklists"],
                    statut=item["StatusDescription"],
                )
                result.append(tournament)
            if offset >= limit:
                break
        return result


# Configuration settings copiées depuis fbettega
class MtgMeleeAnalyzerSettings:
    ValidFormats = [
        "Standard",
        "Modern",
        "Pioneer",
        "Legacy",
        "Vintage",
        "Pauper",
        "Commander",
        "Premodern",
    ]
    PlayersLoadedForAnalysis = 25
    DecksLoadedForAnalysis = 16
    BlacklistedTerms = ["Team "]


class MtgMeleeAnalyzer:
    def get_scraper_tournaments(
        self, tournament: MtgMeleeTournamentInfo
    ) -> Optional[List[MtgMeleeTournament]]:
        is_pro_tour = (
            tournament.organizer == "Wizards of the Coast"
            and (
                "Pro Tour" in tournament.name or "World Championship" in tournament.name
            )
            and "Qualifier" not in tournament.name
        )
        # Skips tournaments with blacklisted terms
        if any(
            term.lower() in tournament.name.lower()
            for term in MtgMeleeAnalyzerSettings.BlacklistedTerms
        ):
            return None

        # Skips tournaments with weird formats
        if (
            not is_pro_tour
            and tournament.formats not in MtgMeleeAnalyzerSettings.ValidFormats
        ):
            return None
        # skip not ended tournament 'In Progress'
        if tournament.statut != "Ended" and (
            tournament.date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
        ) < timedelta(days=5):
            return None

        client = MtgMeleeClient()
        players = client.get_players(
            tournament.uri, MtgMeleeAnalyzerSettings.PlayersLoadedForAnalysis
        )
        # Skips empty tournaments
        if not players:
            return None
        # Not commander multi tournament
        if tournament.formats == "Commander":
            for player in players:
                if player.nb_of_oppo > (
                    player.standing.wins
                    + player.standing.losses
                    + player.standing.draws
                ):
                    return None

        return [self.generate_single_format_tournament(tournament)]

    def generate_single_format_tournament(
        self, tournament: MtgMeleeTournamentInfo
    ) -> MtgMeleeTournament:
        format_detected = tournament.formats

        return MtgMeleeTournament(
            uri=tournament.uri,
            date=tournament.date,
            name=tournament.name,
            formats=format_detected,
            json_file=self.generate_file_name(tournament, format_detected, -1),
        )

    def generate_file_name(
        self, tournament: MtgMeleeTournamentInfo, format: str, offset: int
    ) -> str:
        name = tournament.name
        if format.lower() not in name.lower():
            name += f" ({format})"

        return f"{name.strip()}-{tournament.tournament_id}-{tournament.date.strftime('%Y-%m-%d')}.json"


class TournamentList:
    def get_tournament_details(self, tournament: MtgMeleeTournament) -> "CacheItem":
        client = MtgMeleeClient()
        players = client.get_players(tournament.uri)

        decks = []
        standings = []

        for player in players:
            standings.append(player.standing)
            player_position = player.standing.rank
            player_result = (
                f"{player_position}th Place"
                if player_position > 3
                else f"{player_position}st Place"
            )

            if player.decks and len(player.decks) > 0:
                deck_uri = player.decks[-1].uri
                deck = MtgMeleeClient().get_deck(deck_uri, players)
                if deck is not None:
                    decks.append(
                        MtgMeleeDeckInfo(
                            date=None,
                            deck_uri=deck.deck_uri,
                            player=player.player_name,
                            format=deck.format,
                            mainboard=deck.mainboard,
                            sideboard=deck.sideboard,
                            result=player_result,
                            rounds=deck.rounds,
                        )
                    )

        return CacheItem(
            tournament=tournament, decks=decks, standings=standings, rounds=[]
        )
