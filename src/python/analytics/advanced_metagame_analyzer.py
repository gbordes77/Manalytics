"""
Advanced Metagame Analyzer - Enhanced analytics for Manalytics
Integrates advanced statistical analysis into the current pipeline
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class AdvancedMetagameAnalyzer:
    """
    Advanced analytics module for Manalytics pipeline

    Provides enhanced statistical analysis capabilities:
    1. Shannon diversity index and Simpson diversity
    2. Archetype clustering and similarity analysis
    3. Temporal trend analysis with categorization
    4. Statistical significance testing
    5. Correlation analysis
    6. Card usage analysis
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data = None
        self.archetype_performance = None
        self.temporal_trends = None
        self.statistical_analysis = None
        self.card_analysis = None

    def load_data(self, df: pd.DataFrame) -> bool:
        """Load tournament data for analysis"""
        try:
            self.data = df.copy()
            self.data["tournament_date"] = pd.to_datetime(self.data["tournament_date"])
            self.data["period"] = self.data["tournament_date"].dt.to_period("W")
            self.data["matches_played"] = self.data["wins"] + self.data["losses"]

            self.logger.info(
                f"📊 Advanced analytics loaded: {len(self.data)} decks, {self.data['archetype'].nunique()} archetypes"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Error loading data for advanced analytics: {e}")
            return False

    def calculate_diversity_metrics(self) -> Dict[str, float]:
        """Calculate Shannon and Simpson diversity indices"""
        if self.data is None:
            return {}

        archetype_counts = self.data["archetype"].value_counts()
        total_decks = len(self.data)

        # Shannon diversity index
        shannon_diversity = -sum(
            (count / total_decks) * np.log(count / total_decks)
            for count in archetype_counts
        )

        # Simpson diversity index
        simpson_diversity = 1 - sum(
            (count / total_decks) ** 2 for count in archetype_counts
        )

        # Effective number of archetypes
        effective_archetypes = np.exp(shannon_diversity)

        # Herfindahl-Hirschman Index (concentration)
        hhi = sum((count / total_decks) ** 2 for count in archetype_counts)

        diversity_metrics = {
            "shannon_diversity": round(shannon_diversity, 4),
            "simpson_diversity": round(simpson_diversity, 4),
            "effective_archetypes": round(effective_archetypes, 2),
            "herfindahl_index": round(hhi, 4),
            "total_archetypes": len(archetype_counts),
            "evenness": round(shannon_diversity / np.log(len(archetype_counts)), 4),
        }

        self.logger.info(
            f"🔢 Diversity metrics calculated: Shannon={shannon_diversity:.3f}, Simpson={simpson_diversity:.3f}"
        )

        return diversity_metrics

    def analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze temporal evolution of archetypes"""
        if self.data is None:
            return {}

        # Group by period and archetype
        temporal_data = (
            self.data.groupby(["period", "archetype"])
            .agg(
                {
                    "archetype": "count",
                    "wins": "sum",
                    "losses": "sum",
                    "winrate": "mean",
                }
            )
            .rename(columns={"archetype": "deck_count"})
        )

        # Calculate meta share by period
        temporal_data["meta_share"] = temporal_data[
            "deck_count"
        ] / temporal_data.groupby("period")["deck_count"].transform("sum")

        # Calculate trends by archetype
        temporal_trends = (
            temporal_data.groupby("archetype")
            .apply(
                lambda x: pd.Series(
                    {
                        "periods_present": len(x),
                        "avg_meta_share": x["meta_share"].mean(),
                        "meta_share_trend": x["meta_share"].diff().mean(),
                        "volatility": x["meta_share"].std(),
                        "growth_rate": (
                            (x["meta_share"].iloc[-1] - x["meta_share"].iloc[0])
                            / max(len(x), 1)
                            if len(x) > 1
                            else 0
                        ),
                        "avg_winrate": x["winrate"].mean(),
                        "peak_meta_share": x["meta_share"].max(),
                        "min_meta_share": x["meta_share"].min(),
                    }
                )
            )
            .fillna(0)
        )

        # Categorize trends
        temporal_trends["trend_category"] = "Stable"
        temporal_trends.loc[
            temporal_trends["meta_share_trend"] > 0.02, "trend_category"
        ] = "Rising"
        temporal_trends.loc[
            temporal_trends["meta_share_trend"] < -0.02, "trend_category"
        ] = "Declining"
        temporal_trends.loc[temporal_trends["volatility"] > 0.1, "trend_category"] = (
            "Volatile"
        )

        # Find emerging and declining archetypes
        emerging = temporal_trends[
            temporal_trends["trend_category"] == "Rising"
        ].nlargest(5, "growth_rate")
        declining = temporal_trends[
            temporal_trends["trend_category"] == "Declining"
        ].nsmallest(5, "growth_rate")

        self.temporal_trends = {
            "summary": temporal_trends,
            "detailed": temporal_data,
            "emerging": emerging,
            "declining": declining,
            "category_counts": temporal_trends["trend_category"]
            .value_counts()
            .to_dict(),
        }

        self.logger.info(
            f"📈 Temporal trends analyzed: {len(temporal_trends)} archetypes"
        )

        return self.temporal_trends

    def perform_archetype_clustering(self, n_clusters: int = 3) -> Dict[str, Any]:
        """Perform K-means clustering on archetype performance"""
        if self.data is None:
            return {}

        # Calculate archetype performance metrics
        archetype_stats = (
            self.data.groupby("archetype")
            .agg(
                {
                    "archetype": "count",
                    "wins": "sum",
                    "losses": "sum",
                    "winrate": "mean",
                    "matches_played": "sum",
                }
            )
            .rename(columns={"archetype": "deck_count"})
        )

        archetype_stats["meta_share"] = archetype_stats["deck_count"] / len(self.data)
        archetype_stats["overall_winrate"] = archetype_stats["wins"] / (
            archetype_stats["wins"] + archetype_stats["losses"]
        )
        archetype_stats["dominance_score"] = (
            archetype_stats["meta_share"] * archetype_stats["overall_winrate"]
        )

        # Prepare clustering features
        features = ["meta_share", "overall_winrate", "dominance_score"]
        clustering_data = archetype_stats[features].fillna(0)

        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clustering_data)

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)

        # Add cluster labels to archetype stats
        archetype_stats["cluster"] = clusters

        # Analyze clusters
        cluster_profiles = (
            archetype_stats.groupby("cluster")
            .agg(
                {
                    "meta_share": ["mean", "std"],
                    "overall_winrate": ["mean", "std"],
                    "dominance_score": ["mean", "std"],
                    "deck_count": "sum",
                }
            )
            .round(4)
        )

        cluster_analysis = {
            "archetype_clusters": archetype_stats["cluster"].to_dict(),
            "cluster_profiles": cluster_profiles,
            "cluster_centers": kmeans.cluster_centers_,
            "inertia": kmeans.inertia_,
            "archetype_stats": archetype_stats,
        }

        self.logger.info(f"🎯 Archetype clustering completed: {n_clusters} clusters")

        return cluster_analysis

    def calculate_correlations(self) -> Dict[str, Any]:
        """Calculate correlation matrix for key metrics"""
        if self.data is None:
            return {}

        numeric_cols = ["wins", "losses", "winrate", "matches_played"]
        available_cols = [col for col in numeric_cols if col in self.data.columns]

        if len(available_cols) < 2:
            return {}

        # Calculate correlation matrix
        correlation_matrix = self.data[available_cols].corr()

        # Statistical significance tests
        significance_tests = {}
        for col in available_cols:
            if col in self.data.columns:
                stat, p_value = stats.normaltest(self.data[col].dropna())
                significance_tests[f"{col}_normality"] = {
                    "statistic": round(stat, 4),
                    "p_value": round(p_value, 4),
                    "is_normal": p_value > 0.05,
                }

        correlation_analysis = {
            "correlation_matrix": correlation_matrix.round(4),
            "significance_tests": significance_tests,
            "strongest_correlations": self._find_strongest_correlations(
                correlation_matrix
            ),
        }

        self.logger.info(f"🔗 Correlation analysis completed")

        return correlation_analysis

    def _find_strongest_correlations(self, corr_matrix: pd.DataFrame) -> List[Dict]:
        """Find strongest correlations excluding diagonal"""
        correlations = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]

                correlations.append(
                    {
                        "variable1": col1,
                        "variable2": col2,
                        "correlation": round(corr_value, 4),
                        "strength": (
                            "Strong"
                            if abs(corr_value) > 0.7
                            else "Moderate" if abs(corr_value) > 0.3 else "Weak"
                        ),
                    }
                )

        return sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True)

    def analyze_card_usage(self) -> Dict[str, Any]:
        """Analyze individual card usage patterns"""
        if self.data is None or "deck_cards" not in self.data.columns:
            return {}

        all_cards = []
        for idx, row in self.data.iterrows():
            cards = row.get("deck_cards", [])
            if isinstance(cards, list):
                for card in cards:
                    if isinstance(card, dict) and "Name" in card:
                        all_cards.append(
                            {
                                "card_name": card["Name"],
                                "quantity": card.get("Quantity", 1),
                                "archetype": row["archetype"],
                                "winrate": row["winrate"],
                                "tournament_date": row["tournament_date"],
                            }
                        )

        if not all_cards:
            return {}

        cards_df = pd.DataFrame(all_cards)

        # Overall card statistics
        card_stats = (
            cards_df.groupby("card_name")
            .agg(
                {
                    "quantity": ["sum", "mean"],
                    "archetype": ["count", "nunique"],
                    "winrate": ["mean", "std"],
                }
            )
            .round(3)
        )

        card_stats.columns = ["_".join(col) for col in card_stats.columns]
        card_stats["usage_rate"] = (
            card_stats["archetype_count"] / len(self.data)
        ).round(4)

        # Top cards by usage
        top_cards = card_stats.nlargest(20, "usage_rate")

        # Cards by archetype
        archetype_card_usage = (
            cards_df.groupby(["archetype", "card_name"])
            .agg({"quantity": ["sum", "mean"], "winrate": "mean"})
            .round(3)
        )

        card_analysis = {
            "total_unique_cards": len(card_stats),
            "top_cards": top_cards,
            "archetype_usage": archetype_card_usage,
            "usage_distribution": card_stats["usage_rate"].describe().round(4),
        }

        self.card_analysis = card_analysis
        self.logger.info(f"🃏 Card analysis completed: {len(card_stats)} unique cards")

        return card_analysis

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate complete advanced analysis report"""
        if self.data is None:
            return {}

        self.logger.info("🔬 Starting comprehensive advanced analysis...")

        # Run all analyses
        diversity_metrics = self.calculate_diversity_metrics()
        temporal_trends = self.analyze_temporal_trends()
        clustering_analysis = self.perform_archetype_clustering()
        correlation_analysis = self.calculate_correlations()
        card_analysis = self.analyze_card_usage()

        # Compile comprehensive report
        comprehensive_report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_decks": len(self.data),
                "unique_archetypes": self.data["archetype"].nunique(),
                "date_range": {
                    "start": self.data["tournament_date"].min().strftime("%Y-%m-%d"),
                    "end": self.data["tournament_date"].max().strftime("%Y-%m-%d"),
                },
            },
            "diversity_metrics": diversity_metrics,
            "temporal_trends": {
                "summary": (
                    temporal_trends.get("summary", pd.DataFrame()).to_dict("index")
                    if not temporal_trends.get("summary", pd.DataFrame()).empty
                    else {}
                ),
                "category_counts": temporal_trends.get("category_counts", {}),
                "emerging_archetypes": (
                    temporal_trends.get("emerging", pd.DataFrame()).to_dict("index")
                    if not temporal_trends.get("emerging", pd.DataFrame()).empty
                    else {}
                ),
                "declining_archetypes": (
                    temporal_trends.get("declining", pd.DataFrame()).to_dict("index")
                    if not temporal_trends.get("declining", pd.DataFrame()).empty
                    else {}
                ),
            },
            "clustering_analysis": {
                "archetype_clusters": clustering_analysis.get("archetype_clusters", {}),
                "cluster_profiles": (
                    clustering_analysis.get("cluster_profiles", pd.DataFrame()).to_dict(
                        "index"
                    )
                    if not clustering_analysis.get(
                        "cluster_profiles", pd.DataFrame()
                    ).empty
                    else {}
                ),
            },
            "correlation_analysis": {
                "correlation_matrix": (
                    correlation_analysis.get(
                        "correlation_matrix", pd.DataFrame()
                    ).to_dict("index")
                    if not correlation_analysis.get(
                        "correlation_matrix", pd.DataFrame()
                    ).empty
                    else {}
                ),
                "significance_tests": correlation_analysis.get(
                    "significance_tests", {}
                ),
                "strongest_correlations": correlation_analysis.get(
                    "strongest_correlations", []
                ),
            },
            "card_analysis": {
                "total_unique_cards": card_analysis.get("total_unique_cards", 0),
                "top_cards": (
                    card_analysis.get("top_cards", pd.DataFrame()).to_dict("index")
                    if not card_analysis.get("top_cards", pd.DataFrame()).empty
                    else {}
                ),
                "usage_distribution": card_analysis.get("usage_distribution", {}),
            },
        }

        self.logger.info("✅ Comprehensive advanced analysis completed")

        return comprehensive_report
