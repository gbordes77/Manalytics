#!/usr/bin/env python3
"""
Script de test de performance pour Manalytics
Usage: python scripts/performance_test.py

Ce script teste les performances des différentes composantes
du pipeline Manalytics et génère un rapport détaillé.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceTester:
    """Classe pour tester les performances de Manalytics"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "performance_tests": {},
            "summary": {},
        }

    def run_performance_tests(self):
        """Exécute tous les tests de performance"""

        print("⚡ TEST DE PERFORMANCE MANALYTICS")
        print("=" * 45)
        print(f"Timestamp: {self.results['timestamp']}")
        print()

        # 1. Collecte des informations système
        print("1. INFORMATIONS SYSTÈME")
        self.collect_system_info()

        # 2. Test de performance des imports
        print("\n2. TEST DES IMPORTS")
        self.test_imports_performance()

        # 3. Test de performance des opérations de base
        print("\n3. TEST DES OPÉRATIONS DE BASE")
        self.test_basic_operations()

        # 4. Test de performance des fichiers
        print("\n4. TEST DES OPÉRATIONS FICHIERS")
        self.test_file_operations()

        # 5. Test de performance mémoire
        print("\n5. TEST MÉMOIRE")
        self.test_memory_usage()

        # 6. Génération du rapport
        print("\n6. RAPPORT DE PERFORMANCE")
        self.generate_performance_report()

        print("\n✅ TESTS DE PERFORMANCE TERMINÉS")

    def collect_system_info(self):
        """Collecte les informations système"""
        try:
            # CPU
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Mémoire
            memory = psutil.virtual_memory()

            # Disque
            disk = psutil.disk_usage("/")

            self.results["system_info"] = {
                "cpu_count": cpu_count,
                "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
                "memory_total_gb": memory.total / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
            }

            if cpu_freq:
                print(f"  💻 CPU: {cpu_count} cœurs à {cpu_freq.current:.0f} MHz")
            else:
                print(f"  💻 CPU: {cpu_count} cœurs")
            print(
                f"  🧠 RAM: {memory.total / (1024**3):.1f} GB total, "
                f"{memory.available / (1024**3):.1f} GB disponible"
            )
            print(
                f"  💾 Disque: {disk.total / (1024**3):.1f} GB total, "
                f"{disk.free / (1024**3):.1f} GB libre"
            )

        except Exception as e:
            logger.error(f"Erreur lors de la collecte des informations système: {e}")
            self.results["system_info"]["error"] = str(e)

    def test_imports_performance(self):
        """Teste la performance des imports"""
        modules_to_test = [
            "pandas",
            "plotly",
            "numpy",
            "matplotlib",
            "seaborn",
            "scipy",
        ]

        self.results["performance_tests"]["imports"] = {}

        for module in modules_to_test:
            try:
                start_time = time.time()
                __import__(module)
                end_time = time.time()

                import_time = (end_time - start_time) * 1000  # en millisecondes

                self.results["performance_tests"]["imports"][module] = {
                    "status": "success",
                    "import_time_ms": import_time,
                }

                print(f"  ✅ {module}: {import_time:.2f} ms")

            except ImportError:
                self.results["performance_tests"]["imports"][module] = {
                    "status": "missing",
                    "import_time_ms": None,
                }
                print(f"  ❌ {module}: Manquant")
            except Exception as e:
                self.results["performance_tests"]["imports"][module] = {
                    "status": "error",
                    "error": str(e),
                    "import_time_ms": None,
                }
                print(f"  ⚠️ {module}: Erreur - {e}")

    def test_basic_operations(self):
        """Teste les opérations de base"""
        self.results["performance_tests"]["basic_operations"] = {}

        # Test de création de DataFrame
        try:
            import numpy as np
            import pandas as pd

            start_time = time.time()
            df = pd.DataFrame(np.random.randn(10000, 10))
            end_time = time.time()

            df_creation_time = (end_time - start_time) * 1000

            self.results["performance_tests"]["basic_operations"][
                "dataframe_creation"
            ] = {
                "status": "success",
                "time_ms": df_creation_time,
                "size": f"{df.memory_usage(deep=True).sum() / (1024**2):.2f} MB",
            }

            print(f"  ✅ Création DataFrame 10k×10: {df_creation_time:.2f} ms")

        except Exception as e:
            self.results["performance_tests"]["basic_operations"][
                "dataframe_creation"
            ] = {"status": "error", "error": str(e)}
            print(f"  ⚠️ Création DataFrame: Erreur - {e}")

        # Test de tri
        try:
            start_time = time.time()
            _ = df.sort_values(by=0)
            end_time = time.time()

            sort_time = (end_time - start_time) * 1000

            self.results["performance_tests"]["basic_operations"]["sorting"] = {
                "status": "success",
                "time_ms": sort_time,
            }

            print(f"  ✅ Tri DataFrame: {sort_time:.2f} ms")

        except Exception as e:
            self.results["performance_tests"]["basic_operations"]["sorting"] = {
                "status": "error",
                "error": str(e),
            }
            print(f"  ⚠️ Tri DataFrame: Erreur - {e}")

        # Test de groupby
        try:
            start_time = time.time()
            _ = df.groupby(df[0] > 0).mean()
            end_time = time.time()

            groupby_time = (end_time - start_time) * 1000

            self.results["performance_tests"]["basic_operations"]["groupby"] = {
                "status": "success",
                "time_ms": groupby_time,
            }

            print(f"  ✅ GroupBy DataFrame: {groupby_time:.2f} ms")

        except Exception as e:
            self.results["performance_tests"]["basic_operations"]["groupby"] = {
                "status": "error",
                "error": str(e),
            }
            print(f"  ⚠️ GroupBy DataFrame: Erreur - {e}")

    def test_file_operations(self):
        """Teste les opérations sur fichiers"""
        self.results["performance_tests"]["file_operations"] = {}

        # Test de lecture CSV
        try:
            import pandas as pd

            # Chercher un fichier CSV dans les analyses
            analyses_dir = self.project_root / "Analyses"
            csv_files = list(analyses_dir.rglob("*.csv"))

            if csv_files:
                test_file = csv_files[0]

                start_time = time.time()
                df = pd.read_csv(test_file)
                end_time = time.time()

                read_time = (end_time - start_time) * 1000
                file_size = test_file.stat().st_size / (1024**2)  # MB

                self.results["performance_tests"]["file_operations"]["csv_read"] = {
                    "status": "success",
                    "time_ms": read_time,
                    "file_size_mb": file_size,
                    "rows": len(df),
                    "columns": len(df.columns),
                }

                print(f"  ✅ Lecture CSV ({file_size:.1f} MB): {read_time:.2f} ms")

            else:
                self.results["performance_tests"]["file_operations"]["csv_read"] = {
                    "status": "no_file",
                    "message": "Aucun fichier CSV trouvé",
                }
                print("  ⚠️ Lecture CSV: Aucun fichier trouvé")

        except Exception as e:
            self.results["performance_tests"]["file_operations"]["csv_read"] = {
                "status": "error",
                "error": str(e),
            }
            print(f"  ⚠️ Lecture CSV: Erreur - {e}")

        # Test d'écriture JSON
        try:
            test_data = {"test": "data", "numbers": list(range(1000))}

            start_time = time.time()
            with open("test_performance.json", "w") as f:
                json.dump(test_data, f)
            end_time = time.time()

            write_time = (end_time - start_time) * 1000

            self.results["performance_tests"]["file_operations"]["json_write"] = {
                "status": "success",
                "time_ms": write_time,
            }

            print(f"  ✅ Écriture JSON: {write_time:.2f} ms")

            # Nettoyer le fichier de test
            os.remove("test_performance.json")

        except Exception as e:
            self.results["performance_tests"]["file_operations"]["json_write"] = {
                "status": "error",
                "error": str(e),
            }
            print(f"  ⚠️ Écriture JSON: Erreur - {e}")

    def test_memory_usage(self):
        """Teste l'utilisation mémoire"""
        self.results["performance_tests"]["memory_usage"] = {}

        try:
            import numpy as np
            import pandas as pd
            import psutil

            # Mesurer la mémoire avant
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024**2)  # MB

            # Créer un gros DataFrame
            df_large = pd.DataFrame(np.random.randn(100000, 20))

            # Mesurer la mémoire après
            memory_after = process.memory_info().rss / (1024**2)  # MB
            memory_used = memory_after - memory_before

            self.results["performance_tests"]["memory_usage"]["dataframe_memory"] = {
                "status": "success",
                "memory_used_mb": memory_used,
                "dataframe_size_mb": df_large.memory_usage(deep=True).sum()
                / (1024**2),
            }

            print(f"  ✅ Utilisation mémoire DataFrame: {memory_used:.1f} MB")

            # Libérer la mémoire
            del df_large

        except Exception as e:
            self.results["performance_tests"]["memory_usage"]["dataframe_memory"] = {
                "status": "error",
                "error": str(e),
            }
            print(f"  ⚠️ Test mémoire: Erreur - {e}")

    def generate_performance_report(self):
        """Génère un rapport de performance"""
        # Calculer les métriques de performance
        performance_metrics = {
            "total_import_time": 0,
            "successful_imports": 0,
            "average_import_time": 0,
            "dataframe_operations_time": 0,
            "file_operations_time": 0,
        }

        # Analyser les imports
        if "imports" in self.results["performance_tests"]:
            import_times = []
            for module, info in self.results["performance_tests"]["imports"].items():
                if info.get("status") == "success" and info.get("import_time_ms"):
                    import_times.append(info["import_time_ms"])
                    performance_metrics["successful_imports"] += 1

            if import_times:
                performance_metrics["total_import_time"] = sum(import_times)
                performance_metrics["average_import_time"] = sum(import_times) / len(
                    import_times
                )

        # Analyser les opérations de base
        if "basic_operations" in self.results["performance_tests"]:
            for operation, info in self.results["performance_tests"][
                "basic_operations"
            ].items():
                if info.get("status") == "success" and info.get("time_ms"):
                    performance_metrics["dataframe_operations_time"] += info["time_ms"]

        # Analyser les opérations fichiers
        if "file_operations" in self.results["performance_tests"]:
            for operation, info in self.results["performance_tests"][
                "file_operations"
            ].items():
                if info.get("status") == "success" and info.get("time_ms"):
                    performance_metrics["file_operations_time"] += info["time_ms"]

        # Calculer le score de performance
        max_score = 100
        score = 0

        # Points pour les imports rapides (max 30 points)
        if performance_metrics["average_import_time"] > 0:
            score += max(0, 30 - (performance_metrics["average_import_time"] / 10))

        # Points pour les opérations DataFrame (max 40 points)
        if performance_metrics["dataframe_operations_time"] > 0:
            score += max(0, 40 - (performance_metrics["dataframe_operations_time"] / 5))

        # Points pour les opérations fichiers (max 30 points)
        if performance_metrics["file_operations_time"] > 0:
            score += max(0, 30 - (performance_metrics["file_operations_time"] / 10))

        self.results["summary"] = {
            "performance_metrics": performance_metrics,
            "performance_score": score,
            "max_score": max_score,
            "performance_percentage": (score / max_score) * 100,
            "status": "excellent" if score >= 80 else "good" if score >= 60 else "poor",
        }

        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"performance_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"  📄 Rapport généré: {report_file}")
        print(
            f"  ⚡ Score de performance: {score:.1f}/{max_score} ({self.results['summary']['performance_percentage']:.1f}%)"
        )
        print(f"  🏆 Statut: {self.results['summary']['status'].upper()}")

        # Afficher les métriques détaillées
        print(f"  📦 Imports réussis: {performance_metrics['successful_imports']}")
        print(
            f"  ⏱️ Temps moyen import: {performance_metrics['average_import_time']:.2f} ms"
        )
        print(
            f"  🔧 Temps opérations DataFrame: {performance_metrics['dataframe_operations_time']:.2f} ms"
        )
        print(
            f"  📁 Temps opérations fichiers: {performance_metrics['file_operations_time']:.2f} ms"
        )


def main():
    """Fonction principale"""
    try:
        tester = PerformanceTester()
        tester.run_performance_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Tests de performance interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors des tests de performance: {e}")
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
