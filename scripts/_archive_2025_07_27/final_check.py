#!/usr/bin/env python3
"""
Final check of archetype names and issues.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.utils.color_names import format_archetype_name


def main():
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    print("\n" + "="*80)
    print("🔍 VÉRIFICATION FINALE DES ARCHÉTYPES")
    print("="*80)
    
    # Extract archetypes
    archetypes = []
    for arch, data in meta_snapshot['archetypes'].items():
        if isinstance(data, dict):
            count = data['count']
        else:
            count = data
        archetypes.append((arch, count))
    
    # Sort by count
    archetypes.sort(key=lambda x: x[1], reverse=True)
    
    print("\n📊 ARCHÉTYPES À 3 COULEURS (problème de duplication):")
    print("-" * 60)
    for arch, count in archetypes:
        if arch and " " in arch:
            parts = arch.split()
            # Detect duplicated color codes
            if len(parts) >= 2 and parts[0] == parts[1] and len(parts[0]) == 3:
                fixed_name = format_archetype_name(arch)
                print(f"❌ {arch:<35} → {fixed_name:<35} ({count} decks)")
    
    print("\n✅ ARCHÉTYPES À 3 COULEURS CORRECTS (après format_archetype_name):")
    print("-" * 60)
    three_color_fixed = []
    for arch, count in archetypes:
        if arch:
            fixed = format_archetype_name(arch)
            if any(name in fixed for name in ["Esper", "Grixis", "Jund", "Naya", "Bant", 
                                                "Abzan", "Jeskai", "Sultai", "Mardu", "Temur"]):
                three_color_fixed.append((fixed, count))
    
    three_color_fixed.sort(key=lambda x: x[1], reverse=True)
    for name, count in three_color_fixed[:10]:
        print(f"  {name:<35} ({count} decks)")
    
    print("\n🎯 ARCHÉTYPES UR (Prowess vs Cauldron):")
    print("-" * 60)
    ur_archetypes = [(arch, count) for arch, count in archetypes if arch and arch.startswith("UR")]
    for arch, count in ur_archetypes:
        fixed = format_archetype_name(arch)
        print(f"  {arch:<35} → {fixed:<35} ({count} decks)")
    
    print("\n💡 ARCHÉTYPES 4 COULEURS:")
    print("-" * 60)
    four_color = [(arch, count) for arch, count in archetypes if arch and "WUBG" in arch]
    for arch, count in four_color:
        fixed = format_archetype_name(arch)
        print(f"  {arch:<35} → {fixed:<35} ({count} decks)")
    
    print("\n📝 RÉSUMÉ DES CORRECTIONS:")
    print("  1. ✅ Noms de guildes: UR → Izzet, UB → Dimir, etc.")
    print("  2. ✅ 4c au lieu de 'Four Color'")
    print("  3. ❌ Duplication des codes couleur (WRG WRG Yuna) - nécessite reprocessing")
    print("  4. ✅ UR Prowess et UR Prowess (Cauldron) sont bien 2 archétypes différents")
    print("\n⚠️  Pour corriger la duplication, il faut reprocesser toutes les données.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()