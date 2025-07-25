# 🏗️ Structure Idéale du Projet Manalytics

## 📋 Vue d'Ensemble de la Nouvelle Structure

```
Manalytics/
├── 📁 src/                      # Code source principal
├── 📁 scripts/                  # Scripts d'exécution et utilitaires
├── 📁 data/                     # Données (scrapées et processées)
├── 📁 database/                 # Schémas et migrations DB
├── 📁 config/                   # Configuration
├── 📁 tests/                    # Tests organisés
├── 📁 docs/                     # Documentation
├── 📁 tools/                    # Outils de développement
├── 📁 archive/                  # Code obsolète
├── 📁 api_credentials/          # Credentials (dans .gitignore)
├── 📄 setup.py                  # Installation Python
├── 📄 requirements.txt          # Dépendances
├── 📄 docker-compose.yml        # Docker
├── 📄 Dockerfile                # Image Docker
├── 📄 .env.example              # Template environnement
├── 📄 README.md                 # Documentation principale
└── 📄 CLAUDE.md                 # Instructions pour Claude
```

## 📁 Structure Détaillée

### 1. `src/` - Code Source Principal
```
src/
├── scrapers/
│   ├── production/              # ✅ Scrapers en production
│   │   ├── __init__.py
│   │   ├── melee_scraper.py    # scrape_melee_working_v2.py renommé
│   │   └── mtgo_scraper.py     # scrape_mtgo_tournaments_enhanced.py renommé
│   │
│   ├── base/                    # Classes de base
│   │   ├── __init__.py
│   │   └── base_scraper.py     # Interface commune
│   │
│   └── models/                  # Modèles de données
│       ├── __init__.py
│       ├── base_model.py        # De scrapers/models/
│       └── melee_model.py       # De scrapers/models/
│
├── parsers/                     # Parsing et validation
│   ├── __init__.py
│   ├── archetype_engine.py     # Détection d'archétypes
│   ├── decklist_parser.py      # Validation des decks
│   └── color_identity.py       # Analyse des couleurs
│
├── analyzers/                   # Analyse de données
│   ├── __init__.py
│   ├── meta_analyzer.py        # Analyse du métagame
│   ├── matchup_calculator.py   # Calcul des matchups
│   └── tournament_analyzer.py  # Analyse des tournois
│
├── api/                         # API REST
│   ├── __init__.py
│   ├── app.py                  # FastAPI app
│   ├── auth.py                 # Authentication JWT
│   ├── models.py               # Modèles Pydantic
│   └── routes/                 # Endpoints
│       ├── __init__.py
│       ├── auth.py
│       ├── decks.py
│       ├── analysis.py
│       └── visualizations.py
│
├── visualizations/              # Génération de graphiques
│   ├── __init__.py
│   ├── matchup_heatmap.py
│   └── meta_charts.py
│
└── utils/                       # Utilitaires
    ├── __init__.py
    ├── data_loader.py          # Chargement des données
    ├── cache_manager.py        # Gestion Redis
    ├── scryfall_client.py      # API Scryfall
    └── card_utils.py           # Utilitaires cartes
```

### 2. `scripts/` - Scripts d'Exécution
```
scripts/
├── scraping/                    # Scripts de scraping
│   ├── scrape_mtgo.py          # Wrapper simple pour MTGO
│   ├── scrape_melee.py         # Wrapper simple pour Melee
│   └── scrape_all.py           # Scraper tous les formats
│
├── pipeline/                    # Pipeline de données
│   ├── run_pipeline.py         # Pipeline complet
│   └── run_analysis.py         # Analyse seule
│
├── maintenance/                 # Maintenance et setup
│   ├── fetch_archetype_rules.py
│   ├── migrate_database.py
│   ├── init_alembic.py
│   └── healthcheck.py
│
└── development/                 # Scripts de dev
    ├── test_auth_melee.py      # Test d'auth
    ├── validate_setup.py
    └── insert_test_data.py
```

