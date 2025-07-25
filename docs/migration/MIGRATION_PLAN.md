# 🏗️ Plan de Migration Manalytics - Architecture Professionnelle

**Date de création** : 25 juillet 2025  
**Architecte** : Claude (Anthropic)  
**Version** : 1.0.0  
**Status** : 🔴 En planification

## 📋 Vue d'ensemble

Ce document détaille le plan complet de migration du projet Manalytics vers une architecture professionnelle de niveau entreprise. Chaque étape est conçue pour être réversible, testable et non-destructive.

## ⚠️ Principes Directeurs

1. **ZÉRO PERTE DE DONNÉES** : Aucun fichier supprimé sans backup complet
2. **TRAÇABILITÉ TOTALE** : Chaque action documentée avec timestamp
3. **RÉVERSIBILITÉ** : Script de rollback pour chaque migration
4. **TESTS CONTINUS** : Validation après chaque étape
5. **MIGRATION PROGRESSIVE** : Petites étapes atomiques

## 📊 État Actuel du Projet

- **Fichiers Python** : 150+ fichiers
- **Structure** : Mixte (racine + src/ + scrapers/)
- **Données** : 72 fichiers JSON (MTGO + Melee)
- **Tests** : Désorganisés, pas de CI/CD
- **Documentation** : Fragmentée
- **Secrets** : Dans des fichiers JSON (à sécuriser)

## 🎯 Objectifs de la Migration

1. Structure standardisée Python moderne
2. Sécurité renforcée (secrets, .env)
3. CI/CD avec GitHub Actions
4. Tests automatisés (unit + integration)
5. Documentation auto-générée
6. Installation en 1 commande

## 📅 Phases de Migration

### 🔍 PHASE 1 : AUDIT & PRÉPARATION (Jour 1)

#### 1.1 Audit Complet
```bash
# Actions:
- Scanner tous les fichiers (.py, .json, .md, etc.)
- Créer PROJECT_AUDIT.json avec:
  - Liste complète des fichiers
  - Tailles et dates de modification
  - Dépendances identifiées
  - Doublons détectés
  - Secrets exposés
```

