# 📊 Analyse des Visualisations Jiliac vs Manalytics

> **Objectif** : Reproduire EXACTEMENT les visualisations de Jiliac avant de les améliorer

## 🎯 Ce que génère Jiliac (R-Meta-Analysis)

D'après `_main.R`, voici les 7 visualisations principales :

### ✅ 1. **Metagame Pie Chart** - Distribution des archétypes
- **Statut Manalytics** : ✅ FAIT (dans notre template)
- **Fichier** : `standard_analysis_no_leagues.html`

### ✅ 2. **Metagame Bar Chart** - Présence des archétypes
- **Statut Manalytics** : ✅ FAIT (dans notre template)
- **Fichier** : `standard_analysis_no_leagues.html`

### ❌ 3. **Win Rate Mustache Graph** - Taux de victoire avec intervalles de confiance
- **Statut Manalytics** : ❌ À FAIRE
- **Description** : Graphique avec "moustaches" montrant les win rates et leurs intervalles de confiance
- **Importance** : CRITIQUE - montre la fiabilité statistique

### ❌ 4. **Win Rate Box Plot** - Distribution des performances
- **Statut Manalytics** : ❌ À FAIRE
- **Description** : Box plots montrant la variance des performances par archétype
- **Importance** : Moyenne - utile pour voir la consistance

### ❌ 5. **Archetype Tier Scatterplot** - Classification en tiers
- **Statut Manalytics** : ❌ À FAIRE
- **Description** : Scatter plot classant les archétypes en Tier 1, 2, 3
- **Importance** : ÉLEVÉE - vision synthétique du méta

### ❌ 6. **Winrate & Presence Scatterplot** - Corrélation performance/popularité
- **Statut Manalytics** : ❌ À FAIRE
- **Description** : X=Presence%, Y=Winrate% - montre les overperformers
- **Importance** : ÉLEVÉE - identifie les decks sous-joués mais forts

### ❌ 7. **Matchup Matrix Heatmap** - LA visualisation clé
- **Statut Manalytics** : ❌ À FAIRE (DÉPEND DU LISTENER)
- **Description** : Matrice NxN des win rates entre archétypes
- **Importance** : CRITIQUE - c'est LA valeur principale du projet
- **Blocage** : Nécessite les données round-par-round du MTGO Listener

## 📈 Timeline Evolution (Bonus Manalytics)
- **Statut** : ✅ FAIT (on l'a déjà, Jiliac ne l'a pas)
- C'est notre première amélioration !

## 🚀 Plan d'Action : Reproduire d'abord, innover ensuite

### Phase 1 : Parité avec Jiliac (PRIORITÉ)
```python
# 1. Win Rate Mustache Graph
create_winrate_mustache_graph.py
- Calculer win rates par archétype
- Calculer intervalles de confiance (95%)
- Visualiser avec error bars

# 2. Archetype Tier Scatterplot  
create_archetype_tiers.py
- Algorithme de tiering basé sur presence + winrate
- Scatter plot avec zones colorées (T1, T2, T3)

# 3. Winrate & Presence Scatterplot
create_performance_scatter.py
- X: Meta % 
- Y: Win rate %
- Taille bulles = nombre de matchs
- Quadrants : overperformers, underperformers

# 4. Box Plot (optionnel)
create_performance_boxplot.py
- Distribution des résultats par archétype
```

### Phase 2 : Matchup Matrix (POST-LISTENER)
```python
# BLOQUÉ jusqu'à l'implémentation du MTGO Listener
create_matchup_matrix.py
- Heatmap NxN 
- Gradient rouge/vert pour win rates
- Nombres de matchs en overlay
```

### Phase 3 : Dépasser Jiliac (APRÈS PARITÉ)
- Dashboard temps réel
- ML predictions
- Sideboard intelligence
- Innovation detector
- Consensus deck generator

## 📝 Template à Respecter

**TOUTES ces nouvelles visualisations DOIVENT** :
- ✅ Utiliser le template `VISUALIZATION_TEMPLATE_REFERENCE.md`
- ✅ Header purple gradient
- ✅ Plotly interactif
- ✅ Couleurs MTG officielles
- ✅ Export CSV
- ✅ Mobile responsive

## 🎯 Message Clé

> "Avant de dire qu'on fait mieux que Jiliac, on doit montrer qu'on sait faire la même chose."

**Ordre de priorité** :
1. Mustache Graph (le plus demandé)
2. Tier Scatterplot (vision synthétique)
3. Performance Scatter (trouve les hidden gems)
4. Box Plot (nice to have)
5. Matchup Matrix (attend le listener)

---

**Note** : Ce document sert de checklist. Cocher au fur et à mesure de l'implémentation.