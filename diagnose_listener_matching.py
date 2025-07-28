#!/usr/bin/env python3
"""
Script de diagnostic pour comprendre pourquoi seulement 41 matchs sont extraits
Analyse le matching entre listener (MTGOData) et cache
"""

import json
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set

class ListenerMatchingDiagnostic:
    """Diagnostic du matching listener ↔ cache"""
    
    def __init__(self):
        self.listener_tournaments = {}
        self.cache_tournaments = {}
        self.matched_pairs = []
        self.unmatched_listener = []
        self.unmatched_cache = []
        
    def extract_tournament_id(self, filename: str) -> str:
        """Extraire l'ID numérique du tournoi depuis différents formats"""
        # Patterns possibles:
        # - "12801190.json"
        # - "standard-challenge-64-12801190.json"
        # - "2025-07-01_standard-challenge-64-2025-07-0112801190.json"
        # - "Standard Challenge 32 (12801654)_2025-07-05.json"
        
        patterns = [
            r'(\d{8})\.json$',  # ID direct
            r'-(\d{8})\.json$',  # Avec tiret
            r'\((\d{8})\)',     # Entre parenthèses
            r'(\d{8})(?=\.json$)',  # Avant .json
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        # Si aucun pattern ne match, essayer de trouver n'importe quel nombre de 8 chiffres
        eight_digit = re.search(r'(\d{8})', filename)
        if eight_digit:
            return eight_digit.group(1)
            
        return None
    
    def load_listener_data(self) -> int:
        """Charge les données depuis MTGOData (listener)"""
        print("📊 Chargement des données listener depuis data/MTGOData...")
        
        mtgo_path = Path("data/MTGOData/2025")
        count = 0
        
        # Parcourir tous les fichiers JSON Standard
        for json_file in mtgo_path.rglob("*standard*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Extraire les infos
                tournament_id = data['Tournament']['Id']
                date = datetime.strptime(data['Tournament']['Date'][:10], '%Y-%m-%d')
                
                # Filtrer juillet 1-21
                if date.month == 7 and 1 <= date.day <= 21:
                    self.listener_tournaments[str(tournament_id)] = {
                        'id': tournament_id,
                        'name': data['Tournament']['Name'],
                        'date': date,
                        'file': str(json_file),
                        'rounds': len(data.get('Rounds', [])),
                        'total_matches': sum(len(r.get('Matches', [])) for r in data.get('Rounds', []))
                    }
                    count += 1
            except Exception as e:
                print(f"⚠️ Erreur lecture {json_file}: {e}")
        
        print(f"✅ Chargé {count} tournois Standard du listener (juillet 1-21)")
        return count
    
    def load_cache_data(self) -> int:
        """Charge les données depuis le cache (raw files)"""
        print("\n📋 Chargement des données du cache depuis data/raw/mtgo/standard...")
        
        cache_path = Path("data/raw/mtgo/standard")
        count = 0
        
        for json_file in cache_path.glob("*.json"):
            try:
                # Extraire l'ID du nom de fichier
                tournament_id = self.extract_tournament_id(str(json_file.name))
                
                if tournament_id:
                    # Lire le fichier pour avoir plus d'infos
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Vérifier la date
                    if 'Tournament' in data and 'Date' in data['Tournament']:
                        date_str = data['Tournament']['Date']
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        
                        # Filtrer juillet 1-21
                        if date.month == 7 and 1 <= date.day <= 21:
                            self.cache_tournaments[tournament_id] = {
                                'id': tournament_id,
                                'name': data['Tournament'].get('Name', 'Unknown'),
                                'date': date,
                                'file': str(json_file),
                                'decks_count': len(data.get('Decks', []))
                            }
                            count += 1
                    
            except Exception as e:
                print(f"⚠️ Erreur lecture {json_file}: {e}")
        
        print(f"✅ Chargé {count} tournois Standard du cache (juillet 1-21)")
        return count
    
    def analyze_matching(self):
        """Analyse le matching entre listener et cache"""
        print("\n🔍 Analyse du matching...")
        
        # IDs sets pour comparaison rapide
        listener_ids = set(self.listener_tournaments.keys())
        cache_ids = set(self.cache_tournaments.keys())
        
        # Matching direct par ID
        matched_ids = listener_ids & cache_ids
        
        # Analyser les matchs
        for tournament_id in matched_ids:
            self.matched_pairs.append({
                'id': tournament_id,
                'listener': self.listener_tournaments[tournament_id],
                'cache': self.cache_tournaments[tournament_id]
            })
        
        # Non-matchés
        unmatched_listener_ids = listener_ids - cache_ids
        unmatched_cache_ids = cache_ids - listener_ids
        
        for tid in unmatched_listener_ids:
            self.unmatched_listener.append(self.listener_tournaments[tid])
            
        for tid in unmatched_cache_ids:
            self.unmatched_cache.append(self.cache_tournaments[tid])
        
        print(f"\n📊 RÉSULTATS DU MATCHING:")
        print(f"✅ Tournois matchés: {len(self.matched_pairs)}")
        print(f"❌ Tournois listener non-matchés: {len(self.unmatched_listener)}")
        print(f"❌ Tournois cache non-matchés: {len(self.unmatched_cache)}")
    
    def calculate_potential_matches(self):
        """Calcule le nombre potentiel de matchs"""
        print("\n📈 CALCUL DU POTENTIEL DE MATCHS:")
        
        total_matches_available = 0
        for match in self.matched_pairs:
            total_matches_available += match['listener']['total_matches']
        
        print(f"💫 Matchs disponibles dans les tournois matchés: {total_matches_available}")
        
        # Détail par tournoi
        print("\n📋 Détail des tournois matchés:")
        for match in sorted(self.matched_pairs, key=lambda x: x['listener']['date']):
            l_data = match['listener']
            c_data = match['cache']
            print(f"  - {l_data['date'].strftime('%Y-%m-%d')} | {l_data['name']} | "
                  f"ID: {match['id']} | Rounds: {l_data['rounds']} | "
                  f"Matchs: {l_data['total_matches']} | Decks cache: {c_data['decks_count']}")
    
    def show_unmatched_details(self):
        """Affiche les détails des tournois non-matchés"""
        if self.unmatched_listener:
            print(f"\n❌ TOURNOIS LISTENER NON-MATCHÉS ({len(self.unmatched_listener)}):")
            for t in sorted(self.unmatched_listener, key=lambda x: x['date']):
                print(f"  - {t['date'].strftime('%Y-%m-%d')} | {t['name']} | "
                      f"ID: {t['id']} | Matchs: {t['total_matches']}")
        
        if self.unmatched_cache:
            print(f"\n❌ TOURNOIS CACHE NON-MATCHÉS ({len(self.unmatched_cache)}):")
            for t in sorted(self.unmatched_cache, key=lambda x: x['date']):
                print(f"  - {t['date'].strftime('%Y-%m-%d')} | {t['name']} | "
                      f"ID: {t['id']} | Decks: {t['decks_count']}")
    
    def check_current_script_issue(self):
        """Vérifie pourquoi le script actuel ne trouve que 41 matchs"""
        print("\n🔍 ANALYSE DU PROBLÈME ACTUEL:")
        
        # Le script actuel cherche dans 'jiliaclistener' pas 'data/MTGOData'
        jiliac_path = Path("jiliaclistener")
        if not jiliac_path.exists():
            print("❌ Le dossier 'jiliaclistener' n'existe pas!")
            print("   Le script cherche au mauvais endroit.")
            print("   Les données sont dans 'data/MTGOData'")
        else:
            # Vérifier si c'est un lien symbolique
            if jiliac_path.is_symlink():
                print(f"⚠️ 'jiliaclistener' est un lien symbolique vers: {jiliac_path.resolve()}")
            
            # Compter les fichiers
            json_files = list(jiliac_path.rglob("*.json"))
            print(f"📁 Fichiers JSON dans jiliaclistener: {len(json_files)}")
    
    def suggest_fixes(self):
        """Suggère des corrections"""
        print("\n💡 SUGGESTIONS DE FIX:")
        
        print("\n1. MODIFIER LE PATH DANS analyze_july_with_cache_and_listener.py:")
        print("   Ligne 40: listener_path = Path('jiliaclistener')")
        print("   Changer en: listener_path = Path('data/MTGOData/2025')")
        
        print("\n2. ADAPTER LA STRUCTURE DE PARCOURS:")
        print("   Le script cherche des dossiers par jour (01, 02, ...)")
        print("   Mais MTGOData utilise: 2025/07/01, 2025/07/02, ...")
        
        print("\n3. AMÉLIORER LE MATCHING D'IDS:")
        print("   Utiliser la fonction extract_tournament_id() pour être plus robuste")
        
        print("\n4. EXEMPLE DE CODE CORRIGÉ:")
        print("""
    def load_listener_data(self):
        listener_path = Path("data/MTGOData/2025/07")
        count = 0
        
        for day in range(1, 22):  # Juillet 1-21
            day_folder = listener_path / f"{day:02d}"
            if day_folder.exists():
                for file in day_folder.glob("*standard*.json"):
                    # ... reste du code
        """)
    
    def run_diagnostic(self):
        """Lance le diagnostic complet"""
        print("=" * 80)
        print("🔍 DIAGNOSTIC DU MATCHING LISTENER ↔ CACHE")
        print("=" * 80)
        
        # 1. Charger les données
        listener_count = self.load_listener_data()
        cache_count = self.load_cache_data()
        
        # 2. Analyser le matching
        self.analyze_matching()
        
        # 3. Calculer le potentiel
        self.calculate_potential_matches()
        
        # 4. Montrer les non-matchés
        self.show_unmatched_details()
        
        # 5. Vérifier le problème actuel
        self.check_current_script_issue()
        
        # 6. Suggérer des fixes
        self.suggest_fixes()
        
        print("\n" + "=" * 80)
        print("✅ DIAGNOSTIC TERMINÉ")
        print("=" * 80)


if __name__ == "__main__":
    diagnostic = ListenerMatchingDiagnostic()
    diagnostic.run_diagnostic()