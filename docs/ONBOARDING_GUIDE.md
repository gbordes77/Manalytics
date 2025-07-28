# 🎓 Guide d'Intégration Manalytics - Parcours du Nouveau Développeur

## 🚀 Bienvenue sur Manalytics !

Ce guide vous accompagne étape par étape pour comprendre le projet et devenir opérationnel rapidement.

## 📚 Parcours de Lecture Recommandé

### 🔴 ÉTAPE 1 : Comprendre le Projet (30 min)

1. **[CLAUDE.md](../CLAUDE.md)** ⭐ **À LIRE EN PREMIER**
   - Vue d'ensemble du projet
   - Objectifs et philosophie
   - Règles critiques du projet
   - État actuel et roadmap

2. **[docs/PROJECT_COMPLETE_DOCUMENTATION.md](./PROJECT_COMPLETE_DOCUMENTATION.md)** 📖
   - Documentation complète du projet
   - Architecture générale
   - Composants principaux
   - Workflow de développement

3. **[docs/MANALYTICS_COMPLETE_ARCHITECTURE.html](./MANALYTICS_COMPLETE_ARCHITECTURE.html)** 🏗️
   - **Ouvrir dans un navigateur**
   - Diagramme interactif du pipeline complet
   - Vue détaillée de chaque phase
   - Scripts et leurs rôles

### 🟡 ÉTAPE 2 : Comprendre les Données (45 min)

4. **[docs/DATA_FLOW_VISUALIZATION.html](./DATA_FLOW_VISUALIZATION.html)** 🔄
   - **Ouvrir dans un navigateur**
   - Flux de données interactif
   - Comment les données circulent dans le système

5. **[docs/FILE_DISCOVERY_PROCESS.html](./FILE_DISCOVERY_PROCESS.html)** 🔍
   - **Ouvrir dans un navigateur**
   - Comment le système trouve et traite les fichiers
   - Logique de découverte automatique

6. **[data/cache/standard_analysis_no_leagues.html](../data/cache/standard_analysis_no_leagues.html)** 📊
   - **VISUALISATION DE RÉFÉRENCE**
   - Exemple concret du résultat final
   - Standards visuels à respecter

### 🟢 ÉTAPE 3 : Maîtriser les Outils (1h)

7. **[docs/SCRAPERS_COMPLETE_GUIDE.md](./SCRAPERS_COMPLETE_GUIDE.md)** 🕷️
   - Guide complet des scrapers
   - Utilisation du scraper unifié
   - Formats supportés
   - Troubleshooting

8. **[docs/CACHE_SYSTEM_IMPLEMENTATION.md](./CACHE_SYSTEM_IMPLEMENTATION.md)** 💾
   - Architecture du système de cache
   - SQLite + JSON hybride
   - Performance et optimisations

9. **[docs/VISUALIZATION_TEMPLATE_REFERENCE.md](./VISUALIZATION_TEMPLATE_REFERENCE.md)** 🎨
   - Standards visuels OBLIGATOIRES
   - Templates et exemples
   - Règles de couleurs MTG

### 🔵 ÉTAPE 4 : Intégration Avancée (Optionnel)

10. **[docs/JILIAC_INTEGRATION_SCHEMAS.html](./JILIAC_INTEGRATION_SCHEMAS.html)** 🔗
    - Intégration avec le pipeline communautaire
    - MTGO Listener (Phase 4)
    - Données de matchups

11. **[docs/guides/DEVELOPMENT.md](./guides/DEVELOPMENT.md)** 💻
    - Guide de développement
    - Standards de code
    - Tests et CI/CD

## 🎯 Quick Start : Votre Première Analyse

Après avoir lu les documents essentiels (1-3), voici comment faire votre première analyse :

```bash
# 1. Installer les dépendances
make install-dev

# 2. Configurer Melee (si nécessaire)
mkdir api_credentials
# Créer api_credentials/melee_login.json avec vos credentials

# 3. Scraper les données Standard des 7 derniers jours
python scrape_all.py --format standard --days 7

# 4. Processer dans le cache
python scripts/process_all_standard_data.py

# 5. Générer une visualisation
python visualize_standard.py

# 6. Ouvrir le résultat
open data/cache/standard_analysis_no_leagues.html
```

