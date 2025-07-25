# 🎯 Générateur de Deck Consensus - Feature Design

## 📝 Concept Principal

Générer automatiquement un "deck type" représentatif d'un archétype en analysant toutes les listes disponibles et en extrayant le consensus.

## 🧮 Algorithme de Génération

### 1. **Analyse Statistique des 20+ Decks**

```python
def generate_consensus_deck(archetype_decks):
    """
    Génère un deck consensus basé sur la fréquence et le nombre moyen
    """
    card_stats = {}
    
    # Analyser chaque carte
    for deck in archetype_decks:
        for card in deck.mainboard:
            if card.name not in card_stats:
                card_stats[card.name] = {
                    'appearances': 0,
                    'total_copies': 0,
                    'copy_counts': []
                }
            
            card_stats[card.name]['appearances'] += 1
            card_stats[card.name]['total_copies'] += card.count
            card_stats[card.name]['copy_counts'].append(card.count)
    
    # Calculer les moyennes et consensus
    consensus_main = []
    for card_name, stats in card_stats.items():
        appearance_rate = stats['appearances'] / len(archetype_decks)
        avg_copies = stats['total_copies'] / stats['appearances']
        
        # Règles de consensus
        if appearance_rate >= 0.90:  # 90%+ des decks = CORE
            consensus_count = round(avg_copies)
        elif appearance_rate >= 0.70:  # 70-89% = STAPLE
            consensus_count = mode(stats['copy_counts'])  # Le plus fréquent
        elif appearance_rate >= 0.50:  # 50-69% = FLEX
            consensus_count = median(stats['copy_counts'])
        else:
            continue  # <50% = pas dans le consensus
        
        consensus_main.append({
            'card': card_name,
            'count': consensus_count,
            'confidence': appearance_rate
        })
    
    return consensus_main
```

### 2. **Visualisation du Deck Consensus**

```
🏆 MONO-RED AGGRO - DECK CONSENSUS
Basé sur 24 decks (7+ wins)

MAINBOARD (60 cartes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE (95%+ des decks):
4 Monastery Swiftspear        [████] 100%
4 Play with Fire              [████] 100%
4 Lightning Strike            [████] 96%
4 Kumano Faces Kakkazan      [████] 96%
4 Phoenix Chick               [████] 95%

STAPLES (70-94%):
3 Urabrask's Forge           [███·] 88%
4 Slickshot Show-Off         [████] 83%
2 Manifold Mouse             [██··] 79%
1 Sokenzan, Crucible         [█···] 75%

FLEX SLOTS (50-69%):
2 Torch the Tower            [██··] 67%
1 Feldon, Ronom Excavator    [█···] 54%

LANDS:
18 Mountain                   [████] 100%

Total: 56/60 cartes ✓
Flex slots disponibles: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIDEBOARD (15 cartes)

CORE SB (80%+):
3 Duress                     [███·] 92%
2 Obliterating Bolt          [██··] 88%

COMMON SB (60-79%):
2 Lithomantic Barrage        [██··] 71%
2 Experimental Confectioner  [██··] 67%
1 Chandra, Dressed to Kill   [█···] 63%

TECH CHOICES (40-59%):
2 Ghost Vacuum               [██··] 46%
1 Torch the Tower            [█···] 42%

Total: 13/15 cartes
Flex slots SB: 2
```

### 3. **Export Options**

```python
def export_consensus_deck(consensus_deck, format='mtgo'):
    """
    Exporte dans différents formats
    """
    if format == 'mtgo':
        # Format MTGO
        output = "// MAINBOARD\n"
        for card in consensus_deck.mainboard:
            output += f"{card.count} {card.name}\n"
            
    elif format == 'arena':
        # Format Arena avec set codes
        output = "Deck\n"
        for card in consensus_deck.mainboard:
            output += f"{card.count} {card.name} ({card.set_code})\n"
            
    elif format == 'visual':
        # Format visuel avec barres
        output = generate_visual_decklist(consensus_deck)
        
    return output
```

