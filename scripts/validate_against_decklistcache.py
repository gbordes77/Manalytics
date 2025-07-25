#!/usr/bin/env python3
"""
Script de validation contre fbettega/MTG_decklistcache
Compare nos données scrapées avec le repo communautaire pour vérifier la compatibilité
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheValidator:
    def __init__(self, our_data_path: str = "data/raw", cache_path: str = "external_repos/MTG_decklistcache"):
        self.our_data_path = Path(our_data_path)
        self.cache_path = Path(cache_path)
        self.validation_results = {
            'mtgo': {'matched': 0, 'missing': 0, 'extra': 0, 'format_diff': 0},
            'melee': {'matched': 0, 'missing': 0, 'extra': 0, 'format_diff': 0}
        }
        
    def load_cache_index(self, platform: str, start_date: str, end_date: str) -> Dict[str, Dict]:
        """Charge l'index des tournois du cache communautaire"""
        cache_index = {}
        
        if platform == 'mtgo':
            platform_dir = self.cache_path / "Tournaments" / "MTGO"
        else:  # melee
            platform_dir = self.cache_path / "Tournaments" / "MTGmelee"
            
        if not platform_dir.exists():
            logger.warning(f"Cache directory not found: {platform_dir}")
            return cache_index
            
        # Parser les dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Parcourir les fichiers
        for year_dir in platform_dir.iterdir():
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue
                
            year = int(year_dir.name)
            if year < start.year or year > end.year:
                continue
                
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir() or not month_dir.name.isdigit():
                    continue
                    
                month = int(month_dir.name)
                
                # Vérifier si ce mois est dans la période
                month_start = datetime(year, month, 1)
                if month_start > end:
                    continue
                    
                for day_dir in month_dir.iterdir():
                    if not day_dir.is_dir() or not day_dir.name.isdigit():
                        continue
                        
                    day = int(day_dir.name)
                    date = datetime(year, month, day)
                    
                    if date < start or date > end:
                        continue
                        
                    # Charger tous les fichiers JSON de ce jour
                    for json_file in day_dir.glob("*.json"):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                
                            tournament = data.get('Tournament', {})
                            cache_index[json_file.stem] = {
                                'path': str(json_file),
                                'name': tournament.get('Name', ''),
                                'date': tournament.get('Date', ''),
                                'format': tournament.get('Formats', ''),
                                'uri': tournament.get('Uri', ''),
                                'deck_count': len(data.get('Decks', []))
                            }
                        except Exception as e:
                            logger.error(f"Error loading {json_file}: {e}")
                            
        return cache_index
        
    def load_our_tournaments(self, platform: str, start_date: str, end_date: str) -> Dict[str, Dict]:
        """Charge nos tournois scrapés"""
        our_index = {}
        
        platform_dir = self.our_data_path / platform
        if not platform_dir.exists():
            logger.warning(f"Our data directory not found: {platform_dir}")
            return our_index
            
        # Parser les dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Parcourir tous les formats
        for format_dir in platform_dir.iterdir():
            if not format_dir.is_dir():
                continue
                
            # Parcourir récursivement pour trouver tous les JSON
            for json_file in format_dir.rglob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Extraire la date du nom de fichier ou du contenu
                    date_str = None
                    if platform == 'mtgo':
                        # Format: 2025-07-01_standard-challenge-64-2025-07-0112801190.json
                        parts = json_file.stem.split('_')
                        if parts and '-' in parts[0]:
                            date_str = parts[0]
                    else:  # melee
                        # Le fichier contient la date
                        if 'TournamentStartDate' in data:
                            date_str = data['TournamentStartDate'][:10]
                        elif 'date' in data:
                            date_str = data['date']
                            
                    if date_str:
                        try:
                            file_date = datetime.strptime(date_str, "%Y-%m-%d")
                            if file_date < start or file_date > end:
                                continue
                        except:
                            continue
                            
                    # Créer une clé unique pour la comparaison
                    if platform == 'mtgo':
                        # Pour MTGO, utiliser l'ID du tournoi
                        tournament_id = data.get('tournament_id', '')
                        key = f"{data.get('name', '').lower().replace(' ', '-')}-{date_str}{tournament_id}"
                    else:
                        # Pour Melee, utiliser le nom et la date
                        name = data.get('TournamentName', data.get('name', ''))
                        key = f"{name.lower().replace(' ', '-')}-{date_str}"
                        
                    our_index[key] = {
                        'path': str(json_file),
                        'name': data.get('TournamentName', data.get('name', '')),
                        'date': date_str,
                        'format': format_dir.name,
                        'data': data
                    }
                    
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")
                    
        return our_index
        
    def compare_structures(self, our_data: Dict, cache_data: Dict) -> Dict[str, any]:
        """Compare la structure de nos données avec le cache"""
        differences = {
            'structural_match': True,
            'missing_fields': [],
            'extra_fields': [],
            'type_mismatches': []
        }
        
        # Champs attendus dans le cache
        if 'Tournament' in cache_data:
            expected_tournament_fields = {'Date', 'Name', 'Uri', 'Formats'}
            expected_deck_fields = {'Date', 'Player', 'Result', 'AnchorUri', 'Mainboard', 'Sideboard'}
            expected_card_fields = {'Count', 'CardName'}
            
            # Vérifier si nous pouvons transformer nos données
            if 'Decks' in our_data:
                # Format Melee - déjà structuré
                differences['can_transform'] = True
                differences['transform_notes'] = "Melee format - needs Tournament wrapper"
            elif 'tournament_id' in our_data:
                # Format MTGO - nécessite transformation complète
                differences['can_transform'] = False
                differences['transform_notes'] = "MTGO format - only metadata, no decks"
            else:
                differences['can_transform'] = False
                differences['transform_notes'] = "Unknown format"
                
        return differences
        
    def validate_platform(self, platform: str, start_date: str, end_date: str):
        """Valide les données d'une plateforme"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Validating {platform.upper()} tournaments from {start_date} to {end_date}")
        logger.info(f"{'='*60}")
        
        # Charger les données
        cache_tournaments = self.load_cache_index(platform, start_date, end_date)
        our_tournaments = self.load_our_tournaments(platform, start_date, end_date)
        
        logger.info(f"\nCache tournaments: {len(cache_tournaments)}")
        logger.info(f"Our tournaments: {len(our_tournaments)}")
        
        # Comparer les tournois
        matched = []
        missing_in_ours = []
        extra_in_ours = []
        format_differences = []
        
        # Créer des mappings pour faciliter la comparaison
        cache_by_date_name = defaultdict(list)
        for key, info in cache_tournaments.items():
            date = info['date'][:10] if info['date'] else 'unknown'
            name = info['name'].lower().replace(' ', '-')
            cache_by_date_name[f"{date}_{name}"].append((key, info))
            
        our_by_date_name = defaultdict(list)
        for key, info in our_tournaments.items():
            date = info['date']
            name = info['name'].lower().replace(' ', '-')
            our_by_date_name[f"{date}_{name}"].append((key, info))
            
        # Trouver les correspondances
        all_keys = set(cache_by_date_name.keys()) | set(our_by_date_name.keys())
        
        for key in all_keys:
            cache_items = cache_by_date_name.get(key, [])
            our_items = our_by_date_name.get(key, [])
            
            if cache_items and our_items:
                # Match trouvé
                matched.append({
                    'key': key,
                    'cache': cache_items[0][1],
                    'ours': our_items[0][1]
                })
                
                # Vérifier le format
                cache_format = (cache_items[0][1].get('format') or '').lower()
                our_format = (our_items[0][1].get('format') or '').lower()
                if cache_format and our_format and cache_format != our_format:
                    format_differences.append({
                        'tournament': key,
                        'cache_format': cache_format,
                        'our_format': our_format
                    })
            elif cache_items and not our_items:
                missing_in_ours.extend(cache_items)
            elif not cache_items and our_items:
                extra_in_ours.extend(our_items)
                
        # Mettre à jour les résultats
        self.validation_results[platform]['matched'] = len(matched)
        self.validation_results[platform]['missing'] = len(missing_in_ours)
        self.validation_results[platform]['extra'] = len(extra_in_ours)
        self.validation_results[platform]['format_diff'] = len(format_differences)
        
        # Afficher le résumé
        logger.info(f"\n📊 Summary for {platform.upper()}:")
        logger.info(f"  ✅ Matched tournaments: {len(matched)}")
        logger.info(f"  ❌ Missing in our data: {len(missing_in_ours)}")
        logger.info(f"  ➕ Extra in our data: {len(extra_in_ours)}")
        logger.info(f"  ⚠️  Format differences: {len(format_differences)}")
        
        # Afficher quelques exemples
        if missing_in_ours:
            logger.info(f"\n🔍 Examples of missing tournaments (first 5):")
            for key, info in missing_in_ours[:5]:
                logger.info(f"  - {info['date']}: {info['name']} ({info['format']})")
                
        if extra_in_ours:
            logger.info(f"\n➕ Examples of extra tournaments (first 5):")
            for key, info in extra_in_ours[:5]:
                logger.info(f"  - {info['date']}: {info['name']} ({info['format']})")
                
        if format_differences:
            logger.info(f"\n⚠️  Format differences (first 5):")
            for diff in format_differences[:5]:
                logger.info(f"  - {diff['tournament']}: cache={diff['cache_format']}, ours={diff['our_format']}")
                
        # Analyser la structure si on a des matches
        if matched:
            logger.info(f"\n🔧 Structural Analysis:")
            # Prendre un exemple de chaque
            cache_example = matched[0]['cache']
            our_example = matched[0]['ours']
            
            # Charger les données complètes pour l'analyse
            try:
                with open(cache_example['path'], 'r', encoding='utf-8') as f:
                    cache_full = json.load(f)
                    
                our_full = our_example['data']
                
                struct_diff = self.compare_structures(our_full, cache_full)
                logger.info(f"  Can transform to cache format: {struct_diff.get('can_transform', False)}")
                logger.info(f"  Notes: {struct_diff.get('transform_notes', 'N/A')}")
                
            except Exception as e:
                logger.error(f"  Error analyzing structure: {e}")
                
    def generate_report(self) -> str:
        """Génère un rapport de validation"""
        report = []
        report.append("\n" + "="*80)
        report.append("VALIDATION REPORT - Comparison with fbettega/MTG_decklistcache")
        report.append("="*80)
        
        total_matched = sum(v['matched'] for v in self.validation_results.values())
        total_missing = sum(v['missing'] for v in self.validation_results.values())
        total_extra = sum(v['extra'] for v in self.validation_results.values())
        
        report.append(f"\n📊 OVERALL SUMMARY:")
        report.append(f"  Total matched tournaments: {total_matched}")
        report.append(f"  Total missing tournaments: {total_missing}")
        report.append(f"  Total extra tournaments: {total_extra}")
        
        report.append(f"\n🎯 RECOMMENDATIONS:")
        
        if total_missing > 0:
            report.append(f"\n  ❌ Missing {total_missing} tournaments from cache")
            report.append(f"     → Consider scraping these missing tournaments")
            
        if total_extra > 0:
            report.append(f"\n  ➕ We have {total_extra} extra tournaments")
            report.append(f"     → These might be newer or from different sources")
            
        if total_matched > 0:
            report.append(f"\n  ✅ {total_matched} tournaments match!")
            report.append(f"     → We can potentially skip re-processing these")
            
        # Analyse de la transformation
        report.append(f"\n🔄 DATA TRANSFORMATION ANALYSIS:")
        report.append(f"  - MTGO: Currently only storing metadata (no decklists)")
        report.append(f"  - Melee: Has full tournament data with decklists")
        report.append(f"  - Cache format: Standardized structure with Tournament wrapper")
        
        report.append(f"\n💡 CONCLUSION:")
        if total_matched > total_missing:
            report.append(f"  ✅ Good overlap with community cache!")
            report.append(f"  → We can use cache data for {total_matched} tournaments")
            report.append(f"  → Only need to scrape {total_missing} missing tournaments")
        else:
            report.append(f"  ⚠️  Limited overlap with community cache")
            report.append(f"  → May need to enhance our scraping coverage")
            
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='Validate our data against fbettega/MTG_decklistcache')
    parser.add_argument('--platform', choices=['mtgo', 'melee', 'all'], default='all',
                       help='Platform to validate')
    parser.add_argument('--start-date', default='2025-07-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', default='2025-07-25',
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--cache-path', default='external_repos/MTG_decklistcache',
                       help='Path to the cache repository')
    
    args = parser.parse_args()
    
    # Créer le validateur
    validator = CacheValidator(cache_path=args.cache_path)
    
    # Valider les plateformes
    if args.platform in ['mtgo', 'all']:
        validator.validate_platform('mtgo', args.start_date, args.end_date)
        
    if args.platform in ['melee', 'all']:
        validator.validate_platform('melee', args.start_date, args.end_date)
        
    # Générer le rapport
    report = validator.generate_report()
    print(report)
    
    # Sauvegarder le rapport
    report_path = Path('data/reports/validation_report.txt')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_path}")


if __name__ == "__main__":
    main()