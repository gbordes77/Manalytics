# 🧹 Plan de Réorganisation des Scripts

## 📊 Audit Initial : 54 scripts dans /scripts/

### Catégories identifiées :

#### 1. **Visualisations** (À MIGRER vers src/manalytics/visualizers/)
- create_archetype_visualization*.py (8 fichiers!)
- create_basic_visualization.py
- create_winrate_mustache_graph.py

#### 2. **Analyses** (À MIGRER vers src/manalytics/analyzers/)
- analyze_*.py (7 fichiers)
- compare_*.py (2 fichiers)
- investigate_jiliac_differences.py

#### 3. **Pipeline/Orchestration** (À MIGRER vers src/manalytics/)
- run_pipeline*.py (3 fichiers)
- scrape_all_platforms.py
- process_all_standard_data.py

#### 4. **Utilities One-Shot** (À GARDER dans /scripts/)
- validate_*.py
- test_*.py
- setup_*.py
- healthcheck.py
- league_protection.py

#### 5. **Database/Migration** (À MIGRER vers src/manalytics/database/)
- migrate_*.py
- init_alembic.py
- insert_test_data.py

#### 6. **Reports** (À SUPPRIMER ou archiver)
- final_report.py
- phase2_complete_report.py
- show_cache_stats.py

## 🎯 Structure Cible

```
src/manalytics/
├── visualizers/
│   ├── __init__.py
│   ├── archetype_charts.py     # Fusionner tous les create_archetype_*
│   ├── winrate_mustache.py     # Nouveau, basé sur Jiliac
│   ├── tier_scatter.py         # À créer
│   └── performance_scatter.py  # À créer
├── analyzers/
│   ├── __init__.py
│   ├── competitive_filter.py   # analyze_competitive_only.py
│   ├── jiliac_matcher.py       # analyze_like_jiliac.py
│   └── meta_analyzer.py        # Fusion des analyze_*
├── pipeline/
│   ├── __init__.py
│   ├── runner.py               # run_pipeline.py principal
│   └── scraper_orchestrator.py # scrape_all_platforms.py
└── database/
    ├── __init__.py
    └── migrations.py           # Tous les migrate_*

scripts/                        # Garder SEULEMENT :
├── validate_*.py               # One-shot validations
├── test_*.py                   # Tests manuels
├── setup_*.py                  # Setup utilities
└── healthcheck.py              # Monitoring
```

## 📋 Plan d'Action

### Phase 1 : Créer la structure (15 min)
1. Créer les dossiers manquants dans src/manalytics/
2. Ajouter les __init__.py

### Phase 2 : Migration des visualisations (2h)
1. Fusionner les 8 variantes de create_archetype_visualization
2. Créer une classe ArchetypeVisualizer propre
3. Intégrer avec le CLI manalytics

### Phase 3 : Migration des analyzers (1h)
1. Créer MetaAnalyzer unifié
2. Intégrer CompetitiveFilter
3. Adapter JiliacMatcher

### Phase 4 : Nettoyage (30 min)
1. Supprimer les doublons
2. Archiver les vieux reports
3. Mettre à jour les imports

### Phase 5 : Documentation (30 min)
1. Mettre à jour le README
2. Documenter la nouvelle structure
3. Créer un guide de migration

## ⚠️ Fichiers Critiques à NE PAS TOUCHER
- league_protection.py (protection leagues)
- validate_against_decklistcache.py (validation importante)
- process_all_standard_data.py (utilisé actuellement)

## 🎉 Résultat Attendu
- De 54 scripts → ~10 scripts utilitaires
- Code organisé par responsabilité
- Intégration complète avec le CLI
- Architecture alignée avec Jiliac