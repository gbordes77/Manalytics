#!/usr/bin/env python3
"""
Analyze tournament data excluding leagues
"""
import sqlite3
from collections import Counter
import json

# Connect to cache database
conn = sqlite3.connect('data/cache/tournaments.db')
cursor = conn.cursor()

# Get all decklists excluding leagues
query = """
SELECT d.archetype, d.colors
FROM decklists d
JOIN tournaments t ON d.tournament_id = t.tournament_id
WHERE (t.platform = 'mtgo' AND t.format = 'standard' AND t.type != 'league')
   OR (t.platform = 'melee' AND t.format = 'standard')
"""

cursor.execute(query)
results = cursor.fetchall()

archetype_counts = Counter()
total_decks = 0

for archetype, colors in results:
    if archetype:
        archetype_counts[archetype] += 1
        total_decks += 1

# Get tournament count
cursor.execute("""
SELECT COUNT(DISTINCT tournament_id) 
FROM tournaments 
WHERE (platform = 'mtgo' AND format = 'standard' AND type != 'league')
   OR (platform = 'melee' AND format = 'standard')
""")
total_tournaments = cursor.fetchone()[0]

# Count unique archetypes
unique_archetypes = len(archetype_counts)

conn.close()

print(f'TOTAL TOURNAMENTS (sans leagues): {total_tournaments}')
print(f'TOTAL DECKS (sans leagues): {total_decks}')
print(f'UNIQUE ARCHETYPES: {unique_archetypes}')
print(f'\nAll Archetypes by frequency:')

# Export data for visualization
data_for_viz = []
for arch, count in archetype_counts.most_common():
    percentage = (count / total_decks) * 100 if total_decks > 0 else 0
    print(f'{arch}: {count} decks ({percentage:.2f}%)')
    data_for_viz.append({
        'name': arch,
        'decks': count,
        'percentage': round(percentage, 2)
    })

# Save to JSON for visualization
with open('archetype_data_no_leagues.json', 'w') as f:
    json.dump({
        'total_tournaments': total_tournaments,
        'total_decks': total_decks,
        'unique_archetypes': unique_archetypes,
        'archetypes': data_for_viz
    }, f, indent=2)

print(f"\nData saved to archetype_data_no_leagues.json")