# 📊 TOUTES LES MÉTHODES DE CALCUL DE JILIAC R-META-ANALYSIS

> **Document de référence complet** recensant TOUTES les méthodes de calcul trouvées dans le code R de Jiliac

## 🎯 RÉSUMÉ : COMBIEN DE MÉTHODES ?

**Réponse : Il existe AU MINIMUM 8 méthodes principales de calcul**, avec de nombreuses variantes :

1. **Méthode Standard** (sans time-weight)
2. **Méthode Time-Weighted** 
3. **22 Types de filtrage d'événements**
4. **3 Méthodes de calcul de présence**
5. **2 Méthodes de calcul de win rate**
6. **2 Méthodes de calcul des tiers**
7. **Méthode de clustering** (WIP)
8. **Analyses spécialisées** (joueurs, cartes, comparaisons)

---

## 📁 FICHIERS ANALYSÉS

1. `01-Tournament_Data_Import.R` - Import et filtrage des données
2. `02-Simple_Getters.R` - Méthodes de récupération
3. `03-Metagame_Data_Treatment.R` - **CŒUR DES CALCULS**
4. `Parameters.R` - Configuration de toutes les options

---

## 1️⃣ MÉTHODE TIME-WEIGHTED

### Fonction : `addTimeWeight()`
```r
# Multiplie wins, losses et draws par (semaine - semaine_min + 1)
df$Wins = df$Wins * (df$Week - min(df$Week) + 1)
df$Losses = df$Losses * (df$Week - min(df$Week) + 1)
df$Draws = df$Draws * (df$Week - min(df$Week) + 1)
```

**Activation** : Paramètre `timeWeight = TRUE/FALSE` dans Parameters.R

**Impact** : "The most recent results become more important to determine the share and WR"

---

## 2️⃣ TYPES DE FILTRAGE D'ÉVÉNEMENTS (22 OPTIONS)

### Fonction : `generate_df()`

```r
EventTypes = c(
  "1" = "All events old",
  "2" = "All events Top32",
  "3" = "All events Top8",
  "4" = "All events Top1",
  "5" = "All events X-2 or better",
  "6" = "All events X-1 or better",
  "7" = "Events with MU Data",
  "8" = "ManaTraders",
  "9" = "Paper Events",
  "10" = "Paper Events Top32",
  "11" = "Paper Events Top8",
  "12" = "Paper Events Top1",
  "13" = "Paper Events X-2 or better",
  "14" = "Paper Events X-1 or better",
  "15" = "MTGO Events",
  "16" = "MTGO Challenges and Qualifiers",
  "17" = "MTGO Events Top8",
  "18" = "MTGO Events Top1",
  "19" = "MTGO Events X-2 or better",
  "20" = "MTGO Events X-1 or better",
  "21" = "MTGO Preliminaries",
  "22" = "All events"  # MÉTHODE PAR DÉFAUT
)
```

### Méthode spéciale : `recalculate_wins_losses()`
Pour EventType = 22 et 15, recalcule les wins/losses depuis les matchups individuels

---

## 3️⃣ MÉTHODES DE CALCUL DE PRÉSENCE

### Fonction : `get_archetype_presence()`

**3 options disponibles** :
1. **"Copies"** : Nombre de lignes (decks) de l'archétype
2. **"Players"** : Nombre de joueurs uniques pilotant l'archétype  
3. **"Matches"** : Nombre total de matches joués par l'archétype ✅ (par défaut)

```r
Presence = "Matches"  # Paramètre dans Parameters.R
```

---

## 4️⃣ MÉTHODES DE CALCUL DU WIN RATE

### Fonction : `archetype_metrics()`

**2 méthodes** :

1. **Sans draws** (MÉTHODE PRINCIPALE) :
```r
metric_df$Measured.Win.Rate = metric_df$Wins * 100 / 
  (metric_df$Wins + metric_df$Defeats)
```

2. **Avec draws** :
```r
archetypeWinRateWDraws = sum(archetypeDf$Wins) / sum(archetypeDf$Matches) * 100
```

### Intervalles de confiance
- Utilise `lm_robust` avec clustering par joueur
- Pondération par nombre de matches
- Niveau de confiance : 95% par défaut (paramétrable)

---

## 5️⃣ NORMALISATION DES MÉTRIQUES

### Fonction : `archetype_normalized_sum()`

1. **Normalisation de la présence** :
   - Utilise le **logarithme** pour linéariser la distribution exponentielle
   - `log(Presence) - log(min(Presence))`

