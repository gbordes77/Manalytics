"""
JSON Mapper - Workaround #2 (CRITIQUE)

Reproduit fidèlement la sérialisation JSON de Newtonsoft.Json avec les attributs JsonProperty
pour assurer 100% de compatibilité avec les formats JSON originaux.

Impact: Assure 100% de compatibilité avec les formats JSON originaux
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class JsonMapper:
    """
    Reproduction fidèle du mapping JSON de Newtonsoft.Json

    Le code C# original utilise des attributs JsonProperty:
    [JsonProperty("CardName")]
    public string Card { get; set; }

    Cette classe reproduit exactement ce comportement en Python.
    """

    @staticmethod
    def map_deck_item(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping pour DeckItem (cartes individuelles)

        Reproduit la structure C#:
        public class DeckItem
        {
            [JsonProperty("Count")]
            public int Count { get; set; }
            [JsonProperty("CardName")]
            public string Card { get; set; }
        }

        Args:
            json_data: Données JSON brutes

        Returns:
            Dictionnaire avec mapping standardisé
        """
        return {
            "count": json_data.get("Count", json_data.get("Quantity", 0)),
            "card": json_data.get(
                "CardName", json_data.get("Card", json_data.get("Name", ""))
            ),
            "name": json_data.get(
                "Name", json_data.get("CardName", json_data.get("Card", ""))
            ),
        }

    @staticmethod
    def map_deck(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping pour Deck

        Reproduit la structure C#:
        public class Deck
        {
            [JsonProperty("Date")]
            public DateTime? Date { get; set; }
            [JsonProperty("Result")]
            public string Result { get; set; }
            [JsonProperty("Player")]
            public string Player { get; set; }
            [JsonProperty("AnchorUri")]
            public Uri AnchorUri { get; set; }
            [JsonProperty("Mainboard")]
            public DeckItem[] Mainboard { get; set; }
            [JsonProperty("Sideboard")]
            public DeckItem[] Sideboard { get; set; }
        }

        Args:
            json_data: Données JSON brutes

        Returns:
            Dictionnaire avec mapping standardisé
        """
        # Mapping des cartes du mainboard
        mainboard_raw = json_data.get("Mainboard", json_data.get("mainboard", []))
        mainboard = (
            [JsonMapper.map_deck_item(item) for item in mainboard_raw]
            if mainboard_raw
            else []
        )

        # Mapping des cartes du sideboard
        sideboard_raw = json_data.get("Sideboard", json_data.get("sideboard", []))
        sideboard = (
            [JsonMapper.map_deck_item(item) for item in sideboard_raw]
            if sideboard_raw
            else []
        )

        return {
            "date": json_data.get("Date", json_data.get("date")),
            "result": json_data.get("Result", json_data.get("result", "0-0")),
            "player": json_data.get("Player", json_data.get("player", "")),
            "anchor_uri": json_data.get(
                "AnchorUri", json_data.get("anchor_uri", json_data.get("deck_url", ""))
            ),
            "mainboard": mainboard,
            "sideboard": sideboard,
            # Champs additionnels pour compatibilité
            "wins": json_data.get("wins", 0),
            "losses": json_data.get("losses", 0),
            "draws": json_data.get("draws", 0),
            "placement": json_data.get("placement", 0),
        }

    @staticmethod
    def map_tournament_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping pour TournamentInfo

        Reproduit la structure C#:
        public class TournamentInfo
        {
            [JsonProperty("Date")]
            public DateTime Date { get; set; }
            [JsonProperty("Name")]
            public string Name { get; set; }
            [JsonProperty("Uri")]
            public Uri Uri { get; set; }
        }

        Args:
            json_data: Données JSON brutes

        Returns:
            Dictionnaire avec mapping standardisé
        """
        return {
            "date": json_data.get("Date", json_data.get("date", "")),
            "name": json_data.get("Name", json_data.get("name", "Unknown Tournament")),
            "uri": json_data.get(
                "Uri",
                json_data.get("uri", json_data.get("URL", json_data.get("id", ""))),
            ),
        }

    @staticmethod
    def map_tournament(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping pour Tournament (structure complète)

        Reproduit la structure C#:
        public class Tournament
        {
            public string File { get; set; }
            [JsonProperty("Tournament")]
            public TournamentInfo Information { get; set; }
            [JsonProperty("Decks")]
            public Deck[] Decks { get; set; }
            [JsonProperty("Standings")]
            public Standing[] Standings { get; set; }
            [JsonProperty("Rounds")]
            public Round[] Rounds{ get; set; }
            public string JsonFile { get; set; }
        }

        Args:
            json_data: Données JSON brutes

        Returns:
            Dictionnaire avec mapping standardisé
        """
        # Extraction des informations du tournoi
        tournament_info_raw = json_data.get("Tournament", json_data)
        tournament_info = JsonMapper.map_tournament_info(tournament_info_raw)

        # Mapping des decks
        decks_raw = json_data.get("Decks", json_data.get("decks", []))
        decks = [JsonMapper.map_deck(deck) for deck in decks_raw] if decks_raw else []

        return {
            "file": json_data.get("file", ""),
            "information": tournament_info,
            "decks": decks,
            "standings": json_data.get("Standings", json_data.get("standings", [])),
            "rounds": json_data.get("Rounds", json_data.get("rounds", [])),
            "json_file": json_data.get("json_file", ""),
            # Champs additionnels pour compatibilité
            "tournament_id": tournament_info.get("uri", ""),
            "tournament_name": tournament_info.get("name", ""),
            "tournament_date": tournament_info.get("date", ""),
            "format": json_data.get("format", "Unknown"),
        }

    @staticmethod
    def load_tournament_from_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Charge un tournoi depuis un fichier JSON avec mapping automatique

        Reproduit la logique C#:
        Tournament item = JsonConvert.DeserializeObject<Tournament>(File.ReadAllText(file));

        Args:
            file_path: Chemin vers le fichier JSON

        Returns:
            Dictionnaire du tournoi mappé ou None en cas d'erreur
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # Mapping automatique
            tournament = JsonMapper.map_tournament(raw_data)

            # Ajout du nom de fichier (comme en C#)
            tournament["file"] = Path(file_path).name
            tournament["json_file"] = Path(file_path).name

            # Reproduction de la logique C# : if (deck.Date == null) deck.Date = tournament.Information.Date;
            tournament_date = tournament["information"]["date"]
            for deck in tournament["decks"]:
                if not deck.get("date"):
                    deck["date"] = tournament_date

            return tournament

        except Exception as e:
            logger.error(f"Error loading tournament from {file_path}: {e}")
            return None

    @staticmethod
    def extract_card_names(decklist: List[Dict[str, Any]]) -> List[str]:
        """
        Extrait les noms de cartes d'une decklist avec mapping automatique

        Args:
            decklist: Liste des cartes (format variable)

        Returns:
            Liste des noms de cartes normalisés
        """
        card_names = []
        for card in decklist:
            # Mapping automatique des différents formats
            mapped_card = JsonMapper.map_deck_item(card)
            card_name = mapped_card.get("card", mapped_card.get("name", ""))
            if card_name:
                card_names.append(card_name)
        return card_names

    @staticmethod
    def normalize_tournament_data(
        tournaments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalise une liste de tournois avec mapping automatique

        Args:
            tournaments: Liste des tournois (formats variables)

        Returns:
            Liste des tournois normalisés
        """
        normalized = []
        for tournament in tournaments:
            try:
                mapped_tournament = JsonMapper.map_tournament(tournament)
                normalized.append(mapped_tournament)
            except Exception as e:
                logger.warning(f"Error mapping tournament: {e}")
                # Ajouter le tournoi original en cas d'erreur de mapping
                normalized.append(tournament)

        return normalized

    @staticmethod
    def create_output_record(
        deck_data: Dict[str, Any], tournament_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crée un enregistrement de sortie compatible avec le format C# original

        Reproduit la structure C# Record:
        new Record()
        {
            TournamentFile = Path.GetFileNameWithoutExtension(tournament.File),
            Tournament = tournament.Information.Name,
            Player = tournament.Decks[i].Player,
            AnchorUri = tournament.Decks[i].AnchorUri,
            Mainboard = includeDecklists ? tournament.Decks[i].Mainboard : null,
            Sideboard = includeDecklists ? tournament.Decks[i].Sideboard : null,
            // ...
        }

        Args:
            deck_data: Données du deck
            tournament_data: Données du tournoi

        Returns:
            Enregistrement formaté pour la sortie
        """
        tournament_info = tournament_data.get("information", {})

        return {
            "deck_id": f"{tournament_info.get('uri', 'unknown')}_{deck_data.get('player', 'unknown')}",
            "tournament_file": Path(tournament_data.get("file", "")).stem,
            "tournament_name": tournament_info.get("name", "Unknown"),
            "tournament_date": tournament_info.get("date", ""),
            "tournament_source": tournament_data.get("tournament_source", "Unknown"),
            "player_name": deck_data.get("player", ""),
            "result": deck_data.get("result", ""),
            "wins": deck_data.get("wins", 0),
            "losses": deck_data.get("losses", 0),
            "draws": deck_data.get("draws", 0),
            "deck_url": deck_data.get("anchor_uri", ""),
            "mainboard": deck_data.get("mainboard", []),
            "sideboard": deck_data.get("sideboard", []),
            "archetype": deck_data.get("archetype", "Unknown"),
            "archetype_with_colors": deck_data.get("archetype_with_colors", "Unknown"),
            "color_identity": deck_data.get("color_identity", ""),
            "guild_name": deck_data.get("guild_name", ""),
        }
