"""
Fbettega Clients - Reproduction de l'écosystème fbettega/mtg_decklist_scrapper
Modules pour scraper MTGO, Melee, TopDeck selon l'architecture Jilliac
"""

from .ManatraderClient import ManatraderClient
from .MtgMeleeClientV2 import MtgMeleeClientV2
from .MTGOclient import MTGOClient
from .TopDeckClient import TopDeckClient

__all__ = ["MTGOClient", "MtgMeleeClientV2", "TopDeckClient", "ManatraderClient"]
