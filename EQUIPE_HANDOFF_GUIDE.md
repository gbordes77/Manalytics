# 📋 GUIDE DE PASSATION MANALYTICS - ÉQUIPE SORTANTE

## 🎯 MODIFICATIONS RÉCENTES CRITIQUES (À DOCUMENTER EN PRIORITÉ)

### ✅ Changements de cette session (Commits: 87d4b37, 9fc7958, a95eb9d)
1. **Titres sans dates** - `src/python/visualizations/metagame_charts.py`
2. **Matchup matrix agrandi 50%** - `src/orchestrator.py` + `src/python/visualizations/matchup_matrix.py`
3. **Filtre MTGO corrigé** - `src/orchestrator.py` (inclut tout sauf 5-0 leagues)
4. **Couleurs matchup matrix** - Rouge-Blanc-Vert pour lisibilité

### 📋 Tracker des modifications
- **OBLIGATOIRE** : Mettre à jour `docs/MODIFICATION_TRACKER.md`
- Documenter chaque commit avec instructions de rollback
- Ajouter entry "Claude_2025-01-14_15-32" si pas fait

---

## 📚 1. FICHIERS CRITIQUES (OBLIGATOIRE - Dans l'ordre)

### 🔥 Urgence Absolue
- `docs/MODIFICATION_TRACKER.md` - **État des changements récents + rollback**
- `README.md` - Version, fonctionnalités, état actuel
- `HANDOFF_SUMMARY.md` - Statut de livraison actuel
- `docs/ALIQUANTO3_TO_MANALYTICS_MAPPING.md` - **Mapping R→Python (18 fonctionnalités)**

### 📊 Documentation Projet
- `CHANGELOG.md` - Tous les changements récents
- `ROADMAP.md` - Jalons complétés et priorités suivantes
- `config/no_mock_policy.py` - **Politique anti-données-fake (CRITIQUE)**
- `enforcement/strict_mode.py` - **Enforcement des vraies données**

---

## 🔧 2. DOCUMENTATION TECHNIQUE (ESSENTIEL)

### 🏗️ Architecture & Code
- `docs/ARCHITECTURE_QUICKREAD.md` - Changements architecturaux
- `docs/IMPLEMENTATION_SUMMARY_v0.X.X.md` - Résumé de version
- `docs/API_REFERENCE_ADVANCED_ANALYTICS.md` - Documentation des fonctions
- `docs/ORCHESTRATOR_INTEGRATION.md` - Détails d'intégration

### ⚙️ Système & Configuration
- `src/orchestrator.py` - **4042 lignes - CŒUR DU SYSTÈME**
- `config/settings.py` - Configuration principale
- `config/logging.yaml` - Configuration logs

---

## 👥 3. GUIDES UTILISATEUR/DÉVELOPPEUR (IMPORTANT)

### 🚀 Onboarding
- `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md` - Instructions d'onboarding
- `docs/SETUP_DEV.md` - Instructions setup développement
- `docs/TEAM_HANDOFF_CHECKLIST.md` - **Checklist complète**

### 📖 Utilisation
- `docs/USER_GUIDE_ADVANCED_ANALYTICS.md` - Exemples d'utilisation
- `docs/ADVANCED_ANALYTICS.md` - Documentation des fonctionnalités
- `docs/ANALYSIS_TEMPLATE_SPECIFICATION.md` - Spécifications templates

---

## 📋 4. DOCUMENTATION PROCESSUS (MAINTENANCE)

- `docs/ONBOARDING_CHECKLIST.md` - Checklist mise à jour
- `docs/GUIDE_NOUVELLE_EQUIPE_2025.md` - Changements récents
- `docs/PROMPT_FINAL_EQUIPE.md` - Instructions finales

---

# 📚 ÉQUIPE ENTRANTE - ORDRE DE LECTURE MANALYTICS

