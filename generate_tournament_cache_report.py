#!/usr/bin/env python3
"""
Generate HTML report of cached tournaments between July 1st and today.
"""
import asyncio
import json
from datetime import datetime, timedelta
import redis
import asyncpg
from pathlib import Path

async def get_cached_tournaments():
    """Retrieve all cached tournaments from Redis and database."""
    tournaments = []
    
    # Redis connection
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Database connection
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='postgres',
        database='manalytics'
    )
    
    try:
        # Define date range
        start_date = datetime(2025, 7, 1)
        end_date = datetime.now()
        
        # Query database for tournaments in date range
        query = """
        SELECT 
            t.id,
            t.name,
            t.date,
            t.url,
            t.source,
            f.name as format,
            COUNT(DISTINCT d.id) as deck_count
        FROM tournaments t
        JOIN formats f ON t.format_id = f.id
        LEFT JOIN decklists d ON d.tournament_id = t.id
        WHERE t.date >= $1 AND t.date <= $2
        GROUP BY t.id, t.name, t.date, t.url, t.source, f.name
        ORDER BY t.date DESC, t.source, t.name
        """
        
        rows = await conn.fetch(query, start_date.date(), end_date.date())
        
        for row in rows:
            # Check if tournament is in Redis cache
            cache_key = f"tournament:{row['source']}:{row['id']}"
            cached_data = r.get(cache_key)
            is_cached = cached_data is not None
            
            tournaments.append({
                "date": row['date'].strftime('%Y-%m-%d'),
                "source": row['source'],
                "format": row['format'],
                "name": row['name'],
                "url": row['url'],
                "decks": row['deck_count'],
                "cached": is_cached
            })
        
        # Also check for recent scrapes in Redis
        # Pattern for MTGO and Melee cache keys
        for source in ['mtgo', 'melee']:
            pattern = f"scraped_content:{source}:*"
            for key in r.scan_iter(match=pattern):
                # Extract URL from key
                url = key.replace(f"scraped_content:{source}:", "")
                
                # Check if this URL is already in our list
                if not any(t['url'] == url for t in tournaments):
                    # Try to get cached data
                    cached_html = r.get(key)
                    if cached_html:
                        # Extract date from URL if possible
                        import re
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', url)
                        if date_match:
                            try:
                                cache_date = datetime(
                                    int(date_match.group(1)),
                                    int(date_match.group(2)),
                                    int(date_match.group(3))
                                )
                                if start_date <= cache_date <= end_date:
                                    tournaments.append({
                                        "date": cache_date.strftime('%Y-%m-%d'),
                                        "source": source,
                                        "format": "Unknown",
                                        "name": f"Cached {source.upper()} Tournament",
                                        "url": url,
                                        "decks": 0,
                                        "cached": True
                                    })
                            except:
                                pass
        
    finally:
        await conn.close()
    
    return tournaments

async def generate_html_report():
    """Generate the HTML report with tournament data."""
    tournaments = await get_cached_tournaments()
    
    # Read the HTML template
    html_path = Path("/Volumes/DataDisk/_Projects/Manalytics/tournaments_cache_report.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Convert tournaments to JSON and inject into HTML
    tournaments_json = json.dumps(tournaments, indent=2)
    html_content = html_content.replace(
        '[/* TOURNAMENTS_DATA_PLACEHOLDER */]',
        tournaments_json
    )
    
    # Write the updated HTML
    output_path = Path("/Volumes/DataDisk/_Projects/Manalytics/tournaments_cache_report_generated.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated report with {len(tournaments)} tournaments")
    print(f"Report saved to: {output_path}")
    
    # Summary statistics
    mtgo_count = sum(1 for t in tournaments if t['source'] == 'mtgo')
    melee_count = sum(1 for t in tournaments if t['source'] == 'melee')
    cached_count = sum(1 for t in tournaments if t['cached'])
    total_decks = sum(t['decks'] for t in tournaments)
    
    print(f"\nStatistics:")
    print(f"  MTGO tournaments: {mtgo_count}")
    print(f"  Melee tournaments: {melee_count}")
    print(f"  Cached tournaments: {cached_count}")
    print(f"  Total decks: {total_decks}")
    
    return output_path

if __name__ == "__main__":
    output_path = asyncio.run(generate_html_report())
    print(f"\nOpen the report with: open '{output_path}'")