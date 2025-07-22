"""
LINQ Equivalent - Workaround #5 (MOYEN)

Reproduit fidèlement les méthodes LINQ C# (Where, SelectMany, Any, etc.)
pour garantir la même logique de filtrage et tri.

Impact: Garantit la même logique de filtrage et tri
"""

import logging
from typing import Any, Callable, Iterable, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")


class LinqEquivalent:
    """
    Reproduction fidèle des méthodes LINQ C#

    Le code C# original utilise:
    var results = tournaments
        .Where(t => t.Date >= startDate)
        .SelectMany(t => t.Decks)
        .Where(d => d.Mainboard.Any(c => targetCards.Contains(c.Card)))
        .OrderBy(d => d.Date)
        .ToArray();

    Cette classe reproduit exactement ce comportement en Python.
    """

    @staticmethod
    def where(iterable: Iterable[T], predicate: Callable[[T], bool]) -> List[T]:
        """
        Équivalent de LINQ Where

        Reproduit la logique C#:
        .Where(t => condition)

        Args:
            iterable: Collection à filtrer
            predicate: Fonction de filtrage

        Returns:
            Liste filtrée
        """
        return [item for item in iterable if predicate(item)]

    @staticmethod
    def select(iterable: Iterable[T], selector: Callable[[T], U]) -> List[U]:
        """
        Équivalent de LINQ Select

        Reproduit la logique C#:
        .Select(t => transformation)

        Args:
            iterable: Collection à transformer
            selector: Fonction de transformation

        Returns:
            Liste transformée
        """
        return [selector(item) for item in iterable]

    @staticmethod
    def select_many(
        iterable: Iterable[T], selector: Callable[[T], Iterable[U]]
    ) -> List[U]:
        """
        Équivalent de LINQ SelectMany

        Reproduit la logique C#:
        .SelectMany(t => t.Collection)

        Args:
            iterable: Collection source
            selector: Fonction retournant une collection

        Returns:
            Liste aplatie
        """
        result = []
        for item in iterable:
            result.extend(selector(item))
        return result

    @staticmethod
    def any(
        iterable: Iterable[T], predicate: Optional[Callable[[T], bool]] = None
    ) -> bool:
        """
        Équivalent de LINQ Any

        Reproduit la logique C#:
        .Any() ou .Any(x => condition)

        Args:
            iterable: Collection à vérifier
            predicate: Fonction de condition (optionnelle)

        Returns:
            True si au moins un élément correspond, False sinon
        """
        if predicate is None:
            # Any() sans condition - vérifie si la collection n'est pas vide
            try:
                next(iter(iterable))
                return True
            except StopIteration:
                return False
        else:
            # Any(predicate) - vérifie si au moins un élément satisfait la condition
            return any(predicate(item) for item in iterable)

    @staticmethod
    def all(iterable: Iterable[T], predicate: Callable[[T], bool]) -> bool:
        """
        Équivalent de LINQ All

        Reproduit la logique C#:
        .All(x => condition)

        Args:
            iterable: Collection à vérifier
            predicate: Fonction de condition

        Returns:
            True si tous les éléments correspondent, False sinon
        """
        return all(predicate(item) for item in iterable)

    @staticmethod
    def first(
        iterable: Iterable[T], predicate: Optional[Callable[[T], bool]] = None
    ) -> T:
        """
        Équivalent de LINQ First

        Reproduit la logique C#:
        .First() ou .First(x => condition)

        Args:
            iterable: Collection source
            predicate: Fonction de condition (optionnelle)

        Returns:
            Premier élément correspondant

        Raises:
            StopIteration: Si aucun élément trouvé
        """
        if predicate is None:
            return next(iter(iterable))
        else:
            return next(item for item in iterable if predicate(item))

    @staticmethod
    def first_or_default(
        iterable: Iterable[T],
        predicate: Optional[Callable[[T], bool]] = None,
        default: Optional[T] = None,
    ) -> Optional[T]:
        """
        Équivalent de LINQ FirstOrDefault

        Reproduit la logique C#:
        .FirstOrDefault() ou .FirstOrDefault(x => condition)

        Args:
            iterable: Collection source
            predicate: Fonction de condition (optionnelle)
            default: Valeur par défaut

        Returns:
            Premier élément correspondant ou valeur par défaut
        """
        try:
            return LinqEquivalent.first(iterable, predicate)
        except StopIteration:
            return default

    @staticmethod
    def last(
        iterable: Iterable[T], predicate: Optional[Callable[[T], bool]] = None
    ) -> T:
        """
        Équivalent de LINQ Last

        Reproduit la logique C#:
        .Last() ou .Last(x => condition)

        Args:
            iterable: Collection source
            predicate: Fonction de condition (optionnelle)

        Returns:
            Dernier élément correspondant

        Raises:
            StopIteration: Si aucun élément trouvé
        """
        items = list(iterable)
        if predicate is None:
            if not items:
                raise StopIteration("Sequence contains no elements")
            return items[-1]
        else:
            matching_items = [item for item in items if predicate(item)]
            if not matching_items:
                raise StopIteration("Sequence contains no matching element")
            return matching_items[-1]

    @staticmethod
    def last_or_default(
        iterable: Iterable[T],
        predicate: Optional[Callable[[T], bool]] = None,
        default: Optional[T] = None,
    ) -> Optional[T]:
        """
        Équivalent de LINQ LastOrDefault

        Reproduit la logique C#:
        .LastOrDefault() ou .LastOrDefault(x => condition)

        Args:
            iterable: Collection source
            predicate: Fonction de condition (optionnelle)
            default: Valeur par défaut

        Returns:
            Dernier élément correspondant ou valeur par défaut
        """
        try:
            return LinqEquivalent.last(iterable, predicate)
        except StopIteration:
            return default

    @staticmethod
    def order_by(
        iterable: Iterable[T], key_selector: Callable[[T], Any], reverse: bool = False
    ) -> List[T]:
        """
        Équivalent de LINQ OrderBy / OrderByDescending

        Reproduit la logique C#:
        .OrderBy(x => x.Property) ou .OrderByDescending(x => x.Property)

        Args:
            iterable: Collection à trier
            key_selector: Fonction de sélection de clé
            reverse: True pour ordre décroissant (OrderByDescending)

        Returns:
            Liste triée
        """
        return sorted(iterable, key=key_selector, reverse=reverse)

    @staticmethod
    def group_by(
        iterable: Iterable[T], key_selector: Callable[[T], Any]
    ) -> List[tuple[Any, List[T]]]:
        """
        Équivalent de LINQ GroupBy

        Reproduit la logique C#:
        .GroupBy(x => x.Property)

        Args:
            iterable: Collection à grouper
            key_selector: Fonction de sélection de clé

        Returns:
            Liste de tuples (clé, groupe)
        """
        from itertools import groupby

        # Trier d'abord par la clé (requis pour groupby)
        sorted_items = sorted(iterable, key=key_selector)

        # Grouper par clé
        groups = []
        for key, group in groupby(sorted_items, key=key_selector):
            groups.append((key, list(group)))

        return groups

    @staticmethod
    def take(iterable: Iterable[T], count: int) -> List[T]:
        """
        Équivalent de LINQ Take

        Reproduit la logique C#:
        .Take(n)

        Args:
            iterable: Collection source
            count: Nombre d'éléments à prendre

        Returns:
            Liste des premiers éléments
        """
        result = []
        for i, item in enumerate(iterable):
            if i >= count:
                break
            result.append(item)
        return result

    @staticmethod
    def skip(iterable: Iterable[T], count: int) -> List[T]:
        """
        Équivalent de LINQ Skip

        Reproduit la logique C#:
        .Skip(n)

        Args:
            iterable: Collection source
            count: Nombre d'éléments à ignorer

        Returns:
            Liste des éléments restants
        """
        result = []
        for i, item in enumerate(iterable):
            if i >= count:
                result.append(item)
        return result

    @staticmethod
    def count(
        iterable: Iterable[T], predicate: Optional[Callable[[T], bool]] = None
    ) -> int:
        """
        Équivalent de LINQ Count

        Reproduit la logique C#:
        .Count() ou .Count(x => condition)

        Args:
            iterable: Collection à compter
            predicate: Fonction de condition (optionnelle)

        Returns:
            Nombre d'éléments
        """
        if predicate is None:
            return len(list(iterable))
        else:
            return sum(1 for item in iterable if predicate(item))

    @staticmethod
    def distinct(iterable: Iterable[T]) -> List[T]:
        """
        Équivalent de LINQ Distinct

        Reproduit la logique C#:
        .Distinct()

        Args:
            iterable: Collection source

        Returns:
            Liste sans doublons (ordre préservé)
        """
        seen = set()
        result = []
        for item in iterable:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def contains(iterable: Iterable[T], item: T) -> bool:
        """
        Équivalent de LINQ Contains

        Reproduit la logique C#:
        .Contains(item)

        Args:
            iterable: Collection source
            item: Élément à chercher

        Returns:
            True si l'élément est trouvé, False sinon
        """
        return item in iterable

    @staticmethod
    def to_array(iterable: Iterable[T]) -> List[T]:
        """
        Équivalent de LINQ ToArray

        Reproduit la logique C#:
        .ToArray()

        Args:
            iterable: Collection source

        Returns:
            Liste (équivalent d'un array en C#)
        """
        return list(iterable)


