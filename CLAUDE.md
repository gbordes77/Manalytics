# 🎯 **Manalytics - Analyseur de Métagame Magic: The Gathering**

## **⚠️ IMPORTANT : Origine du Projet**

Ce projet est un dérivé du pipeline communautaire MTG suivant :

```mermaid
graph TB
    subgraph "Step 1: Data Collection"
        A1[MTGO Platform] -->|Scrapes decklists| B1[mtg_decklist_scrapper<br/>github.com/fbettega/mtg_decklist_scrapper]
        B1 -->|Stores raw data| C1[MTG_decklistcache<br/>github.com/fbettega/MTG_decklistcache]
        
        A2[MTGO Client] -->|Listens for matchups| D1[MTGO-listener<br/>github.com/Jiliac/MTGO-listener]
        D1 -->|Uses SDK| E1[MTGOSDK<br/>github.com/videre-project/MTGOSDK]
        
        C1 -->|Combined with| F1[MTGODecklistCache<br/>github.com/Jiliac/MTGODecklistCache]
        D1 -->|Matchup data| F1
        
        G1[Legacy: MTGODecklistCache.Tools<br/>github.com/Badaro/MTGODecklistCache.Tools<br/>⚠️ Retired by Badaro] -.->|Replaced by| B1
    end
    
    subgraph "Step 2: Data Treatment"
        F1 -->|Raw lists| H2[MTGOArchetypeParser<br/>github.com/Badaro/MTGOArchetypeParser]
        I2[MTGOFormatData<br/>github.com/Badaro/MTGOFormatData<br/>Archetype Rules] -->|Defines parsing logic| H2
        H2 -->|Categorized by archetype| J2[Processed Data<br/>by Format]
        
        K2[Maintainers:<br/>- Jiliac: Most formats<br/>- iamactuallylvl1: Vintage] -->|Maintains rules| I2
    end
    
    subgraph "Step 3: Visualization"
        J2 -->|Archetype data| L3[R-Meta-Analysis Fork<br/>github.com/Jiliac/R-Meta-Analysis]
        L3 -->|Generates| M3[Matchup Matrix<br/>Like the image shown]
        M3 -->|Published to| N3[Discord]
        
        O3[Original: R-Meta-Analysis<br/>github.com/Aliquanto3/R-Meta-Analysis<br/>⚠️ Aliquanto left] -.->|Forked to| L3
    end
```

### **📚 Ressources Clés à Consulter**
Il est important d'aller chercher dans ces repos les codes et ressources qui nous servent de base :
- **mtg_decklist_scrapper** : Notre base pour les scrapers (déjà intégré)
- **MTGOArchetypeParser** : Logique de détection d'archétypes
- **MTGOFormatData** : Règles d'archétypes par format
- **R-Meta-Analysis** : Visualisations et matrices de matchups

## **Objectif Principal**
Collecter, analyser et visualiser les données de tournois Magic: The Gathering pour comprendre le métagame (les decks les plus joués et leurs performances).

## **🔄 Flux de Données**

```
1. SCRAPING
   ↓
MTGO & Melee → Tournois → data/raw/{platform}/{format}/
   ↓
2. TRAITEMENT
   ↓
Parser → Détection d'archétypes → Validation des decks
   ↓
3. STOCKAGE
   ↓
PostgreSQL Database
   ↓
4. ANALYSE
   ↓
Meta % → Matchups → Visualisations
   ↓
5. API
   ↓
FastAPI → Frontend/Rapports
```

## **📦 Composants Principaux**

### 1. **Scrapers** (`scrapers/`)
- **MTGO** : Récupère les tournois depuis www.mtgo.com
- **Melee** : Récupère depuis melee.gg (avec authentification)
- Sauvegarde dans `data/raw/{platform}/{format}/`

### 2. **Parsers** (`src/parsers/`)
- **Archetype Engine** : Identifie le type de deck (Aggro Rouge, Control Bleu, etc.)
- **Decklist Parser** : Valide les listes (60 cartes main, 15 sideboard)
- **Color Identity** : Détermine les couleurs du deck

### 3. **Analyzers** (`src/analyzers/`)
- **Meta Analyzer** : Calcule le % de chaque archétype
- **Matchup Calculator** : Calcule les taux de victoire entre archétypes
- **Tournament Analyzer** : Analyse les performances

### 4. **Database** (`database/`)
- PostgreSQL avec schéma complet
- Tables : tournaments, decklists, cards, matchups, etc.
- Support des migrations Alembic

