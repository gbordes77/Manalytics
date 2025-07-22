#!/usr/bin/env python3
"""
Script pour créer facilement des zips d'analyses Manalytics
Usage: python scripts/create_analysis_zip.py [nom_dossier_analyse]
"""

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def create_analysis_zip(analysis_folder_name: str = None):
    """Crée un zip d'une analyse pour partage"""

    # Dossier des analyses
    analyses_dir = Path("Analyses")

    if not analyses_dir.exists():
        print("❌ Erreur : Dossier 'Analyses' introuvable")
        print("💡 Assurez-vous d'être dans le dossier racine du projet")
        return False

    # Si pas de nom spécifié, lister les analyses disponibles
    if not analysis_folder_name:
        print("📁 Analyses disponibles :")
        analysis_folders = [f for f in analyses_dir.iterdir() if f.is_dir()]

        if not analysis_folders:
            print("❌ Aucune analyse trouvée dans le dossier Analyses/")
            return False

        for i, folder in enumerate(analysis_folders, 1):
            print(f"  {i}. {folder.name}")

        try:
            choice = input(f"\n🎯 Choisissez une analyse (1-{len(analysis_folders)}) : ")
            selected_folder = analysis_folders[int(choice) - 1]
            analysis_folder_name = selected_folder.name
        except (ValueError, IndexError):
            print("❌ Choix invalide")
            return False

    # Vérifier que le dossier d'analyse existe
    analysis_path = analyses_dir / analysis_folder_name
    if not analysis_path.exists():
        print(f"❌ Erreur : Analyse '{analysis_folder_name}' introuvable")
        return False

    # Créer le nom du zip
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"{analysis_folder_name}_{timestamp}.zip"
    zip_path = analyses_dir / zip_name

    print(f"📦 Création du zip : {zip_name}")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Ajouter tous les fichiers du dossier d'analyse
            for file_path in analysis_path.rglob("*"):
                if file_path.is_file():
                    # Chemin relatif dans le zip
                    arcname = file_path.relative_to(analyses_dir)
                    zipf.write(file_path, arcname)
                    print(f"  ✅ {arcname}")

        # Statistiques du zip
        zip_size = zip_path.stat().st_size
        zip_size_mb = zip_size / (1024 * 1024)

        print(f"\n🎉 Zip créé avec succès !")
        print(f"📦 Fichier : {zip_path}")
        print(f"📏 Taille : {zip_size_mb:.2f} MB")

        # Instructions pour le partage
        print(f"\n🚀 Pour partager :")
        print(f"1. 📧 Attachez le fichier : {zip_name}")
        print(f"2. 💾 Uploadez sur Google Drive, Dropbox, etc.")
        print(f"3. 🔗 Envoyez dans Slack, Discord, etc.")

        print(f"\n👤 Instructions pour le destinataire :")
        print(f"1. Dézipper le fichier")
        print(f"2. Ouvrir le fichier .html principal")
        print(f"3. Naviguer dans l'analyse complète !")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création du zip : {e}")
        return False


def main():
    """Point d'entrée principal"""
    print("🎯 Manalytics - Créateur de Zip d'Analyses")
    print("=" * 50)

    # Vérifier qu'on est dans le bon dossier
    if not Path("src/orchestrator.py").exists():
        print(
            "❌ Erreur : Ce script doit être exécuté depuis le dossier racine du projet"
        )
        sys.exit(1)

    # Nom du dossier d'analyse en argument
    analysis_folder = sys.argv[1] if len(sys.argv) > 1 else None

    # Créer le zip
    success = create_analysis_zip(analysis_folder)

    if success:
        print("\n✅ Analyse prête à être partagée !")
    else:
        print("\n❌ Échec de la création du zip")
        sys.exit(1)


if __name__ == "__main__":
    main()
