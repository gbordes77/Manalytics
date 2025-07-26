#!/usr/bin/env python3
"""
Compare our tournaments with Jiliac's list for July 1-20, 2025
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.cache.database import CacheDatabase

# Jiliac's tournament list (July 1-20, 2025)
jiliac_tournaments = [
    ("2025-07-01", "Standard Challenge 64 2025-07-01", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0112801190"),
    ("2025-07-02", "TheGathering.gg Standard Post-BNR Celebration 2025-07-02", "https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58"),
    ("2025-07-02", "TheGathering.gg Standard Post-BNR Celebration #2 2025-07-02", "https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4"),
    ("2025-07-03", "Standard Challenge 32 2025-07-03", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0312801623"),
    ("2025-07-04", "Standard Challenge 32 2025-07-04", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0412801637"),
    ("2025-07-05", "Standard Challenge 32 2025-07-05", "https://www.mtgo.com/decklist/standard-challenge-32-2025-05-2512801654"),
    ("2025-07-06", "第2回シングルスター杯　サブイベント 2025-07-06", "https://melee.gg/Decklist/View/58391bb8-9d9a-4c34-98af-b31100d6d6ea"),
    ("2025-07-06", "Jaffer's Tarkir Dragonstorm Mosh Pit 2025-07-06", "https://melee.gg/Decklist/View/ddae0ba9-a4d7-4708-9e0b-b2cc003d55e2"),
    ("2025-07-06", "F2F Tour Red Deer - Sunday Super Qualifier 2025-07-06", "https://melee.gg/Decklist/View/f9fbb177-1238-4e17-8146-b31201842d46"),
    ("2025-07-06", "Standard Challenge 32 2025-07-06", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0612801677"),
    ("2025-07-07", "Standard Challenge 64 2025-07-07", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0712801688"),
    ("2025-07-08", "Standard Challenge 64 2025-07-08", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0812801696"),
    ("2025-07-10", "Standard Challenge 32 2025-07-10", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1012802771"),
    ("2025-07-11", "Standard Challenge 32 2025-07-11", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1112802789"),
    ("2025-07-11", "Standard RC Qualifier 2025-07-11", "https://www.mtgo.com/decklist/standard-rc-qualifier-2025-07-1112802761"),
    ("2025-07-12", "Standard Challenge 32 2025-07-12", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1212802811"),
    ("2025-07-12", "Valley Dasher's Bishkek Classic #1 2025-07-12", "https://melee.gg/Decklist/View/d11c46a4-4cdb-4603-bf82-b317008faa42"),
    ("2025-07-13", "Jaffer's Final Fantasy Mosh Pit 2025-07-13", "https://melee.gg/Decklist/View/07f0edf6-0180-447c-b258-b3190103047b"),
    ("2025-07-13", "Standard Challenge 32 2025-07-13", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1312802841"),
    ("2025-07-14", "Standard Challenge 64 2025-07-14", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1412802856"),
    ("2025-07-15", "Standard Challenge 64 2025-07-15", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1512802868"),
    ("2025-07-17", "Standard Challenge 32 2025-07-17", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1712803657"),
    ("2025-07-18", "Standard Challenge 32 2025-07-18", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1812803671"),
    ("2025-07-19", "Standard Challenge 32 2025-07-19", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1912803688"),
    ("2025-07-19", "Boa Qualifier #2 2025 (standard) 2025-07-19", "https://melee.gg/Decklist/View/e87b4ce1-7121-44ad-a9be-b31f00927479"),
]

def get_our_tournaments():
    """Get our tournaments from cache for July 1-20, 2025"""
    db = CacheDatabase()
    all_tournaments = db.get_tournaments_by_format("standard")
    
    # Filter for July 1-20, 2025 and exclude leagues
    our_tournaments = []
    for t in all_tournaments:
        if 'league' in t.type.lower():
            continue
            
        date_str = t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d')
        if date_str >= "2025-07-01" and date_str <= "2025-07-20":
            our_tournaments.append({
                'date': date_str,
                'name': t.name,
                'id': t.id,
                'platform': t.platform,
                'type': t.type,
                'decks': t.players
            })
    
    return sorted(our_tournaments, key=lambda x: x['date'])

def extract_mtgo_id(url):
    """Extract MTGO tournament ID from URL"""
    if "mtgo.com" in url:
        # Extract the numeric ID at the end
        return url.split("-")[-1]
    return None

def extract_melee_id(url):
    """Extract Melee tournament ID from URL"""
    if "melee.gg" in url:
        # Extract the UUID from the URL
        return url.split("/")[-1]
    return None

def compare_tournaments():
    """Compare our tournaments with Jiliac's list"""
    our_tournaments = get_our_tournaments()
    
    # Create lookup dictionaries
    our_by_date = {}
    for t in our_tournaments:
        if t['date'] not in our_by_date:
            our_by_date[t['date']] = []
        our_by_date[t['date']].append(t)
    
    # Analyze differences
    comparison_results = []
    
    for date, name, url in jiliac_tournaments:
        platform = "MTGO" if "mtgo.com" in url else "Melee"
        jiliac_id = extract_mtgo_id(url) if platform == "MTGO" else extract_melee_id(url)
        
        # Check if we have this tournament
        found = False
        match_type = "Not Found"
        our_tournament = None
        
        if date in our_by_date:
            for our_t in our_by_date[date]:
                # Check by ID match
                if platform == "MTGO" and our_t['id'] == jiliac_id:
                    found = True
                    match_type = "✅ Exact Match"
                    our_tournament = our_t
                    break
                elif platform == "Melee" and jiliac_id in our_t['id']:
                    found = True
                    match_type = "✅ Exact Match"
                    our_tournament = our_t
                    break
                # Check by name similarity
                elif name.lower() in our_t['name'].lower() or our_t['name'].lower() in name.lower():
                    found = True
                    match_type = "⚠️ Name Match"
                    our_tournament = our_t
                    break
        
        comparison_results.append({
            'date': date,
            'platform': platform,
            'jiliac_name': name,
            'jiliac_id': jiliac_id,
            'status': match_type,
            'our_name': our_tournament['name'] if our_tournament else "N/A",
            'our_id': our_tournament['id'] if our_tournament else "N/A",
            'our_decks': our_tournament['decks'] if our_tournament else 0
        })
    
    # Check for tournaments we have that Jiliac doesn't
    jiliac_dates = {date for date, _, _ in jiliac_tournaments}
    for date, tournaments in our_by_date.items():
        if date >= "2025-07-01" and date <= "2025-07-20":
            for t in tournaments:
                # Check if this tournament is in Jiliac's list
                found_in_jiliac = False
                for j_date, j_name, j_url in jiliac_tournaments:
                    if j_date == date:
                        j_platform = "MTGO" if "mtgo.com" in j_url else "Melee"
                        j_id = extract_mtgo_id(j_url) if j_platform == "MTGO" else extract_melee_id(j_url)
                        
                        if (t['platform'].upper() == j_platform.upper() and 
                            (t['id'] == j_id or j_id in t['id'] or 
                             j_name.lower() in t['name'].lower() or 
                             t['name'].lower() in j_name.lower())):
                            found_in_jiliac = True
                            break
                
                if not found_in_jiliac:
                    comparison_results.append({
                        'date': date,
                        'platform': t['platform'],
                        'jiliac_name': "N/A",
                        'jiliac_id': "N/A",
                        'status': "❌ Only in Ours",
                        'our_name': t['name'],
                        'our_id': t['id'],
                        'our_decks': t['decks']
                    })
    
    return sorted(comparison_results, key=lambda x: (x['date'], x['platform'], x['status']))

