"""
Générateur de graphiques de métagame avec heatmap interactive
Utilise les vraies données de tournois pour tous les graphiques
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats


class MetagameChartsGenerator:
    """Générateur de graphiques de métagame avec vraies données de tournois"""

    def __init__(self, data_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.data_path = data_path  # Optionnel maintenant

        # 🎯 ORDRE STANDARD DES ARCHÉTYPES (HIÉRARCHIQUE)
        # Basé sur l'expertise métagame et psychologie des couleurs gaming
        # ORDRE OBLIGATOIRE : Izzet Prowess en PREMIER
        self.standard_archetype_order = [
            # 🏆 ARCHÉTYPES PRIMAIRES (>10% métagame) - ORDRE FIXE
            "Izzet Prowess",  # 1. TOUJOURS EN PREMIER - Aggro dominant
            "Azorius Control",  # 2. Contrôle dominant
            "Mono Red Aggro",  # 3. Aggro pur
            "Jeskai Control",  # 4. Contrôle complexe
            # 🎯 ARCHÉTYPES SECONDAIRES (5-10% métagame)
            "Dimir Ramp",  # 5. Contrôle sombre
            "Jeskai Oculus",  # 6. Combo-contrôle
            "Azorius Omniscience",  # 7. Contrôle alternatif
            "Mono Black Demons",  # 8. Midrange sombre
            "Azorius Ramp",  # 9. Ramp contrôle
            "Mono Red Ramp",  # 10. Ramp aggro
            # 🔧 ARCHÉTYPES TERTIAIRES (<5% métagame)
            "Orzhov Selfbounce",  # 11. Combo-contrôle
            "Orzhov Demons",  # 12. Midrange sombre
            "Grixis Midrange",  # 13. Midrange complexe
            "Boros Aggro",  # 14. Aggro rapide
            "Selesnya Midrange",  # 15. Midrange équilibré
            "Simic Ramp",  # 16. Ramp-combo
            "Rakdos Aggro",  # 17. Aggro agressif
            "Gruul Aggro",  # 18. Aggro naturel
            "Golgari Midrange",  # 19. Midrange valeur
            "Temur Midrange",  # 20. Midrange tri-couleur
            # 📊 ARCHÉTYPES GÉNÉRIQUES (ordonnés par fréquence)
            "Four-Color Ramp",  # 21. Multi-couleur
            "Esper Control",  # 22. Contrôle tri-couleur
            "Bant Control",  # 23. Contrôle tri-couleur
            "Mardu Midrange",  # 24. Midrange tri-couleur
            "Abzan Midrange",  # 25. Midrange tri-couleur
            "Naya Aggro",  # 26. Aggro tri-couleur
            "Sultai Midrange",  # 27. Midrange tri-couleur
            "Jund Midrange",  # 28. Midrange tri-couleur
            "Five-Color",  # 29. Multi-couleur extrême
            "Colorless",  # 30. Artéfacts
            # ⚠️ CATÉGORIES FALLBACK (JAMAIS en première position)
            "Autres",  # 31. Toujours à la fin
            "Autres / Non classifiés",  # 32. Toujours à la fin
            "Non classifiés",  # 33. JAMAIS en première position
        ]

        # 🎨 PALETTE HEATMAP OPTIMISÉE - SYSTÈME EXPERT
        # Basée sur ColorBrewer RdYlBu pour accessibilité daltonisme
        self.heatmap_colors = {
            "c-50": "#D73027",  # Rouge intense - Très défavorable (0-35%)
            "c-40": "#F46D43",  # Orange-rouge - Défavorable (35-40%)
            "c-30": "#F46D43",  # Orange-rouge - Défavorable (35-40%)
            "c-20": "#FDAE61",  # Orange clair - Légèrement défavorable (40-45%)
            "c-10": "#FEE08B",  # Jaune clair - Presque équilibré (45-50%)
            "c0": "#FFFFBF",  # Jaune neutre - Équilibré (50%)
            "c+10": "#E0F3DB",  # Vert très clair - Légèrement favorable (50-55%)
            "c+20": "#A7D96A",  # Vert clair - Favorable (55-60%)
            "c+30": "#65BD63",  # Vert - Favorable (60-65%)
            "c+40": "#1A9641",  # Vert foncé - Très favorable (65-70%)
            "c+50": "#006837",  # Vert intense - Extrêmement favorable (70%+)
        }

        # Palette alternative pour matrices (échelle continue)
        self.matchup_scale_colors = [
            "#D73027",  # 0% - Rouge intense
            "#F46D43",  # 20% - Orange-rouge
            "#FDAE61",  # 40% - Orange clair
            "#FEE08B",  # 45% - Jaune clair
            "#FFFFBF",  # 50% - Jaune neutre
            "#E0F3DB",  # 55% - Vert très clair
            "#A7D96A",  # 60% - Vert clair
            "#65BD63",  # 70% - Vert
            "#1A9641",  # 80% - Vert foncé
            "#006837",  # 100% - Vert intense
        ]

        # 🎨 COULEURS OPTIMALES MANALYTICS - SYSTÈME EXPERT
        # Basé sur l'expertise data viz et psychologie des couleurs gaming

        # Système hiérarchique : Primary > Secondary > Tertiary
        self.manalytics_colors = {
            # 🏆 COULEURS PRIMAIRES (Archétypes dominants >10%)
            "Izzet Prowess": "#E74C3C",  # Rouge vif - Aggro dominant
            "Azorius Control": "#3498DB",  # Bleu profond - Contrôle dominant
            "Mono Red Aggro": "#C0392B",  # Rouge foncé - Aggro pur
            "Jeskai Control": "#9B59B6",  # Violet - Contrôle complexe
            # 🎯 COULEURS SECONDAIRES (Archétypes moyens 5-10%)
            "Dimir Ramp": "#2C3E50",  # Bleu-noir - Contrôle sombre
            "Jeskai Oculus": "#E67E22",  # Orange - Combo-contrôle
            "Azorius Omniscience": "#5DADE2",  # Bleu clair - Contrôle alternatif
            "Mono Black Demons": "#34495E",  # Noir - Midrange sombre
            "Azorius Ramp": "#AED6F1",  # Bleu très clair
            "Mono Red Ramp": "#F1948A",  # Rouge clair
            # 🔧 COULEURS TERTIAIRES (Archétypes mineurs <5%)
            "Orzhov Selfbounce": "#BDC3C7",  # Gris clair
            "Orzhov Demons": "#85929E",  # Gris moyen
            "Grixis Midrange": "#8E44AD",  # Violet foncé
            "Boros Aggro": "#F39C12",  # Orange doré
            "Selesnya Midrange": "#27AE60",  # Vert équilibré
            "Simic Ramp": "#16A085",  # Turquoise
            "Rakdos Aggro": "#E74C3C",  # Rouge-noir
            "Gruul Aggro": "#D35400",  # Rouge-vert
            "Golgari Midrange": "#7D6608",  # Noir-vert
            "Temur Midrange": "#C0392B",  # Tri-couleur équilibré
            # 🎯 COULEUR SPÉCIALE (JAMAIS la plus importante)
            "Autres": "#95A5A6",  # Gris neutre
            "Autres / Non classifiés": "#95A5A6",  # Gris neutre
            "Non classifiés": "#95A5A6",  # Gris neutre
        }

        # Ancienne palette MTG conservée pour compatibilité
        self.mtg_colors = {
            # Mono-couleurs
            "Mono White": "#FFF8DC",
            "Mono Blue": "#0E68AB",
            "Mono Black": "#2C2C2C",
            "Mono Red": "#D3202A",
            "Mono Green": "#00733E",
            # Guildes (2 couleurs)
            "Azorius": "#3498DB",  # Optimisé
            "Dimir": "#2C3E50",  # Optimisé
            "Rakdos": "#C0392B",  # Optimisé
            "Gruul": "#D35400",  # Optimisé
            "Selesnya": "#27AE60",  # Optimisé
            "Orzhov": "#85929E",  # Optimisé
            "Golgari": "#7D6608",  # Optimisé
            "Simic": "#16A085",  # Optimisé
            "Izzet": "#E74C3C",  # Optimisé
            "Boros": "#F39C12",  # Optimisé
            # Tri-couleurs
            "Esper": "#5DADE2",  # Optimisé
            "Jeskai": "#9B59B6",  # Optimisé
            "Bant": "#A3E4D7",  # Optimisé
            "Mardu": "#CD853F",  # Conservation
            "Abzan": "#F0E68C",  # Conservation
            "Naya": "#FFA500",  # Conservation
            "Grixis": "#8E44AD",  # Optimisé
            "Sultai": "#2E8B57",  # Conservation
            "Temur": "#C0392B",  # Optimisé
            "Jund": "#A0522D",  # Conservation
            # Multi-couleurs
            "Four-Color": "#9932CC",
            "Five-Color": "#FFD700",
            "Colorless": "#BDC3C7",
        }

        # Couleurs pour les archétypes (palette étendue de fallback)
        self.archetype_colors = [
            "#762a83",
            "#1b7837",
            "#d6604d",
            "#4393c3",
            "#f4a582",
            "#92c5de",
            "#d1e5f0",
            "#fddbc7",
            "#b2182b",
            "#2166ac",
            "#5aae61",
            "#9970ab",
            "#c2a5cf",
            "#a6dba0",
            "#008837",
            "#7b3294",
            "#c51b7d",
            "#de77ae",
            "#f1b6da",
            "#fde0ef",
            "#e6f5d0",
            "#b8e186",
            "#7fbc41",
            "#4d9221",
            "#276419",
            "#8c510a",
            "#bf812d",
            "#dfc27d",
            "#f6e8c3",
            "#f5f5f5",
        ]

    def get_archetype_color(self, archetype_name: str, guild_name: str = None) -> str:
        """🎨 SYSTÈME EXPERT - Obtient la couleur optimale d'un archétype

        Hiérarchie d'attribution des couleurs :
        1. Couleurs Manalytics optimales (archétypes spécifiques)
        2. Couleurs MTG (guildes et patterns)
        3. Couleurs fallback (basées sur l'index)
        """

        # 🏆 PRIORITÉ 1: Couleurs Manalytics optimales (correspondance exacte)
        if archetype_name in self.manalytics_colors:
            return self.manalytics_colors[archetype_name]

        # 🏆 PRIORITÉ 2: Correspondance partielle pour archétypes Manalytics
        archetype_lower = archetype_name.lower()
        for mana_archetype, color in self.manalytics_colors.items():
            if mana_archetype.lower() in archetype_lower:
                return color

        # 🎯 PRIORITÉ 3: Utiliser la guilde si disponible
        if guild_name and guild_name in self.mtg_colors:
            return self.mtg_colors[guild_name]

        # 🎯 PRIORITÉ 4: Extraire la guilde du nom d'archétype
        for guild, color in self.mtg_colors.items():
            if guild.lower() in archetype_lower:
                return color

        # 🎯 PRIORITÉ 5: Couleurs par mots-clés
        if any(word in archetype_lower for word in ["mono white", "white"]):
            return self.mtg_colors["Mono White"]
        elif any(word in archetype_lower for word in ["mono blue", "blue"]):
            return self.mtg_colors["Mono Blue"]
        elif any(word in archetype_lower for word in ["mono black", "black"]):
            return self.mtg_colors["Mono Black"]
        elif any(word in archetype_lower for word in ["mono red", "red"]):
            return self.mtg_colors["Mono Red"]
        elif any(word in archetype_lower for word in ["mono green", "green"]):
            return self.mtg_colors["Mono Green"]

        # 🔧 PRIORITÉ 6: Fallback - Couleur tertiaire basée sur l'index
        archetype_hash = hash(archetype_name) % len(self.archetype_colors)
        return self.archetype_colors[archetype_hash]

    def get_archetype_colors_for_chart(
        self, archetypes: List[str], guild_names: List[str] = None
    ) -> List[str]:
        """Génère une liste de couleurs pour les archétypes dans un graphique"""
        if guild_names is None:
            guild_names = [None] * len(archetypes)

        colors = []
        for i, archetype in enumerate(archetypes):
            guild = guild_names[i] if i < len(guild_names) else None
            colors.append(self.get_archetype_color(archetype, guild))

        return colors

    def _get_archetype_column(self, df: pd.DataFrame) -> str:
        """🎯 FONCTION CENTRALISÉE - Détermine la colonne d'archétype correcte

        RÈGLE ABSOLUE : Utiliser TOUJOURS la même logique que calculate_archetype_stats()
        pour garantir la cohérence des noms d'archétypes dans TOUS les graphiques

        Returns:
            "archetype_with_colors" si disponible (noms complets comme "Izzet Prowess")
            "archetype" sinon (noms simples comme "Prowess")
        """
        return (
            "archetype_with_colors"
            if "archetype_with_colors" in df.columns
            else "archetype"
        )

    def sort_archetypes_by_hierarchy(self, archetypes: List[str]) -> List[str]:
        """🎯 SYSTÈME EXPERT - Ordonne les archétypes selon la hiérarchie standardisée

        Ordre obligatoire : Izzet Prowess en PREMIER
        Puis hiérarchie Primary > Secondary > Tertiary

        Args:
            archetypes: Liste d'archétypes à ordonner

        Returns:
            Liste ordonnée selon standard_archetype_order
        """

        def get_archetype_priority(archetype: str) -> int:
            """Retourne la priorité d'un archétype selon l'ordre standard"""
            try:
                return self.standard_archetype_order.index(archetype)
            except ValueError:
                # Si archétype non trouvé, le placer avant les catégories fallback
                return len(self.standard_archetype_order) - 10

        # Trier selon la hiérarchie, avec Izzet Prowess toujours en premier
        sorted_archetypes = sorted(archetypes, key=get_archetype_priority)

        # Vérification : Izzet Prowess doit être en premier s'il existe
        if "Izzet Prowess" in sorted_archetypes:
            sorted_archetypes.remove("Izzet Prowess")
            sorted_archetypes.insert(0, "Izzet Prowess")

        return sorted_archetypes

    def limit_archetypes_to_max(
        self, archetypes: List[str], max_archetypes: int = 12
    ) -> List[str]:
        """🎯 LIMITATION INTELLIGENTE - Limite le nombre d'archétypes selon la hiérarchie

        Garde les archétypes les plus importants selon l'ordre hiérarchique
        Izzet Prowess reste TOUJOURS en premier s'il existe

        Args:
            archetypes: Liste d'archétypes à limiter
            max_archetypes: Nombre maximum d'archétypes à garder

        Returns:
            Liste limitée et ordonnée selon l'importance
        """
        # Ordonner selon la hiérarchie
        sorted_archetypes = self.sort_archetypes_by_hierarchy(archetypes)

        # Limiter au maximum demandé
        if len(sorted_archetypes) <= max_archetypes:
            return sorted_archetypes

        # Garder les plus importants selon l'ordre
        limited_archetypes = sorted_archetypes[:max_archetypes]

        # S'assurer qu'Izzet Prowess reste en premier
        if "Izzet Prowess" in archetypes and "Izzet Prowess" not in limited_archetypes:
            limited_archetypes[0] = "Izzet Prowess"

        return limited_archetypes

    def _get_guild_names_for_archetypes(self, archetype_names: List[str]) -> List[str]:
        """Helper function to get guild names for a list of archetypes"""
        guild_names = []

        # Obtenir les guildes depuis les données originales si disponibles
        if hasattr(self, "original_df") and "guild_name" in self.original_df.columns:
            for archetype in archetype_names:
                archetype_data = self.original_df[
                    self.original_df["archetype"] == archetype
                ]
                if not archetype_data.empty:
                    most_common_guild = archetype_data["guild_name"].mode()
                    guild_names.append(
                        most_common_guild.iloc[0]
                        if len(most_common_guild) > 0
                        else None
                    )
                else:
                    guild_names.append(None)
        else:
            guild_names = [None] * len(archetype_names)

        return guild_names

    def load_data(self) -> pd.DataFrame:
        """Charge les données de tournois réels (si un fichier est spécifié)"""
        if not self.data_path:
            raise ValueError("Aucun fichier de données spécifié")

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            self.logger.info(
                f"Données chargées: {len(df)} entrées de "
                f"{df['tournament_source'].nunique()} sources"
            )
            return df
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {e}")
            raise

    def _get_top_archetypes_consistent(
        self, df: pd.DataFrame, max_archetypes: int = 12
    ) -> pd.Series:
        """🎯 FONCTION CENTRALISÉE - Calcule les top archétypes de manière cohérente

        Cette fonction garantit que TOUS les graphiques utilisent exactement les mêmes données
        et le même ordre de tri pour éviter les incohérences.

        Args:
            df: DataFrame avec les données
            max_archetypes: Nombre maximum d'archétypes à retourner

        Returns:
            pd.Series avec les archétypes triés par pourcentage décroissant
        """
        # 🚨 FIX CRITIQUE: Vérifier si le DataFrame est vide avant traitement
        if df.empty:
            self.logger.warning("DataFrame vide passé à _get_top_archetypes_consistent")
            return pd.Series(dtype=float)

        # CORRECTION: Filtrer pour correspondre exactement à la liste de Jilliac
        # 🚨 FIX: Inclure les données League 5-0 au lieu de les exclure
        filtered_df = df[
            (
                df["tournament_source"].str.contains("Challenge", case=False)
                | df["tournament_source"].str.contains("melee.gg", case=False)
                | df["tournament_source"].str.contains("League 5-0", case=False)
            )
            & ~df["tournament_source"].str.contains("fbettega.gg", case=False)
            & ~df["tournament_source"].str.contains("Other Tournaments", case=False)
        ]

        # 🚨 FIX CRITIQUE: Vérifier si le DataFrame filtré est vide
        if filtered_df.empty:
            self.logger.warning(
                "Aucune donnée après filtrage dans _get_top_archetypes_consistent"
            )
            # Fallback: utiliser le DataFrame original si le filtrage est trop restrictif
            filtered_df = df
            if filtered_df.empty:
                return pd.Series(dtype=float)

        # 🎯 UTILISER LA FONCTION CENTRALISÉE pour garantir cohérence
        archetype_column = self._get_archetype_column(filtered_df)
        archetype_counts = filtered_df[archetype_column].value_counts()
        total_entries = len(filtered_df)

        # 🚨 FIX CRITIQUE: Vérifier si nous avons des données
        if total_entries == 0:
            self.logger.warning("Aucune entrée trouvée pour calculer les archétypes")
            return pd.Series(dtype=float)

        # Calculer les pourcentages
        archetype_shares = (archetype_counts / total_entries * 100).round(2)

        # RÈGLE ABSOLUE : Prendre SEULEMENT les max_archetypes les plus populaires
        top_archetypes = archetype_shares.head(max_archetypes)

        # RÈGLE ABSOLUE : "Autres" ne doit JAMAIS apparaître dans les graphiques
        if "Autres" in top_archetypes.index:
            top_archetypes = top_archetypes.drop("Autres")
        if "Autres / Non classifiés" in top_archetypes.index:
            top_archetypes = top_archetypes.drop("Autres / Non classifiés")

        # 🎯 ORDRE DÉCROISSANT avec Izzet Prowess TOUJOURS EN PREMIER
        # Trier par valeur décroissante
        top_archetypes = top_archetypes.sort_values(ascending=False)

        # Forcer Izzet Prowess en première position s'il existe
        if "Izzet Prowess" in top_archetypes.index:
            izzet_value = top_archetypes["Izzet Prowess"]
            top_archetypes = top_archetypes.drop("Izzet Prowess")
            # Créer nouvelle série avec Izzet Prowess en premier
            new_index = ["Izzet Prowess"] + top_archetypes.index.tolist()
            new_values = [izzet_value] + top_archetypes.values.tolist()
            top_archetypes = pd.Series(new_values, index=new_index)

        return top_archetypes

    def create_metagame_pie_chart(
        self, df: pd.DataFrame, min_threshold: float = 0.01
    ) -> go.Figure:
        """Crée le pie chart de part de métagame

        RÈGLES ABSOLUES:
        - JAMAIS afficher "Autres / Non classifiés"
        - MAXIMUM 12 segments dans le camembert
        - Prendre seulement les 12 archétypes les plus représentés
        """

        # 🎯 UTILISER LA FONCTION CENTRALISÉE pour garantir cohérence
        main_archetypes = self._get_top_archetypes_consistent(df, max_archetypes=12)

        # 🚨 FIX CRITIQUE: Vérifier si nous avons des données
        if main_archetypes.empty:
            self.logger.warning("Aucun archétype trouvé pour create_metagame_pie_chart")
            # Retourner un graphique vide avec message
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible pour cette période",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(size=16),
            )
            fig.update_layout(
                title="Répartition du Métagame - Aucune donnée", width=1000, height=700
            )
            return fig

        # Créer le pie chart
        fig = go.Figure()

        # Couleurs MTG pour chaque archétype
        archetype_names = main_archetypes.index.tolist()

        # CORRECTION: Filtrer pour correspondre exactement à la liste de Jilliac
        filtered_df = df[
            (
                df["tournament_source"].str.contains("Challenge", case=False)
                | df["tournament_source"].str.contains("melee.gg", case=False)
            )
            & ~df["tournament_source"].str.contains("League 5-0", case=False)
            & ~df["tournament_source"].str.contains("fbettega.gg", case=False)
            & ~df["tournament_source"].str.contains("Other Tournaments", case=False)
        ]

        # Obtenir les guildes pour chaque archétype depuis les données filtrées
        guild_names = []
        for archetype in archetype_names:
            # Trouver la guilde la plus commune pour cet archétype
            archetype_data = filtered_df[filtered_df["archetype"] == archetype]
            if not archetype_data.empty and "guild_name" in archetype_data.columns:
                most_common_guild = archetype_data["guild_name"].mode()
                guild_names.append(
                    most_common_guild.iloc[0] if len(most_common_guild) > 0 else None
                )
            else:
                guild_names.append(None)

        colors = self.get_archetype_colors_for_chart(archetype_names, guild_names)

        fig.add_trace(
            go.Pie(
                labels=main_archetypes.index,
                values=main_archetypes.values,
                hole=0,  # Pie chart complet (pas de donut)
                marker=dict(colors=colors, line=dict(color="white", width=2)),
                textinfo="label+percent",
                textposition="auto",
                textfont=dict(size=11, color="white", family="Arial, sans-serif"),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Part: %{percent}<br>"
                    "Joueurs: %{value:.0f}<br>"
                    "<extra></extra>"
                ),
                # Afficher le nom de l'archétype + pourcentage sur chaque segment
                texttemplate="<b>%{label}</b><br>%{percent}",
                showlegend=True,
            )
        )

        # Mise en page
        fig.update_layout(
            title={
                "text": "Standard Metagame Share (Top 12 Only)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            font=dict(family="Arial, sans-serif", size=12),
            width=1000,
            height=700,
            margin=dict(l=20, r=20, t=80, b=20),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=10),
            ),
        )

        return fig

    def calculate_archetype_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les statistiques par archétype avec intégration des couleurs"""
        # CORRECTION: Filtrer pour correspondre exactement à la liste de Jilliac
        filtered_df = df[
            (
                df["tournament_source"].str.contains("Challenge", case=False)
                | df["tournament_source"].str.contains("melee.gg", case=False)
            )
            & ~df["tournament_source"].str.contains("League 5-0", case=False)
            & ~df["tournament_source"].str.contains("fbettega.gg", case=False)
            & ~df["tournament_source"].str.contains("Other Tournaments", case=False)
        ]

        # Utiliser archetype_with_colors pour l'affichage avec les couleurs intégrées
        group_column = (
            "archetype_with_colors"
            if "archetype_with_colors" in filtered_df.columns
            else "archetype"
        )

        stats_df = (
            filtered_df.groupby(group_column)
            .agg(
                {
                    "winrate": ["mean", "std", "count"],
                    "wins": "sum",
                    "losses": "sum",
                    "matches_played": "sum",
                    "player_name": "nunique",
                }
            )
            .round(4)
        )

        # Aplatir les colonnes multi-niveaux
        stats_df.columns = [
            "winrate_mean",
            "winrate_std",
            "sample_size",
            "total_wins",
            "total_losses",
            "total_matches",
            "unique_players",
        ]
        stats_df = stats_df.reset_index()
        # Renommer la colonne pour maintenir la compatibilité
        stats_df.rename(columns={group_column: "archetype"}, inplace=True)

        # Calculer les intervalles de confiance
        stats_df["ci_lower"] = stats_df.apply(
            lambda row: self._calculate_confidence_interval(
                row["total_wins"], row["total_matches"]
            )[0],
            axis=1,
        )
        stats_df["ci_upper"] = stats_df.apply(
            lambda row: self._calculate_confidence_interval(
                row["total_wins"], row["total_matches"]
            )[1],
            axis=1,
        )

        # Calculer la part de métagame
        stats_df["metagame_share"] = (
            stats_df["unique_players"] / stats_df["unique_players"].sum()
        )

        # Calculer les tiers basés sur la borne inférieure de l'IC
        stats_df = stats_df.sort_values("ci_lower", ascending=False)
        stats_df["tier"] = pd.cut(
            stats_df["ci_lower"],
            bins=[0, 0.45, 0.50, 0.55, 1.0],
            labels=["Tier 4", "Tier 3", "Tier 2", "Tier 1"],
        )

        return stats_df

    def _calculate_confidence_interval(
        self, wins: int, total: int, confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calcule l'intervalle de confiance Wilson pour une proportion"""
        if total == 0:
            return 0.0, 1.0

        z = stats.norm.ppf((1 + confidence) / 2)
        p = wins / total
        n = total

        # Intervalle de confiance Wilson
        denominator = 1 + z**2 / n
        centre = (p + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator

        return max(0, centre - margin), min(1, centre + margin)

    def create_metagame_share_chart(
        self, stats_df: pd.DataFrame, threshold: float = 0.05
    ) -> go.Figure:
        """Crée le bar chart horizontal de part de métagame"""

        # Filtrer les archétypes au-dessus du seuil
        filtered_df = stats_df[stats_df["metagame_share"] >= threshold].copy()
        filtered_df = filtered_df.sort_values("metagame_share", ascending=True)

        # Obtenir les couleurs MTG pour chaque archétype
        archetype_names = filtered_df["archetype"].tolist()
        guild_names = self._get_guild_names_for_archetypes(archetype_names)
        colors = self.get_archetype_colors_for_chart(archetype_names, guild_names)

        # Créer le graphique
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=filtered_df["archetype"],
                x=filtered_df["metagame_share"] * 100,
                orientation="h",
                marker_color=colors,
                text=[f"{x:.1f}%" for x in filtered_df["metagame_share"] * 100],
                textposition="auto",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Metagame share: %{x:.1f}%<br>"
                    "Players: %{customdata[0]}<br>"
                    "Average winrate: %{customdata[1]:.1%}<br>"
                    "<extra></extra>"
                ),
                customdata=list(
                    zip(filtered_df["unique_players"], filtered_df["winrate_mean"])
                ),
            )
        )

        fig.update_layout(
            title={
                "text": f"Standard Archetypes Metagame Share "
                f"(threshold ≥{threshold:.0%})",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="Archetype",
            font=dict(family="Arial, sans-serif", size=12),
            width=1000,
            height=700,
            margin=dict(l=150, r=50, t=80, b=50),
        )

        return fig

    def create_winrate_confidence_chart(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le graphique à barres d'erreur avec intervalles de confiance"""

        # RÈGLE: Limiter à 12 archétypes maximum
        sorted_df = stats_df.sort_values("winrate_mean", ascending=False).head(12)

        # Obtenir les couleurs MTG pour chaque archétype
        archetype_names = sorted_df["archetype"].tolist()
        guild_names = self._get_guild_names_for_archetypes(archetype_names)
        colors = self.get_archetype_colors_for_chart(archetype_names, guild_names)

        fig = go.Figure()

        # Barres d'erreur
        fig.add_trace(
            go.Scatter(
                x=sorted_df["archetype"],
                y=sorted_df["winrate_mean"],
                error_y=dict(
                    type="data",
                    symmetric=False,
                    array=sorted_df["ci_upper"] - sorted_df["winrate_mean"],
                    arrayminus=sorted_df["winrate_mean"] - sorted_df["ci_lower"],
                    width=3,
                    thickness=2,
                ),
                mode="markers",
                marker=dict(
                    size=10,
                    color=colors,
                    line=dict(width=2, color="white"),
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Winrate: %{y:.1%}<br>"
                    "IC 95%: [%{customdata[0]:.1%}, %{customdata[1]:.1%}]<br>"
                    "Matchs: %{customdata[2]}<br>"
                    "<extra></extra>"
                ),
                customdata=list(
                    zip(
                        sorted_df["ci_lower"],
                        sorted_df["ci_upper"],
                        sorted_df["total_matches"],
                    )
                ),
            )
        )

        # Ligne de référence à 50%
        fig.add_hline(
            y=0.5, line_dash="dash", line_color="gray", annotation_text="50% (balance)"
        )

        fig.update_layout(
            title={
                "text": "Archetype Winrates with 95% Confidence Intervals (Top 12)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Archetype",
            yaxis_title="Winrate",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=700,
            margin=dict(l=50, r=50, t=80, b=80),
        )

        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        fig.update_xaxes(tickangle=45)

        return fig

    def create_tiers_scatter_plot(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le scatter plot des tiers basé sur les bornes inférieures des IC"""

        # RÈGLE: Limiter à 12 archétypes maximum
        filtered_df = stats_df.nlargest(12, "metagame_share")

        # Couleurs par tier
        tier_colors = {
            "Tier 1": self.heatmap_colors["c+50"],
            "Tier 2": self.heatmap_colors["c+20"],
            "Tier 3": self.heatmap_colors["c-10"],
            "Tier 4": self.heatmap_colors["c-30"],
        }

        fig = go.Figure()

        for tier in filtered_df["tier"].unique():
            tier_data = filtered_df[filtered_df["tier"] == tier]

            fig.add_trace(
                go.Scatter(
                    x=tier_data["metagame_share"] * 100,
                    y=tier_data["ci_lower"],
                    mode="markers+text",
                    marker=dict(
                        size=12,
                        color=tier_colors.get(tier, "gray"),
                        line=dict(width=2, color="white"),
                    ),
                    text=tier_data["archetype"],
                    textposition="top center",
                    name=tier,
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "Tier: " + str(tier) + "<br>"
                        "Lower CI bound: %{x:.3f}<br>"
                        "Metagame share: %{y:.1%}<br>"
                        "Players: %{customdata[0]}<br>"
                        "<extra></extra>"
                    ),
                    customdata=list(
                        zip(tier_data["unique_players"], tier_data["winrate_mean"])
                    ),
                )
            )

        # Lignes de référence pour les tiers
        fig.add_hline(
            y=0.55,
            line_dash="dash",
            line_color="green",
            annotation_text="Tier 1 (>55%)",
        )
        fig.add_hline(
            y=0.50,
            line_dash="dash",
            line_color="orange",
            annotation_text="Tier 2 (50-55%)",
        )
        fig.add_hline(
            y=0.45,
            line_dash="dash",
            line_color="red",
            annotation_text="Tier 3 (45-50%)",
        )

        fig.update_layout(
            title={
                "text": "Archetype Classification by Tiers (95% CI Lower Bound) - Top 12",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="95% CI Lower Bound",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=700,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.update_yaxes(tickformat=".0%", range=[0.3, 0.8])

        return fig

    def create_bubble_chart_winrate_presence(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le bubble chart winrate vs présence"""

        # RÈGLE: Limiter à 12 archétypes maximum
        filtered_df = stats_df.nlargest(12, "metagame_share")

        # Couleurs par tier
        tier_colors = {
            "Tier 1": self.heatmap_colors["c+50"],
            "Tier 2": self.heatmap_colors["c+20"],
            "Tier 3": self.heatmap_colors["c-10"],
            "Tier 4": self.heatmap_colors["c-30"],
        }

        fig = go.Figure()

        for tier in filtered_df["tier"].unique():
            tier_data = filtered_df[filtered_df["tier"] == tier]

            fig.add_trace(
                go.Scatter(
                    x=tier_data["metagame_share"] * 100,
                    y=tier_data["winrate_mean"],
                    mode="markers+text",
                    marker=dict(
                        size=tier_data["unique_players"]
                        * 2,  # Taille = nombre de joueurs
                        color=tier_colors.get(tier, "gray"),
                        line=dict(width=2, color="white"),
                        opacity=0.7,
                    ),
                    text=tier_data["archetype"],
                    textposition="middle center",
                    name=tier,
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "Tier: " + str(tier) + "<br>"
                        "Winrate: %{x:.1%}<br>"
                        "Metagame share: %{y:.1%}<br>"
                        "Players: %{marker.size}<br>"
                        "<extra></extra>"
                    ),
                    customdata=list(
                        zip(tier_data["unique_players"], tier_data["total_matches"])
                    ),
                )
            )

        # Reference line at 50%
        fig.add_hline(
            y=0.5, line_dash="dash", line_color="gray", annotation_text="50% (balance)"
        )

        fig.update_layout(
            title={
                "text": "Winrate vs Metagame Presence (size = number of players) - Top 12",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="Average winrate",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=700,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.update_yaxes(tickformat=".0%", range=[0.3, 0.8])

        return fig

    def create_top_5_0_chart(self, df: pd.DataFrame) -> go.Figure:
        """Crée le bar chart des archétypes ayant atteint 5-0"""

        # Filtrer les joueurs avec 5 victoires et 0 défaite
        perfect_players = df[(df["wins"] >= 5) & (df["losses"] == 0)]

        if len(perfect_players) == 0:
            # Si pas de 5-0, prendre les meilleurs scores
            best_players = df[df["winrate"] >= 0.8]
            title_suffix = "avec winrate ≥80%"
        else:
            best_players = perfect_players
            title_suffix = "ayant atteint 5-0"

        # Compter par archétype
        archetype_counts = best_players["archetype"].value_counts()

        # RÈGLE: Limiter à 12 archétypes maximum
        archetype_counts = archetype_counts.head(12)

        # Obtenir les couleurs MTG pour chaque archétype
        archetype_names = archetype_counts.index.tolist()
        guild_names = self._get_guild_names_for_archetypes(archetype_names)
        colors = self.get_archetype_colors_for_chart(archetype_names, guild_names)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=archetype_counts.index,
                y=archetype_counts.values,
                marker_color=colors,
                text=archetype_counts.values,
                textposition="auto",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Joueurs " + title_suffix + ": %{y}<br>"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            title={
                "text": f"Top archétypes {title_suffix} (Top 12)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Archétype",
            yaxis_title="Nombre de joueurs",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=700,
            margin=dict(l=50, r=50, t=80, b=80),
        )

        fig.update_xaxes(tickangle=45)

        return fig

    def create_data_sources_pie_chart(self, df: pd.DataFrame):
        """
        Crée un graphique en secteurs de la répartition des sources de données
        """
        # CORRECTION: Compter les sources de données (seulement Challenge et melee.gg)
        source_counts = df["tournament_source"].value_counts().to_dict()

        # CORRECTION: Filtrer pour correspondre exactement à la liste de Jilliac
        filtered_source_counts = {}
        for source, count in source_counts.items():
            if "Challenge" in source or "melee.gg" in source:
                filtered_source_counts[source] = count

        total_players = sum(filtered_source_counts.values())

        # Mapper les sources vers des noms d'affichage
        source_mapping = {
            "mtgdecks": "MTGDecks",
            "mtgo.com": "mtgo.com",
            "melee.gg": "Melee.gg",
            "topdeck.gg": "TopDeck.gg",
            "manatraders.com": "Manatraders",
        }

        # Préparer les données pour le graphique
        labels = []
        values = []
        colors = [
            "#FFD700",
            "#6495ED",
            "#9932CC",
            "#FF6347",
            "#32CD32",
            "#FF69B4",
            "#20B2AA",
            "#FFA500",
        ]

        for source, count in filtered_source_counts.items():
            display_name = source_mapping.get(source, source)
            labels.append(display_name)
            values.append(count)

        # Créer le graphique en secteurs
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker=dict(colors=colors[: len(labels)]),
                    textinfo="label+percent",
                    textposition="auto",
                    hovertemplate="<b>%{label}</b><br>"
                    + "Entrées: %{value}<br>"
                    + "Pourcentage: %{percent}<br>"
                    + "<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title={
                "text": "Data Sources Distribution",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20, "family": "Arial, sans-serif"},
            },
            font=dict(size=14),
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05
            ),
            margin=dict(l=20, r=120, t=60, b=20),
            width=1000,
            height=700,
        )

        return fig

    def create_archetype_evolution_chart(self, df: pd.DataFrame):
        """
        Crée un graphique d'évolution temporelle des archétypes Standard
        """
        import pandas as pd

        # CORRECTION: Filtrer pour correspondre exactement à la liste de Jilliac
        filtered_df = df[
            (
                df["tournament_source"].str.contains("Challenge", case=False)
                | df["tournament_source"].str.contains("melee.gg", case=False)
            )
            & ~df["tournament_source"].str.contains("League 5-0", case=False)
            & ~df["tournament_source"].str.contains("fbettega.gg", case=False)
            & ~df["tournament_source"].str.contains("Other Tournaments", case=False)
        ].copy()

        # Convertir les dates
        filtered_df["tournament_date"] = pd.to_datetime(filtered_df["tournament_date"])
        filtered_df["date"] = filtered_df["tournament_date"].dt.date

        # Grouper par date et archétype avec couleurs
        archetype_column = (
            "archetype_with_colors"
            if "archetype_with_colors" in filtered_df.columns
            else "archetype"
        )
        daily_counts = (
            filtered_df.groupby(["date", archetype_column])
            .size()
            .reset_index(name="count")
        )

        # Créer un pivot pour avoir les archétypes en colonnes
        pivot_data = daily_counts.pivot(
            index="date", columns=archetype_column, values="count"
        ).fillna(0)

        # Trier les archétypes par popularité totale
        archetype_totals = filtered_df[archetype_column].value_counts()
        top_archetypes = archetype_totals.head(
            5
        ).index.tolist()  # Limiter à 5 pour la lisibilité

        # Filtrer les données pour les top archétypes
        pivot_data = pivot_data[top_archetypes]

        # Palette de couleurs distinctes
        colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#98D8C8",
        ]

        # Créer le graphique
        fig = go.Figure()

        for i, archetype in enumerate(pivot_data.columns):
            fig.add_trace(
                go.Scatter(
                    x=pivot_data.index,
                    y=pivot_data[archetype],
                    mode="lines+markers",
                    name=archetype,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8, symbol="circle"),
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Date: %{x}<br>"
                    + "Nombre de decks: %{y}<br>"
                    + "<extra></extra>",
                )
            )

        # Mise en forme
        fig.update_layout(
            title={
                "text": "Temporal Evolution of Standard Archetypes",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20, "family": "Arial, sans-serif"},
            },
            xaxis_title="Date",
            yaxis_title="Nombre de decks",
            font=dict(size=14),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
            ),
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            margin=dict(l=60, r=20, t=80, b=60),
            width=1000,
            height=700,
            hovermode="x unified",
        )

        # Améliorer les axes
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
        )

        return fig

    def create_main_archetypes_bar_chart(self, df: pd.DataFrame):
        """
        Crée un graphique en barres des archétypes principaux avec les vraies données

        RÈGLES ABSOLUES:
        - JAMAIS afficher "Autres / Non classifiés"
        - MAXIMUM 12 segments
        - Prendre seulement les 12 archétypes les plus représentés
        """
        import pandas as pd

        # Utiliser le DataFrame directement
        df = df.copy()

        # 🎯 UTILISER LA FONCTION CENTRALISÉE pour garantir cohérence
        top_archetypes = self._get_top_archetypes_consistent(df, max_archetypes=12)

        # Préparer les données pour le graphique
        archetypes = list(top_archetypes.index)
        percentages = list(top_archetypes.values)

        # Couleurs MTG pour chaque archétype
        guild_names = []
        for archetype in archetypes:
            # 🎯 Trouver la guilde avec la colonne d'archétype correcte
            archetype_column = self._get_archetype_column(df)
            archetype_data = df[df[archetype_column] == archetype]
            if not archetype_data.empty and "guild_name" in archetype_data.columns:
                most_common_guild = archetype_data["guild_name"].mode()
                guild_names.append(
                    most_common_guild.iloc[0] if len(most_common_guild) > 0 else None
                )
            else:
                guild_names.append(None)

        colors = self.get_archetype_colors_for_chart(archetypes, guild_names)

        # Créer le graphique en barres
        fig = go.Figure(
            data=[
                go.Bar(
                    x=archetypes,
                    y=percentages,
                    marker=dict(
                        color=colors,
                        line=dict(color="white", width=1),
                    ),
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition="outside",
                    textfont=dict(size=12, color="black"),
                    hovertemplate="<b>%{x}</b><br>"
                    + "Metagame share: %{y:.1f}%<br>"
                    + f"Number of decks: {[int(p/100*len(df)) for p in percentages]}<br>"
                    + "<extra></extra>",
                )
            ]
        )

        # Mise en forme
        fig.update_layout(
            title={
                "text": f"Main STANDARD Archetypes - {len(df)} decks analyzed (Top 12 Only)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "family": "Arial, sans-serif", "color": "#2c3e50"},
            },
            xaxis_title="Archetype",
            yaxis_title="Metagame share (%)",
            font=dict(size=12, family="Arial, sans-serif"),
            showlegend=False,
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            margin=dict(l=60, r=20, t=80, b=120),
            width=1200,
            height=700,
        )

        # Améliorer les axes
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
            tickangle=45,
            tickfont=dict(size=11),
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
            range=[
                0,
                max(percentages) * 1.1 if percentages else 10,
            ],  # 🚨 FIX: Gérer liste vide
        )

        return fig

    def create_main_archetypes_bar_horizontal(self, df: pd.DataFrame):
        """
        Crée un graphique en barres horizontal des archétypes principaux (top 12)

        RÈGLES ABSOLUES:
        - JAMAIS afficher "Autres / Non classifiés"
        - MAXIMUM 12 segments
        - Prendre seulement les 12 archétypes les plus représentés
        """
        import pandas as pd

        # Utiliser le DataFrame directement
        df = df.copy()

        # 🎯 UTILISER LA FONCTION CENTRALISÉE pour garantir cohérence
        top_archetypes = self._get_top_archetypes_consistent(df, max_archetypes=12)

        # 🚨 FIX CRITIQUE: Vérifier si nous avons des données
        if top_archetypes.empty:
            self.logger.warning(
                "Aucun archétype trouvé pour create_main_archetypes_bar_horizontal"
            )
            # Retourner un graphique vide avec message
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible pour cette période",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(size=16),
            )
            fig.update_layout(
                title="Archétypes Principaux - Aucune donnée", width=1200, height=700
            )
            return fig

        archetypes = list(top_archetypes.index)
        percentages = list(top_archetypes.values)

        # Couleurs MTG pour chaque archétype
        guild_names = []
        for archetype in archetypes:
            # 🎯 Trouver la guilde avec la colonne d'archétype correcte
            archetype_column = self._get_archetype_column(df)
            archetype_data = df[df[archetype_column] == archetype]
            if not archetype_data.empty and "guild_name" in archetype_data.columns:
                most_common_guild = archetype_data["guild_name"].mode()
                guild_names.append(
                    most_common_guild.iloc[0] if len(most_common_guild) > 0 else None
                )
            else:
                guild_names.append(None)

        colors = self.get_archetype_colors_for_chart(archetypes, guild_names)
        fig = go.Figure(
            data=[
                go.Bar(
                    y=archetypes,
                    x=percentages,
                    orientation="h",
                    marker=dict(
                        color=colors,
                        line=dict(color="white", width=1),
                    ),
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition="outside",
                    textfont=dict(size=12, color="black"),
                    hovertemplate="<b>%{y}</b><br>Metagame share: %{x:.1f}%<br>Number of decks: "
                    + "<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title={
                "text": f"Main STANDARD Archetypes (Horizontal) - {len(df)} decks analyzed (Top 12 Only)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "family": "Arial, sans-serif", "color": "#2c3e50"},
            },
            yaxis_title="Archetype",
            xaxis_title="Metagame share (%)",
            font=dict(size=12, family="Arial, sans-serif"),
            showlegend=False,
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            margin=dict(l=120, r=20, t=80, b=60),
            width=1200,
            height=700,
        )
        fig.update_yaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
            tickfont=dict(size=11),
            autorange="reversed",
        )
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            showline=True,
            linewidth=1,
            linecolor="rgba(128,128,128,0.5)",
            range=[
                0,
                max(percentages) * 1.1 if percentages else 10,
            ],  # 🚨 FIX: Gérer liste vide
        )
        return fig

    def export_all_data(
        self,
        stats_df: pd.DataFrame,
        df: pd.DataFrame,
        output_dir: str = "analysis_output",
    ):
        """Exporte toutes les données en CSV et JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Export statistiques archétypes
        stats_csv = output_path / "archetype_stats.csv"
        stats_json = output_path / "archetype_stats.json"
        stats_df.to_csv(stats_csv, index=False, encoding="utf-8")
        stats_df.to_json(stats_json, orient="records", indent=2)

        # Export données top performers
        top_performers = df[df["winrate"] >= 0.8]
        top_csv = output_path / "top_performers.csv"
        top_json = output_path / "top_performers.json"
        top_performers.to_csv(top_csv, index=False, encoding="utf-8")
        top_performers.to_json(top_json, orient="records", indent=2)

        self.logger.info(
            f"Data exported: {stats_csv}, {stats_json}, {top_csv}, {top_json}"
        )

        return {
            "archetype_stats": {"csv": str(stats_csv), "json": str(stats_json)},
            "top_performers": {"csv": str(top_csv), "json": str(top_json)},
        }

    def generate_all_charts(
        self, df: pd.DataFrame, output_dir: str = "analysis_output"
    ) -> Dict:
        """Génère tous les graphiques de métagame"""

        # Stocker le DataFrame original pour accéder aux informations de guilde
        self.original_df = df.copy()

        # Calculer les statistiques
        stats_df = self.calculate_archetype_stats(df)

        # Créer tous les graphiques
        charts = {
            "metagame_pie": self.create_metagame_pie_chart(df),  # NOUVEAU !
            "metagame_share": self.create_metagame_share_chart(stats_df),
            "winrate_confidence": self.create_winrate_confidence_chart(stats_df),
            "tiers_scatter": self.create_tiers_scatter_plot(stats_df),
            "bubble_winrate_presence": self.create_bubble_chart_winrate_presence(
                stats_df
            ),
            "data_sources_pie": self.create_data_sources_pie_chart(df),  # CORRIGÉ !
            "archetype_evolution": self.create_archetype_evolution_chart(
                df
            ),  # CORRIGÉ !
            "main_archetypes_bar": self.create_main_archetypes_bar_chart(
                df
            ),  # CORRIGÉ !
            "main_archetypes_bar_horizontal": self.create_main_archetypes_bar_horizontal(
                df
            ),  # CORRIGÉ !
        }

        # Sauvegarder tous les graphiques
        output_path = Path(output_dir)
        files = {}

        for chart_name, fig in charts.items():
            html_file = output_path / f"{chart_name}.html"
            fig.write_html(str(html_file))
            files[chart_name] = str(html_file)

        # Exporter les données
        data_files = self.export_all_data(stats_df, df, output_dir)

        # Métadonnées
        metadata = {
            "generation_date": pd.Timestamp.now().isoformat(),
            "source_data": str(self.data_path),
            "total_tournaments": df["tournament_id"].nunique(),
            "total_players": len(df),
            "archetypes_count": df["archetype"].nunique(),
            "archetypes": sorted(df["archetype"].unique().tolist()),
            "charts_generated": list(charts.keys()),
        }

        return {
            "charts": charts,
            "stats_data": stats_df,
            "raw_data": df,
            "metadata": metadata,
            "files": files,
            "data_exports": data_files,
        }
