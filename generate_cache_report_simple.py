#!/usr/bin/env python3
"""
Generate HTML report of cached tournaments - simplified version using Docker.
"""
import subprocess
import json
from pathlib import Path

def get_tournaments_from_docker():
    """Get tournament data by executing commands in Docker containers."""
    
    # Get tournament data from PostgreSQL via Docker
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
    
    # Execute query in PostgreSQL container
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
                        "cached": True  # Assume cached if in DB
                    })
    
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
    output_path = Path("/Volumes/DataDisk/_Projects/Manalytics/tournaments_cache_report_final.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nGenerated report with {len(tournaments)} tournaments")
    print(f"Report saved to: {output_path}")
    
    # Summary statistics
    mtgo_count = sum(1 for t in tournaments if t['source'] == 'mtgo')
    melee_count = sum(1 for t in tournaments if t['source'] == 'melee')
    total_decks = sum(t['decks'] for t in tournaments)
    
    print(f"\nStatistics:")
    print(f"  MTGO tournaments: {mtgo_count}")
    print(f"  Melee tournaments: {melee_count}")
    print(f"  Total decks: {total_decks}")
    
    # Show first few tournaments
    print(f"\nFirst 5 tournaments:")
    for t in tournaments[:5]:
        print(f"  {t['date']} - {t['source'].upper()} - {t['name']} ({t['decks']} decks)")
    
    return output_path

if __name__ == "__main__":
    output_path = generate_html_report()
    print(f"\nTo view the report, run:")
    print(f"  open '{output_path}'")