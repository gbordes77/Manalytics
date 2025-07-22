# Formats de Données MTG Analytics Pipeline

## Vue d'Ensemble

Ce document détaille les formats de données utilisés à chaque étape du pipeline MTG Analytics, avec des exemples réels et les spécifications techniques.

## Étape 1 : Données Brutes (Raw Data)

### Format MTG_decklistcache

#### Structure Principale
```json
{
  "Tournament": {
    "date": "2025-01-15",
    "name": "MTGO Standard Challenge",
    "uri": "https://www.mtgo.com/decklists/standard-challenge-2025-01-15",
    "formats": ["Standard"],
    "json_file": "MTGO/2025/01/15/standard-challenge-2025-01-15.json",
    "force_redownload": false
  },
  "Decks": [
    {
      "date": "2025-01-15",
      "player": "PlayerName",
      "result": "5-1",
      "anchor_uri": "https://www.mtgo.com/decklists/player-deck-12345",
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"},
        {"count": 4, "card_name": "Ragavan, Nimble Pilferer"},
        {"count": 20, "card_name": "Mountain"}
      ],
      "sideboard": [
        {"count": 2, "card_name": "Fury"},
        {"count": 1, "card_name": "Engineered Explosives"}
      ]
    }
  ],
  "Rounds": [
    {
      "round_name": "Quarterfinals",
      "matches": [
        {
          "player1": "PlayerName1",
          "player2": "PlayerName2",
          "result": "2-1",
          "id": "match1"
        }
      ]
    }
  ],
  "Standings": [
    {
      "rank": 1,
      "player": "PlayerName",
      "points": 15,
      "wins": 5,
      "losses": 0,
      "draws": 0,
      "omwp": 0.67,
      "gwp": 0.75,
      "ogwp": 0.71
    }
  ]
}
```

#### Exemple Réel - MTGO Standard Challenge
```json
{
  "Tournament": {
    "date": "2025-01-15",
    "name": "Standard Challenge",
    "uri": "https://magic.wizards.com/en/articles/archive/mtgo-standings/standard-challenge-2025-01-15",
    "formats": ["Standard"],
    "json_file": "MTGO/2025/01/15/standard-challenge-2025-01-15.json"
  },
  "Decks": [
    {
      "date": "2025-01-15",
      "player": "yamakiller",
      "result": "5-0",
      "anchor_uri": "https://www.mtgo.com/decklists/standard-challenge-2025-01-15-yamakiller",
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"},
        {"count": 4, "card_name": "Ragavan, Nimble Pilferer"},
        {"count": 4, "card_name": "Monastery Swiftspear"},
        {"count": 4, "card_name": "Lava Spike"},
        {"count": 4, "card_name": "Rift Bolt"},
        {"count": 4, "card_name": "Skewer the Critics"},
        {"count": 4, "card_name": "Searing Blaze"},
        {"count": 4, "card_name": "Eidolon of the Great Revel"},
        {"count": 4, "card_name": "Skullcrack"},
        {"count": 4, "card_name": "Lightning Strike"},
        {"count": 20, "card_name": "Mountain"}
      ],
      "sideboard": [
        {"count": 2, "card_name": "Fury"},
        {"count": 2, "card_name": "Smash to Smithereens"},
        {"count": 2, "card_name": "Destructive Revelry"},
        {"count": 2, "card_name": "Searing Blood"},
        {"count": 2, "card_name": "Skullcrack"},
        {"count": 2, "card_name": "Exquisite Firecraft"},
        {"count": 2, "card_name": "Grim Lavamancer"},
        {"count": 1, "card_name": "Engineered Explosives"}
      ]
    }
  ]
}
```

### Format MTGMelee (Extension)

#### Structure Proposée
```json
{
  "Tournament": {
    "date": "2025-01-15",
    "name": "MTGMelee Standard Open",
    "uri": "https://melee.gg/Tournament/View/12345",
    "formats": ["Standard"],
    "source": "MTGMelee",
    "tournament_id": "12345"
  },
  "Decks": [
    {
      "date": "2025-01-15",
      "player": "PlayerName",
      "result": "5-1",
      "rank": 3,
      "decklist_id": "67890",
      "anchor_uri": "https://melee.gg/Decklist/View/67890",
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"}
      ],
      "sideboard": [
        {"count": 2, "card_name": "Abrade"}
      ]
    }
  ]
}
```

