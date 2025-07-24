#!/usr/bin/env python3
"""
Database migration script for Manalytics.
Applies SQL migrations in order.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from pathlib import Path
import logging
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        self.migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        self.applied_migrations = set()
        
    def connect(self):
        """Connect to database."""
        return psycopg2.connect(settings.DATABASE_URL)
    
    def create_migrations_table(self, conn):
        """Create migrations tracking table if it doesn't exist."""
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO manalytics, public;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("✅ Migrations table ready")
    
    def get_applied_migrations(self, conn):
        """Get list of already applied migrations."""
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO manalytics, public;")
            cursor.execute("SELECT filename FROM schema_migrations;")
            return {row[0] for row in cursor.fetchall()}
    
    def apply_migration(self, conn, migration_file):
        """Apply a single migration file."""
        logger.info(f"📝 Applying migration: {migration_file.name}")
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SET search_path TO manalytics, public;")
                
                # Read and execute migration
                with open(migration_file, 'r') as f:
                    sql = f.read()
                cursor.execute(sql)
                
                # Record migration as applied
                cursor.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s);",
                    (migration_file.name,)
                )
                
            conn.commit()
            logger.info(f"✅ Migration {migration_file.name} applied successfully")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Migration {migration_file.name} failed: {e}")
            return False
    
    def run_migrations(self):
        """Run all pending migrations."""
        logger.info("🚀 Starting database migrations...")
        
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return
        
        try:
            conn = self.connect()
            
            # Ensure migrations table exists
            self.create_migrations_table(conn)
            
            # Get already applied migrations
            applied = self.get_applied_migrations(conn)
            logger.info(f"📊 Found {len(applied)} applied migrations")
            
            # Get migration files
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            logger.info(f"📁 Found {len(migration_files)} migration files")
            
            # Apply pending migrations
            pending_count = 0
            for migration_file in migration_files:
                if migration_file.name not in applied:
                    pending_count += 1
                    if not self.apply_migration(conn, migration_file):
                        logger.error("❌ Migration failed, stopping.")
                        break
            
            if pending_count == 0:
                logger.info("✅ No pending migrations")
            else:
                logger.info(f"✅ Applied {pending_count} migrations")
            
            conn.close()
            
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            sys.exit(1)
    
    def rollback_migration(self, migration_name):
        """Rollback a specific migration (if rollback script exists)."""
        logger.warning("⚠️  Rollback functionality not implemented yet")
        # TODO: Implement rollback using down scripts
    
    def status(self):
        """Show migration status."""
        try:
            conn = self.connect()
            self.create_migrations_table(conn)
            
            applied = self.get_applied_migrations(conn)
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            
            print("\n📊 Migration Status:")
            print("=" * 60)
            
            for migration_file in migration_files:
                status = "✅ Applied" if migration_file.name in applied else "⏳ Pending"
                print(f"{status} - {migration_file.name}")
            
            print("=" * 60)
            print(f"Total: {len(migration_files)} migrations, {len(applied)} applied")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error checking status: {e}")

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("command", choices=["migrate", "status", "rollback"],
                       help="Command to run")
    parser.add_argument("--migration", help="Specific migration for rollback")
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.command == "migrate":
        migrator.run_migrations()
    elif args.command == "status":
        migrator.status()
    elif args.command == "rollback":
        if not args.migration:
            logger.error("❌ Please specify migration to rollback with --migration")
            sys.exit(1)
        migrator.rollback_migration(args.migration)

if __name__ == "__main__":
    main()