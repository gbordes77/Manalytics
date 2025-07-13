"""
Manalytics Orchestrator - Phase 3 (Visualizations only)
Simplified pipeline with automatic chart generation
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
    """Phase 3 Orchestrator - Visualizations only"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def run_pipeline(self, format: str, start_date: str, end_date: str):
        """Phase 3 pipeline with automatic visualization generation"""
        try:
            # Create dated analysis folder in Analyses/
            analysis_folder = f"{format.lower()}_analysis_{start_date}_{end_date}"
            analyses_dir = Path("Analyses")
            analyses_dir.mkdir(exist_ok=True)
            output_dir = analyses_dir / analysis_folder
            output_dir.mkdir(exist_ok=True)

            self.logger.info(f"🚀 Starting complete pipeline for {format}")
            self.logger.info(f"📁 Analysis folder: {analysis_folder}")

            # Store parameters for dashboard
            self.format = format
            self.start_date = start_date
            self.end_date = end_date

            # 1. Generate visualizations
            self.logger.info("🎨 Generating visualizations...")
            visualization_report = await self.generate_visualizations(str(output_dir))

            # 2. Final summary
            self.logger.info(f"✅ Pipeline completed successfully in {analysis_folder}!")

            return {
                "analysis_folder": analysis_folder,
                "visualization_report": visualization_report,
                "main_filename": f"{format.lower()}_{start_date}_{end_date}.html",
                "format": format,
                "start_date": start_date,
                "end_date": end_date,
            }

        except Exception as e:
            self.logger.error(f"❌ Pipeline error: {e}")
            raise

    async def generate_visualizations(self, output_dir: str):
        """Generate all visualizations with real tournament data"""
        try:
            # Create visualizations folder
            viz_dir = Path(output_dir) / "visualizations"
            viz_dir.mkdir(exist_ok=True)

            # Load real tournament data from cache
            self.logger.info("🔍 Loading tournament data from MTGODecklistCache...")
            df = self._load_real_tournament_data()

            # 1. Matchup matrix
            self.logger.info("📊 Generating matchup matrix...")
            matrix_generator = MatchupMatrixGenerator()
            matrix_report = matrix_generator.generate_full_report(str(viz_dir), df)

            # 2. Metagame charts
            self.logger.info("📈 Generating metagame charts...")
            charts_generator = MetagameChartsGenerator()

            # Generate all charts
            charts_result = charts_generator.generate_all_charts(df, str(viz_dir))
            charts = charts_result["charts"]

            # Save individual charts
            chart_files = []
            for chart_name, fig in charts.items():
                chart_file = viz_dir / f"{chart_name}.html"
                fig.write_html(str(chart_file))
                chart_files.append(str(chart_file))
                self.logger.info(f"Chart saved: {chart_file}")

            # 3. Data is already exported by generate_all_charts
            self.logger.info("💾 Data exported automatically...")

            # 4. Complete dashboard
            self.logger.info("🎯 Generating dashboard...")
            dashboard_path = self.generate_dashboard(output_dir, df)

            # 5. Summary
            total_files = len(chart_files) + len(matrix_report.get("files", [])) + 1
            self.logger.info(
                f"✅ {total_files} visualizations generated in {output_dir}/"
            )

            return {
                "chart_files": chart_files,
                "matrix_report": matrix_report,
                "dashboard_path": dashboard_path,
                "total_files": total_files,
            }

        except Exception as e:
            self.logger.error(f"❌ Error generating visualizations: {e}")
            raise

    def _load_real_tournament_data(self):
        """Load real tournament data from MTGODecklistCache with intelligent caching"""
        print(f"\n🔍 Searching for {self.format.upper()} tournaments...")

        # Dynamic search patterns (like the old system)
        patterns = self._generate_search_patterns()

        tournament_files = []
        for pattern in patterns:
            tournament_files.extend(glob.glob(pattern))

        print(f"📁 Files found: {len(tournament_files)}")

        if not tournament_files:
            print(f"❌ No tournament files found for {self.format}")
            return pd.DataFrame()

        # Load and filter tournaments with intelligent caching
        all_decks = []
        tournaments_loaded = 0

        for file_path in tournament_files:
            try:
                decks = self._process_tournament_file(file_path)
                if decks:
                    all_decks.extend(decks)
                    tournaments_loaded += 1

            except Exception as e:
                self.logger.warning(f"Error reading file {file_path}: {e}")
                continue

        if not all_decks:
            print(f"❌ No decks found for {self.format} in the specified period")
            return pd.DataFrame()

        # Create DataFrame with the same structure as the old system
        df = pd.DataFrame(all_decks)
        df["tournament_date"] = pd.to_datetime(df["tournament_date"])

        print(f"\n📊 DATA LOADED:")
        print(f"🏆 Tournaments: {tournaments_loaded}")
        print(f"🎯 Decks: {len(df)}")
        print(
            f"📅 Actual period: {df['tournament_date'].min().strftime('%Y-%m-%d')} to {df['tournament_date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"🎲 Archetypes: {df['archetype'].nunique()}")
        print(f"🌐 Sources: {', '.join(df['tournament_source'].unique())}")

        self.logger.info(
            f"✅ {len(df)} decks loaded from {df['tournament_source'].nunique()} sources"
        )

        return df

    def _generate_search_patterns(self):
        """Generate search patterns for tournament files (like the old system)"""
        patterns = []

        # Generate patterns for each year/month in the period
        current_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()

        while current_date <= end_date:
            year = current_date.year
            month = f"{current_date.month:02d}"

            # Patterns for different sources and structures (adapted to real structure with days)
            base_patterns = [
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}-*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
            ]
            patterns.extend(base_patterns)

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return patterns

    def _process_tournament_file(self, file_path):
        """Process individual tournament file (like the old system)"""
        with open(file_path, "r", encoding="utf-8") as f:
            tournament_data = json.load(f)

        # Adapt to different data formats
        tournament_info = tournament_data.get("Tournament", tournament_data)

        # Check format STRICTLY (based on filename or data)
        file_format_check = self.format.lower() in file_path.lower()
        data_format_check = False

        format_in_data = tournament_info.get("format", "").lower()
        if format_in_data:
            data_format_check = self.format.lower() in format_in_data

        # STRICT REJECTION: must match requested format
        if not file_format_check and not data_format_check:
            return []

        # EXPLICIT REJECTION of other formats
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
        """Extract tournament date from data or filename (like the old system)"""
        # Try to extract from data
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

        # Extract from filename (ex: tournament-2025-05-01.json)
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

        # Classify archetype with the new corrected logic
        archetype = self._classify_archetype(
            deck.get("Mainboard", deck.get("mainboard", []))
        )

        # Determine source with MTGO differentiation
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
            # Format directly in data
            wins = deck.get("wins", 0)
            losses = deck.get("losses", 0)

        return wins, losses

    def _determine_source(self, file_path, tournament_info=None):
        """Determine tournament source with MTGO Challenge vs League differentiation"""
        if "mtgo.com" in file_path:
            # Differentiate MTGO tournament types
            if tournament_info:
                # Search for URL in different possible fields
                tournament_url = (
                    tournament_info.get("URL", "")
                    or tournament_info.get("Uri", "")
                    or tournament_info.get("TournamentID", "")
                    or tournament_info.get("ID", "")
                    or tournament_info.get("id", "")
                )

                # Analyze URL/ID to determine type
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
        """Detailed archetype classification based on key cards"""
        # Convert to list of card names
        card_names = []
        for card in mainboard:
            card_names.extend([card.get("CardName", "")] * card.get("Count", 0))

        card_names_str = " ".join(card_names).lower()

        # Detailed Standard classification
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

        # NOTE: Removed non-Standard archetypes (Storm, Splinter Twin, Death Shadow, Burn, Affinity, Tron, etc.)
        # These decks will be classified as "Others" since they don't exist in Standard format

        # Color-based classification if no specific archetype
        colors = self._detect_colors(card_names)

        # CRITICAL RULE: Generic monocolor archetypes = "Others"
        if len(colors) == 1:
            # In Standard: Mono Blue = "Others"
            # In Modern: Mono Red = "Others"
            # All other monocolor also = "Others"
            return "Others"
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
        """Detect deck colors based on card names"""
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
            # Position-based approximation
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

            # Generate source badges
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - {format_name} Analysis ({start_date} to {end_date})</title>
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
        <p>Complete analysis of {format_name} metagame • {start_date} to {end_date}</p>
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <span style="font-size: 0.9rem; color: white;">Data sources:</span>
            {source_badges}
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card clickable" onclick="window.open('{format_name.lower()}_{start_date}_{end_date}_tournaments_list.html', '_blank')">
                <div class="stat-number">{total_tournaments}</div>
                <div class="stat-label">Tournaments analyzed</div>
                <div class="stat-hint">🔍 Click to view list</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_players}</div>
                <div class="stat-label">Players</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_matches}</div>
                <div class="stat-label">Matches played</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(archetypes)}</div>
                <div class="stat-label">Archetypes identified</div>
            </div>
        </div>

        <div class="viz-grid">
            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🥧 Metagame Distribution</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/metagame_pie.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">📊 Main Archetypes</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/main_archetypes_bar.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🔥 Matchup Matrix</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/matchup_matrix.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🎯 Winrates with Confidence Intervals</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/winrate_confidence.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🏆 Tier Classification</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/tiers_scatter.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">💫 Winrate vs Presence</h3>
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
                    <h3 class="viz-title">📈 Temporal Evolution</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/archetype_evolution.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🔍 Data Sources</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/data_sources_pie.html" class="viz-iframe"></iframe>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>🎯 Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} • 100% real data • Automated Manalytics pipeline</p>
        <p>📊 All charts are interactive • Click and explore the data</p>
    </div>
