"""
Precision Calculator - Workaround #7 (FAIBLE)

Reproduit fidèlement les calculs flottants C# avec précision contrôlée
pour éliminer les différences de précision numérique.

Impact: Élimine les différences de précision numérique
"""

import logging
from decimal import ROUND_HALF_UP, Decimal, getcontext
from typing import Union

logger = logging.getLogger(__name__)


class PrecisionCalculator:
    """
    Reproduction fidèle des calculs flottants C# avec précision contrôlée

    Le code C# original utilise:
    double similarity = ((double)max) / ((double)(mainboardCards.Length + sideboardCards.Length));

    Cette classe reproduit exactement ce comportement en Python avec la même précision.
    """

    def __init__(self):
        # Même précision que C# double (15-17 chiffres significatifs)
        getcontext().prec = 17
        getcontext().rounding = ROUND_HALF_UP

    @staticmethod
    def calculate_similarity(max_matches: int, total_cards: int) -> float:
        """
        Calcul de similarité avec précision contrôlée

        Reproduit la logique C#:
        double similarity = ((double)max) / ((double)(mainboardCards.Length + sideboardCards.Length));

        Args:
            max_matches: Nombre maximum de correspondances
            total_cards: Nombre total de cartes

        Returns:
            Similarité calculée avec précision C#
        """
        if total_cards == 0:
            return 0.0

        # Utilisation de Decimal pour éviter les erreurs d'arrondi
        max_decimal = Decimal(max_matches)
        total_decimal = Decimal(total_cards)

        # Division avec précision contrôlée
        similarity_decimal = max_decimal / total_decimal

        # Conversion en float avec précision C#
        return float(similarity_decimal)

    @staticmethod
    def calculate_percentage(
        numerator: Union[int, float], denominator: Union[int, float]
    ) -> float:
        """
        Calcul de pourcentage avec précision contrôlée

        Args:
            numerator: Numérateur
            denominator: Dénominateur

        Returns:
            Pourcentage calculé avec précision C#
        """
        if denominator == 0:
            return 0.0

        # Conversion en Decimal pour précision
        num_decimal = Decimal(str(numerator))
        den_decimal = Decimal(str(denominator))

        # Calcul du pourcentage
        percentage_decimal = (num_decimal / den_decimal) * Decimal("100")

        return float(percentage_decimal)

    @staticmethod
    def calculate_winrate(wins: int, losses: int) -> float:
        """
        Calcul du taux de victoire avec précision contrôlée

        Reproduit la logique C#:
        winrate = wins / max(1, wins + losses) if (wins + losses) > 0 else 0

        Args:
            wins: Nombre de victoires
            losses: Nombre de défaites

        Returns:
            Taux de victoire calculé avec précision C#
        """
        total_matches = wins + losses
        if total_matches == 0:
            return 0.0

        # Utilisation de Decimal pour précision
        wins_decimal = Decimal(wins)
        total_decimal = Decimal(total_matches)

        winrate_decimal = wins_decimal / total_decimal

        return float(winrate_decimal)

    @staticmethod
    def calculate_average(values: list[Union[int, float]]) -> float:
        """
        Calcul de moyenne avec précision contrôlée

        Args:
            values: Liste des valeurs

        Returns:
            Moyenne calculée avec précision C#
        """
        if not values:
            return 0.0

        # Conversion en Decimal
        decimal_values = [Decimal(str(v)) for v in values]

        # Calcul de la somme et moyenne
        sum_decimal = sum(decimal_values)
        count_decimal = Decimal(len(values))

        average_decimal = sum_decimal / count_decimal

        return float(average_decimal)

    @staticmethod
    def calculate_standard_deviation(values: list[Union[int, float]]) -> float:
        """
        Calcul d'écart-type avec précision contrôlée

        Args:
            values: Liste des valeurs

        Returns:
            Écart-type calculé avec précision C#
        """
        if len(values) < 2:
            return 0.0

        # Calcul de la moyenne
        mean = PrecisionCalculator.calculate_average(values)
        mean_decimal = Decimal(str(mean))

        # Calcul des écarts au carré
        squared_diffs = []
        for value in values:
            value_decimal = Decimal(str(value))
            diff = value_decimal - mean_decimal
            squared_diffs.append(diff * diff)

        # Variance
        variance_decimal = sum(squared_diffs) / Decimal(len(values) - 1)

        # Écart-type (racine carrée)
        std_dev_decimal = variance_decimal.sqrt()

        return float(std_dev_decimal)

    @staticmethod
    def round_to_precision(value: float, decimal_places: int) -> float:
        """
        Arrondi avec précision spécifiée (comme Math.Round en C#)

        Args:
            value: Valeur à arrondir
            decimal_places: Nombre de décimales

        Returns:
            Valeur arrondie
        """
        # Utilisation de Decimal pour arrondi précis
        value_decimal = Decimal(str(value))

        # Arrondi avec le nombre de décimales spécifié
        rounded_decimal = value_decimal.quantize(
            Decimal("0." + "0" * decimal_places), rounding=ROUND_HALF_UP
        )

        return float(rounded_decimal)

    @staticmethod
    def compare_floats(a: float, b: float, tolerance: float = 1e-10) -> bool:
        """
        Compare deux nombres flottants avec tolérance

        Args:
            a: Premier nombre
            b: Deuxième nombre
            tolerance: Tolérance pour la comparaison

        Returns:
            True si les nombres sont égaux dans la tolérance, False sinon
        """
        return abs(a - b) < tolerance

    @staticmethod
    def calculate_diversity_metrics(
        archetype_counts: dict[str, int]
    ) -> dict[str, float]:
        """
        Calcule les métriques de diversité avec précision contrôlée

        Reproduit les calculs de Shannon et Simpson avec précision C#

        Args:
            archetype_counts: Dictionnaire {archétype: nombre}

        Returns:
            Dictionnaire avec les métriques calculées
        """
        if not archetype_counts:
            return {
                "shannon_diversity": 0.0,
                "simpson_diversity": 0.0,
                "total_count": 0,
                "unique_archetypes": 0,
            }

        total_count = sum(archetype_counts.values())
        if total_count == 0:
            return {
                "shannon_diversity": 0.0,
                "simpson_diversity": 0.0,
                "total_count": 0,
                "unique_archetypes": len(archetype_counts),
            }

        # Calcul avec Decimal pour précision
        total_decimal = Decimal(total_count)
        shannon_sum = Decimal("0")
        simpson_sum = Decimal("0")

        for count in archetype_counts.values():
            if count > 0:
                count_decimal = Decimal(count)
                proportion = count_decimal / total_decimal

                # Shannon: -sum(p * ln(p))
                if proportion > 0:
                    shannon_sum += proportion * proportion.ln()

                # Simpson: sum(p^2)
                simpson_sum += proportion * proportion

        # Finalisation des calculs
        shannon_diversity = float(
            -shannon_sum
        )  # Négatif car on a calculé sum(p * ln(p))
        simpson_diversity = float(Decimal("1") - simpson_sum)  # 1 - sum(p^2)

        return {
            "shannon_diversity": shannon_diversity,
            "simpson_diversity": simpson_diversity,
            "total_count": total_count,
            "unique_archetypes": len(archetype_counts),
        }

    @staticmethod
    def calculate_meta_share(archetype_count: int, total_count: int) -> float:
        """
        Calcule la part de méta d'un archétype avec précision contrôlée

        Args:
            archetype_count: Nombre de decks de l'archétype
            total_count: Nombre total de decks

        Returns:
            Part de méta en pourcentage
        """
        return PrecisionCalculator.calculate_percentage(archetype_count, total_count)

    @staticmethod
    def calculate_confidence_interval(
        success_count: int, total_count: int, confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """
        Calcule l'intervalle de confiance avec précision contrôlée

        Args:
            success_count: Nombre de succès
            total_count: Nombre total d'essais
            confidence_level: Niveau de confiance (par défaut 95%)

        Returns:
            Tuple (borne_inférieure, borne_supérieure)
        """
        if total_count == 0:
            return (0.0, 0.0)

        # Proportion observée
        p = PrecisionCalculator.calculate_similarity(success_count, total_count)

        # Z-score pour le niveau de confiance (approximation)
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence_level, 1.96)

        # Calcul avec Decimal
        p_decimal = Decimal(str(p))
        z_decimal = Decimal(str(z))
        n_decimal = Decimal(total_count)

        # Erreur standard
        se_decimal = (p_decimal * (Decimal("1") - p_decimal) / n_decimal).sqrt()

        # Marge d'erreur
        margin_decimal = z_decimal * se_decimal

        # Intervalles
        lower_bound = float(p_decimal - margin_decimal)
        upper_bound = float(p_decimal + margin_decimal)

        # Borner entre 0 et 1
        lower_bound = max(0.0, lower_bound)
        upper_bound = min(1.0, upper_bound)

        return (lower_bound, upper_bound)
