#!/usr/bin/env python3
"""
Setup test archetype rules for development
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_pool import get_db_connection
import logging
import json

logger = logging.getLogger(__name__)

def setup_test_archetypes():
    """Create some test archetype rules"""
    
    test_archetypes = [
        # Modern archetypes
        ('Burn', 'modern', 8, ['Lightning Bolt', 'Goblin Guide', 'Monastery Swiftspear', 'Eidolon of the Great Revel']),
        ('Ragavan Midrange', 'modern', 6, ['Ragavan, Nimble Pilferer', 'Dragon\'s Rage Channeler', 'Mishra\'s Bauble']),
        ('Amulet Titan', 'modern', 8, ['Amulet of Vigor', 'Primeval Titan', 'Dryad of the Ilysian Grove']),
        ('Murktide', 'modern', 4, ['Murktide Regent', 'Ledger Shredder', 'Counterspell']),
        ('Hammer Time', 'modern', 6, ['Colossus Hammer', 'Sigarda\'s Aid', 'Puresteel Paladin']),
        
        # Legacy archetypes  
        ('Delver', 'legacy', 8, ['Delver of Secrets', 'Daze', 'Force of Will', 'Wasteland']),
        ('Reanimator', 'legacy', 6, ['Reanimate', 'Entomb', 'Griselbrand', 'Dark Ritual']),
        
        # Pioneer archetypes
        ('Rakdos Midrange', 'pioneer', 6, ['Bloodtithe Harvester', 'Fable of the Mirror-Breaker', 'Thoughtseize']),
        ('Green Devotion', 'pioneer', 8, ['Nykthos, Shrine to Nyx', 'Elvish Mystic', 'Karn, the Great Creator']),
    ]
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET search_path TO manalytics, public;")
                
                # First check if archetypes table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'manalytics' 
                        AND table_name = 'archetypes'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.error("Archetypes table does not exist!")
                    return False
                
                # Insert test archetypes
                for name, format_name, min_cards, key_cards in test_archetypes:
                    # Get format ID
                    cursor.execute("SELECT id FROM formats WHERE name = %s;", (format_name,))
                    format_id = cursor.fetchone()[0]
                    
                    # First insert into archetypes table
                    cursor.execute("""
                        INSERT INTO archetypes (name, format_id) 
                        VALUES (%s, %s)
                        ON CONFLICT (format_id, name) DO NOTHING
                        RETURNING id;
                    """, (name, format_id))
                    
                    result = cursor.fetchone()
                    if result:
                        archetype_id = result[0]
                    else:
                        # Get existing ID
                        cursor.execute("""
                            SELECT id FROM archetypes 
                            WHERE name = %s AND format_id = %s;
                        """, (name, format_id))
                        archetype_id = cursor.fetchone()[0]
                    
                    # Insert archetype rule
                    rule_data = {
                        'key_cards': key_cards,
                        'min_cards': min_cards,
                        'required': key_cards[:2]
                    }
                    
                    cursor.execute("""
                        INSERT INTO archetype_rules (archetype_id, rule_type, rule_data)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (archetype_id, 'card_detection', json.dumps(rule_data)))
                
                conn.commit()
                
                # Verify
                cursor.execute("SELECT COUNT(*) FROM archetype_rules;")
                count = cursor.fetchone()[0]
                print(f"✅ Successfully created {count} archetype rules")
                
                return True
                
    except Exception as e:
        logger.error(f"Error setting up archetypes: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_test_archetypes()