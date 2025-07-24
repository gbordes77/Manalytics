-- Quick test data for Modern format
BEGIN;

-- Insert test tournaments
INSERT INTO manalytics.tournaments (name, date, players_count, format_id, source_id, url)
SELECT 
    'Test Modern League ' || i,
    CURRENT_DATE - (i || ' days')::interval,
    100 + (random() * 100)::int,
    (SELECT id FROM manalytics.formats WHERE name = 'modern'),
    (SELECT id FROM manalytics.sources WHERE name = 'mtgo'),
    'https://example.com/tournament/' || i
FROM generate_series(0, 4) i;

-- Insert test players
INSERT INTO manalytics.players (name)
SELECT 'TestPlayer' || i
FROM generate_series(1, 50) i;

-- Insert test decklists
WITH tournaments AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY date DESC) as rn
    FROM manalytics.tournaments
    WHERE format_id = (SELECT id FROM manalytics.formats WHERE name = 'modern')
    ORDER BY date DESC
    LIMIT 5
),
players AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY name) as rn
    FROM manalytics.players
    WHERE name LIKE 'TestPlayer%'
),
archetypes AS (
    SELECT id, name, ROW_NUMBER() OVER (ORDER BY name) as rn
    FROM manalytics.archetypes
    WHERE format_id = (SELECT id FROM manalytics.formats WHERE name = 'modern')
    LIMIT 10
)
INSERT INTO manalytics.decklists (tournament_id, player_id, archetype_id, position, wins, losses, mainboard, sideboard)
SELECT 
    t.id,
    p.id,
    a.id,
    ((t.rn - 1) * 20 + (p.rn % 20) + 1),
    CASE WHEN (p.rn % 20) <= 8 THEN 4 + (random() * 2)::int ELSE 3 + (random() * 2)::int END,
    CASE WHEN (p.rn % 20) <= 8 THEN (random() * 2)::int ELSE 1 + (random() * 2)::int END,
    '[{"name": "Lightning Bolt", "quantity": 4}, {"name": "Mountain", "quantity": 20}]'::jsonb,
    '[{"name": "Alpine Moon", "quantity": 2}]'::jsonb
FROM tournaments t
CROSS JOIN players p
CROSS JOIN archetypes a
WHERE p.rn <= 20
AND a.rn = ((p.rn - 1) % 10) + 1;

COMMIT;