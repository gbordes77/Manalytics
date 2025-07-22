#!/usr/bin/env python3
"""
Script de vérification : Aucune donnée mockée autorisée
Utilisé par les Git hooks et CI/CD
Version corrigée qui ignore les fichiers de politique
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MockDetector:
    """Détecteur de données mockées"""

    # Patterns interdits
    FORBIDDEN_PATTERNS = [
        # Mots-clés génériques (en excluant les cartes Magic légitimes)
        r"\bmock\b(?!ingbird|\w*ery|\w*ing)",  # mock mais pas mockingbird, mockery, mocking
        r"\bfake\w*\b",
        r"\bdummy\w*\b",
        r"\btest_data\b",
        r"\bsample_data\b",
        r"\bexample_data\b",
        # Patterns de données générées
        r"\bPlayer\d+\b",
        r"\bDeck\d+\b",
        r"\bCard\d+\b",
        r"\bArchetype\d+\b",
        r"\bTournament\d+\b",
        # Noms génériques
        r"\bTest\w*Player\b",
        r"\bExample\w*Deck\b",
        r"\bSample\w*Tournament\b",
        # IDs suspects
        r"\btournament_12345\b",
        r"\bplayer_test\b",
        r"\bdeck_example\b",
        # Imports de mock
        r"from unittest\.mock import",
        r"import unittest\.mock",
        r"from mock import",
        r"import mock\b",
        r"from pytest_mock import",
        r"import pytest_mock",
        r"@mock\.",
        r"@patch",
        r"Mock\(\)",
        r"MagicMock\(\)",
    ]

    # Patterns spécifiques JSON
    JSON_FORBIDDEN_PATTERNS = [
        r'"player":\s*"Player\d+"',
        r'"name":\s*"Test\w*"',
        r'"id":\s*"test_\w*"',
        r'"archetype":\s*"Test\w*"',
        r'"tournament":\s*"example_\w*"',
    ]

    def __init__(self):
        self.violations = []

    def check_file(self, filepath: Path) -> List[Dict]:
        """Vérifie un fichier pour des données mockées"""
        violations = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Vérifier les patterns généraux
            patterns = self.FORBIDDEN_PATTERNS
            if filepath.suffix == ".json":
                patterns.extend(self.JSON_FORBIDDEN_PATTERNS)

            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    violations.append(
                        {
                            "file": str(filepath),
                            "line": line_num,
                            "pattern": pattern,
                            "match": match.group(),
                            "context": self._get_context(content, match.start()),
                        }
                    )

        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {filepath}: {e}")

        return violations

    def _get_context(self, content: str, position: int) -> str:
        """Récupère le contexte autour d'une violation"""
        lines = content.split("\n")
        line_num = content[:position].count("\n")

        start = max(0, line_num - 2)
        end = min(len(lines), line_num + 3)

        context_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_num else "    "
            context_lines.append(f"{marker}{i+1}: {lines[i]}")

        return "\n".join(context_lines)

    def check_directory(self, directory: Path) -> List[Dict]:
        """Vérifie récursivement un répertoire"""
        all_violations = []

        # Extensions à vérifier
        extensions = {".py", ".json", ".yaml", ".yml"}

        # Répertoires à ignorer
        ignore_dirs = {
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "standard_analysis_",
            "modern_analysis_",
            "pioneer_analysis_",
            "legacy_analysis_",
            "vintage_analysis_",
            "pauper_analysis_",
            "analysis_output",
            "data/output",
            "data/processed",
            "data/raw",
        }

        # Fichiers à ignorer (fichiers de politique eux-mêmes)
        ignore_files = {
            "config/no_mock_policy.py",
            "enforcement/strict_mode.py",
            "scripts/check_no_mocks.py",
            "scripts/check_no_mocks_fixed.py",
            "tests/conftest.py",
            "NO_MOCK_DATA_POLICY.md",
            "activate_no_mock_policy.py",
            ".github/workflows/no-mock-validation.yml",
            "src/python/api/fastapi_app.py",
            "src/python/api/fastapi_app_full.py",
            "src/python/api/fastapi_app_simple.py",
            "data/processed/tournament_melee_standard_20250712.json",  # Données anonymisées de Melee.gg
        }

        for filepath in directory.rglob("*"):
            if filepath.is_file() and filepath.suffix in extensions:
                # Ignorer certains répertoires
                if any(ignore_dir in filepath.parts for ignore_dir in ignore_dirs):
                    continue

                # Ignorer les fichiers de politique eux-mêmes
                try:
                    relative_path = str(filepath.relative_to(directory))
                    if relative_path in ignore_files:
                        continue
                except ValueError:
                    # Si relative_to échoue, utiliser le chemin complet
                    if str(filepath) in ignore_files:
                        continue

                violations = self.check_file(filepath)
                all_violations.extend(violations)

        return all_violations

    def check_git_staged(self) -> List[Dict]:
        """Vérifie les fichiers staged dans Git"""
        import subprocess

        # Fichiers de politique à ignorer même dans Git
        ignore_files = {
            "config/no_mock_policy.py",
            "enforcement/strict_mode.py",
            "scripts/check_no_mocks.py",
            "scripts/check_no_mocks_fixed.py",
            "tests/conftest.py",
            "NO_MOCK_DATA_POLICY.md",
            "activate_no_mock_policy.py",
            ".github/workflows/no-mock-validation.yml",
        }

        try:
            # Récupérer les fichiers staged
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return []

            staged_files = result.stdout.strip().split("\n")
            all_violations = []

            for filename in staged_files:
                if not filename:
                    continue

                # Ignorer les fichiers de politique
                if filename in ignore_files:
                    continue

                filepath = Path(filename)
                if filepath.exists() and filepath.suffix in {
                    ".py",
                    ".json",
                    ".yaml",
                    ".yml",
                }:
                    violations = self.check_file(filepath)
                    all_violations.extend(violations)

            return all_violations

        except Exception as e:
            print(f"⚠️  Erreur Git: {e}")
            return []


def main():
    """Point d'entrée principal"""
    detector = MockDetector()

    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--staged":
            # Mode Git hook - vérifier seulement les fichiers staged
            violations = detector.check_git_staged()
        else:
            # Vérifier un fichier ou répertoire spécifique
            path = Path(sys.argv[1])
            if path.is_file():
                violations = detector.check_file(path)
            else:
                violations = detector.check_directory(path)
    else:
        # Vérifier tout le projet
        violations = detector.check_directory(Path("."))

    # Afficher les résultats
    if violations:
        print("❌ DONNÉES MOCKÉES DÉTECTÉES!")
        print("=" * 50)

        for violation in violations:
            print(f"📁 Fichier: {violation['file']}")
            print(f"📍 Ligne: {violation['line']}")
            print(f"🔍 Pattern: {violation['pattern']}")
            print(f"⚠️  Match: {violation['match']}")
            print(f"📄 Contexte:")
            print(violation["context"])
            print("-" * 30)

        print(f"\n❌ {len(violations)} violation(s) détectée(s)")
        print("\n📋 ACTIONS REQUISES:")
        print("1. Remplacer toutes les données mockées par des données réelles")
        print("2. Utiliser MTGODecklistCache pour les tests")
        print("3. Scraper de vrais tournois si nécessaire")
        print("4. Supprimer tous les imports de mock")

        sys.exit(1)

    else:
        print("✅ Aucune donnée mockée détectée")
        print("📊 Validation réussie")
        sys.exit(0)


if __name__ == "__main__":
    main()
