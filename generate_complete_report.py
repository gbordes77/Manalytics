#!/usr/bin/env python3
"""
Generate complete tournament report including Redis cache check.
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

def get_tournaments_from_docker():
    """Get tournament data from database and Redis."""
    
    # First get from database
    query = """
    SELECT 
        t.id,
        t.name,
        t.date,
        t.url,
        s.name as source,
        f.name as format,
        COUNT(DISTINCT d.id) as deck_count
    FROM tournaments t
    JOIN formats f ON t.format_id = f.id
    JOIN sources s ON t.source_id = s.id
    LEFT JOIN decklists d ON d.tournament_id = t.id
    WHERE t.date >= '2025-07-01' AND t.date <= CURRENT_DATE
    GROUP BY t.id, t.name, t.date, t.url, s.name, f.name
    ORDER BY t.date DESC, s.name, t.name
    """
    
    cmd = [
        'docker', 'compose', 'exec', '-T', 'db',
        'psql', '-U', 'manalytics', '-d', 'manalytics', '-t', '-A', '-F|', '-c', query
    ]
    
    print("Fetching tournament data from database...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    tournaments = []
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line:
                parts = line.split('|')
                if len(parts) >= 7:
                    tournaments.append({
                        "date": parts[2],
                        "source": parts[4],
                        "format": parts[5],
                        "name": parts[1],
                        "url": parts[3],
                        "decks": int(parts[6]) if parts[6].isdigit() else 0,
                        "cached": True,
                        "in_database": True
                    })
    
    # Check Redis for cached URLs
    print("\nChecking Redis cache for additional tournaments...")
    redis_cmd = [
        'docker', 'compose', 'exec', '-T', 'redis',
        'redis-cli', 'keys', 'scraped_content:*'
    ]
    
    redis_result = subprocess.run(redis_cmd, capture_output=True, text=True)
    if redis_result.returncode == 0:
        redis_keys = redis_result.stdout.strip().split('\n')
        cached_urls = set()
        
        for key in redis_keys:
            if key and ':' in key:
                # Extract URL from key
                parts = key.split(':', 2)
                if len(parts) >= 3:
                    source = parts[1]
                    url = parts[2]
                    
                    # Check if this URL is already in our tournament list
                    if not any(t['url'] == url for t in tournaments):
                        # Try to extract date from URL
                        import re
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', url)
                        if date_match:
                            date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                            try:
                                tournament_date = datetime.strptime(date_str, '%Y-%m-%d')
                                if datetime(2025, 7, 1) <= tournament_date <= datetime.now():
                                    tournaments.append({
                                        "date": date_str,
                                        "source": source,
                                        "format": "standard",
                                        "name": f"Cached {source.upper()} Tournament",
                                        "url": url,
                                        "decks": 0,
                                        "cached": True,
                                        "in_database": False
                                    })
                                    print(f"  Found cached tournament: {date_str} - {source}")
                            except:
                                pass
    
    # Sort by date
    tournaments.sort(key=lambda x: x['date'], reverse=True)
    
    return tournaments

def generate_html_report():
    """Generate the HTML report with tournament data."""
    tournaments = get_tournaments_from_docker()
    
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
    output_path = Path("/Volumes/DataDisk/_Projects/Manalytics/tournaments_cache_report_complete.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nGenerated report with {len(tournaments)} tournaments")
    print(f"Report saved to: {output_path}")
    
    # Summary statistics
    mtgo_count = sum(1 for t in tournaments if t['source'] == 'mtgo')
    melee_count = sum(1 for t in tournaments if t['source'] == 'melee')
    in_db_count = sum(1 for t in tournaments if t.get('in_database', False))
    cached_only_count = sum(1 for t in tournaments if not t.get('in_database', False))
    total_decks = sum(t['decks'] for t in tournaments)
    
    print(f"\nStatistics:")
    print(f"  MTGO tournaments: {mtgo_count}")
    print(f"  Melee tournaments: {melee_count}")
    print(f"  Tournaments in database: {in_db_count}")
    print(f"  Tournaments only in cache: {cached_only_count}")
    print(f"  Total decks: {total_decks}")
    
    # Date range
    if tournaments:
        earliest = min(t['date'] for t in tournaments)
        latest = max(t['date'] for t in tournaments)
        print(f"  Date range: {earliest} to {latest}")
    
    # Show gaps in dates
    if tournaments:
        dates = sorted(set(t['date'] for t in tournaments))
        print(f"\nDates with tournaments: {len(dates)}")
        print(f"Missing dates from July 1-24:")
        for day in range(1, 25):
            date_str = f"2025-07-{day:02d}"
            if date_str not in dates:
                print(f"  - {date_str}")
    
    return output_path

if __name__ == "__main__":
    output_path = generate_html_report()
    print(f"\nTo view the report, run:")
    print(f"  open '{output_path}'")