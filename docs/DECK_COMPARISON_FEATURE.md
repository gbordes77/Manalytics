# 🔍 Comparaison de Listes & Sideboards - Feature Design

## 🎯 Concept Principal

Un outil interactif pour comparer visuellement 2-4 decklists du même archétype pour identifier les différences et tendances.

## 📊 Visualisations Proposées

### 1. **Diff View - Comparaison 2 Listes**

```
        Deck A (Trophy)          |         Deck B (0-3 drop)
    --------------------------------|--------------------------------
    Mainboard:                      | Mainboard:
    ✅ 4 Monastery Swiftspear       | ✅ 4 Monastery Swiftspear
    ✅ 4 Play with Fire             | ✅ 4 Play with Fire
    ✅ 4 Lightning Strike           | ❌ 3 Lightning Strike (-1)
    ❌ 0 Torch the Tower            | 🆕 2 Torch the Tower (+2)
    ✅ 3 Urabrask's Forge           | ❌ 2 Urabrask's Forge (-1)
                                    |
    Différences: 3 cartes           | Total: 60 cartes
    
    Sideboard:                      | Sideboard:
    ✅ 3 Duress                     | ✅ 3 Duress  
    ❌ 2 Obliterating Bolt          | 🆕 3 Obliterating Bolt (+1)
    🆕 2 Chandra, Dressed to Kill   | ❌ 0 Chandra (-2)
```

### 2. **Heatmap Multi-Decks (3+ listes)**

```
                    Deck1  Deck2  Deck3  Deck4  Avg
Monastery Swiftspear   4     4      4      4    4.0  [████████]
Play with Fire         4     4      4      4    4.0  [████████]
Lightning Strike       4     4      3      4    3.75 [███████▌]
Kumano Faces          4     4      4      3    3.75 [███████▌]
Torch the Tower       0     2      1      2    1.25 [██▌     ]
Urabrask's Forge      3     2      3      3    2.75 [█████▌  ]

Légende: ■ = 1 copie
```

### 3. **Variance Analysis - Flex Slots**

```python
CORE CARDS (100% des listes):
- 4 Monastery Swiftspear
- 4 Play with Fire
- 20 Mountain

FLEX MAINBOARD (variance haute):
- Torch the Tower: 0-3 copies (σ=1.2)
- Urabrask's Forge: 2-4 copies (σ=0.8)
- Feldon: 0-2 copies (σ=0.9)

SIDEBOARD VARIANCE:
- Obliterating Bolt: 2-4 copies
- Lithomantic Barrage: 0-3 copies
- Chandra: 0-2 copies
```

### 4. **Performance Correlation**

```
Carte               | Win Rate avec | Win Rate sans | Impact
--------------------|---------------|---------------|--------
Torch the Tower     | 67% (n=24)    | 52% (n=48)    | +15% ⬆️
3rd Urabrask's Forge| 71% (n=31)    | 48% (n=41)    | +23% ⬆️
4th Kumano          | 45% (n=20)    | 61% (n=52)    | -16% ⬇️
```

## 🎨 Interface Interactive

### Mode 1: Quick Compare (2 decks)
```
[Sélectionner Deck A ▼] vs [Sélectionner Deck B ▼]

Filtres:
□ Top 8 uniquement
□ 7+ wins
□ Dernière semaine
□ Même tournoi

[Comparer]
```

### Mode 2: Archetype Overview
```
Sélectionner: [Mono-Red Aggro ▼]
Période: [7 derniers jours ▼]
Nombre de listes: [10 meilleures ▼]

Affichage:
○ Heatmap
● Variance Analysis  
○ Evolution temporelle
```

### Mode 3: Innovation Tracker
```
🔥 CARTES EN HAUSSE (Mono-Red)
1. Torch the Tower: 5% → 35% (+30%)
2. Screaming Nemesis: 0% → 18% (+18%)

📉 CARTES EN BAISSE
1. Feldon: 45% → 12% (-33%)
2. 4th Kumano: 89% → 56% (-33%)
```

## 💡 Cas d'Usage Concrets

### Pour les Joueurs Compétitifs
1. **Préparation Tournoi**
   - "Quelle version de Mono-Red performer le mieux?"
   - "Combien de Torch the Tower je dois jouer?"
   - "Quel sideboard est optimal cette semaine?"

2. **Méta-Adaptation**
   - Voir les trends en temps réel
   - Identifier les tech choices gagnantes
   - Ajuster sa liste en conséquence

### Pour les Créateurs de Contenu
1. **Articles**
   - "Stock list vs Innovations"
   - "Evolution du sideboard post-ban"
   - "Les 5 versions de UW Control"

2. **Streams/Videos**
   - Deck tech comparatif
   - "Pourquoi cette carte monte?"

## 🔧 Implementation Technique

### Backend
```python
def compare_decklists(deck1, deck2):
    diff = {
        'only_in_deck1': [],
        'only_in_deck2': [],
        'different_counts': [],
        'identical': []
    }
    
    # Algorithme de diff
    all_cards = set(deck1.cards) | set(deck2.cards)
    
    for card in all_cards:
        count1 = deck1.get_count(card)
        count2 = deck2.get_count(card)
        
        if count1 == count2:
            diff['identical'].append(card)
        elif count1 == 0:
            diff['only_in_deck2'].append((card, count2))
        elif count2 == 0:
            diff['only_in_deck1'].append((card, count1))
        else:
            diff['different_counts'].append((card, count1, count2))
    
    return diff
```

### Visualisation Plotly
```python
import plotly.graph_objects as go

def create_comparison_heatmap(decks):
    # Créer matrice cards x decks
    fig = go.Figure(data=go.Heatmap(
        z=card_counts_matrix,
        x=[f"Deck {i+1}" for i in range(len(decks))],
        y=card_names,
        colorscale='RdBu',
        text=hover_texts,
        hovertemplate='%{y}: %{text} copies<extra></extra>'
    ))
    
    fig.update_layout(
        title="Comparaison Multi-Decks",
        xaxis_title="Decks",
        yaxis_title="Cartes"
    )
    
    return fig
```

## 📈 Métriques de Succès

1. **Utilisation**: 70% des users comparent avant un tournoi
2. **Engagement**: 5+ comparaisons par session
3. **Conversion**: Les decks "optimisés" performent +10%

## 🚀 Priorité: TRÈS HAUTE

Cette feature est **immédiatement utile** avec nos données actuelles et ne nécessite aucune déduction/estimation.

## Exemples Visuels

### Exemple 1: Sidebar Compare
```
MAINBOARD DIFF:
← Deck A        Deck B →
   -1      Lightning Strike    +1
   -2      Feldon, Ronom       
          Torch the Tower      +2
   
SIDEBOARD DIFF:
   -2      Chandra             
          Obliterating Bolt    +1
          Lithomantic B.       +1
```

### Exemple 2: Performance Matrix
```
            Trophy  Top8  5-2  0-3
Torch       ●●○    ●○○   ○○○  ○○○
3x Forge    ●●●    ●●○   ●○○  ○○○
4x Kumano   ●●●●   ●●●●  ●●●● ●●●●
Screaming   ●○○    ○○○   ○○○  ○○○

● = Présent dans la liste
```