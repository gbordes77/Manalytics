"""
POLITIQUE STRICTE : AUCUNE DONNÉE MOCKÉE
Toutes les données DOIVENT provenir de sources réelles
"""

import json
import os
import re
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List


class NoMockDataError(Exception):
    """Erreur levée quand des données mockées sont détectées"""

    pass


class RealDataEnforcer:
    """Enforce l'utilisation exclusive de données réelles"""

    # Mots-clés interdits qui indiquent des données mockées
    FORBIDDEN_KEYWORDS = [
        "mock",
        "fake",
        "dummy",
        "test",
        "sample",
        "example",
        "lorem",
        "ipsum",
        "foo",
        "bar",
        "baz",
        "placeholder",
    ]

    # Mots-clés autorisés (cartes Magic légitimes)
    ALLOWED_KEYWORDS = [
        "mockingbird",
        "mockery",
        "mocking",  # Cartes Magic avec "mock"
        "test",
        "testing",
        "tester",  # Permis dans certains contextes
    ]

    # Patterns de données mockées typiques
    MOCK_PATTERNS = [
        r"test_\w+",
        r"Test\w+",
        r"example_\w+",
        r"Player\d+",  # Player1, Player2...
        r"Deck\d+",  # Deck1, Deck2...
        r"tournament_12345",  # IDs génériques
        r"Card\d+",  # Card1, Card2...
        r"Archetype\d+",  # Archetype1, Archetype2...
    ]

    @staticmethod
    def validate_no_mock_data(data: Any) -> None:
        """Valide qu'aucune donnée mockée n'est présente"""
        data_str = str(data).lower()

        # Vérifier mots-clés interdits (en excluant les autorisés)
        for keyword in RealDataEnforcer.FORBIDDEN_KEYWORDS:
            if keyword in data_str:
                # Vérifier si c'est un mot-clé autorisé
                is_allowed = False
                for allowed in RealDataEnforcer.ALLOWED_KEYWORDS:
                    if allowed in data_str:
                        is_allowed = True
                        break

                if not is_allowed:
                    raise NoMockDataError(
                        f"❌ DONNÉES MOCKÉES DÉTECTÉES! Mot-clé interdit: '{keyword}'\n"
                        f"📋 Règle: TOUTES les données doivent être RÉELLES (scraping/API)\n"
                        f"🔧 Action: Remplacer par des données réelles depuis MTGODecklistCache"
                    )

        # Vérifier patterns suspects
        for pattern in RealDataEnforcer.MOCK_PATTERNS:
            if re.search(pattern, str(data), re.IGNORECASE):
                raise NoMockDataError(
                    f"❌ PATTERN MOCKÉ DÉTECTÉ: {pattern}\n"
                    f"📋 Données suspectes: {str(data)[:100]}...\n"
                    f"🔧 Action: Utiliser de vraies données de tournois"
                )

    @staticmethod
    def require_real_data(func: Callable) -> Callable:
        """Décorateur qui force l'utilisation de données réelles"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Vérifier tous les arguments
            for arg in args:
                RealDataEnforcer.validate_no_mock_data(arg)
            for key, value in kwargs.items():
                RealDataEnforcer.validate_no_mock_data(value)

            # Exécuter la fonction
            result = func(*args, **kwargs)

            # Vérifier le résultat
            if result is not None:
                RealDataEnforcer.validate_no_mock_data(result)

            return result

        return wrapper

    @staticmethod
    def validate_tournament_data(tournament: Dict) -> bool:
        """Valide qu'un tournoi est réel et non mocké"""
        # Vérifier l'ID du tournoi
        if not tournament.get("id"):
            raise NoMockDataError("❌ Tournament sans ID réel")

        # Pattern d'ID réel MTGO/Melee
        mtgo_pattern = r"(modern|legacy|vintage|pioneer|standard)-(challenge|preliminary|showcase)-\d{4}-\d{2}-\d{2}"
        melee_pattern = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"

        tournament_id = str(tournament["id"])

        if not (
            re.match(mtgo_pattern, tournament_id, re.IGNORECASE)
            or re.match(melee_pattern, tournament_id)
        ):
            raise NoMockDataError(
                f"❌ ID de tournoi invalide: {tournament_id}\n"
                f"📋 Doit matcher un vrai pattern MTGO/Melee\n"
                f"🔧 Utiliser des données de MTGODecklistCache"
            )

        # Vérifier les decks
        decks = tournament.get("decks", [])
        if len(decks) < 8:
            raise NoMockDataError(
                f"❌ Tournoi avec {len(decks)} decks (minimum 8 pour être réaliste)"
            )

        # Valider chaque deck
        for deck in decks:
            RealDataEnforcer.validate_decklist(deck)

        return True

    @staticmethod
    def validate_decklist(deck: Dict) -> bool:
        """Valide qu'une decklist est réelle"""
        mainboard = deck.get("mainboard", [])

        # Vérifier taille réaliste
        total_cards = sum(card.get("count", 0) for card in mainboard)
        if total_cards < 60:
            raise NoMockDataError(
                f"❌ Deck avec {total_cards} cartes (minimum 60)\n"
                f"🔧 Utiliser des decklists réelles complètes"
            )

        # Vérifier noms de cartes réels (pas Card1, Card2...)
        for card in mainboard:
            card_name = card.get("name", "")
            if re.match(r"Card\d+", card_name):
                raise NoMockDataError(
                    f"❌ Nom de carte mocké détecté: {card_name}\n"
                    f"🔧 Utiliser de vrais noms de cartes Magic"
                )

            # Vérifier que le nom n'est pas générique
            if card_name.lower() in ["test card", "example card", "mock card"]:
                raise NoMockDataError(
                    f"❌ Nom de carte générique: {card_name}\n"
                    f"🔧 Utiliser de vraies cartes Magic"
                )

        return True