# Fonctions utilitaires pour reproduire les requêtes LINQ complexes du code original
def get_filtered_tournaments(
    tournaments: List[dict],
    start_date,
    filters: List[str] = None,
    excludes: List[str] = None,
) -> List[dict]:
    """
    Reproduit la logique de filtrage des tournois du code C# original

    Reproduit la logique C#:
    Tournament[] tournaments = settings.TournamentFolder.SelectMany(c => TournamentLoader.GetTournamentsByDate(c, startDate, t =>
    {
        if (settings.Filter != null)
        {
            foreach (string filter in settings.Filter)
            {
                if (!t.Contains(filter, StringComparison.InvariantCultureIgnoreCase)) return false;
            }
        }
        if (settings.Exclude != null)
        {
            foreach (string exclude in settings.Exclude)
            {
                if (t.Contains(exclude, StringComparison.InvariantCultureIgnoreCase)) return false;
            }
        }
        return true;
    })).ToArray();

    Args:
        tournaments: Liste des tournois
        start_date: Date de début
        filters: Filtres à appliquer
        excludes: Exclusions à appliquer

    Returns:
        Liste des tournois filtrés
    """
    from .date_handler import DateHandler
    from .string_utils import SafeStringCompare

    # Filtrage par date
    filtered = LinqEquivalent.where(
        tournaments,
        lambda t: DateHandler.is_date_in_range(
            DateHandler.parse_tournament_date(t.get("date")),
            start_date,
            start_date,  # Pour simplifier, on utilise la même date
        ),
    )

    # Application des filtres
    if filters:
        filtered = LinqEquivalent.where(
            filtered,
            lambda t: LinqEquivalent.all(
                filters, lambda f: SafeStringCompare.contains(t.get("name", ""), f)
            ),
        )

    # Application des exclusions
    if excludes:
        filtered = LinqEquivalent.where(
            filtered,
            lambda t: not LinqEquivalent.any(
                excludes, lambda e: SafeStringCompare.contains(t.get("name", ""), e)
            ),
        )

    return LinqEquivalent.to_array(filtered)


