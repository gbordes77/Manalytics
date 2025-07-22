# -*- coding: utf-8 -*-
"""
Modèles de données de base pour le scraping MTG
Reproduction fidèle de fbettega/mtg_decklist_scrapper
"""

import decimal
from datetime import datetime
from typing import List, Optional


class Tournament:
    def __init__(
        self,
        date: Optional[datetime] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        formats: Optional[str] = None,
        json_file: Optional[str] = None,
        force_redownload: bool = False,
    ):
        self.date = date
        self.name = name
        self.uri = uri
        self.formats = formats
        self.json_file = json_file
        self.force_redownload = force_redownload

    def __str__(self):
        if self.date:
            return f"{self.name}|{self.date.strftime('%Y-%m-%d')}"
        else:
            return f"{self.name}|No date available"

    def __eq__(self, other):
        if not isinstance(other, Tournament):
            return False
        return (
            self.date == other.date
            and self.name == other.name
            and self.uri == other.uri
            and self.formats == other.formats
            and self.json_file == other.json_file
            and self.force_redownload == other.force_redownload
        )

    def to_dict(self):
        return {
            "Date": self.date.isoformat() if self.date else None,
            "Name": self.name,
            "Uri": self.uri,
            "Formats": self.formats,
        }


class Standing:
    def __init__(
        self,
        rank: Optional[int] = None,
        player: Optional[str] = None,
        points: Optional[int] = None,
        wins: Optional[int] = None,
        losses: Optional[int] = None,
        draws: Optional[int] = None,
        omwp: Optional[float] = None,
        gwp: Optional[float] = None,
        ogwp: Optional[float] = None,
    ):
        self.rank = rank
        self.player = player
        self.points = points
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.omwp = omwp
        self.gwp = gwp
        self.ogwp = ogwp

    def __str__(self):
        return (
            f"Standing(rank={self.rank}, player='{self.player}', points={self.points}, "
            f"wins={self.wins}, losses={self.losses}, draws={self.draws}, "
            f"omwp={'{:.7f}'.format(self.omwp) if self.omwp is not None else 'None'}, "
            f"gwp={'{:.5f}'.format(self.gwp) if self.gwp is not None else 'None'}, "
            f"ogwp={'{:.5f}'.format(self.ogwp) if self.ogwp is not None else 'None'})"
        )

    def get_significant_digits(self, value: float) -> int:
        if value is None:
            return 0
        d = decimal.Decimal(str(value))
        return max(d.as_tuple().exponent, -d.as_tuple().exponent)

    def __eq__(self, other):
        if not isinstance(other, Standing):
            return NotImplemented

        def float_equals(a, b):
            digits_a = self.get_significant_digits(a)
            digits_b = self.get_significant_digits(b)
            tolerance = 10 ** -min(digits_a, digits_b)
            return abs(a - b) <= tolerance

        return (
            self.rank == other.rank
            and self.player == other.player
            and self.points == other.points
            and self.wins == other.wins
            and self.losses == other.losses
            and self.draws == other.draws
            and float_equals(self.omwp, other.omwp)
            and float_equals(self.gwp, other.gwp)
            and float_equals(self.ogwp, other.ogwp)
        )

    def to_dict(self):
        return {
            "Rank": self.rank,
            "Player": self.player,
            "Points": self.points,
            "Wins": self.wins,
            "Losses": self.losses,
            "Draws": self.draws,
            "OMWP": self.omwp,
            "GWP": self.gwp,
            "OGWP": self.ogwp,
        }


