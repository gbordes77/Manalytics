#!/usr/bin/env python3
"""
Migrate downloaded archetype rules to the database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import click
from pathlib import Path
from database.db_pool import get_db_connection
from config.settings import settings

@click.command()
def migrate_rules():
    """Load archetype rules from files into the database."""
    click.echo("Migrating archetype rules to database...")
    
    rules_dir = settings.RULES_DIR
    if not rules_dir.exists():
        click.echo(f"Rules directory not found: {rules_dir}")
        return
    
    rules_loaded = 0
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO manalytics, public;")
            
            # Clear existing rules
            cursor.execute("TRUNCATE TABLE archetype_rules CASCADE;")
            
            # Process each format directory
            for format_dir in rules_dir.iterdir():
                if not format_dir.is_dir():
                    continue
                
                format_name = format_dir.name
                archetypes_dir = format_dir / "Archetypes"
                
                if not archetypes_dir.exists():
                    continue
                
                # Process each archetype file
                for archetype_file in archetypes_dir.glob("*.json"):
                    try:
                        with open(archetype_file, 'r', encoding='utf-8') as f:
                            archetype_data = json.load(f)
                        
                        # First, get or create the archetype
                        cursor.execute("""
                            SELECT id FROM formats WHERE name = %s
                        """, (format_name,))
                        format_result = cursor.fetchone()
                        
                        if not format_result:
                            click.echo(f"  -> Format {format_name} not found in database")
                            continue
                            
                        format_id = format_result[0]
                        archetype_name = archetype_file.stem
                        
                        # Insert or get archetype
                        cursor.execute("""
                            INSERT INTO archetypes (format_id, name, display_name)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (format_id, name) DO UPDATE
                            SET display_name = EXCLUDED.display_name
                            RETURNING id
                        """, (format_id, archetype_name, archetype_name))
                        
                        archetype_id = cursor.fetchone()[0]
                        
                        # Insert archetype rule
                        cursor.execute("""
                            INSERT INTO archetype_rules (archetype_id, rule_type, rule_data)
                            VALUES (%s, %s, %s)
                        """, (
                            archetype_id,
                            'detection',
                            json.dumps(archetype_data)
                        ))
                        
                        rules_loaded += 1
                        conn.commit()  # Commit after each successful insert
                        
                    except Exception as e:
                        click.echo(f"  -> Error loading {archetype_file}: {e}")
                        conn.rollback()  # Rollback on error
                        continue
            
            click.echo(f"Successfully loaded {rules_loaded} archetype rules.")

if __name__ == "__main__":
    migrate_rules()