</body>
</html>
            """

            # Generate tournament list
            self.generate_tournaments_list(output_dir, df)

            # Save dashboard with user-requested name
            prefix = f"{format_name.lower()}_{start_date}_{end_date}"
            dashboard_filename = f"{prefix}.html"
            dashboard_path = Path(output_dir) / dashboard_filename
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(html_template)

            self.logger.info(f"✅ Complete dashboard created: {dashboard_path}")
            return str(dashboard_path)

        except Exception as e:
            self.logger.error(f"❌ Dashboard generation error: {e}")
            raise

    def generate_tournaments_list(self, output_dir: str, df: pd.DataFrame):
        """Generate tournament list sorted by source and date"""
        try:
            # Prepare tournament data
            tournaments_data = (
                df.groupby(["tournament_source", "tournament_date", "tournament_id"])
                .size()
                .reset_index(name="deck_count")
            )
            tournaments_data = tournaments_data.sort_values(
                ["tournament_source", "tournament_date"]
            )

            # Use pipeline parameters
            start_date = getattr(self, "start_date", "2025-07-02")
            end_date = getattr(self, "end_date", "2025-07-12")
            format_name = getattr(self, "format", "Standard")

            # Create HTML for tournament list
            tournaments_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournament List - {format_name} ({start_date} to {end_date})</title>
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
        <h1>📋 Tournament List</h1>
        <p>Analysis {format_name} • {start_date} to {end_date}</p>
    </div>

     <div style="display: flex; align-items: center; margin-bottom: 2rem;">
         <button class="back-button" onclick="window.location.href='{format_name.lower()}_{start_date}_{end_date}.html'">← Back to Dashboard</button>
         <button class="export-button" onclick="exportToCSV()">📥 Export to CSV (in progress)</button>
     </div>

    <div class="stats-summary">
        <h3>Source Summary</h3>
        <div class="stats-grid">
"""

            # Add statistics by source
            source_stats = (
                tournaments_data.groupby("tournament_source")
                .agg({"tournament_id": "count", "deck_count": "sum"})
                .reset_index()
            )

            for _, row in source_stats.iterrows():
                # Create safe CSS class
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
                    <th>Tournament</th>
                    <th>Decks</th>
                </tr>
            </thead>
            <tbody>
