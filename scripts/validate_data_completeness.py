#!/usr/bin/env python3
"""
Script de validation de la complétude des données pour Manalytics
Usage: python scripts/validate_data_completeness.py

Ce script vérifie la complétude et la qualité des données
collectées et traitées par le pipeline Manalytics.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataCompletenessValidator:
    """Classe pour valider la complétude des données"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "raw_data": {},
            "processed_data": {},
            "analysis_data": {},
            "summary": {},
        }

    def validate_data_completeness(self):
        """Valide la complétude des données"""

        print("📊 VALIDATION COMPLÉTUDE DES DONNÉES MANALYTICS")
        print("=" * 55)
        print(f"Timestamp: {self.results['timestamp']}")
        print()

        # 1. Validation des données brutes
        print("1. DONNÉES BRUTES")
        self.validate_raw_data()

        # 2. Validation des données traitées
        print("\n2. DONNÉES TRAITÉES")
        self.validate_processed_data()

        # 3. Validation des analyses
        print("\n3. ANALYSES")
        self.validate_analysis_data()

        # 4. Génération du rapport
        print("\n4. RAPPORT DE VALIDATION")
        self.generate_validation_report()

        print("\n✅ VALIDATION TERMINÉE")

    def validate_raw_data(self):
        """Valide les données brutes"""
        raw_dir = self.project_root / "data" / "raw"

        if not raw_dir.exists():
            self.results["raw_data"]["status"] = "missing"
            print("  ❌ Dossier data/raw/ manquant")
            return

        # Vérifier les sources de données
        sources = ["mtgo", "melee", "topdeck"]

        for source in sources:
            source_dir = raw_dir / source
            if source_dir.exists():
                # Compter les fichiers par année
                years = [d.name for d in source_dir.iterdir() if d.is_dir()]
                file_counts = {}

                for year in years:
                    year_dir = source_dir / year
                    file_count = len(list(year_dir.rglob("*.json")))
                    file_counts[year] = file_count

                total_files = sum(file_counts.values())

                self.results["raw_data"][source] = {
                    "status": "present",
                    "years": years,
                    "file_counts": file_counts,
                    "total_files": total_files,
                }

                print(f"  ✅ {source}: {total_files} fichiers ({', '.join(years)})")
            else:
                self.results["raw_data"][source] = {
                    "status": "missing",
                    "years": [],
                    "file_counts": {},
                    "total_files": 0,
                }
                print(f"  ❌ {source}: Aucune donnée")

    def validate_processed_data(self):
        """Valide les données traitées"""
        processed_dir = self.project_root / "data" / "processed"

        if not processed_dir.exists():
            self.results["processed_data"]["status"] = "missing"
            print("  ❌ Dossier data/processed/ manquant")
            return

        # Vérifier les fichiers de données traitées
        processed_files = list(processed_dir.glob("*.csv"))

        if processed_files:
            self.results["processed_data"]["status"] = "present"
            self.results["processed_data"]["files"] = []

            for file_path in processed_files:
                try:
                    # Lire le fichier CSV pour vérifier sa structure
                    df = pd.read_csv(file_path)

                    file_info = {
                        "name": file_path.name,
                        "size_bytes": file_path.stat().st_size,
                        "rows": len(df),
                        "columns": len(df.columns),
                        "columns_list": list(df.columns),
                    }

                    self.results["processed_data"]["files"].append(file_info)

                    print(
                        f"  ✅ {file_path.name}: {len(df)} lignes, "
                        f"{len(df.columns)} colonnes"
                    )

                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de {file_path}: {e}")
                    print(f"  ⚠️ {file_path.name}: Erreur de lecture")
        else:
            self.results["processed_data"]["status"] = "empty"
            print("  ⚠️ Aucun fichier de données traitées trouvé")

    def validate_analysis_data(self):
        """Valide les données d'analyse"""
        analyses_dir = self.project_root / "Analyses"

        if not analyses_dir.exists():
            self.results["analysis_data"]["status"] = "missing"
            print("  ❌ Dossier Analyses/ manquant")
            return

        # Trouver les analyses récentes
        analysis_dirs = [
            d
            for d in analyses_dir.iterdir()
            if d.is_dir() and d.name.startswith("standard_analysis")
        ]

        if not analysis_dirs:
            self.results["analysis_data"]["status"] = "empty"
            print("  ⚠️ Aucune analyse trouvée")
            return

        # Trier par date de modification
        analysis_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        self.results["analysis_data"]["status"] = "present"
        self.results["analysis_data"]["analyses"] = []

        # Analyser les 5 analyses les plus récentes
        for analysis_dir in analysis_dirs[:5]:
            try:
                # Compter les fichiers par type
                file_types = {}
                total_size = 0

                for file_path in analysis_dir.rglob("*"):
                    if file_path.is_file():
                        ext = file_path.suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                        total_size += file_path.stat().st_size

                analysis_info = {
                    "name": analysis_dir.name,
                    "file_types": file_types,
                    "total_files": sum(file_types.values()),
                    "total_size_bytes": total_size,
                    "last_modified": datetime.fromtimestamp(
                        analysis_dir.stat().st_mtime
                    ).isoformat(),
                }

                self.results["analysis_data"]["analyses"].append(analysis_info)

                print(
                    f"  ✅ {analysis_dir.name}: {sum(file_types.values())} fichiers "
                    f"({total_size / (1024**2):.1f} MB)"
                )

            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {analysis_dir}: {e}")
                print(f"  ⚠️ {analysis_dir.name}: Erreur d'analyse")

    def generate_validation_report(self):
        """Génère un rapport de validation"""
        # Calculer les métriques de qualité
        quality_metrics = {
            "raw_data_sources": 0,
            "raw_data_files": 0,
            "processed_files": 0,
            "analysis_count": 0,
        }

        # Compter les sources de données brutes
        if "raw_data" in self.results:
            for source, info in self.results["raw_data"].items():
                if isinstance(info, dict) and info.get("status") == "present":
                    quality_metrics["raw_data_sources"] += 1
                    quality_metrics["raw_data_files"] += info.get("total_files", 0)

        # Compter les fichiers traités
        if (
            "processed_data" in self.results
            and self.results["processed_data"].get("status") == "present"
        ):
            quality_metrics["processed_files"] = len(
                self.results["processed_data"].get("files", [])
            )

        # Compter les analyses
        if (
            "analysis_data" in self.results
            and self.results["analysis_data"].get("status") == "present"
        ):
            quality_metrics["analysis_count"] = len(
                self.results["analysis_data"].get("analyses", [])
            )

        # Calculer le score de qualité
        max_score = 100
        score = 0

        # Points pour les sources de données (max 30 points)
        score += min(quality_metrics["raw_data_sources"] * 10, 30)

        # Points pour les fichiers bruts (max 20 points)
        score += min(quality_metrics["raw_data_files"] / 10, 20)

        # Points pour les fichiers traités (max 25 points)
        score += min(quality_metrics["processed_files"] * 5, 25)

        # Points pour les analyses (max 25 points)
        score += min(quality_metrics["analysis_count"] * 5, 25)

        self.results["summary"] = {
            "quality_metrics": quality_metrics,
            "quality_score": score,
            "max_score": max_score,
            "quality_percentage": (score / max_score) * 100,
            "status": "excellent" if score >= 80 else "good" if score >= 60 else "poor",
        }

        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"data_validation_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"  📄 Rapport généré: {report_file}")
        print(
            f"  📊 Score de qualité: {score:.1f}/{max_score} ({self.results['summary']['quality_percentage']:.1f}%)"
        )
        print(f"  🏆 Statut: {self.results['summary']['status'].upper()}")

        # Afficher les métriques détaillées
        print(f"  📈 Sources de données: {quality_metrics['raw_data_sources']}/3")
        print(f"  📁 Fichiers bruts: {quality_metrics['raw_data_files']}")
        print(f"  🔧 Fichiers traités: {quality_metrics['processed_files']}")
        print(f"  📊 Analyses: {quality_metrics['analysis_count']}")


def main():
    """Fonction principale"""
    try:
        validator = DataCompletenessValidator()
        validator.validate_data_completeness()
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de la validation: {e}")
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
