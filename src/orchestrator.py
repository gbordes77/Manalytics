"""
Orchestrator Manalytics - Phase 3 (Visualisations uniquement)
Pipeline simplifié avec génération automatique des graphiques
"""
import asyncio
import glob
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.python.visualizations.matchup_matrix import MatchupMatrixGenerator
from src.python.visualizations.metagame_charts import MetagameChartsGenerator


class ManalyticsOrchestrator:
    """Orchestrateur Phase 3 - Visualisations uniquement"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def run_pipeline(self, format: str, start_date: str, end_date: str):
        """Pipeline Phase 3 avec génération automatique des visualisations"""
        try:
            # Créer le dossier d'analyse daté dans Analyses/
            analysis_folder = f"{format.lower()}_analysis_{start_date}_{end_date}"
            analyses_dir = Path("Analyses")
            analyses_dir.mkdir(exist_ok=True)
            output_dir = analyses_dir / analysis_folder
            output_dir.mkdir(exist_ok=True)

            self.logger.info(f"🚀 Démarrage du pipeline complet pour {format}")
            self.logger.info(f"📁 Dossier d'analyse: {analysis_folder}")

            # Stocker les paramètres pour le dashboard
            self.format = format
            self.start_date = start_date
            self.end_date = end_date

            # 1. Génération des visualisations
            self.logger.info("🎨 Génération des visualisations...")
            visualization_report = await self.generate_visualizations(str(output_dir))

            # 2. Résumé final
            self.logger.info(f"✅ Pipeline terminé avec succès dans {analysis_folder}!")

            return {
                "analysis_folder": analysis_folder,
                "visualization_report": visualization_report,
            }

        except Exception as e:
            self.logger.error(f"❌ Erreur pipeline: {e}")
            raise

    async def generate_visualizations(self, output_dir: str):
        """Génère toutes les visualisations avec les vraies données de tournois"""
        try:
            # Créer le dossier visualizations
            viz_dir = Path(output_dir) / "visualizations"
            viz_dir.mkdir(exist_ok=True)

            # Charger les vraies données de tournois depuis le cache
            self.logger.info(
                "🔍 Chargement des données de tournois depuis MTGODecklistCache..."
            )
            df = self._load_real_tournament_data()

            # 1. Matrice de matchups
            self.logger.info("📊 Génération de la matrice de matchups...")
            matrix_generator = MatchupMatrixGenerator()
            matrix_report = matrix_generator.generate_full_report(str(viz_dir), df)

            # 2. Graphiques de métagame
            self.logger.info("📈 Génération des graphiques de métagame...")
            charts_generator = MetagameChartsGenerator()

            # Générer tous les graphiques
            charts_result = charts_generator.generate_all_charts(df, str(viz_dir))
            charts = charts_result["charts"]

            # Sauvegarder les graphiques individuels
            chart_files = []
            for chart_name, fig in charts.items():
                chart_file = viz_dir / f"{chart_name}.html"
                fig.write_html(str(chart_file))
                chart_files.append(str(chart_file))
                self.logger.info(f"Graphique sauvegardé: {chart_file}")

            # 3. Les données sont déjà exportées par generate_all_charts
            self.logger.info("💾 Données exportées automatiquement...")

            # 4. Tableau de bord complet
            self.logger.info("🎯 Génération du tableau de bord...")
            dashboard_path = self.generate_dashboard(output_dir, df)

            # 5. Résumé
            total_files = len(chart_files) + len(matrix_report.get("files", [])) + 1
            self.logger.info(
                f"✅ {total_files} visualisations générées dans {output_dir}/"
            )

            return {
                "chart_files": chart_files,
                "matrix_report": matrix_report,
                "dashboard_path": dashboard_path,
                "total_files": total_files,
            }

        except Exception as e:
            self.logger.error(f"❌ Erreur génération visualisations: {e}")
            raise

    def _load_real_tournament_data(self):
        """Charge les données de tournois réels depuis MTGODecklistCache avec cache intelligent"""
        print(f"\n🔍 Recherche des tournois {self.format.upper()}...")

        # Patterns de recherche dynamiques (comme l'ancien système)
        patterns = self._generate_search_patterns()

        tournament_files = []
        for pattern in patterns:
            tournament_files.extend(glob.glob(pattern))

        print(f"📁 Fichiers trouvés: {len(tournament_files)}")

        if not tournament_files:
            print(f"❌ Aucun fichier de tournoi trouvé pour {self.format}")
            return pd.DataFrame()

        # Charger et filtrer les tournois avec cache intelligent
        all_decks = []
        tournaments_loaded = 0

        for file_path in tournament_files:
            try:
                decks = self._process_tournament_file(file_path)
                if decks:
                    all_decks.extend(decks)
                    tournaments_loaded += 1

            except Exception as e:
                self.logger.warning(f"Erreur lecture fichier {file_path}: {e}")
                continue

        if not all_decks:
            print(f"❌ Aucun deck trouvé pour {self.format} dans la période spécifiée")
            return pd.DataFrame()

        # Créer le DataFrame avec la même structure que l'ancien système
        df = pd.DataFrame(all_decks)
        df["tournament_date"] = pd.to_datetime(df["tournament_date"])

        print(f"\n📊 DONNÉES CHARGÉES:")
        print(f"🏆 Tournois: {tournaments_loaded}")
        print(f"🎯 Decks: {len(df)}")
        print(
            f"📅 Période réelle: {df['tournament_date'].min().strftime('%Y-%m-%d')} à {df['tournament_date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"🎲 Archétypes: {df['archetype'].nunique()}")
        print(f"🌐 Sources: {', '.join(df['tournament_source'].unique())}")

        self.logger.info(
            f"✅ {len(df)} decks chargés depuis {df['tournament_source'].nunique()} sources"
        )

        return df

    def _generate_search_patterns(self):
        """Générer les patterns de recherche pour les fichiers de tournois (comme l'ancien système)"""
        patterns = []

        # Générer les patterns pour chaque année/mois dans la période
        current_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()

        while current_date <= end_date:
            year = current_date.year
            month = f"{current_date.month:02d}"

            # Patterns pour différentes sources et structures (adaptés à la vraie structure avec jours)
            base_patterns = [
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}-*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
            ]
            patterns.extend(base_patterns)

            # Passer au mois suivant
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return patterns

    def _process_tournament_file(self, file_path):
        """Traiter un fichier de tournoi individual (comme l'ancien système)"""
        with open(file_path, "r", encoding="utf-8") as f:
            tournament_data = json.load(f)

        # Adapter à différents formats de données
        tournament_info = tournament_data.get("Tournament", tournament_data)

        # Vérifier le format STRICTEMENT (basé sur le nom du fichier ou les données)
        file_format_check = self.format.lower() in file_path.lower()
        data_format_check = False

        format_in_data = tournament_info.get("format", "").lower()
        if format_in_data:
            data_format_check = self.format.lower() in format_in_data

        # REJET STRICT : doit correspondre au format demandé
        if not file_format_check and not data_format_check:
            return []

        # REJET EXPLICIT des autres formats
        other_formats = ["modern", "legacy", "vintage", "pioneer", "pauper", "standard"]
        if self.format.lower() in other_formats:
            other_formats.remove(self.format.lower())

        for other_format in other_formats:
            if other_format in file_path.lower():
                return []

        # Extraire la date du tournoi
        tournament_date = self._extract_tournament_date(tournament_info, file_path)
        if not tournament_date:
            return []

        # Filtrer par période
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        if not (start_date <= tournament_date <= end_date):
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

        return processed_decks

    def _extract_tournament_date(self, tournament_info, file_path):
        """Extraire la date du tournoi depuis les données ou le nom du fichier (comme l'ancien système)"""
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
        """Traiter un deck individual (comme l'ancien système)"""
        # Extraire les wins/losses
        wins, losses = self._extract_results(deck)

        # Classifier l'archétype avec la nouvelle logique corrigée
        archetype = self._classify_archetype(
            deck.get("Mainboard", deck.get("mainboard", []))
        )

        # Déterminer la source avec différenciation MTGO
        source = self._determine_source(file_path, tournament_info)

        return {
            "tournament_id": tournament_info.get(
                "Uri", tournament_info.get("id", file_path)
            ),
            "tournament_name": tournament_info.get(
                "Name", tournament_info.get("name", "Tournoi")
            ),
            "tournament_date": tournament_date,
            "tournament_source": source,
            "format": self.format,
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
        """Extraire les résultats (wins/losses) d'un deck (comme l'ancien système)"""
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
            # Format direct dans les données
            wins = deck.get("wins", 0)
            losses = deck.get("losses", 0)

        return wins, losses

    def _determine_source(self, file_path, tournament_info=None):
        """Déterminer la source du tournoi avec différenciation MTGO Challenge vs League"""
        if "mtgo.com" in file_path:
            # Différencier les types de tournois MTGO
            if tournament_info:
                # Chercher l'URL dans différents champs possibles
                tournament_url = (
                    tournament_info.get("URL", "")
                    or tournament_info.get("Uri", "")
                    or tournament_info.get("TournamentID", "")
                    or tournament_info.get("ID", "")
                    or tournament_info.get("id", "")
                )

                # Analyser l'URL/ID pour déterminer le type
                tournament_str = str(tournament_url).lower()
                if "challenge" in tournament_str:
                    return "mtgo.com (Challenge)"
                elif "league" in tournament_str:
                    return "mtgo.com (League 5-0)"
                else:
                    return "mtgo.com (Other)"
            return "mtgo.com"
        elif "melee.gg" in file_path:
            return "melee.gg"
        elif "topdeck.gg" in file_path:
            return "topdeck.gg"
        elif "manatraders.com" in file_path:
            return "manatraders.com"
        else:
            return "unknown"

    def _classify_archetype(self, mainboard):
        """Classification détaillée des archétypes basée sur les cartes clés"""
        # Convertir en liste de noms de cartes
        card_names = []
        for card in mainboard:
            card_names.extend([card.get("CardName", "")] * card.get("Count", 0))

        card_names_str = " ".join(card_names).lower()

        # Classification détaillée Standard
        # Aggro
        if any(
            card in card_names_str
            for card in [
                "lightning bolt",
                "goblin guide",
                "monastery swiftspear",
                "torch the tower",
            ]
        ):
            return "Mono Red Aggro"
        elif any(
            card in card_names_str
            for card in ["elite spellbinder", "luminarch aspirant", "adeline"]
        ):
            return "Mono White Aggro"
        elif any(
            card in card_names_str
            for card in ["ragavan", "dragon rage channeler", "sprite dragon"]
        ):
            return "Izzet Aggro"

        # Control
        elif any(
            card in card_names_str
            for card in [
                "teferi hero",
                "teferi time raveler",
                "dovin's veto",
                "narset parter",
            ]
        ):
            return "Jeskai Control"
        elif any(
            card in card_names_str
            for card in ["counterspell", "wrath of god", "supreme verdict", "teferi"]
        ):
            return "Azorius Control"
        elif any(
            card in card_names_str for card in ["damnation", "thoughtseize", "liliana"]
        ):
            return "Dimir Control"

        # Midrange
        elif any(
            card in card_names_str
            for card in ["tarmogoyf", "bloodbraid elf", "wrenn and six"]
        ):
            return "Jund Midrange"
        elif any(
            card in card_names_str
            for card in ["siege rhino", "lingering souls", "path to exile"]
        ):
            return "Abzan Midrange"
        elif any(
            card in card_names_str
            for card in ["thoughtseize", "fatal push", "liliana of the veil"]
        ):
            return "Grixis Midrange"

        # Ramp
        elif any(
            card in card_names_str
            for card in [
                "overlord of the hauntwoods",
                "beza the bounding spring",
                "leyline binding",
            ]
        ):
            return "Bant Ramp"
        elif any(
            card in card_names_str
            for card in ["primeval titan", "hour of promise", "azusa"]
        ):
            return "Green Ramp"

        # Combo
        elif any(
            card in card_names_str
            for card in ["splinter twin", "deceiver exarch", "pestermite"]
        ):
            return "Splinter Twin"
        elif any(
            card in card_names_str for card in ["storm", "grapeshot", "past in flames"]
        ):
            return "Storm"
        elif any(
            card in card_names_str for card in ["devoted druid", "vizier of remedies"]
        ):
            return "Devoted Druid"

        # Archétypes spéciaux
        elif any(
            card in card_names_str
            for card in ["death shadow", "street wraith", "temur battle rage"]
        ):
            return "Death Shadow"
        elif any(
            card in card_names_str for card in ["burn", "lava spike", "rift bolt"]
        ):
            return "Burn"
        elif any(
            card in card_names_str
            for card in ["affinity", "ornithopter", "cranial plating"]
        ):
            return "Affinity"
        elif any(card in card_names_str for card in ["tron", "karn", "ugin"]):
            return "Tron"

        # Classification par couleurs si pas d'archétype spécifique
        colors = self._detect_colors(card_names)

        # RÈGLE CRITIQUE: Les archétypes monocolor génériques = "Autres"
        if len(colors) == 1:
            # En Standard: Mono Blue = "Autres"
            # En Modern: Mono Red = "Autres"
            # Tous les autres monocolor aussi = "Autres"
            return "Autres"
        elif len(colors) == 2:
            color_pairs = {
                frozenset(["W", "U"]): "Azorius",
                frozenset(["W", "B"]): "Orzhov",
                frozenset(["W", "R"]): "Boros",
                frozenset(["W", "G"]): "Selesnya",
                frozenset(["U", "B"]): "Dimir",
                frozenset(["U", "R"]): "Izzet",
                frozenset(["U", "G"]): "Simic",
                frozenset(["B", "R"]): "Rakdos",
                frozenset(["B", "G"]): "Golgari",
                frozenset(["R", "G"]): "Gruul",
            }
            return f"{color_pairs.get(frozenset(colors), 'Multicolor')} Deck"
        elif len(colors) == 3:
            color_triples = {
                frozenset(["W", "U", "B"]): "Esper",
                frozenset(["W", "U", "R"]): "Jeskai",
                frozenset(["W", "U", "G"]): "Bant",
                frozenset(["W", "B", "R"]): "Mardu",
                frozenset(["W", "B", "G"]): "Abzan",
                frozenset(["W", "R", "G"]): "Naya",
                frozenset(["U", "B", "R"]): "Grixis",
                frozenset(["U", "B", "G"]): "Sultai",
                frozenset(["U", "R", "G"]): "Temur",
                frozenset(["B", "R", "G"]): "Jund",
            }
            return f"{color_triples.get(frozenset(colors), 'Three-Color')} Deck"
        else:
            return "Autres"

    def _detect_colors(self, card_names):
        """Détecte les couleurs d'un deck basé sur les noms de cartes"""
        colors = set()

        # Cartes de base et terrains
        white_cards = [
            "plains",
            "azorius",
            "boros",
            "orzhov",
            "selesnya",
            "jeskai",
            "esper",
            "mardu",
            "abzan",
            "naya",
            "bant",
        ]
        blue_cards = [
            "island",
            "azorius",
            "dimir",
            "izzet",
            "simic",
            "jeskai",
            "esper",
            "grixis",
            "sultai",
            "temur",
            "bant",
        ]
        black_cards = [
            "swamp",
            "orzhov",
            "dimir",
            "rakdos",
            "golgari",
            "mardu",
            "esper",
            "grixis",
            "abzan",
            "sultai",
            "jund",
        ]
        red_cards = [
            "mountain",
            "boros",
            "izzet",
            "rakdos",
            "gruul",
            "jeskai",
            "mardu",
            "grixis",
            "naya",
            "temur",
            "jund",
        ]
        green_cards = [
            "forest",
            "selesnya",
            "simic",
            "golgari",
            "gruul",
            "abzan",
            "naya",
            "bant",
            "sultai",
            "temur",
            "jund",
        ]

        # Cartes spécifiques par couleur
        white_spells = [
            "wrath",
            "path to exile",
            "swords to plowshares",
            "counterspell",
            "teferi",
            "elspeth",
        ]
        blue_spells = [
            "counterspell",
            "force of will",
            "brainstorm",
            "ponder",
            "jace",
            "teferi",
        ]
        black_spells = [
            "thoughtseize",
            "fatal push",
            "liliana",
            "dark ritual",
            "cabal therapy",
        ]
        red_spells = [
            "lightning bolt",
            "lava spike",
            "goblin guide",
            "monastery swiftspear",
            "ragavan",
        ]
        green_spells = [
            "tarmogoyf",
            "noble hierarch",
            "birds of paradise",
            "primeval titan",
            "green sun",
        ]

        card_names_str = " ".join(card_names).lower()

        # Vérifier chaque couleur
        if any(card in card_names_str for card in white_cards + white_spells):
            colors.add("W")
        if any(card in card_names_str for card in blue_cards + blue_spells):
            colors.add("U")
        if any(card in card_names_str for card in black_cards + black_spells):
            colors.add("B")
        if any(card in card_names_str for card in red_cards + red_spells):
            colors.add("R")
        if any(card in card_names_str for card in green_cards + green_spells):
            colors.add("G")

        return colors

    def _parse_result(self, result):
        """Parse les résultats pour extraire wins/losses"""
        if not result:
            return 0, 0

        # Patterns courants
        if "Place" in result:
            # Approximation basée sur la position
            if "1st" in result:
                return 6, 1  # Gagnant probable
            elif "2nd" in result:
                return 5, 2  # Finaliste
            elif "3rd" in result or "4th" in result:
                return 4, 3  # Top 4
            else:
                return 3, 4  # Autres

        # Pattern X-Y
        import re

        match = re.search(r"(\d+)-(\d+)", result)
        if match:
            return int(match.group(1)), int(match.group(2))

        # Défaut
        return 3, 3

    def generate_dashboard(self, output_dir: str, df: pd.DataFrame):
        """Génère le tableau de bord HTML complet"""
        try:
            from datetime import datetime

            # Statistiques générales
            total_tournaments = df["tournament_id"].nunique()
            total_players = len(df)
            total_matches = df["matches_played"].sum()
            archetypes = sorted(df["archetype"].unique())

            # Générer les badges des sources
            sources = df["tournament_source"].unique()
            source_badges = ""
            for source in sources:
                if "melee.gg" in source:
                    badge_color = "#4ECDC4"  # Turquoise
                elif "Challenge" in source:
                    badge_color = "#e74c3c"  # Rouge
                elif "League" in source:
                    badge_color = "#27ae60"  # Vert
                else:
                    badge_color = "#3498db"  # Bleu

                source_badges += f'<span style="background-color: {badge_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin: 0 0.5rem;">{source}</span>'

            # Utiliser les paramètres du pipeline
            start_date = getattr(self, "start_date", "2025-07-02")
            end_date = getattr(self, "end_date", "2025-07-12")
            format_name = getattr(self, "format", "Standard")

            # Template HTML complet avec tous les graphiques
            html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Analyse {format_name} ({start_date} à {end_date})</title>
    <style>
        :root {{
            --primary: #762a83; --secondary: #1b7837; --accent: #4ECDC4;
            --bg-light: #f8f9fa; --bg-white: #ffffff; --text-dark: #2c3e50;
            --shadow: 0 2px 10px rgba(0,0,0,0.1); --border-radius: 12px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
               background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}

        .header {{ background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                  color: white; padding: 3rem 0; text-align: center; }}
        .header h1 {{ font-size: 3rem; font-weight: 300; margin-bottom: 1rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}

        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}

        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                      gap: 2rem; margin: 2rem 0 3rem; }}
        .stat-card {{ background: var(--bg-white); padding: 2rem; border-radius: var(--border-radius);
                     box-shadow: var(--shadow); text-align: center; transition: transform 0.3s; }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card.clickable {{ cursor: pointer; transition: all 0.3s ease; }}
        .stat-card.clickable:hover {{
            transform: translateY(-8px);
            box-shadow: 0 8px 25px rgba(118, 42, 131, 0.2);
            border: 2px solid var(--primary);
        }}
        .stat-hint {{
            font-size: 0.9rem; color: var(--primary); margin-top: 0.5rem;
            opacity: 0.7; font-weight: 500;
        }}
        .stat-number {{ font-size: 3rem; font-weight: bold; color: var(--primary); }}
        .stat-label {{ font-size: 1.1rem; color: var(--text-dark); margin-top: 0.5rem; }}

        .viz-grid {{ display: grid; gap: 2rem; }}
        .viz-card {{ background: var(--bg-white); border-radius: var(--border-radius);
                    box-shadow: var(--shadow); overflow: hidden; }}
        .viz-header {{ background: var(--bg-light); padding: 1.5rem; border-bottom: 1px solid #eee; }}
        .viz-title {{ font-size: 1.4rem; font-weight: 600; color: var(--text-dark); }}
        .viz-content {{ height: 600px; }}
        .viz-iframe {{ width: 100%; height: 100%; border: none; }}

        .footer {{ background: var(--text-dark); color: white; text-align: center;
                  padding: 2rem; margin-top: 3rem; }}
        .footer p {{ opacity: 0.8; }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .container {{ padding: 1rem; }}
            .viz-content {{ height: 400px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics</h1>
        <p>Analyse complète du métagame {format_name} • {start_date} à {end_date}</p>
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <span style="font-size: 0.9rem; color: white;">Sources des données :</span>
            {source_badges}
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card clickable" onclick="window.open('{format_name.lower()}_{start_date}_{end_date}_tournaments_list.html', '_blank')">
                <div class="stat-number">{total_tournaments}</div>
                <div class="stat-label">Tournois analysés</div>
                <div class="stat-hint">🔍 Cliquez pour voir la liste</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_players}</div>
                <div class="stat-label">Joueurs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_matches}</div>
                <div class="stat-label">Matchs joués</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(archetypes)}</div>
                <div class="stat-label">Archétypes identifiés</div>
            </div>
        </div>

        <div class="viz-grid">
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🥧 Répartition du Métagame</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/metagame_pie.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">📊 Archétypes Principaux</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/main_archetypes_bar.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🔥 Matrice de Matchups</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/matchup_matrix.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🎯 Winrates avec Intervalles de Confiance</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/winrate_confidence.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🏆 Classification par Tiers</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/tiers_scatter.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">💫 Winrate vs Présence</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/bubble_winrate_presence.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🌟 Top Performers</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/top_5_0.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">📈 Évolution Temporelle</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/archetype_evolution.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🔍 Sources de Données</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/data_sources_pie.html" class="viz-iframe"></iframe>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>🎯 Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} • Données 100% réelles • Pipeline automatique Manalytics</p>
        <p>📊 Tous les graphiques sont interactifs • Cliquez et explorez les données</p>
    </div>
</body>
</html>
            """

            # Générer la liste des tournois
            self.generate_tournaments_list(output_dir, df)

            # Sauvegarder le dashboard avec le nom demandé par l'utilisateur
            prefix = f"{format_name.lower()}_{start_date}_{end_date}"
            dashboard_filename = f"{prefix}.html"
            dashboard_path = Path(output_dir) / dashboard_filename
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(html_template)

            # Créer aussi index.html pour compatibilité (sans préfixe)
            legacy_index_path = Path(output_dir) / "index.html"
            with open(legacy_index_path, "w", encoding="utf-8") as f:
                f.write(html_template)

            self.logger.info(f"✅ Dashboard complet créé: {dashboard_path}")
            self.logger.info(f"✅ Index créé pour compatibilité: index.html")
            return str(dashboard_path)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération dashboard: {e}")
            raise

    def generate_tournaments_list(self, output_dir: str, df: pd.DataFrame):
        """Génère la liste des tournois triée par source et date"""
        try:
            # Préparer les données des tournois
            tournaments_data = (
                df.groupby(["tournament_source", "tournament_date", "tournament_id"])
                .size()
                .reset_index(name="deck_count")
            )
            tournaments_data = tournaments_data.sort_values(
                ["tournament_source", "tournament_date"]
            )

            # Utiliser les paramètres du pipeline
            start_date = getattr(self, "start_date", "2025-07-02")
            end_date = getattr(self, "end_date", "2025-07-12")
            format_name = getattr(self, "format", "Standard")

            # Créer le HTML pour la liste des tournois
            tournaments_html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liste des Tournois - {format_name} ({start_date} à {end_date})</title>
    <style>
        :root {{
            --primary: #762a83; --secondary: #1b7837; --accent: #4ECDC4;
            --bg-light: #f8f9fa; --bg-white: #ffffff; --text-dark: #2c3e50;
            --shadow: 0 2px 10px rgba(0,0,0,0.1); --border-radius: 12px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white; padding: 2rem; border-radius: var(--border-radius);
            text-align: center; margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.1rem; opacity: 0.9; }}

                 .back-button {{
             background: var(--accent); color: white; padding: 0.8rem 1.5rem;
             border: none; border-radius: var(--border-radius); cursor: pointer;
             font-size: 1rem; margin-bottom: 2rem; transition: all 0.3s;
             margin-right: 1rem;
         }}
         .back-button:hover {{ background: #3ba99c; transform: translateY(-2px); }}

         .export-button {{
             background: var(--primary); color: white; padding: 0.8rem 1.5rem;
             border: none; border-radius: var(--border-radius); cursor: pointer;
             font-size: 1rem; margin-bottom: 2rem; transition: all 0.3s;
             display: inline-flex; align-items: center; gap: 0.5rem;
         }}
         .export-button:hover {{
             background: var(--secondary); transform: translateY(-2px);
             box-shadow: 0 4px 12px rgba(118, 42, 131, 0.3);
         }}

        .tournaments-container {{
            background: var(--bg-white); border-radius: var(--border-radius);
            box-shadow: var(--shadow); overflow: hidden;
        }}

        .tournaments-table {{
            width: 100%; border-collapse: collapse;
        }}
        .tournaments-table th {{
            background: var(--bg-light); padding: 1rem; text-align: left;
            font-weight: 600; color: var(--text-dark); border-bottom: 2px solid #eee;
        }}
        .tournaments-table td {{
            padding: 1rem; border-bottom: 1px solid #eee;
        }}
        .tournaments-table tr:hover {{ background: #f8f9fa; }}

                 .source-badge {{
             background: var(--primary); color: white; padding: 0.3rem 0.8rem;
             border-radius: 20px; font-size: 0.9rem; font-weight: 500;
         }}
         .source-meleegg {{ background: #4ECDC4; }}
         .source-mtgocom-challenge {{ background: #e74c3c; }}
         .source-mtgocom-league-5-0 {{ background: #27ae60; }}
         .source-mtgocom-other {{ background: #95a5a6; }}
         .source-topdeckgg {{ background: #762a83; }}

                 .deck-count {{
             background: var(--bg-light); padding: 0.4rem 0.8rem;
             border-radius: var(--border-radius); font-weight: 600;
             color: var(--primary);
         }}

         .tournament-link {{
             color: var(--primary); text-decoration: none; font-weight: 500;
             padding: 0.5rem 1rem; border-radius: var(--border-radius);
             background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
             border: 1px solid #dee2e6; transition: all 0.3s ease;
             display: inline-flex; align-items: center; gap: 0.5rem;
         }}
         .tournament-link:hover {{
             background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
             color: white; transform: translateY(-2px);
             box-shadow: 0 4px 12px rgba(118, 42, 131, 0.3);
         }}
         .external-icon {{
             font-size: 0.8rem; opacity: 0.7; transition: opacity 0.3s;
         }}
         .tournament-link:hover .external-icon {{ opacity: 1; }}

        .stats-summary {{
            background: var(--bg-light); padding: 1.5rem; margin-bottom: 2rem;
            border-radius: var(--border-radius); text-align: center;
        }}
        .stats-summary h3 {{ color: var(--primary); margin-bottom: 1rem; }}
        .stats-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}
        .stat-item {{
            background: var(--bg-white); padding: 1rem; border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: var(--primary); }}
        .stat-label {{ font-size: 0.9rem; color: var(--text-dark); }}

        @media (max-width: 768px) {{
            .tournaments-table {{ font-size: 0.9rem; }}
            .tournaments-table th, .tournaments-table td {{ padding: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Liste des Tournois</h1>
        <p>Analyse {format_name} • {start_date} à {end_date}</p>
    </div>

     <div style="display: flex; align-items: center; margin-bottom: 2rem;">
         <button class="back-button" onclick="window.location.href='{format_name.lower()}_{start_date}_{end_date}.html'">← Retour au Dashboard</button>
         <button class="export-button" onclick="exportToCSV()">📥 Exporter en CSV (en travaux)</button>
     </div>

    <div class="stats-summary">
        <h3>Résumé des Sources</h3>
        <div class="stats-grid">
"""

            # Ajouter les statistiques par source
            source_stats = (
                tournaments_data.groupby("tournament_source")
                .agg({"tournament_id": "count", "deck_count": "sum"})
                .reset_index()
            )

            for _, row in source_stats.iterrows():
                # Créer une classe CSS sûre
                source_name = row["tournament_source"].lower()
                source_class = f"source-{source_name.replace('.', '').replace(' ', '-').replace('(', '').replace(')', '').replace('-5-0', '-5-0')}"
                tournaments_html += f"""
            <div class="stat-item">
                <div class="stat-number">{row['tournament_id']}</div>
                <div class="stat-label">{row['tournament_source']}</div>
                <div style="font-size: 0.8rem; color: #666;">{row['deck_count']} decks</div>
            </div>
"""

            tournaments_html += """
        </div>
    </div>

    <div class="tournaments-container">
        <table class="tournaments-table">
            <thead>
                <tr>
                    <th>Source</th>
                    <th>Date</th>
                    <th>Tournoi</th>
                    <th>Decks</th>
                </tr>
            </thead>
            <tbody>
"""

            # Ajouter les lignes des tournois
            for _, row in tournaments_data.iterrows():
                # Créer une classe CSS sûre pour le badge
                source_name = row["tournament_source"].lower()
                source_class = f"source-{source_name.replace('.', '').replace(' ', '-').replace('(', '').replace(')', '').replace('-5-0', '-5-0')}"
                date_formatted = row["tournament_date"].strftime("%d/%m/%Y")

                # Créer le lien cliquable pour le tournoi
                tournament_url = row["tournament_id"]
                if tournament_url.startswith("http"):
                    tournament_link = f'<a href="{tournament_url}" target="_blank" class="tournament-link">🔗 Voir le tournoi <span class="external-icon">↗</span></a>'
                else:
                    tournament_link = tournament_url

                tournaments_html += f"""
                <tr>
                    <td><span class="source-badge {source_class}">{row['tournament_source']}</span></td>
                    <td>{date_formatted}</td>
                    <td>{tournament_link}</td>
                    <td><span class="deck-count">{row['deck_count']}</span></td>
                </tr>
"""

            tournaments_html += """
            </tbody>
        </table>
    </div>

         <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #666;">
         <p>🎯 Données 100% réelles • Triées par source puis par date</p>
     </div>

     <script>
         function exportToCSV() {{
             // Récupérer les données du tableau
             const table = document.querySelector('.tournaments-table');
             let csv = [];

             // En-têtes
             const headers = [];
             table.querySelectorAll('thead th').forEach(th => {{
                 headers.push(th.textContent.trim());
             }});
             csv.push(headers.join(','));

             // Données
             table.querySelectorAll('tbody tr').forEach(tr => {{
                 const row = [];
                 tr.querySelectorAll('td').forEach((td, index) => {{
                     if (index === 0) {{
                         // Source - extraire le texte du badge
                         const badge = td.querySelector('.source-badge');
                         row.push(badge ? badge.textContent.trim() : td.textContent.trim());
                     }} else if (index === 2) {{
                         // Tournoi - extraire l'URL du lien
                         const link = td.querySelector('a');
                         row.push(link ? link.href : td.textContent.trim());
                     }} else {{
                         // Autres colonnes - texte brut
                         row.push(td.textContent.trim());
                     }}
                 }});
                 csv.push(row.join(','));
             }});

             // Créer et télécharger le fichier
             const csvContent = csv.join('\\n');
             const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
             const link = document.createElement('a');

             if (link.download !== undefined) {{
                 const url = URL.createObjectURL(blob);
                 link.setAttribute('href', url);
                 link.setAttribute('download', 'tournois_{format_name.lower()}_{start_date}_{end_date}.csv');
                 link.style.visibility = 'hidden';
                 document.body.appendChild(link);
                 link.click();
                 document.body.removeChild(link);
             }}
         }}
     </script>
 </body>
 </html>
"""

            # Sauvegarder le fichier avec préfixe
            prefix = f"{format_name.lower()}_{start_date}_{end_date}"
            tournaments_filename = f"{prefix}_tournaments_list.html"
            tournaments_path = Path(output_dir) / tournaments_filename
            with open(tournaments_path, "w", encoding="utf-8") as f:
                f.write(tournaments_html)

            self.logger.info(f"✅ Liste des tournois créée: {tournaments_filename}")
            return str(tournaments_path)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération liste tournois: {e}")
            raise
