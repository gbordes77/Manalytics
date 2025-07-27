# 📁 Scripts Directory

Ce dossier contient uniquement les **scripts utilitaires one-shot** qui ne font pas partie du code principal.

## ✅ Scripts Conservés

### 🔧 Configuration & Setup
- `setup_credentials.py` - Configure les credentials API
- `setup_test_archetypes.py` - Setup pour tests
- `init_alembic.py` - Initialise les migrations DB

### 🧪 Tests & Validation
- `test_*.py` - Tests manuels divers
- `validate_*.py` - Scripts de validation
- `healthcheck.py` - Vérification santé système

### 🛡️ Protection & Maintenance
- `league_protection.py` - Protection contre les leagues
- `clean_git_secrets.sh` - Nettoyage secrets Git
- `audit_project.py` - Audit du projet

### 📊 Processing (À MIGRER)
- `process_all_standard_data.py` - Processing cache
- `scrape_all_platforms.py` - Scraping orchestration
- `run_pipeline*.py` - Pipeline runners

### 🗄️ Database
- `migrate_*.py` - Scripts de migration
- `manage_users.py` - Gestion utilisateurs

## ❌ Ne PAS Ajouter Ici
- Code réutilisable → `src/manalytics/`
- Visualisations → `src/manalytics/visualizers/`
- Analyses → `src/manalytics/analyzers/`
- API/CLI → `src/manalytics/`

## 📦 Archives
Les anciens scripts sont dans `_archive_2025_07_27/` pour référence.