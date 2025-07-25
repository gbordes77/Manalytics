# 🔧 Implementation Technique du Hover IN/OUT

## ❓ Le Problème : Comment savoir quoi IN/OUT ?

Actuellement, nos données JSON ont :
- ✅ Les decklists complètes (mainboard + sideboard)
- ❌ PAS d'info sur ce qui entre/sort pendant les matchs

## 💡 La Solution : Analyse Statistique des Patterns

### 1. **Données qu'on a VRAIMENT**
```json
{
  "player": "SoulStrong",
  "mainboard": [
    {"count": 4, "card_name": "Cut Down"},
    {"count": 3, "card_name": "Go for the Throat"},
    // ...
  ],
  "sideboard": [
    {"count": 2, "card_name": "Ghost Vacuum"},
    {"count": 3, "card_name": "Duress"},
    // ...
  ]
}
```

### 2. **Comment déduire les guides IN/OUT**

#### Méthode 1 : Analyse Statistique des Sideboards
```python
def analyze_sideboard_patterns(archetype_A, archetype_B):
    """
    Analyse tous les matchs A vs B pour trouver les patterns
    """
    sideboard_usage = {}
    
    # Pour chaque deck de type A
    for deck_A in archetype_A_decks:
        # Regarder quelles cartes de side sont communes
        for card in deck_A.sideboard:
            if card in anti_archetype_B_cards:  # Base de données de cartes
                sideboard_usage[card] += 1
    
    # Les cartes les plus fréquentes = IN probables
    return sorted(sideboard_usage, by=frequency)
```

#### Méthode 2 : Base de Connaissances MTG
```python
SIDEBOARD_KNOWLEDGE = {
    "Duress": {
        "good_against": ["Control", "Combo"],
        "bad_against": ["Aggro"],
        "typically_replaces": ["removal", "expensive_spells"]
    },
    "Ghost Vacuum": {
        "good_against": ["Graveyard", "Reanimator"],
        "typically_replaces": ["generic_removal"]
    },
    "Negate": {
        "good_against": ["Control", "Midrange"],
        "bad_against": ["Aggro"],
        "typically_replaces": ["creatures", "removal"]
    }
}
```

#### Méthode 3 : Patterns par Coût de Mana
```python
def suggest_cuts_by_curve(deck, matchup):
    """
    Contre Aggro : OUT cartes chères, IN removal cheap
    Contre Control : OUT removal, IN menaces/counters
    """
    if matchup == "vs_aggro":
        # Suggérer de sortir les cartes 4+ mana
        cuts = [card for card in deck if card.cmc >= 4]
    elif matchup == "vs_control":
        # Suggérer de sortir les removals 1-2 mana
        cuts = [card for card in deck if card.type == "removal" and card.cmc <= 2]
```

### 3. **Implémentation Concrète avec Plotly**

```python
import plotly.graph_objects as go

def create_sideboard_matrix():
    # Créer la heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matchup_scores,
        x=archetypes,
        y=archetypes,
        customdata=sideboard_guides,  # Les guides IN/OUT
        hovertemplate='''
        <b>%{y} vs %{x}</b><br>
        <br>
        <b>Suggested Plan:</b><br>
        %{customdata}
        <extra></extra>
        ''',
    ))
    
    return fig

# Structure des guides
sideboard_guides = {
    "UB_Faeries_vs_MonoRed": """
        <b>OUT (7):</b><br>
        -4 Faerie Mastermind<br>
        -3 Spell Stutter<br>
        <br>
        <b>IN (7):</b><br>
        +3 Experimental Confectioner<br>
        +2 Sheoldred's Edict<br>
        +2 Ghost Vacuum<br>
        <br>
        💡 Focus on surviving early
    """
}
```

### 4. **Sources de Données Réelles**

#### Option A : Crowdsourcing
- Les joueurs soumettent leurs guides
- Validation par win rate
- Système de votes

#### Option B : Analyse des Résultats
```python
# Si on avait les decklists round par round
def analyze_actual_sideboards(round_data):
    game1_deck = round_data.game1
    game2_deck = round_data.game2
    
    cards_out = game1_deck - game2_deck
    cards_in = game2_deck - game1_deck
    
    return cards_in, cards_out
```

#### Option C : Intelligence Artificielle
```python
# Entraîner un modèle sur des guides connus
def predict_sideboard_plan(deck_A, deck_B):
    features = extract_features(deck_A, deck_B)
    # Cartes removal, threats, interaction, etc.
    
    prediction = model.predict(features)
    return prediction.in_cards, prediction.out_cards
```

### 5. **Ce qu'on peut faire MAINTENANT**

```python
# 1. Créer des guides basiques basés sur les patterns connus
BASIC_SIDEBOARD_RULES = {
    ("Aggro", "Control"): {
        "in": ["Duress", "Negate", "Planeswalkers"],
        "out": ["Removal", "Sweepers"]
    },
    ("Control", "Aggro"): {
        "in": ["Cheap Removal", "Lifegain", "Sweepers"],
        "out": ["Counterspells", "Card Draw"]
    }
}

# 2. Analyser les sideboards populaires
def get_common_sideboard_cards(archetype, opponent):
    cards = []
    for deck in archetype_decks:
        for card in deck.sideboard:
            if is_good_against(card, opponent):
                cards.append(card)
    
    return Counter(cards).most_common(5)

# 3. Afficher dans le hover
hover_text = f"""
{archetype_A} vs {archetype_B}
------------------------
Cartes populaires en side:
{format_popular_cards(common_sb_cards)}

Guide suggéré (basé sur {n} decks):
IN: {suggested_in}
OUT: {suggested_out}

⚠️ Guide généré automatiquement
"""
```

## 🎯 Résumé : C'est Faisable !

**On ne peut pas** : Savoir exactement ce que chaque joueur a sideboard

**On peut** :
1. Déduire les patterns statistiques
2. Utiliser la connaissance MTG (Duress vs Control, etc.)
3. Analyser les sideboards les plus fréquents
4. Suggérer des plans basés sur la théorie
5. Améliorer avec le crowdsourcing

**Le hover montrera** :
- Les cartes de side les plus jouées pour ce matchup
- Un guide suggéré basé sur les patterns
- Un disclaimer "généré automatiquement"
- Option pour les utilisateurs de corriger/améliorer