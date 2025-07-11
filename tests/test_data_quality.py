#!/usr/bin/env python3
"""
Data Quality Tests for Manalytics
Validates the quality and consistency of pipeline outputs
"""

import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_classification_coverage():
    """Vérifie que >85% des decks sont classifiés"""
    print("🧪 Testing classification coverage...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    total_decks = data['metadata']['total_decks']
    unknown_decks = 0
    
    # Count unknown/unclassified decks
    for archetype in data['archetype_performance']:
        if archetype['archetype'].lower() in ['unknown', 'unclassified', 'other']:
            unknown_decks += archetype['deck_count']
    
    classification_rate = (total_decks - unknown_decks) / total_decks * 100
    
    if classification_rate < 85:
        print(f"❌ Classification rate too low: {classification_rate:.1f}%")
        return False
    
    print(f"✅ Classification rate: {classification_rate:.1f}%")
    return True

def test_data_consistency():
    """Vérifie la cohérence des données"""
    print("🧪 Testing data consistency...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    # Test 1: La somme des decks par archétype = total
    sum_decks = sum(a['deck_count'] for a in data['archetype_performance'])
    if sum_decks != data['metadata']['total_decks']:
        print(f"❌ Deck count mismatch: sum={sum_decks}, total={data['metadata']['total_decks']}")
        return False
    
    # Test 2: Win rates entre 0 et 1
    for archetype in data['archetype_performance']:
        win_rate = archetype['win_rate']
        if not (0 <= win_rate <= 1):
            print(f"❌ Invalid win rate for {archetype['archetype']}: {win_rate}")
            return False
    
    # Test 3: Meta shares somment à ~100%
    total_share = sum(a['meta_share'] for a in data['archetype_performance'])
    if not (0.99 <= total_share <= 1.01):
        print(f"❌ Meta shares don't sum to 100%: {total_share:.3f}")
        return False
    
    # Test 4: Counts sont cohérents avec meta_share (tolérance plus large)
    for archetype in data['archetype_performance']:
        expected_share = archetype['deck_count'] / data['metadata']['total_decks']
        actual_share = archetype['meta_share']
        if abs(expected_share - actual_share) > 0.01:  # Tolérance de 1%
            print(f"❌ Meta share inconsistent for {archetype['archetype']}: expected {expected_share:.3f}, got {actual_share:.3f}")
            return False
    
    print("✅ Data consistency checks passed")
    return True

def test_archetype_diversity():
    """Vérifie la diversité des archétypes"""
    print("🧪 Testing archetype diversity...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    archetypes = data['archetype_performance']
    
    # Test minimum number of archetypes
    if len(archetypes) < 2:
        print(f"❌ Too few archetypes: {len(archetypes)}")
        return False
    
    # Test that no single archetype dominates > 60%
    for archetype in archetypes:
        if archetype['meta_share'] > 0.6:
            print(f"❌ Archetype {archetype['archetype']} dominates with {archetype['meta_share']:.1%}")
            return False
    
    # Test archetype names are not empty
    for archetype in archetypes:
        if not archetype['archetype'] or archetype['archetype'].strip() == '':
            print(f"❌ Empty archetype name found")
            return False
    
    print(f"✅ Found {len(archetypes)} diverse archetypes")
    return True

def test_matchup_matrix_validity():
    """Vérifie la matrice de matchups"""
    print("🧪 Testing matchup matrix validity...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    matrix = data.get('matchup_matrix', {})
    
    if not matrix:
        print("⚠️  No matchup matrix found (acceptable for demo)")
        return True
    
    # Test values are between 0 and 1
    for archA in matrix:
        for archB in matrix.get(archA, {}):
            win_rate = matrix[archA][archB]
            if not (0 <= win_rate <= 1):
                print(f"❌ Invalid matchup win rate: {archA} vs {archB} = {win_rate}")
                return False
    
    # Test diagonal values (self-matchups) are around 0.5
    for archetype in matrix:
        if archetype in matrix[archetype]:
            self_rate = matrix[archetype][archetype]
            if abs(self_rate - 0.5) > 0.1:
                print(f"❌ Self-matchup not ~50%: {archetype} vs {archetype} = {self_rate}")
                return False
    
    print("✅ Matchup matrix validated")
    return True

def test_temporal_trends():
    """Vérifie les tendances temporelles"""
    print("🧪 Testing temporal trends...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    trends = data.get('temporal_trends', {})
    
    if not trends:
        print("⚠️  No temporal trends found (acceptable for demo)")
        return True
    
    # Test that trend data has proper structure
    for trend_key, trend_data in trends.items():
        if trend_key == 'trend_summary':
            # Handle trend_summary structure
            if not isinstance(trend_data, list):
                print(f"❌ Invalid trend summary data")
                return False
            
            for point in trend_data:
                if not all(key in point for key in ['archetype', 'avg_meta_share']):
                    print(f"❌ Invalid trend summary point: {point}")
                    return False
        else:
            # Handle other trend structures
            if not isinstance(trend_data, list):
                print(f"❌ Invalid trend data for {trend_key}")
                return False
            
            for point in trend_data:
                if not all(key in point for key in ['date', 'meta_share']):
                    print(f"❌ Invalid trend point for {trend_key}: {point}")
                    return False
    
    print("✅ Temporal trends validated")
    return True

def test_source_attribution():
    """Vérifie l'attribution des sources"""
    print("🧪 Testing source attribution...")
    
    output_file = 'data/output/metagame_Modern_demo.json'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    with open(output_file) as f:
        data = json.load(f)
    
    metadata = data['metadata']
    
    # Test sources are documented
    if 'sources' not in metadata:
        print("❌ No sources documented in metadata")
        return False
    
    sources = metadata['sources']
    if not sources or len(sources) == 0:
        print("❌ Empty sources list")
        return False
    
    # Test each source has required fields
    for source in sources:
        if isinstance(source, str):
            # Simple string sources are acceptable
            continue
        elif isinstance(source, dict):
            if not all(key in source for key in ['name', 'tournaments']):
                print(f"❌ Invalid source structure: {source}")
                return False
        else:
            print(f"❌ Invalid source type: {source}")
            return False
    
    print(f"✅ Found {len(sources)} documented sources")
    return True

def run_all_data_quality_tests():
    """Execute all data quality tests"""
    print("🔍 Running Data Quality Tests")
    print("=" * 50)
    
    tests = [
        test_classification_coverage,
        test_data_consistency,
        test_archetype_diversity,
        test_matchup_matrix_validity,
        test_temporal_trends,
        test_source_attribution
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
        print("✅ All data quality tests PASSED!")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_data_quality_tests()
    sys.exit(0 if success else 1) 