"""

            # Add tournament rows
            for _, row in tournaments_data.iterrows():
                # Create safe CSS class for badge
                source_name = row["tournament_source"].lower()
                source_class = f"source-{source_name.replace('.', '').replace(' ', '-').replace('(', '').replace(')', '').replace('-5-0', '-5-0')}"
                date_formatted = row["tournament_date"].strftime("%Y-%m-%d")

                # Create clickable link for tournament
                tournament_url = row["tournament_id"]
                if tournament_url.startswith("http"):
                    tournament_link = f'<a href="{tournament_url}" target="_blank" class="tournament-link">🔗 View tournament <span class="external-icon">↗</span></a>'
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
         <p>🎯 100% real data • Sorted by source then by date</p>
     </div>

     <script>
         function exportToCSV() {{
             // Get table data
             const table = document.querySelector('.tournaments-table');
             let csv = [];

             // Headers
             const headers = [];
             table.querySelectorAll('thead th').forEach(th => {{
                 headers.push(th.textContent.trim());
             }});
             csv.push(headers.join(','));

             // Data
             table.querySelectorAll('tbody tr').forEach(tr => {{
                 const row = [];
                 tr.querySelectorAll('td').forEach((td, index) => {{
                     if (index === 0) {{
                         // Source - extract badge text
                         const badge = td.querySelector('.source-badge');
                         row.push(badge ? badge.textContent.trim() : td.textContent.trim());
                     }} else if (index === 2) {{
                         // Tournament - extract URL from link
                         const link = td.querySelector('a');
                         row.push(link ? link.href : td.textContent.trim());
                     }} else {{
                         // Other columns - plain text
                         row.push(td.textContent.trim());
                     }}
                 }});
                 csv.push(row.join(','));
             }});

             // Create and download file
             const csvContent = csv.join('\\n');
             const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
             const link = document.createElement('a');

             if (link.download !== undefined) {{
                 const url = URL.createObjectURL(blob);
                 link.setAttribute('href', url);
                 link.setAttribute('download', 'tournaments_{format_name.lower()}_{start_date}_{end_date}.csv');
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

            # Save file with prefix
            prefix = f"{format_name.lower()}_{start_date}_{end_date}"
            tournaments_filename = f"{prefix}_tournaments_list.html"
            tournaments_path = Path(output_dir) / tournaments_filename
            with open(tournaments_path, "w", encoding="utf-8") as f:
                f.write(tournaments_html)

            self.logger.info(f"✅ Tournament list created: {tournaments_filename}")
            return str(tournaments_path)

        except Exception as e:
            self.logger.error(f"❌ Error generating tournament list: {e}")
            raise
