#!/usr/bin/env python3
"""
Script d'activation de la politique NO MOCK DATA
Configure automatiquement le projet pour rejeter toute donnée mockée
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Active la politique NO MOCK DATA"""
    
    print("🚀 ACTIVATION POLITIQUE NO MOCK DATA")
    print("=" * 50)
    
    # 1. Configurer les variables d'environnement
    print("⚙️  Configuration des variables d'environnement...")
    
    env_vars = {
        'NO_MOCK_DATA': 'true',
        'REJECT_MOCK_DATA': 'true',
        'REQUIRE_REAL_SOURCES': 'true',
        'PYTHONPATH': f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  ✅ {key}={value}")
    
    # 2. Créer les dossiers nécessaires
    print("\n📁 Création des dossiers...")
    
    required_dirs = [
        'config',
        'scripts', 
        'enforcement',
        '.github/workflows'
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}/")
    
    # 3. Vérifier que les fichiers de politique existent
    print("\n📋 Vérification des fichiers de politique...")
    
    required_files = [
        'config/no_mock_policy.py',
        'enforcement/strict_mode.py',
        'scripts/check_no_mocks.py',
        '.git/hooks/pre-commit',
        '.github/workflows/no-mock-validation.yml',
        'tests/conftest.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (manquant)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} fichier(s) manquant(s)")
        print("🔧 Exécuter d'abord la création des fichiers de politique")
        return False
    
    # 4. Rendre les scripts exécutables
    print("\n🔧 Configuration des permissions...")
    
    executable_files = [
        'scripts/check_no_mocks.py',
        '.git/hooks/pre-commit'
    ]
    
    for file_path in executable_files:
        try:
            os.chmod(file_path, 0o755)
            print(f"  ✅ {file_path} rendu exécutable")
        except Exception as e:
            print(f"  ❌ Erreur avec {file_path}: {e}")
    
    # 5. Tester la validation
    print("\n🧪 Test de validation...")
    
    try:
        # Importer et tester le module de politique
        sys.path.insert(0, str(Path.cwd()))
        from config.no_mock_policy import enforce_real_data_only, Settings
        
        # Activer le mode strict
        enforce_real_data_only()
        print("  ✅ Mode strict activé")
        
        # Valider l'environnement
        Settings.validate_environment()
        print("  ✅ Environnement validé")
        
    except Exception as e:
        print(f"  ❌ Erreur de validation: {e}")
        return False
    
    # 6. Tester le script de vérification
    print("\n🔍 Test du script de vérification...")
    
    try:
        result = subprocess.run([
            'python', 'scripts/check_no_mocks.py', 'config/no_mock_policy.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Script de vérification fonctionne")
        else:
            print(f"  ❌ Erreur dans le script: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Impossible de tester le script: {e}")
        return False
    
    # 7. Configurer Git
    print("\n📝 Configuration Git...")
    
    try:
        # Configurer Git pour utiliser le hook
        subprocess.run(['git', 'config', 'core.hooksPath', '.git/hooks'], check=True)
        print("  ✅ Hooks Git configurés")
        
        # Ajouter la configuration au .gitignore si nécessaire
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            if 'mock_data' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n# Mock data (interdit)\n')
                    f.write('*mock*\n')
                    f.write('*fake*\n')
                    f.write('*dummy*\n')
                    f.write('test_data/\n')
                print("  ✅ .gitignore mis à jour")
        
    except Exception as e:
        print(f"  ⚠️  Configuration Git: {e}")
    
    # 8. Afficher le résumé
    print("\n" + "=" * 50)
    print("✅ POLITIQUE NO MOCK DATA ACTIVÉE")
    print("=" * 50)
    
    print("\n📋 RÈGLES ACTIVÉES:")
    print("  ❌ Aucune donnée mockée autorisée")
    print("  ❌ Imports de mock interdits")
    print("  ❌ Patterns test/fake/dummy interdits")
    print("  ✅ Seules les données réelles acceptées")
    
    print("\n🔧 ENFORCEMENT ACTIVÉ:")
    print("  ✅ Git hook pre-commit")
    print("  ✅ CI/CD GitHub Actions")
    print("  ✅ Validation pytest")
    print("  ✅ Mode strict Python")
    
    print("\n📊 SOURCES DE DONNÉES AUTORISÉES:")
    print("  ✅ MTGODecklistCache/Tournaments/")
    print("  ✅ data/raw/ (données scrapées)")
    print("  ✅ API Scryfall")
    print("  ✅ Scraping Melee.gg/MTGO")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("  1. Tester un commit : git add . && git commit -m 'test'")
    print("  2. Lancer les tests : pytest tests/")
    print("  3. Vérifier le codebase : python scripts/check_no_mocks.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 