class Settings:
    """Configuration globale : données réelles uniquement"""

    # Mode strict activé par défaut
    ENFORCE_REAL_DATA = True
    NO_MOCK_DATA = True
    NO_TEST_DATA = True

    # Sources de données autorisées
    ALLOWED_DATA_SOURCES = [
        "https://www.mtgo.com/decklists",
        "https://melee.gg",
        "https://topdeck.gg",
        "https://api.scryfall.com",
        "./MTGODecklistCache/Tournaments/",  # Cache local de vrais tournois
        "./data/raw/",  # Données scrapées
    ]

    # Validation obligatoire
    VALIDATE_ALL_DATA = True
    MINIMUM_REAL_TOURNAMENTS = 10  # Au moins 10 vrais tournois
    MINIMUM_REAL_DECKS = 100  # Au moins 100 vrais decks

    # Chemins de données réelles
    REAL_DATA_PATHS = [
        Path("./MTGODecklistCache/Tournaments/"),
        Path("./data/raw/"),
        Path("./data/processed/"),
    ]

    @staticmethod
    def validate_environment():
        """Valide que l'environnement est configuré pour les données réelles"""
        # Vérifier variable d'environnement
        if not os.getenv("NO_MOCK_DATA"):
            raise RuntimeError(
                "❌ Variable d'environnement manquante!\n"
                "🔧 Exécuter: export NO_MOCK_DATA=true"
            )

        # Vérifier disponibilité des données réelles
        real_data_available = False
        for path in Settings.REAL_DATA_PATHS:
            if path.exists() and list(path.rglob("*.json")):
                real_data_available = True
                break

        if not real_data_available:
            raise RuntimeError(
                "❌ ERREUR: Aucune donnée réelle disponible!\n"
                "📋 Action requise:\n"
                "1. git clone https://github.com/Jiliac/MTGODecklistCache\n"
                "2. Ou lancer le scraper sur de vrais tournois\n"
                "3. Vérifier que ./data/ contient des fichiers JSON réels"
            )

        return True


def enforce_real_data_only():
    """Active le mode strict globalement"""

    # Configurer les variables d'environnement
    os.environ["REJECT_MOCK_DATA"] = "true"
    os.environ["REQUIRE_REAL_SOURCES"] = "true"
    os.environ["NO_MOCK_DATA"] = "true"

    # Valider l'environnement
    Settings.validate_environment()

    print("✅ MODE STRICT ACTIVÉ: Données réelles uniquement!")
    print("📋 Toute donnée mockée sera rejetée automatiquement")

    return True


def get_real_tournament_data() -> List[Dict]:
    """Récupère de vraies données de tournoi pour les tests"""
    real_tournaments = []

    # Chercher dans MTGODecklistCache
    cache_path = Path("./MTGODecklistCache/Tournaments/")
    if cache_path.exists():
        for json_file in cache_path.rglob("*.json"):
            try:
                with open(json_file) as f:
                    tournament = json.load(f)
                    # Valider que c'est bien réel
                    RealDataEnforcer.validate_tournament_data(tournament)
                    real_tournaments.append(tournament)
            except (json.JSONDecodeError, NoMockDataError):
                continue

    # Chercher dans data/raw/
    raw_path = Path("./data/raw/")
    if raw_path.exists():
        for json_file in raw_path.rglob("*.json"):
            try:
                with open(json_file) as f:
                    tournament = json.load(f)
                    RealDataEnforcer.validate_tournament_data(tournament)
                    real_tournaments.append(tournament)
            except (json.JSONDecodeError, NoMockDataError):
                continue

    if len(real_tournaments) < Settings.MINIMUM_REAL_TOURNAMENTS:
        raise RuntimeError(
            f"❌ Pas assez de tournois réels: {len(real_tournaments)}\n"
            f"📋 Minimum requis: {Settings.MINIMUM_REAL_TOURNAMENTS}\n"
            f"🔧 Scraper plus de données ou cloner MTGODecklistCache"
        )

    return real_tournaments


# Décorateur principal pour les fonctions
def real_data_only(func: Callable) -> Callable:
    """Décorateur principal qui garantit l'utilisation de données réelles"""
    return RealDataEnforcer.require_real_data(func)


# Validation au niveau module
if __name__ == "__main__":
    try:
        enforce_real_data_only()
        print("✅ Configuration NO MOCK DATA validée")
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        sys.exit(1)
