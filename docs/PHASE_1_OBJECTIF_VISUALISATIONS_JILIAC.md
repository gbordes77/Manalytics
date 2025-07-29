# 🎯 PHASE 1 : OBJECTIF VISUALISATIONS JILIAC

> **Document de référence** : Les 6 visualisations essentielles à reproduire fidèlement pour valider la Phase 1 de Manalytics

## 📊 VUE D'ENSEMBLE

Ce document référence les **6 visualisations standard** produites par Jiliac avec R-Meta-Analysis que nous devons reproduire **À L'IDENTIQUE** pour valider notre implémentation.

**Période analysée** : 1-21 juillet 2025  
**Format** : Standard  
**Filtrage** : All events  
**Seuil** : 1.2% (au lieu du 2% habituel)  
**Présence** : Basée sur les Matches  
**Auteurs** : Valentin Manès et Anaël Yahi

---

## 📈 VISUALISATION 1 : Metagame Share Bar Chart

### Description
Graphique en barres horizontales montrant la répartition du métagame.

### Caractéristiques visuelles
- **Titre** : "Metagame share of Standard archetypes in All events between [dates] based on number of Matches"
- **Sous-titre** : "Archetype cut at 1.2%"
- **Couleurs** : Dégradé de rose/violet à vert (palette arc-en-ciel)
- **Ordre** : Par présence décroissante
- **Labels** : Pourcentages affichés à droite des barres

### Données observées (Top 5)
1. Izzet Cauldron : 20.4%
2. Dimir Midrange : 17.9%
3. Golgari Midrange : 5.9%
4. Mono White Caretaker : 4.8%
5. Gruul Aggro : 4.7%

### Spécificités techniques
- 15 archétypes affichés (seuil 1.2%)
- Pas de catégorie "Other"
- Attribution : "by Valentin Manès and Anaël Yahi"

---

## 📊 VISUALISATION 2 : Win Rate Confidence Intervals

### Description
Graphique des win rates avec intervalles de confiance à 90%.

### Caractéristiques visuelles
- **Titre principal** : "90% confidence intervals on the winrates of the most present Standard archetypes"
- **Sous-titres** :
  - "Red lines for the average of the bounds of the CI"
  - "Green line for the average of the measured winrate"
- **Axes** : 
  - X : Archétypes
  - Y : Win rate (%)
- **Éléments** :
  - Points bleus : Win rate mesuré
  - Barres d'erreur : IC 90%
  - Ligne verte horizontale : Moyenne des win rates (~51.8%)
  - Lignes rouges : Moyennes des bornes CI (~41% et ~62%)

### Données clés
- Izzet Cauldron : 64.2% (le plus haut)
- Naya Yuna : 47.5%
- Moyenne générale : ~51.8%

### Spécificités techniques
- Tri par CI lower bound décroissant
- Affichage des valeurs exactes sur les points

---

## 📊 VISUALISATION 3 : Tier List Scatterplot

### Description
Graphique de dispersion montrant les tiers basés sur la borne inférieure de l'IC.

### Caractéristiques visuelles
- **Titre** : "Lower Bound of CI on WR for the most present Standard archetypes"
- **Axes** :
  - X : Archétypes (ordonné par lower bound)
  - Y : Lower bound of CI (%)
- **Tiers affichés** :
  - Tier 0 : Mean + 3*SD (~63%)
  - Tier 0.5 : Mean + 2*SD (~56%)
  - Tier 1 : Mean + 1*SD (~48%)
  - Tier 1.5 : Mean (~41%)
  - Tier 2 : Mean - 1*SD (~34%)
  - Tier 2.5 : Mean - 2*SD (~27%)
  - Tier 3 : Mean - 3*SD (~19%)

### Classification observée
- **Tier 0.5** : Izzet Cauldron (51.08%)
- **Tier 1** : Mono Red Aggro, Azorius Control, Golgari Midrange
- **Tier 1.5** : Dimir Midrange, Izzet Aggro, etc.
- **Tier 2** : Gruul Aggro, Mono White Caretaker, etc.

---

## 📊 VISUALISATION 4 : Win Rate vs Presence Scatterplot (Full)

### Description
Nuage de points montrant TOUS les archétypes avec win rate vs présence.

