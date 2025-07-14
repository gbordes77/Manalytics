"""
Générateur de graphiques de métagame avec heatmap interactive
Utilise les vraies données de tournois pour tous les graphiques
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats


class MetagameChartsGenerator:
    """Générateur de graphiques de métagame avec vraies données de tournois"""

    def __init__(self, data_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.data_path = data_path  # Optionnel maintenant

        # Palette heatmap (du violet au vert)
        self.heatmap_colors = {
            "c-50": "#762a83",  # Extrême perdant
            "c-40": "#8e4d99",
            "c-30": "#a66fb0",
            "c-20": "#be91c7",
            "c-10": "#d6b3de",
            "c0": "#f7f7f7",  # Neutre (50%)
            "c+10": "#c7e9c0",
            "c+20": "#a1d99b",
            "c+30": "#7bc87c",
            "c+40": "#4eb265",
            "c+50": "#1b7837",  # Extrême gagnant
        }

        # Couleurs MTG pour les guildes et archétypes
        self.mtg_colors = {
            # Mono-couleurs
            "Mono White": "#fffbd5",
            "Mono Blue": "#0e68ab",
            "Mono Black": "#150b00",
            "Mono Red": "#d3202a",
            "Mono Green": "#00733e",
            # Guildes (2 couleurs)
            "Azorius": "#a4c2f4",  # Blanc-Bleu
            "Dimir": "#4a5568",  # Bleu-Noir
            "Rakdos": "#8b0000",  # Noir-Rouge
            "Gruul": "#8b4513",  # Rouge-Vert
            "Selesnya": "#90ee90",  # Vert-Blanc
            "Orzhov": "#dda0dd",  # Blanc-Noir
            "Golgari": "#556b2f",  # Noir-Vert
            "Simic": "#20b2aa",  # Vert-Bleu
            "Izzet": "#ff6347",  # Bleu-Rouge
            "Boros": "#ff8c00",  # Rouge-Blanc
            # Tri-couleurs
            "Esper": "#b0c4de",  # Blanc-Bleu-Noir
            "Jeskai": "#ffd700",  # Blanc-Bleu-Rouge
            "Bant": "#98fb98",  # Blanc-Bleu-Vert
            "Mardu": "#cd853f",  # Blanc-Noir-Rouge
            "Abzan": "#f0e68c",  # Blanc-Noir-Vert
            "Naya": "#ffa500",  # Rouge-Vert-Blanc
            "Grixis": "#8b008b",  # Bleu-Noir-Rouge
            "Sultai": "#2e8b57",  # Noir-Vert-Bleu
            "Temur": "#ff4500",  # Vert-Bleu-Rouge
            "Jund": "#a0522d",  # Noir-Rouge-Vert
            # Multi-couleurs
            "Four-Color": "#9932cc",
            "Five-Color": "#ffd700",
            "Colorless": "#c0c0c0",
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
        """Obtient la couleur d'un archétype basée sur sa guilde MTG"""
        # Priorité 1: Utiliser la guilde si disponible
        if guild_name and guild_name in self.mtg_colors:
            return self.mtg_colors[guild_name]

        # Priorité 2: Extraire la guilde du nom d'archétype
        archetype_lower = archetype_name.lower()
        for guild, color in self.mtg_colors.items():
            if guild.lower() in archetype_lower:
                return color

        # Priorité 3: Couleurs par mots-clés
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

        # Fallback: Couleur par défaut basée sur l'index
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
                f"Données chargées: {len(df)} entrées de {df['tournament_source'].nunique()} sources"
            )
            return df
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {e}")
            raise

    def create_metagame_pie_chart(
        self, df: pd.DataFrame, min_threshold: float = 0.01
    ) -> go.Figure:
        """Crée le pie chart de part de métagame (comme l'image PNG)"""

        # Calculer les parts de métagame par archétype avec couleurs
        archetype_column = (
            "archetype_with_colors"
            if "archetype_with_colors" in df.columns
            else "archetype"
        )
        archetype_counts = df[archetype_column].value_counts()
        total_players = len(df)

        # Calculer les pourcentages
        archetype_shares = (archetype_counts / total_players * 100).round(2)

        # Filtrer les archétypes au-dessus du seuil
        main_archetypes = archetype_shares[archetype_shares >= min_threshold * 100]

        # Regrouper les petits archétypes
        small_archetypes_sum = archetype_shares[
            archetype_shares < min_threshold * 100
        ].sum()

        if small_archetypes_sum > 0:
            main_archetypes["Autres / Non classifiés"] = small_archetypes_sum

        # Trier par valeur décroissante MAIS "Autres" ne doit jamais être en premier
        main_archetypes = main_archetypes.sort_values(ascending=False)

        # RÈGLE CRITIQUE: "Autres" ne doit jamais apparaître en premier
        if main_archetypes.index[0] == "Autres" and len(main_archetypes) > 1:
            # Réorganiser pour que "Autres" soit en dernier
            other_value = main_archetypes["Autres"]
            main_archetypes = main_archetypes.drop("Autres")
            main_archetypes["Autres"] = other_value
        elif (
            main_archetypes.index[0] == "Autres / Non classifiés"
            and len(main_archetypes) > 1
        ):
            # Réorganiser pour que "Autres" soit en dernier
            other_value = main_archetypes["Autres / Non classifiés"]
            main_archetypes = main_archetypes.drop("Autres / Non classifiés")
            main_archetypes["Autres / Non classifiés"] = other_value

        # Créer le pie chart
        fig = go.Figure()

        # Couleurs MTG pour chaque archétype
        archetype_names = main_archetypes.index.tolist()

        # Obtenir les guildes pour chaque archétype depuis les données
        guild_names = []
        for archetype in archetype_names:
            if archetype in ["Autres", "Autres / Non classifiés"]:
                guild_names.append(None)  # Pas de guilde pour "Autres"
            else:
                # Trouver la guilde la plus commune pour cet archétype
                archetype_data = df[df["archetype"] == archetype]
                if not archetype_data.empty and "guild_name" in archetype_data.columns:
                    most_common_guild = archetype_data["guild_name"].mode()
                    guild_names.append(
                        most_common_guild.iloc[0]
                        if len(most_common_guild) > 0
                        else None
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

        # Période d'analyse (à partir des données)
        dates = pd.to_datetime(df["tournament_date"])
        start_date = dates.min().strftime("%Y-%m-%d")
        end_date = dates.max().strftime("%Y-%m-%d")

        # Mise en page
        fig.update_layout(
            title={
                "text": "Standard Metagame Share",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            font=dict(family="Arial, sans-serif", size=12),
            width=900,
            height=600,
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
        # Utiliser archetype_with_colors pour l'affichage avec les couleurs intégrées
        group_column = (
            "archetype_with_colors"
            if "archetype_with_colors" in df.columns
            else "archetype"
        )

        stats_df = (
            df.groupby(group_column)
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
                "text": f"Standard Archetypes Metagame Share (threshold ≥{threshold:.0%})",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="Archetype",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=500,
            margin=dict(l=150, r=50, t=80, b=50),
        )

        return fig

    def create_winrate_confidence_chart(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le graphique à barres d'erreur avec intervalles de confiance"""

        sorted_df = stats_df.sort_values("winrate_mean", ascending=False)

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
                "text": "Archetype Winrates with 95% Confidence Intervals",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Archetype",
            yaxis_title="Winrate",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=500,
            margin=dict(l=50, r=50, t=80, b=80),
        )

        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        fig.update_xaxes(tickangle=45)

        return fig

    def create_tiers_scatter_plot(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le scatter plot des tiers basé sur les bornes inférieures des IC"""

        # Couleurs par tier
        tier_colors = {
            "Tier 1": self.heatmap_colors["c+50"],
            "Tier 2": self.heatmap_colors["c+20"],
            "Tier 3": self.heatmap_colors["c-10"],
            "Tier 4": self.heatmap_colors["c-30"],
        }

        fig = go.Figure()

        for tier in stats_df["tier"].unique():
            tier_data = stats_df[stats_df["tier"] == tier]

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
                "text": "Archetype Classification by Tiers (95% CI Lower Bound)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="95% CI Lower Bound",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
        )

        fig.update_yaxes(tickformat=".0%", range=[0.3, 0.8])

        return fig

    def create_bubble_chart_winrate_presence(self, stats_df: pd.DataFrame) -> go.Figure:
        """Crée le bubble chart winrate vs présence"""

        # Couleurs par tier
        tier_colors = {
            "Tier 1": self.heatmap_colors["c+50"],
            "Tier 2": self.heatmap_colors["c+20"],
            "Tier 3": self.heatmap_colors["c-10"],
            "Tier 4": self.heatmap_colors["c-30"],
        }

        fig = go.Figure()

        for tier in stats_df["tier"].unique():
            tier_data = stats_df[stats_df["tier"] == tier]

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
                "text": "Winrate vs Metagame Presence (size = number of players)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Metagame share (%)",
            yaxis_title="Average winrate",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=600,
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
                "text": f"Top archétypes {title_suffix}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"},
            },
            xaxis_title="Archétype",
            yaxis_title="Nombre de joueurs",
            font=dict(family="Arial, sans-serif", size=12),
            width=800,
            height=500,
            margin=dict(l=50, r=50, t=80, b=80),
        )

        fig.update_xaxes(tickangle=45)

        return fig

    def create_data_sources_pie_chart(self, data):
        """
        Crée un graphique en secteurs de la répartition des sources de données
        """
        # Compter les sources de données
        source_counts = {}
        total_players = 0

        for entry in data:
            source = entry.get("tournament_source", "Unknown")
            players = entry.get("tournament_players", 1)

            if source not in source_counts:
                source_counts[source] = 0
            source_counts[source] += 1
            total_players += 1

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

        for source, count in source_counts.items():
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
            width=800,
            height=500,
        )

        return fig

    def create_archetype_evolution_chart(self, data):
        """
        Crée un graphique d'évolution temporelle des archétypes Standard
        """
        from datetime import datetime

        import pandas as pd

        # Convertir en DataFrame si nécessaire
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()

        # Convertir les dates
        df["tournament_date"] = pd.to_datetime(df["tournament_date"])
        df["date"] = df["tournament_date"].dt.date

        # Grouper par date et archétype avec couleurs
        archetype_column = (
            "archetype_with_colors"
            if "archetype_with_colors" in df.columns
            else "archetype"
        )
        daily_counts = (
            df.groupby(["date", archetype_column]).size().reset_index(name="count")
        )

        # Créer un pivot pour avoir les archétypes en colonnes
        pivot_data = daily_counts.pivot(
            index="date", columns=archetype_column, values="count"
        ).fillna(0)

        # Trier les archétypes par popularité totale
        archetype_totals = df[archetype_column].value_counts()
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
            height=600,
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

    def create_main_archetypes_bar_chart(self, data):
        """
        Crée un graphique en barres des archétypes principaux avec les vraies données
        """
        import pandas as pd

        # Convertir en DataFrame si nécessaire
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()

        # Calculer les pourcentages réels de métagame
        archetype_counts = df["archetype"].value_counts()
        total_decks = len(df)

        # Calculer les pourcentages pour tous les archétypes
        archetype_percentages = (archetype_counts / total_decks * 100).round(2)

        # Prendre les 15 archétypes les plus populaires
        top_archetypes = archetype_percentages.head(15)

        # Calculer le reste comme "Autres"
        others_percentage = (
            archetype_percentages.iloc[15:].sum()
            if len(archetype_percentages) > 15
            else 0
        )

        # Préparer les données pour le graphique
        archetypes = list(top_archetypes.index)
        percentages = list(top_archetypes.values)

        # Ajouter "Autres" si nécessaire
        if others_percentage > 0:
            archetypes.append("Autres / Non classifiés")
            percentages.append(others_percentage)

        # Couleurs MTG pour chaque archétype
        guild_names = []
        for archetype in archetypes:
            if archetype in ["Autres", "Autres / Non classifiés"]:
                guild_names.append(None)  # Pas de guilde pour "Autres"
            else:
                # Trouver la guilde la plus commune pour cet archétype
                archetype_data = df[df["archetype"] == archetype]
                if not archetype_data.empty and "guild_name" in archetype_data.columns:
                    most_common_guild = archetype_data["guild_name"].mode()
                    guild_names.append(
                        most_common_guild.iloc[0]
                        if len(most_common_guild) > 0
                        else None
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
                    + f"Number of decks: {[int(p/100*total_decks) for p in percentages]}<br>"
                    + "<extra></extra>",
                )
            ]
        )

        # Mise en forme
        fig.update_layout(
            title={
                "text": f"Main STANDARD Archetypes - {len(df)} decks analyzed",
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
            height=600,
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
            range=[0, max(percentages) * 1.1],
        )

        return fig

    def create_main_archetypes_bar_horizontal(self, data):
        """
        Crée un graphique en barres horizontal des archétypes principaux (top 15)
        """
        import pandas as pd

        # Convertir en DataFrame si nécessaire
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()

        # Calculer les pourcentages réels de métagame
        archetype_counts = df["archetype"].value_counts()
        total_decks = len(df)
        archetype_percentages = (archetype_counts / total_decks * 100).round(2)
        top_archetypes = archetype_percentages.head(15)
        others_percentage = (
            archetype_percentages.iloc[15:].sum()
            if len(archetype_percentages) > 15
            else 0
        )
        archetypes = list(top_archetypes.index)
        percentages = list(top_archetypes.values)
        if others_percentage > 0:
            archetypes.append("Autres / Non classifiés")
            percentages.append(others_percentage)
        # Couleurs MTG pour chaque archétype
        guild_names = []
        for archetype in archetypes:
            if archetype in ["Autres", "Autres / Non classifiés"]:
                guild_names.append(None)  # Pas de guilde pour "Autres"
            else:
                # Trouver la guilde la plus commune pour cet archétype
                archetype_data = df[df["archetype"] == archetype]
                if not archetype_data.empty and "guild_name" in archetype_data.columns:
                    most_common_guild = archetype_data["guild_name"].mode()
                    guild_names.append(
                        most_common_guild.iloc[0]
                        if len(most_common_guild) > 0
                        else None
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
                "text": f"Main STANDARD Archetypes (Horizontal) - {len(df)} decks analyzed",
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
            height=600,
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
            range=[0, max(percentages) * 1.1],
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
            "top_5_0": self.create_top_5_0_chart(df),
            "data_sources_pie": self.create_data_sources_pie_chart(
                df.to_dict("records")
            ),  # NOUVEAU !
            "archetype_evolution": self.create_archetype_evolution_chart(
                df.to_dict("records")
            ),  # NOUVEAU !
            "main_archetypes_bar": self.create_main_archetypes_bar_chart(
                df.to_dict("records")
            ),  # NOUVEAU !
            "main_archetypes_bar_horizontal": self.create_main_archetypes_bar_horizontal(
                df.to_dict("records")
            ),  # NOUVEAU !
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