### 5. **API** (`src/api/`)
- FastAPI avec authentification JWT
- Endpoints pour :
  - Récupérer les données de métagame
  - Analyser des decklists
  - Générer des visualisations
  - Gérer les utilisateurs

### 6. **Visualizations** (`src/visualizers/`)
- Heatmaps de matchups
- Graphiques de distribution du méta
- Évolution temporelle

## **🎮 Formats Supportés**
- Standard
- Modern
- Legacy
- Pioneer
- Pauper
- Vintage
- Commander (Melee)

## **📊 Ce que le projet analyse**
1. **Distribution du Métagame** : Quel % joue chaque deck
2. **Matchups** : Quel deck bat quel deck
3. **Tendances** : Évolution dans le temps
4. **Performance** : Top 8, win rates
5. **Innovation** : Nouveaux decks émergents

## **💡 Cas d'Usage**
- Joueurs compétitifs préparant des tournois
- Comprendre le métagame actuel
- Choisir le meilleur deck
- Adapter son sideboard
- Suivre l'évolution du format

C'est essentiellement un **outil d'intelligence compétitive** pour Magic: The Gathering !

## **🚀 État Actuel**
- ✅ 27 tournois MTGO Standard scrapés (juillet 2025) avec données enrichies
- ✅ 26 Standard Challenges + 1 RC Qualifier avec IDs uniques
- ✅ **15 tournois Melee Standard** scrapés (25 juillet 2025) - **5,362 decklists**
- ✅ Infrastructure complète (DB, API, scrapers)
- ✅ Scrapers robustes avec gestion des doublons et retry logic
- ✅ **Scraper Melee 100% fonctionnel** avec authentification par cookies
- ✅ DataLoader créé pour charger les données existantes
- ✅ Credentials Melee configurés (api_credentials/melee_login.json)
- ⏳ Pipeline d'analyse à tester
- ⏳ Frontend à développer

## **📁 Structure des Données**
```
data/
├── raw/
│   ├── mtgo/
│   │   ├── standard/
│   │   │   ├── challenge/   # 26 challenges avec IDs uniques
│   │   │   └── *.json       # 1 RC Qualifier
│   │   └── modern/          # À scraper
│   └── melee/
│       └── standard/        # Tournois Melee
│           └── leagues/     # Leagues stockées séparément
└── processed/               # Non utilisé actuellement
```

## **🔧 Scripts Importants**
- `scripts/scrape_all_platforms.py` : Script unifié MTGO + Melee (NOUVEAU)
- `scrape_mtgo_tournaments_enhanced.py` : Scraper MTGO avec données enrichies
- **`scrape_melee_working_v2.py`** : Scraper Melee **FONCTIONNEL** (25/07/2025)
- `test_melee_auth_simple.py` : Test d'authentification Melee
- `scripts/run_pipeline_with_existing_data.py` : Pipeline pour données existantes
- `src/utils/data_loader.py` : Charge les données depuis data/raw/

## **⚡ Commandes Utiles**
```bash
# Scraper de nouveaux tournois (script unifié pour MTGO + Melee)
python3 scripts/scrape_all_platforms.py --format standard --start-date 2025-07-01 --end-date 2025-07-24

# Scraper MTGO seul (avec rapport détaillé)
python3 scrape_mtgo_tournaments_enhanced.py --format standard --days 30 --generate-report

# Scraper Melee seul (VERSION FONCTIONNELLE)
python3 scrape_melee_working_v2.py

# Test d'authentification Melee
python3 test_melee_auth_simple.py

# Analyser les données existantes
python3 scripts/run_pipeline_with_existing_data.py --format standard --platform melee

# Voir les données disponibles
python3 -c "from src.utils.data_loader import DataLoader; dl = DataLoader(); print(dl.count_tournaments())"
```

## **📚 Documentation Importante**
- `docs/SCRAPING_BEST_PRACTICES.md` : **LEÇONS CRITIQUES** sur le scraping (notamment pourquoi on ne doit JAMAIS deviner les IDs MTGO)
- **`docs/MELEE_SCRAPING_GUIDE.md`** : Guide complet du scraping Melee avec authentification
- Les IDs MTGO ne sont PAS séquentiels - toujours parser la page de liste officielle
- Les tournois du même jour ont des IDs complètement différents (écarts de 5, 10, 17...)
- L'authentification Melee utilise des cookies valides 21 jours (pas de JWT)