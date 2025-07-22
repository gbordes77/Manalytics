#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de Connectivité MTG Analytics Pipeline
Ce script teste la connectivité avec les différentes sources de données MTG.
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configuration des couleurs pour les messages
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(message):
    """Affiche un message d'information."""
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def log_success(message):
    """Affiche un message de succès."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def log_warning(message):
    """Affiche un message d'avertissement."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {message}")

def log_error(message):
    """Affiche un message d'erreur."""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}")

def test_url_connectivity(url, timeout=10):
    """Teste la connectivité vers une URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return True, response.status_code, response.elapsed.total_seconds()
        else:
            return False, response.status_code, response.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        return False, str(e), 0

def test_mtgo_connectivity():
    """Teste la connectivité vers MTGO."""
    log_info("Testing MTGO connectivity...")
    
    mtgo_urls = [
        "https://www.mtgo.com/decklists",
        "https://www.mtgo.com/tournaments",
        "https://www.mtgo.com/standings"
    ]
    
    results = {}
    for url in mtgo_urls:
        success, status, response_time = test_url_connectivity(url)
        results[url] = {
            'success': success,
            'status': status,
            'response_time': response_time
        }
        
        if success:
            log_success(f"MTGO {url} - Status: {status}, Time: {response_time:.2f}s")
        else:
            log_error(f"MTGO {url} - Failed: {status}")
    
    return results

def test_mtgmelee_connectivity():
    """Teste la connectivité vers MTGMelee."""
    log_info("Testing MTGMelee connectivity...")
    
    melee_urls = [
        "https://melee.gg",
        "https://melee.gg/Decklists",
        "https://melee.gg/Tournaments"
    ]
    
    results = {}
    for url in melee_urls:
        success, status, response_time = test_url_connectivity(url)
        results[url] = {
            'success': success,
            'status': status,
            'response_time': response_time
        }
        
        if success:
            log_success(f"MTGMelee {url} - Status: {status}, Time: {response_time:.2f}s")
        else:
            log_error(f"MTGMelee {url} - Failed: {status}")
    
    return results

def test_topdeck_connectivity():
    """Teste la connectivité vers Topdeck."""
    log_info("Testing Topdeck connectivity...")
    
    topdeck_urls = [
        "https://topdeck.gg",
        "https://topdeck.gg/decklists",
        "https://topdeck.gg/tournaments"
    ]
    
    results = {}
    for url in topdeck_urls:
        success, status, response_time = test_url_connectivity(url)
        results[url] = {
            'success': success,
            'status': status,
            'response_time': response_time
        }
        
        if success:
            log_success(f"Topdeck {url} - Status: {status}, Time: {response_time:.2f}s")
        else:
            log_error(f"Topdeck {url} - Failed: {status}")
    
    return results

def test_local_repositories():
    """Teste la présence des repositories locaux."""
    log_info("Testing local repositories...")
    
    base_dir = Path(__file__).parent
    repositories = {
        'mtg_decklist_scrapper': base_dir / 'data-collection' / 'scraper' / 'mtgo',
        'MTG_decklistcache': base_dir / 'data-collection' / 'raw-cache',
        'MTGODecklistCache': base_dir / 'data-collection' / 'processed-cache',
        'MTGOArchetypeParser': base_dir / 'data-treatment' / 'parser',
        'MTGOFormatData': base_dir / 'data-treatment' / 'format-rules',
        'R-Meta-Analysis': base_dir / 'visualization' / 'r-analysis'
    }
    
    results = {}
    for repo_name, repo_path in repositories.items():
        if repo_path.exists():
            # Vérifier si c'est un repository git
            git_dir = repo_path / '.git'
            if git_dir.exists():
                log_success(f"Repository {repo_name} found at {repo_path}")
                results[repo_name] = {'exists': True, 'is_git': True, 'path': str(repo_path)}
            else:
                log_warning(f"Directory {repo_name} exists but is not a git repository")
                results[repo_name] = {'exists': True, 'is_git': False, 'path': str(repo_path)}
        else:
            log_error(f"Repository {repo_name} not found at {repo_path}")
            results[repo_name] = {'exists': False, 'is_git': False, 'path': str(repo_path)}
    
    return results

def test_configuration_files():
    """Teste la présence des fichiers de configuration."""
    log_info("Testing configuration files...")
    
    base_dir = Path(__file__).parent
    config_files = {
        'sources.json': base_dir / 'config' / 'sources.json',
        'melee_login.json': base_dir / 'data-collection' / 'scraper' / 'mtgo' / 'melee_login.json',
        'api_topdeck.txt': base_dir / 'data-collection' / 'scraper' / 'mtgo' / 'Api_token_and_login' / 'api_topdeck.txt'
    }
    
    results = {}
    for file_name, file_path in config_files.items():
        if file_path.exists():
            log_success(f"Configuration file {file_name} found")
            results[file_name] = {'exists': True, 'path': str(file_path)}
        else:
            log_warning(f"Configuration file {file_name} not found at {file_path}")
            results[file_name] = {'exists': False, 'path': str(file_path)}
    
    return results

def test_dependencies():
    """Teste la présence des dépendances requises."""
    log_info("Testing dependencies...")
    
    # Test Python packages
    python_packages = [
        'requests', 'bs4', 'numpy', 'pandas',
        'click', 'rich', 'tqdm', 'yaml'
    ]
    
    results = {'python_packages': {}, 'system_commands': {}}
    
    for package in python_packages:
        try:
            __import__(package)
            log_success(f"Python package {package} is available")
            results['python_packages'][package] = True
        except ImportError:
            log_error(f"Python package {package} is not available")
            results['python_packages'][package] = False
    
    # Test system commands
    system_commands = ['git', 'python3', 'dotnet', 'R']
    
    for command in system_commands:
        try:
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                log_success(f"System command {command} is available: {version}")
                results['system_commands'][command] = True
            else:
                log_error(f"System command {command} failed")
                results['system_commands'][command] = False
        except Exception as e:
            log_error(f"System command {command} is not available: {e}")
            results['system_commands'][command] = False
    
    return results

def test_data_availability():
    """Teste la disponibilité des données récentes."""
    log_info("Testing data availability...")
    
    base_dir = Path(__file__).parent
    raw_cache_dir = base_dir / 'data-collection' / 'raw-cache' / 'Tournaments'
    
    results = {'tournaments_found': 0, 'recent_tournaments': 0, 'formats': []}
    
    if raw_cache_dir.exists():
        # Compter les tournois
        tournament_files = list(raw_cache_dir.rglob('*.json'))
        results['tournaments_found'] = len(tournament_files)
        
        # Vérifier les tournois récents (7 derniers jours)
        recent_date = datetime.now() - timedelta(days=7)
        recent_count = 0
        
        for file_path in tournament_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'Tournament' in data and 'date' in data['Tournament']:
                        tournament_date = datetime.strptime(data['Tournament']['date'], '%Y-%m-%d')
                        if tournament_date >= recent_date:
                            recent_count += 1
                        
                        # Collecter les formats
                        if 'formats' in data['Tournament']:
                            results['formats'].extend(data['Tournament']['formats'])
            except Exception as e:
                log_warning(f"Error reading tournament file {file_path}: {e}")
        
        results['recent_tournaments'] = recent_count
        results['formats'] = list(set(results['formats']))  # Dédupliquer
        
        log_success(f"Found {results['tournaments_found']} tournament files")
        log_success(f"Found {results['recent_tournaments']} recent tournaments (last 7 days)")
        log_success(f"Formats available: {', '.join(results['formats'])}")
    else:
        log_warning("Raw cache directory not found")
    
    return results

def generate_report(all_results):
    """Génère un rapport de test."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        },
        'results': all_results
    }
    
    # Calculer les statistiques
    for category, results in all_results.items():
        if isinstance(results, dict):
            for test_name, test_result in results.items():
                report['summary']['total_tests'] += 1
                if isinstance(test_result, dict):
                    if test_result.get('success', test_result.get('exists', False)):
                        report['summary']['passed_tests'] += 1
                    else:
                        report['summary']['failed_tests'] += 1
                elif isinstance(test_result, bool):
                    if test_result:
                        report['summary']['passed_tests'] += 1
                    else:
                        report['summary']['failed_tests'] += 1
    
    return report

