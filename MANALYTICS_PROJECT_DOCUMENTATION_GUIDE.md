# 📚 Guide des Documents du Projet Manalytics

## 🎯 Objectif de ce Guide

Ce document sert de guide central pour tous les documents liés au projet Manalytics. Il explique quels documents doivent être consultés et remplis à chaque étape du projet, assurant ainsi une compréhension complète et une documentation cohérente.

## 📋 Documents Principaux à Consulter

### 1. Documentation de Référence

| Document | Description | Statut | Action Requise |
|----------|-------------|--------|----------------|
| **[HANDOFF_SUMMARY.md](HANDOFF_SUMMARY.md)** | **DOCUMENT PRINCIPAL** - Résumé complet du projet, état actuel, et prochaines étapes | ✅ À jour | Consulter en priorité |
| [ECOSYSTEM_REFERENCE_ULTIMATE.md](ECOSYSTEM_REFERENCE_ULTIMATE.md) | Référence complète de l'écosystème original multi-repositories | ✅ À jour | Consulter pour comprendre le workflow original |
| [RULES_OF_MANALYTICS.md](RULES_OF_MANALYTICS.md) | Règles fondamentales du projet et contraintes techniques | ✅ À jour | Consulter avant toute modification |

### 2. Spécification du Projet

| Document | Description | Statut | Action Requise |
|----------|-------------|--------|----------------|
| [.kiro/specs/manalytics-system-consolidation/requirements.md](.kiro/specs/manalytics-system-consolidation/requirements.md) | Exigences détaillées du projet | ✅ À jour | Consulter pour comprendre les objectifs |
| [.kiro/specs/manalytics-system-consolidation/design.md](.kiro/specs/manalytics-system-consolidation/design.md) | Architecture et conception du système | ✅ À jour | Consulter pour comprendre l'architecture |
| [.kiro/specs/manalytics-system-consolidation/tasks.md](.kiro/specs/manalytics-system-consolidation/tasks.md) | Plan d'implémentation avec tâches | ✅ Mis à jour | **Consulter pour voir les tâches restantes** |

### 3. Rapports d'Analyse et Problèmes

| Document | Description | Statut | Action Requise |
|----------|-------------|--------|----------------|
| [PROBLEMATIQUE_PRIORITAIRE_A_REGLE.md](PROBLEMATIQUE_PRIORITAIRE_A_REGLE.md) | Liste des problèmes critiques à résoudre | ✅ À jour | Consulter pour les problèmes prioritaires |
| [LEAGUE_ANALYSIS_FIX.md](LEAGUE_ANALYSIS_FIX.md) | Analyse du problème "max() iterable empty" | ✅ À jour | Consulter pour résoudre ce bug spécifique |
| [RAPPORT_INTEGRATION_TOP_5_0.md](RAPPORT_INTEGRATION_TOP_5_0.md) | Rapport sur l'intégration des données League 5-0 | ✅ À jour | Consulter pour comprendre ce problème |

## 📝 Documents à Remplir/Mettre à Jour

### 1. Suivi des Modifications

| Document | Description | Quand Mettre à Jour | Comment Remplir |
|----------|-------------|---------------------|-----------------|
| **[MODIFICATION_TRACKER.md](MODIFICATION_TRACKER.md)** | Suivi de toutes les modifications | **À chaque modification** | Format: `[Date] - [Type] - [Description] - [Fichiers modifiés]` |
| [diagnostic_report_YYYYMMDD_HHMMSS.json](diagnostic_report_20250715_202838.json) | Rapport de diagnostic automatique | Après chaque test majeur | Généré automatiquement, vérifier les erreurs |
| [performance_report_YYYYMMDD_HHMMSS.json](performance_report_20250715_203005.json) | Rapport de performance | Après optimisations | Généré automatiquement, vérifier les métriques |

### 2. Documentation Technique

| Document | Description | Quand Mettre à Jour | Comment Remplir |
|----------|-------------|---------------------|-----------------|
| [docs/architecture/README.md](docs/architecture/README.md) | Documentation d'architecture | Après changements architecturaux | Documenter les décisions avec justifications |
| [docs/api/README.md](docs/api/README.md) | Documentation API | Après modifications API | Documenter endpoints, paramètres, exemples |
| [docs/troubleshooting/README.md](docs/troubleshooting/README.md) | Guide de dépannage | Après résolution de bugs | Documenter problème, cause, solution |

## 🚀 Workflow de Développement

### Phase 1: Préparation et Analyse
1. Consulter **HANDOFF_SUMMARY.md** pour comprendre l'état actuel
2. Consulter **PROBLEMATIQUE_PRIORITAIRE_A_REGLE.md** pour les problèmes critiques
3. Consulter **.kiro/specs/manalytics-system-consolidation/tasks.md** pour les tâches restantes

### Phase 2: Implémentation
1. Travailler sur les tâches Step 3 (Visualization) restantes
2. Résoudre les problèmes critiques identifiés
3. Mettre à jour **MODIFICATION_TRACKER.md** à chaque modification

### Phase 3: Validation et Documentation
1. Exécuter les tests complets (`python run_full_pipeline.py`)
2. Générer les rapports de diagnostic et performance
3. Mettre à jour la documentation technique pertinente

## 🔍 État Actuel du Projet

- ✅ **Step 1: Data Collection** - **TERMINÉ**
- ✅ **Step 2: Data Treatment** - **TERMINÉ** (20 juillet 2025)
- ⚠️ **Step 3: Visualization** - **EN COURS**

### Problèmes Critiques Restants
1. **Erreur Leagues Analysis** : `max() iterable argument is empty`
2. **Warnings ArchetypeEngine** : `Unknown condition type: twoormoreinmainboard`
3. **API Melee 403** : 0 tournois récupérés, problème d'authentification

## 📞 Ressources et Contacts

- **Repository GitHub** : https://github.com/gbordes77/Manalytics
- **Documentation Originale** : Voir repositories listés dans ECOSYSTEM_REFERENCE_ULTIMATE.md
- **Commandes Utiles** : Voir section "Commandes Utiles" dans HANDOFF_SUMMARY.md

---

*Document créé le 21 juillet 2025*
*Dernière mise à jour: 21 juillet 2025*