## Étape 2 : Données Traitées (Processed Data)

### Format MTGOArchetypeParser

#### Structure Principale
```json
{
  "tournament_id": "mtgo-standard-20250115",
  "source": "MTGO",
  "name": "Standard Challenge",
  "format": "Standard",
  "date": "2025-01-15",
  "url": "https://magic.wizards.com/en/articles/archive/mtgo-standings/standard-challenge-2025-01-15",
  "decks": [
    {
      "deck_id": "mtgo-standard-20250115-deck-1",
      "player_name": "yamakiller",
      "archetype": "Burn",
      "rank": 1,
      "result": "5-0",
      "mainboard": [
        {
          "card_name": "Lightning Bolt",
          "quantity": 4
        }
      ],
      "sideboard": [
        {
          "card_name": "Fury",
          "quantity": 2
        }
      ],
      "matches": []
    }
  ]
}
```

#### Exemple Réel - Sortie MTGOArchetypeParser
```json
{
  "tournament_id": "modern-preliminary-2021-01-21",
  "source": "MTGO",
  "name": "Modern Preliminary",
  "format": "Modern",
  "date": "2021-01-21",
  "decks": [
    {
      "deck_id": "modern-preliminary-2021-01-21-yamakiller",
      "player_name": "yamakiller",
      "archetype": "Burn",
      "rank": 1,
      "result": "4-0",
      "mainboard": [
        {"card_name": "Lightning Bolt", "quantity": 4},
        {"card_name": "Lava Spike", "quantity": 4},
        {"card_name": "Rift Bolt", "quantity": 4},
        {"card_name": "Skewer the Critics", "quantity": 4},
        {"card_name": "Monastery Swiftspear", "quantity": 4},
        {"card_name": "Eidolon of the Great Revel", "quantity": 4},
        {"card_name": "Goblin Guide", "quantity": 4},
        {"card_name": "Searing Blaze", "quantity": 4},
        {"card_name": "Skullcrack", "quantity": 4},
        {"card_name": "Lightning Strike", "quantity": 4},
        {"card_name": "Mountain", "quantity": 20}
      ],
      "sideboard": [
        {"card_name": "Fury", "quantity": 2},
        {"card_name": "Smash to Smithereens", "quantity": 2},
        {"card_name": "Destructive Revelry", "quantity": 2},
        {"card_name": "Searing Blood", "quantity": 2},
        {"card_name": "Skullcrack", "quantity": 2},
        {"card_name": "Exquisite Firecraft", "quantity": 2},
        {"card_name": "Grim Lavamancer", "quantity": 2},
        {"card_name": "Engineered Explosives", "quantity": 1}
      ]
    }
  ]
}
```

### Format CSV MTGOArchetypeParser

#### Structure
```csv
Tournament,Player,Result,Archetype,Rank,Date,Format
modern-preliminary-2021-01-21,yamakiller,4-0,Burn,1,2021-01-21,Modern
modern-preliminary-2021-01-21,Simpleliquid,4-0,Spirits,1,2021-01-21,Modern
modern-preliminary-2021-01-21,cntrlfreak,3-1,Shadow Prowess,3,2021-01-21,Modern
```

#### Exemple Réel
```csv
Tournament,Player,Result,Archetype,Rank,Date,Format
modern-preliminary-2021-01-2112252742,yamakiller,4-0,Burn,1,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,Simpleliquid,4-0,Spirits,1,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,cntrlfreak,3-1,Shadow Prowess,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,ElectricBob,3-1,Rakdos Midrange,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,cariollins,3-1,Shadow Prowess,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,HouseOfManaMTG,3-1,Amulet Titan,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252742,aplapp,3-1,Heliod Combo,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,kthanakit26,4-0,Izzet Prowess,1,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,SourceOdin,3-1,Heliod Combo,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,Dean911,2-1,Green Tron,2,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,Rosencrantz_920,3-1,Amulet Titan,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,Rinko,3-1,Enduring Ideal,3,2021-01-21,Modern
modern-preliminary-2021-01-2112252745,errorman,3-1,Gyruda Reanimator,3,2021-01-21,Modern
```

