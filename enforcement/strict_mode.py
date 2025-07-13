"""
Mode strict pour développement - AUCUNE DONNÉE MOCKÉE
"""

import os
import sys
import builtins
from pathlib import Path
from config.no_mock_policy import NoMockDataError, RealDataEnforcer, Settings

def enforce_real_data_only():
    """Active le mode strict globalement"""
    
    print("🔄 Activation du mode strict NO MOCK DATA...")
    
    # 1. Configurer les variables d'environnement
    os.environ['REJECT_MOCK_DATA'] = 'true'
    os.environ['REQUIRE_REAL_SOURCES'] = 'true'
    os.environ['NO_MOCK_DATA'] = 'true'
    os.environ['PYTHONPATH'] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"
    
    # 2. Valider l'environnement
    try:
        Settings.validate_environment()
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # 3. Monkey-patch pour intercepter les créations de données suspectes
    original_dict = dict
    
    class StrictDict(original_dict):
        def __setitem__(self, key, value):
            # Vérifier les valeurs suspectes
            if isinstance(value, str):
                try:
                    RealDataEnforcer.validate_no_mock_data(value)
                except NoMockDataError as e:
                    print(f"❌ INTERDIT: Tentative d'ajout de donnée mockée")
                    print(f"Clé: {key}, Valeur: {value}")
                    raise e
            super().__setitem__(key, value)
    
    # 4. Intercepter les imports de modules de mock
    original_import = builtins.__import__
    
    def strict_import(name, *args, **kwargs):
        # Bloquer les modules de mock
        forbidden_modules = [
            'unittest.mock',
            'mock',
            'pytest_mock',
            'responses',
            'httpretty'
        ]
        
        if name in forbidden_modules:
            raise ImportError(
                f"❌ MODULE INTERDIT: {name}\n"
                f"📋 Règle: Aucun mock autorisé\n"
                f"🔧 Utiliser des données réelles uniquement"
            )
        
        return original_import(name, *args, **kwargs)
    
    builtins.__import__ = strict_import
    
    # 5. Vérifier la disponibilité des données réelles
    real_data_count = 0
    for path in Settings.REAL_DATA_PATHS:
        if path.exists():
            real_data_count += len(list(path.rglob('*.json')))
    
    if real_data_count < Settings.MINIMUM_REAL_TOURNAMENTS:
        print(f"⚠️  Attention: Seulement {real_data_count} fichiers de données réelles")
        print(f"📋 Minimum recommandé: {Settings.MINIMUM_REAL_TOURNAMENTS}")
    
    print("✅ MODE STRICT ACTIVÉ: Données réelles uniquement!")
    print(f"📊 {real_data_count} fichiers de données réelles disponibles")
    
    return True


def disable_mock_libraries():
    """Désactive complètement les bibliothèques de mock"""
    
    # Désactiver unittest.mock
    try:
        import unittest.mock
        unittest.mock.Mock = None
        unittest.mock.MagicMock = None
        unittest.mock.patch = None
        print("✅ unittest.mock désactivé")
    except ImportError:
        pass
    
    # Désactiver pytest-mock
    try:
        import pytest_mock
        pytest_mock.MockFixture = None
        pytest_mock.mocker = None
        print("✅ pytest-mock désactivé")
    except ImportError:
        pass
    
    # Désactiver responses
    try:
        import responses
        responses.mock = None
        print("✅ responses désactivé")
    except ImportError:
        pass


def validate_codebase_no_mocks():
    """Valide que le codebase ne contient pas de données mockées"""
    
    print("🔍 Validation du codebase...")
    
    # Patterns à détecter
    mock_patterns = [
        r'mock\w*',
        r'fake\w*',
        r'dummy\w*',
        r'test_data',
        r'Player\d+',
        r'Deck\d+',
        r'Card\d+',
        r'example\w*',
        r'sample\w*'
    ]
    
    # Fichiers à vérifier
    python_files = list(Path('.').rglob('*.py'))
    json_files = list(Path('.').rglob('*.json'))
    
    violations = []
    
    # Vérifier les fichiers Python
    for py_file in python_files:
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in mock_patterns:
                import re
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append({
                        'file': str(py_file),
                        'pattern': pattern,
                        'matches': matches
                    })
        except Exception:
            continue
    
    # Vérifier les fichiers JSON
    for json_file in json_files:
        if 'venv' in str(json_file) or 'node_modules' in str(json_file):
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in mock_patterns:
                import re
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append({
                        'file': str(json_file),
                        'pattern': pattern,
                        'matches': matches
                    })
        except Exception:
            continue
    
    if violations:
        print("❌ VIOLATIONS DÉTECTÉES:")
        for violation in violations[:10]:  # Limiter l'affichage
            print(f"  📁 {violation['file']}")
            print(f"  🔍 Pattern: {violation['pattern']}")
            print(f"  ⚠️  Matches: {violation['matches'][:5]}")
            print()
        
        if len(violations) > 10:
            print(f"... et {len(violations) - 10} autres violations")
        
        return False
    
    print("✅ Aucune donnée mockée détectée dans le codebase")
    return True


if __name__ == "__main__":
    try:
        enforce_real_data_only()
        disable_mock_libraries()
        
        if validate_codebase_no_mocks():
            print("✅ Validation complète réussie")
        else:
            print("❌ Validation échouée - Corriger les violations")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1) 