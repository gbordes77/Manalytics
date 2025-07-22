# Analyse des Repositories MTG Analytics Pipeline

## Vue d'ensemble

Ce document analyse les 6 repositories GitHub intégrés dans le pipeline unifié MTG Analytics, détaillant leur structure, dépendances, points d'entrée et formats de données.

## 1. mtg_decklist_scrapper (fbettega)

**Rôle** : Scraping des decklists depuis MTGO, MTGMelee, Topdeck et Manatraders  
**Localisation** : `data-collection/scraper/mtgo/`  
**Maintainer** : fbettega  

### Structure Principale
```
mtg_decklist_scrapper/
├── main.py                    # Point d'entrée adapté pour le pipeline
├── fetch_tournament.py        # Script principal de scraping
├── Client/                    # Clients pour chaque plateforme
│   ├── MTGOclient.py
│   ├── MtgMeleeClient.py
│   ├── TopDeckClient.py
│   └── ManatraderClient.py
├── models/                    # Modèles de données
├── comon_tools/              # Outils communs
├── Api_token_and_login/      # Configuration API
├── requirements.txt          # Dépendances Python
└── README.md
```

### Dépendances Python
```txt
beautifulsoup4
numpy
pytest
python_dateutil
Requests
```

### Points d'Entrée
- **main.py** : Adaptateur pour le pipeline unifié
- **fetch_tournament.py** : Script original de scraping

### Format de Données
```json
{
  "Tournament": {
    "date": "2025-01-15",
    "name": "MTGO Standard Challenge",
    "uri": "https://www.mtgo.com/decklists/...",
    "formats": ["Standard"],
    "json_file": "MTGO/2025/01/15/tournament_12345.json"
  },
  "Decks": [
    {
      "date": "2025-01-15",
      "player": "PlayerName",
      "result": "5-1",
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"}
      ],
      "sideboard": [
        {"count": 2, "card_name": "Abrade"}
      ]
    }
  ],
  "Rounds": [...],
  "Standings": [...]
}
```

### Configuration Requise
- **MTGMelee** : `melee_login.json` avec credentials
- **Topdeck** : `api_topdeck.txt` avec clé API

---

## 2. MTG_decklistcache (fbettega)

**Rôle** : Cache des données brutes scrapées  
**Localisation** : `data-collection/raw-cache/`  
**Maintainer** : fbettega  

### Structure Principale
```
MTG_decklistcache/
├── Tournaments/              # Données actuelles par source/date
│   ├── MTGO/
│   ├── MTGmelee/
│   ├── Topdeck/
│   └── Manatraders/
├── Tournaments-Archive/      # Données archivées
├── MTGO/                     # Données MTGO spécifiques
├── mtgo-standard-sample.json # Exemple de format
└── README.md
```

### Format de Stockage
```
Tournaments/
├── MTGO/2025/01/15/tournament_12345.json
├── MTGmelee/2025/01/15/tournament_67890.json
└── Topdeck/2025/01/15/tournament_11111.json
```

### Mise à Jour
- **MTGO, Melee, Topdeck** : Mise à jour quotidienne vers 17:00 UTC
- **Manatraders** : Mise à jour le lundi suivant le tournoi

---

## 3. MTGODecklistCache (Jiliac)

**Rôle** : Traitement et organisation des données du cache  
**Localisation** : `data-collection/processed-cache/`  
**Maintainer** : Jiliac  

### Structure Principale
```
MTGODecklistCache/
├── Tournaments/              # Données traitées actuelles
├── Tournaments-Archive/      # Données traitées archivées
├── CHANGELOG.md
└── README.md
```

### Statut
⚠️ **Note importante** : Ce projet n'est plus activement maintenu. Le scraper continue de fonctionner jusqu'à ce que les changements sur les sites sources le cassent.

### Limitations Actuelles
- **melee.gg** : Scraper ne fonctionne plus (2025-03-19)
- **manatraders.com** : Scraper désactivé (2025-03-20)
- **mtgo.com** : Données limitées depuis 2024-06-20

---

## 4. MTGOArchetypeParser (Badaro)

**Rôle** : Moteur de détection d'archétypes basé sur des règles  
**Localisation** : `data-treatment/parser/`  
**Maintainer** : Badaro (plus maintenu)  

### Structure Principale
```
MTGOArchetypeParser/
├── main.py                   # Adaptateur Python pour le pipeline
├── MTGOArchetypeParser/      # Bibliothèque principale (.NET)
├── MTGOArchetypeParser.App/  # Application console (.NET)
├── MTGOArchetypeParser.Data/ # Modèles de données (.NET)
├── MTGOArchetypeParser.Tests/ # Tests unitaires
├── MTGOArchetypeParser.sln   # Solution Visual Studio
└── README.md
```

### Dépendances
- **.NET Runtime 8.0** : Requis pour l'exécution
- **MTGOFormatData** : Règles d'archétypes (submodule)

### Points d'Entrée
- **main.py** : Adaptateur Python pour le pipeline
- **MTGOArchetypeParser.App.exe** : Application .NET originale