### 4. **Interface Interactive**

```
┌─────────────────────────────────────┐
│ 🎯 GÉNÉRATEUR DE DECK CONSENSUS     │
├─────────────────────────────────────┤
│ Archétype: [Mono-Red Aggro ▼]      │
│ Période: [7 derniers jours ▼]      │
│ Filtres:                            │
│ ☑ Top 8 uniquement                 │
│ ☑ 6+ wins minimum                  │
│ ☐ Exclure leagues                  │
│                                     │
│ Seuils de consensus:                │
│ Core: [90%▼] Staple: [70%▼]       │
│                                     │
│ [Générer Deck Consensus]            │
└─────────────────────────────────────┘
```

### 5. **Fonctionnalités Avancées**

#### A. **Variance Indicator**
```python
# Pour chaque carte, montrer la variance
"Urabrask's Forge": {
    "consensus": 3,
    "range": "2-4",
    "distribution": {
        2: 25%,
        3: 65%,  # Le plus commun
        4: 10%
    }
}
```

#### B. **Meta-Adjusted Consensus**
```python
def weighted_consensus(decks, weights='performance'):
    """
    Pondère selon la performance
    """
    if weights == 'performance':
        # Trophy = 3x, Top8 = 2x, autres = 1x
        for deck in decks:
            if deck.result == 'trophy':
                weight = 3
            elif deck.is_top8:
                weight = 2
            else:
                weight = 1
```

#### C. **Diff avec sa propre liste**
```
VOTRE LISTE vs CONSENSUS:
------------------------
Mainboard:
✅ 4 Swiftspear (consensus: 4)
⚠️ 2 Urabrask's Forge (consensus: 3) [-1]
❌ 0 Torch the Tower (consensus: 2) [-2]
🆕 2 Rabbit Battery (pas dans consensus)

Score de conformité: 87%
```

## 📊 Cas d'Usage

### Pour les Débutants
- "Je veux jouer Mono-Red, quelle liste?"
- Obtenir LA liste standard/safe

### Pour les Compétiteurs
- Base pour tuning personnel
- Identifier les flex slots
- Comprendre le "core" intouchable

### Pour le Métagame
- Evolution du consensus semaine/semaine
- Impact des nouvelles cartes
- Shifts post-ban/release

## 🎨 Visualisations Complémentaires

### 1. **Evolution Timeline**
```
Semaine 1: 4 Kumano standard
Semaine 2: 3.8 Kumano (baisse)
Semaine 3: 3.2 Kumano (4ème coupé)
```

### 2. **Heatmap Consensus**
```
         S1  S2  S3  S4
Kumano   4   4   3   3
Torch    0   1   2   2
Forge    3   3   3   4
```

### 3. **Confidence Bubbles**
Bulles plus grosses = plus de consensus
Position = mainboard vs sideboard

## 💻 Implementation

```python
class ConsensusDeckGenerator:
    def __init__(self, archetype):
        self.archetype = archetype
        self.decks = []
        
    def add_decks(self, decks):
        # Filtrer par archétype
        self.decks = [d for d in decks if d.archetype == self.archetype]
        
    def generate(self, min_appearance=0.5):
        consensus = {
            'mainboard': self._generate_main(),
            'sideboard': self._generate_side(),
            'metadata': {
                'total_decks': len(self.decks),
                'date_range': self._get_date_range(),
                'confidence': self._calculate_confidence()
            }
        }
        return consensus
        
    def export(self, format='visual'):
        # Différents formats d'export
        pass
```

## 🚀 Valeur Ajoutée

1. **Time Saver** - Plus besoin de moyenner manuellement
2. **Objectivité** - Basé sur données, pas opinions
3. **Découverte** - Voir les trends émergents
4. **Base solide** - Point de départ pour innovation

C'est une feature KILLER pour Manalytics!