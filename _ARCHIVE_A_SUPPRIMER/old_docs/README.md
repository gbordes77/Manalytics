# 🎯 MANALYTICS - Système d'Analyse Métagame Magic: The Gathering

> **📋 DOCUMENTATION DE TRANSITION POUR ÉQUIPE DE REPRISE**

## 🚀 DÉMARRAGE RAPIDE

### Commande principale
```bash
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-13
```

### Résultat attendu
- ✅ Analyse complète en 10-60 secondes
- 📊 13 visualisations interactives générées
- 🌐 Dashboard HTML avec tous les graphiques
- 📁 Dossier `standard_analysis_YYYY-MM-DD_YYYY-MM-DD/`

## 📚 DOCUMENTATION COMPLÈTE

| Document | Public cible | Contenu |
|----------|-------------|---------|
| [**DOCUMENTATION_EQUIPE_MANALYTICS.md**](DOCUMENTATION_EQUIPE_MANALYTICS.md) | **Développeurs** | Architecture, code, règles critiques |
| [**GUIDE_UTILISATEUR_MANALYTICS.md**](GUIDE_UTILISATEUR_MANALYTICS.md) | **Utilisateurs finaux** | Manuel d'utilisation, exemples |
| [**GUIDE_ADMIN_MANALYTICS.md**](GUIDE_ADMIN_MANALYTICS.md) | **Administrateurs** | Installation, maintenance, troubleshooting |

## 🚨 RÈGLES CRITIQUES À RESPECTER

### 1. Données réelles uniquement
- ❌ **INTERDIT** : Données mock, fake, test, dummy, générées
- ✅ **OBLIGATOIRE** : Données réelles de tournois scrapées
- 🔒 **Contrôle** : Politique appliquée via `enforcement/strict_mode.py`

### 2. Autorisation pour nouvelles fonctionnalités
- ⚠️ **OBLIGATOIRE** : Demander autorisation avant tout développement
- 💡 Proposer des idées, mais attendre le go/no-go
- 🛡️ Conserver l'existant si pas d'impact

### 3. Cohérence des analyses
- 📊 **RÈGLE ABSOLUE** : Tous les graphiques doivent correspondre EXACTEMENT au format et période demandés
- 🚫 **Interdit** : Mélanger formats ou périodes dans une même analyse
- 🎯 **Archétypes "Autres"** : Jamais majoritaires, toujours en dernier

## 🔧 MAINTENANCE ESSENTIELLE

### Vérification hebdomadaire
```bash
# Test de santé du système
python run_full_pipeline.py --start-date $(date -d '7 days ago' +%Y-%m-%d) --end-date $(date +%Y-%m-%d)
```

### Surveillance des logs
- 📋 **Normal** : Erreurs `_detect_colors` (n'impactent pas le fonctionnement)
- 🚨 **Alerte** : Archétypes "Autres" > 30%
- ⏱️ **Performance** : Temps d'exécution > 2 minutes

## 🏗️ ARCHITECTURE SYSTÈME

```
Manalytics/
├── run_full_pipeline.py          # 🎯 POINT D'ENTRÉE PRINCIPAL
├── src/orchestrator.py           # 🧠 Logique métier
├── MTGODecklistCache/            # 📊 Données de tournois
├── MTGOFormatData/               # 🎲 Définitions archétypes
├── enforcement/strict_mode.py    # 🔒 Contrôle données réelles
└── [format]_analysis_[dates]/    # 📁 Résultats générés
```

## 🎲 FORMATS SUPPORTÉS

| Format | Commande | Données disponibles |
|--------|----------|-------------------|
| **Standard** | `--format Standard` | ✅ Excellent |
| **Modern** | `--format Modern` | ✅ Excellent |
| **Pioneer** | `--format Pioneer` | ✅ Bon |
| **Legacy** | `--format Legacy` | ⚠️ Partiel |
| **Vintage** | `--format Vintage` | ⚠️ Partiel |
| **Pauper** | `--format Pauper` | ⚠️ Partiel |

## 📊 VISUALISATIONS GÉNÉRÉES

1. **Répartition des archétypes** (pie chart)
2. **Parts de métagame** (bar chart)
3. **Matrice de matchups** (heatmap)
4. **Winrates avec intervalles de confiance** (error bars)
5. **Classification par tiers** (scatter plot)
6. **Top 5-0 MTGO** (bar chart)
7. **Bubble chart winrate/présence**
8. **Évolution temporelle**
9. **Sources de données**

## 🛠️ DÉPENDANCES

```bash
# Python 3.8+
pip install pandas plotly numpy scipy matplotlib seaborn
```

## 🚨 CONTACTS ET ESCALADE

### Problèmes critiques
1. **Système cassé** → Voir `GUIDE_ADMIN_MANALYTICS.md` section "Procédures d'urgence"
2. **Données incohérentes** → Vérifier les règles dans `DOCUMENTATION_EQUIPE_MANALYTICS.md`
3. **Performance dégradée** → Scripts de diagnostic dans `GUIDE_ADMIN_MANALYTICS.md`

### Évolutions futures
- 📝 **Obligation** : Documenter toute modification
- 🔄 **Processus** : Proposition → Autorisation → Développement → Tests
- 📊 **Priorité** : Stabilité > Nouvelles fonctionnalités

---

> **⚠️ ATTENTION** : Ce système analyse des données réelles de tournois Magic: The Gathering. Les résultats reflètent le métagame actuel et doivent être interprétés avec expertise du jeu.

**🎯 SUCCÈS = Analyses rapides, données pures, visualisations claires, système stable** 