2. **Normalisation du win rate** :
   - Linéaire : `WR - min(WR)`

3. **Mise à l'échelle [0,1]** :
   - Division par le maximum pour chaque métrique

4. **Somme normalisée** :
   - `Normalized.Presence + Normalized.Win.Rate`

---

## 6️⃣ CALCUL DES TIERS

### Fonction : `archetype_tiers()`

**2 méthodes de classification** :

### Méthode 1 : Par somme normalisée
```r
Tier = case_when(
  Sum >= mean + 3*sd ~ "0",
  Sum >= mean + 2*sd ~ "0.5",
  Sum >= mean + 1*sd ~ "1",
  Sum >= mean       ~ "1.5",
  Sum >= mean - 1*sd ~ "2",
  Sum >= mean - 2*sd ~ "2.5",
  Sum >= mean - 3*sd ~ "3",
  TRUE ~ "Other"
)
```

### Méthode 2 : Par CI Lower Bound ✅ (UTILISÉE PAR DÉFAUT)
```r
# Même logique mais basée sur Lower.Bound.of.CI.on.WR
# Avec récursion pour recalculer si des "Other" apparaissent
```

---

## 7️⃣ CALCUL DES MATCHUPS

### Fonction : `generate_matchup_data()`

- Génère une matrice NxN de matchups
- Compte wins/losses par paire d'archétypes
- Calcule win rate et intervalles de confiance
- Maximum 18 archétypes (les autres agrégés en "Other")

---

## 8️⃣ OPTIONS DE CONFIGURATION AVANCÉES

### Tri des résultats
```r
SortValue = "Lower.Bound.of.CI.on.WR"  # ou "Measured.Win.Rate"
```

### Échelle de l'axe de présence
```r
PresenceAxisLogScale = TRUE  # Échelle log ou linéaire
```

### Seuils de filtrage
```r
ChartShare = 2  # Seuil minimum de présence (%)
Share.autoupdate = TRUE  # Mise à jour automatique du seuil
```

### Diamètres des bulles
```r
Diameters = "Players"  # Pour les graphiques de type bubble chart
```

---

## 9️⃣ ANALYSES SPÉCIALISÉES

### Scripts additionnels trouvés :
1. `Player_Result_Analysis.R` - Analyse par joueur
2. `week_comparison.R` - Comparaisons temporelles
3. `analyze_unknown_archetypes.R` - Détection d'archétypes
4. `test_clustering_WIP.R` - Méthode de clustering (en développement)
5. `extract_archetype_player_stats.py` - Extraction stats joueurs (Python)

---

## 🔴 MÉTHODE IMPLÉMENTÉE DANS MANALYTICS

Manalytics utilise actuellement :
- ✅ EventType = 22 ("All events")
- ✅ Presence = "Matches"
- ✅ Win rate SANS draws
- ✅ Intervalles de confiance avec clustering
- ✅ Normalisation log pour présence
- ✅ Tiers basés sur CI Lower Bound
- ✅ Seuil 2% de présence
- ❌ PAS de time-weighting

---

## 🎨 VISUALISATIONS GÉNÉRÉES PAR LE PIPELINE

Le pipeline `_main.R` génère **8 visualisations standard** :

1. **01_Presence-Pie-Chart** - Camembert de la répartition du métagame
2. **02_Presence-Bar-Chart** - Graphique en barres de présence
3. **03_Winrate-Mustache-Box** - Win rates avec intervalles de confiance
4. **04_Winrate-Box-Plot** - Box plots des win rates par archétype
5. **05_Scatterplot-of-Tiers** - Distribution des tiers (CI Lower Bound)
6. **06_Winrate-&-Presence-Full-Scatterplot** - Vue complète présence vs win rate
7. **07_Winrate-&-Presence-Zoom-Scatterplot** - Vue zoomée avec détails et tiers
8. **08_Matchup-Matrix** - Matrice complète des matchups

### Exports additionnels :
- Données joueurs (optionnel)
- Données cartes
- Données archétypes/cartes
- Synthèse textuelle

---

## 📌 CONCLUSION

Le système de Jiliac est **extrêmement flexible** avec de multiples combinaisons possibles :
- 22 types de filtrage × 3 méthodes de présence × 2 options time-weight × 2 méthodes de tiers = **264 combinaisons de base**
- Sans compter les variantes de seuils, intervalles de confiance, et analyses spécialisées
- Plus 8 visualisations standard générées automatiquement

La méthode actuellement implémentée dans Manalytics correspond à **UNE configuration spécifique** parmi toutes ces possibilités.