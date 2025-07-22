#!/usr/bin/env python3
"""
Script de diagnostic complet pour Manalytics
Usage: python scripts/diagnostic_complete.py

Ce script effectue un diagnostic complet du système Manalytics
et génère un rapport détaillé de l'état du système.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ManalyticsDiagnostic:
    """Classe principale pour le diagnostic de Manalytics"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": {},
            "dependencies": {},
            "configuration": {},
            "data_integrity": {},
            "upstream_repos": {},
            "functionality_tests": {},
            "summary": {},
        }

    def run_complete_diagnostic(self):
        """Exécute un diagnostic complet du système"""

        print("🔍 DIAGNOSTIC COMPLET MANALYTICS")
        print("=" * 50)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Project root: {self.project_root}")
        print()

        # 1. Vérification de l'environnement
        print("1. ENVIRONNEMENT")
        self.check_environment()

        # 2. Vérification des dépendances
        print("\n2. DÉPENDANCES")
        self.check_dependencies()

        # 3. Vérification de la configuration
        print("\n3. CONFIGURATION")
        self.check_configuration()

        # 4. Vérification des données
        print("\n4. DONNÉES")
        self.check_data_integrity()

        # 5. Vérification des repositories upstream
        print("\n5. REPOSITORIES UPSTREAM")
        self.check_upstream_repos()

        # 6. Tests de fonctionnalités
        print("\n6. TESTS DE FONCTIONNALITÉS")
        self.run_functionality_tests()

        # 7. Génération du rapport
        print("\n7. GÉNÉRATION DU RAPPORT")
        self.generate_report()

        print("\n✅ DIAGNOSTIC TERMINÉ")
        print(
            f"📄 Rapport généré: "
            f"{self.project_root}/diagnostic_report_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    def check_environment(self):
        """Vérifie l'environnement système"""
        try:
            # Version Python
            python_version = sys.version
            self.results["environment"]["python_version"] = python_version
            print(f"  ✅ Python version: {python_version.split()[0]}")

            # Working directory
            working_dir = os.getcwd()
            self.results["environment"]["working_directory"] = working_dir
            print(f"  ✅ Working directory: {working_dir}")

            # Virtual environment
            virtual_env = os.environ.get("VIRTUAL_ENV", "Non activé")
            self.results["environment"]["virtual_environment"] = virtual_env
            print(
                f"  {'✅' if virtual_env != 'Non activé' else '⚠️'} "
                f"Virtual env: {virtual_env}"
            )

            # Espace disque
            disk_space = self.get_disk_space()
            self.results["environment"]["disk_space_gb"] = disk_space
            print(f"  ✅ Disk space: {disk_space:.1f} GB")

            # Système d'exploitation
            import platform

            os_info = f"{platform.system()} {platform.release()}"
            self.results["environment"]["operating_system"] = os_info
            print(f"  ✅ OS: {os_info}")

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'environnement: {e}")
            self.results["environment"]["error"] = str(e)

    def check_dependencies(self):
        """Vérifie les dépendances Python"""
        required_packages = [
            "pandas",
            "plotly",
            "requests",
            "beautifulsoup4",
            "numpy",
            "matplotlib",
            "seaborn",
            "scipy",
        ]

        for package in required_packages:
            try:
                module = __import__(package)
                version = getattr(module, "__version__", "Version inconnue")
                self.results["dependencies"][package] = {
                    "status": "present",
                    "version": version,
                }
                print(f"  ✅ {package}: {version}")
            except ImportError:
                self.results["dependencies"][package] = {
                    "status": "missing",
                    "version": None,
                }
                print(f"  ❌ {package}: Manquant")
            except Exception as e:
                self.results["dependencies"][package] = {
                    "status": "error",
                    "error": str(e),
                }
                print(f"  ⚠️ {package}: Erreur - {e}")

    def check_configuration(self):
        """Vérifie la configuration"""
        config_files = [
            "config/settings.py",
            "config/logging.yaml",
            "credentials/api_tokens.json",
        ]

        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                file_size = file_path.stat().st_size
                self.results["configuration"][config_file] = {
                    "status": "present",
                    "size_bytes": file_size,
                }
                print(f"  ✅ {config_file}: Présent ({file_size} bytes)")
            else:
                self.results["configuration"][config_file] = {
                    "status": "missing",
                    "size_bytes": 0,
                }
                print(f"  ❌ {config_file}: Manquant")

    def check_data_integrity(self):
        """Vérifie l'intégrité des données"""
        data_dirs = ["data/raw/", "data/processed/", "Analyses/"]

        for data_dir in data_dirs:
            dir_path = self.project_root / data_dir
            if dir_path.exists():
                # Compter les fichiers
                file_count = len(list(dir_path.rglob("*")))
                # Calculer la taille totale
                total_size = sum(
                    f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
                )

                self.results["data_integrity"][data_dir] = {
                    "status": "present",
                    "file_count": file_count,
                    "total_size_bytes": total_size,
                }
                print(
                    f"  ✅ {data_dir}: {file_count} fichiers "
                    f"({total_size / (1024**2):.1f} MB)"
                )
            else:
                self.results["data_integrity"][data_dir] = {
                    "status": "missing",
                    "file_count": 0,
                    "total_size_bytes": 0,
                }
                print(f"  ❌ {data_dir}: Manquant")

    def check_upstream_repos(self):
        """Vérifie les repositories upstream"""
        repos = ["MTGOFormatData", "MTGOArchetypeParser", "MTGODecklistCache"]

        for repo in repos:
            repo_path = self.project_root / repo
            if repo_path.exists():
                # Vérifier si c'est un repository git
                git_dir = repo_path / ".git"
                is_git_repo = git_dir.exists()

                # Compter les fichiers
                file_count = len(list(repo_path.rglob("*")))

                self.results["upstream_repos"][repo] = {
                    "status": "present",
                    "is_git_repo": is_git_repo,
                    "file_count": file_count,
                }
                print(
                    f"  ✅ {repo}: Présent "
                    f"({'Git repo' if is_git_repo else 'Dossier'}, {file_count} fichiers)"
                )
            else:
                self.results["upstream_repos"][repo] = {
                    "status": "missing",
                    "is_git_repo": False,
                    "file_count": 0,
                }
                print(f"  ❌ {repo}: Manquant")

    def run_functionality_tests(self):
        """Exécute des tests de fonctionnalités"""
        tests = [
            "Test scraping MTGO",
            "Test classification archétypes",
            "Test génération graphiques",
            "Test export données",
        ]

        for test in tests:
            # Simulation de tests (à implémenter avec de vrais tests)
            self.results["functionality_tests"][test] = {
                "status": "not_implemented",
                "message": "Test à implémenter",
            }
            print(f"  🔄 {test}: À implémenter")

    def get_disk_space(self):
        """Retourne l'espace disque disponible en GB"""
        try:
            stat = os.statvfs(".")
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            return free_gb
        except Exception:
            return 0.0

    def generate_report(self):
        """Génère un rapport JSON détaillé"""
        # Calculer le score global
        total_checks = 0
        passed_checks = 0

        for category, items in self.results.items():
            if isinstance(items, dict) and category != "timestamp":
                for item, details in items.items():
                    if isinstance(details, dict) and "status" in details:
                        total_checks += 1
                        if details["status"] == "present":
                            passed_checks += 1

        score_percentage = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        self.results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "score_percentage": score_percentage,
            "status": "healthy"
            if score_percentage >= 80
            else "warning"
            if score_percentage >= 60
            else "critical",
        }

        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"diagnostic_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"  📄 Rapport généré: {report_file}")
        print(
            f"  📊 Score global: {score_percentage:.1f}% ({passed_checks}/{total_checks})"
        )
        print(f"  🏥 Statut: {self.results['summary']['status'].upper()}")


def main():
    """Fonction principale"""
    try:
        diagnostic = ManalyticsDiagnostic()
        diagnostic.run_complete_diagnostic()
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors du diagnostic: {e}")
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