### Caractéristiques visuelles
- **Titre** : "Win rates depending on presence (Matches) of Standard archetypes"
- **Sous-titre** : "Circle diameters depending on Players"
- **Axes** :
  - X : Présence (%) - Échelle logarithmique
  - Y : Win rate (%)
- **Bulles** : Taille proportionnelle au nombre de joueurs

### Points notables
- Izzet Cauldron : Grande bulle à ~20% présence, ~54% WR
- Nombreux petits archétypes < 1% présence
- Distribution complète du métagame visible

---

## 📊 VISUALISATION 5 : Win Rate vs Presence (Zoom avec Tiers)

### Description
Version zoomée sur les archétypes principaux avec classification en tiers.

### Caractéristiques visuelles
- **Titre** : "Win rates depending on presence of the most present Standard archetypes"
- **Sous-titre** : "Tiers based on Lower Bound of CI on WR"
- **Légende** : 
  - Couleurs par tier (1, 1.5, 2, 2.5)
  - Taille = nombre de joueurs
- **Boîtes d'information** : 
  - Nom de l'archétype
  - Présence : X%
  - Win rate : Y%

### Organisation
- Seuls les archétypes > 1.2% présence
- Classification visuelle par couleur de tier
- Labels détaillés pour chaque archétype

---

## 📊 VISUALISATION 6 : Matchup Matrix

### Description
Matrice complète des matchups entre les archétypes principaux.

### Caractéristiques visuelles
- **Titre** : "Match Up Matrix of the most present Standard archetypes"
- **Format** : Grille 9x9 (+ Other)
- **Code couleur** :
  - Vert : >50% win rate
  - Rouge : <50% win rate
  - Intensité : Force du matchup
  - Gris : Miroir ou données insuffisantes
- **Informations par cellule** :
  - Win rate en gras
  - IC en petit (min% - max%)
  - Nombre de matches

### Exemple de lecture
- Izzet Cauldron vs Dimir Midrange : 47.6% (143 matches)
- Cellules diagonales : 50% (miroirs)

### Spécificités
- Maximum 9 archétypes + "Other"
- Affichage bidirectionnel (A vs B et B vs A)
- Données complètes avec IC et sample size

---

## 🔧 ÉLÉMENTS TECHNIQUES À REPRODUIRE

### 1. Calculs exacts
- ✅ Win rate SANS draws
- ✅ IC à 90% (pas 95%)
- ✅ Clustering par joueur pour les IC
- ✅ Normalisation log pour la présence
- ✅ Tiers basés sur mean ± n*SD de la CI lower bound

### 2. Seuils et filtres
- ✅ Seuil de présence : 1.2% (configurable)
- ✅ Période : 1-21 juillet 2025
- ✅ Format : Standard
- ✅ Event Type : "All events" (type 22)

### 3. Design et mise en forme
- ✅ Attribution aux auteurs
- ✅ Palettes de couleurs cohérentes
- ✅ Formats de titre standardisés
- ✅ Échelle log pour l'axe de présence (viz 4)

---

## ✅ CHECKLIST DE VALIDATION PHASE 1

Pour valider la Phase 1, nous devons :

1. [ ] Reproduire les 6 visualisations avec les mêmes données
2. [ ] Obtenir des chiffres identiques (±0.1% de tolérance)
3. [ ] Respecter l'ordre et la classification des archétypes
4. [ ] Implémenter les mêmes palettes de couleurs
5. [ ] Générer des fichiers avec la même structure de nommage
6. [ ] Inclure toutes les métadonnées (titres, sous-titres, attributions)

---

## 📝 NOTES IMPORTANTES

1. **Ordre de développement suggéré** :
   - D'abord : Calculs de base (présence, WR, IC)
   - Ensuite : Classifications (tiers)
   - Enfin : Visualisations

2. **Points de vigilance** :
   - Le seuil 1.2% au lieu de 2% change le nombre d'archétypes
   - Les IC sont à 90%, pas 95%
   - L'échelle log est cruciale pour la lisibilité

3. **Validation des données** :
   - Comparer avec nos résultats actuels
   - Vérifier la cohérence des matchups
   - S'assurer que les totaux = 100%

---

**Version** : 1.0  
**Date** : 29/07/2025  
**Objectif** : Reproduction fidèle du pipeline Jiliac R-Meta-Analysis