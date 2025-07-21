"""
Exception Handler - Workaround #6 (MOYEN)

Reproduit fidèlement la gestion d'exceptions robuste du code C#
pour assurer la même robustesse et les mêmes messages d'erreur que l'original.

Impact: Même robustesse et messages d'erreur que l'original
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArchetypeLoadingException(Exception):
    """Exception spécifique pour le chargement d'archétypes"""

    pass


class TournamentLoadingException(Exception):
    """Exception spécifique pour le chargement de tournois"""

    pass


class DataValidationException(Exception):
    """Exception spécifique pour la validation de données"""

    pass


class ArchetypeLoader:
    """
    Reproduction fidèle de la gestion d'exceptions C# pour le chargement d'archétypes

    Le code C# original utilise:
    try
    {
        var archetype = JsonConvert.DeserializeObject<ArchetypeSpecific>(File.ReadAllText(archetypeFile));
        if (archetype.Conditions == null || archetype.Conditions.Length == 0)
            throw new Exception($"Archetype file {Path.GetFileName(archetypeFile)} is invalid, no conditions declared");
    }
    catch(Exception ex)
    {
        throw new Exception($"Could not load archetype file {Path.GetFileName(archetypeFile)}: {ex.Message}");
    }

    Cette classe reproduit exactement ce comportement en Python.
    """

    @staticmethod
    def load_archetype_file(archetype_file: str) -> Dict[str, Any]:
        """
        Charge un fichier d'archétype avec gestion d'erreurs identique au C#

        Args:
            archetype_file: Chemin vers le fichier d'archétype

        Returns:
            Données de l'archétype

        Raises:
            ArchetypeLoadingException: Si le chargement échoue
        """
        file_name = Path(archetype_file).name

        try:
            # Lecture du fichier (équivalent de File.ReadAllText)
            with open(archetype_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Désérialisation JSON (équivalent de JsonConvert.DeserializeObject)
            try:
                archetype_data = json.loads(content)
            except json.JSONDecodeError as json_ex:
                raise ArchetypeLoadingException(
                    f"Could not parse archetype file {file_name}: Invalid JSON format - {str(json_ex)}"
                )

            # Validation identique au C# : if (archetype.Conditions == null || archetype.Conditions.Length == 0)
            conditions = archetype_data.get("Conditions")
            if conditions is None or len(conditions) == 0:
                raise ArchetypeLoadingException(
                    f"Archetype file {file_name} is invalid, no conditions declared"
                )

            # Validation supplémentaire du nom
            if not archetype_data.get("Name"):
                raise ArchetypeLoadingException(
                    f"Archetype file {file_name} is invalid, no name declared"
                )

            return archetype_data

        except FileNotFoundError:
            raise ArchetypeLoadingException(
                f"Could not load archetype file {file_name}: File not found"
            )
        except PermissionError:
            raise ArchetypeLoadingException(
                f"Could not load archetype file {file_name}: Permission denied"
            )
        except ArchetypeLoadingException:
            # Re-raise les exceptions spécifiques
            raise
        except Exception as ex:
            # Gestion générale (équivalent du catch(Exception ex) en C#)
            raise ArchetypeLoadingException(
                f"Could not load archetype file {file_name}: {str(ex)}"
            )

    @staticmethod
    def load_fallback_file(fallback_file: str) -> Dict[str, Any]:
        """
        Charge un fichier de fallback avec gestion d'erreurs identique au C#

        Reproduit la logique C#:
        var archetype = JsonConvert.DeserializeObject<ArchetypeGeneric>(File.ReadAllText(archetypeFile));
        if (archetype.CommonCards == null || archetype.CommonCards.Length == 0)
            throw new Exception($"Fallback file {Path.GetFileName(archetypeFile)} in invalid, no common cards declared");

        Args:
            fallback_file: Chemin vers le fichier de fallback

        Returns:
            Données du fallback

        Raises:
            ArchetypeLoadingException: Si le chargement échoue
        """
        file_name = Path(fallback_file).name

        try:
            with open(fallback_file, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                fallback_data = json.loads(content)
            except json.JSONDecodeError as json_ex:
                raise ArchetypeLoadingException(
                    f"Could not parse fallback file {file_name}: Invalid JSON format - {str(json_ex)}"
                )

            # Validation identique au C# : if (archetype.CommonCards == null || archetype.CommonCards.Length == 0)
            common_cards = fallback_data.get("CommonCards")
            if common_cards is None or len(common_cards) == 0:
                raise ArchetypeLoadingException(
                    f"Fallback file {file_name} is invalid, no common cards declared"
                )

            # Validation supplémentaire du nom
            if not fallback_data.get("Name"):
                raise ArchetypeLoadingException(
                    f"Fallback file {file_name} is invalid, no name declared"
                )

            return fallback_data

        except FileNotFoundError:
            raise ArchetypeLoadingException(
                f"Could not load fallback file {file_name}: File not found"
            )
        except PermissionError:
            raise ArchetypeLoadingException(
                f"Could not load fallback file {file_name}: Permission denied"
            )
        except ArchetypeLoadingException:
            raise
        except Exception as ex:
            raise ArchetypeLoadingException(
                f"Could not load fallback file {file_name}: {str(ex)}"
            )

    @staticmethod
    def load_format_directory(
        format_path: str,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Charge tous les archétypes et fallbacks d'un format avec gestion d'erreurs robuste

        Reproduit la logique C# de chargement de dossier complet avec gestion d'erreurs

        Args:
            format_path: Chemin vers le dossier du format

        Returns:
            Tuple (archétypes, fallbacks)

        Raises:
            ArchetypeLoadingException: Si le chargement échoue
        """
        if not Path(format_path).exists():
            raise ArchetypeLoadingException(
                f"Format directory not found: {format_path}"
            )

        archetypes = []
        fallbacks = []
        errors = []

        # Chargement des archétypes
        archetypes_path = Path(format_path) / "Archetypes"
        if archetypes_path.exists():
            for archetype_file in archetypes_path.glob("*.json"):
                try:
                    archetype_data = ArchetypeLoader.load_archetype_file(
                        str(archetype_file)
                    )
                    archetypes.append(archetype_data)
                except ArchetypeLoadingException as ex:
                    errors.append(str(ex))
                    logger.error(str(ex))

        # Chargement des fallbacks
        fallbacks_path = Path(format_path) / "Fallbacks"
        if fallbacks_path.exists():
            for fallback_file in fallbacks_path.glob("*.json"):
                try:
                    fallback_data = ArchetypeLoader.load_fallback_file(
                        str(fallback_file)
                    )
                    fallbacks.append(fallback_data)
                except ArchetypeLoadingException as ex:
                    errors.append(str(ex))
                    logger.error(str(ex))

        # Si aucun archétype ni fallback n'a pu être chargé, lever une exception
        if not archetypes and not fallbacks:
            if errors:
                raise ArchetypeLoadingException(
                    f"Could not load any archetype or fallback files from {format_path}. Errors: {'; '.join(errors)}"
                )
            else:
                raise ArchetypeLoadingException(
                    f"No archetype or fallback files found in {format_path}"
                )

        return archetypes, fallbacks


class TournamentLoader:
    """
    Reproduction fidèle de la gestion d'exceptions C# pour le chargement de tournois
    """

    @staticmethod
    def load_tournament_file(tournament_file: str) -> Dict[str, Any]:
        """
        Charge un fichier de tournoi avec gestion d'erreurs identique au C#

        Reproduit la logique C#:
        Tournament item = JsonConvert.DeserializeObject<Tournament>(File.ReadAllText(file));

        Args:
            tournament_file: Chemin vers le fichier de tournoi

        Returns:
            Données du tournoi

        Raises:
            TournamentLoadingException: Si le chargement échoue
        """
        file_name = Path(tournament_file).name

        try:
            with open(tournament_file, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tournament_data = json.loads(content)
            except json.JSONDecodeError as json_ex:
                raise TournamentLoadingException(
                    f"Could not parse tournament file {file_name}: Invalid JSON format - {str(json_ex)}"
                )

            # Validation de base
            if not isinstance(tournament_data, dict):
                raise TournamentLoadingException(
                    f"Tournament file {file_name} is invalid: Expected object, got {type(tournament_data).__name__}"
                )

            return tournament_data

        except FileNotFoundError:
            raise TournamentLoadingException(
                f"Could not load tournament file {file_name}: File not found"
            )
        except PermissionError:
            raise TournamentLoadingException(
                f"Could not load tournament file {file_name}: Permission denied"
            )
        except TournamentLoadingException:
            raise
        except Exception as ex:
            raise TournamentLoadingException(
                f"Could not load tournament file {file_name}: {str(ex)}"
            )

    @staticmethod
    def load_tournaments_from_directory(
        directory: str, file_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Charge tous les tournois d'un dossier avec gestion d'erreurs robuste

        Args:
            directory: Dossier contenant les fichiers de tournois
            file_filter: Filtre pour les noms de fichiers (optionnel)

        Returns:
            Liste des tournois chargés
        """
        if not Path(directory).exists():
            logger.warning(f"Tournament directory not found: {directory}")
            return []

        tournaments = []
        errors = []

        pattern = file_filter if file_filter else "*.json"

        for tournament_file in Path(directory).glob(pattern):
            try:
                tournament_data = TournamentLoader.load_tournament_file(
                    str(tournament_file)
                )
                tournaments.append(tournament_data)
            except TournamentLoadingException as ex:
                errors.append(str(ex))
                logger.warning(str(ex))

        if errors:
            logger.info(
                f"Loaded {len(tournaments)} tournaments with {len(errors)} errors from {directory}"
            )
        else:
            logger.info(f"Loaded {len(tournaments)} tournaments from {directory}")

        return tournaments


class DataValidator:
    """
    Validation de données avec gestion d'erreurs robuste
    """

    @staticmethod
    def validate_deck_data(deck_data: Dict[str, Any], context: str = "") -> None:
        """
        Valide les données d'un deck

        Args:
            deck_data: Données du deck à valider
            context: Contexte pour les messages d'erreur

        Raises:
            DataValidationException: Si la validation échoue
        """
        context_str = f" in {context}" if context else ""

        if not isinstance(deck_data, dict):
            raise DataValidationException(
                f"Invalid deck data{context_str}: Expected dict, got {type(deck_data).__name__}"
            )

        # Validation des champs requis
        required_fields = ["player", "mainboard"]
        for field in required_fields:
            if field not in deck_data:
                raise DataValidationException(
                    f"Missing required field '{field}' in deck data{context_str}"
                )

        # Validation du mainboard
        mainboard = deck_data.get("mainboard", [])
        if not isinstance(mainboard, list):
            raise DataValidationException(
                f"Invalid mainboard{context_str}: Expected list, got {type(mainboard).__name__}"
            )

        # Validation du sideboard (optionnel)
        sideboard = deck_data.get("sideboard", [])
        if sideboard is not None and not isinstance(sideboard, list):
            raise DataValidationException(
                f"Invalid sideboard{context_str}: Expected list, got {type(sideboard).__name__}"
            )

    @staticmethod
    def validate_tournament_data(
        tournament_data: Dict[str, Any], context: str = ""
    ) -> None:
        """
        Valide les données d'un tournoi

        Args:
            tournament_data: Données du tournoi à valider
            context: Contexte pour les messages d'erreur

        Raises:
            DataValidationException: Si la validation échoue
        """
        context_str = f" in {context}" if context else ""

        if not isinstance(tournament_data, dict):
            raise DataValidationException(
                f"Invalid tournament data{context_str}: Expected dict, got {type(tournament_data).__name__}"
            )

        # Validation des decks
        decks = tournament_data.get("decks", [])
        if not isinstance(decks, list):
            raise DataValidationException(
                f"Invalid decks{context_str}: Expected list, got {type(decks).__name__}"
            )

        # Validation de chaque deck
        for i, deck in enumerate(decks):
            try:
                DataValidator.validate_deck_data(deck, f"deck {i}{context_str}")
            except DataValidationException as ex:
                raise DataValidationException(
                    f"Invalid deck data at index {i}{context_str}: {str(ex)}"
                )


# Fonctions utilitaires pour compatibilité
def safe_load_archetype(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Charge un archétype de manière sécurisée (retourne None en cas d'erreur)

    Args:
        file_path: Chemin vers le fichier

    Returns:
        Données de l'archétype ou None
    """
    try:
        return ArchetypeLoader.load_archetype_file(file_path)
    except ArchetypeLoadingException as ex:
        logger.error(str(ex))
        return None


def safe_load_tournament(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Charge un tournoi de manière sécurisée (retourne None en cas d'erreur)

    Args:
        file_path: Chemin vers le fichier

    Returns:
        Données du tournoi ou None
    """
    try:
        return TournamentLoader.load_tournament_file(file_path)
    except TournamentLoadingException as ex:
        logger.error(str(ex))
        return None