class RoundItem:
    def __init__(
        self, player1: str, player2: str, result: str, id: Optional[str] = None
    ):
        self.player1 = player1
        self.player2 = player2
        self.result = result
        self.id = id
        try:
            scores = list(map(int, result.split("-")))
            if len(scores) == 2:
                p1_wins, p2_wins = scores
                draws = 0
            elif len(scores) == 3:
                p1_wins, p2_wins, draws = scores
            else:
                raise ValueError
        except ValueError:
            p1_wins, p2_wins, draws = 0, 0, 0
        self.scores = [
            (int(p1_wins > p2_wins), int(p1_wins < p2_wins)),
            (int(p2_wins > p1_wins), int(p2_wins < p1_wins)),
        ]
        self.numeric_score = [p1_wins, p2_wins, draws]

    def __eq__(self, other):
        return (
            self.player1 == other.player1
            and self.player2 == other.player2
            and self.result == other.result
        )

    def __str__(self):
        return f"player1 : {self.player1}, player2 : {self.player2}, result : {self.result}"

    def to_dict(self):
        return {"Player1": self.player1, "Player2": self.player2, "Result": self.result}

    def __hash__(self):
        return hash((self.player1, self.player2, self.result))

    def shallow_copy(self):
        return RoundItem(self.player1, self.player2, self.result)


class Round:
    def __init__(self, round_name: str, matches: List[RoundItem]):
        self.round_name = round_name
        self.matches = matches

    def __str__(self):
        return f"Round: {self.round_name}, {len(self.matches)} matches"

    def __eq__(self, other):
        if not isinstance(other, Round):
            return False
        return self.round_name == other.round_name and self.matches == other.matches

    def to_dict(self):
        return {
            "RoundName": self.round_name,
            "Matches": [match.to_dict() for match in self.matches],
        }

    def display_round(self):
        print(f"--- {self.round_name} ---")
        for match in self.matches:
            print(f"{match.player1} vs {match.player2} -> Résultat: {match.result}")
        print()


class DeckItem:
    def __init__(self, count: int, card_name: str):
        self.count = count
        self.card_name = card_name

    def __eq__(self, other):
        return self.count == other.count and self.card_name == other.card_name

    def to_dict(self):
        return {"Count": self.count, "CardName": self.card_name}


class Deck:
    def __init__(
        self,
        date: Optional[datetime],
        player: str,
        result: str,
        anchor_uri: str,
        mainboard: List[DeckItem],
        sideboard: List[DeckItem],
    ):
        self.date = date
        self.player = player
        self.result = result
        self.anchor_uri = anchor_uri
        self.mainboard = mainboard
        self.sideboard = sideboard

    def contains(self, *cards: str) -> bool:
        all_cards = [item.card_name for item in self.mainboard + self.sideboard]
        return all(card in all_cards for card in cards)

    def __str__(self):
        total_cards = sum(item.count for item in self.mainboard)
        return f"Deck({self.player}, {self.result}, {total_cards} cards)"

    def __eq__(self, other):
        if not isinstance(other, Deck):
            return False
        return (
            self.date == other.date
            and self.player == other.player
            and self.result == other.result
            and self.anchor_uri == other.anchor_uri
            and self.mainboard == other.mainboard
            and self.sideboard == other.sideboard
        )

    def to_dict(self):
        return {
            "Date": self.date.isoformat() if self.date else None,
            "Player": self.player,
            "Result": self.result,
            "AnchorUri": self.anchor_uri,
            "Mainboard": [item.to_dict() for item in self.mainboard],
            "Sideboard": [item.to_dict() for item in self.sideboard],
        }


class CacheItem:
    def __init__(
        self,
        tournament: Tournament,
        decks: List[Deck],
        rounds: List[Round],
        standings: List[Standing],
    ):
        self.tournament = tournament
        self.decks = decks
        self.rounds = rounds
        self.standings = standings

    def __str__(self):
        return f"CacheItem({self.tournament.name}, {len(self.decks)} decks)"

    def to_dict(self):
        return {
            "Tournament": self.tournament.to_dict(),
            "Decks": [deck.to_dict() for deck in self.decks],
            "Rounds": [round_obj.to_dict() for round_obj in self.rounds]
            if self.rounds
            else [],
            "Standings": [standing.to_dict() for standing in self.standings]
            if self.standings
            else [],
        }
