# 🎯 **Manalytics - Analyseur de Métagame Magic: The Gathering**

> **"Chaque visualisation doit raconter une histoire. Pas de graphs pour faire joli - uniquement des insights actionnables pour gagner des tournois."**
> 
> **Chaque visualisation doit apporter de la valeur compétitive réelle.**

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

## **🚀 État Actuel (25/07/2025)**

### ✅ Phase 1 COMPLÈTE : Collection de Données
- **Scrapers avec decklists complètes** - MTGO (enhanced) + Melee (Records field)
- **Juillet 2025 scrapé** - 53 tournois MTGO + 14 Melee = ~1346 decklists
- **Correction du problème initial** : Les scrapers récupèrent maintenant les decklists complètes (mainboard + sideboard)

### ✅ Phase 2 COMPLÈTE : Pipeline de Traitement
- **Cache SQLite** : Metadata + JSON decklists storage
- **Parser d'archétypes** : 44 règles Standard intégrées (basé sur MTGOArchetypeParser)
- **Détecteur de couleurs** : 28,000+ cartes database (card_colors.json)
- **Performance** : <500ms par tournoi
- **Visualisations** : Charts interactifs avec noms complets (Izzet, Naya, etc.)

### 🚀 Phase 3 EN COURS : Visualisations Avancées & Insights Compétitifs
**Réalisations Phase 3 :**
- ✅ **Analyse sans leagues** : `data/cache/standard_analysis_no_leagues.html` - Focus sur les tournois compétitifs uniquement
- ✅ **Règles d'archétypes customisées** : "Izzet Prowess (Cauldron)" → "Izzet Cauldron" (fichier créé : `IzzetCauldron.json`)
- ✅ **Visualisation interactive** : Charts.js avec pie chart, bar charts et tableaux détaillés
- ✅ **Comparaison avec/sans leagues** : Statistiques comparatives intégrées

**En développement (autonomie créative) :**
1. **Dashboard temps réel** - Métagame evolution avec WebSockets
2. **Heatmap de matchups** - Win rates entre archétypes  
3. **Innovation Detector** - Détection automatique des tech choices émergentes
4. **Consensus Deck Generator** - LA liste optimale générée par ML
5. **Sideboard Intelligence** - Patterns et suggestions automatiques

**Documentation Phase 3** :
  - `docs/PHASE3_VISUALIZATIONS_ROADMAP.md` - 30+ visualisations planifiées
  - `docs/CONSENSUS_DECK_GENERATOR.md` - Feature unique : génération automatique de LA liste optimale
  - `docs/INNOVATION_DETECTOR_CONCEPT.md` - Détection des tech choices émergentes
  - `docs/DECK_COMPARISON_FEATURE.md` - Comparaison visuelle multi-listes
  - `docs/SIDEBOARD_GUIDE_MATRIX_EXAMPLE.md` - Guide sideboard interactif
  - `docs/PROJECT_SUMMARY_DIFFERENTIATORS.md` - Nos avantages concurrentiels

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

## **🔧 Architecture Moderne (25/07/2025)**
- **CLI Principal** : `manalytics` - Point d'entrée unique
- **Orchestrateur** : `src/manalytics/orchestrator.py` - Coordonne tout
- **Scrapers** : Dans `src/manalytics/scrapers/` (MTGO + Melee)
- **Configuration** : `.env` + `src/manalytics/config.py`
- **Structure** : 100% professionnelle dans `src/manalytics/`

## **📊 État Actuel du Métagame Standard (25/07/2025) - Sans Leagues**
```
1. Izzet Cauldron - 20.0% (125 decks)
2. Dimir Midrange - 19.4% (121 decks)  
3. Golgari Midrange - 4.7% (29 decks)
4. Mono White Caretaker - 4.3% (27 decks)
5. Boros Convoke - 3.5% (22 decks)

Total: 41 tournois compétitifs, 624 decks analysés
```

