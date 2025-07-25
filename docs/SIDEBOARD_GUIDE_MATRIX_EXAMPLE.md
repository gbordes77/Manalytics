# 📊 Sideboard Guide Matrix - Exemple Visuel

## 🎯 Concept

La **Sideboard Guide Matrix** est une heatmap interactive qui montre comment sideboard entre différents archétypes.

## 📐 Structure de la Matrice

```
                    VS
           Mono-Red  UW Control  GB Midrange  Domain
    M    ┌─────────┬───────────┬────────────┬────────┐
    o    │ +3 Duress│ -4 Wrath  │ +2 Negate  │ +1 Void│
    n    │ +2 Lithom│ -3 Teferi │ +2 Dispute │ +2 Necr│
    o    │ -2 Shock │ +3 Helix  │ -3 Push    │ -3 Land│
    -    │ -3 Play  │ +4 Fable  │ +1 Bankbus │        │
    R    └─────────┴───────────┴────────────┴────────┘
    e    
    d    ┌─────────┬───────────┬────────────┬────────┐
         │ +4 Negate│          │ +3 Duress  │ -2 Sunf│
    U    │ +3 Doomskar        │ +1 Farewell│ +3 Depr│
    W    │ -4 Wedding│        │ -4 Wedding │ -1 Raff│
         │ -3 Emperor│        │            │        │
    C    └─────────┴───────────┴────────────┴────────┘
    o
    n    ┌─────────┬───────────┬────────────┬────────┐
    t    │ ...     │ ...       │ ...        │ ...    │
    r    └─────────┴───────────┴────────────┴────────┘
    o
    l

```

## 🎨 Visualisation avec Plotly

### Version 1 : Heatmap Simple
```python
# Chaque cellule = intensité du sideboarding
# Rouge = beaucoup de cartes OUT
# Vert = beaucoup de cartes IN
# Gris = matchup équilibré
```

### Version 2 : Matrice Interactive
- **Hover** sur une cellule → affiche le guide complet
- **Click** → ouvre le détail avec explications
- **Filtres** → par tournoi, période, win rate

### Exemple de Cellule au Hover :
```
Mono-Red vs UW Control
----------------------
OUT (7 cartes):
-4 Play with Fire
-3 Kumano Faces Kakkazan

IN (7 cartes):
+3 Duress
+2 Lithomantic Barrage  
+2 Chandra, Dressed to Kill

Win Rate: 45% → 52% (post-side)
```

## 📊 Données Affichées

1. **Code Couleur Principal**
   - 🟩 Vert foncé : Matchup très favorable post-side
   - 🟨 Jaune : Matchup équilibré
   - 🟥 Rouge : Matchup défavorable

2. **Métriques dans chaque cellule**
   - Nombre de cartes IN/OUT
   - Delta de win rate (pre vs post-side)
   - Cartes les plus impactantes

3. **Patterns Visuels**
   - Lignes vertes = deck avec bon sideboard
   - Colonnes rouges = deck difficile à battre post-side
   - Diagonale = toujours neutre (miroir)

## 🔧 Fonctionnalités Avancées

### 1. **Agrégation Intelligente**
- Combine les données de plusieurs tournois
- Pondération par performance des joueurs
- Détection des "tech choices" inhabituelles

### 2. **Mode Comparaison**
- Avant/Après un ban
- Évolution semaine par semaine
- Différences entre MTGO et Melee

### 3. **Export & Partage**
- PNG haute résolution pour articles
- CSV avec les guides détaillés
- Lien interactif pour Discord/Twitter

## 💡 Valeur pour les Joueurs

1. **Préparation Tournoi**
   - Vue d'ensemble instantanée
   - Guides validés par les données
   - Identification des matchups clés

2. **Métagame Intelligence**
   - Quels decks ont le meilleur sideboard ?
   - Contre quoi les gens sideboard mal ?
   - Opportunités de "next level"

3. **Deck Building**
   - Optimisation des 15 cartes de side
   - Identification des flex slots
   - Couverture des matchups importants

## 🎯 Exemple Concret

Pour un tournoi avec 5 archétypes majeurs, on aurait une matrice 5x5 = 25 cellules.

Si Mono-Red = 30% du meta et UW Control = 20%, la cellule "Mono-Red vs UW" sera plus grosse/importante visuellement.

Les données proviennent de l'analyse des decklists pre/post side dans les rounds de tournois.