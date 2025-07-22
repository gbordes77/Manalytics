"""
Fbettega Clients - Reproduction de l'écosystème fbettega/mtg_decklist_scrapper
Modules pour scraper MTGO, Melee, TopDeck selon l'architecture Jilliac
"""

# Utiliser les nouveaux clients fonctionnels créés aujourd'hui
from .melee_client import MtgMeleeClient
from .mtgo_client import TournamentList, TournamentLoader


# Clients temporaires pour TopDeck et Manatraders (à implémenter plus tard)
class TopDeckClient:
    def __init__(self, cache_folder, config):
        self.cache_folder = cache_folder
        self.config = config

    async def get_tournaments(self, format_name, start_date, end_date):
        # TODO: Implémenter TopDeck scraping
        return []


class ManatraderClient:
    def __init__(self, cache_folder, config):
        self.cache_folder = cache_folder
        self.config = config

    async def get_tournaments(self, format_name, start_date, end_date):
        # TODO: Implémenter Manatraders scraping
        return []


__all__ = [
    "MtgMeleeClient",
    "TournamentList",
    "TournamentLoader",
    "TopDeckClient",
    "ManatraderClient",
]
