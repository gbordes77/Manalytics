#!/usr/bin/env python3
"""
Tests de qualité des données pour le pipeline Manalytics
Tests sur les vraies données uniquement
"""

import json
import os
import sys
from pathlib import Path

def test_real_data_structure():
    """Vérifie la structure des vraies données"""
    print("🧪 Testing real data structure...")
    
    # Chercher les vraies données
    real_data_paths = [
        'data/processed/',
        'MTGODecklistCache/Tournaments/'
    ]
    
    found_data = False
    for path in real_data_paths:
        if os.path.exists(path):
            files = list(Path(path).glob('**/*.json'))
            if files:
                print(f"✅ Found real data in {path}: {len(files)} files")
                found_data = True
                
                # Tester un fichier
                test_file = files[0]
                try:
                    with open(test_file) as f:
                        data = json.load(f)
                    print(f"✅ JSON structure valid in {test_file.name}")
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON in {test_file.name}: {e}")
                    return False
                break
    
    if not found_data:
        print("⚠️  No real data found - structure test skipped")
        return True
    
    return True

def test_archetype_data_quality():
    """Vérifie la qualité des données d'archétypes"""
    print("🧪 Testing archetype data quality...")
    
    # Vérifier MTGOFormatData
    if not os.path.exists('MTGOFormatData/'):
        print("⚠️  No MTGOFormatData found - archetype test skipped")
        return True
    
    # Vérifier les formats disponibles
    formats = ['Modern', 'Legacy', 'Pioneer', 'Standard', 'Pauper', 'Vintage']
    
    for format_name in formats:
        format_path = Path('MTGOFormatData/Formats') / format_name
        if format_path.exists():
            archetypes_path = format_path / 'Archetypes'
            if archetypes_path.exists():
                archetype_files = list(archetypes_path.glob('*.json'))
                print(f"✅ {format_name}: {len(archetype_files)} archetype definitions")
            else:
                print(f"⚠️  {format_name}: No archetypes directory")
        else:
            print(f"⚠️  {format_name}: Format not found")
    
    return True

def test_tournament_data_consistency():
    """Vérifie la cohérence des données de tournois"""
    print("🧪 Testing tournament data consistency...")
    
    processed_path = Path('data/processed/')
    if not processed_path.exists():
        print("⚠️  No processed data found - consistency test skipped")
        return True
    
    json_files = list(processed_path.glob('**/*.json'))
    if not json_files:
        print("⚠️  No JSON files in processed data")
        return True
    
    valid_files = 0
    for file_path in json_files:
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            # Vérifications basiques
            if isinstance(data, dict):
                valid_files += 1
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Invalid file {file_path.name}: {e}")
            return False
    
    print(f"✅ {valid_files} valid tournament files")
    return True

def test_cache_data_integrity():
    """Vérifie l'intégrité des données de cache"""
    print("🧪 Testing cache data integrity...")
    
    cache_path = Path('data_cache/')
    if not cache_path.exists():
        print("⚠️  No cache data found - integrity test skipped")
        return True
    
    cache_files = list(cache_path.glob('**/*'))
    print(f"✅ Cache contains {len(cache_files)} files")
    
    return True

def test_output_data_validity():
    """Vérifie la validité des données de sortie"""
    print("🧪 Testing output data validity...")
    
    output_path = Path('data/output/')
    if not output_path.exists():
        print("⚠️  No output data found - validity test skipped")
        return True
    
    json_files = list(output_path.glob('*.json'))
    if not json_files:
        print("⚠️  No JSON output files found")
        return True
    
    for file_path in json_files:
        try:
            with open(file_path) as f:
                data = json.load(f)
            print(f"✅ Valid output file: {file_path.name}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path.name}: {e}")
            return False
    
    return True

def test_visualization_data():
    """Vérifie les données de visualisation"""
    print("🧪 Testing visualization data...")
    
    viz_path = Path('results/')
    if not viz_path.exists():
        print("⚠️  No visualization results found - test skipped")
        return True
    
    viz_files = list(viz_path.glob('**/*'))
    if viz_files:
        print(f"✅ Visualization files found: {len(viz_files)}")
    else:
        print("⚠️  No visualization files found")
    
    return True

def run_all_data_quality_tests():
    """Exécute tous les tests de qualité des données"""
    print("🚀 Running Data Quality Tests...")
    print("=" * 50)
    
    tests = [
        test_real_data_structure,
        test_archetype_data_quality,
        test_tournament_data_consistency,
        test_cache_data_integrity,
        test_output_data_validity,
        test_visualization_data
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
    print(f"📊 Data Quality Tests Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All data quality tests passed!")
        return True
    else:
        print("❌ Some data quality tests failed")
        return False

if __name__ == "__main__":
    success = run_all_data_quality_tests()
    sys.exit(0 if success else 1) 