#### 1.2 Backup Initial
```bash
# Créer backup complet avec versioning
tar -czf backups/manalytics_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

#### 1.3 Initialisation Git
```bash
# Créer branches de travail
git checkout -b migration/professional-structure
git tag pre-migration-v1.0.0
```

### 🔒 PHASE 2 : SÉCURISATION (Jour 1-2)

#### 2.1 Gestion des Secrets
```bash
# Actions:
1. Créer .env.example avec toutes les variables
2. Migrer api_credentials/*.json vers .env
3. Mettre à jour .gitignore complet
4. Supprimer secrets de l'historique Git (BFG Repo-Cleaner)
5. Créer scripts/setup_credentials.py pour aide config
```

#### 2.2 Permissions et Accès
```bash
# Sécuriser les dossiers sensibles
chmod 700 api_credentials/
chmod 600 .env
```

### 🏗️ PHASE 3 : RESTRUCTURATION CORE (Jour 3-5)

#### 3.1 Création Structure Cible
```bash
mkdir -p src/manalytics/{scrapers/{melee,mtgo},auth,models,utils,config}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs/{api,guides,architecture}
mkdir -p scripts/migrations
mkdir -p .github/workflows
mkdir -p configs
```

#### 3.2 Migration des Scrapers
```
# Ordre de migration (critique → moins critique):
1. scrape_melee_working_v2.py → src/manalytics/scrapers/melee/scraper.py
2. scrape_mtgo_tournaments_enhanced.py → src/manalytics/scrapers/mtgo/scraper.py
3. scrapers/mtgo_scraper_enhanced.py → src/manalytics/scrapers/mtgo/enhanced.py
4. scrapers/models/* → src/manalytics/models/
```

#### 3.3 Migration des Utilitaires
```
# Consolidation et refactoring:
- src/utils/* → src/manalytics/utils/
- config/* → src/manalytics/config/
- database/* → src/manalytics/database/
```

### 🔧 PHASE 4 : MODERNISATION (Jour 6-7)

#### 4.1 Configuration Python Moderne
```toml
# Créer pyproject.toml avec:
- Métadonnées projet
- Dépendances (requirements.txt intégré)
- Configuration outils (black, isort, pytest)
- Scripts entry points
```

#### 4.2 Makefile Professionnel
```makefile
# Commandes standards:
install:    # Installation complète
test:       # Lancer tous les tests
lint:       # Vérifier le style
format:     # Formater le code
run:        # Lancer l'application
clean:      # Nettoyer les artifacts
docker:     # Build containers
```

#### 4.3 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml:
- Black (formatage)
- isort (imports)
- flake8 (linting)
- mypy (types)
- security checks
```

### 🧪 PHASE 5 : TESTS & QUALITÉ (Jour 8-9)

#### 5.1 Tests Unitaires
```
# Structure tests:
tests/
├── unit/
│   ├── test_scrapers/
│   ├── test_models/
│   └── test_utils/
├── integration/
│   └── test_pipeline.py
└── conftest.py  # Fixtures pytest
```

#### 5.2 CI/CD Pipeline
```yaml
# .github/workflows/ci.yml:
- Tests sur Python 3.9, 3.10, 3.11
- Linting et formatting check
- Security scan
- Coverage report
- Auto-deploy docs
```

### 📚 PHASE 6 : DOCUMENTATION (Jour 10)

#### 6.1 Documentation Sphinx
```
docs/
├── conf.py           # Config Sphinx
├── index.rst         # Page principale
├── api/             # API auto-générée
├── guides/          # Guides utilisateur
└── _build/          # HTML généré
```

#### 6.2 README Professionnel
- Badges (CI, coverage, version)
- Installation rapide
- Usage examples
- Architecture overview
- Contributing guidelines

### ✅ PHASE 7 : VALIDATION FINALE (Jour 11)

#### 7.1 Checklist de Validation
- [ ] `make install` fonctionne en 1 commande
- [ ] `make test` - 100% des tests passent
- [ ] `make lint` - 0 erreur
- [ ] Docker compose up fonctionne
- [ ] Documentation générée automatiquement
- [ ] Rollback script testé

#### 7.2 Performance Testing
- Benchmark scrapers avant/après
- Memory profiling
- Optimisations identifiées

## 🔄 Plan de Rollback

### Script de Rollback Automatique
```bash
#!/bin/bash
# ROLLBACK.sh
# Restaure l'état pré-migration

echo "🔄 Début du rollback..."
git checkout pre-migration-v1.0.0
tar -xzf backups/manalytics_backup_YYYYMMDD.tar.gz
echo "✅ Rollback terminé"
```

### Points de Sauvegarde
- Après chaque phase : git tag + backup
- Logs détaillés dans MIGRATION_LOG.md
- Tests de rollback à chaque étape

## 📊 Métriques de Succès

1. **Code Quality** : Coverage > 80%, 0 erreurs lint
2. **Performance** : Pas de régression vs baseline
3. **Sécurité** : 0 secrets exposés, scan OK
4. **Documentation** : 100% fonctions documentées
5. **Installation** : < 2 minutes setup complet

## 🚀 Planning Détaillé

| Phase | Durée | Risque | Priorité |
|-------|-------|--------|----------|
| Audit | 1 jour | Faible | Critique |
| Sécurisation | 2 jours | Moyen | Critique |
| Restructuration | 3 jours | Élevé | Haute |
| Modernisation | 2 jours | Moyen | Haute |
| Tests | 2 jours | Faible | Moyenne |
| Documentation | 1 jour | Faible | Moyenne |
| Validation | 1 jour | Faible | Haute |

**Total estimé** : 12 jours

## ⚠️ Risques Identifiés

1. **Casse des imports** → Solution : Script de mise à jour automatique
2. **Perte de données** → Solution : Backups multiples
3. **Régression fonctionnelle** → Solution : Tests exhaustifs
4. **Conflits Git** → Solution : Branches isolées

## 📝 Notes de l'Architecte

Ce plan assure une migration progressive et sécurisée vers une architecture professionnelle. Chaque étape est conçue pour minimiser les risques et maximiser la traçabilité. La clé du succès réside dans l'exécution méthodique et la validation continue.

---
*Document créé le 25/07/2025 - À valider avant exécution*