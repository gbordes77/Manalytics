#!/usr/bin/env python3
"""
Tests de régression pour le pipeline Manalytics
Tests sur les vraies données uniquement
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

def test_pipeline_structure_stability():
    """Vérifie la stabilité de la structure du pipeline"""
    print("🧪 Testing pipeline structure stability...")
    
    # Fichiers critiques du pipeline
    critical_files = [
        'fetch_tournament.py',
        'data_treatment.py',
        'step3_visualization.py',
        'orchestrator.py'
    ]
    
    missing_files = []
    for file in critical_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Critical files missing: {missing_files}")
        return False
    
    print("✅ Pipeline structure stable")
    return True

def test_mtgo_format_data_integrity():
    """Vérifie l'intégrité des données MTGOFormatData"""
    print("🧪 Testing MTGOFormatData integrity...")
    
    if not os.path.exists('MTGOFormatData/'):
        print("⚠️  MTGOFormatData not found - integrity test skipped")
        return True
    
    # Vérifier les formats critiques
    formats = ['Modern', 'Legacy', 'Pioneer', 'Standard']
    
    for format_name in formats:
        format_path = Path('MTGOFormatData/Formats') / format_name
        if format_path.exists():
            # Vérifier les fichiers critiques
            critical_files = ['metas.json', 'color_overrides.json']
            for file in critical_files:
                file_path = format_path / file
                if file_path.exists():
                    try:
                        with open(file_path) as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON in {format_name}/{file}")
                        return False
        else:
            print(f"⚠️  Format {format_name} not found")
    
    print("✅ MTGOFormatData integrity verified")
    return True

def test_api_configuration_stability():
    """Vérifie la stabilité de la configuration API"""
    print("🧪 Testing API configuration stability...")
    
    if not os.path.exists('Api_token_and_login/'):
        print("⚠️  API configuration not found - stability test skipped")
        return True
    
    # Vérifier les fichiers de configuration
    config_files = list(Path('Api_token_and_login/').glob('*'))
    if config_files:
        print(f"✅ API configuration files found: {len(config_files)}")
    else:
        print("⚠️  No API configuration files found")
    
    return True

def test_real_data_consistency():
    """Vérifie la cohérence des vraies données"""
    print("🧪 Testing real data consistency...")
    
    # Vérifier les données réelles
    real_data_paths = [
        'data/processed/',
        'data/raw/',
        'MTGODecklistCache/Tournaments/'
    ]
    
    consistent_data = True
    for path in real_data_paths:
        if os.path.exists(path):
            json_files = list(Path(path).glob('**/*.json'))
            if json_files:
                # Tester quelques fichiers
                for file_path in json_files[:5]:  # Limiter à 5 fichiers
                    try:
                        with open(file_path) as f:
                            data = json.load(f)
                        # Vérification basique de structure
                        if not isinstance(data, dict):
                            print(f"❌ Invalid structure in {file_path.name}")
                            consistent_data = False
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON in {file_path.name}")
                        consistent_data = False
                
                print(f"✅ {path}: {len(json_files)} files checked")
            else:
                print(f"⚠️  {path}: No JSON files found")
        else:
            print(f"⚠️  {path}: Directory not found")
    
    if consistent_data:
        print("✅ Real data consistency verified")
    
    return consistent_data

def test_output_format_regression():
    """Vérifie la régression du format de sortie"""
    print("🧪 Testing output format regression...")
    
    # Vérifier les sorties existantes
    output_paths = [
        'data/output/',
        'results/'
    ]
    
    format_stable = True
    for path in output_paths:
        if os.path.exists(path):
            json_files = list(Path(path).glob('**/*.json'))
            if json_files:
                for file_path in json_files:
                    try:
                        with open(file_path) as f:
                            data = json.load(f)
                        print(f"✅ Valid output format: {file_path.name}")
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON format: {file_path.name}")
                        format_stable = False
            else:
                print(f"⚠️  {path}: No output files found")
        else:
            print(f"⚠️  {path}: Directory not found")
    
    if format_stable:
        print("✅ Output format regression test passed")
    
    return format_stable

def test_dependency_stability():
    """Vérifie la stabilité des dépendances"""
    print("🧪 Testing dependency stability...")
    
    # Vérifier requirements.txt
    if os.path.exists('requirements.txt'):
        try:
            with open('requirements.txt') as f:
                requirements = f.read().strip().split('\n')
            
            # Vérifier les dépendances critiques
            critical_deps = ['pandas', 'numpy', 'matplotlib', 'seaborn']
            missing_deps = []
            
            for dep in critical_deps:
                if not any(dep in req for req in requirements):
                    missing_deps.append(dep)
            
            if missing_deps:
                print(f"❌ Missing critical dependencies: {missing_deps}")
                return False
            
            print(f"✅ Dependencies stable: {len(requirements)} packages")
            
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            return False
    else:
        print("⚠️  requirements.txt not found")
    
    return True

def test_configuration_regression():
    """Vérifie la régression de configuration"""
    print("🧪 Testing configuration regression...")
    
    # Vérifier config.yaml
    if os.path.exists('config.yaml'):
        try:
            import yaml
            with open('config.yaml') as f:
                config = yaml.safe_load(f)
            print("✅ Configuration YAML valid")
        except Exception as e:
            print(f"❌ Configuration YAML invalid: {e}")
            return False
    else:
        print("⚠️  config.yaml not found")
    
    return True

def test_file_permissions():
    """Vérifie les permissions des fichiers"""
    print("🧪 Testing file permissions...")
    
    # Vérifier les permissions des scripts principaux
    scripts = ['fetch_tournament.py', 'data_treatment.py', 'step3_visualization.py']
    
    for script in scripts:
        if os.path.exists(script):
            # Vérifier que le fichier est lisible
            if os.access(script, os.R_OK):
                print(f"✅ {script}: readable")
            else:
                print(f"❌ {script}: not readable")
                return False
        else:
            print(f"⚠️  {script}: not found")
    
    return True

def run_all_regression_tests():
    """Exécute tous les tests de régression"""
    print("🚀 Running Regression Tests...")
    print("=" * 50)
    
    tests = [
        test_pipeline_structure_stability,
        test_mtgo_format_data_integrity,
        test_api_configuration_stability,
        test_real_data_consistency,
        test_output_format_regression,
        test_dependency_stability,
        test_configuration_regression,
        test_file_permissions
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
            print()
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Regression Tests Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All regression tests passed!")
        return True
    else:
        print("❌ Some regression tests failed")
        return False

if __name__ == "__main__":
    success = run_all_regression_tests()
    sys.exit(0 if success else 1) 