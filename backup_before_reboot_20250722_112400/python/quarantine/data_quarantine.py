"""
Data quarantine system for identifying and handling suspicious tournament data.
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..schema.validation_result import ValidationResult

logger = logging.getLogger(__name__)


class DataQuarantine:
    """System for validating and quarantining suspicious tournament data."""

    def __init__(self, threshold_config: Dict[str, Any]):
        """
        Initialize data quarantine system.

        Args:
            threshold_config: Configuration for validation thresholds
        """
        self.thresholds = {
            "max_unknown_rate": 0.3,  # 30% max unknown archetypes
            "min_players": 8,  # Minimum players for valid tournament
            "max_players": 5000,  # Maximum reasonable players
            "min_rounds": 3,  # Minimum rounds
            "max_rounds": 20,  # Maximum reasonable rounds
            "min_win_rate": 0.0,  # Minimum win rate
            "max_win_rate": 1.0,  # Maximum win rate
            "max_duplicate_rate": 0.1,  # 10% max duplicate players
            "min_deck_size": 40,  # Minimum deck size (Limited)
            "max_deck_size": 250,  # Maximum reasonable deck size
            "max_sideboard_size": 15,  # Maximum sideboard size
            **threshold_config,
        }

        # Statistical thresholds
        self.statistical_thresholds = {
            "win_rate_stddev_threshold": 3.0,  # Standard deviations from mean
            "archetype_distribution_threshold": 0.05,  # Minimum expected frequency
            "round_time_threshold": 120,  # Minutes per round
        }

        self.quarantine_history = []

    def validate_tournament(self, tournament: Dict[str, Any]) -> ValidationResult:
        """
        Validate tournament data for quality issues.

        Args:
            tournament: Tournament data to validate

        Returns:
            ValidationResult with validation status and issues
        """
        try:
            issues = []
            severity = "info"

            # Basic structure validation
            structure_issues = self._validate_structure(tournament)
            issues.extend(structure_issues)

            # Data quality validation
            quality_issues = self._validate_data_quality(tournament)
            issues.extend(quality_issues)

            # Statistical anomaly detection
            statistical_issues = self._detect_statistical_anomalies(tournament)
            issues.extend(statistical_issues)

            # Determine severity
            if len(issues) > 3:
                severity = "quarantine"
            elif len(issues) > 1:
                severity = "warning"
            elif any("critical" in issue.lower() for issue in issues):
                severity = "critical"

            is_valid = severity not in ["quarantine", "critical"]

            # Log quarantine decision
            if severity == "quarantine":
                self._log_quarantine(tournament, issues)

            return ValidationResult(
                is_valid=is_valid,
                issues=issues,
                severity=severity,
                details={
                    "tournament_id": tournament.get("tournament_id"),
                    "player_count": len(tournament.get("players", [])),
                    "unknown_rate": self.calculate_unknown_rate(tournament),
                    "validation_timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Error validating tournament: {e}")
            return ValidationResult(
                is_valid=False, issues=[f"Validation error: {str(e)}"], severity="error"
            )

    def _validate_structure(self, tournament: Dict[str, Any]) -> List[str]:
        """Validate basic tournament structure."""
        issues = []

        # Required fields
        required_fields = ["tournament_id", "name", "date"]
        for field in required_fields:
            if field not in tournament or not tournament[field]:
                issues.append(f"Missing required field: {field}")

        # Players or standings data
        if not tournament.get("players") and not tournament.get("standings"):
            issues.append("Missing player/standings data")

        # Date validation
        if "date" in tournament:
            date_issue = self._validate_date(tournament["date"])
            if date_issue:
                issues.append(date_issue)

        return issues

    def _validate_data_quality(self, tournament: Dict[str, Any]) -> List[str]:
        """Validate data quality metrics."""
        issues = []

        # Player count validation
        players = tournament.get("players", [])
        player_count = len(players)

        if player_count < self.thresholds["min_players"]:
            issues.append(
                f"Too few players: {player_count} < {self.thresholds['min_players']}"
            )
        elif player_count > self.thresholds["max_players"]:
            issues.append(
                f"Too many players: {player_count} > {self.thresholds['max_players']}"
            )

        # Unknown archetype rate
        unknown_rate = self.calculate_unknown_rate(tournament)
        if unknown_rate > self.thresholds["max_unknown_rate"]:
            issues.append(
                f"High unknown archetype rate: {unknown_rate:.1%} > {self.thresholds['max_unknown_rate']:.1%}"
            )

        # Missing standings data
        if self.has_missing_standings(tournament):
            issues.append("Incomplete standings data")

        # Duplicate player detection
        duplicate_rate = self._calculate_duplicate_rate(tournament)
        if duplicate_rate > self.thresholds["max_duplicate_rate"]:
            issues.append(f"High duplicate player rate: {duplicate_rate:.1%}")

        # Deck validation
        deck_issues = self._validate_decks(tournament)
        issues.extend(deck_issues)

        # Round validation
        round_issues = self._validate_rounds(tournament)
        issues.extend(round_issues)

        return issues

    def _detect_statistical_anomalies(self, tournament: Dict[str, Any]) -> List[str]:
        """Detect statistical anomalies in tournament data."""
        issues = []

        try:
            players = tournament.get("players", [])
            if len(players) < 10:  # Need sufficient data for statistics
                return issues

            # Win rate distribution analysis
            win_rates = []
            for player in players:
                wins = player.get("wins", 0)
                losses = player.get("losses", 0)
                total_games = wins + losses
                if total_games > 0:
                    win_rates.append(wins / total_games)

            if win_rates:
                win_rate_issues = self._analyze_win_rate_distribution(win_rates)
                issues.extend(win_rate_issues)

            # Archetype distribution analysis
            archetype_issues = self._analyze_archetype_distribution(players)
            issues.extend(archetype_issues)

            # Performance consistency analysis
            consistency_issues = self._analyze_performance_consistency(players)
            issues.extend(consistency_issues)

        except Exception as e:
            logger.warning(f"Error in statistical analysis: {e}")

        return issues

    def _analyze_win_rate_distribution(self, win_rates: List[float]) -> List[str]:
        """Analyze win rate distribution for anomalies."""
        issues = []

        if len(win_rates) < 5:
            return issues

        try:
            mean_wr = statistics.mean(win_rates)
            stdev_wr = statistics.stdev(win_rates)

            # Check for unrealistic win rates
            outliers = [
                wr
                for wr in win_rates
                if abs(wr - mean_wr)
                > self.statistical_thresholds["win_rate_stddev_threshold"] * stdev_wr
            ]

            if len(outliers) > len(win_rates) * 0.1:  # More than 10% outliers
                issues.append(
                    f"Unusual win rate distribution: {len(outliers)} outliers"
                )

            # Check for impossible win rates
            impossible_rates = [wr for wr in win_rates if wr < 0 or wr > 1]
            if impossible_rates:
                issues.append(
                    f"Impossible win rates detected: {len(impossible_rates)} cases"
                )

        except statistics.StatisticsError:
            pass  # Not enough data for meaningful analysis

        return issues

    def _analyze_archetype_distribution(
        self, players: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze archetype distribution for anomalies."""
        issues = []

        # Count archetypes
        archetype_counts = {}
        total_players = len(players)

        for player in players:
            archetype = player.get("deck", {}).get("archetype", "Unknown")
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        # Check for suspicious distributions
        for archetype, count in archetype_counts.items():
            frequency = count / total_players

            # Single archetype dominance
            if frequency > 0.8:  # 80% of field
                issues.append(
                    f"Archetype '{archetype}' dominates field: {frequency:.1%}"
                )

            # Too many different archetypes (fragmentation)
            if len(archetype_counts) > total_players * 0.8:  # More than 80% unique
                issues.append("Excessive archetype fragmentation")
                break

        return issues

    def _analyze_performance_consistency(
        self, players: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze performance consistency across players."""
        issues = []

        # Check for consistent performance patterns that might indicate data issues
        performance_patterns = {}

        for player in players:
            wins = player.get("wins", 0)
            losses = player.get("losses", 0)
            pattern = f"{wins}-{losses}"
            performance_patterns[pattern] = performance_patterns.get(pattern, 0) + 1

        # Check if too many players have identical records
        for pattern, count in performance_patterns.items():
            if count > len(players) * 0.3:  # More than 30% have same record
                issues.append(
                    f"Suspicious performance pattern: {count} players with {pattern} record"
                )

        return issues

    def calculate_unknown_rate(self, tournament: Dict[str, Any]) -> float:
        """Calculate the rate of unknown archetypes."""
        players = tournament.get("players", [])
        if not players:
            return 0.0

        unknown_count = 0
        for player in players:
            archetype = player.get("deck", {}).get("archetype")
            if not archetype or archetype.lower() in ["unknown", "other", "misc"]:
                unknown_count += 1

        return unknown_count / len(players)

    def has_missing_standings(self, tournament: Dict[str, Any]) -> bool:
        """Check if tournament has missing standings data."""
        players = tournament.get("players", [])

        missing_count = 0
        for player in players:
            if not player.get("rank") or (
                player.get("wins") is None and player.get("losses") is None
            ):
                missing_count += 1

        return missing_count > len(players) * 0.2  # More than 20% missing

    def _calculate_duplicate_rate(self, tournament: Dict[str, Any]) -> float:
        """Calculate rate of duplicate players."""
        players = tournament.get("players", [])
        if not players:
            return 0.0

        player_names = [player.get("name", "").lower().strip() for player in players]
        unique_names = set(player_names)

        duplicate_count = len(player_names) - len(unique_names)
        return duplicate_count / len(player_names)

    def _validate_decks(self, tournament: Dict[str, Any]) -> List[str]:
        """Validate deck data."""
        issues = []
        players = tournament.get("players", [])

        for i, player in enumerate(players):
            deck = player.get("deck", {})

            # Check deck size
            mainboard = deck.get("mainboard", [])
            sideboard = deck.get("sideboard", [])

            if mainboard:
                main_size = sum(card.get("count", 0) for card in mainboard)
                if main_size < self.thresholds["min_deck_size"]:
                    issues.append(f"Player {i+1}: deck too small ({main_size} cards)")
                elif main_size > self.thresholds["max_deck_size"]:
                    issues.append(f"Player {i+1}: deck too large ({main_size} cards)")

            if sideboard:
                side_size = sum(card.get("count", 0) for card in sideboard)
                if side_size > self.thresholds["max_sideboard_size"]:
                    issues.append(
                        f"Player {i+1}: sideboard too large ({side_size} cards)"
                    )

        return issues

    def _validate_rounds(self, tournament: Dict[str, Any]) -> List[str]:
        """Validate round data."""
        issues = []

        rounds = tournament.get("rounds", [])
        if not rounds:
            return issues

        round_count = len(rounds)
        if round_count < self.thresholds["min_rounds"]:
            issues.append(f"Too few rounds: {round_count}")
        elif round_count > self.thresholds["max_rounds"]:
            issues.append(f"Too many rounds: {round_count}")

        return issues

    def _validate_date(self, date_str: str) -> Optional[str]:
        """Validate tournament date."""
        try:
            if isinstance(date_str, str):
                # Try to parse various date formats
                tournament_date = datetime.fromisoformat(
                    date_str.replace("Z", "+00:00")
                )
            else:
                tournament_date = date_str

            now = datetime.now()

            # Check if date is in the future
            if tournament_date > now + timedelta(days=1):
                return f"Tournament date in future: {tournament_date}"

            # Check if date is too old (more than 10 years)
            if tournament_date < now - timedelta(days=365 * 10):
                return f"Tournament date too old: {tournament_date}"

        except (ValueError, TypeError) as e:
            return f"Invalid date format: {date_str}"

        return None

    def _log_quarantine(self, tournament: Dict[str, Any], issues: List[str]):
        """Log quarantine decision."""
        quarantine_record = {
            "timestamp": datetime.now().isoformat(),
            "tournament_id": tournament.get("tournament_id"),
            "tournament_name": tournament.get("name"),
            "issues": issues,
            "player_count": len(tournament.get("players", [])),
            "unknown_rate": self.calculate_unknown_rate(tournament),
        }

        self.quarantine_history.append(quarantine_record)
        logger.warning(
            f"Tournament quarantined: {tournament.get('tournament_id')} - {len(issues)} issues"
        )

    def get_quarantine_stats(self) -> Dict[str, Any]:
        """Get quarantine statistics."""
        if not self.quarantine_history:
            return {"total_quarantined": 0, "common_issues": [], "quarantine_rate": 0.0}

        # Count common issues
        issue_counts = {}
        for record in self.quarantine_history:
            for issue in record["issues"]:
                # Extract issue type (before colon)
                issue_type = issue.split(":")[0]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Sort by frequency
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_quarantined": len(self.quarantine_history),
            "common_issues": common_issues[:10],  # Top 10
            "quarantine_rate": len(
                self.quarantine_history
            ),  # Would need total processed
            "recent_quarantines": self.quarantine_history[-5:],  # Last 5
        }

    def update_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update validation thresholds."""
        self.thresholds.update(new_thresholds)
        logger.info(f"Updated validation thresholds: {new_thresholds}")

    def clear_quarantine_history(self):
        """Clear quarantine history."""
        self.quarantine_history.clear()
        logger.info("Cleared quarantine history")
