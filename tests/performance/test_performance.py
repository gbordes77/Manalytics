#!/usr/bin/env python3
"""
Performance Tests for Manalytics
Benchmarks scraping and classification performance
"""

import time
import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, memory monitoring disabled")

def test_demo_execution_performance():
    """Mesure les performances d'exécution du demo"""
    print("🧪 Testing demo execution performance...")
    
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0
    
    # Import and run demo components
    try:
        from demo import create_sample_tournament_data
        
        # Create demo data
        demo_data = create_sample_tournament_data()
        
        # Simple validation
        if not demo_data or 'tournament' not in demo_data:
            print("❌ Invalid demo data structure")
            return False
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory if PSUTIL_AVAILABLE else 0
        
        print(f"✅ Demo executed in {duration:.2f}s")
        if PSUTIL_AVAILABLE:
            print(f"✅ Memory usage: {memory_used:.1f} MB")
        
        # Performance assertions
        if duration > 30:  # 30 seconds for demo should be enough
            print(f"⚠️  Demo execution slow (>{30}s): {duration:.2f}s")
            return False
        
        if PSUTIL_AVAILABLE and memory_used > 1000:  # 1GB limit
            print(f"⚠️  High memory usage (>1GB): {memory_used:.1f} MB")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")
        return False

def test_classification_performance():
    """Benchmark de la classification"""
    print("🧪 Testing classification performance...")
    
    try:
        from src.python.classifier.archetype_engine import ArchetypeEngine
        
        # Create test decks
        test_decks = [
            {
                'player': f'Player_{i}',
                'mainboard': [
                    {'name': 'Lightning Bolt', 'count': 4},
                    {'name': 'Monastery Swiftspear', 'count': 4},
                    {'name': 'Mountain', 'count': 20}
                ],
                'sideboard': []
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Initialize engine
        engine = ArchetypeEngine('./MTGOFormatData')
        
        # Classify decks
        classified_count = 0
        for deck in test_decks:
            try:
                result = engine.classify_deck(deck, 'modern')
                if result:
                    classified_count += 1
            except Exception as e:
                print(f"⚠️  Classification error: {e}")
        
        duration = time.time() - start_time
        rate = len(test_decks) / duration if duration > 0 else 0
        
        print(f"✅ Classified {classified_count}/{len(test_decks)} decks in {duration:.2f}s ({rate:.0f} decks/sec)")
        
        # Performance assertions
        if rate < 10:  # At least 10 decks/sec
            print(f"⚠️  Classification too slow (<10 decks/sec): {rate:.1f}")
            return False
        
        if classified_count < len(test_decks) * 0.8:  # At least 80% success rate
            print(f"⚠️  Low classification success rate: {classified_count}/{len(test_decks)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Classification performance test failed: {e}")
        return False

def test_scraper_initialization_performance():
    """Test les performances d'initialisation des scrapers"""
    print("🧪 Testing scraper initialization performance...")
    
    try:
        from src.python.scraper.base_scraper import BaseScraper
        from src.python.scraper.mtgo_scraper import MTGOScraper
        from src.python.scraper.melee_scraper import MeleeScraper
        from src.python.scraper.topdeck_scraper import TopdeckScraper
        
        scrapers = [
            ('MTGOScraper', MTGOScraper),
            ('MeleeScraper', MeleeScraper),
            ('TopdeckScraper', TopdeckScraper)
        ]
        
        for name, scraper_class in scrapers:
            start_time = time.time()
            
            try:
                # Provide config for scrapers that need it
                config = {}
                scraper = scraper_class('data/test', config)
                duration = time.time() - start_time
                
                print(f"✅ {name} initialized in {duration:.3f}s")
                
                if duration > 5:  # 5 seconds max for initialization
                    print(f"⚠️  {name} initialization slow (>5s): {duration:.2f}s")
                    return False
                    
            except Exception as e:
                print(f"❌ {name} initialization failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper initialization test failed: {e}")
        return False

def test_json_processing_performance():
    """Test les performances de traitement JSON"""
    print("🧪 Testing JSON processing performance...")
    
    try:
        # Create large test data
        large_tournament = {
            'id': 'perf_test',
            'name': 'Performance Test Tournament',
            'date': '2025-01-15',
            'format': 'Modern',
            'decks': []
        }
        
        # Generate 1000 decks
        for i in range(1000):
            deck = {
                'player': f'Player_{i}',
                'rank': i + 1,
                'mainboard': [
                    {'name': f'Card_{j}', 'count': j % 4 + 1}
                    for j in range(60)
                ],
                'sideboard': [
                    {'name': f'SB_Card_{j}', 'count': j % 4 + 1}
                    for j in range(15)
                ]
            }
            large_tournament['decks'].append(deck)
        
        # Test JSON serialization
        start_time = time.time()
        json_str = json.dumps(large_tournament)
        serialize_time = time.time() - start_time
        
        # Test JSON deserialization
        start_time = time.time()
        parsed_data = json.loads(json_str)
        deserialize_time = time.time() - start_time
        
        print(f"✅ JSON serialize: {serialize_time:.3f}s for {len(json_str)} chars")
        print(f"✅ JSON deserialize: {deserialize_time:.3f}s")
        
        # Performance assertions
        if serialize_time > 2:  # 2 seconds max for serialization
            print(f"⚠️  JSON serialization slow (>2s): {serialize_time:.2f}s")
            return False
        
        if deserialize_time > 2:  # 2 seconds max for deserialization
            print(f"⚠️  JSON deserialization slow (>2s): {deserialize_time:.2f}s")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ JSON processing test failed: {e}")
        return False

def test_memory_usage_stability():
    """Test la stabilité de l'utilisation mémoire"""
    print("🧪 Testing memory usage stability...")
    
    if not PSUTIL_AVAILABLE:
        print("⚠️  psutil not available, skipping memory test")
        return True
    
    try:
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Simulate repeated operations
        for i in range(10):
            # Create and destroy objects
            data = {
                'test': [{'item': j} for j in range(1000)]
            }
            json_str = json.dumps(data)
            parsed = json.loads(json_str)
            del data, json_str, parsed
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"✅ Memory: {initial_memory:.1f} MB → {final_memory:.1f} MB (growth: {memory_growth:.1f} MB)")
        
        # Memory growth should be reasonable
        if memory_growth > 100:  # 100 MB max growth
            print(f"⚠️  Excessive memory growth: {memory_growth:.1f} MB")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Memory stability test failed: {e}")
        return False

def run_all_performance_tests():
    """Execute all performance tests"""
    print("⚡ Running Performance Tests")
    print("=" * 50)
    
    tests = [
        test_demo_execution_performance,
        test_classification_performance,
        test_scraper_initialization_performance,
        test_json_processing_performance,
        test_memory_usage_stability
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
        print("✅ All performance tests PASSED!")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_performance_tests()
    sys.exit(0 if success else 1) 