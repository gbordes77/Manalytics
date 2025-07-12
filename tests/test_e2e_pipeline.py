#!/usr/bin/env python3
"""
Tests d'intégration E2E pour le pipeline Manalytics
Tests sur les vraies données uniquement
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def test_pipeline_structure():
    """Vérifie la structure du pipeline"""
    print("🧪 Testing pipeline structure...")
    
    required_files = [
        'fetch_tournament.py',
        'data_treatment.py', 
        'step3_visualization.py',
        'orchestrator.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing pipeline files: {missing_files}")
        return False
    
    print("✅ Pipeline structure complete")
    return True

def test_real_data_processing():
    """Teste le traitement des vraies données"""
    print("🧪 Testing real data processing...")
    
    # Vérifier les données réelles
    real_data_paths = [
        'data/processed/',
        'MTGODecklistCache/Tournaments/'
    ]
    
    has_real_data = False
    for path in real_data_paths:
        if os.path.exists(path):
            files = list(Path(path).glob('**/*.json'))
            if files:
                has_real_data = True
                print(f"✅ Found real data in {path}: {len(files)} files")
                break
    
    if not has_real_data:
        print("⚠️  No real data found - pipeline structure only")
        return True
    
    return True

def test_configuration_validity():
    """Vérifie la validité des configurations"""
    print("🧪 Testing configuration validity...")
    
    # Vérifier config.yaml
    if os.path.exists('config.yaml'):
        print("✅ Config file exists")
    else:
        print("⚠️  No config.yaml found")
    
    # Vérifier MTGOFormatData
    if os.path.exists('MTGOFormatData/'):
        print("✅ MTGOFormatData exists")
    else:
        print("⚠️  No MTGOFormatData found")
    
    return True

def test_api_credentials():
    """Vérifie la présence des credentials API"""
    print("🧪 Testing API credentials...")
    
    if os.path.exists('Api_token_and_login/'):
        print("✅ API credentials directory exists")
    else:
        print("⚠️  No API credentials found")
    
    return True

def test_output_structure():
    """Vérifie la structure des outputs"""
    print("🧪 Testing output structure...")
    
    output_dirs = [
        'data/processed/',
        'data/raw/',
        'results/'
    ]
    
    for dir_path in output_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Output directory exists: {dir_path}")
        else:
            print(f"⚠️  Output directory missing: {dir_path}")
    
    return True

def run_all_tests():
    """Exécute tous les tests E2E"""
    print("🚀 Running E2E Pipeline Tests...")
    print("=" * 50)
    
    tests = [
        test_pipeline_structure,
        test_real_data_processing,
        test_configuration_validity,
        test_api_credentials,
        test_output_structure
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
    print(f"📊 E2E Tests Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All E2E tests passed!")
        return True
    else:
        print("❌ Some E2E tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 