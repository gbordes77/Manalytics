"""
Rules loader for loading archetype rules from various formats.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class RulesLoader:
    """Loader for archetype rules from JSON and YAML files."""

    def __init__(self):
        """Initialize rules loader."""
        self.supported_formats = {".json", ".yaml", ".yml"}

    def load_rules(self, file_path: str) -> Dict[str, Any]:
        """
        Load rules from a file.

        Args:
            file_path: Path to rules file

        Returns:
            Loaded rules dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Rules file not found: {file_path}")

        path = Path(file_path)

        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    return json.load(f)
                else:  # YAML
                    return yaml.safe_load(f)

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error(f"Error parsing rules file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading rules file {file_path}: {e}")
            raise

    def load_format_rules(self, format_dir: str) -> Dict[str, Any]:
        """
        Load all rules for a specific format.

        Args:
            format_dir: Directory containing format rules

        Returns:
            Combined rules dictionary
        """
        if not os.path.exists(format_dir):
            logger.warning(f"Format directory not found: {format_dir}")
            return {}

        rules = {
            "archetypes": [],
            "format": os.path.basename(format_dir).lower(),
            "metadata": {},
        }

        # Look for standard files
        archetype_files = [
            "Archetypes.json",
            "archetypes.json",
            "archetypes.yaml",
            "archetypes.yml",
        ]

        for filename in archetype_files:
            file_path = os.path.join(format_dir, filename)
            if os.path.exists(file_path):
                try:
                    loaded_rules = self.load_rules(file_path)

                    # Handle different rule formats
                    if isinstance(loaded_rules, list):
                        rules["archetypes"].extend(loaded_rules)
                    elif isinstance(loaded_rules, dict):
                        if "archetypes" in loaded_rules:
                            rules["archetypes"].extend(loaded_rules["archetypes"])
                        else:
                            # Assume the dict itself contains archetype definitions
                            rules["archetypes"].append(loaded_rules)

                        # Extract metadata
                        if "metadata" in loaded_rules:
                            rules["metadata"].update(loaded_rules["metadata"])

                    logger.info(f"Loaded rules from {file_path}")
                    break

                except Exception as e:
                    logger.error(f"Failed to load rules from {file_path}: {e}")
                    continue

        # Load additional rule files
        for file_path in Path(format_dir).glob("**/*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_formats
                and file_path.name not in archetype_files
            ):

                try:
                    additional_rules = self.load_rules(str(file_path))
                    if isinstance(additional_rules, list):
                        rules["archetypes"].extend(additional_rules)
                    elif (
                        isinstance(additional_rules, dict)
                        and "archetypes" in additional_rules
                    ):
                        rules["archetypes"].extend(additional_rules["archetypes"])

                    logger.debug(f"Loaded additional rules from {file_path}")

                except Exception as e:
                    logger.warning(
                        f"Failed to load additional rules from {file_path}: {e}"
                    )

        return rules

    def load_all_formats(self, rules_repo_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Load rules for all formats in the repository.

        Args:
            rules_repo_path: Path to rules repository

        Returns:
            Dictionary mapping format names to rules
        """
        all_rules = {}

        if not os.path.exists(rules_repo_path):
            logger.error(f"Rules repository not found: {rules_repo_path}")
            return all_rules

        # Iterate through format directories
        for item in os.listdir(rules_repo_path):
            format_path = os.path.join(rules_repo_path, item)

            if os.path.isdir(format_path) and not item.startswith("."):
                try:
                    format_rules = self.load_format_rules(format_path)
                    if format_rules["archetypes"]:  # Only include if has archetypes
                        all_rules[item.lower()] = format_rules
                        logger.info(
                            f"Loaded {len(format_rules['archetypes'])} archetypes for {item}"
                        )

                except Exception as e:
                    logger.error(f"Failed to load rules for format {item}: {e}")

        return all_rules

    def validate_rules(self, rules: Dict[str, Any]) -> List[str]:
        """
        Validate rules structure.

        Args:
            rules: Rules dictionary to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(rules, dict):
            errors.append("Rules must be a dictionary")
            return errors

        if "archetypes" not in rules:
            errors.append("Missing 'archetypes' key")
            return errors

        if not isinstance(rules["archetypes"], list):
            errors.append("'archetypes' must be a list")
            return errors

        # Validate each archetype
        for i, archetype in enumerate(rules["archetypes"]):
            archetype_errors = self._validate_archetype(archetype, i)
            errors.extend(archetype_errors)

        return errors

    def _validate_archetype(self, archetype: Dict[str, Any], index: int) -> List[str]:
        """Validate a single archetype definition."""
        errors = []
        prefix = f"Archetype {index}"

        if not isinstance(archetype, dict):
            errors.append(f"{prefix}: must be a dictionary")
            return errors

        # Required fields
        required_fields = ["name", "conditions"]
        for field in required_fields:
            if field not in archetype:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Validate name
        if "name" in archetype:
            if not isinstance(archetype["name"], str) or not archetype["name"].strip():
                errors.append(f"{prefix}: 'name' must be a non-empty string")

        # Validate conditions
        if "conditions" in archetype:
            if not isinstance(archetype["conditions"], list):
                errors.append(f"{prefix}: 'conditions' must be a list")
            else:
                for j, condition in enumerate(archetype["conditions"]):
                    condition_errors = self._validate_condition(
                        condition, f"{prefix}, condition {j}"
                    )
                    errors.extend(condition_errors)

        return errors

    def _validate_condition(self, condition: Dict[str, Any], prefix: str) -> List[str]:
        """Validate a single condition."""
        errors = []

        if not isinstance(condition, dict):
            errors.append(f"{prefix}: must be a dictionary")
            return errors

        # Required fields
        if "type" not in condition:
            errors.append(f"{prefix}: missing required field 'type'")

        if "cards" not in condition:
            errors.append(f"{prefix}: missing required field 'cards'")

        # Validate type
        valid_types = ["contains", "excludes", "count", "ratio"]
        if "type" in condition:
            if condition["type"] not in valid_types:
                errors.append(
                    f"{prefix}: invalid type '{condition['type']}', must be one of {valid_types}"
                )

        # Validate cards
        if "cards" in condition:
            if not isinstance(condition["cards"], list):
                errors.append(f"{prefix}: 'cards' must be a list")
            elif not condition["cards"]:
                errors.append(f"{prefix}: 'cards' list cannot be empty")
            else:
                for card in condition["cards"]:
                    if not isinstance(card, str):
                        errors.append(f"{prefix}: all cards must be strings")
                        break

        return errors

    def get_format_from_path(self, file_path: str) -> Optional[str]:
        """
        Extract format name from file path.

        Args:
            file_path: Path to rules file

        Returns:
            Format name or None
        """
        path = Path(file_path)

        # Look for format in parent directories
        for parent in path.parents:
            parent_name = parent.name.lower()
            if parent_name in [
                "modern",
                "legacy",
                "vintage",
                "standard",
                "pioneer",
                "historic",
            ]:
                return parent_name

        # Try to extract from filename
        filename = path.stem.lower()
        if any(
            fmt in filename
            for fmt in [
                "modern",
                "legacy",
                "vintage",
                "standard",
                "pioneer",
                "historic",
            ]
        ):
            for fmt in [
                "modern",
                "legacy",
                "vintage",
                "standard",
                "pioneer",
                "historic",
            ]:
                if fmt in filename:
                    return fmt

        return None

    def save_rules(self, rules: Dict[str, Any], file_path: str):
        """
        Save rules to file.

        Args:
            rules: Rules dictionary to save
            file_path: Output file path
        """
        path = Path(file_path)

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    json.dump(rules, f, indent=2, ensure_ascii=False)
                else:  # YAML
                    yaml.dump(rules, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Saved rules to {file_path}")

        except Exception as e:
            logger.error(f"Error saving rules to {file_path}: {e}")
            raise
