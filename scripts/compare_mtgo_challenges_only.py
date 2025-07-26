#!/usr/bin/env python3
"""
Compare only MTGO Challenges between our data and Jiliac's list
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.cache.database import CacheDatabase

# Jiliac's MTGO Challenges (July 1-20, 2025)
jiliac_challenges = [
    ("2025-07-01", "Standard Challenge 64", "12801190"),
    ("2025-07-03", "Standard Challenge 32", "12801623"),
    ("2025-07-04", "Standard Challenge 32", "12801637"),
    ("2025-07-05", "Standard Challenge 32", "12801654"),  # Note: URL says 05-25 but date is 07-05
    ("2025-07-06", "Standard Challenge 32", "12801677"),
    ("2025-07-07", "Standard Challenge 64", "12801688"),
    ("2025-07-08", "Standard Challenge 64", "12801696"),
    ("2025-07-10", "Standard Challenge 32", "12802771"),
    ("2025-07-11", "Standard Challenge 32", "12802789"),
    ("2025-07-11", "Standard RC Qualifier", "12802761"),
    ("2025-07-12", "Standard Challenge 32", "12802811"),
    ("2025-07-13", "Standard Challenge 32", "12802841"),
    ("2025-07-14", "Standard Challenge 64", "12802856"),
    ("2025-07-15", "Standard Challenge 64", "12802868"),
    ("2025-07-17", "Standard Challenge 32", "12803657"),
    ("2025-07-18", "Standard Challenge 32", "12803671"),
    ("2025-07-19", "Standard Challenge 32", "12803688"),
]

def get_our_mtgo_challenges():
    """Get our MTGO challenges from cache"""
    db = CacheDatabase()
    all_tournaments = db.get_tournaments_by_format("standard")
    
    # Filter for MTGO challenges only (July 1-20, 2025)
    our_challenges = []
    for t in all_tournaments:
        if t.platform.lower() != "mtgo":
            continue
        if 'league' in t.type.lower():
            continue
            
        date_str = t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d')
        if date_str >= "2025-07-01" and date_str <= "2025-07-20":
            # Extract just the numeric ID from various formats
            mtgo_id = t.id
            if '-' in mtgo_id:
                # Handle IDs like "challenge-32-2025-07-03-12801623"
                parts = mtgo_id.split('-')
                mtgo_id = parts[-1]
            
            our_challenges.append({
                'date': date_str,
                'name': t.name,
                'id': mtgo_id,
                'full_id': t.id,
                'type': t.type,
                'players': t.players
            })
    
    return sorted(our_challenges, key=lambda x: x['date'])

def compare_challenges():
    """Compare MTGO challenges"""
    our_challenges = get_our_mtgo_challenges()
    
    # Create lookup by date
    our_by_date = {}
    for c in our_challenges:
        if c['date'] not in our_by_date:
            our_by_date[c['date']] = []
        our_by_date[c['date']].append(c)
    
    comparison_results = []
    
    for date, name, jiliac_id in jiliac_challenges:
        found = False
        match_type = "❌ Not Found"
        our_challenge = None
        
        if date in our_by_date:
            for our_c in our_by_date[date]:
                # Check by ID
                if our_c['id'] == jiliac_id:
                    found = True
                    match_type = "✅ Exact Match"
                    our_challenge = our_c
                    break
                # Check by name similarity
                elif name.lower() in our_c['name'].lower():
                    found = True
                    match_type = "⚠️ Name Match"
                    our_challenge = our_c
                    break
        
        comparison_results.append({
            'date': date,
            'jiliac_name': name,
            'jiliac_id': jiliac_id,
            'status': match_type,
            'our_name': our_challenge['name'] if our_challenge else "N/A",
            'our_id': our_challenge['id'] if our_challenge else "N/A",
            'our_full_id': our_challenge['full_id'] if our_challenge else "N/A",
            'players': our_challenge['players'] if our_challenge else 0
        })
    
    # Check for challenges we have that Jiliac doesn't
    jiliac_dates_ids = {(date, id) for date, _, id in jiliac_challenges}
    
    for date, challenges in our_by_date.items():
        for c in challenges:
            found_in_jiliac = False
            for j_date, j_name, j_id in jiliac_challenges:
                if j_date == date and (c['id'] == j_id or j_name.lower() in c['name'].lower()):
                    found_in_jiliac = True
                    break
            
            if not found_in_jiliac:
                comparison_results.append({
                    'date': date,
                    'jiliac_name': "N/A",
                    'jiliac_id': "N/A",
                    'status': "🔵 Only in Ours",
                    'our_name': c['name'],
                    'our_id': c['id'],
                    'our_full_id': c['full_id'],
                    'players': c['players']
                })
    
    return sorted(comparison_results, key=lambda x: (x['date'], x['status']))

def generate_html_report(comparison_results):
    """Generate HTML comparison report for MTGO Challenges"""
    
    # Count statistics
    exact_matches = sum(1 for r in comparison_results if r['status'] == "✅ Exact Match")
    name_matches = sum(1 for r in comparison_results if r['status'] == "⚠️ Name Match")
    not_found = sum(1 for r in comparison_results if r['status'] == "❌ Not Found")
    only_ours = sum(1 for r in comparison_results if r['status'] == "🔵 Only in Ours")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTGO Challenges Comparison - Manalytics vs Jiliac</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .exact {{ color: #27ae60; }}
        .name {{ color: #f39c12; }}
        .notfound {{ color: #e74c3c; }}
        .onlyours {{ color: #3498db; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .small {{
            font-size: 0.85em;
            color: #7f8c8d;
        }}
        .id-cell {{
            font-family: monospace;
            font-size: 0.9em;
        }}
        .status-cell {{
            font-weight: 600;
        }}
        .summary {{
            background: #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .summary h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .note {{
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 MTGO Challenges Comparison</h1>
        <p>Manalytics vs Jiliac's List • July 1-20, 2025 • Challenges Only</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-value exact">{exact_matches}</div>
            <div class="stat-label">Exact ID Matches</div>
        </div>
        <div class="stat-box">
            <div class="stat-value name">{name_matches}</div>
            <div class="stat-label">Name Matches</div>
        </div>
        <div class="stat-box">
            <div class="stat-value notfound">{not_found}</div>
            <div class="stat-label">Not Found</div>
        </div>
        <div class="stat-box">
            <div class="stat-value onlyours">{only_ours}</div>
            <div class="stat-label">Only in Ours</div>
        </div>
    </div>
    
    <div class="summary">
        <h3>📋 Summary</h3>
        <ul>
            <li><strong>Jiliac's MTGO Challenges:</strong> {len(jiliac_challenges)}</li>
            <li><strong>Our MTGO Challenges:</strong> {len(set(r['our_id'] for r in comparison_results if r['our_id'] != 'N/A'))}</li>
            <li><strong>Match rate:</strong> {round((exact_matches + name_matches) / len(jiliac_challenges) * 100, 1)}%</li>
        </ul>
    </div>
"""

    if not_found > 0:
        html += """
    <div class="note">
        <strong>⚠️ Note:</strong> Some challenges show as "Not Found" but might be present with different ID formats.
        Check the detailed table below for potential matches by date.
    </div>
"""

    html += """
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Status</th>
                <th>Jiliac's Name</th>
                <th>Our Name</th>
                <th>Players</th>
                <th>Jiliac ID</th>
                <th>Our ID</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for result in comparison_results:
        status_class = {
            "✅ Exact Match": "exact",
            "⚠️ Name Match": "name",
            "❌ Not Found": "notfound",
            "🔵 Only in Ours": "onlyours"
        }.get(result['status'], "")
        
        html += f"""
            <tr>
                <td>{result['date']}</td>
                <td class="status-cell {status_class}">{result['status']}</td>
                <td>{result['jiliac_name']}</td>
                <td>{result['our_name']}</td>
                <td>{result['players'] if result['players'] else 'N/A'}</td>
                <td class="id-cell">{result['jiliac_id']}</td>
                <td class="id-cell">{result['our_id']}</td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <div class="note" style="margin-top: 30px;">
        <strong>📝 ID Format Notes:</strong><br>
        - Jiliac uses numeric IDs only (e.g., "12801190")<br>
        - Our system may store full IDs (e.g., "challenge-64-2025-07-01-12801190")<br>
        - The comparison extracts numeric parts for matching
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("🔍 Comparing MTGO Challenges with Jiliac's list...")
    
    comparison_results = compare_challenges()
    html = generate_html_report(comparison_results)
    
    output_file = Path("data/cache/mtgo_challenges_comparison.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Comparison report created: {output_file}")
    
    # Print summary
    exact_matches = sum(1 for r in comparison_results if r['status'] == "✅ Exact Match")
    name_matches = sum(1 for r in comparison_results if r['status'] == "⚠️ Name Match")
    not_found = sum(1 for r in comparison_results if r['status'] == "❌ Not Found")
    only_ours = sum(1 for r in comparison_results if r['status'] == "🔵 Only in Ours")
    
    print(f"\n📊 MTGO Challenges Summary:")
    print(f"  - Exact ID matches: {exact_matches}")
    print(f"  - Name matches: {name_matches}")
    print(f"  - Not found: {not_found}")
    print(f"  - Only in ours: {only_ours}")
    
    # Show missing ones if any
    if not_found > 0:
        print(f"\n⚠️ Missing challenges:")
        for r in comparison_results:
            if r['status'] == "❌ Not Found":
                print(f"  - {r['date']}: {r['jiliac_name']} (ID: {r['jiliac_id']})")

if __name__ == "__main__":
    main()