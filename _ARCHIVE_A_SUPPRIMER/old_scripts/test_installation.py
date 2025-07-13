#!/usr/bin/env python3

"""
Script de test pour valider l'installation de Manalytics
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def test_python_dependencies():
    """Tester que toutes les dépendances Python sont installées"""
    print("🐍 Test des dépendances Python...")
    
    required_modules = [
        'yaml', 'aiohttp', 'aiofiles', 'structlog', 
        'asyncio', 'tenacity', 'pandas'
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Modules manquants: {', '.join(failed)}")
        print("Installer avec: pip install -r requirements.txt")
        return False
    
    print("✅ Toutes les dépendances Python sont installées")
    return True

def test_r_installation():
    """Tester que R est installé et accessible"""
    print("\n📊 Test de l'installation R...")
    
    try:
        result = subprocess.run(['Rscript', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  ✅ R version: {result.stderr.strip()}")
            return True
        else:
            print(f"  ❌ Erreur R: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ R non trouvé ou non accessible")
        print("  Installer R: https://www.r-project.org/")
        return False

def test_r_packages():
    """Tester que les packages R requis sont installés"""
    print("\n📦 Test des packages R...")
    
    required_packages = ['jsonlite', 'dplyr', 'tidyr', 'purrr', 'lubridate']
    
    r_script = f"""
    packages <- c({', '.join([f"'{pkg}'" for pkg in required_packages])})
    missing <- packages[!packages %in% installed.packages()[,"Package"]]
    if(length(missing) > 0) {{
        cat("MISSING:", paste(missing, collapse=","), "\\n")
        quit(status=1)
    }} else {{
        cat("ALL_INSTALLED\\n")
        quit(status=0)
    }}
    """
    
    try:
        result = subprocess.run(['Rscript', '-e', r_script], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "ALL_INSTALLED" in result.stdout:
            print("  ✅ Tous les packages R sont installés")
            return True
        else:
            missing = result.stdout.replace("MISSING:", "").strip()
            print(f"  ❌ Packages manquants: {missing}")
            print("  Installer avec: Rscript -e \"install.packages(c('jsonlite', 'dplyr', 'tidyr', 'purrr', 'lubridate'))\"")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Timeout lors du test des packages R")
        return False

def test_directory_structure():
    """Tester que la structure de dossiers est correcte"""
    print("\n📁 Test de la structure des dossiers...")
    
    required_dirs = [
        'src/python/scraper',
        'src/python/classifier', 
        'src/r/analysis',
        'data/raw',
        'data/processed',
        'data/output',
        'logs',
        'credentials',
        'MTGOFormatData'
    ]
    
    missing = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path}")
            missing.append(dir_path)
    
    if missing:
        print(f"\n❌ Dossiers manquants: {', '.join(missing)}")
        return False
    
    print("✅ Structure des dossiers correcte")
    return True

def test_config_file():
    """Tester que le fichier de configuration est valide"""
    print("\n⚙️ Test du fichier de configuration...")
    
    if not os.path.exists('config.yaml'):
        print("  ❌ config.yaml non trouvé")
        return False
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['cache_folder', 'enabled_sources', 'apis']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"  ❌ Clés manquantes dans config.yaml: {', '.join(missing_keys)}")
            return False
        
        print("  ✅ config.yaml valide")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la lecture de config.yaml: {e}")
        return False

def test_mtgo_format_data():
    """Tester que MTGOFormatData est présent et contient des données"""
    print("\n🎯 Test des données MTGOFormatData...")
    
    format_data_path = "MTGOFormatData/Formats"
    
    if not os.path.exists(format_data_path):
        print("  ❌ MTGOFormatData/Formats non trouvé")
        print("  Cloner avec: git clone https://github.com/Badaro/MTGOFormatData.git")
        return False
    
    # Vérifier qu'il y a au moins un format
    formats = [d for d in os.listdir(format_data_path) 
              if os.path.isdir(os.path.join(format_data_path, d))]
    
    if not formats:
        print("  ❌ Aucun format trouvé dans MTGOFormatData")
        return False
    
    print(f"  ✅ Formats disponibles: {', '.join(formats[:5])}{'...' if len(formats) > 5 else ''}")
    return True

def test_imports():
    """Tester que les modules principaux peuvent être importés"""
    print("\n🔧 Test des imports des modules...")
    
    try:
        # Test import du scraper
        sys.path.append('.')
        from src.python.scraper.base_scraper import BaseScraper
        print("  ✅ BaseScraper importé")
        
        from src.python.classifier.archetype_engine import ArchetypeEngine
        print("  ✅ ArchetypeEngine importé")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧙‍♂️ Test d'installation de Manalytics\n")
    
    tests = [
        test_python_dependencies,
        test_r_installation,
        test_r_packages,
        test_directory_structure,
        test_config_file,
        test_mtgo_format_data,
        test_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Erreur lors du test: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "="*50)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ Tous les tests réussis ({passed}/{total})")
        print("\n🎉 Installation validée ! Vous pouvez utiliser Manalytics.")
        print("\nCommande de test:")
        print("python orchestrator.py --format Modern --skip-scraping --skip-classification")
        return 0
    else:
        print(f"❌ Tests échoués: {total - passed}/{total}")
        print("\n🔧 Veuillez corriger les problèmes avant d'utiliser Manalytics.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 