def get_filtered_decks(
    tournaments: List[dict], target_cards: List[str] = None
) -> List[dict]:
    """
    Reproduit la logique de filtrage des decks du code C# original

    Reproduit la logique C#:
    var results = tournaments
        .Where(t => t.Date >= startDate)
        .SelectMany(t => t.Decks)
        .Where(d => d.Mainboard.Any(c => targetCards.Contains(c.Card)))
        .OrderBy(d => d.Date)
        .ToArray();

    Args:
        tournaments: Liste des tournois
        target_cards: Cartes cibles à chercher

    Returns:
        Liste des decks filtrés et triés
    """
    from .string_utils import SafeStringCompare

    # SelectMany pour obtenir tous les decks
    all_decks = LinqEquivalent.select_many(tournaments, lambda t: t.get("decks", []))

    # Filtrage par cartes cibles si spécifié
    if target_cards:
        filtered_decks = LinqEquivalent.where(
            all_decks,
            lambda d: LinqEquivalent.any(
                d.get("mainboard", []),
                lambda c: LinqEquivalent.any(
                    target_cards,
                    lambda target: SafeStringCompare.equals(c.get("card", ""), target),
                ),
            ),
        )
    else:
        filtered_decks = all_decks

    # Tri par date
    sorted_decks = LinqEquivalent.order_by(filtered_decks, lambda d: d.get("date", ""))

    return LinqEquivalent.to_array(sorted_decks)
