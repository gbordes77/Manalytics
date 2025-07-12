# 📋 HANDOFF DOCUMENTATION - MANALYTICS

## 🎯 Vue d'ensemble du projet

**Manalytics** est un système d'analyse de métagame Magic: The Gathering comprenant :
- Backend FastAPI avec API REST
- Interface web avec générateur d'analyses interactif
- Moteur d'analyse avancé avec clustering et visualisations
- Base de données de vrais tournois (1383+ decks)

## 🏆 ÉTAT FONCTIONNEL CONFIRMÉ

### ✅ Dernière configuration fonctionnelle (12 juillet 2025, 18:10)

**Commandes exactes qui ont fonctionné :**
```bash
# 1. Nettoyer les processus
pkill -f "python.*fastapi_app_simple"

# 2. Installer les dépendances
pip install python-multipart

# 3. Démarrer le serveur
cd src/python/api && python fastapi_app_simple.py &

# 4. Tester (SUCCÈS CONFIRMÉ)
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis
```

**Résultats obtenus :**
- ✅ 1383 decks de 20 tournois analysés
- ✅ 3 archétypes identifiés
- ✅ 4 visualisations créées (PNG haute résolution)
- ✅ Dashboard interactif généré (4.6 MB)
- ✅ Rapport JSON complet créé
- ✅ Interface web accessible sur http://localhost:8000/web

## 🏗️ Architecture technique

### Structure des fichiers critiques
```
Manalytics/
├── src/python/api/
│   └── fastapi_app_simple.py          # ✅ SERVEUR PRINCIPAL FONCTIONNEL
├── advanced_metagame_analyzer.py      # ✅ MOTEUR D'ANALYSE FONCTIONNEL
├── real_data/                         # ✅ DONNÉES RÉELLES (260KB+ par format)
│   ├── standard_tournaments.json
│   ├── modern_tournaments.json
│   └── ...
└── analysis_output/                   # ✅ SORTIE DES ANALYSES
    ├── dashboard.html
    ├── complete_report.json
    └── visualizations/
```

### Endpoints API fonctionnels
- `GET /health` - Statut serveur
- `GET /web` - Interface web complète
- `POST /generate-analysis` - **GÉNÉRATEUR PRINCIPAL** (JSON)
- `GET /metagame` - Données métagame
- `GET /real-data` - Informations sur les données

## 🔧 Procédure de démarrage

### 1. Prérequis
```bash
cd /Volumes/DataDisk/_Projects/Manalytics
source venv/bin/activate
pip install python-multipart  # CRITIQUE pour FastAPI
```

### 2. Démarrage du serveur
```bash
# Nettoyer les processus existants
pkill -f "python.*fastapi_app_simple"

# Démarrer le serveur
cd src/python/api
python fastapi_app_simple.py &

# Vérifier le statut
curl http://localhost:8000/health
```

### 3. Accès à l'interface
- **Interface web :** http://localhost:8000/web
- **API Health :** http://localhost:8000/health
- **Documentation API :** http://localhost:8000/docs

## 🎨 Interface utilisateur

### Fonctionnalités de l'interface web
1. **Timeline chronologique** - Sidebar avec historique Magic
2. **Générateur d'analyses** - Formulaire avec :
   - Sélecteur de format (Standard, Modern, Pioneer, etc.)
   - Calendriers de dates
   - Bouton de génération
3. **Cartes de fonctionnalités** - 4 cartes horizontales
4. **Design responsive** - Gradients et animations

### Formats supportés
- Standard (1383 decks, 20 tournois)
- Modern
- Pioneer  
- Legacy
- Vintage
- Pauper

## 🔍 Corrections critiques appliquées

### 1. Clustering adaptatif (advanced_metagame_analyzer.py)
**Problème :** Erreur `n_samples=3 should be >= n_clusters=4`
**Solution :** Adaptation dynamique du nombre de clusters
```python
# Adapter le nombre de clusters au nombre d'archétypes disponibles
n_archetypes = len(self.archetype_performance)
n_clusters = min(4, max(1, n_archetypes))  # Entre 1 et 4 clusters
```

### 2. Gestion des formulaires (fastapi_app_simple.py)
**Problème :** Erreur `python-multipart` manquant
**Solution :** Installation + utilisation de Request/JSON au lieu de Form

### 3. Répertoire d'exécution
**Problème :** Commandes exécutées dans le mauvais répertoire
**Solution :** Ajout du paramètre `cwd` dans subprocess

## 📊 Données et analyses

### Données réelles confirmées
- **Format Standard :** 1383 decks, 20 tournois
- **Archétypes identifiés :** 3 principaux
- **Période couverte :** Données multi-années
- **Taille fichiers :** 260KB+ par format

### Sorties générées
1. **Visualisations PNG** (4 fichiers) :
   - `archetype_performance_analysis.png`
   - `matchup_matrix.png`
   - `statistical_analysis.png`
   - `temporal_trends_analysis.png`

2. **Dashboard interactif** : `dashboard.html` (4.6 MB)
3. **Rapport JSON** : `complete_report.json`

## 🚨 Points d'attention

### Problèmes récurrents identifiés
1. **Port 8000 occupé** → Utiliser `pkill` pour nettoyer
2. **Imports relatifs** → Éviter les autres fichiers FastAPI
3. **Clustering insuffisant** → Déjà corrigé avec adaptation dynamique
4. **Multipart manquant** → Installer `python-multipart`

### Dépendances critiques
- `python-multipart` (FastAPI forms)
- `uvicorn` (serveur ASGI)
- `sklearn` (clustering)
- `matplotlib` + `seaborn` (visualisations)
- `pandas` + `numpy` (analyse données)

## 🔄 Workflow de développement

### Tests recommandés
```bash
# Test de santé
curl http://localhost:8000/health

# Test de génération d'analyse
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis

# Test interface web
open http://localhost:8000/web
```

### Monitoring
- Logs serveur : Console directe
- Fichiers générés : `analysis_output/`
- Statut processus : `ps aux | grep fastapi_app_simple`

## 📝 Mémoire utilisateur

L'utilisateur a les exigences suivantes (mémoire ID: 3019851) :
- **DONNÉES RÉELLES UNIQUEMENT** : Aucune donnée mock/fake autorisée
- **POLITIQUE STRICTE** : Enforcement via pre-commit hooks
- **VRAIES DONNÉES DE TOURNOIS** : Confirmé avec 1383 decks réels

## 🎯 Prochaines étapes recommandées

1. **Stabilisation** : Créer un script de démarrage robuste
2. **Monitoring** : Ajouter logs structurés
3. **Documentation API** : Compléter la documentation Swagger
4. **Tests automatisés** : Créer suite de tests pour l'API
5. **Déploiement** : Containerisation Docker

## 📞 Contact et support

- **Projet :** Manalytics - Analyse métagame Magic: The Gathering
- **Répertoire :** `/Volumes/DataDisk/_Projects/Manalytics`
- **Serveur :** FastAPI sur port 8000
- **Status :** ✅ FONCTIONNEL (confirmé 12/07/2025)

---
*Document créé le 12 juillet 2025 - État fonctionnel confirmé* 