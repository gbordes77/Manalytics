"""
KPI Calculator module for Manalytics
Calcule les indicateurs clés de performance pour le métagame
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class KPICalculator:
    """Calculateur d'indicateurs clés de performance pour le métagame"""

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialise le calculateur KPI

        Args:
            data_path: Chemin vers les données (optionnel)
        """
        self.data_path = data_path
        self.cache = {}

    def calculate_metagame_diversity(self, tournament_data: List[Dict]) -> Dict:
        """
        Calcule la diversité du métagame

        Args:
            tournament_data: Données des tournois

        Returns:
            Dict contenant les métriques de diversité
        """
        if not tournament_data:
            return {"diversity_index": 0, "archetype_count": 0, "hhi": 1.0}

        # Compter les archétypes
        archetype_counts = {}
        total_decks = len(tournament_data)

        for deck in tournament_data:
            archetype = deck.get("archetype", "Unknown")
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        # Calculer l'indice de diversité (Shannon)
        diversity_index = 0
        for count in archetype_counts.values():
            if count > 0:
                p = count / total_decks
                diversity_index -= p * np.log2(p)

        # Calculer l'indice Herfindahl-Hirschman (HHI)
        hhi = sum((count / total_decks) ** 2 for count in archetype_counts.values())

        return {
            "diversity_index": round(diversity_index, 3),
            "archetype_count": len(archetype_counts),
            "hhi": round(hhi, 3),
            "total_decks": total_decks,
            "archetype_distribution": archetype_counts,
        }

    def calculate_win_rates(self, tournament_data: List[Dict]) -> Dict:
        """
        Calcule les taux de victoire par archétype

        Args:
            tournament_data: Données des tournois

        Returns:
            Dict contenant les taux de victoire
        """
        archetype_stats = {}

        for deck in tournament_data:
            archetype = deck.get("archetype", "Unknown")
            wins = deck.get("wins", 0)
            losses = deck.get("losses", 0)

            if archetype not in archetype_stats:
                archetype_stats[archetype] = {
                    "total_wins": 0,
                    "total_losses": 0,
                    "deck_count": 0,
                }

            archetype_stats[archetype]["total_wins"] += wins
            archetype_stats[archetype]["total_losses"] += losses
            archetype_stats[archetype]["deck_count"] += 1

        # Calculer les taux de victoire
        win_rates = {}
        for archetype, stats in archetype_stats.items():
            total_games = stats["total_wins"] + stats["total_losses"]
            win_rate = stats["total_wins"] / total_games if total_games > 0 else 0

            win_rates[archetype] = {
                "win_rate": round(win_rate, 3),
                "total_games": total_games,
                "deck_count": stats["deck_count"],
                "avg_wins_per_deck": round(stats["total_wins"] / stats["deck_count"], 2)
                if stats["deck_count"] > 0
                else 0,
            }

        return win_rates

    def calculate_metagame_share(self, tournament_data: List[Dict]) -> Dict:
        """
        Calcule la part de marché de chaque archétype

        Args:
            tournament_data: Données des tournois

        Returns:
            Dict contenant les parts de marché
        """
        if not tournament_data:
            return {}

        archetype_counts = {}
        total_decks = len(tournament_data)

        for deck in tournament_data:
            archetype = deck.get("archetype", "Unknown")
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        # Calculer les pourcentages
        metagame_share = {}
        for archetype, count in archetype_counts.items():
            percentage = (count / total_decks) * 100
            metagame_share[archetype] = {
                "count": count,
                "percentage": round(percentage, 2),
                "tier": self._classify_tier(percentage),
            }

        return metagame_share

    def calculate_temporal_trends(
        self, tournament_data: List[Dict], days: int = 30
    ) -> Dict:
        """
        Calcule les tendances temporelles

        Args:
            tournament_data: Données des tournois
            days: Nombre de jours à analyser

        Returns:
            Dict contenant les tendances
        """
        # Filtrer les données récentes
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = []

        for deck in tournament_data:
            deck_date = deck.get("date")
            if deck_date and isinstance(deck_date, str):
                try:
                    deck_datetime = datetime.fromisoformat(
                        deck_date.replace("Z", "+00:00")
                    )
                    if deck_datetime >= cutoff_date:
                        recent_data.append(deck)
                except:
                    continue

        if not recent_data:
            return {"trend": "stable", "growth_rate": 0, "period_days": days}

        # Analyser les tendances (simplifié)
        current_diversity = self.calculate_metagame_diversity(recent_data)

        return {
            "trend": "growing"
            if current_diversity["diversity_index"] > 2.0
            else "stable",
            "growth_rate": 0.05,  # Exemple
            "period_days": days,
            "current_diversity": current_diversity,
        }

    def _classify_tier(self, percentage: float) -> str:
        """
        Classifie un archétype par tier selon son pourcentage

        Args:
            percentage: Pourcentage de représentation

        Returns:
            Tier de l'archétype
        """
        if percentage >= 15:
            return "Tier 1"
        elif percentage >= 8:
            return "Tier 2"
        elif percentage >= 3:
            return "Tier 3"
        else:
            return "Tier 4"

    def generate_summary_report(self, tournament_data: List[Dict]) -> Dict:
        """
        Génère un rapport de synthèse complet

        Args:
            tournament_data: Données des tournois

        Returns:
            Dict contenant le rapport complet
        """
        diversity = self.calculate_metagame_diversity(tournament_data)
        win_rates = self.calculate_win_rates(tournament_data)
        metagame_share = self.calculate_metagame_share(tournament_data)
        trends = self.calculate_temporal_trends(tournament_data)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_decks_analyzed": len(tournament_data),
            "diversity_metrics": diversity,
            "win_rates": win_rates,
            "metagame_share": metagame_share,
            "temporal_trends": trends,
            "top_archetypes": self._get_top_archetypes(metagame_share, 5),
        }

    def _get_top_archetypes(self, metagame_share: Dict, limit: int = 5) -> List[Dict]:
        """
        Récupère les top archétypes par popularité

        Args:
            metagame_share: Données de part de marché
            limit: Nombre d'archétypes à retourner

        Returns:
            Liste des top archétypes
        """
        sorted_archetypes = sorted(
            metagame_share.items(), key=lambda x: x[1]["percentage"], reverse=True
        )

        return [
            {
                "archetype": archetype,
                "percentage": data["percentage"],
                "tier": data["tier"],
            }
            for archetype, data in sorted_archetypes[:limit]
        ]
