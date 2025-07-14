# 📋 ANALYSIS TEMPLATE SPECIFICATION

## 🎯 **PAGES OBLIGATOIRES À GÉNÉRER**

### **1. Pages principales**
- ✅ `standard_YYYY-MM-DD_YYYY-MM-DD.html` - Dashboard principal
- ✅ `standard_YYYY-MM-DD_YYYY-MM-DD_tournaments_list.html` - Liste des tournois
- ✅ `all_archetypes.html` - Vue d'ensemble des archétypes
- ❌ `players_analysis.html` - **MANQUANT** - Analyse des joueurs
- ❌ `mtgo_analysis.html` - **MANQUANT** - Analyse dédiée MTGO

### **2. Pages d'archétypes individuels**
- ✅ `archetype_XXX.html` - Une page par archétype

### **3. Visualisations obligatoires (11 charts)**
- ✅ `metagame_pie.html` - Répartition des archétypes
- ✅ `metagame_share.html` - Parts de métajeu détaillées
- ✅ `winrate_confidence.html` - Intervalles de confiance
- ✅ `tiers_scatter.html` - Classification en tiers
- ✅ `bubble_winrate_presence.html` - Winrate vs présence
- ✅ `top_5_0.html` - Top performers
- ✅ `data_sources_pie.html` - Répartition des sources
- ✅ `archetype_evolution.html` - Évolution temporelle
- ✅ `main_archetypes_bar.html` - Archétypes principaux
- ✅ `main_archetypes_bar_horizontal.html` - Version horizontale
- ✅ `matchup_matrix.html` - Matrice de matchups

### **4. Données exportées obligatoires**
- ✅ `decklists_detailed.csv` - Données complètes
- ✅ `decklists_detailed.json` - Format JSON
- ✅ `advanced_analysis.json` - Analyse avancée
- ✅ `archetype_stats.csv` - Stats d'archétypes
- ✅ `matchup_matrix.csv` - Matrice de matchups

## 🚨 **PAGES MANQUANTES À IMPLÉMENTER**

### **1. Page Players Analysis**
**Fichier** : `players_analysis.html`

**Contenu requis :**
- 🏆 **Top joueurs** par winrate
- 🎯 **Joueurs parfaits** (5-0 en League)
- 📊 **Diversité des archétypes** par joueur
- 📈 **Évolution temporelle** des performances
- 🎪 **Répartition par source** (MTGO vs Melee)

**Données disponibles :**
- `player_name` dans le CSV
- Performances par joueur
- Archétypes joués
- Sources de tournois

### **2. Page MTGO Analysis**
**Fichier** : `mtgo_analysis.html`

**Contenu requis :**
- 🏆 **League vs Challenge** - Comparaison
- 📊 **Métriques MTGO** spécifiques
- 🎯 **Archétypes dominants** sur MTGO
- 📈 **Évolution temporelle** MTGO
- 🎪 **Statistiques de sources** MTGO

**Données disponibles :**
- `tournament_source` avec indication MTGO
- Distinction League 5-0 vs Challenge
- Données temporelles MTGO

## 🔄 **PROCESSUS DE VALIDATION**

### **Checklist de génération :**
1. [ ] Toutes les pages principales générées
2. [ ] Toutes les visualisations créées
3. [ ] Tous les fichiers de données exportés
4. [ ] Page players créée
5. [ ] Page MTGO créée
6. [ ] Test d'ouverture de toutes les pages
7. [ ] Validation des liens entre pages

### **Contrôle qualité :**
- **Nombre de pages HTML** : Minimum 25+ pages
- **Nombre de visualisations** : Exactement 11 charts
- **Fichiers de données** : Minimum 5 fichiers (CSV/JSON)
- **Liens internes** : Tous les liens fonctionnels
- **Conformité design** : Style cohérent avec le template

## 🛠️ **IMPLÉMENTATION TECHNIQUE**

### **Modifications requises dans l'orchestrateur :**
1. **Ajouter** `generate_players_analysis()` méthode
2. **Ajouter** `generate_mtgo_analysis()` méthode
3. **Modifier** `run_pipeline()` pour inclure ces générations
4. **Ajouter** validation de complétude

### **Fichiers à modifier :**
- `src/orchestrator.py` - Ajouter nouvelles méthodes
- `src/python/visualizations/metagame_charts.py` - Ajouter charts joueurs
- `docs/ANALYSIS_TEMPLATE_SPECIFICATION.md` - Ce fichier (référence)

## 📅 **ROADMAP D'IMPLÉMENTATION**

### **Phase 1 : Page Players (Priorité 1)**
- [ ] Créer méthode `generate_players_analysis()`
- [ ] Implémenter visualisations joueurs
- [ ] Intégrer dans le pipeline principal

### **Phase 2 : Page MTGO (Priorité 2)**
- [ ] Créer méthode `generate_mtgo_analysis()`
- [ ] Implémenter métriques MTGO spécifiques
- [ ] Intégrer dans le pipeline principal

### **Phase 3 : Validation système (Priorité 3)**
- [ ] Créer script de validation complétude
- [ ] Ajouter tests automatiques
- [ ] Documentation utilisateur

---

> **Note importante** : Ce fichier fait office de **contrat** pour ce qui doit être généré.
> Toute modification du pipeline doit être reflétée ici pour assurer la continuité entre équipes.
