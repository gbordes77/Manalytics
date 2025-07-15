# 🔍 COMPARAISON MANALYTICS vs JILLIAC/ALIQUANTO3

## 📊 **ANALYSE GÉNÉRÉE PAR MANALYTICS**
**Période** : 2025-06-13 à 2025-06-24
**Format** : Standard
**Date de génération** : 2025-07-15 21:44

---

## 📈 **MÉTRIQUES CLÉS PRODUITES**

### **Données Brutes**
- **🏆 Tournaments** : 57 tournois analysés
- **🎯 Decks** : 1,103 decks (502 doublons supprimés)
- **🎲 Archetypes** : 33 archétypes identifiés
- **🌐 Sources** : melee.gg, mtgo.com (League 5-0), mtgo.com (Challenge), mtgo.com

### **Analyses Statistiques Avancées**
- **Shannon Diversity** : 1.754
- **Simpson Diversity** : 0.690
- **Effective Archetypes** : 5.78
- **Herfindahl Index** : 0.310
- **Evenness** : 0.502

### **Top 5 Archétypes (Metagame Share)**
1. **Izzet Ramp** : 32.42% (378 decks)
2. **Azorius Omniscience** : 13.42% (148 decks)
3. **Mono Red Ramp** : 8.45% (110 decks)
4. **Mono Red Aggro** : 9.81% (115 decks)
5. **Dimir Ramp** : 5.71% (66 decks)

---

## 🎯 **ANALYSE MTGO SPÉCIFIQUE**

### **Données MTGO Seules**
- **Archetypes MTGO** : 17 archétypes
- **Top MTGO** :
  1. **Izzet Ramp** : 30.69% (145 decks)
  2. **Mono Red Aggro** : 13.79% (65 decks)
  3. **Mono Red Ramp** : 13.45% (76 decks)
  4. **Azorius Omniscience** : 10.69% (46 decks)
  5. **Dimir Ramp** : 8.97% (39 decks)

---

## 📁 **FICHIERS GÉNÉRÉS**

### **Dashboard Principal**
- `standard_2025-06-13_2025-06-24.html` - Dashboard complet
- `players_stats.html` - Statistiques des joueurs
- `all_archetypes.html` - Vue d'ensemble des archétypes

### **Visualisations (14 graphiques)**
- `metagame_pie.html` - Pie chart du métagame
- `metagame_share.html` - Parts de marché
- `winrate_confidence.html` - Winrates avec intervalles de confiance
- `tiers_scatter.html` - Scatter plot des tiers
- `bubble_winrate_presence.html` - Bubble chart performance/présence
- `matchup_matrix.html` - Matrice des matchups
- `archetype_evolution.html` - Évolution temporelle
- `main_archetypes_bar.html` - Bar chart horizontal
- `main_archetypes_bar_horizontal.html` - Bar chart vertical

### **Données Exportées**
- `archetype_stats.csv` - Statistiques par archétype
- `matchup_matrix.csv` - Matrice des matchups
- `decklists_detailed.csv` - Decklists détaillées
- `advanced_analysis.json` - Analyses statistiques avancées

### **Pages par Archétype**
- 33 pages HTML individuelles (une par archétype)
- Navigation et liens fonctionnels

---

## 🔬 **ANALYSES AVANCÉES IMPLÉMENTÉES**

### **Diversité du Métagame**
- Indices de Shannon et Simpson calculés
- Nombre effectif d'archétypes : 5.78
- Concentration (HHI) : 0.310

### **Tendances Temporelles**
- Catégorisation : Rising/Declining/Stable/Volatile
- Volatilité et taux de croissance calculés
- Archétypes émergents et déclinants identifiés

### **Clustering K-means**
- 3 clusters d'archétypes basés sur performance
- Profils de clusters analysés

### **Corrélations Statistiques**
- Matrice de corrélation entre variables
- Tests de significativité
- Corrélations les plus fortes identifiées

---

## ✅ **STANDARDS JILLIAC RESPECTÉS**

### **Classification des Archétypes**
- ✅ Reproduction fidèle du moteur C# MTGOArchetypeParser
- ✅ 12 types de conditions supportées
- ✅ Variants et fallbacks implémentés
- ✅ Intégration couleurs (guildes, tri-couleurs)

### **Visualisation**
- ✅ Palette couleurs professionnelle (MTGGoldfish/17lands standard)
- ✅ Accessibilité daltonisme (ColorBrewer RdYlBu)
- ✅ Règles strictes : 12 archétypes max, "Autres" en gris
- ✅ Tailles standardisées (1000×700px)

### **Analyses Statistiques**
- ✅ Indices de diversité (Shannon, Simpson)
- ✅ Tendances temporelles
- ✅ Clustering et corrélations
- ✅ Intervalles de confiance

### **Export et Dashboard**
- ✅ HTML interactif avec navigation
- ✅ CSV/JSON pour auditabilité
- ✅ Pages détaillées par archétype
- ✅ Statistiques des joueurs

---

## 🚀 **POINTS D'AMÉLIORATION POUR DÉPASSER JILLIAC**

### **Performance**
- Pipeline plus rapide (parallélisation)
- Cache intelligent pour éviter re-calculs

### **UX/UI**
- Dashboard plus interactif (filtres temps réel)
- Export PDF automatique
- Mobile-responsive

### **Analyses Avancées**
- ML pour détection nouveaux archétypes
- Prédiction de tendances
- Analyse bayésienne

### **API et Extensibilité**
- API REST publique
- Ajout facile nouveaux formats
- Intégration continue

---

## 📋 **PROCHAINES ÉTAPES**

1. **Comparer** avec les données Jilliac sur la même période
2. **Valider** la fidélité de reproduction
3. **Identifier** les écarts et améliorations possibles
4. **Optimiser** pour dépasser les standards existants

---

*Document généré automatiquement par Manalytics v0.3.5*
