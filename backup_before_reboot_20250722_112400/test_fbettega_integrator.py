#!/usr/bin/env python3
"""
Test FBettega Integrator - Test de l'intégrateur complet reproduisant fetch_tournament.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

from scraper.fbettega_authentic_integrator import *


def test_mtgo_integration():
    """Test de l'intégration MTGO complète"""
    print("🧪 Test de l'intégration MTGO complète...")

    # Créer le dossier de cache
    cache_folder = "data/raw"
    os.makedirs(cache_folder, exist_ok=True)

    # Définir une période de test (derniers 3 jours)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=3)

    print(f"📅 Période de test: {start_date.date()} à {end_date.date()}")
    print(f"📁 Cache folder: {cache_folder}")

    try:
        # Tester la fonction update_mtgo_folder
        print("\n🔍 Test de update_mtgo_folder...")
        update_mtgo_folder(cache_folder, start_date, end_date)

        # Vérifier que les fichiers ont été créés
        mtgo_folder = os.path.join(cache_folder, "mtgo.com")
        if os.path.exists(mtgo_folder):
            print(f"✅ Dossier MTGO créé: {mtgo_folder}")

            # Lister les fichiers créés
            for root, dirs, files in os.walk(mtgo_folder):
                if files:
                    print(f"📁 {root}: {len(files)} fichiers")
                    for file in files[:5]:  # Afficher les 5 premiers
                        print(f"   📄 {file}")
                    if len(files) > 5:
                        print(f"   ... et {len(files) - 5} autres fichiers")
        else:
            print("❌ Dossier MTGO non créé")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()


def test_retry_mechanism():
    """Test du mécanisme de retry"""
    print("\n🧪 Test du mécanisme de retry...")

    def failing_function():
        raise Exception("Test error")

    def succeeding_function():
        return "Success"

    try:
        # Test avec une fonction qui échoue
        print("🔍 Test avec une fonction qui échoue...")
        result = run_with_retry(failing_function, 3)
    except Exception as e:
        print(f"✅ Exception attendue: {e}")

    # Test avec une fonction qui réussit
    print("🔍 Test avec une fonction qui réussit...")
    result = run_with_retry(succeeding_function, 3)
    print(f"✅ Résultat: {result}")


def test_logging():
    """Test du système de logging"""
    print("\n🧪 Test du système de logging...")

    log_file = "test_log.txt"

    # Sauvegarder stdout original
    original_stdout = sys.stdout

    try:
        configure_logging(log_file)
        print("Test message 1")
        print("Test message 2")

        # Restaurer stdout
        sys.stdout = original_stdout

        # Vérifier que le fichier de log a été créé
        if os.path.exists(log_file):
            print(f"✅ Fichier de log créé: {log_file}")

            # Lire le contenu
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 Contenu du log ({len(content)} caractères):")
                print(content[:200] + "..." if len(content) > 200 else content)
        else:
            print("❌ Fichier de log non créé")

    except Exception as e:
        print(f"❌ Erreur lors du test de logging: {e}")
        sys.stdout = original_stdout


def main():
    """Fonction principale de test"""
    print("🚀 Test de l'intégrateur FBettega Authentic")
    print("=" * 60)

    # Test du logging
    test_logging()

    # Test du mécanisme de retry
    test_retry_mechanism()

    # Test de l'intégration MTGO
    test_mtgo_integration()

    print("\n" + "=" * 60)
    print("✅ Tests terminés!")


if __name__ == "__main__":
    main()
