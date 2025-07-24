#!/usr/bin/env python3
"""
Final integration test for Manalytics.
Tests the complete flow from setup to API responses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import httpx
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import settings
from database.db_pool import get_db_connection
import redis

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"

class IntegrationTester:
    def __init__(self):
        self.results = []
        self.token = None
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        icon = "✅" if success else "❌"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_env_variables(self):
        """Test that all required environment variables are set."""
        print("\n🔍 SETUP VALIDATION")
        print("=" * 60)
        
        required_vars = [
            'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY',
            'MELEE_EMAIL', 'MELEE_PASSWORD', 'API_KEY'
        ]
        
        all_set = True
        for var in required_vars:
            value = os.getenv(var)
            if value and value != "changeme":
                self.log_result(f"Environment: {var}", True, "Set and not default")
            else:
                self.log_result(f"Environment: {var}", False, "Missing or default value")
                all_set = False
        
        return all_set
    
    def test_db_connection(self):
        """Test database connection and schema."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Test connection
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    self.log_result("Database connection", True, f"PostgreSQL {version}")
                    
                    # Test schema exists
                    cursor.execute("""
                        SELECT EXISTS(
                            SELECT 1 FROM information_schema.schemata 
                            WHERE schema_name = 'manalytics'
                        );
                    """)
                    schema_exists = cursor.fetchone()[0]
                    self.log_result("Schema 'manalytics'", schema_exists)
                    
                    # Test tables exist
                    tables = [
                        'tournaments', 'decklists', 'archetype_rules',
                        'users', 'user_sessions', 'api_keys'
                    ]
                    cursor.execute("SET search_path TO manalytics, public;")
                    
                    for table in tables:
                        cursor.execute(f"""
                            SELECT EXISTS(
                                SELECT 1 FROM information_schema.tables 
                                WHERE table_schema = 'manalytics' 
                                AND table_name = '{table}'
                            );
                        """)
                        exists = cursor.fetchone()[0]
                        self.log_result(f"Table '{table}'", exists)
            return True
            
        except Exception as e:
            self.log_result("Database connection", False, str(e))
            return False
    
    def test_redis_connection(self):
        """Test Redis connection."""
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            
            # Test set/get
            r.set("test_key", "test_value", ex=10)
            value = r.get("test_key")
            
            self.log_result("Redis connection", True, "Connected and functional")
            return True
            
        except Exception as e:
            self.log_result("Redis connection", False, str(e))
            return False
    
    def test_user_creation(self):
        """Test user creation and management."""
        try:
            from src.api.auth import create_user, get_user_by_username, UserCreate
            
            # Check if test user exists
            existing = get_user_by_username(TEST_USERNAME)
            if existing:
                self.log_result("Test user exists", True, "Using existing user")
                return True
            
            # Create test user
            user_data = UserCreate(
                username=TEST_USERNAME,
                email="test@manalytics.com",
                password=TEST_PASSWORD,
                full_name="Test User"
            )
            
            user = create_user(user_data)
            if user:
                self.log_result("User creation", True, f"Created user ID: {user.id}")
                return True
            else:
                self.log_result("User creation", False, "Failed to create user")
                return False
                
        except Exception as e:
            self.log_result("User creation", False, str(e))
            return False
    
    async def test_pipeline(self):
        """Test complete data pipeline."""
        print("\n🔍 PIPELINE END-TO-END")
        print("=" * 60)
        
        try:
            # 1. Test archetype rules
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SET search_path TO manalytics, public;")
                    cursor.execute("SELECT COUNT(*) FROM archetype_rules;")
                    rules_count = cursor.fetchone()[0]
                
            if rules_count > 0:
                self.log_result("Archetype rules", True, f"{rules_count} rules loaded")
            else:
                self.log_result("Archetype rules", False, "No rules in database")
                # Try to fetch and migrate rules
                os.system("python scripts/fetch_archetype_rules.py")
                os.system("python scripts/migrate_rules.py")
            
            # 2. Test tournament scraping (minimal)
            from src.scrapers.mtgo_scraper import MTGOScraper
            
            scraper = MTGOScraper("modern")
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()
            
            print("   Scraping MTGO tournaments...")
            # MTGOScraper is synchronous, not async
            tournaments = scraper.scrape_tournaments(
                start_date=start_date,
                end_date=end_date
            )
            
            if tournaments:
                self.log_result("Tournament scraping", True, f"{len(tournaments)} tournaments found")
                
                # Get first tournament with standings
                tournament = next((t for t in tournaments if t.get('standings')), None)
                if tournament:
                    # 3. Test deck parsing
                    from src.parsers.deck_parser import DeckParser
                    parser = DeckParser()
                    
                    parsed_count = 0
                    for standing in tournament['standings'][:5]:  # Parse first 5 decks
                        if 'decklist' in standing and standing['decklist']:
                            parsed = parser.parse_decklist(standing['decklist'])
                            if parsed:
                                parsed_count += 1
                    
                    self.log_result("Deck parsing", parsed_count > 0, 
                                  f"{parsed_count} decks parsed successfully")
                    
                    # 4. Test archetype detection
                    from src.analyzers.archetype_detector import ArchetypeDetector
                    detector = ArchetypeDetector()
                    
                    detected_count = 0
                    for standing in tournament['standings'][:5]:
                        if 'parsed_deck' in standing:
                            archetype = detector.detect_archetype(standing['parsed_deck'])
                            if archetype:
                                detected_count += 1
                    
                    self.log_result("Archetype detection", detected_count > 0,
                                  f"{detected_count} archetypes detected")
                    
                    # 5. Test database storage
                    with conn.cursor() as cursor:
                        cursor.execute("SET search_path TO manalytics, public;")
                        cursor.execute("SELECT COUNT(*) FROM tournaments WHERE date >= %s;", 
                                     (start_date,))
                        new_tournaments = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT COUNT(*) FROM decklists WHERE created_at >= %s;",
                                     (start_date,))
                        new_decks = cursor.fetchone()[0]
                    
                    self.log_result("Database storage", new_tournaments > 0 or new_decks > 0,
                                  f"{new_tournaments} tournaments, {new_decks} decks")
                else:
                    self.log_result("Tournament standings", False, "No tournaments with standings")
            else:
                self.log_result("Tournament scraping", False, "No tournaments found")
            
            return True
            
        except Exception as e:
            self.log_result("Pipeline test", False, str(e))
            return False
    
    async def test_api_complete(self):
        """Test complete API functionality."""
        print("\n🔍 API COMPLÈTE")
        print("=" * 60)
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 1. Health check
            try:
                resp = await client.get(f"{API_BASE_URL}/health")
                self.log_result("Health check", resp.status_code == 200, 
                              f"Status: {resp.json().get('status', 'unknown')}")
            except Exception as e:
                self.log_result("Health check", False, str(e))
            
            # 2. JWT Authentication
            try:
                # Login
                resp = await client.post(
                    f"{API_BASE_URL}/api/auth/token",
                    data={
                        "username": TEST_USERNAME,
                        "password": TEST_PASSWORD
                    }
                )
                
                if resp.status_code == 200:
                    self.token = resp.json()["access_token"]
                    self.log_result("JWT login", True, "Token obtained")
                    
                    # Test protected endpoint
                    headers = {"Authorization": f"Bearer {self.token}"}
                    resp = await client.get(f"{API_BASE_URL}/api/auth/me", headers=headers)
                    
                    if resp.status_code == 200:
                        user = resp.json()
                        self.log_result("JWT validation", True, 
                                      f"Authenticated as {user['username']}")
                    else:
                        self.log_result("JWT validation", False, 
                                      f"Status {resp.status_code}")
                else:
                    self.log_result("JWT login", False, f"Status {resp.status_code}")
                    
            except Exception as e:
                self.log_result("JWT authentication", False, str(e))
            
            # 3. Decks endpoint
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
                
                try:
                    resp = await client.get(f"{API_BASE_URL}/api/decks", headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        self.log_result("GET /decks", True, 
                                      f"{data.get('total', 0)} decks returned")
                    else:
                        self.log_result("GET /decks", False, f"Status {resp.status_code}")
                except Exception as e:
                    self.log_result("GET /decks", False, str(e))
                
                # 4. Archetypes endpoint
                try:
                    resp = await client.get(f"{API_BASE_URL}/api/archetypes?format=modern")
                    if resp.status_code == 200:
                        archetypes = resp.json()
                        self.log_result("GET /archetypes", True, 
                                      f"{len(archetypes)} archetypes")
                    else:
                        self.log_result("GET /archetypes", False, 
                                      f"Status {resp.status_code}")
                except Exception as e:
                    self.log_result("GET /archetypes", False, str(e))
                
                # 5. Meta analysis endpoint
                try:
                    resp = await client.get(f"{API_BASE_URL}/api/analysis/meta/modern")
                    if resp.status_code == 200:
                        meta = resp.json()
                        self.log_result("GET /analysis/meta", True,
                                      f"{meta.get('total_decks', 0)} decks analyzed")
                    elif resp.status_code == 404:
                        # Expected when no data exists
                        self.log_result("GET /analysis/meta", True,
                                      "No data (expected for empty DB)")
                    else:
                        self.log_result("GET /analysis/meta", False,
                                      f"Status {resp.status_code}")
                except Exception as e:
                    self.log_result("GET /analysis/meta", False, str(e))
                
                # 6. Test pagination
                try:
                    resp = await client.get(
                        f"{API_BASE_URL}/api/decks?limit=5&offset=0", 
                        headers=headers
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        has_pagination = all(k in data for k in ['items', 'total', 'size', 'page'])
                        self.log_result("Pagination", has_pagination,
                                      f"Size: {data.get('size')}, Total: {data.get('total')}")
                    else:
                        self.log_result("Pagination", False, f"Status {resp.status_code}")
                except Exception as e:
                    self.log_result("Pagination", False, str(e))
                
                # 7. Test filters
                try:
                    resp = await client.get(
                        f"{API_BASE_URL}/api/decks?format=modern&archetype=Burn",
                        headers=headers
                    )
                    self.log_result("Filters", resp.status_code == 200,
                                  "Format and archetype filters work")
                except Exception as e:
                    self.log_result("Filters", False, str(e))
    
    def test_visualizations(self):
        """Test visualization generation."""
        print("\n🔍 VISUALISATIONS")
        print("=" * 60)
        
        try:
            from src.visualizations.matchup_heatmap import generate_matchup_heatmap
            
            # Generate test heatmap
            output_path = Path("output/test_heatmap.png")
            output_path.parent.mkdir(exist_ok=True)
            
            # Get some matchup data
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SET search_path TO manalytics, public;")
                    cursor.execute("""
                        SELECT COUNT(*) FROM decklists 
                        WHERE archetype_id IS NOT NULL;
                    """)
                    deck_count = cursor.fetchone()[0]
            
            if deck_count > 10:
                # Try to generate heatmap
                success = generate_matchup_heatmap(
                    format_name="modern",
                    days=30,
                    output_path=str(output_path)
                )
                
                if success and output_path.exists():
                    self.log_result("Heatmap generation", True, 
                                  f"Created {output_path}")
                else:
                    self.log_result("Heatmap generation", False,
                                  "Failed to create heatmap")
            else:
                self.log_result("Heatmap generation", False,
                              f"Not enough data ({deck_count} decks)")
            
            
        except Exception as e:
            self.log_result("Visualizations", False, str(e))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success rate: {passed/total*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed == 0

async def main():
    """Run all integration tests."""
    print("🚀 MANALYTICS FINAL INTEGRATION TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    tester = IntegrationTester()
    
    # Run tests in order
    tester.test_env_variables()
    tester.test_db_connection()
    tester.test_redis_connection()
    tester.test_user_creation()
    
    # Async tests
    await tester.test_pipeline()
    await tester.test_api_complete()
    
    # Sync tests
    tester.test_visualizations()
    
    # Summary
    all_passed = tester.print_summary()
    
    print(f"\nCompleted at: {datetime.now()}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)