## 📁 Scripts à Utiliser vs Scripts Obsolètes

### ✅ SCRIPTS ACTUELS (À UTILISER)

#### Scrapers
- **`scrape_all.py`** ⭐ - Scraper unifié (RECOMMANDÉ)
- `scrape_mtgo_flexible.py` - MTGO seul (cas spécifiques)
- `scrape_melee_flexible.py` - Melee seul (cas spécifiques)

#### Processing & Analyse
- **`scripts/process_all_standard_data.py`** - Processeur principal
- **`analyze_july_1_21.py`** - Analyse juillet (comparaison Jiliac)
- **`analyze_july_with_cache_and_listener.py`** - Analyse avec matchups
- **`visualize_standard.py`** - Génération rapide de visualisations

#### Utilitaires
- `scripts/validate_against_decklistcache.py` - Validation des données
- `test_melee_auth_simple.py` - Test d'authentification Melee

### ❌ SCRIPTS OBSOLÈTES (NE PAS UTILISER)

Ces scripts sont conservés pour référence historique mais ne doivent plus être utilisés :

#### Anciens Scrapers
- `scrape_mtgo_standalone.py` - Remplacé par `scrape_mtgo_flexible.py`
- `scrape_melee_from_commit.py` - Remplacé par `scrape_melee_flexible.py`
- Tout fichier dans `obsolete/` - INTERDICTION ABSOLUE de les utiliser

#### Scripts Archivés
- Tout dans `scripts/_archive_2025_07_27/` - 54 scripts archivés
- Scripts de test one-shot obsolètes

## 🛡️ Règles Critiques

### ⚠️ À RETENIR ABSOLUMENT

1. **JAMAIS toucher au dossier `obsolete/`**
   - Interdiction d'exécuter ces fichiers
   - Si demandé, refuser et proposer l'alternative actuelle

2. **TOUJOURS exclure les leagues**
   - Elles sont dans `{format}/leagues/`
   - Triple protection dans le code

3. **Période d'analyse : 1-21 juillet 2025**
   - Pour comparaison avec Jiliac
   - Ne jamais aller au-delà du 21 juillet

4. **Auto-commit après chaque modification**
   ```bash
   git add -A && git commit -m "auto: $(date +%Y%m%d_%H%M%S)"
   ```

## 📊 Architecture Modulaire

```
src/manalytics/          # Code principal
├── scrapers/           # Récupération données
├── parsers/            # Détection archétypes  
├── cache/              # Système de cache
├── analyzers/          # Analyses statistiques
├── visualizers/        # Génération graphiques
├── pipeline/           # Orchestration
└── api/                # API FastAPI

data/                   # Données
├── raw/                # Données brutes scrapers
├── cache/              # Données processées
└── listener/           # Future: données matchups

scripts/                # Scripts utilitaires
docs/                   # Documentation complète
```

## 💡 Conseils pour Bien Démarrer

1. **Commencez petit** : Faites d'abord une analyse Standard sur 7 jours
2. **Utilisez les visualisations de référence** : `standard_analysis_no_leagues.html`
3. **Respectez les standards visuels** : Voir VISUALIZATION_TEMPLATE_REFERENCE.md
4. **En cas de doute** : Le code dans `src/manalytics/` est la référence

## 🆘 Besoin d'Aide ?

1. **Documentation technique** : Voir `docs/guides/TROUBLESHOOTING.md`
2. **Problèmes de scraping** : Voir `docs/SCRAPERS_COMPLETE_GUIDE.md#troubleshooting`
3. **Questions architecture** : Voir `docs/MANALYTICS_COMPLETE_ARCHITECTURE.html`

## 🎉 Prochaines Étapes

Une fois ce parcours terminé, vous pouvez :

1. **Contribuer au code** : Voir les TODOs dans le code
2. **Implémenter de nouvelles visualisations** : Suivre les patterns existants
3. **Travailler sur la Phase 4** : MTGO Listener pour les vrais matchups
4. **Améliorer les parsers** : Ajouter de nouvelles règles d'archétypes

---

**Bienvenue dans l'équipe Manalytics ! 🚀**

*Ce guide est maintenu à jour. Dernière mise à jour : 28/07/2025*