### Options de Sortie
- `console` : Affichage console
- `csv` : Fichier CSV
- `json` : Fichier JSON
- `reddit` : Format Reddit

### Filtrage
```bash
# Exemples de commandes
format=Modern filter=modern-preliminary-2021-01-21
format=Standard meta=current
format=Legacy startdate=2025-01-01
```

---

## 5. MTGOFormatData (Badaro)

**Rôle** : Définitions d'archétypes et règles de parsing  
**Localisation** : `data-treatment/format-rules/`  
**Maintainers** : Jiliac (formats principaux), IamActuallyLvL1 (Vintage)  

### Structure Principale
```
MTGOFormatData/
├── Formats/                  # Définitions par format
│   ├── Standard/
│   ├── Modern/
│   ├── Legacy/
│   ├── Vintage/
│   ├── Pioneer/
│   └── Pauper/
├── card_colors.json          # Couleurs des cartes (auto-généré)
└── README.md
```

### Structure par Format
```
Formats/Modern/
├── metas.json               # Définition des métas
├── color_overrides.json     # Surcharges de couleurs
├── Archetypes/              # Définitions d'archétypes
│   ├── Burn.json
│   ├── Tron.json
│   └── ...
└── Fallbacks/               # Archétypes génériques
    ├── Aggro.json
    ├── Control.json
    └── ...
```

### Format d'Archétype
```json
{
  "Name": "Burn",
  "IncludeColorInName": true,
  "Conditions": [
    {
      "Type": "InMainboard",
      "Cards": ["Lightning Bolt", "Lava Spike"]
    }
  ],
  "Variants": [...]
}
```

### Types de Conditions
- `InMainboard` / `InSideboard` / `InMainOrSideboard`
- `OneOrMoreInMainboard` / `TwoOrMoreInMainboard`
- `DoesNotContain` / `DoesNotContainMainboard`

### Maintainers Actifs
- **Standard, Pioneer, Modern, Legacy, Pauper** : Jiliac
- **Vintage** : IamActuallyLvL1

---

## 6. R-Meta-Analysis (Jiliac)

**Rôle** : Génération de matrices de matchups et analyses du métagame  
**Localisation** : `visualization/r-analysis/`  
**Maintainer** : Jiliac  
**Fork de** : Aliquanto3/R-Meta-Analysis (Aliquanto a quitté)  

### Structure Principale
```
R-Meta-Analysis/
├── generate_matrix.R         # Script principal adapté
├── Scripts/                  # Scripts R originaux
│   ├── Executables/         # Scripts exécutables
│   ├── Imports/             # Fonctions d'import
│   └── Parameters/          # Paramètres
├── Data/                    # Données externes
├── R Meta Analysis.Rproj    # Projet RStudio
└── README.md
```

### Dépendances R
```r
tidyverse
ggplot2
reshape2
gridExtra
scales
```

### Points d'Entrée
- **generate_matrix.R** : Script principal adapté pour le pipeline
- **Scripts/Executables/** : Scripts R originaux

### Fonctionnalités
- Génération de matrices de matchups
- Analyses du métagame
- Visualisations de données
- Rapports automatiques

---

## Flux de Données Inter-Modules

### Étape 1 : Collecte
```
mtg_decklist_scrapper → MTG_decklistcache
```

### Étape 2 : Traitement
```
MTG_decklistcache → MTGODecklistCache → MTGOArchetypeParser
```

### Étape 3 : Visualisation
```
MTGOArchetypeParser → R-Meta-Analysis
```

### Format de Données Intermédiaire
```json
{
  "tournament_id": "mtgo-standard-20250115",
  "format": "Standard",
  "date": "2025-01-15",
  "decks": [
    {
      "player": "PlayerName",
      "archetype": "Izzet Prowess",
      "result": "5-1",
      "mainboard": [...],
      "sideboard": [...]
    }
  ]
}
```

---

## Points d'Intégration MTGMelee

### API MTGMelee
- **Base URL** : https://melee.gg
- **Authentication** : Login/password requis
- **Rate Limiting** : 2 requêtes/minute
- **Endpoints** : /Decklists, /Tournaments, /api

### Extension Nécessaire
Le module MTGMelee doit être étendu dans `data-collection/scraper/mtgmelee/` pour :
1. Authentification API
2. Récupération des tournois
3. Extraction des decklists
4. Formatage des données

---

## Dépendances Globales

### Python
```txt
beautifulsoup4
numpy
pytest
python_dateutil
requests
```

### R
```r
tidyverse
ggplot2
reshape2
gridExtra
scales
```

### .NET
- .NET Runtime 8.0

---

## Prochaines Étapes

1. **Validation des URLs MTGO** : Vérifier les endpoints exacts
2. **Documentation API MTGMelee** : Compléter la documentation
3. **Tests de Connectivité** : Créer les scripts de test
4. **Extension MTGMelee** : Implémenter le module manquant
5. **Intégration Pipeline** : Connecter tous les modules 