#!/usr/bin/env python3
"""
Test script to validate critical paths and fixes.
Runs isolated tests to identify exactly what works and what doesn't.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_module_imports():
    """Test critical module imports."""
    print("\n🔍 Testing Module Imports...")
    
    tests = {
        "ArchetypeEngine": lambda: __import__('src.parsers.archetype_engine', fromlist=['ArchetypeEngine']),
        "BaseScraper": lambda: __import__('src.scrapers.base_scraper', fromlist=['BaseScraper']),
        "CacheManager": lambda: __import__('src.utils.cache_manager', fromlist=['CacheManager']),
        "MetaAnalyzer": lambda: __import__('src.analyzers.meta_analyzer', fromlist=['MetaAnalyzer']),
        "db_pool": lambda: __import__('database.db_pool', fromlist=['get_db_connection']),
        "Settings": lambda: __import__('config.settings', fromlist=['settings']),
    }
    
    results = []
    for name, import_func in tests.items():
        try:
            module = import_func()
            results.append(f"✅ {name} - Import successful")
        except Exception as e:
            results.append(f"❌ {name} - Import failed: {str(e)}")
    
    for result in results:
        print(result)
    
    return all("✅" in r for r in results)

def test_database_connection():
    """Test database connection with schema."""
    print("\n🔍 Testing Database Connection...")
    
    try:
        from database.db_pool import get_db_connection
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Test schema is set correctly
                cursor.execute("SHOW search_path;")
                search_path = cursor.fetchone()[0]
                print(f"✅ DB Connection successful - search_path: {search_path}")
                
                # Test querying a table
                cursor.execute("SELECT COUNT(*) FROM formats;")
                count = cursor.fetchone()[0]
                print(f"✅ Query successful - formats count: {count}")
                
                return True
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_api_startup():
    """Test if API can be imported and configured."""
    print("\n🔍 Testing API Configuration...")
    
    try:
        from src.api.app import app
        from src.api.routes import decks, archetypes, analysis
        
        # Check routes are registered
        routes = [r.path for r in app.routes]
        
        critical_routes = ["/api/health", "/api/decks", "/api/archetypes", "/api/analysis/meta/{format_name}"]
        
        results = []
        for route in critical_routes:
            if any(route in r for r in routes):
                results.append(f"✅ Route {route} - Registered")
            else:
                results.append(f"❌ Route {route} - Not found")
        
        for result in results:
            print(result)
            
        return all("✅" in r for r in results)
        
    except Exception as e:
        print(f"❌ API import failed: {str(e)}")
        return False

def test_pipeline_components():
    """Test pipeline can be initialized."""
    print("\n🔍 Testing Pipeline Components...")
    
    try:
        from scripts.run_pipeline import process_tournaments
        from src.scrapers.mtgo_scraper import MTGOScraper
        from src.scrapers.melee_scraper import MeleeScraper
        from src.parsers.archetype_engine import ArchetypeEngine
        
        # Test instantiation
        engine = ArchetypeEngine()
        print("✅ ArchetypeEngine - Instantiated")
        
        # Test scraper instantiation
        mtgo = MTGOScraper("modern")
        print("✅ MTGOScraper - Instantiated")
        
        melee = MeleeScraper("modern")
        print("✅ MeleeScraper - Instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline component failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test required environment variables."""
    print("\n🔍 Testing Environment Variables...")
    
    try:
        from config.settings import settings
        
        required_vars = {
            "DATABASE_URL": settings.DATABASE_URL,
            "API_KEY": settings.API_KEY,
            "SECRET_KEY": settings.SECRET_KEY,
            "MELEE_EMAIL": settings.MELEE_EMAIL,
            "MELEE_PASSWORD": settings.MELEE_PASSWORD,
        }
        
        results = []
        for var_name, var_value in required_vars.items():
            if var_value and var_value != "":
                results.append(f"✅ {var_name} - Set")
            else:
                results.append(f"❌ {var_name} - Missing or empty")
        
        for result in results:
            print(result)
            
        return all("✅" in r for r in results)
        
    except Exception as e:
        print(f"❌ Settings import failed: {str(e)}")
        return False

def main():
    """Run all tests and summarize results."""
    print("=" * 60)
    print("🚀 MANALYTICS CRITICAL PATH VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Database Connection", test_database_connection),
        ("API Configuration", test_api_startup),
        ("Pipeline Components", test_pipeline_components),
        ("Environment Variables", test_environment_variables),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Unexpected error: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - System ready to start!")
        print("\nNext steps:")
        print("1. docker-compose build api")
        print("2. docker-compose up -d db redis")
        print("3. docker-compose up api")
    else:
        print("❌ SOME TESTS FAILED - Please fix the issues above")
        print("\nDebug tips:")
        print("- Check .env file exists and has all required values")
        print("- Ensure PostgreSQL is running if testing locally")
        print("- Check import paths match the project structure")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())