## Étape 3 : Données de Visualisation (Visualization Data)

### Format R-Meta-Analysis

#### Structure des Données d'Entrée
```r
# Données d'archétypes
archetype_data <- data.frame(
  tournament_id = c("modern-preliminary-2021-01-21", "modern-preliminary-2021-01-21"),
  player = c("yamakiller", "Simpleliquid"),
  archetype = c("Burn", "Spirits"),
  result = c("4-0", "4-0"),
  rank = c(1, 1),
  date = as.Date(c("2021-01-21", "2021-01-21")),
  format = c("Modern", "Modern")
)
```

#### Matrice de Matchups
```r
# Matrice de matchups entre archétypes
matchup_matrix <- matrix(
  c(0.50, 0.45, 0.55, 0.60, 0.40, 0.65,
    0.55, 0.50, 0.48, 0.52, 0.58, 0.42,
    0.45, 0.52, 0.50, 0.47, 0.53, 0.49,
    0.40, 0.48, 0.53, 0.50, 0.45, 0.55,
    0.60, 0.42, 0.47, 0.55, 0.50, 0.51,
    0.35, 0.58, 0.51, 0.45, 0.49, 0.50),
  nrow = 6, ncol = 6,
  dimnames = list(
    c("Burn", "Spirits", "Shadow Prowess", "Rakdos Midrange", "Amulet Titan", "Heliod Combo"),
    c("Burn", "Spirits", "Shadow Prowess", "Rakdos Midrange", "Amulet Titan", "Heliod Combo")
  )
)
```

#### Métadonnées du Métagame
```r
# Répartition du métagame
metagame_breakdown <- data.frame(
  archetype = c("Burn", "Spirits", "Shadow Prowess", "Rakdos Midrange", "Amulet Titan", "Heliod Combo", "Green Tron", "Enduring Ideal", "Gyruda Reanimator", "Izzet Prowess"),
  count = c(1, 1, 2, 1, 2, 2, 1, 1, 1, 1),
  percentage = c(7.69, 7.69, 15.38, 7.69, 15.38, 15.38, 7.69, 7.69, 7.69, 7.69),
  rank = c(1, 1, 3, 3, 3, 3, 2, 3, 3, 1)
)
```

### Format de Sortie HTML

#### Structure du Rapport
```html
<!DOCTYPE html>
<html>
<head>
    <title>MTG Analytics - Modern Metagame Analysis</title>
    <style>
        /* Styles CSS pour la présentation */
    </style>
</head>
<body>
    <h1>Modern Metagame Analysis</h1>
    <h2>Date: 2021-01-21</h2>
    
    <h3>Metagame Breakdown</h3>
    <table>
        <tr><th>Archetype</th><th>Count</th><th>Percentage</th></tr>
        <tr><td>Burn</td><td>1</td><td>7.69%</td></tr>
        <tr><td>Spirits</td><td>1</td><td>7.69%</td></tr>
        <!-- ... -->
    </table>
    
    <h3>Matchup Matrix</h3>
    <div id="matchup-matrix">
        <!-- Matrice de matchups générée -->
    </div>
    
    <h3>Top Performing Decks</h3>
    <div id="top-decks">
        <!-- Liste des meilleurs decks -->
    </div>
</body>
</html>
```

## Formats de Configuration

### MTGOFormatData - Définition d'Archétype

#### Structure Complète
```json
{
  "Name": "Burn",
  "IncludeColorInName": true,
  "Conditions": [
    {
      "Type": "InMainboard",
      "Cards": ["Lightning Bolt", "Lava Spike", "Rift Bolt"]
    },
    {
      "Type": "TwoOrMoreInMainboard",
      "Cards": ["Monastery Swiftspear", "Goblin Guide", "Eidolon of the Great Revel"]
    }
  ],
  "Variants": [
    {
      "Name": "Mono-Red Burn",
      "Conditions": [
        {
          "Type": "DoesNotContainMainboard",
          "Cards": ["Boros Charm", "Lightning Helix"]
        }
      ]
    },
    {
      "Name": "Boros Burn",
      "Conditions": [
        {
          "Type": "InMainboard",
          "Cards": ["Boros Charm", "Lightning Helix"]
        }
      ]
    }
  ]
}
```

