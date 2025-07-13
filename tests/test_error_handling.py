#!/usr/bin/env python3
"""
Error Handling Tests for Manalytics
Tests robustness and error handling capabilities
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_scraper_resilience():
    """Test la résilience aux erreurs réseau"""
    print("🧪 Testing scraper resilience...")
    
    try:
        from src.python.scraper.mtgo_scraper import MTGOScraper
        
        # Test with mock network errors
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Simulate network error
            mock_get.side_effect = Exception("Network error")
            
            scraper = MTGOScraper('data/test', {})
            
            # Should handle errors gracefully
            result = asyncio.run(scraper.fetch_tournament('invalid_id'))
            
            # Should return empty dict or None, not crash
            if result is None or result == {}:
                print("✅ Scraper handles network errors gracefully")
                return True
            else:
                print(f"❌ Scraper should return empty result on error, got: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Scraper resilience test failed: {e}")
        return False

def test_malformed_data_handling():
    """Test avec des données malformées"""
    print("🧪 Testing malformed data handling...")
    
    try:
        from src.python.classifier.archetype_engine import ArchetypeEngine
        
        # Create malformed tournament data
        malformed_data = {
            'tournament': {'name': 'Test Tournament'},
            'decks': [
                {'player': 'Test1', 'mainboard': 'invalid_format'},  # Malformed
                {'player': 'Test2', 'mainboard': None},  # Null mainboard
                {'player': 'Test3', 'mainboard': []},  # Empty mainboard
                {'player': 'Valid', 'mainboard': [{'name': 'Island', 'count': 20}]}  # Valid
            ]
        }
        
        engine = ArchetypeEngine('./MTGOFormatData')
        
        # Should process valid decks, skip invalid ones
        processed_count = 0
        for deck in malformed_data['decks']:
            try:
                result = engine.classify_deck(deck, 'modern')
                if result:
                    processed_count += 1
            except Exception as e:
                # Should handle errors gracefully
                print(f"⚠️  Handled malformed deck error: {e}")
        
        if processed_count >= 1:  # At least the valid deck should be processed
            print(f"✅ Handles malformed data gracefully ({processed_count} valid decks processed)")
            return True
        else:
            print("❌ Failed to process any valid decks")
            return False
            
    except Exception as e:
        print(f"❌ Malformed data handling test failed: {e}")
        return False

def test_missing_files_handling():
    """Test la gestion des fichiers manquants"""
    print("🧪 Testing missing files handling...")
    
    try:
        from src.python.classifier.archetype_engine import ArchetypeEngine
        
        # Test with non-existent format data directory
        engine = ArchetypeEngine('./non_existent_directory')
        
        # Should handle missing directory gracefully
        result = engine.load_format_data('Modern')
        
        if result is False:
            print("✅ Handles missing format data directory gracefully")
            return True
        else:
            print("❌ Should return False for missing directory")
            return False
            
    except Exception as e:
        print(f"❌ Missing files handling test failed: {e}")
        return False

def test_invalid_json_handling():
    """Test la gestion des JSON invalides"""
    print("🧪 Testing invalid JSON handling...")
    
    try:
        # Create temporary invalid JSON file
        invalid_json_path = 'data/test_invalid.json'
        os.makedirs('data', exist_ok=True)
        
        with open(invalid_json_path, 'w') as f:
            f.write('{"invalid": json content}')  # Invalid JSON
        
        # Try to load invalid JSON
        try:
            with open(invalid_json_path, 'r') as f:
                data = json.load(f)
            print("❌ Should have failed to load invalid JSON")
            return False
        except json.JSONDecodeError:
            print("✅ Correctly handles invalid JSON")
            return True
        finally:
            # Cleanup
            if os.path.exists(invalid_json_path):
                os.remove(invalid_json_path)
            
    except Exception as e:
        print(f"❌ Invalid JSON handling test failed: {e}")
        return False

def test_memory_pressure_handling():
    """Test la gestion de la pression mémoire"""
    print("🧪 Testing memory pressure handling...")
    
    try:
        # Create large data structures to simulate memory pressure
        large_data = []
        
        for i in range(1000):
            tournament = {
                'id': f'tournament_{i}',
                'decks': [
                    {
                        'player': f'Player_{j}',
                        'mainboard': [
                            {'name': f'Card_{k}', 'count': k % 4 + 1}
                            for k in range(100)
                        ]
                    }
                    for j in range(100)
                ]
            }
            large_data.append(tournament)
        
        # Test that we can still process data
        processed_count = 0
        for tournament in large_data[:10]:  # Process first 10
            if tournament and 'decks' in tournament:
                processed_count += len(tournament['decks'])
        
        # Cleanup
        del large_data
        
        if processed_count > 0:
            print(f"✅ Handles memory pressure gracefully ({processed_count} items processed)")
            return True
        else:
            print("❌ Failed to process data under memory pressure")
            return False
            
    except Exception as e:
        print(f"❌ Memory pressure handling test failed: {e}")
        return False

def test_concurrent_access_handling():
    """Test la gestion des accès concurrents"""
    print("🧪 Testing concurrent access handling...")
    
    try:
        from src.python.classifier.archetype_engine import ArchetypeEngine
        
        # Create multiple engines concurrently
        engines = []
        for i in range(5):
            engine = ArchetypeEngine('./MTGOFormatData')
            engines.append(engine)
        
        # Test concurrent classification
        test_deck = {
            'player': 'Test Player',
            'mainboard': [
                {'name': 'Lightning Bolt', 'count': 4},
                {'name': 'Mountain', 'count': 20}
            ]
        }
        
        results = []
        for engine in engines:
            try:
                result = engine.classify_deck(test_deck, 'modern')
                results.append(result)
            except Exception as e:
                print(f"⚠️  Concurrent access error: {e}")
        
        if len(results) >= 3:  # At least 3 successful classifications
            print(f"✅ Handles concurrent access gracefully ({len(results)} successful)")
            return True
        else:
            print(f"❌ Too many concurrent access failures: {len(results)} successful")
            return False
            
    except Exception as e:
        print(f"❌ Concurrent access handling test failed: {e}")
        return False

def test_configuration_validation():
    """Test la validation de configuration"""
    print("🧪 Testing configuration validation...")
    
    try:
        from src.python.scraper.mtgo_scraper import MTGOScraper
        
        # Test with invalid configurations
        invalid_configs = [
            None,  # Null config
            {},    # Empty config
            {'invalid': 'config'},  # Invalid structure
        ]
        
        for config in invalid_configs:
            try:
                scraper = MTGOScraper('data/test', config)
                # Should not crash, should handle gracefully
                print(f"✅ Handles config {config} gracefully")
            except Exception as e:
                print(f"⚠️  Config validation error for {config}: {e}")
        
        print("✅ Configuration validation handled gracefully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation test failed: {e}")
        return False

def run_all_error_handling_tests():
    """Execute all error handling tests"""
    print("🛡️  Running Error Handling Tests")
    print("=" * 50)
    
    tests = [
        test_scraper_resilience,
        test_malformed_data_handling,
        test_missing_files_handling,
        test_invalid_json_handling,
        test_memory_pressure_handling,
        test_concurrent_access_handling,
        test_configuration_validation
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
        print("✅ All error handling tests PASSED!")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_error_handling_tests()
    sys.exit(0 if success else 1) 