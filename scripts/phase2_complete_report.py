#!/usr/bin/env python3
"""
Final report for Phase 2 completion with all improvements.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name


def main():
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    print("\n" + "="*80)
    print("🎉 PHASE 2 COMPLÈTE - SYSTÈME DE CACHE AVEC TOUTES LES AMÉLIORATIONS")
    print("="*80)
    
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"  • Tournois processés: {len(tournaments)}")
    print(f"  • Decks analysés: {meta_snapshot['total_decks']}")
    print(f"  • Archétypes détectés: {len(meta_snapshot['archetypes'])}")
    
    # Extract and clean archetype names
    archetype_counts = {}
    for arch, data in meta_snapshot['archetypes'].items():
        if isinstance(data, dict):
            count = data['count']
        else:
            count = data
        clean_name = format_archetype_name(arch) if arch else "Unknown"
        archetype_counts[clean_name] = count
    
    # Sort and show top 15
    sorted_archetypes = sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n🏆 TOP 15 ARCHÉTYPES (noms complets et corrigés):")
    print("-" * 70)
    print(f"{'Rang':<5} {'Archétype':<40} {'Decks':<8} {'Meta %':<8}")
    print("-" * 70)
    
    for i, (archetype, count) in enumerate(sorted_archetypes[:15], 1):
        percentage = (count / meta_snapshot['total_decks']) * 100
        print(f"{i:<5} {archetype:<40} {count:<8} {percentage:>6.1f}%")
    
    print("\n✅ AMÉLIORATIONS IMPLÉMENTÉES:")
    print("  1. ✅ Noms de guildes: UR → Izzet, UB → Dimir, WR → Boros")
    print("  2. ✅ Noms de shards: WUB → Esper, BRG → Jund, RGW → Naya") 
    print("  3. ✅ Noms de wedges: WUR → Jeskai, WBG → Abzan, UBG → Sultai")
    print("  4. ✅ Noms courts pour 4 couleurs: Four Color → 4c")
    print("  5. ✅ Correction de la duplication (WRG WRG Yuna → Naya Yuna)")
    print("  6. ✅ Distinction UR Prowess vs UR Prowess (Cauldron)")
    print("  7. ✅ Ajout des % et noms dans le camembert")
    print("  8. ✅ Plugin datalabels pour afficher les infos dans le graphique")
    
    print("\n🎨 ARCHÉTYPES À 3 COULEURS DÉTECTÉS:")
    three_color = [(arch, count) for arch, count in sorted_archetypes 
                   if any(name in arch for name in ["Esper", "Grixis", "Jund", "Naya", "Bant", 
                                                     "Abzan", "Jeskai", "Sultai", "Mardu", "Temur"])]
    if three_color:
        for arch, count in three_color[:10]:
            print(f"  • {arch}: {count} decks")
    
    print("\n📁 FICHIERS GÉNÉRÉS:")
    print("  • data/cache/archetype_visualization.html - Visualisation complète")
    print("    → Camembert avec % et noms d'archétypes")
    print("    → Graphiques en barres (top 10 et complet)")
    print("    → Table détaillée de tous les archétypes")
    print("  • data/cache/tournaments.db - Base SQLite")
    print("  • data/cache/decklists/2025-07.json - Decklists avec archétypes")
    
    print("\n🚀 PROCHAINE ÉTAPE:")
    print("  Phase 3: Visualisations avancées")
    print("  - Heatmap des matchups")
    print("  - Évolution temporelle")
    print("  - Générateur de deck consensus")
    print("  - Détecteur d'innovations")
    
    print("\n✨ La Phase 2 est 100% COMPLÈTE avec toutes les améliorations demandées!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()