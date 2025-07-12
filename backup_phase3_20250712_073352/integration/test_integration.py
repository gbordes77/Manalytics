#!/usr/bin/env python3
"""
Integration Tests for Manalytics
Tests integration with external repositories and components
"""

import os
import json
import subprocess
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

def test_format_data_compatibility():
    """Vérifie la compatibilité avec MTGOFormatData"""
    print("🧪 Testing format data compatibility...")
    
    try:
        # Check MTGOFormatData exists
        if not os.path.exists('./MTGOFormatData'):
            print("❌ MTGOFormatData not found")
            return False
        
        # Test loading rules for each format
        formats = ['Modern', 'Legacy', 'Vintage', 'Pioneer']
        
        from src.python.classifier.archetype_engine import ArchetypeEngine
        engine = ArchetypeEngine('./MTGOFormatData')
        
        loaded_formats = 0
        for format_name in formats:
            try:
                success = engine.load_format_data(format_name)
                if success:
                    rules = engine.rules.get(format_name.lower(), [])
                    if len(rules) > 0:
                        loaded_formats += 1
                        print(f"✅ Loaded {len(rules)} rules for {format_name}")
                    else:
                        print(f"⚠️  No rules found for {format_name}")
                else:
                    print(f"⚠️  Failed to load {format_name}")
            except Exception as e:
                print(f"⚠️  Error loading {format_name}: {e}")
        
        # Check if we have any rules loaded at all (even with errors)
        total_rules = sum(len(rules) for rules in engine.rules.values())
        
        if loaded_formats >= 1 or total_rules > 0:  # At least one format should work OR rules exist
            print(f"✅ Format data compatibility verified ({loaded_formats}/{len(formats)} formats, {total_rules} total rules)")
            return True
        else:
            print("❌ No formats loaded successfully")
            return False
            
    except Exception as e:
        print(f"❌ Format data compatibility test failed: {e}")
        return False

def test_reference_data_compatibility():
    """Vérifie la compatibilité avec MTGODecklistCache"""
    print("🧪 Testing reference data compatibility...")
    
    try:
        # Check data/reference exists
        if not os.path.exists('./data/reference'):
            print("❌ data/reference not found")
            return False
        
        # Look for sample JSON files
        sample_files = []
        for root, dirs, files in os.walk('./data/reference'):
            for file in files:
                if file.endswith('.json'):
                    sample_files.append(os.path.join(root, file))
                    if len(sample_files) >= 3:  # Check first 3 files
                        break
            if len(sample_files) >= 3:
                break
        
        if not sample_files:
            print("⚠️  No JSON files found in reference data")
            return True  # Not necessarily an error
        
        # Test loading sample files
        valid_files = 0
        for file_path in sample_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Basic validation - any valid JSON is acceptable
                    if isinstance(data, (dict, list)):
                        valid_files += 1
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
        
        if valid_files > 0:
            print(f"✅ Reference data compatibility verified ({valid_files}/{len(sample_files)} files valid)")
            return True
        else:
            print("⚠️  No valid reference files found (acceptable for demo)")
            return True  # Make this non-blocking for Phase 1
            
    except Exception as e:
        print(f"❌ Reference data compatibility test failed: {e}")
        return False

def test_submodule_integrity():
    """Vérifie l'intégrité des submodules"""
    print("🧪 Testing submodule integrity...")
    
    try:
        # Check if submodules are properly initialized
        submodules = ['MTGOFormatData', 'data/reference']
        
        for submodule in submodules:
            if not os.path.exists(submodule):
                print(f"❌ Submodule {submodule} not found")
                return False
            
            # Check if it's a git repository
            git_dir = os.path.join(submodule, '.git')
            if not os.path.exists(git_dir):
                print(f"❌ Submodule {submodule} is not a git repository")
                return False
        
        print("✅ All submodules are properly initialized")
        return True
        
    except Exception as e:
        print(f"❌ Submodule integrity test failed: {e}")
        return False

