"""
Workarounds Techniques pour Migration C# → Python

Ce module contient tous les workarounds nécessaires pour reproduire fidèlement
le comportement du code C# original de MTGOArchetypeParser en Python.

Modules:
- string_utils: Comparaisons de chaînes compatibles C#
- json_mapper: Sérialisation JSON compatible Newtonsoft.Json
- date_handler: Gestion des dates nullable comme en C#
- archetype_color: Enum flags pour couleurs d'archétypes
- linq_equivalent: Équivalents des méthodes LINQ
- exception_handler: Gestion d'exceptions robuste
- precision_calculator: Calculs flottants avec précision contrôlée
"""

from .archetype_color import ArchetypeColor
from .date_handler import DateHandler
from .exception_handler import ArchetypeLoader
from .json_mapper import JsonMapper
from .linq_equivalent import LinqEquivalent
from .precision_calculator import PrecisionCalculator
from .string_utils import SafeStringCompare

__all__ = [
    "SafeStringCompare",
    "JsonMapper",
    "DateHandler",
    "ArchetypeColor",
    "LinqEquivalent",
    "ArchetypeLoader",
    "PrecisionCalculator",
]