#### Exemple Réel - Modern Burn
```json
{
  "Name": "Burn",
  "IncludeColorInName": true,
  "Conditions": [
    {
      "Type": "InMainboard",
      "Cards": ["Lightning Bolt"]
    },
    {
      "Type": "InMainboard",
      "Cards": ["Lava Spike"]
    },
    {
      "Type": "InMainboard",
      "Cards": ["Rift Bolt"]
    },
    {
      "Type": "InMainboard",
      "Cards": ["Skewer the Critics"]
    },
    {
      "Type": "TwoOrMoreInMainboard",
      "Cards": ["Monastery Swiftspear", "Goblin Guide", "Eidolon of the Great Revel"]
    }
  ]
}
```

### Configuration des Sources

#### Structure sources.json
```json
{
  "mtgo": {
    "base_url": "https://www.mtgo.com/decklists",
    "api_endpoints": {
      "decklists": "https://www.mtgo.com/decklists",
      "tournaments": "https://www.mtgo.com/tournaments",
      "standings": "https://www.mtgo.com/standings"
    },
    "scraping_config": {
      "rate_limit": 1,
      "retry_attempts": 5,
      "timeout": 30
    },
    "formats": ["Standard", "Modern", "Legacy", "Vintage", "Pioneer", "Pauper"]
  },
  "mtgmelee": {
    "base_url": "https://melee.gg",
    "api_endpoints": {
      "decklists": "https://melee.gg/Decklists",
      "tournaments": "https://melee.gg/Tournaments"
    },
    "authentication": {
      "login_url": "https://melee.gg/login",
      "credentials_file": "data-collection/scraper/mtgo/melee_login.json"
    }
  }
}
```

## Validation des Données

### Règles de Validation

#### Données Brutes
- **Tournament** : date, name, uri, formats requis
- **Decks** : player, result, mainboard requis
- **Cards** : count > 0, card_name non vide

#### Données Traitées
- **Archetype** : doit correspondre à une définition MTGOFormatData
- **Result** : format "X-Y" où X, Y sont des entiers
- **Rank** : entier positif

#### Données de Visualisation
- **Matchup Matrix** : valeurs entre 0 et 1, diagonale = 0.5
- **Metagame** : pourcentages somment à 100%

### Exemples d'Erreurs

#### Données Invalides
```json
{
  "Decks": [
    {
      "player": "",  // ❌ Nom de joueur vide
      "result": "invalid",  // ❌ Format de résultat invalide
      "mainboard": [
        {"count": 0, "card_name": "Lightning Bolt"}  // ❌ Quantité nulle
      ]
    }
  ]
}
```

#### Données Valides
```json
{
  "Decks": [
    {
      "player": "yamakiller",  // ✅ Nom valide
      "result": "4-0",  // ✅ Format valide
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"}  // ✅ Quantité valide
      ]
    }
  ]
}
```

## Migration et Compatibilité

### Versions des Formats

#### Version 1.0 (Actuelle)
- Format JSON standard pour MTG_decklistcache
- CSV pour MTGOArchetypeParser
- R DataFrames pour R-Meta-Analysis

#### Version 2.0 (Planifiée)
- Support des matchups détaillés
- Métadonnées enrichies
- API REST pour l'accès aux données

### Migration des Données
```python
def migrate_v1_to_v2(data_v1):
    """Migration du format v1 vers v2"""
    data_v2 = {
        "version": "2.0",
        "tournament": data_v1["Tournament"],
        "decks": []
    }
    
    for deck in data_v1["Decks"]:
        deck_v2 = {
            "player": deck["player"],
            "result": deck["result"],
            "mainboard": deck["mainboard"],
            "sideboard": deck.get("sideboard", []),
            "metadata": {
                "source": "v1_migration",
                "migrated_at": datetime.now().isoformat()
            }
        }
        data_v2["decks"].append(deck_v2)
    
    return data_v2
``` 