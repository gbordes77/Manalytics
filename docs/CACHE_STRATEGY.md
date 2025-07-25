# 🚀 Stratégie de Cache pour Manalytics

## Problème
Le système de Jiliac est plus efficace grâce à ses couches multiples :
- Cache centralisé (pas de re-parsing)
- Processing C# compilé (plus rapide)
- Distribution de charge

## Solution Proposée : Cache Local Intelligent

### Architecture à 2 Couches

```
Couche 1: Collection & Cache
├── Scrapers (MTGO/Melee)
├── Cache Processor
│   ├── Parse raw JSON une fois
│   ├── Détecte couleurs & archétypes
│   └── Sauve en cache optimisé
└── data/cache/
    ├── tournaments_cache.json     # Métadonnées
    ├── decklists_cache.parquet   # Format columnar
    └── archetypes_cache.json      # Résultats

Couche 2: Analyse
├── Cache Reader (ms)
├── Analyzers
└── Visualizers
```

### Format de Cache Optimisé

```json
// tournaments_cache.json
{
  "last_updated": "2025-01-25T20:00:00Z",
  "tournaments": {
    "2025-01-15_standard-challenge-64": {
      "id": "12801190",
      "date": "2025-01-15",
      "format": "standard",
      "type": "challenge",
      "players": 64,
      "cache_file": "cache_20250115_12801190.parquet"
    }
  }
}
```

### Utilisation de Parquet
- Format columnar = lecture 10x plus rapide
- Compression native = 70% moins d'espace
- Support natif pandas = analyse rapide

### Workflow Optimisé

1. **Scraping** (1x/jour)
   ```python
   raw_data = scrape_tournaments()
   ```

2. **Processing** (après scraping)
   ```python
   for tournament in new_tournaments:
       decks = parse_tournament(tournament)
       colors = detect_colors_batch(decks)
       archetypes = detect_archetypes_batch(decks)
       save_to_cache(decks, colors, archetypes)
   ```

3. **Analyse** (instantané)
   ```python
   # Charge tout en <100ms
   cache = load_parquet_cache()
   analyze_metagame(cache)
   ```

### Avantages
- ✅ Parsing 1x seulement (comme Jiliac)
- ✅ Lecture ultra-rapide avec Parquet
- ✅ Pas de dépendance externe (GitHub)
- ✅ Cache incrémental (only new data)

### Implementation Phases

**Phase 1: Cache Simple** (2 jours)
- JSON cache basique
- Détection lors du scraping
- 5x plus rapide

**Phase 2: Cache Parquet** (3 jours)
- Migration vers Parquet
- Optimisations columnar
- 20x plus rapide

**Phase 3: Cache Distribué** (optionnel)
- Upload vers S3/GitHub
- CDN pour partage communautaire
- Comme Jiliac mais modernisé