## 🎯 Phase 1: Contexte Critique (Jour 1 - 3h)

### 🔥 URGENT - Compréhension Projet (45 min)
1. `README.md` - Vue d'ensemble du projet
2. `docs/MODIFICATION_TRACKER.md` - **DERNIERS CHANGEMENTS + ROLLBACK**
3. `HANDOFF_SUMMARY.md` - Ce qui vient d'être livré
4. `config/no_mock_policy.py` - **POLITIQUE ANTI-FAKE DATA (CRITIQUE)**

### 🏗️ Fondations Manalytics (90 min)
1. `docs/ALIQUANTO3_TO_MANALYTICS_MAPPING.md` - **Contexte R→Python**
2. `docs/ARCHITECTURE_QUICKREAD.md` - Design système
3. `src/orchestrator.py` (lignes 1-50) - Point d'entrée principal
4. `docs/IMPLEMENTATION_SUMMARY_v0.X.X.md` - Détails implémentation

### ⚙️ Setup & Premier Test (45 min)
1. `docs/SETUP_DEV.md` - Setup environnement
2. Test: `python run_full_pipeline.py --start-date 2025-05-08 --end-date 2025-06-09 --format Standard`
3. Vérifier: Analyses générées dans `Analyses/`

---

## 🔧 Phase 2: Technique Approfondie (Jour 2 - 4h)

### 📊 Système d'Analyse (120 min)
1. `src/python/analytics/advanced_metagame_analyzer.py` - Moteur analytique
2. `src/python/classifier/advanced_archetype_classifier.py` - Classification
3. `src/python/visualizations/` - Système de visualisation
4. `docs/API_REFERENCE_ADVANCED_ANALYTICS.md` - API complète

### 🎨 Interface & Génération (120 min)
1. `src/orchestrator.py` (sections dashboard) - Génération HTML
2. Templates et CSS embarqués
3. Système de fichiers de sortie
4. `docs/ANALYSIS_TEMPLATE_SPECIFICATION.md` - Spécifications

---

## 🚀 Phase 3: Maîtrise & Production (Jour 3 - 2h)

### 🔍 Tests & Validation (60 min)
1. Tests d'intégration existants
2. Validation données réelles vs. mocks
3. Performance et monitoring

### 📈 Évolution & Maintenance (60 min)
1. `ROADMAP.md` - Prochaines étapes
2. `docs/USER_GUIDE_ADVANCED_ANALYTICS.md` - Cas d'usage
3. Stratégie de développement

---

## ⚠️ POINTS CRITIQUES MANALYTICS

### 🚨 ABSOLUMENT CRITIQUE
- **JAMAIS de données mock/fake/test** - Politique enforcement stricte
- **Tout changement doit être dans le CODE SOURCE** (pas les fichiers générés)
- **Commits récents**: 87d4b37, 9fc7958, a95eb9d - à comprendre absolument

### 🔒 Écosystème
- **4 repos GitHub**: R-Meta-Analysis, r_mtgo_modern_analysis, Shiny_mtg_meta_analysis, MTGOCardDiversity
- **Transformation R→Python** de l'écosystème Aliquanto3
- **18 fonctionnalités R** mappées vers Python

### 📊 Données & Sources
- **Sources MTGO**: Challenge + tournois (PAS de 5-0 leagues)
- **Filtrage automatique** des duplicatas
- **Validation stricte** des archétypes et couleurs

---

## 🆘 EN CAS DE PROBLÈME

### 🔄 Rollback des modifications récentes
```bash
git revert a95eb9d  # Couleurs matchup matrix
git revert 9fc7958  # Taille matchup matrix  
git revert 87d4b37  # Titres + filtres MTGO
```

### 📞 Contacts & Ressources
- Backup tag: `backup-auto-backup-20250714-0954`
- Documentation tracking: `docs/MODIFICATION_TRACKER.md`
- Tests: `python run_full_pipeline.py --help` 