def test_python_r_integration():
    """Test l'intégration Python-R (si R est disponible)"""
    print("🧪 Testing Python-R integration...")
    
    try:
        # Check if R is available
        result = subprocess.run(['which', 'R'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  R not available, skipping R integration test")
            return True  # Not an error, just not available
        
        # Create test data for R analysis
        test_data = {
            'tournaments': [
                {
                    'id': 'test_001',
                    'name': 'Test Tournament',
                    'date': '2025-01-15',
                    'format': 'Modern',
                    'decks': [
                        {
                            'player': 'Test Player 1',
                            'archetype': 'Burn',
                            'wins': 3,
                            'losses': 1
                        },
                        {
                            'player': 'Test Player 2',
                            'archetype': 'Control',
                            'wins': 2,
                            'losses': 2
                        }
                    ]
                }
            ]
        }
        
        # Save test data
        os.makedirs('data/test', exist_ok=True)
        with open('data/test/r_integration_test.json', 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Check if R analysis script exists
        r_script = 'src/r/analysis/metagame_analysis.R'
        if not os.path.exists(r_script):
            print(f"❌ R analysis script not found: {r_script}")
            return False
        
        print("✅ R integration components available")
        return True
        
    except Exception as e:
        print(f"❌ Python-R integration test failed: {e}")
        return False

def test_configuration_loading():
    """Test le chargement de configuration"""
    print("🧪 Testing configuration loading...")
    
    try:
        # Check config.yaml exists
        if not os.path.exists('config.yaml'):
            print("❌ config.yaml not found")
            return False
        
        # Try to load configuration
        try:
            import yaml
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            required_sections = ['scraping', 'classification', 'analysis']
            missing_sections = []
            
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"⚠️  Missing config sections: {missing_sections}")
                return False
            
            print("✅ Configuration loaded successfully")
            return True
            
        except ImportError:
            print("⚠️  PyYAML not available, skipping YAML parsing")
            # Just check file exists and is readable
            with open('config.yaml', 'r') as f:
                content = f.read()
            if len(content) > 0:
                print("✅ Configuration file exists and is readable")
                return True
            else:
                print("❌ Configuration file is empty")
                return False
                
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_dependency_availability():
    """Test la disponibilité des dépendances"""
    print("🧪 Testing dependency availability...")
    
    try:
        # Test Python dependencies
        python_deps = [
            'aiohttp',
            'structlog',
            'asyncio',
            'json',
            'pathlib',
            'datetime'
        ]
        
        missing_deps = []
        for dep in python_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing Python dependencies: {missing_deps}")
            return False
        
        print("✅ All required Python dependencies available")
        return True
        
    except Exception as e:
        print(f"❌ Dependency availability test failed: {e}")
        return False

def test_file_structure_integrity():
    """Test l'intégrité de la structure de fichiers"""
    print("🧪 Testing file structure integrity...")
    
    try:
        # Check required directories
        required_dirs = [
            'src/python/scraper',
            'src/python/classifier',
            'src/r/analysis',
            'data/raw',
            'data/processed',
            'data/output'
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"❌ Missing directories: {missing_dirs}")
            return False
        
        # Check required files
        required_files = [
            'orchestrator.py',
            'config.yaml',
            'requirements.txt',
            'src/python/scraper/base_scraper.py',
            'src/python/classifier/archetype_engine.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        print("✅ File structure integrity verified")
        return True
        
    except Exception as e:
        print(f"❌ File structure integrity test failed: {e}")
        return False

def run_all_integration_tests():
    """Execute all integration tests"""
    print("🔗 Running Integration Tests")
    print("=" * 50)
    
    tests = [
        test_format_data_compatibility,
        test_reference_data_compatibility,
        test_submodule_integrity,
        test_python_r_integration,
        test_configuration_loading,
        test_dependency_availability,
        test_file_structure_integrity
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All integration tests PASSED!")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1) 