## **⚡ Commandes Utiles (NOUVEAU SYSTÈME)**
```bash
# Installation complète
make install-dev

# Vérifier le système
manalytics status

# Pipeline complet (scrape → parse → analyze → visualize)
manalytics pipeline --format standard --days 7

# Scraper seul
manalytics scrape --format standard --platform all --days 7

# Analyser les données existantes
manalytics analyze --format standard

# Lancer l'API
manalytics serve

# Ancienne méthode (si besoin)
python3 scripts/scrape_all_platforms.py --format standard --days 7

# Analyser les données existantes  
python3 scripts/run_pipeline_with_existing_data.py --format standard --platform melee

# Phase 2: Cache processing et visualisation
python3 scripts/process_all_standard_data.py
python3 scripts/create_archetype_visualization.py
python3 scripts/show_cache_stats.py

# Voir les données disponibles
python3 -c "from src.utils.data_loader import DataLoader; dl = DataLoader(); print(dl.count_tournaments())"
```

## **📚 Documentation Importante**
- `docs/SCRAPING_BEST_PRACTICES.md` : **LEÇONS CRITIQUES** sur le scraping (notamment pourquoi on ne doit JAMAIS deviner les IDs MTGO)
- **`docs/MELEE_SCRAPING_GUIDE.md`** : Guide complet du scraping Melee avec authentification
- **`docs/MTGO_SCRAPING_GUIDE.md`** : Guide complet du scraping MTGO (pas d'auth requise)
- **`docs/CACHE_SYSTEM_IMPLEMENTATION.md`** : Architecture complète du système de cache Phase 2
- Les IDs MTGO ne sont PAS séquentiels - toujours parser la page de liste officielle
- Les tournois du même jour ont des IDs complètement différents (écarts de 5, 10, 17...)
- L'authentification Melee utilise des cookies valides 21 jours (pas de JWT)

## ⛔️ RÈGLES CRITIQUES DE SÉCURITÉ ⛔️

### NE JAMAIS TOUCHER AU DOSSIER `obsolete/`
- **INTERDICTION ABSOLUE** d'exécuter tout fichier dans `obsolete/`
- **INTERDICTION** de lire ou analyser le code obsolète
- **INTERDICTION** d'importer ou référencer ces fichiers
- Si l'utilisateur demande d'utiliser un fichier obsolète : **REFUSER** et proposer l'alternative actuelle

### Fichiers Actuels à Utiliser
- **Scraper Melee** : `scrape_melee_from_commit.py` (standalone, fonctionnel)
- **Scraper MTGO** : `scrape_mtgo_standalone.py` (standalone, fonctionnel)
- **Validation** : `scripts/validate_against_decklistcache.py`
- **Test Auth** : `test_melee_auth_simple.py`

## 📝 RÈGLE DE DOCUMENTATION

**Quand l'utilisateur confirme qu'un module fonctionne** ("c'est ok", "ça fonctionne", etc.) :
1. **CRÉER IMMÉDIATEMENT** un guide complet dans `docs/`
2. **Format** : `{MODULE}_SCRAPING_GUIDE.md` ou `{MODULE}_GUIDE.md`
3. **Contenu obligatoire** :
   - Vue d'ensemble avec résultats obtenus
   - Architecture détaillée du code
   - Guide d'utilisation complet
   - Points techniques importants
   - Leçons apprises
4. **Exemples créés** : `MELEE_SCRAPING_GUIDE.md`, `MTGO_SCRAPING_GUIDE.md`

## 🚨 RÈGLES DE SCRAPING OBLIGATOIRES

1. **TOUJOURS DEMANDER LA PÉRIODE** : Ne JAMAIS utiliser "7 jours" par défaut. Toujours demander à l'utilisateur quelle période scraper.
2. **FORMAT PAR DÉFAUT = STANDARD** : Sauf contre-ordre explicite, toujours scraper le format Standard uniquement.
3. **CONFIRMATION AVANT LANCEMENT** : Toujours confirmer la période et le format avant de lancer un scraping.

## ⚠️ RÈGLE ABSOLUE : EXCLUSION DES LEAGUES

**LES LEAGUES (5-0) SONT STOCKÉES DANS UN DOSSIER `leagues/` SÉPARÉ ET NE DOIVENT JAMAIS ÊTRE UTILISÉES DANS LES ANALYSES OU VISUALISATIONS.**

Raison : Les leagues ne représentent pas des tournois compétitifs mais des résultats de ladder filtrés. Seuls les vrais tournois (challenges, qualifiers, etc.) doivent être analysés.