def generate_html_report(comparison_results):
    """Generate HTML comparison report"""
    
    # Count statistics
    exact_matches = sum(1 for r in comparison_results if r['status'] == "✅ Exact Match")
    name_matches = sum(1 for r in comparison_results if r['status'] == "⚠️ Name Match")
    not_found = sum(1 for r in comparison_results if r['status'] == "Not Found")
    only_ours = sum(1 for r in comparison_results if r['status'] == "❌ Only in Ours")
    
    # Group by status
    by_status = {
        "✅ Exact Match": [],
        "⚠️ Name Match": [],
        "Not Found": [],
        "❌ Only in Ours": []
    }
    
    for result in comparison_results:
        if result['status'] in by_status:
            by_status[result['status']].append(result)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournament Comparison - Manalytics vs Jiliac</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .onlyours {{ color: #9b59b6; }}
        
        .section {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h2 {{
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #667eea;
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
        .summary ul {{
            margin: 10px 0;
        }}
        .summary li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Tournament Comparison Report</h1>
        <p>Manalytics vs Jiliac's Tournament List • July 1-20, 2025</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-value exact">{exact_matches}</div>
            <div class="stat-label">Exact Matches</div>
        </div>
        <div class="stat-box">
            <div class="stat-value name">{name_matches}</div>
            <div class="stat-label">Name Matches</div>
        </div>
        <div class="stat-box">
            <div class="stat-value notfound">{not_found}</div>
            <div class="stat-label">Not Found in Ours</div>
        </div>
        <div class="stat-box">
            <div class="stat-value onlyours">{only_ours}</div>
            <div class="stat-label">Only in Ours</div>
        </div>
    </div>
    
    <div class="summary">
        <h3>📋 Summary</h3>
        <ul>
            <li><strong>Total tournaments in Jiliac's list:</strong> {len(jiliac_tournaments)}</li>
            <li><strong>Total tournaments in our database (July 1-20):</strong> {len(set(r['our_id'] for r in comparison_results if r['our_id'] != 'N/A'))}</li>
            <li><strong>Match rate:</strong> {round((exact_matches + name_matches) / len(jiliac_tournaments) * 100, 1)}%</li>
        </ul>
    </div>
"""
    
    # Add sections for each status
    for status, results in by_status.items():
        if not results:
            continue
            
        status_color = {
            "✅ Exact Match": "exact",
            "⚠️ Name Match": "name", 
            "Not Found": "notfound",
            "❌ Only in Ours": "onlyours"
        }[status]
        
        html += f"""
    <div class="section">
        <h2 class="{status_color}">{status} ({len(results)} tournaments)</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Platform</th>
                    <th>Jiliac's Name</th>
                    <th>Our Name</th>
                    <th>Decks</th>
                    <th>IDs</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in results:
            html += f"""
                <tr>
                    <td>{result['date']}</td>
                    <td>{result['platform']}</td>
                    <td>{result['jiliac_name']}</td>
                    <td>{result['our_name']}</td>
                    <td>{result['our_decks'] if result['our_decks'] else 'N/A'}</td>
                    <td class="small">
                        J: {result['jiliac_id'] if result['jiliac_id'] else 'N/A'}<br>
                        O: {result['our_id'] if result['our_id'] != 'N/A' else 'N/A'}
                    </td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    return html

def main():
    print("🔍 Comparing tournaments with Jiliac's list...")
    
    comparison_results = compare_tournaments()
    html = generate_html_report(comparison_results)
    
    output_file = Path("data/cache/tournament_comparison_jiliac.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Comparison report created: {output_file}")
    
    # Print summary
    exact_matches = sum(1 for r in comparison_results if r['status'] == "✅ Exact Match")
    name_matches = sum(1 for r in comparison_results if r['status'] == "⚠️ Name Match")
    not_found = sum(1 for r in comparison_results if r['status'] == "Not Found")
    only_ours = sum(1 for r in comparison_results if r['status'] == "❌ Only in Ours")
    
    print(f"\n📊 Summary:")
    print(f"  - Exact matches: {exact_matches}")
    print(f"  - Name matches: {name_matches}")
    print(f"  - Not found in ours: {not_found}")
    print(f"  - Only in ours: {only_ours}")

if __name__ == "__main__":
    main()