### 3. `data/` - Données
```
data/
├── raw/                         # Données brutes scrapées
│   ├── mtgo/
│   │   ├── standard/
│   │   ├── modern/
│   │   ├── legacy/
│   │   └── .tracking/          # Fichiers de tracking
│   │
│   └── melee/
│       ├── standard/
│       ├── modern/
│       └── .tracking/
│
├── processed/                   # Données processées
│   └── {format}/
│       └── {date}/
│
├── cache/                       # Cache temporaire
├── exports/                     # Exports (CSV, JSON)
└── visualizations/              # Graphiques générés
```

### 4. `tests/` - Tests Organisés
```
tests/
├── unit/                        # Tests unitaires
│   ├── scrapers/
│   ├── parsers/
│   └── analyzers/
│
├── integration/                 # Tests d'intégration
│   ├── test_pipeline.py
│   └── test_api.py
│
├── fixtures/                    # Données de test
│   ├── sample_tournaments/
│   └── sample_decks/
│
└── e2e/                        # Tests end-to-end
    └── test_full_flow.py
```

### 5. `tools/` - Outils de Développement
```
tools/
├── auth/                        # Outils d'authentification
│   ├── test_melee_auth.py
│   └── refresh_cookies.py
│
├── debug/                       # Outils de debug
│   └── analyze_tournament.py
│
└── migration/                   # Scripts de migration
    ├── reorganize_project.py
    └── cleanup_obsolete.py
```

### 6. `archive/` - Code Obsolète
```
archive/
├── old_scrapers/               # Anciennes versions
├── old_tests/                  # Anciens tests
├── experiments/                # Code expérimental
└── README.md                   # Explication du contenu
```

### 7. `docs/` - Documentation
```
docs/
├── guides/                     # Guides d'utilisation
│   ├── SCRAPING_GUIDE.md
│   ├── API_GUIDE.md
│   └── DEVELOPMENT.md
│
├── architecture/               # Documentation technique
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── DATA_FLOW.md
│
└── references/                 # Références
    ├── MELEE_SCRAPING_GUIDE.md
    ├── SCRAPING_BEST_PRACTICES.md
    └── TROUBLESHOOTING.md
```

## 🔄 Plan de Migration

### Phase 1 : Création de la Structure
```bash
# Créer les dossiers principaux
mkdir -p src/scrapers/{production,base,models}
mkdir -p scripts/{scraping,pipeline,maintenance,development}
mkdir -p tests/{unit,integration,fixtures,e2e}
mkdir -p tools/{auth,debug,migration}
mkdir -p archive/{old_scrapers,old_tests,experiments}
mkdir -p docs/{guides,architecture,references}
```

### Phase 2 : Migration des Fichiers Critiques
```bash
# Scrapers en production
cp scrape_melee_working_v2.py src/scrapers/production/melee_scraper.py
cp scrape_mtgo_tournaments_enhanced.py src/scrapers/production/mtgo_scraper.py

# Modèles
cp scrapers/models/*.py src/scrapers/models/

# Utils
# Déjà au bon endroit : src/utils/

# Scripts
mv scripts/run_pipeline.py scripts/pipeline/
mv scripts/fetch_archetype_rules.py scripts/maintenance/
```

### Phase 3 : Archivage des Obsolètes
```bash
# Déplacer tous les tests obsolètes
mv test_melee_*.py archive/old_tests/
mv debug_*.py archive/old_tests/
mv test_*.py archive/old_tests/

# Déplacer les anciens scrapers
mv scrape_melee_tournaments_*.py archive/old_scrapers/
mv scrape_mtgo_tournaments.py archive/old_scrapers/
```

### Phase 4 : Mise à Jour des Imports
- Mettre à jour tous les imports dans les fichiers conservés
- Créer des __init__.py appropriés
- Tester que tout fonctionne

## ✅ Avantages de cette Structure

1. **Clarté** : Chaque fichier a sa place logique
2. **Maintenabilité** : Facile de trouver et modifier
3. **Scalabilité** : Facile d'ajouter de nouveaux composants
4. **Testabilité** : Tests organisés par type
5. **Propreté** : Séparation claire prod/dev/obsolète

## 🚀 Commandes Post-Migration

```bash
# Scraper MTGO
python -m scripts.scraping.scrape_mtgo --format standard --days 7

# Scraper Melee
python -m scripts.scraping.scrape_melee --format standard --days 7

# Pipeline complet
python -m scripts.pipeline.run_pipeline --format standard

# Tests
pytest tests/
```