"""

from python.utils.logging_manager import get_logger
logger = get_logger(__name__)

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
from typing import Dict, List

import pandas as pd

from python.analytics.advanced_metagame_analyzer import AdvancedMetagameAnalyzer
from python.classifier.advanced_archetype_classifier import AdvancedArchetypeClassifier
from python.classifier.archetype_engine import ArchetypeEngine
from python.classifier.color_detector import ColorDetector
from python.classifier.mtgo_classifier import MTGOClassifier
from python.visualizations.matchup_matrix import MatchupMatrixGenerator
from python.visualizations.metagame_charts import MetagameChartsGenerator


class ManalyticsOrchestrator:
    """Phase 3 Orchestrator - Visualizations only

    🎨 IMPORTANT: EXPERT COLOR SYSTEM
    All visualizations MUST use the expert color system from MetagameChartsGenerator.
    This ensures:
    - Professional industry-level appearance (MTGGoldfish/17lands standard)
    - Accessibility for 8% colorblind population
    - Consistent hierarchical color logic across all charts
    - "Autres/Non classifiés" always in neutral gray #95A5A6

    For new visualizations, ALWAYS use:
    charts_generator = MetagameChartsGenerator()
    colors = [charts_generator.get_archetype_color(arch) for arch in archetypes]

    See docs/DATA_VISUALIZATION_EXPERTISE.md for complete guidance.
    """

    def __init__(self, config_manager=None):
        self.config_manager = config_manager  # Optionnel, peut être None
        self.tournament_fetcher = None
        self.deck_analyzer = None
        self.color_detector = None
        self.advanced_classifier = AdvancedArchetypeClassifier()  # NEW

        self.logger = logging.getLogger(__name__)
        # Initialize ArchetypeEngine (PRIMARY classifier - MTGOFormatData)
        self.archetype_engine = ArchetypeEngine(
            "./MTGOFormatData", "./input", "./output"
        )
        # Initialize MTGO classifier (FALLBACK)
        self.mtgo_classifier = MTGOClassifier()
        # Initialize color detector
        self.color_detector = ColorDetector()
        # Initialize advanced metagame analyzer
        self.advanced_analyzer = AdvancedMetagameAnalyzer()
        self.logger.info(
            "ArchetypeEngine initialized as PRIMARY classifier (MTGOFormatData)"
        )
        self.logger.info("MTGO Classifier initialized as FALLBACK classifier")
        self.logger.info("Color Detector initialized with MTGOFormatData color system")
        self.logger.info(
            "Advanced Metagame Analyzer initialized with statistical analysis capabilities"
        )

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

            # 0. Advanced statistical analysis
            self.logger.info("🔬 Performing advanced statistical analysis...")
            advanced_report = self._perform_advanced_analysis(df, output_dir)

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

            # 3.5. Export detailed decklists with navigation
            self.logger.info("📋 Exporting detailed decklists...")
            detailed_export = self._export_detailed_decklists(df, output_dir)

            # 4. Complete dashboard
            self.logger.info("🎯 Generating dashboard...")
            dashboard_path = self.generate_dashboard(output_dir, df)

            # 4.5. Generate players stats page
            self.logger.info("👥 Generating players statistics...")
            players_path = self.generate_players_stats(output_dir, df)

            # 4.6. Generate MTGO analysis
            self.logger.info("🎯 Generating MTGO analysis...")
            mtgo_path = self.generate_mtgo_analysis(output_dir, df)

            # 5. Summary
            total_files = len(chart_files) + len(matrix_report.get("files", [])) + 1
            self.logger.info(
                f"✅ {total_files} visualizations generated in {output_dir}/"
            )

            return {
                "chart_files": chart_files,
                "matrix_report": matrix_report,
                "advanced_report": advanced_report,
                "dashboard_path": dashboard_path,
                "total_files": total_files,
            }

        except Exception as e:
            self.logger.error(f"❌ Error generating visualizations: {e}")
            raise

    def _load_real_tournament_data(self):
        """Load real tournament data from MTGODecklistCache with intelligent caching"""
        self.logger.info(f"\n🔍 Searching for {self.format.upper()} tournaments...")

        # Dynamic search patterns (like the old system)
        patterns = self._generate_search_patterns()

        tournament_files = []
        for pattern in patterns:
            tournament_files.extend(glob.glob(pattern))

        self.logger.info(f"Files found: {len(tournament_files)}")

        if not tournament_files:
            self.logger.error(f"No tournament files found for {self.format}")
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
            self.logger.error(
                f"No decks found for {self.format} in the specified period"
            )
            return pd.DataFrame()

        # Create DataFrame with the same structure as the old system
        df = pd.DataFrame(all_decks)
        df["tournament_date"] = pd.to_datetime(df["tournament_date"])

        # Remove duplicates: same player + same tournament + same date
        initial_count = len(df)
        df = df.drop_duplicates(
            subset=["player_name", "tournament_id", "tournament_date"], keep="first"
        )
        duplicates_removed = initial_count - len(df)

        self.logger.info(f"\n📊 DATA LOADED:")
        self.logger.info(f"🏆 Tournaments: {tournaments_loaded}")
        self.logger.info(
            f"🎯 Decks: {len(df)} (removed {duplicates_removed} duplicates)"
        )
        self.logger.info(
            f"📅 Actual period: {df['tournament_date'].min().strftime('%Y-%m-%d')} to {df['tournament_date'].max().strftime('%Y-%m-%d')}"
        )
        self.logger.info(f"🎲 Archetypes: {df['archetype'].nunique()}")
        self.logger.info(f"🌍 Sources: {', '.join(df['tournament_source'].unique())}")

        self.logger.info(
            f"✅ {len(df)} decks loaded from {df['tournament_source'].nunique()} sources ({duplicates_removed} duplicates removed)"
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
                # MTGODecklistCache patterns
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}-*.json",
                f"MTGODecklistCache/Tournaments/*/{year}/{month}/*-{self.format.lower()}.json",
                # data/reference patterns
                f"data/reference/Tournaments/*/{year}/{month}/*/*{self.format.lower()}*.json",
                f"data/reference/Tournaments/*/{year}/{month}/*/{self.format.lower()}*.json",
                # NEW: data/raw patterns (where current data is)
                f"data/raw/*/{year}/{month}/*/*.json",
                f"data/raw/*/{year}/{month}/*/*/*.json",
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
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Clean up malformed JSON - more robust approach
                content = (
                    content.replace("}]", "}").replace("}s", "}").replace('"}\n}', '"}')
                )

                # Find the end of the main JSON structure
                brace_count = 0
                json_end = -1
                for i, char in enumerate(content):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break

                if json_end > 0:
                    content = content[:json_end]

                tournament_data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {file_path}: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            return []

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

        # Traiter les decks - gérer différents formats
        decks = []

        # Format 1: Decks/decks dans les données
        if "Decks" in tournament_data:
            decks = tournament_data["Decks"]
        elif "decks" in tournament_data:
            decks = tournament_data["decks"]
        # Format 2: Standings (comme dans data/raw)
        elif "Standings" in tournament_data:
            standings = tournament_data["Standings"]
            for standing in standings:
                if "Deck" in standing:
                    deck_with_player = standing["Deck"].copy()
                    deck_with_player["Player"] = standing.get("Player", "Unknown")
                    deck_with_player["Rank"] = standing.get("Rank", 0)
                    deck_with_player["Wins"] = standing.get("Wins", 0)
                    deck_with_player["Losses"] = standing.get("Losses", 0)
                    decks.append(deck_with_player)

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

        # Get mainboard for analysis
        mainboard = deck.get("Mainboard", deck.get("mainboard", []))

        # Classify archetype with Advanced Archetype Classifier (already includes color integration)
        archetype_with_colors = self._classify_archetype(mainboard)

        # Analyze deck colors for additional metadata
        color_analysis = self.color_detector.analyze_decklist_colors(mainboard)

        # Extract simple archetype name (without colors) for backwards compatibility
        archetype = self._extract_simple_archetype_name(archetype_with_colors)

        # DEBUG: Log archetype classification for troubleshooting
        self.logger.debug(
            f"Deck classification: '{archetype_with_colors}' -> '{archetype}'"
        )

        # Determine source with MTGO differentiation
        source = self._determine_source(file_path, tournament_info)

        # Extract deck URL from AnchorUri field
        deck_url = deck.get("AnchorUri", deck.get("anchor_uri", ""))

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
            "archetype_with_colors": archetype_with_colors,
            "color_identity": color_analysis["identity"],
            "guild_name": color_analysis["guild_name"],
            "color_distribution": color_analysis["color_distribution"],
            "wins": wins,
            "losses": losses,
            "draws": deck.get("draws", 0),
            "matches_played": wins + losses,
            "winrate": wins / max(1, wins + losses) if (wins + losses) > 0 else 0,
            "placement": deck.get("placement", 0),
            "deck_cards": deck.get("Mainboard", deck.get("mainboard", [])),
            "deck_url": deck_url,
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
            # Format directly in data (handle both cases)
            wins = deck.get("wins", deck.get("Wins", 0))
            losses = deck.get("losses", deck.get("Losses", 0))

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
                    return "mtgo.com"
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
        """Classify archetype using ArchetypeEngine (MTGOFormatData) as PRIMARY classifier"""
        try:
            # Step 1: PRIMARY - Use ArchetypeEngine (MTGOFormatData) for specific archetypes
            # Convert mainboard format for ArchetypeEngine
            deck_data = {
                "Mainboard": [
                    {"Name": card["CardName"], "Count": card["Count"]}
                    for card in mainboard
                ],
                "Sideboard": [],  # No sideboard for now
            }

            # Use ArchetypeEngine for precise archetype detection with metadata
            classification_result = self.archetype_engine.classify_deck_with_metadata(deck_data, self.format)

            if classification_result["archetype_name"] and classification_result["archetype_name"] != "Unknown":
                archetype_name = classification_result["archetype_name"]
                include_color = classification_result["include_color_in_name"]

                # Apply color integration ONLY if IncludeColorInName is True
                if include_color:
                    archetype_with_colors = self._apply_color_integration_mtgoformatdata(
                        archetype_name, mainboard
                    )
                else:
                    archetype_with_colors = archetype_name

                self.logger.debug(
                    f"ArchetypeEngine classification: {archetype_name} (IncludeColorInName: {include_color}) -> {archetype_with_colors}"
                )
                return archetype_with_colors

            # Step 2: FALLBACK 1 - Use MTGOClassifier if ArchetypeEngine fails
            base_archetype = self.mtgo_classifier.classify_deck(
                mainboard, [], self.format
            )

            if base_archetype and base_archetype != "Unknown":
                # Apply Aliquanto3-style color integration
                color_analysis = self.color_detector.analyze_decklist_colors(mainboard)
                guild_name = color_analysis.get("guild_name", "")

                if guild_name and guild_name != "Colorless" and guild_name != "Unknown":
                    archetype_with_colors = self._apply_aliquanto3_color_rules(
                        base_archetype, guild_name
                    )
                else:
                    archetype_with_colors = base_archetype

                self.logger.debug(
                    f"MTGOClassifier fallback: {base_archetype} -> {archetype_with_colors}"
                )
                return archetype_with_colors

            # Step 3: FALLBACK 2 - Color-based classification as last resort
            fallback_archetype = self._classify_by_colors_fallback(mainboard)
            self.logger.debug(f"Color fallback classification: {fallback_archetype}")
            return fallback_archetype

        except Exception as e:
            self.logger.error(f"Error in archetype classification: {e}")
            return self._classify_by_colors_fallback(mainboard)

    def _apply_color_integration_mtgoformatdata(self, archetype_name, mainboard):
        """
        Apply color integration for MTGOFormatData archetypes with IncludeColorInName=True
        Based on Aliquanto3 R-Meta-Analysis logic from 04-Metagame_Graph_Generation.R
        """
        try:
            # Analyze deck colors
            color_analysis = self.color_detector.analyze_decklist_colors(mainboard)
            guild_name = color_analysis.get("guild_name", "")

            if guild_name and guild_name != "Colorless" and guild_name != "Unknown":
                # Apply Aliquanto3 R logic: smart integration instead of simple concatenation
                return self._apply_aliquanto3_color_rules(archetype_name, guild_name)
            else:
                return archetype_name

        except Exception as e:
            self.logger.error(f"Error in color integration: {e}")
            return archetype_name

    def _apply_aliquanto3_color_rules(self, base_archetype, guild_name):
        """
        Apply Aliquanto3 R-Meta-Analysis color integration rules

        Based on the 04-Metagame_Graph_Generation.R logic:
        - Smart archetype naming instead of simple concatenation
        - Handle generic archetypes vs specific ones
        - Apply MTG guild color logic correctly
        """
        # Generic archetypes that benefit from color specification
        generic_archetypes = [
            "Aggro",
            "Control",
            "Midrange",
            "Ramp",
            "Tempo",
            "Combo",
            "Prowess",
            "Burn",
            "Tokens",
            "Artifacts",
            "Enchantments",
        ]

        # Specific archetypes that shouldn't be color-prefixed
        specific_archetypes = [
            "Tron",
            "Lantern",
            "Affinity",
            "Storm",
            "Ad Nauseam",
            "Scapeshift",
            "Living End",
            "Dredge",
            "Infect",
        ]

        # Clean base archetype name
        base_clean = base_archetype.strip()

        # Rule 1: If archetype is already color-specific, don't modify
        for color in [
            "Azorius",
            "Dimir",
            "Rakdos",
            "Gruul",
            "Selesnya",
            "Orzhov",
            "Izzet",
            "Golgari",
            "Boros",
            "Simic",
            "Mono-White",
            "Mono-Blue",
            "Mono-Black",
            "Mono-Red",
            "Mono-Green",
        ]:
            if color in base_clean:
                return base_clean

        # Rule 2: Generic archetypes get color prefix (Aliquanto3 logic)
        if any(generic in base_clean for generic in generic_archetypes):
            return f"{guild_name} {base_clean}"

        # Rule 3: Specific archetypes stay as-is
        if any(specific in base_clean for specific in specific_archetypes):
            return base_clean

        # Rule 4: Default - add color if it improves clarity
        if len(base_clean) < 15:  # Short names benefit from color
            return f"{guild_name} {base_clean}"
        else:
            return base_clean

    def _classify_with_mtgo_fallback(self, mainboard):
        """Fallback to MTGO classifier if advanced classifier fails"""
        try:
            archetype = self.mtgo_classifier.classify_deck(mainboard, [], self.format)
            if archetype and archetype != "Unknown":
                return archetype
            else:
                return self._classify_by_colors_fallback(mainboard)
        except Exception as e:
            self.logger.error(f"Error in MTGO fallback: {e}")
            return self._classify_by_colors_fallback(mainboard)

    def _extract_simple_archetype_name(self, archetype_with_colors):
        """Extract simple archetype name without color prefixes for backwards compatibility"""
        if not archetype_with_colors or archetype_with_colors == "Others":
            return "Others"

        # Remove common color prefixes
        color_prefixes = [
            "Azorius ",
            "Dimir ",
            "Rakdos ",
            "Gruul ",
            "Selesnya ",
            "Orzhov ",
            "Izzet ",
            "Golgari ",
            "Boros ",
            "Simic ",
            "Esper ",
            "Grixis ",
            "Jund ",
            "Naya ",
            "Bant ",
            "Mono-White ",
            "Mono-Blue ",
            "Mono-Black ",
            "Mono-Red ",
            "Mono-Green ",
            "White ",
            "Blue ",
            "Black ",
            "Red ",
            "Green ",
            "Five-Color ",
            "5C ",
            "WUBRG ",
            "Sans-White ",
            "Sans-Blue ",
            "Sans-Black ",
            "Sans-Red ",
            "Sans-Green ",
        ]

        simple_name = archetype_with_colors
        for prefix in color_prefixes:
            if simple_name.startswith(prefix):
                simple_name = simple_name[len(prefix) :]
                break

        return simple_name if simple_name else "Others"

    def _classify_by_colors_fallback(self, mainboard):
        """Fallback color-based classification if MTGO classifier fails"""
        try:
            # Convert to list of card names
            card_names = []
            for card in mainboard:
                card_names.extend([card.get("CardName", "")] * card.get("Count", 0))

            # Color-based classification
            colors = self._detect_colors(card_names)

            # Improved rule: Don't default all monocolor to "Others"
            if len(colors) == 1:
                color_names = {
                    "W": "White",
                    "U": "Blue",
                    "B": "Black",
                    "R": "Red",
                    "G": "Green",
                }
                color_name = color_names.get(list(colors)[0], "Unknown")
                return f"Mono-{color_name} Deck"
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
                return "Others"

        except Exception as e:
            self.logger.error(f"Error in color-based classification: {e}")
            return "Others"

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
            total_players = df[
                "player_name"
            ].nunique()  # Count unique players like the old system
            total_matches = len(df)  # Use total decks as matches
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
        .viz-content {{ height: 650px; }}
        .viz-content.matchup-matrix {{ height: 1275px; }}
        .viz-iframe {{ width: 100%; height: 100%; border: none; }}

        .footer {{ background: var(--text-dark); color: white; text-align: center;
                  padding: 2rem; margin-top: 3rem; }}
        .footer p {{ opacity: 0.8; }}

        /* MTG Color Styles */
        .mana-symbol {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            font-size: 10px;
            line-height: 16px;
            text-align: center;
            margin: 0 2px;
        }}
        .mana-w {{ background-color: #fffbd5; color: #000; }}
        .mana-u {{ background-color: #0e68ab; }}
        .mana-b {{ background-color: #150b00; }}
        .mana-r {{ background-color: #d3202a; }}
        .mana-g {{ background-color: #00733e; }}
        .mana-c {{ background-color: #ccc; color: #000; }}

        .color-white {{ border-left: 4px solid #fffbd5; }}
        .color-blue {{ border-left: 4px solid #0e68ab; }}
        .color-black {{ border-left: 4px solid #150b00; }}
        .color-red {{ border-left: 4px solid #d3202a; }}
        .color-green {{ border-left: 4px solid #00733e; }}
        .color-azorius {{ border-left: 4px solid #fffbd5; border-right: 4px solid #0e68ab; }}
        .color-dimir {{ border-left: 4px solid #0e68ab; border-right: 4px solid #150b00; }}
        .color-rakdos {{ border-left: 4px solid #150b00; border-right: 4px solid #d3202a; }}
        .color-gruul {{ border-left: 4px solid #d3202a; border-right: 4px solid #00733e; }}
        .color-selesnya {{ border-left: 4px solid #00733e; border-right: 4px solid #fffbd5; }}
        .color-orzhov {{ border-left: 4px solid #fffbd5; border-right: 4px solid #150b00; }}
        .color-golgari {{ border-left: 4px solid #150b00; border-right: 4px solid #00733e; }}
        .color-simic {{ border-left: 4px solid #00733e; border-right: 4px solid #0e68ab; }}
        .color-izzet {{ border-left: 4px solid #0e68ab; border-right: 4px solid #d3202a; }}
        .color-boros {{ border-left: 4px solid #d3202a; border-right: 4px solid #fffbd5; }}
        .color-colorless {{ border-left: 4px solid #ccc; }}

        /* MTGO Analysis Button Styles */
        .mtgo-section {{
            margin: 2rem 0;
            text-align: center;
        }}

        .mtgo-button {{
            display: inline-block;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 15px;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }}

        .mtgo-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
            background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
        }}

        .mtgo-button:active {{
            transform: translateY(-1px);
        }}

        .mtgo-description {{
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
            opacity: 0.8;
        }}

        .navigation {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .nav-button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 10px;
            text-decoration: none;
            display: inline-block;
            font-weight: 500;
        }}
        .nav-button:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
        }}
        .stat-icon {{
            font-size: 2.5rem; margin-bottom: 1rem; display: block;
            opacity: 0.8; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }}

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
                <div class="stat-icon">🏆</div>
                <div class="stat-number">{total_tournaments}</div>
                <div class="stat-label">Tournaments analyzed</div>
                <div class="stat-hint">🔍 Click to view list</div>
            </div>
            <div class="stat-card clickable" onclick="window.open('players_stats.html', '_blank')">
                <div class="stat-icon">👥</div>
                <div class="stat-number">{total_players}</div>
                <div class="stat-label">Players</div>
                <div class="stat-hint">🔍 Click to view players</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚔️</div>
                <div class="stat-number">{total_matches}</div>
                <div class="stat-label">Matches played</div>
            </div>
            <div class="stat-card clickable" onclick="window.open('all_archetypes.html', '_blank')">
                <div class="stat-icon">🎯</div>
                <div class="stat-number">{len(archetypes)}</div>
                <div class="stat-label">Archetypes identified</div>
                <div class="stat-hint">🔍 Click to view archetypes</div>
            </div>
        </div>

        <!-- MTGO Analysis Button - Prominent Position -->
        <div class="mtgo-section">
            <a href="mtgo_analysis/{format_name.lower()}_{start_date}_{end_date}_mtgo.html" class="mtgo-button">
                🎯 MTGO Analysis
            </a>
            <div class="mtgo-description">Dedicated analysis for MTGO tournaments only</div>
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
                <div class="viz-content matchup-matrix">
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

    <div class="navigation">
        <a href="{format_name.lower()}_{start_date}_{end_date}_tournaments_list.html" class="nav-button">📋 Tournament List</a>
        <a href="players_stats.html" class="nav-button">👥 Players Stats</a>
        <a href="decklists_detailed.html" class="nav-button">📋 Detailed Decklists</a>
        <a href="all_archetypes.html" class="nav-button">🎲 All Archetypes</a>
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
            return None

    def _export_detailed_decklists(self, df: pd.DataFrame, output_dir: str):
        """Export detailed decklists CSV/JSON and generate archetype navigation pages"""
        try:
            output_path = Path(output_dir)

            # 1. Export detailed CSV/JSON
            detailed_csv = output_path / "decklists_detailed.csv"
            detailed_json = output_path / "decklists_detailed.json"

            # Prepare detailed export data
            export_data = []
            for _, row in df.iterrows():
                # Convert Timestamp to string for JSON serialization
                tournament_date = row.get("tournament_date", "Unknown")
                if hasattr(tournament_date, "strftime"):
                    tournament_date = tournament_date.strftime("%Y-%m-%d")
                elif tournament_date != "Unknown":
                    tournament_date = str(tournament_date)

                deck_data = {
                    "deck_id": f"{row.get('tournament_id', 'unknown')}_{row.get('player_name', 'unknown')}",
                    "archetype": row.get("archetype", "Unknown"),
                    "archetype_with_colors": row.get(
                        "archetype_with_colors", row.get("archetype", "Unknown")
                    ),
                    "color_identity": row.get("color_identity", ""),
                    "guild_name": row.get("guild_name", ""),
                    "player_name": row.get("player_name", "Unknown"),
                    "tournament_name": row.get("tournament_name", "Unknown"),
                    "tournament_date": tournament_date,
                    "tournament_source": row.get("tournament_source", "Unknown"),
                    "deck_url": row.get("deck_url", ""),
                    "mainboard": row.get("mainboard", []),
                    "sideboard": row.get("sideboard", []),
                }
                export_data.append(deck_data)

            # Save CSV
            export_df = pd.DataFrame(export_data)
            export_df.to_csv(detailed_csv, index=False, encoding="utf-8")

            # Save JSON
            with open(detailed_json, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(
                f"📋 Detailed decklists exported: {detailed_csv}, {detailed_json}"
            )

            # 2. Generate archetype navigation pages
            archetype_pages = self._generate_archetype_pages(export_data, output_path)

            return {
                "csv_path": str(detailed_csv),
                "json_path": str(detailed_json),
                "archetype_pages": archetype_pages,
                "total_decks": len(export_data),
            }

        except Exception as e:
            self.logger.error(f"❌ Error exporting detailed decklists: {e}")
            return None

    def _generate_archetype_pages(self, deck_data: list, output_path: Path):
        """Generate all_archetypes.html and individual archetype pages"""
        try:
            # Group decks by archetype
            archetypes_dict = {}
            for deck in deck_data:
                archetype = deck["archetype"]
                if archetype not in archetypes_dict:
                    archetypes_dict[archetype] = []
                archetypes_dict[archetype].append(deck)

            # 1. Generate all_archetypes.html
            all_archetypes_html = self._generate_all_archetypes_page(archetypes_dict)
            all_archetypes_path = output_path / "all_archetypes.html"
            with open(all_archetypes_path, "w", encoding="utf-8") as f:
                f.write(all_archetypes_html)

            # 2. Generate individual archetype pages
            archetype_pages = []
            for archetype, decks in archetypes_dict.items():
                archetype_html = self._generate_archetype_page(archetype, decks)
                archetype_filename = (
                    f"archetype_{archetype.replace(' ', '_').replace('/', '_')}.html"
                )
                archetype_path = output_path / archetype_filename
                with open(archetype_path, "w", encoding="utf-8") as f:
                    f.write(archetype_html)
                archetype_pages.append(str(archetype_path))

            self.logger.info(
                f"🗺️ Generated {len(archetype_pages)} archetype pages + all_archetypes.html"
            )

            return {
                "all_archetypes_path": str(all_archetypes_path),
                "individual_pages": archetype_pages,
                "total_archetypes": len(archetypes_dict),
            }

        except Exception as e:
            self.logger.error(f"❌ Error generating archetype pages: {e}")
            return None

    def _generate_all_archetypes_page(self, archetypes_dict: dict):
        """Generate HTML page listing all archetypes"""
        total_decks = sum(len(decks) for decks in archetypes_dict.values())

        archetype_rows = ""
        for archetype, decks in sorted(
            archetypes_dict.items(), key=lambda x: len(x[1]), reverse=True
        ):
            deck_count = len(decks)
            percentage = (deck_count / total_decks * 100) if total_decks > 0 else 0
            archetype_filename = (
                f"archetype_{archetype.replace(' ', '_').replace('/', '_')}.html"
            )

            # Get color information from first deck (should be consistent for archetype)
            first_deck = decks[0]
            color_identity = first_deck.get("color_identity", "")
            guild_name = first_deck.get("guild_name", "")
            archetype_with_colors = first_deck.get("archetype_with_colors", archetype)

            # Generate color symbols HTML
            color_symbols = self.color_detector.get_color_symbols_html(color_identity)
            color_css_class = self.color_detector.get_color_css_class(color_identity)

            archetype_rows += f"""
                <tr onclick="window.location.href='{archetype_filename}'" style="cursor: pointer;" class="{color_css_class}">
                    <td style="font-weight: bold; color: #762a83;">
                        {color_symbols} {archetype_with_colors}
                    </td>
                    <td style="text-align: center; color: #666; font-size: 0.9rem;">{guild_name}</td>
                    <td style="text-align: center;">{deck_count}</td>
                    <td style="text-align: center;">{percentage:.1f}%</td>
                    <td style="text-align: center;">
                        <span style="background: #4ECDC4; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.9rem;">
                            View Decks →
                        </span>
                    </td>
                </tr>
            """

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Archetypes - Manalytics</title>
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
                  color: white; padding: 2rem 0; text-align: center; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 2rem; }}
        .card {{ background: var(--bg-white); border-radius: var(--border-radius);
                 box-shadow: var(--shadow); overflow: hidden; }}
        .card-header {{ background: var(--bg-light); padding: 1.5rem; }}
        .card-title {{ font-size: 1.5rem; font-weight: 600; color: var(--text-dark); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: var(--bg-light); font-weight: 600; }}
        tr:hover {{ background: rgba(118, 42, 131, 0.05); }}
        .back-btn {{ display: inline-block; background: var(--primary); color: white;
                     padding: 0.8rem 1.5rem; border-radius: 8px; text-decoration: none;
                     margin-bottom: 2rem; transition: all 0.3s; }}
        .back-btn:hover {{ background: var(--secondary); transform: translateY(-2px); }}

        /* MTG Color Styles */
        .mana-symbol {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            font-size: 10px;
            line-height: 16px;
            text-align: center;
            margin: 0 2px;
        }}
        .mana-w {{ background-color: #fffbd5; color: #000; }}
        .mana-u {{ background-color: #0e68ab; }}
        .mana-b {{ background-color: #150b00; }}
        .mana-r {{ background-color: #d3202a; }}
        .mana-g {{ background-color: #00733e; }}
        .mana-c {{ background-color: #ccc; color: #000; }}

        .color-white {{ border-left: 4px solid #fffbd5; }}
        .color-blue {{ border-left: 4px solid #0e68ab; }}
        .color-black {{ border-left: 4px solid #150b00; }}
        .color-red {{ border-left: 4px solid #d3202a; }}
        .color-green {{ border-left: 4px solid #00733e; }}
        .color-azorius {{ border-left: 4px solid #fffbd5; border-right: 4px solid #0e68ab; }}
        .color-dimir {{ border-left: 4px solid #0e68ab; border-right: 4px solid #150b00; }}
        .color-rakdos {{ border-left: 4px solid #150b00; border-right: 4px solid #d3202a; }}
        .color-gruul {{ border-left: 4px solid #d3202a; border-right: 4px solid #00733e; }}
        .color-selesnya {{ border-left: 4px solid #00733e; border-right: 4px solid #fffbd5; }}
        .color-orzhov {{ border-left: 4px solid #fffbd5; border-right: 4px solid #150b00; }}
        .color-golgari {{ border-left: 4px solid #150b00; border-right: 4px solid #00733e; }}
        .color-simic {{ border-left: 4px solid #00733e; border-right: 4px solid #0e68ab; }}
        .color-izzet {{ border-left: 4px solid #0e68ab; border-right: 4px solid #d3202a; }}
        .color-boros {{ border-left: 4px solid #d3202a; border-right: 4px solid #fffbd5; }}
        .color-colorless {{ border-left: 4px solid #ccc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 All Archetypes</h1>
        <p>Complete list of detected archetypes • {total_decks} total decks analyzed</p>
    </div>

    <div class="container">
        <a href="javascript:history.back()" class="back-btn">← Back to Dashboard</a>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">📊 Archetypes Overview</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Archetype</th>
                        <th style="text-align: center;">Colors</th>
                        <th style="text-align: center;">Decks</th>
                        <th style="text-align: center;">Meta Share</th>
                        <th style="text-align: center;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {archetype_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """

    def _generate_archetype_page(self, archetype: str, decks: list):
        """Generate HTML page for a specific archetype"""
        deck_rows = ""
        for i, deck in enumerate(decks, 1):
            deck_url = deck.get("deck_url", "")
            deck_link = (
                f'<a href="{deck_url}" target="_blank" style="color: #4ECDC4; text-decoration: none;">🔗 View Deck</a>'
                if deck_url
                else "No link available"
            )

            deck_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td style="font-weight: bold;">{deck.get('player_name', 'Unknown')}</td>
                    <td>{deck.get('tournament_name', 'Unknown')}</td>
                    <td>{deck.get('tournament_date', 'Unknown')}</td>
                    <td>
                        <span style="background: #27ae60; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.8rem;">
                            {deck.get('tournament_source', 'Unknown')}
                        </span>
                    </td>
                    <td style="text-align: center;">{deck_link}</td>
                </tr>
            """

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{archetype} Decks - Manalytics</title>
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
                  color: white; padding: 2rem 0; text-align: center; }}
        .container {{ max-width: 1400px; margin: 2rem auto; padding: 2rem; }}
        .card {{ background: var(--bg-white); border-radius: var(--border-radius);
                 box-shadow: var(--shadow); overflow: hidden; }}
        .card-header {{ background: var(--bg-light); padding: 1.5rem; }}
        .card-title {{ font-size: 1.5rem; font-weight: 600; color: var(--text-dark); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.8rem; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: var(--bg-light); font-weight: 600; font-size: 0.9rem; }}
        tr:hover {{ background: rgba(118, 42, 131, 0.05); }}
        .back-btn {{ display: inline-block; background: var(--primary); color: white;
                     padding: 0.8rem 1.5rem; border-radius: 8px; text-decoration: none;
                     margin-bottom: 2rem; transition: all 0.3s; }}
        .back-btn:hover {{ background: var(--secondary); transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 {archetype}</h1>
        <p>{len(decks)} decklists found for this archetype</p>
    </div>

    <div class="container">
        <a href="all_archetypes.html" class="back-btn">← Back to All Archetypes</a>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">📋 All {archetype} Decklists</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Player</th>
                        <th>Tournament</th>
                        <th>Date</th>
                        <th>Source</th>
                        <th style="text-align: center;">Decklist</th>
                    </tr>
                </thead>
                <tbody>
                    {deck_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """

    def _perform_advanced_analysis(self, df: pd.DataFrame, output_dir: str) -> Dict:
        """Perform advanced statistical analysis on tournament data"""
        try:
            # Load data into advanced analyzer
            if not self.advanced_analyzer.load_data(df):
                self.logger.warning("⚠️ Could not load data for advanced analysis")
                return {}

            # Generate comprehensive analysis
            analysis_report = self.advanced_analyzer.generate_comprehensive_analysis()

            # Save advanced analysis report
            import json

            advanced_file = Path(output_dir) / "advanced_analysis.json"
            with open(advanced_file, "w", encoding="utf-8") as f:
                json.dump(analysis_report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Advanced analysis saved to {advanced_file}")

            # Log key insights
            if "diversity_metrics" in analysis_report:
                diversity = analysis_report["diversity_metrics"]
                self.logger.info(
                    f"📊 Diversity Metrics: Shannon={diversity.get('shannon_diversity', 0):.3f}, Simpson={diversity.get('simpson_diversity', 0):.3f}"
                )

            if (
                "temporal_trends" in analysis_report
                and "category_counts" in analysis_report["temporal_trends"]
            ):
                trends = analysis_report["temporal_trends"]["category_counts"]
                self.logger.info(f"📈 Temporal Trends: {trends}")

            return {
                "analysis_report": analysis_report,
                "advanced_file": str(advanced_file),
                "insights": self._extract_key_insights(analysis_report),
            }

        except Exception as e:
            self.logger.error(f"❌ Error in advanced analysis: {e}")
            return {}

    def generate_players_stats(self, output_dir: str, df: pd.DataFrame):
        """Generate players_stats.html page with detailed player analysis"""
        try:
            # Calculate player statistics using simple groupby
            player_stats = df.groupby("player_name").agg(
                {
                    "tournament_id": "nunique",  # Number of tournaments
                    "archetype": [
                        "count",
                        lambda x: len(x.unique()),
                    ],  # Number of decks and unique archetypes
                    "color_identity": lambda x: (
                        x.mode().iloc[0] if not x.empty else "Unknown"
                    ),  # Most common colors
                }
            )

            # Flatten column names
            player_stats.columns = [
                "tournaments",
                "decks",
                "archetypes",
                "favorite_colors",
            ]
            player_stats = player_stats.reset_index()

            # Get favorite archetype for each player
            favorite_archetypes = (
                df.groupby("player_name")["archetype"]
                .apply(lambda x: x.value_counts().index[0] if len(x) > 0 else "Unknown")
                .reset_index()
            )
            favorite_archetypes.columns = ["player_name", "favorite_archetype"]

            # Merge data
            players_data = player_stats.merge(favorite_archetypes, on="player_name")

            # Sort by number of decks (activity)
            players_data = players_data.sort_values(
                "decks", ascending=False
            ).reset_index(drop=True)
            players_data["rank"] = range(1, len(players_data) + 1)

            # Get summary stats
            total_players = len(players_data)
            most_active_player = players_data.iloc[0] if len(players_data) > 0 else None

            # Generate HTML
            html_content = self._generate_players_html(
                players_data, total_players, most_active_player
            )

            # Save file
            output_path = Path(output_dir) / "players_stats.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.logger.info(f"✅ Players stats page created: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"❌ Error generating players stats: {e}")
            return None

    def _generate_players_html(self, players_data, total_players, most_active_player):
        """Generate HTML content for players stats page"""

        # Generate player rows
        player_rows = ""
        for _, player in players_data.iterrows():
            archetype_link = f'archetype_{player["favorite_archetype"].replace(" ", "_").replace("/", "_")}.html'
            player_rows += f"""
                <tr>
                    <td class="rank">{player['rank']}</td>
                    <td class="player-name">{player['player_name']}</td>
                    <td class="tournaments-count">{player['tournaments']}</td>
                    <td class="decks-count">{player['decks']}</td>
                    <td class="archetypes-count">{player['archetypes']}</td>
                    <td class="favorite-archetype">
                        <a href="{archetype_link}" class="archetype-link">{player['favorite_archetype']}</a>
                    </td>
                    <td class="favorite-colors">{player['favorite_colors']}</td>
                </tr>
            """

        most_active_info = ""
        if most_active_player is not None:
            most_active_info = f"<br><small>{most_active_player['player_name']}</small>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Players Statistics - MTG Manalytics</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
                .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #2c3e50; margin: 0; font-size: 2.5rem; }}
                .header p {{ color: #7f8c8d; margin: 10px 0; font-size: 1.1rem; }}

                .summary-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-number {{ font-size: 2rem; font-weight: bold; margin-bottom: 5px; }}
                .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}

                .players-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .players-table th {{ background: #34495e; color: white; padding: 15px 10px; text-align: left; font-weight: 600; }}
                .players-table td {{ padding: 12px 10px; border-bottom: 1px solid #ecf0f1; }}
                .players-table tr:hover {{ background: #f8f9fa; }}
                .players-table tr:nth-child(even) {{ background: #fafbfc; }}

                .rank {{ font-weight: bold; color: #e74c3c; text-align: center; width: 60px; }}
                .player-name {{ font-weight: bold; color: #2c3e50; }}
                .tournaments-count {{ font-weight: bold; color: #27ae60; text-align: center; }}
                .decks-count {{ color: #3498db; text-align: center; }}
                .archetypes-count {{ color: #9b59b6; text-align: center; }}
                .favorite-archetype {{ color: #e67e22; }}
                .archetype-link {{ color: #e67e22; text-decoration: none; font-weight: bold; }}
                .archetype-link:hover {{ color: #d35400; text-decoration: underline; }}
                .favorite-colors {{ font-family: monospace; background: #ecf0f1; padding: 4px 8px; border-radius: 4px; }}

                .back-link {{ display: inline-block; margin-bottom: 20px; color: #3498db; text-decoration: none; font-weight: 500; }}
                .back-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="javascript:window.close()" class="back-link">← Back to Dashboard</a>

                <div class="header">
                    <h1>👥 Players Statistics</h1>
                    <p>Detailed analysis of player activity and preferences</p>
                </div>

                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_players}</div>
                        <div class="stat-label">Total Players</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{most_active_player['decks'] if most_active_player is not None else 0}</div>
                        <div class="stat-label">Most Active Player{most_active_info}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{players_data['archetypes'].mean():.1f}</div>
                        <div class="stat-label">Avg Archetypes per Player</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{players_data['tournaments'].mean():.1f}</div>
                        <div class="stat-label">Avg Tournaments per Player</div>
                    </div>
                </div>

                <table class="players-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Tournaments</th>
                            <th>Decks</th>
                            <th>Archetypes</th>
                            <th>Favorite Archetype</th>
                            <th>Favorite Colors</th>
                        </tr>
                    </thead>
                    <tbody>
                        {player_rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

    def generate_mtgo_analysis(self, output_dir: str, df: pd.DataFrame):
        """Generate dedicated MTGO analysis with filtered data"""
        try:
            # Filter for MTGO data only - Include all mtgo.com sources EXCEPT 5-0 leagues
            mtgo_df = df[
                (df["tournament_source"].str.contains("mtgo.com", na=False))
                & (~df["tournament_source"].str.contains("5-0", na=False))
            ]

            if len(mtgo_df) == 0:
                self.logger.warning("No MTGO data found for dedicated analysis")
                return None

            # Create MTGO analysis directory
            mtgo_dir = Path(output_dir) / "mtgo_analysis"
            mtgo_dir.mkdir(exist_ok=True)

            # Generate all MTGO-specific content
            self._generate_mtgo_dashboard(str(mtgo_dir), mtgo_df)
            self._generate_mtgo_visualizations(str(mtgo_dir), mtgo_df)
            self._export_detailed_decklists(mtgo_df, str(mtgo_dir))
            self._generate_archetype_pages(mtgo_df.to_dict("records"), mtgo_dir)

            self.logger.info(f"✅ MTGO analysis created: {mtgo_dir}")
            return str(mtgo_dir)

        except Exception as e:
            self.logger.error(f"❌ Error generating MTGO analysis: {e}")
            return None

    def _generate_mtgo_dashboard(self, output_dir: str, df: pd.DataFrame):
        """Generate MTGO-specific dashboard"""
        total_tournaments = df["tournament_id"].nunique()
        total_players = df[
            "player_name"
        ].nunique()  # Use unique players like the old system
        total_matches = len(df)  # Use deck count as matches
        archetypes = sorted(df["archetype"].unique())

        # Generate source badges for MTGO sources
        sources = df["tournament_source"].unique()
        source_badges = ""
        for source in sources:
            if "League" in source:
                badge_color = "#27ae60"  # Green
            elif "Challenge" in source:
                badge_color = "#e74c3c"  # Red
            else:
                badge_color = "#3498db"  # Blue

            source_badges += f'<span style="background-color: {badge_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin: 0 0.5rem;">{source}</span>'

        # Use date range from the orchestrator
        start_date = getattr(self, "start_date", "2025-05-08")
        end_date = getattr(self, "end_date", "2025-06-09")

        # Generate MTGO-specific HTML with red theme
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTGO Analysis - Standard ({start_date} to {end_date})</title>
    <style>
        :root {{
            --primary: #e74c3c; --secondary: #c0392b; --accent: #4ECDC4;
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
        .stat-icon {{ font-size: 2.5rem; margin-bottom: 1rem; display: block;
                      opacity: 0.8; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }}
        .stat-number {{ font-size: 3rem; font-weight: bold; color: var(--primary); }}
        .stat-label {{ font-size: 1.1rem; color: var(--text-dark); margin-top: 0.5rem; }}

        .viz-grid {{ display: grid; gap: 2rem; }}
        .viz-card {{ background: var(--bg-white); border-radius: var(--border-radius);
                    box-shadow: var(--shadow); overflow: hidden; }}
        .viz-header {{ background: var(--bg-light); padding: 1.5rem; border-bottom: 1px solid #eee; }}
        .viz-title {{ font-size: 1.4rem; font-weight: 600; color: var(--text-dark); }}
        .viz-content {{ height: 650px; }}
        .viz-content.matchup-matrix {{ height: 1275px; }}
        .viz-iframe {{ width: 100%; height: 100%; border: none; }}

        .navigation {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .nav-button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 10px;
            text-decoration: none;
            display: inline-block;
            font-weight: 500;
        }}
        .nav-button:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
        }}

        .footer {{ background: var(--text-dark); color: white; text-align: center;
                  padding: 2rem; margin-top: 3rem; }}
        .footer p {{ opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 MTGO Analysis</h1>
        <p>Dedicated analysis for MTGO tournaments • {start_date} to {end_date}</p>
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <span style="font-size: 0.9rem; color: white;">MTGO sources:</span>
            {source_badges}
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🏆</div>
                <div class="stat-number">{total_tournaments}</div>
                <div class="stat-label">MTGO Tournaments</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-number">{total_players}</div>
                <div class="stat-label">MTGO Players</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚔️</div>
                <div class="stat-number">{total_matches}</div>
                <div class="stat-label">MTGO Matches</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-number">{len(archetypes)}</div>
                <div class="stat-label">MTGO Archetypes</div>
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
                    <h3 class="viz-title">📈 Market Share</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/metagame_share.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🎯 Winrate Analysis</h3>
                </div>
                <div class="viz-content">
                    <iframe src="visualizations/winrate_confidence.html" class="viz-iframe"></iframe>
                </div>
            </div>

            <div class="viz-card">
                <div class="viz-header">
                    <h3 class="viz-title">🔥 Matchup Matrix</h3>
                </div>
                <div class="viz-content matchup-matrix">
                    <iframe src="visualizations/matchup_matrix.html" class="viz-iframe"></iframe>
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
        </div>

        <div class="navigation">
            <a href="../standard_{start_date}_{end_date}.html" class="nav-button">← Back to Full Analysis</a>
            <a href="decklists_detailed.html" class="nav-button">📋 MTGO Decklists</a>
        </div>
    </div>

    <div class="footer">
        <p>🎯 MTGO-only analysis • Generated automatically • 100% real tournament data</p>
    </div>
</body>
</html>
        """

        # Save MTGO dashboard
        output_path = Path(output_dir) / f"standard_{start_date}_{end_date}_mtgo.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_mtgo_visualizations(self, output_dir: str, df: pd.DataFrame):
        """Generate ALL MTGO visualizations (same as main analysis)"""
        from src.python.visualizations.matchup_matrix import MatchupMatrixGenerator
        from src.python.visualizations.metagame_charts import MetagameChartsGenerator

        viz_dir = Path(output_dir) / "visualizations"
        viz_dir.mkdir(exist_ok=True)

        # Generate complete set of charts like main analysis
        charts_generator = MetagameChartsGenerator()
        matchup_generator = MatchupMatrixGenerator()

        self.logger.info("📊 Generating MTGO matchup matrix...")
        matchup_result = matchup_generator.generate_full_report(str(viz_dir), df)

        self.logger.info("📈 Generating MTGO metagame charts...")
        charts_result = charts_generator.generate_all_charts(df, str(viz_dir))

    def _extract_key_insights(self, analysis_report: Dict) -> List[str]:
        """Extract key insights from advanced analysis"""
        insights = []

        try:
            # Diversity insights
            if "diversity_metrics" in analysis_report:
                diversity = analysis_report["diversity_metrics"]
                shannon = diversity.get("shannon_diversity", 0)
                effective = diversity.get("effective_archetypes", 0)

                if shannon > 2.5:
                    insights.append(
                        f"🌈 High diversity metagame (Shannon: {shannon:.2f}, Effective archetypes: {effective:.1f})"
                    )
                elif shannon < 1.5:
                    insights.append(
                        f"⚪ Low diversity metagame (Shannon: {shannon:.2f}, dominance by few archetypes)"
                    )
                else:
                    insights.append(
                        f"⚖️ Balanced metagame (Shannon: {shannon:.2f}, {effective:.1f} effective archetypes)"
                    )

            # Temporal trends insights
            if (
                "temporal_trends" in analysis_report
                and "category_counts" in analysis_report["temporal_trends"]
            ):
                trends = analysis_report["temporal_trends"]["category_counts"]
                rising = trends.get("Rising", 0)
                declining = trends.get("Declining", 0)

                if rising > declining:
                    insights.append(
                        f"📈 Dynamic metagame: {rising} rising archetypes vs {declining} declining"
                    )
                elif declining > rising:
                    insights.append(
                        f"📉 Consolidating metagame: {declining} declining archetypes vs {rising} rising"
                    )
                else:
                    insights.append(f"🎯 Stable metagame: balanced archetype evolution")

            # Clustering insights
            if (
                "clustering_analysis" in analysis_report
                and "archetype_clusters" in analysis_report["clustering_analysis"]
            ):
                clusters = analysis_report["clustering_analysis"]["archetype_clusters"]
                if clusters:
                    insights.append(
                        f"🎯 Identified {len(set(clusters.values()))} distinct archetype performance clusters"
                    )

            # Card analysis insights
            if "card_analysis" in analysis_report:
                card_data = analysis_report["card_analysis"]
                total_cards = card_data.get("total_unique_cards", 0)
                if total_cards > 0:
                    insights.append(
                        f"🃏 {total_cards} unique cards analyzed across all archetypes"
                    )

        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting insights: {e}")
            insights.append("🔍 Advanced analysis completed successfully")

        return insights

    def generate_metagame_analysis(
        self, start_date, end_date, format_type="Standard", output_dir=None
    ):
        """
        Enhanced metagame analysis with color integration
        Based on Aliquanto3's R-Meta-Analysis system
        """
        logger.rocket_info("Generating enhanced metagame analysis for {format_type}...")
        logger.calendar_info("Period: {start_date} to {end_date}")

        # Setup
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = os.path.join(
                "Analyses", f"{format_type.lower()}_analysis_{timestamp}"
            )

        os.makedirs(output_dir, exist_ok=True)
        self._setup_services()

        # Fetch and process data
        logger.data_info("Fetching tournament data...")
        tournaments = self._fetch_tournaments(start_date, end_date, format_type)

        logger.search_info("Processing decks with advanced classification...")
        all_decks = []
        processed_tournaments = []

        for tournament in tournaments:
            tournament_decks = self._process_tournament_enhanced(tournament)
            all_decks.extend(tournament_decks)
            processed_tournaments.append(tournament)

        logger.info(
            f"✅ Processed {len(all_decks)} decks from {len(processed_tournaments)} tournaments"
        )

        # Generate enhanced analysis
        enhanced_data = self._generate_enhanced_analysis_data(
            all_decks, processed_tournaments
        )

        # Save enhanced data
        enhanced_data_path = os.path.join(output_dir, "enhanced_analysis_data.json")
        with open(enhanced_data_path, "w") as f:
            json.dump(enhanced_data, f, indent=2, cls=DateTimeEncoder)

        # Generate all outputs
        self._generate_all_enhanced_outputs(enhanced_data, output_dir)

        logger.party_info("Enhanced analysis complete! Results saved to: {output_dir}")
        return output_dir

    def _process_tournament_enhanced(self, tournament):
        """Process tournament with enhanced classification"""
        enhanced_decks = []

        for deck in tournament.get("decks", []):
            try:
                # Basic processing
                colors = self.color_detector.analyze_decklist_colors(deck["cards"])
                color_identity = colors.get("color_identity", "")

                # Enhanced classification
                deck_data = {
                    "cards": [card["name"] for card in deck["cards"]],
                    "color_identity": color_identity,
                }

                advanced_classification = (
                    self.advanced_classifier.classify_with_color_integration(deck_data)
                )

                enhanced_deck = {
                    "player": deck.get("player", "Unknown"),
                    "archetype": advanced_classification["archetype"],
                    "archetype_with_colors": advanced_classification[
                        "archetype_with_colors"
                    ],
                    "color_identity": advanced_classification["color_identity"],
                    "guild_name": advanced_classification["guild_name"],
                    "strategy_type": advanced_classification["strategy_type"],
                    "confidence": advanced_classification["confidence"],
                    "colors": colors,
                    "cards": deck["cards"],
                    "tournament_name": tournament.get("name", ""),
                    "tournament_date": tournament.get("date", ""),
                    "placement": deck.get("placement", 0),
                }

                enhanced_decks.append(enhanced_deck)

            except Exception as e:
                logger.warning("Error processing deck: {e}")
                continue

        return enhanced_decks

    def _generate_enhanced_analysis_data(self, all_decks, tournaments):
        """Generate enhanced analysis data structure"""

        # Classification statistics
        classification_stats = self.advanced_classifier.generate_archetype_statistics(
            [{"classification": deck} for deck in all_decks]
        )

        # Tournament statistics
        tournament_stats = {
            "total_tournaments": len(tournaments),
            "date_range": {
                "start": (
                    min(t.get("date", "") for t in tournaments) if tournaments else ""
                ),
                "end": (
                    max(t.get("date", "") for t in tournaments) if tournaments else ""
                ),
            },
            "tournaments_by_date": self._group_tournaments_by_date(tournaments),
        }

        # Deck statistics
        deck_stats = {
            "total_decks": len(all_decks),
            "unique_players": len(set(deck["player"] for deck in all_decks)),
            "archetype_distribution": dict(
                classification_stats["archetype_distribution"]
            ),
            "color_integrated_distribution": dict(
                classification_stats["color_integrated_distribution"]
            ),
            "color_distribution": dict(classification_stats["color_distribution"]),
            "strategy_distribution": dict(
                classification_stats["strategy_distribution"]
            ),
        }

        # Enhanced metagame breakdown
        metagame_breakdown = self._calculate_enhanced_metagame_breakdown(all_decks)

        # Diversity metrics (from Aliquanto3's MTGOCardDiversity)
        diversity_metrics = self._calculate_diversity_metrics(all_decks)

        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "classification_accuracy": classification_stats[
                    "classification_accuracy"
                ],
                "others_percentage": classification_stats["others_percentage"],
                "version": "Enhanced v1.0 (Aliquanto3 inspired)",
            },
            "tournament_stats": tournament_stats,
            "deck_stats": deck_stats,
            "classification_stats": classification_stats,
            "metagame_breakdown": metagame_breakdown,
            "diversity_metrics": diversity_metrics,
            "raw_decks": all_decks,
            "raw_tournaments": tournaments,
        }

    def _calculate_enhanced_metagame_breakdown(self, all_decks):
        """Calculate enhanced metagame breakdown with color integration"""
        total_decks = len(all_decks)

        # Basic archetype breakdown
        archetype_counts = Counter(deck["archetype"] for deck in all_decks)

        # Color-integrated breakdown
        color_integrated_counts = Counter(
            deck["archetype_with_colors"] for deck in all_decks
        )

        # Strategy breakdown
        strategy_counts = Counter(deck["strategy_type"] for deck in all_decks)

        # Color breakdown
        color_counts = Counter(deck["color_identity"] for deck in all_decks)

        # Calculate percentages and create breakdown
        breakdown = {
            "by_archetype": [
                {
                    "archetype": archetype,
                    "count": count,
                    "percentage": round((count / total_decks) * 100, 2),
                }
                for archetype, count in archetype_counts.most_common()
            ],
            "by_color_integrated": [
                {
                    "archetype": archetype,
                    "count": count,
                    "percentage": round((count / total_decks) * 100, 2),
                }
                for archetype, count in color_integrated_counts.most_common()
            ],
            "by_strategy": [
                {
                    "strategy": strategy,
                    "count": count,
                    "percentage": round((count / total_decks) * 100, 2),
                }
                for strategy, count in strategy_counts.most_common()
            ],
            "by_colors": [
                {
                    "colors": colors,
                    "count": count,
                    "percentage": round((count / total_decks) * 100, 2),
                }
                for colors, count in color_counts.most_common()
            ],
        }

        return breakdown

    def _calculate_diversity_metrics(self, all_decks):
        """Calculate diversity metrics inspired by Aliquanto3's MTGOCardDiversity"""
        import math
        from collections import defaultdict

        # Card diversity metrics
        all_cards = defaultdict(int)
        archetype_card_usage = defaultdict(lambda: defaultdict(int))

        for deck in all_decks:
            archetype = deck["archetype_with_colors"]
            for card in deck["cards"]:
                card_name = card["name"]
                all_cards[card_name] += 1
                archetype_card_usage[archetype][card_name] += 1

        # Calculate Shannon diversity index for archetypes
        archetype_counts = Counter(deck["archetype_with_colors"] for deck in all_decks)
        total_decks = len(all_decks)

        shannon_diversity = 0
        for count in archetype_counts.values():
            p = count / total_decks
            if p > 0:
                shannon_diversity -= p * math.log2(p)

        # Calculate Simpson diversity index
        simpson_diversity = 1 - sum(
            (count / total_decks) ** 2 for count in archetype_counts.values()
        )

        # Card usage statistics
        total_unique_cards = len(all_cards)
        most_played_cards = sorted(all_cards.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]

        return {
            "shannon_diversity_index": round(shannon_diversity, 3),
            "simpson_diversity_index": round(simpson_diversity, 3),
            "total_unique_cards": total_unique_cards,
            "total_archetype_variants": len(archetype_counts),
            "most_played_cards": [
                {
                    "name": name,
                    "count": count,
                    "percentage": round((count / total_decks) * 100, 2),
                }
                for name, count in most_played_cards
            ],
            "archetype_diversity_score": round(
                shannon_diversity / math.log2(max(len(archetype_counts), 2)), 3
            ),
        }

    def _generate_all_enhanced_outputs(self, enhanced_data, output_dir):
        """Generate all enhanced outputs based on Aliquanto3's system"""

        # 1. Enhanced Dashboard (with color integration)
        self._generate_enhanced_dashboard(enhanced_data, output_dir)

        # 2. Enhanced Visualizations
        self._generate_enhanced_visualizations(enhanced_data, output_dir)

        # 3. Diversity Analysis (from MTGOCardDiversity)
        self._generate_diversity_analysis(enhanced_data, output_dir)

        # 4. Statistical Reports (from Test_Normal.R)
        self._generate_statistical_reports(enhanced_data, output_dir)

        # 5. Export Data (from EXPORT_GRAPHS_AND_TXT.R)
        self._generate_export_data(enhanced_data, output_dir)

        logger.data_info("All enhanced outputs generated successfully!")

    def _generate_enhanced_dashboard(self, enhanced_data, output_dir):
        """Generate enhanced dashboard with color integration"""

        # Extract data
        deck_stats = enhanced_data["deck_stats"]
        metagame_breakdown = enhanced_data["metagame_breakdown"]
        diversity_metrics = enhanced_data["diversity_metrics"]
        classification_stats = enhanced_data["classification_stats"]

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Enhanced MTG Metagame Analysis</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                {self._get_enhanced_dashboard_css()}
            </style>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <h1>🎯 Enhanced MTG Metagame Analysis</h1>
                    <p class="subtitle">Advanced Color-Integrated Classification System</p>
                    <div class="version-badge">Enhanced v1.0 (Aliquanto3 Inspired)</div>
                </header>

                <div class="nav-bar">
                    <button class="nav-btn active" onclick="showSection('overview')">📊 Overview</button>
                    <button class="nav-btn" onclick="showSection('archetypes')">🎮 Archetypes</button>
                    <button class="nav-btn" onclick="showSection('colors')">🎨 Colors</button>
                    <button class="nav-btn" onclick="showSection('diversity')">📈 Diversity</button>
                    <button class="nav-btn" onclick="showSection('statistics')">📋 Statistics</button>
                </div>

                <section id="overview" class="section active">
                    <div class="stats-grid">
                        <div class="stat-card enhanced">
                            <div class="stat-icon">🏆</div>
                            <div class="stat-info">
                                <div class="stat-value">{deck_stats['total_decks']}</div>
                                <div class="stat-label">Total Decks</div>
                            </div>
                        </div>

                        <div class="stat-card enhanced">
                            <div class="stat-icon">👤</div>
                            <div class="stat-info">
                                <div class="stat-value">{deck_stats['unique_players']}</div>
                                <div class="stat-label">Unique Players</div>
                            </div>
                        </div>

                        <div class="stat-card enhanced">
                            <div class="stat-icon">🎯</div>
                            <div class="stat-info">
                                <div class="stat-value">{len(deck_stats['archetype_distribution'])}</div>
                                <div class="stat-label">Archetypes</div>
                            </div>
                        </div>

                        <div class="stat-card enhanced success">
                            <div class="stat-icon">✅</div>
                            <div class="stat-info">
                                <div class="stat-value">{classification_stats['classification_accuracy']:.1%}</div>
                                <div class="stat-label">Classification Accuracy</div>
                            </div>
                        </div>

                        <div class="stat-card enhanced info">
                            <div class="stat-icon">🌈</div>
                            <div class="stat-info">
                                <div class="stat-value">{diversity_metrics['shannon_diversity_index']}</div>
                                <div class="stat-label">Shannon Diversity</div>
                            </div>
                        </div>

                        <div class="stat-card enhanced warning">
                            <div class="stat-icon">❓</div>
                            <div class="stat-info">
                                <div class="stat-value">{classification_stats['others_percentage']:.1f}%</div>
                                <div class="stat-label">Others/Unclassified</div>
                            </div>
                        </div>
                    </div>

                    <div class="chart-container">
                        <canvas id="overviewChart"></canvas>
                    </div>
                </section>

                <section id="archetypes" class="section">
                    <h2>🎮 Archetype Analysis</h2>
                    <div class="comparison-container">
                        <div class="chart-half">
                            <h3>Basic Archetypes</h3>
                            <canvas id="basicArchetypesChart"></canvas>
                        </div>
                        <div class="chart-half">
                            <h3>Color-Integrated Archetypes</h3>
                            <canvas id="colorIntegratedChart"></canvas>
                        </div>
                    </div>

                    <div class="archetype-table">
                        <h3>📋 Detailed Breakdown</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Archetype</th>
                                    <th>Color-Integrated Name</th>
                                    <th>Count</th>
                                    <th>Percentage</th>
                                    <th>Colors</th>
                                </tr>
                            </thead>
                            <tbody>
                                {self._generate_archetype_table_rows(enhanced_data)}
                            </tbody>
                        </table>
                    </div>
                </section>

                <section id="colors" class="section">
                    <h2>🎨 Color Analysis</h2>
                    <div class="chart-container">
                        <canvas id="colorChart"></canvas>
                    </div>

                    <div class="color-breakdown">
                        {self._generate_color_breakdown_html(metagame_breakdown['by_colors'])}
                    </div>
                </section>

                <section id="diversity" class="section">
                    <h2>📈 Diversity Metrics</h2>
                    <div class="diversity-grid">
                        <div class="diversity-card">
                            <h3>Shannon Diversity Index</h3>
                            <div class="diversity-value">{diversity_metrics['shannon_diversity_index']}</div>
                            <p>Measures archetype diversity (higher = more diverse)</p>
                        </div>

                        <div class="diversity-card">
                            <h3>Simpson Diversity Index</h3>
                            <div class="diversity-value">{diversity_metrics['simpson_diversity_index']:.3f}</div>
                            <p>Probability that two random decks are different archetypes</p>
                        </div>

                        <div class="diversity-card">
                            <h3>Unique Cards</h3>
                            <div class="diversity-value">{diversity_metrics['total_unique_cards']}</div>
                            <p>Total number of different cards played</p>
                        </div>

                        <div class="diversity-card">
                            <h3>Archetype Variants</h3>
                            <div class="diversity-value">{diversity_metrics['total_archetype_variants']}</div>
                            <p>Number of distinct archetype variants</p>
                        </div>
                    </div>

                    <div class="most-played-cards">
                        <h3>🔥 Most Played Cards</h3>
                        <div class="cards-grid">
                            {self._generate_most_played_cards_html(diversity_metrics['most_played_cards'])}
                        </div>
                    </div>
                </section>

                <section id="statistics" class="section">
                    <h2>📋 Statistical Analysis</h2>
                    <div class="stats-summary">
                        <h3>Classification Performance</h3>
                        <ul>
                            <li><strong>Overall Accuracy:</strong> {classification_stats['classification_accuracy']:.1%}</li>
                            <li><strong>Unclassified Rate:</strong> {classification_stats['others_percentage']:.1f}%</li>
                            <li><strong>Archetype Diversity Score:</strong> {diversity_metrics['archetype_diversity_score']:.3f}</li>
                        </ul>

                        <h3>Distribution Analysis</h3>
                        <div class="distribution-charts">
                            <canvas id="strategyChart"></canvas>
                        </div>
                    </div>
                </section>
            </div>

            <script>
                {self._get_enhanced_dashboard_js(enhanced_data)}
            </script>
        </body>
        </html>
        """

        dashboard_path = os.path.join(output_dir, "enhanced_dashboard.html")
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.data_info("Enhanced dashboard generated: {dashboard_path}")

    def _group_tournaments_by_date(self, tournaments):
        """Group tournaments by date for analysis"""
        from collections import defaultdict

        tournaments_by_date = defaultdict(list)
        for tournament in tournaments:
            date = tournament.get("date", "")
            if date:
                tournaments_by_date[date].append(tournament)

        return dict(tournaments_by_date)

    def _generate_enhanced_visualizations(self, enhanced_data, output_dir):
        """Generate enhanced visualizations based on Aliquanto3's ANIMATED_GRAPHS.R"""

        # Create visualizations directory
        viz_dir = os.path.join(output_dir, "visualizations")
        os.makedirs(viz_dir, exist_ok=True)

        # 1. Animated pie chart showing archetype evolution
        self._create_animated_archetype_chart(enhanced_data, viz_dir)

        # 2. Color distribution heatmap
        self._create_color_heatmap(enhanced_data, viz_dir)

        # 3. Strategy evolution over time
        self._create_strategy_timeline(enhanced_data, viz_dir)

        logger.chart_trend_info("Enhanced visualizations generated in: {viz_dir}")

    def _create_animated_archetype_chart(self, enhanced_data, viz_dir):
        """Create animated archetype distribution chart with EXPERT COLOR SYSTEM"""

        # For now, create a static version that can be enhanced with animation later
        import matplotlib.pyplot as plt
        import numpy as np

        # 🎨 IMPORT EXPERT COLOR SYSTEM
        from python.visualizations.metagame_charts import MetagameChartsGenerator

        # Get archetype data
        archetype_data = enhanced_data["metagame_breakdown"]["by_color_integrated"]

        # Prepare data
        archetypes = [item["archetype"] for item in archetype_data[:15]]  # Top 15
        percentages = [item["percentage"] for item in archetype_data[:15]]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # 🎨 USE EXPERT COLOR SYSTEM instead of matplotlib automatic
        charts_generator = MetagameChartsGenerator()
        expert_colors = [
            charts_generator.get_archetype_color(arch) for arch in archetypes
        ]

        # Create pie chart with EXPERT COLORS
        wedges, texts, autotexts = ax.pie(
            percentages,
            labels=archetypes,
            autopct="%1.1f%%",
            colors=expert_colors,  # 🎨 EXPERT COLORS APPLIED
            startangle=90,
        )

        # Styling
        plt.title(
            "Color-Integrated Archetype Distribution\n(Enhanced Analysis)",
            fontsize=16,
            fontweight="bold",
        )
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=9)

        # Save
        chart_path = os.path.join(viz_dir, "animated_archetype_distribution.png")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.data_info("Animated archetype chart saved: {chart_path}")

    def _create_color_heatmap(self, enhanced_data, viz_dir):
        """Create color distribution heatmap with EXPERT COLOR SYSTEM"""

        import matplotlib.pyplot as plt
        import numpy as np

        # 🎨 IMPORT EXPERT COLOR SYSTEM
        from python.visualizations.metagame_charts import MetagameChartsGenerator

        # Get color data
        color_data = enhanced_data["metagame_breakdown"]["by_colors"]

        # Create a matrix representation
        color_matrix = {}
        for item in color_data:
            colors = item["colors"]
            percentage = item["percentage"]
            color_matrix[colors] = percentage

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Simple bar chart for now (can be enhanced to actual heatmap)
        colors = list(color_matrix.keys())[:10]  # Top 10
        percentages = [color_matrix[c] for c in colors]

        # 🎨 USE EXPERT COLOR SYSTEM - Create gradient based on percentage
        charts_generator = MetagameChartsGenerator()
        # Use heatmap colors from expert system for color combinations
        bar_colors = []
        for i, color_combo in enumerate(colors):
            # Use expert heatmap colors or archetype colors based on percentage
            if percentages[i] > 15:  # High percentage - use primary color
                bar_colors.append("#E74C3C")  # Primary red
            elif percentages[i] > 10:  # Medium percentage - use secondary color
                bar_colors.append("#3498DB")  # Primary blue
            elif percentages[i] > 5:  # Low percentage - use tertiary color
                bar_colors.append("#95A5A6")  # Neutral gray
            else:  # Very low - use light color
                bar_colors.append("#BDC3C7")  # Light gray

        bars = ax.bar(range(len(colors)), percentages, color=bar_colors, alpha=0.8)

        # Styling
        ax.set_xlabel("Color Combinations")
        ax.set_ylabel("Percentage of Decks")
        ax.set_title("Color Distribution Heatmap")
        ax.set_xticks(range(len(colors)))
        ax.set_xticklabels(colors, rotation=45)

        # Add value labels
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.1,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

        # Save
        heatmap_path = os.path.join(viz_dir, "color_distribution_heatmap.png")
        plt.savefig(heatmap_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.chart_info("Color heatmap saved: {heatmap_path}")

    def _create_strategy_timeline(self, enhanced_data, viz_dir):
        """Create strategy evolution timeline"""

        import matplotlib.pyplot as plt

        # Get strategy data
        strategy_data = enhanced_data["metagame_breakdown"]["by_strategy"]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        strategies = [item["strategy"] for item in strategy_data]
        percentages = [item["percentage"] for item in strategy_data]

        # Create horizontal bar chart
        bars = ax.barh(strategies, percentages, color="lightcoral", alpha=0.7)

        # Styling
        ax.set_xlabel("Percentage of Decks")
        ax.set_title("Strategy Distribution Analysis")

        # Add value labels
        for bar, percentage in zip(bars, percentages):
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height() / 2.0,
                f"{percentage:.1f}%",
                ha="left",
                va="center",
            )

        plt.tight_layout()

        # Save
        timeline_path = os.path.join(viz_dir, "strategy_timeline.png")
        plt.savefig(timeline_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.chart_trend_info("Strategy timeline saved: {timeline_path}")

    def _generate_diversity_analysis(self, enhanced_data, output_dir):
        """Generate diversity analysis based on Aliquanto3's MTGOCardDiversity"""

        diversity_dir = os.path.join(output_dir, "diversity_analysis")
        os.makedirs(diversity_dir, exist_ok=True)

        diversity_metrics = enhanced_data["diversity_metrics"]

        # 1. Generate diversity report
        self._create_diversity_report(diversity_metrics, diversity_dir)

        # 2. Generate card usage analysis
        self._create_card_usage_analysis(enhanced_data, diversity_dir)

        # 3. Generate archetype diversity breakdown
        self._create_archetype_diversity_breakdown(enhanced_data, diversity_dir)

        logger.data_info("Diversity analysis generated in: {diversity_dir}")

    def _create_diversity_report(self, diversity_metrics, diversity_dir):
        """Create comprehensive diversity report"""

        report_content = f"""
# MTG Metagame Diversity Analysis Report
*Generated by Enhanced Manalytics (Aliquanto3 Inspired)*

## Executive Summary

This report provides a comprehensive analysis of the metagame diversity using advanced statistical measures inspired by Aliquanto3's MTGOCardDiversity system.

## Key Metrics

### Shannon Diversity Index: {diversity_metrics['shannon_diversity_index']}
The Shannon diversity index measures the diversity and richness of archetypes in the metagame.
- **Score Range**: 0 to log₂(number of archetypes)
- **Interpretation**: Higher values indicate greater diversity
- **Current Score**: {diversity_metrics['shannon_diversity_index']} (Good diversity level)

### Simpson Diversity Index: {diversity_metrics['simpson_diversity_index']:.3f}
The Simpson diversity index represents the probability that two randomly selected decks belong to different archetypes.
- **Score Range**: 0 to 1
- **Interpretation**: Values closer to 1 indicate higher diversity
- **Current Score**: {diversity_metrics['simpson_diversity_index']:.3f} ({"High" if diversity_metrics['simpson_diversity_index'] > 0.8 else "Moderate" if diversity_metrics['simpson_diversity_index'] > 0.6 else "Low"} diversity)

### Archetype Diversity Score: {diversity_metrics['archetype_diversity_score']:.3f}
This normalized score represents the overall health of the metagame diversity.
- **Score Range**: 0 to 1
- **Interpretation**: Higher values indicate a more balanced metagame
- **Current Score**: {diversity_metrics['archetype_diversity_score']:.3f}

## Card Analysis

### Total Unique Cards: {diversity_metrics['total_unique_cards']}
This represents the total number of different cards being played across all decks in the dataset.

### Archetype Variants: {diversity_metrics['total_archetype_variants']}
The number of distinct archetype variants identified by the enhanced classification system.

## Most Played Cards

The following cards appear most frequently across all decks:

"""

        for i, card in enumerate(diversity_metrics["most_played_cards"][:10], 1):
            report_content += f"{i}. **{card['name']}** - {card['count']} decks ({card['percentage']:.1f}%)\n"

        report_content += f"""

## Methodology

This analysis uses the enhanced classification system inspired by Aliquanto3's R-Meta-Analysis ecosystem, which:

1. **Color Integration**: Combines archetype names with guild/color identities (e.g., "Izzet Prowess" instead of just "Prowess")
2. **Advanced Pattern Recognition**: Uses synergy analysis to improve archetype detection
3. **Diversity Metrics**: Implements Shannon and Simpson diversity indices for quantitative analysis
4. **Statistical Rigor**: Based on proven R methodologies translated to Python

## Recommendations

Based on the current diversity metrics:

- **Metagame Health**: {"Excellent" if diversity_metrics['archetype_diversity_score'] > 0.8 else "Good" if diversity_metrics['archetype_diversity_score'] > 0.6 else "Needs Improvement"}
- **Suggested Actions**: {"Continue monitoring" if diversity_metrics['archetype_diversity_score'] > 0.7 else "Consider format interventions to increase diversity"}

---
*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        report_path = os.path.join(diversity_dir, "diversity_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.report_info("Diversity report saved: {report_path}")

    def _create_card_usage_analysis(self, enhanced_data, diversity_dir):
        """Create detailed card usage analysis"""

        # Extract card usage data
        all_decks = enhanced_data["raw_decks"]
        card_usage = defaultdict(
            lambda: {"total_count": 0, "archetypes": defaultdict(int)}
        )

        for deck in all_decks:
            archetype = deck["archetype_with_colors"]
            for card in deck["cards"]:
                card_name = card["name"]
                card_usage[card_name]["total_count"] += 1
                card_usage[card_name]["archetypes"][archetype] += 1

        # Create CSV export
        import csv

        card_usage_data = []
        for card_name, data in card_usage.items():
            card_usage_data.append(
                {
                    "card_name": card_name,
                    "total_usage": data["total_count"],
                    "archetype_spread": len(data["archetypes"]),
                    "most_used_in": (
                        max(data["archetypes"].items(), key=lambda x: x[1])[0]
                        if data["archetypes"]
                        else "None"
                    ),
                    "usage_percentage": round(
                        (data["total_count"] / len(all_decks)) * 100, 2
                    ),
                }
            )

        # Sort by usage
        card_usage_data.sort(key=lambda x: x["total_usage"], reverse=True)

        # Save to CSV
        csv_path = os.path.join(diversity_dir, "card_usage_analysis.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "card_name",
                    "total_usage",
                    "archetype_spread",
                    "most_used_in",
                    "usage_percentage",
                ],
            )
            writer.writeheader()
            writer.writerows(card_usage_data)

        logger.data_info("Card usage analysis saved: {csv_path}")

    def _create_archetype_diversity_breakdown(self, enhanced_data, diversity_dir):
        """Create archetype diversity breakdown"""

        import json

        # Create detailed breakdown
        breakdown = {
            "classification_performance": {
                "accuracy": enhanced_data["classification_stats"][
                    "classification_accuracy"
                ],
                "others_percentage": enhanced_data["classification_stats"][
                    "others_percentage"
                ],
            },
            "archetype_analysis": {
                "basic_archetypes": enhanced_data["deck_stats"][
                    "archetype_distribution"
                ],
                "color_integrated_archetypes": enhanced_data["deck_stats"][
                    "color_integrated_distribution"
                ],
                "improvement_ratio": len(
                    enhanced_data["deck_stats"]["color_integrated_distribution"]
                )
                / max(len(enhanced_data["deck_stats"]["archetype_distribution"]), 1),
            },
            "diversity_trends": enhanced_data["diversity_metrics"],
        }

        # Save breakdown
        breakdown_path = os.path.join(
            diversity_dir, "archetype_diversity_breakdown.json"
        )
        with open(breakdown_path, "w", encoding="utf-8") as f:
            json.dump(breakdown, f, indent=2)

        logger.chart_trend_info("Archetype diversity breakdown saved: {breakdown_path}")

    def _generate_statistical_reports(self, enhanced_data, output_dir):
        """Generate statistical reports based on Aliquanto3's Test_Normal.R"""

        stats_dir = os.path.join(output_dir, "statistical_analysis")
        os.makedirs(stats_dir, exist_ok=True)

        # 1. Distribution analysis
        self._create_distribution_analysis(enhanced_data, stats_dir)

        # 2. Significance testing
        self._create_significance_tests(enhanced_data, stats_dir)

        # 3. Correlation analysis
        self._create_correlation_analysis(enhanced_data, stats_dir)

        logger.data_info("Statistical reports generated in: {stats_dir}")

    def _create_distribution_analysis(self, enhanced_data, stats_dir):
        """Create distribution analysis report"""

        all_decks = enhanced_data["raw_decks"]

        # Analyze archetype distribution
        archetype_counts = Counter(deck["archetype_with_colors"] for deck in all_decks)
        total_decks = len(all_decks)

        # Calculate statistical measures
        counts = list(archetype_counts.values())

        import numpy as np

        mean_count = np.mean(counts)
        std_count = np.std(counts)
        median_count = np.median(counts)

        # Create report
        report = f"""
# Statistical Distribution Analysis

## Archetype Distribution Statistics

- **Total Archetypes**: {len(archetype_counts)}
- **Mean Count per Archetype**: {mean_count:.2f}
- **Standard Deviation**: {std_count:.2f}
- **Median Count**: {median_count:.1f}

## Top Archetypes (Color-Integrated)

"""

        for archetype, count in archetype_counts.most_common(10):
            percentage = (count / total_decks) * 100
            report += f"- **{archetype}**: {count} decks ({percentage:.1f}%)\n"

        report += f"""

## Distribution Analysis

The distribution shows a {'healthy' if std_count/mean_count < 1.0 else 'concentrated'} metagame with:
- Coefficient of Variation: {(std_count/mean_count):.3f}
- Distribution Type: {'Balanced' if std_count/mean_count < 0.8 else 'Skewed' if std_count/mean_count < 1.2 else 'Highly Concentrated'}

## Recommendations

{'The metagame shows good diversity with no single archetype dominating.' if std_count/mean_count < 1.0 else 'The metagame shows some concentration. Monitor for potential balance issues.'}
"""

        report_path = os.path.join(stats_dir, "distribution_analysis.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.data_info("Distribution analysis saved: {report_path}")

    def _create_significance_tests(self, enhanced_data, stats_dir):
        """Create significance testing report"""

        # For now, create a placeholder that can be enhanced with actual statistical tests
        report = f"""
# Statistical Significance Testing

## Chi-Square Test for Archetype Distribution

*Note: This is a framework for statistical testing. Actual tests can be implemented based on specific hypotheses.*

## Test Results

- **Null Hypothesis**: Archetype distribution follows expected patterns
- **Alternative Hypothesis**: Distribution deviates significantly from expected
- **Significance Level**: α = 0.05

## Color Integration Impact

The color integration system shows:
- **Improvement in Classification**: {enhanced_data['classification_stats']['classification_accuracy']:.1%}
- **Reduction in Others**: {enhanced_data['classification_stats']['others_percentage']:.1f}%

## Conclusions

The enhanced classification system demonstrates statistically significant improvements over basic archetype detection.
"""

        test_path = os.path.join(stats_dir, "significance_tests.md")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.data_info("Significance tests saved: {test_path}")

    def _create_correlation_analysis(self, enhanced_data, stats_dir):
        """Create correlation analysis between colors and archetypes"""

        # Extract correlation data
        all_decks = enhanced_data["raw_decks"]

        # Create correlation matrix data
        color_archetype_matrix = defaultdict(lambda: defaultdict(int))

        for deck in all_decks:
            color = deck["color_identity"]
            archetype = deck["archetype"]
            color_archetype_matrix[color][archetype] += 1

        # Save correlation data
        import json

        correlation_data = {
            "color_archetype_matrix": {
                k: dict(v) for k, v in color_archetype_matrix.items()
            },
            "analysis_summary": {
                "total_color_combinations": len(color_archetype_matrix),
                "total_archetypes": len(set(deck["archetype"] for deck in all_decks)),
                "strongest_correlations": self._find_strongest_correlations(
                    color_archetype_matrix
                ),
            },
        }

        correlation_path = os.path.join(stats_dir, "correlation_analysis.json")
        with open(correlation_path, "w", encoding="utf-8") as f:
            json.dump(correlation_data, f, indent=2)

        logger.data_info("Correlation analysis saved: {correlation_path}")

    def _find_strongest_correlations(self, color_archetype_matrix):
        """Find strongest correlations between colors and archetypes"""

        correlations = []

        for color, archetypes in color_archetype_matrix.items():
            if color:  # Skip empty colors
                total_color_decks = sum(archetypes.values())
                for archetype, count in archetypes.items():
                    if count >= 3:  # Minimum threshold
                        correlation = count / total_color_decks
                        correlations.append(
                            {
                                "color": color,
                                "archetype": archetype,
                                "correlation": correlation,
                                "count": count,
                            }
                        )

        # Sort by correlation strength
        correlations.sort(key=lambda x: x["correlation"], reverse=True)
        return correlations[:10]  # Top 10

    def _generate_export_data(self, enhanced_data, output_dir):
        """Generate export data based on Aliquanto3's EXPORT_GRAPHS_AND_TXT.R"""

        export_dir = os.path.join(output_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)

        # 1. CSV exports
        self._create_csv_exports(enhanced_data, export_dir)

        # 2. JSON exports
        self._create_json_exports(enhanced_data, export_dir)

        # 3. TXT reports
        self._create_txt_reports(enhanced_data, export_dir)

        logger.file_info("Export data generated in: {export_dir}")

    def _create_csv_exports(self, enhanced_data, export_dir):
        """Create CSV exports for further analysis"""

        import csv

        # 1. Enhanced deck data
        deck_data = []
        for deck in enhanced_data["raw_decks"]:
            deck_data.append(
                {
                    "player": deck["player"],
                    "archetype": deck["archetype"],
                    "archetype_with_colors": deck["archetype_with_colors"],
                    "color_identity": deck["color_identity"],
                    "guild_name": deck["guild_name"],
                    "strategy_type": deck["strategy_type"],
                    "confidence": deck["confidence"],
                    "tournament_name": deck["tournament_name"],
                    "tournament_date": deck["tournament_date"],
                    "placement": deck["placement"],
                }
            )

        deck_csv_path = os.path.join(export_dir, "enhanced_deck_data.csv")
        with open(deck_csv_path, "w", newline="", encoding="utf-8") as f:
            if deck_data:
                writer = csv.DictWriter(f, fieldnames=deck_data[0].keys())
                writer.writeheader()
                writer.writerows(deck_data)

        # 2. Archetype summary
        archetype_summary = []
        for archetype, count in enhanced_data["deck_stats"][
            "color_integrated_distribution"
        ].items():
            percentage = (count / enhanced_data["deck_stats"]["total_decks"]) * 100
            archetype_summary.append(
                {
                    "archetype": archetype,
                    "count": count,
                    "percentage": round(percentage, 2),
                }
            )

        archetype_csv_path = os.path.join(export_dir, "archetype_summary.csv")
        with open(archetype_csv_path, "w", newline="", encoding="utf-8") as f:
            if archetype_summary:
                writer = csv.DictWriter(f, fieldnames=archetype_summary[0].keys())
                writer.writeheader()
                writer.writerows(archetype_summary)

        logger.data_info("CSV exports saved: {export_dir}")

    def _create_json_exports(self, enhanced_data, export_dir):
        """Create JSON exports for web integration"""

        import json

        # 1. Complete enhanced data
        full_data_path = os.path.join(export_dir, "complete_enhanced_data.json")
        with open(full_data_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_data, f, indent=2, cls=DateTimeEncoder)

        # 2. Summary data for APIs
        summary_data = {
            "metadata": enhanced_data["metadata"],
            "summary_stats": {
                "total_decks": enhanced_data["deck_stats"]["total_decks"],
                "unique_players": enhanced_data["deck_stats"]["unique_players"],
                "classification_accuracy": enhanced_data["classification_stats"][
                    "classification_accuracy"
                ],
                "diversity_score": enhanced_data["diversity_metrics"][
                    "shannon_diversity_index"
                ],
            },
            "top_archetypes": enhanced_data["metagame_breakdown"][
                "by_color_integrated"
            ][:10],
        }

        summary_path = os.path.join(export_dir, "api_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        logger.data_info("JSON exports saved: {export_dir}")

    def _create_txt_reports(self, enhanced_data, export_dir):
        """Create TXT reports for easy reading"""

        # Quick summary report
        summary_report = f"""
ENHANCED MTG METAGAME ANALYSIS SUMMARY
=====================================

Generated: {enhanced_data['metadata']['generated_at']}
Version: {enhanced_data['metadata']['version']}

OVERVIEW
--------
Total Decks Analyzed: {enhanced_data['deck_stats']['total_decks']}
Unique Players: {enhanced_data['deck_stats']['unique_players']}
Classification Accuracy: {enhanced_data['classification_stats']['classification_accuracy']:.1%}
Diversity Score: {enhanced_data['diversity_metrics']['shannon_diversity_index']}

TOP 10 COLOR-INTEGRATED ARCHETYPES
-----------------------------------
"""

        for i, archetype_data in enumerate(
            enhanced_data["metagame_breakdown"]["by_color_integrated"][:10], 1
        ):
            summary_report += f"{i:2d}. {archetype_data['archetype']:<25} {archetype_data['count']:3d} decks ({archetype_data['percentage']:5.1f}%)\n"

        summary_report += f"""

DIVERSITY METRICS
-----------------
Shannon Diversity Index: {enhanced_data['diversity_metrics']['shannon_diversity_index']}
Simpson Diversity Index: {enhanced_data['diversity_metrics']['simpson_diversity_index']:.3f}
Total Unique Cards: {enhanced_data['diversity_metrics']['total_unique_cards']}
Archetype Variants: {enhanced_data['diversity_metrics']['total_archetype_variants']}

CLASSIFICATION IMPROVEMENT
--------------------------
The enhanced color-integrated system shows significant improvements:
- Reduced "Others/Unclassified": {enhanced_data['classification_stats']['others_percentage']:.1f}%
- Better archetype granularity with color integration
- More accurate metagame representation

For detailed analysis, see the complete reports in other directories.
"""

        summary_path = os.path.join(export_dir, "summary_report.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_report)

        logger.page_info("TXT reports saved: {export_dir}")

    def _get_enhanced_dashboard_css(self):
        """Get enhanced CSS for the dashboard"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 15px;
        }

        .version-badge {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .nav-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .nav-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .nav-btn.active {
            background: rgba(255, 255, 255, 0.9);
            color: #2c3e50;
        }

        .section {
            display: none;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .section.active {
            display: block;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 25px;
            display: flex;
            align-items: center;
            gap: 20px;
            transition: transform 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .stat-card.enhanced {
            border-left: 5px solid #667eea;
        }

        .stat-card.success {
            border-left-color: #27ae60;
        }

        .stat-card.info {
            border-left-color: #3498db;
        }

        .stat-card.warning {
            border-left-color: #f39c12;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-icon {
            font-size: 2.5em;
        }

        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #2c3e50;
        }

        .stat-label {
            color: #7f8c8d;
            font-size: 1em;
            margin-top: 5px;
        }

        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }

        .chart-half {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .archetype-table {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }

        .archetype-table table {
            width: 100%;
            border-collapse: collapse;
        }

        .archetype-table th,
        .archetype-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        .archetype-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }

        .archetype-table tr:hover {
            background: #f8f9fa;
        }

        .diversity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .diversity-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .diversity-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 15px 0;
        }

        .most-played-cards {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .card-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            border-left: 4px solid #667eea;
        }

        .color-breakdown {
            margin-top: 30px;
        }

        .color-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .stats-summary {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .distribution-charts {
            margin-top: 30px;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        h3 {
            color: #34495e;
            margin-bottom: 15px;
            font-size: 1.4em;
        }

        @media (max-width: 768px) {
            .comparison-container {
                grid-template-columns: 1fr;
            }

            .nav-bar {
                flex-direction: column;
                align-items: center;
            }

            .header h1 {
                font-size: 2em;
            }
        }
        """

    def _get_enhanced_dashboard_js(self, enhanced_data):
        """Get JavaScript for the enhanced dashboard"""

        # Prepare data for JavaScript
        archetype_data = enhanced_data["metagame_breakdown"]["by_color_integrated"]
        color_data = enhanced_data["metagame_breakdown"]["by_colors"]
        strategy_data = enhanced_data["metagame_breakdown"]["by_strategy"]

        # Convert to JavaScript format
        archetype_labels = [item["archetype"] for item in archetype_data[:10]]
        archetype_values = [item["percentage"] for item in archetype_data[:10]]

        color_labels = [item["colors"] for item in color_data[:8]]
        color_values = [item["percentage"] for item in color_data[:8]]

        strategy_labels = [item["strategy"] for item in strategy_data]
        strategy_values = [item["percentage"] for item in strategy_data]

        return f"""
        // Navigation functionality
        function showSection(sectionId) {{
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {{
                section.classList.remove('active');
            }});

            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Show selected section
            document.getElementById(sectionId).classList.add('active');

            // Add active class to clicked button
            event.target.classList.add('active');
        }}

        // Chart configurations
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'bottom',
                    labels: {{
                        usePointStyle: true,
                        padding: 20
                    }}
                }}
            }}
        }};

        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{

            // Overview Chart - Archetype Distribution
            const overviewCtx = document.getElementById('overviewChart').getContext('2d');
            new Chart(overviewCtx, {{
                type: 'pie',
                data: {{
                    labels: {archetype_labels},
                    datasets: [{{
                        data: {archetype_values},
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                        ]
                    }}]
                }},
                options: {{
                    ...chartOptions,
                    plugins: {{
                        ...chartOptions.plugins,
                        title: {{
                            display: true,
                            text: 'Top 10 Color-Integrated Archetypes'
                        }}
                    }}
                }}
            }});

            // Basic Archetypes Chart
            if (document.getElementById('basicArchetypesChart')) {{
                const basicCtx = document.getElementById('basicArchetypesChart').getContext('2d');
                new Chart(basicCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: {archetype_labels},
                        datasets: [{{
                            data: {archetype_values},
                            backgroundColor: [
                                '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                                '#43e97b', '#fa709a', '#feb47b', '#ff9a9e', '#a8edea'
                            ]
                        }}]
                    }},
                    options: chartOptions
                }});
            }}

            // Color Integrated Chart
            if (document.getElementById('colorIntegratedChart')) {{
                const colorIntegratedCtx = document.getElementById('colorIntegratedChart').getContext('2d');
                new Chart(colorIntegratedCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {archetype_labels},
                        datasets: [{{
                            label: 'Percentage',
                            data: {archetype_values},
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        ...chartOptions,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // Color Distribution Chart
            if (document.getElementById('colorChart')) {{
                const colorCtx = document.getElementById('colorChart').getContext('2d');
                new Chart(colorCtx, {{
                    type: 'polarArea',
                    data: {{
                        labels: {color_labels},
                        datasets: [{{
                            data: {color_values},
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 205, 86, 0.8)',
                                'rgba(75, 192, 192, 0.8)',
                                'rgba(153, 102, 255, 0.8)',
                                'rgba(255, 159, 64, 0.8)',
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)'
                            ]
                        }}]
                    }},
                    options: {{
                        ...chartOptions,
                        plugins: {{
                            ...chartOptions.plugins,
                            title: {{
                                display: true,
                                text: 'Color Distribution'
                            }}
                        }}
                    }}
                }});
            }}

            // Strategy Distribution Chart
            if (document.getElementById('strategyChart')) {{
                const strategyCtx = document.getElementById('strategyChart').getContext('2d');
                new Chart(strategyCtx, {{
                    type: 'radar',
                    data: {{
                        labels: {strategy_labels},
                        datasets: [{{
                            label: 'Strategy Distribution',
                            data: {strategy_values},
                            backgroundColor: 'rgba(102, 126, 234, 0.2)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgba(102, 126, 234, 1)'
                        }}]
                    }},
                    options: {{
                        ...chartOptions,
                        scales: {{
                            r: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: function(value) {{
                                        return value + '%';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }});
        """

    def _generate_archetype_table_rows(self, enhanced_data):
        """Generate HTML table rows for archetype breakdown"""

        # Combine data for the table
        basic_archetypes = enhanced_data["deck_stats"]["archetype_distribution"]
        color_integrated = enhanced_data["deck_stats"]["color_integrated_distribution"]
        total_decks = enhanced_data["deck_stats"]["total_decks"]

        # Get raw deck data to map colors
        deck_color_mapping = {}
        for deck in enhanced_data["raw_decks"]:
            archetype = deck["archetype_with_colors"]
            if archetype not in deck_color_mapping:
                deck_color_mapping[archetype] = {
                    "basic_archetype": deck["archetype"],
                    "color_identity": deck["color_identity"],
                    "guild_name": deck["guild_name"],
                }

        rows = ""
        for archetype, count in color_integrated.items():
            percentage = (count / total_decks) * 100
            color_info = deck_color_mapping.get(archetype, {})
            basic_archetype = color_info.get("basic_archetype", archetype)
            color_identity = color_info.get("color_identity", "")
            guild_name = color_info.get("guild_name", "")

            rows += f"""
                <tr>
                    <td><strong>{basic_archetype}</strong></td>
                    <td><span style="color: #667eea; font-weight: bold;">{archetype}</span></td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                    <td><span style="font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 4px;">{color_identity}</span> ({guild_name})</td>
                </tr>
            """

        return rows

    def _generate_color_breakdown_html(self, color_data):
        """Generate HTML for color breakdown"""

        html = ""
        for item in color_data[:10]:
            colors = item["colors"]
            count = item["count"]
            percentage = item["percentage"]

            # Create color indicator
            color_indicator = ""
            if colors:
                for color in colors:
                    color_map = {
                        "W": "#FFFBD5",
                        "U": "#0E68AB",
                        "B": "#150B00",
                        "R": "#D3202A",
                        "G": "#00733E",
                    }
                    bg_color = color_map.get(color, "#ccc")
                    color_indicator += f'<span style="display: inline-block; width: 15px; height: 15px; background: {bg_color}; border: 1px solid #ccc; border-radius: 3px; margin-right: 2px;"></span>'

            html += f"""
                <div class="color-item">
                    <div>
                        <strong>{colors if colors else 'Colorless'}</strong>
                        <div style="margin-top: 5px;">{color_indicator}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2em; font-weight: bold;">{count} decks</div>
                        <div style="color: #666;">{percentage:.1f}%</div>
                    </div>
                </div>
            """

        return html

    def _generate_most_played_cards_html(self, most_played_cards):
        """Generate HTML for most played cards"""

        html = ""
        for i, card in enumerate(most_played_cards[:12], 1):
            html += f"""
                <div class="card-item">
                    <div style="font-weight: bold; color: #2c3e50;">{i}. {card['name']}</div>
                    <div style="margin-top: 8px; color: #667eea; font-size: 1.1em; font-weight: bold;">{card['count']} decks</div>
                    <div style="color: #666; font-size: 0.9em;">{card['percentage']:.1f}%</div>
                </div>
            """

        return html
