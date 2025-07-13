#!/usr/bin/env python3
"""
Manalytics - Outil d'analyse de métagame Magic: The Gathering
Outil de production unifié avec paramètres en ligne de commande

Usage:
    python manalytics_tool.py --format standard --start-date 2025-05-01 --end-date 2025-07-01
    python manalytics_tool.py --format modern --start-date 2025-01-01 --end-date 2025-12-31
    python manalytics_tool.py --format legacy --start-date 2025-06-01 --end-date 2025-06-30
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
import seaborn as sns
from plotly.subplots import make_subplots


class ManalyticsEngine:
    """Moteur d'analyse unifié pour tous les formats Magic"""

    def __init__(
        self, format_name: str, start_date: str, end_date: str, output_dir: str = None
    ):
        self.format_name = format_name.lower()
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        self.output_dir = (
            output_dir or f"{self.format_name}_analysis_{start_date}_{end_date}"
        )
        self.df = None
        self.tournaments_loaded = 0

        print(f"🎯 Manalytics Engine initialisé")
        print(f"📊 Format: {self.format_name.upper()}")
        print(f"📅 Période: {start_date} à {end_date}")
        print(f"📁 Sortie: {self.output_dir}")

    def load_tournament_data(self):
        """Charger les données de tournois selon les paramètres"""
        print(f"\n🔍 Recherche des tournois {self.format_name.upper()}...")

        # Patterns de recherche dynamiques
        patterns = self._generate_search_patterns()

        tournament_files = []
        for pattern in patterns:
            tournament_files.extend(glob.glob(pattern))

        print(f"📁 Fichiers trouvés: {len(tournament_files)}")

        if not tournament_files:
            print(f"❌ Aucun fichier de tournoi trouvé pour {self.format_name}")
            return False

        # Charger et filtrer les tournois
        all_decks = []
        self.tournaments_loaded = 0

        for file_path in tournament_files:
            try:
                decks = self._process_tournament_file(file_path)
                if decks:
                    all_decks.extend(decks)
                    self.tournaments_loaded += 1

            except Exception as e:
                print(f"❌ Erreur lors du chargement de {file_path}: {e}")
                continue

        if not all_decks:
            print(
                f"❌ Aucun deck trouvé pour {self.format_name} dans la période spécifiée"
            )
            return False

        # Créer le DataFrame
        self.df = pd.DataFrame(all_decks)
        self.df["tournament_date"] = pd.to_datetime(self.df["tournament_date"])

        print(f"\n📊 DONNÉES CHARGÉES:")
        print(f"🏆 Tournois: {self.tournaments_loaded}")
        print(f"🎯 Decks: {len(self.df)}")
        print(
            f"📅 Période réelle: {self.df['tournament_date'].min().strftime('%Y-%m-%d')} à {self.df['tournament_date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"🎲 Archétypes: {self.df['archetype'].nunique()}")
        print(f"🌐 Sources: {', '.join(self.df['tournament_source'].unique())}")

        return True

    def _generate_search_patterns(self):
        """Générer les patterns de recherche pour les fichiers de tournois"""
        patterns = []

        # Générer les patterns pour chaque année/mois dans la période
        current_date = self.start_date
        while current_date <= self.end_date:
            year = current_date.year
            month = f"{current_date.month:02d}"

            # Patterns pour différentes sources et structures
            base_patterns = [
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/{self.format_name}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/*{self.format_name}*.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/{self.format_name}*.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/*{self.format_name}*.json",
                f"MTGODecklistCache/Tournaments/*/*/{year}/{month}/*/{self.format_name}*.json",
                f"MTGODecklistCache/Tournaments/*/*/{year}/{month}/*/*{self.format_name}*.json",
            ]
            patterns.extend(base_patterns)

            # Passer au mois suivant
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return patterns

    def _process_tournament_file(self, file_path: str):
        """Traiter un fichier de tournoi individual"""
        with open(file_path, "r", encoding="utf-8") as f:
            tournament_data = json.load(f)

        # Adapter à différents formats de données
        tournament_info = tournament_data.get("Tournament", tournament_data)

        # Vérifier le format (basé sur le nom du fichier ou les données)
        if self.format_name not in file_path.lower():
            # Vérifier aussi dans les données si disponible
            format_in_data = tournament_info.get("format", "").lower()
            if format_in_data and self.format_name not in format_in_data:
                return []

        # Extraire la date du tournoi
        tournament_date = self._extract_tournament_date(tournament_info, file_path)
        if not tournament_date:
            return []

        # Filtrer par période
        if not (self.start_date <= tournament_date <= self.end_date):
            return []

        # Traiter les decks
        decks = tournament_data.get("Decks", tournament_data.get("decks", []))
        processed_decks = []

        for deck in decks:
            deck_data = self._process_deck(
                deck, tournament_info, tournament_date, file_path
            )
            if deck_data:
                processed_decks.append(deck_data)

        if processed_decks:
            tournament_name = tournament_info.get(
                "Name", tournament_info.get("name", "Tournoi")
            )
            print(
                f"✅ {tournament_name} ({tournament_date}) - {len(processed_decks)} decks"
            )

        return processed_decks

    def _extract_tournament_date(self, tournament_info, file_path):
        """Extraire la date du tournoi depuis les données ou le nom du fichier"""
        # Essayer d'extraire depuis les données
        date_str = tournament_info.get("Date", tournament_info.get("date", ""))

        if date_str:
            try:
                # Format ISO avec timezone
                if "T" in date_str:
                    return datetime.fromisoformat(
                        date_str.replace("Z", "+00:00")
                    ).date()
                # Format simple YYYY-MM-DD
                else:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                pass

        # Extraire depuis le nom du fichier (ex: tournament-2025-05-01.json)
        import re

        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path)
        if date_match:
            try:
                return datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            except:
                pass

        return None

    def _process_deck(self, deck, tournament_info, tournament_date, file_path):
        """Traiter un deck individual"""
        # Extraire les wins/losses
        wins, losses = self._extract_results(deck)

        # Classifier l'archétype
        archetype = self._classify_archetype(deck)

        # Déterminer la source
        source = self._determine_source(file_path)

        return {
            "tournament_id": tournament_info.get(
                "Uri", tournament_info.get("id", file_path)
            ),
            "tournament_name": tournament_info.get(
                "Name", tournament_info.get("name", "Tournoi")
            ),
            "tournament_date": tournament_date,
            "tournament_source": source,
            "format": self.format_name,
            "player_name": deck.get("Player", deck.get("player", "")),
            "archetype": archetype,
            "wins": wins,
            "losses": losses,
            "draws": deck.get("draws", 0),
            "matches_played": wins + losses,
            "winrate": wins / max(1, wins + losses) if (wins + losses) > 0 else 0,
            "placement": deck.get("placement", 0),
            "deck_cards": deck.get("Mainboard", deck.get("mainboard", [])),
        }

    def _extract_results(self, deck):
        """Extraire les résultats (wins/losses) d'un deck"""
        # Format "5-0", "4-1", etc.
        result = deck.get("Result", deck.get("result", "0-0"))

        wins, losses = 0, 0
        if "-" in str(result):
            try:
                parts = str(result).split("-")
                wins = int(parts[0])
                losses = int(parts[1]) if len(parts) > 1 else 0
            except:
                pass
        else:
            # Format directly in data
            wins = deck.get("wins", 0)
            losses = deck.get("losses", 0)

        return wins, losses

    def _classify_archetype(self, deck):
        """Classifier l'archétype d'un deck"""
        # Si l'archétype est déjà fourni
        if deck.get("archetype"):
            return deck["archetype"]

        # Sinon, classifier basé sur les cartes
        mainboard = deck.get("Mainboard", deck.get("mainboard", []))
        if not mainboard:
            return "Unknown"

        # Classification par format
        if self.format_name == "standard":
            return self._classify_standard_archetype(mainboard)
        elif self.format_name == "modern":
            return self._classify_modern_archetype(mainboard)
        elif self.format_name == "legacy":
            return self._classify_legacy_archetype(mainboard)
        else:
            return self._classify_generic_archetype(mainboard)

    def _classify_standard_archetype(self, mainboard):
        """Classification spécifique au Standard"""
        archetype_cards = {
            "Jeskai Control": [
                "Teferi, Hero of Dominaria",
                "Teferi, Time Raveler",
                "Dovin's Veto",
                "Wrath of God",
                "Day of Judgment",
            ],
            "Bant Ramp": [
                "Overlord of the Hauntwoods",
                "Beza, the Bounding Spring",
                "Leyline Binding",
            ],
            "Jeskai Convoke": [
                "Helping Hand",
                "Proft's Eidetic Memory",
                "Steamcore Scholar",
            ],
            "Mono Red Aggro": [
                "Lightning Bolt",
                "Goblin Guide",
                "Monastery Swiftspear",
                "Torch the Tower",
            ],
            "Azorius Control": [
                "Teferi, Hero of Dominaria",
                "Absorb",
                "Dovin's Veto",
                "Wrath of God",
            ],
        }

        matched_archetype = self._match_archetype(mainboard, archetype_cards)

        # RÈGLE CRITIQUE: En Standard, les archétypes monocolor génériques = "Other"
        if matched_archetype and any(
            mono in matched_archetype
            for mono in ["Mono Blue", "Mono White", "Mono Black", "Mono Green"]
        ):
            return "Other"

        return matched_archetype if matched_archetype else "Other"

    def _classify_modern_archetype(self, mainboard):
        """Classification spécifique au Modern"""
        archetype_cards = {
            "Burn": [
                "Lightning Bolt",
                "Lava Spike",
                "Rift Bolt",
                "Monastery Swiftspear",
            ],
            "Affinity": [
                "Ornithopter",
                "Mox Opal",
                "Arcbound Ravager",
                "Steel Overseer",
            ],
            "Tron": [
                "Karn Liberated",
                "Ugin, the Spirit Dragon",
                "Urza's Tower",
                "Urza's Mine",
            ],
            "Death's Shadow": [
                "Death's Shadow",
                "Thoughtseize",
                "Street Wraith",
                "Temur Battle Rage",
            ],
            "Jund": ["Tarmogoyf", "Dark Confidant", "Lightning Bolt", "Thoughtseize"],
        }

        matched_archetype = self._match_archetype(mainboard, archetype_cards)

        # RÈGLE CRITIQUE: En Modern, Mono Red = "Other"
        if matched_archetype and any(
            mono in matched_archetype
            for mono in [
                "Mono Red",
                "Mono Blue",
                "Mono White",
                "Mono Black",
                "Mono Green",
            ]
        ):
            return "Other"

        return matched_archetype if matched_archetype else "Other"

    def _classify_legacy_archetype(self, mainboard):
        """Classification spécifique au Legacy"""
        archetype_cards = {
            "Delver": ["Delver of Secrets", "Daze", "Force of Will", "Wasteland"],
            "Miracles": [
                "Terminus",
                "Counterbalance",
                "Sensei's Divining Top",
                "Brainstorm",
            ],
            "Storm": [
                "Tendrils of Agony",
                "Lion's Eye Diamond",
                "Infernal Tutor",
                "Dark Ritual",
            ],
            "Reanimator": ["Reanimate", "Entomb", "Griselbrand", "Show and Tell"],
        }

        return self._match_archetype(mainboard, archetype_cards)

    def _match_archetype(self, mainboard, archetype_cards):
        """Matcher un archétype basé sur les cartes clés"""
        card_names = [card.get("CardName", card.get("name", "")) for card in mainboard]

        archetype_scores = {}
        for archetype, key_cards in archetype_cards.items():
            score = 0
            for key_card in key_cards:
                if any(key_card in card_name for card_name in card_names):
                    score += 1
            archetype_scores[archetype] = score

        if archetype_scores:
            best_archetype = max(archetype_scores, key=archetype_scores.get)
            if archetype_scores[best_archetype] > 0:
                return best_archetype

        # Classification par couleurs si pas d'archétype spécifique
        colors = self._detect_colors(card_names)
        return f"{colors} Deck" if colors else "Unknown"

    def _classify_generic_archetype(self, mainboard):
        """Classification générique par couleurs"""
        card_names = [card.get("CardName", card.get("name", "")) for card in mainboard]
        colors = self._detect_colors(card_names)
        return f"{colors} Deck" if colors else "Unknown"

    def _detect_colors(self, card_names):
        """Détecter les couleurs d'un deck"""
        color_indicators = {
            "W": [
                "Plains",
                "Wrath",
                "Teferi",
                "Dovin",
                "Day of Judgment",
                "Swords to Plowshares",
            ],
            "U": [
                "Island",
                "Counterspell",
                "Teferi",
                "Dovin",
                "Force of Will",
                "Brainstorm",
            ],
            "B": [
                "Swamp",
                "Thoughtseize",
                "Sheoldred",
                "Liliana",
                "Dark Ritual",
                "Fatal Push",
            ],
            "R": ["Mountain", "Lightning", "Torch", "Goblin", "Monastery", "Bolt"],
            "G": ["Forest", "Llanowar", "Cultivate", "Tarmogoyf", "Noble Hierarch"],
        }

        detected_colors = []
        for color, indicators in color_indicators.items():
            for indicator in indicators:
                if any(indicator in card_name for card_name in card_names):
                    detected_colors.append(color)
                    break

        # Mapper les combinaisons
        color_combinations = {
            frozenset(["W"]): "Mono White",
            frozenset(["U"]): "Mono Blue",
            frozenset(["B"]): "Mono Black",
            frozenset(["R"]): "Mono Red",
            frozenset(["G"]): "Mono Green",
            frozenset(["W", "U"]): "Azorius",
            frozenset(["U", "B"]): "Dimir",
            frozenset(["B", "R"]): "Rakdos",
            frozenset(["R", "G"]): "Gruul",
            frozenset(["G", "W"]): "Selesnya",
            frozenset(["W", "B"]): "Orzhov",
            frozenset(["U", "R"]): "Izzet",
            frozenset(["B", "G"]): "Golgari",
            frozenset(["R", "W"]): "Boros",
            frozenset(["G", "U"]): "Simic",
            frozenset(["W", "U", "B"]): "Esper",
            frozenset(["U", "B", "R"]): "Grixis",
            frozenset(["B", "R", "G"]): "Jund",
            frozenset(["R", "G", "W"]): "Naya",
            frozenset(["G", "W", "U"]): "Bant",
            frozenset(["W", "U", "R"]): "Jeskai",
        }

        color_set = frozenset(detected_colors)
        return color_combinations.get(
            color_set, "Multicolor" if len(detected_colors) > 3 else "Unknown"
        )

    def _determine_source(self, file_path):
        """Déterminer la source du tournoi"""
        if "mtgo.com" in file_path:
            return "mtgo.com"
        elif "melee.gg" in file_path:
            return "melee.gg"
        elif "topdeck.gg" in file_path:
            return "topdeck.gg"
        elif "manatraders.com" in file_path:
            return "manatraders.com"
        else:
            return "unknown"

    def analyze_metagame(self):
        """Analyser le métagame"""
        if self.df is None or len(self.df) == 0:
            print("❌ Aucune donnée à analyser")
            return {}

        print(f"\n🎯 ANALYSE DU MÉTAGAME {self.format_name.upper()}")
        print("=" * 50)

        # Part de métagame
        archetype_counts = self.df["archetype"].value_counts()
        total_decks = len(self.df)
        meta_share = (archetype_counts / total_decks * 100).round(2)

        print("📊 PART DE MÉTAGAME:")
        print("-" * 30)
        for archetype, count in archetype_counts.head(10).items():
            percentage = meta_share[archetype]
            print(f"🎯 {archetype}: {count} decks ({percentage}%)")

        # Winrates
        print(f"\n📈 WINRATES PAR ARCHÉTYPE:")
        print("-" * 30)
        archetype_winrates = (
            self.df.groupby("archetype")
            .agg(
                {
                    "wins": "sum",
                    "losses": "sum",
                    "winrate": "mean",
                    "player_name": "count",
                }
            )
            .round(3)
        )

        archetype_winrates["global_winrate"] = archetype_winrates["wins"] / (
            archetype_winrates["wins"] + archetype_winrates["losses"]
        )

        archetype_winrates = archetype_winrates.sort_values(
            "global_winrate", ascending=False
        )

        for archetype, stats in archetype_winrates.head(10).iterrows():
            print(
                f"🎯 {archetype}: {stats['global_winrate']:.3f} ({stats['player_name']} decks)"
            )

        return {
            "meta_share": meta_share,
            "winrates": archetype_winrates,
            "total_decks": total_decks,
            "total_tournaments": self.tournaments_loaded,
        }

    def create_all_visualizations(self):
        """Créer toutes les visualisations"""
        print(f"\n📊 CRÉATION DES VISUALISATIONS")
        print("=" * 50)

        output_path = Path(self.output_dir)
        output_path.mkdir(exist_ok=True)

        # 1. Part de métagame
        self._create_metagame_pie_chart(output_path)

        # 2. Winrates par archétype
        self._create_winrates_bar_chart(output_path)

        # 3. Évolution temporelle
        self._create_temporal_evolution(output_path)

        # 4. Distribution des performances
        self._create_performance_distribution(output_path)

        # 5. Analyse par source
        self._create_source_analysis(output_path)

        # 6. Matrice de matchups (estimée)
        self._create_matchup_matrix(output_path)

        print(f"✅ Toutes les visualisations créées dans {self.output_dir}/")

        return output_path

    def _create_metagame_pie_chart(self, output_path):
        """Créer le graphique de part de métagame"""
        archetype_counts = self.df["archetype"].value_counts()

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=archetype_counts.index,
                    values=archetype_counts.values,
                    hole=0.3,
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )

        fig.update_layout(
            title=f"Part de métagame {self.format_name.upper()} ({self.start_date} à {self.end_date})",
            font=dict(size=14),
            width=800,
            height=600,
        )

        fig.write_html(output_path / "metagame_share.html")
        print("✅ Graphique part de métagame créé")

    def _create_winrates_bar_chart(self, output_path):
        """Créer le graphique des winrates"""
        archetype_stats = (
            self.df.groupby("archetype")
            .agg({"wins": "sum", "losses": "sum", "winrate": ["mean", "std", "count"]})
            .round(3)
        )

        archetype_stats.columns = [
            "total_wins",
            "total_losses",
            "avg_winrate",
            "winrate_std",
            "deck_count",
        ]
        archetype_stats["global_winrate"] = archetype_stats["total_wins"] / (
            archetype_stats["total_wins"] + archetype_stats["total_losses"]
        )

        archetype_stats = archetype_stats.sort_values("global_winrate", ascending=True)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=archetype_stats.index,
                x=archetype_stats["global_winrate"],
                orientation="h",
                text=[f"{wr:.3f}" for wr in archetype_stats["global_winrate"]],
                textposition="auto",
            )
        )

        fig.update_layout(
            title=f"Winrates par archétype {self.format_name.upper()}",
            xaxis_title="Winrate",
            yaxis_title="Archétype",
            width=1000,
            height=600,
        )

        fig.write_html(output_path / "winrates_by_archetype.html")
        print("✅ Graphique winrates créé")

    def _create_temporal_evolution(self, output_path):
        """Créer l'évolution temporelle"""
        daily_data = (
            self.df.groupby(["tournament_date", "archetype"])
            .size()
            .reset_index(name="count")
        )

        # Top 8 archétypes
        top_archetypes = self.df["archetype"].value_counts().head(8).index
        daily_data = daily_data[daily_data["archetype"].isin(top_archetypes)]

        fig = px.line(
            daily_data,
            x="tournament_date",
            y="count",
            color="archetype",
            title=f"Évolution temporelle {self.format_name.upper()}",
            labels={"count": "Nombre de decks", "tournament_date": "Date"},
        )

        fig.update_layout(width=1200, height=600)
        fig.write_html(output_path / "temporal_evolution.html")
        print("✅ Graphique évolution temporelle créé")

    def _create_performance_distribution(self, output_path):
        """Créer la distribution des performances"""
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=self.df["winrate"],
                nbinsx=20,
                name="Distribution des winrates",
                opacity=0.7,
            )
        )

        fig.update_layout(
            title=f"Distribution des winrates {self.format_name.upper()}",
            xaxis_title="Winrate",
            yaxis_title="Nombre de decks",
            width=800,
            height=500,
        )

        fig.write_html(output_path / "performance_distribution.html")
        print("✅ Distribution des performances créée")

    def _create_source_analysis(self, output_path):
        """Créer l'analyse par source"""
        source_stats = (
            self.df.groupby("tournament_source")
            .agg(
                {"tournament_id": "nunique", "player_name": "count", "winrate": "mean"}
            )
            .round(3)
        )

        fig = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=("Tournois", "Decks", "Winrate moyen"),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
        )

        fig.add_trace(
            go.Bar(x=source_stats.index, y=source_stats["tournament_id"]), row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=source_stats.index, y=source_stats["player_name"]), row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=source_stats.index, y=source_stats["winrate"]), row=1, col=3
        )

        fig.update_layout(
            title="Analyse par source de données",
            showlegend=False,
            width=1200,
            height=400,
        )

        fig.write_html(output_path / "source_analysis.html")
        print("✅ Analyse par source créée")

    def _create_matchup_matrix(self, output_path):
        """Créer une matrice de matchups estimée"""
        archetypes = self.df["archetype"].value_counts().head(10).index

        # Matrice basée sur les winrates relatifs
        base_winrates = {}
        for archetype in archetypes:
            archetype_data = self.df[self.df["archetype"] == archetype]
            base_winrates[archetype] = archetype_data["winrate"].mean()

        matrix = np.zeros((len(archetypes), len(archetypes)))

        for i, arch1 in enumerate(archetypes):
            for j, arch2 in enumerate(archetypes):
                if i == j:
                    matrix[i][j] = 0.5
                else:
                    wr1 = base_winrates[arch1]
                    wr2 = base_winrates[arch2]
                    matchup_wr = 0.5 + (wr1 - wr2) * 0.3
                    matrix[i][j] = max(0.1, min(0.9, matchup_wr))

        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=archetypes,
                y=archetypes,
                colorscale="RdYlBu",
                zmid=0.5,
                text=np.round(matrix, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title=f"Matrice de matchups {self.format_name.upper()} (estimée)",
            width=800,
            height=600,
        )

        fig.write_html(output_path / "matchup_matrix.html")
        print("✅ Matrice de matchups créée")

    def generate_complete_report(self):
        """Générer le rapport complet"""
        print(f"\n📋 GÉNÉRATION DU RAPPORT COMPLET")
        print("=" * 50)

        # Analyser les données
        analysis_results = self.analyze_metagame()

        # Créer les visualisations
        output_path = self.create_all_visualizations()

        # Générer le rapport HTML
        self._generate_html_report(output_path, analysis_results)

        # Exporter les données
        self._export_data(output_path)

        print(f"\n🎉 RAPPORT COMPLET GÉNÉRÉ!")
        print(f"📁 Dossier: {self.output_dir}")
        print(f"📊 {len(self.df)} decks analysés de {self.tournaments_loaded} tournois")
        print(f"🎯 {self.df['archetype'].nunique()} archétypes différents")

        return output_path

    def _generate_html_report(self, output_path, analysis_results):
        """Générer le rapport HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rapport {self.format_name.upper()} - {self.start_date} à {self.end_date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #2c3e50; }}
                .section {{ margin: 30px 0; }}
                .stats {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .chart-link {{ display: inline-block; margin: 10px; padding: 10px 20px;
                             background: #3498db; color: white; text-decoration: none;
                             border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Rapport {self.format_name.upper()}</h1>
                <p>Période: {self.start_date} à {self.end_date}</p>
                <p>Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="section">
                <h2>📊 Résumé des données</h2>
                <div class="stats">
                    <p><strong>Decks analysés:</strong> {len(self.df)}</p>
                    <p><strong>Tournois:</strong> {self.tournaments_loaded}</p>
                    <p><strong>Archétypes:</strong> {self.df['archetype'].nunique()}</p>
                    <p><strong>Sources:</strong> {', '.join(self.df['tournament_source'].unique())}</p>
                </div>
            </div>

            <div class="section">
                <h2>📈 Graphiques</h2>
                <a href="metagame_share.html" class="chart-link">Part de métagame</a>
                <a href="winrates_by_archetype.html" class="chart-link">Winrates</a>
                <a href="temporal_evolution.html" class="chart-link">Évolution temporelle</a>
                <a href="performance_distribution.html" class="chart-link">Distribution performances</a>
                <a href="source_analysis.html" class="chart-link">Analyse sources</a>
                <a href="matchup_matrix.html" class="chart-link">Matrice matchups</a>
            </div>

            <div class="section">
                <h2>🏆 Top 5 archétypes</h2>
                <div class="stats">
        """

        # Top 5 archétypes
        top_5 = self.df["archetype"].value_counts().head(5)
        for archetype, count in top_5.items():
            percentage = count / len(self.df) * 100
            avg_winrate = self.df[self.df["archetype"] == archetype]["winrate"].mean()
            html_content += f"<p><strong>{archetype}:</strong> {count} decks ({percentage:.1f}%) - WR: {avg_winrate:.3f}</p>"

        html_content += """
                </div>
            </div>

            <div class="section">
                <p><em>Rapport généré par Manalytics - Données réelles de tournois scrapés</em></p>
            </div>
        </body>
        </html>
        """

        with open(output_path / "rapport_complet.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("✅ Rapport HTML généré")

    def _export_data(self, output_path):
        """Exporter les données"""
        # CSV
        self.df.to_csv(output_path / "donnees_analysees.csv", index=False)
        print("✅ Données CSV exportées")

        # JSON
        self.df.to_json(
            output_path / "donnees_analysees.json", orient="records", indent=2
        )
        print("✅ Données JSON exportées")


def main():
    """Fonction principale avec arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Manalytics - Outil d'analyse de métagame Magic: The Gathering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python manalytics_tool.py --format standard --start-date 2025-05-01 --end-date 2025-07-01
  python manalytics_tool.py --format modern --start-date 2025-01-01 --end-date 2025-12-31
  python manalytics_tool.py --format legacy --start-date 2025-06-01 --end-date 2025-06-30
        """,
    )

    parser.add_argument(
        "--format",
        required=True,
        choices=["standard", "modern", "legacy", "pioneer", "vintage", "pauper"],
        help="Format de Magic à analyser",
    )

    parser.add_argument(
        "--start-date", required=True, help="Date de début (format: YYYY-MM-DD)"
    )

    parser.add_argument(
        "--end-date", required=True, help="Date de fin (format: YYYY-MM-DD)"
    )

    parser.add_argument("--output-dir", help="Dossier de sortie (optionnel)")

    parser.add_argument("--verbose", action="store_true", help="Affichage détaillé")

    args = parser.parse_args()

    # Validation des dates
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

        if start_date >= end_date:
            print("❌ La date de début doit être antérieure à la date de fin")
            sys.exit(1)

    except ValueError:
        print("❌ Format de date invalide. Utilisez YYYY-MM-DD")
        sys.exit(1)

    print("🚀 MANALYTICS - OUTIL DE PRODUCTION")
    print("=" * 50)
    print(f"📊 Format: {args.format.upper()}")
    print(f"📅 Période: {args.start_date} à {args.end_date}")
    print("🎯 Utilisation exclusive de données réelles")
    print()

    # Créer l'analyseur
    engine = ManalyticsEngine(
        format_name=args.format,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
    )

    # Charger les données
    if not engine.load_tournament_data():
        print("❌ Impossible de charger les données")
        sys.exit(1)

    # Générer le rapport complet
    engine.generate_complete_report()

    # SUPPRIMÉ: Ancien code qui causait l'erreur d'import
    # try:
    #     from html_report_generator import update_index_html
    #     update_index_html()
    #     print("\n✅ index.html mis à jour automatiquement !")
    # except Exception as e:
    #     print(f"⚠️ Erreur lors de la mise à jour automatique de l'index.html : {e}")

    print("\n🎉 ANALYSE TERMINÉE!")
    print(f"📁 Consultez le dossier '{engine.output_dir}' pour tous les résultats")


if __name__ == "__main__":
    main()