def save_report(report, output_file='connection_test_report.json'):
    """Sauvegarde le rapport de test."""
    try:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        log_success(f"Test report saved to {output_file}")
    except Exception as e:
        log_error(f"Failed to save test report: {e}")

def main():
    """Fonction principale."""
    print(f"{Colors.BOLD}MTG Analytics Pipeline - Connection Test{Colors.ENDC}")
    print("=" * 50)
    
    all_results = {}
    
    # Tests de connectivité
    all_results['mtgo_connectivity'] = test_mtgo_connectivity()
    all_results['mtgmelee_connectivity'] = test_mtgmelee_connectivity()
    all_results['topdeck_connectivity'] = test_topdeck_connectivity()
    
    # Tests locaux
    all_results['local_repositories'] = test_local_repositories()
    all_results['configuration_files'] = test_configuration_files()
    all_results['dependencies'] = test_dependencies()
    all_results['data_availability'] = test_data_availability()
    
    # Générer et sauvegarder le rapport
    report = generate_report(all_results)
    save_report(report)
    
    # Afficher le résumé
    print("\n" + "=" * 50)
    print(f"{Colors.BOLD}Test Summary{Colors.ENDC}")
    print(f"Total tests: {report['summary']['total_tests']}")
    print(f"Passed: {Colors.GREEN}{report['summary']['passed_tests']}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{report['summary']['failed_tests']}{Colors.ENDC}")
    
    if report['summary']['failed_tests'] == 0:
        print(f"\n{Colors.GREEN}✅ All tests passed! The pipeline is ready to use.{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Please check the report for details.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())