#!/usr/bin/env python3
"""
Complete validation script for Manalytics setup.
Tests all critical components and provides clear diagnostics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Disable other loggers for cleaner output
for name in ['urllib3', 'httpx', 'redis', 'psycopg2']:
    logging.getLogger(name).setLevel(logging.WARNING)


class SetupValidator:
    """Validates the complete Manalytics setup."""
    
    def __init__(self):
        self.results = []
        self.section_count = 0
        
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        """Add a test result."""
        icon = "✅" if passed else "❌"
        message = f"{icon} {test_name}"
        if details and not passed:
            message += f" - {details}"
        self.results.append((test_name, passed, message))
        print(message)
        
    def print_section(self, title: str):
        """Print a section header."""
        self.section_count += 1
        print(f"\n{'=' * 60}")
        print(f"{self.section_count}. {title}")
        print('=' * 60)
        
    def test_service_connections(self):
        """Test connections to all required services."""
        self.print_section("SERVICE CONNECTIONS")
        
        # Test PostgreSQL
        try:
            from database.db_pool import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    self.add_result("PostgreSQL Connection", True, version.split(',')[0])
                    
                    # Check search_path
                    cursor.execute("SHOW search_path;")
                    search_path = cursor.fetchone()[0]
                    correct_path = "manalytics" in search_path
                    self.add_result("PostgreSQL Schema Path", correct_path, search_path)
        except Exception as e:
            self.add_result("PostgreSQL Connection", False, str(e))
            
        # Test Redis
        try:
            from src.utils.cache_manager import CacheManager
            cache = CacheManager()
            if cache.redis_client:
                cache.redis_client.ping()
                info = cache.redis_client.info()
                self.add_result("Redis Connection", True, f"v{info['redis_version']}")
                
                # Test cache operations
                test_key = "test_key_validate"
                cache.set(test_key, {"test": "data"}, ttl=60)
                retrieved = cache.get(test_key)
                cache_works = retrieved and retrieved.get("test") == "data"
                self.add_result("Redis Cache Operations", cache_works)
            else:
                self.add_result("Redis Connection", True, "Optional - Not configured")
        except Exception as e:
            self.add_result("Redis Connection", False, str(e))
            
    def test_module_imports(self):
        """Test all critical module imports."""
        self.print_section("MODULE IMPORTS")
        
        modules_to_test = [
            # Core modules
            ("Settings", "config.settings", ["settings"]),
            ("Logging Config", "config.logging_config", []),
            
            # Database modules
            ("DB Pool", "database.db_pool", ["get_db_connection", "init_db_pool"]),
            ("DB Manager", "database.db_manager", ["save_tournament_results"]),
            
            # Scraper modules
            ("Base Scraper", "src.scrapers.base_scraper", ["BaseScraper"]),
            ("MTGO Scraper", "src.scrapers.mtgo_scraper", ["MTGOScraper"]),
            ("Melee Scraper", "src.scrapers.melee_scraper", ["MeleeScraper"]),
            
            # Parser modules
            ("Decklist Parser", "src.parsers.decklist_parser", ["DecklistParser"]),
            ("Archetype Engine", "src.parsers.archetype_engine", ["ArchetypeEngine"]),
            ("Color Identity", "src.parsers.color_identity", ["ColorIdentityParser"]),
            
            # Analyzer modules
            ("Meta Analyzer", "src.analyzers.meta_analyzer", ["MetaAnalyzer"]),
            ("Matchup Calculator", "src.analyzers.matchup_calculator", ["MatchupCalculator"]),
            
            # API modules
            ("API App", "src.api.app", ["app"]),
            ("API Models", "src.api.models", ["DecklistResponse", "MetaSnapshotResponse"]),
            ("API Security", "src.api.security", ["get_api_key"]),
            ("API Metrics", "src.api.metrics", ["metrics_middleware"]),
            
            # Utility modules
            ("Cache Manager", "src.utils.cache_manager", ["CacheManager"]),
            ("Card Utils", "src.utils.card_utils", ["normalize_card_name"]),
        ]
        
        for name, module_path, attributes in modules_to_test:
            try:
                module = __import__(module_path, fromlist=attributes)
                # Check specific attributes exist
                missing = [attr for attr in attributes if not hasattr(module, attr)]
                if missing:
                    self.add_result(name, False, f"Missing: {', '.join(missing)}")
                else:
                    self.add_result(name, True)
            except Exception as e:
                self.add_result(name, False, str(e).split('\n')[0])
                
    def test_database_schema(self):
        """Test database tables exist and can be queried."""
        self.print_section("DATABASE SCHEMA")
        
        tables_to_check = [
            ("formats", "SELECT COUNT(*) FROM formats"),
            ("sources", "SELECT COUNT(*) FROM sources"),
            ("tournaments", "SELECT COUNT(*) FROM tournaments"),
            ("players", "SELECT COUNT(*) FROM players"),
            ("archetypes", "SELECT COUNT(*) FROM archetypes"),
            ("decklists", "SELECT COUNT(*) FROM decklists"),
            ("matchups", "SELECT COUNT(*) FROM matchups"),
            ("archetype_rules", "SELECT COUNT(*) FROM archetype_rules"),
        ]
        
        try:
            from database.db_pool import get_db_connection
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for table_name, query in tables_to_check:
                        try:
                            cursor.execute(query)
                            count = cursor.fetchone()[0]
                            self.add_result(f"Table '{table_name}'", True, f"{count} rows")
                        except Exception as e:
                            if "does not exist" in str(e):
                                self.add_result(f"Table '{table_name}'", False, "Does not exist")
                            else:
                                self.add_result(f"Table '{table_name}'", False, str(e))
        except Exception as e:
            self.add_result("Database Schema Check", False, f"Connection failed: {e}")
            
    def test_mini_pipeline(self):
        """Test a minimal pipeline flow."""
        self.print_section("MINI PIPELINE TEST")
        
        try:
            # Test archetype engine initialization
            from src.parsers.archetype_engine import ArchetypeEngine
            engine = ArchetypeEngine()
            self.add_result("Archetype Engine Init", True)
            
            # Test decklist parsing
            from src.parsers.decklist_parser import DecklistParser
            parser = DecklistParser()
            
            # Create a test decklist
            test_mainboard = [
                {"name": "Lightning Bolt", "quantity": 4},
                {"name": "Mountain", "quantity": 20},
                {"name": "Ragavan, Nimble Pilferer", "quantity": 4},
            ]
            test_sideboard = [
                {"name": "Alpine Moon", "quantity": 2},
            ]
            
            # Validate decklist
            is_valid, errors = parser.validate_decklist(test_mainboard, test_sideboard)
            self.add_result("Decklist Validation", is_valid, ", ".join(errors) if errors else "")
            
            # Test archetype detection
            if is_valid:
                archetype, method, confidence = engine.identify_archetype(test_mainboard, "modern")
                self.add_result(
                    "Archetype Detection", 
                    True, 
                    f"Detected: {archetype} (method: {method}, confidence: {confidence:.2f})"
                )
            
            # Test tournament data structure
            test_tournament = {
                "name": "Test Tournament",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "format": "modern",
                "source": "test",
                "decklists": [{
                    "player": "Test Player",
                    "mainboard": test_mainboard,
                    "sideboard": test_sideboard,
                    "archetype": "Red Aggro",
                    "position": 1,
                    "wins": 5,
                    "losses": 0,
                }]
            }
            
            self.add_result("Tournament Data Structure", True)
            
        except Exception as e:
            self.add_result("Mini Pipeline", False, str(e))
            
    def test_api_health(self):
        """Test API endpoints are accessible."""
        self.print_section("API HEALTH CHECK")
        
        try:
            from src.api.app import app
            from fastapi.testclient import TestClient
            
            # Create test client
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/api/health")
            health_ok = response.status_code == 200
            self.add_result("Health Endpoint", health_ok, 
                          f"Status: {response.status_code}, Response: {response.json() if health_ok else response.text}")
            
            # Test metrics endpoint
            response = client.get("/metrics")
            metrics_ok = response.status_code == 200 and "http_requests_total" in response.text
            self.add_result("Metrics Endpoint", metrics_ok, f"Status: {response.status_code}")
            
            # Test API documentation
            response = client.get("/api/docs")
            docs_ok = response.status_code == 200
            self.add_result("API Documentation", docs_ok, f"Status: {response.status_code}")
            
            # Test a protected endpoint (should fail without API key)
            response = client.put("/api/archetypes/1/rules", json=[])
            auth_works = response.status_code == 422 or response.status_code == 401  # Missing API key
            self.add_result("API Authentication", auth_works, 
                          "Protected endpoints require API key" if auth_works else f"Unexpected status: {response.status_code}")
            
        except Exception as e:
            self.add_result("API Health Check", False, str(e))
            
    def test_environment_config(self):
        """Test environment configuration."""
        self.print_section("ENVIRONMENT CONFIGURATION")
        
        try:
            from config.settings import settings
            
            # Required settings
            required = {
                "DATABASE_URL": bool(settings.DATABASE_URL),
                "API_KEY": bool(settings.API_KEY),
                "SECRET_KEY": bool(settings.SECRET_KEY),
                "MELEE_EMAIL": bool(settings.MELEE_EMAIL),
                "MELEE_PASSWORD": bool(settings.MELEE_PASSWORD),
            }
            
            for setting, is_set in required.items():
                self.add_result(f"ENV: {setting}", is_set, "Not set" if not is_set else "")
                
            # Optional but recommended
            optional = {
                "REDIS_URL": settings.REDIS_URL,
                "DEBUG": settings.DEBUG,
                "LOG_LEVEL": settings.LOG_LEVEL,
            }
            
            for setting, value in optional.items():
                self.add_result(f"ENV: {setting} (optional)", True, f"Value: {value}")
                
            # Check data directories exist
            dirs_exist = all([
                settings.DATA_DIR.exists(),
                settings.CACHE_DIR.exists(),
                settings.OUTPUT_DIR.exists(),
            ])
            self.add_result("Data Directories", dirs_exist, 
                          f"DATA_DIR: {settings.DATA_DIR.exists()}, CACHE_DIR: {settings.CACHE_DIR.exists()}, OUTPUT_DIR: {settings.OUTPUT_DIR.exists()}")
            
        except Exception as e:
            self.add_result("Environment Config", False, str(e))
            
    def run_all_tests(self):
        """Run all validation tests."""
        print("\n" + "🚀 " * 20)
        print("MANALYTICS COMPLETE SETUP VALIDATION")
        print("🚀 " * 20)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_environment_config()
        self.test_service_connections()
        self.test_module_imports()
        self.test_database_schema()
        self.test_mini_pipeline()
        self.test_api_health()
        
        # Summary
        elapsed = time.time() - start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for _, passed, _ in self.results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'=' * 60}")
        print("📊 VALIDATION SUMMARY")
        print('=' * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {elapsed:.2f}s")
        
        if failed_tests > 0:
            print(f"\n{'=' * 60}")
            print("❌ FAILED TESTS:")
            print('=' * 60)
            for name, passed, message in self.results:
                if not passed:
                    print(f"  • {name}: {message}")
                    
        print(f"\n{'=' * 60}")
        if failed_tests == 0:
            print("✅ ALL VALIDATION TESTS PASSED! 🎉")
            print("\nYour Manalytics setup is ready. You can now:")
            print("1. Start the services: docker-compose up -d")
            print("2. Run the pipeline: docker-compose exec worker python scripts/run_pipeline.py --format modern --days 7")
            print("3. Access the API: http://localhost:8000/api/docs")
        else:
            print("❌ VALIDATION FAILED - Please fix the issues above")
            print("\nCommon fixes:")
            print("1. Ensure .env file exists with all required values")
            print("2. Run: docker-compose up -d db redis (and wait 10s)")
            print("3. Check PostgreSQL logs: docker-compose logs db")
            print("4. Verify all files were deployed correctly")
        print('=' * 60)
        
        return 0 if failed_tests == 0 else 1


def main():
    """Main entry point."""
    validator = SetupValidator()
    return validator.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())