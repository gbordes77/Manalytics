# Diagramme Complet du Pipeline MTG Analytics Unifié

## Architecture Complète du Pipeline

```mermaid
graph TB
    %% ===== NOUVEAUX COMPOSANTS D'ORCHESTRATION =====
    subgraph "🎯 ORCHESTRATION UNIFIÉE"
        O1[orchestrator.py<br/>Pipeline Principal] -->|Coordonne tout| O2[analyze.py<br/>Interface Utilisateur]
        O2 -->|Lance| O1
        O3[generate_analysis.sh<br/>Script d'automatisation] -->|Exécute| O1
        O4[test_connections.py<br/>Validation Système] -->|Vérifie| O5[config/sources.json<br/>Configuration Centralisée]
    end

    %% ===== ÉTAPE 1: COLLECTE DE DONNÉES =====
    subgraph "📊 ÉTAPE 1: COLLECTE DE DONNÉES"
        %% Sources de données
        A1[MTGO Platform<br/>https://www.mtgo.com] -->|Scrapes decklists| B1[mtg_decklist_scrapper<br/>github.com/fbettega/mtg_decklist_scrapper<br/>[Python]]
        A2[MTGMelee Platform<br/>https://melee.gg] -->|API calls| B2[mtgmelee_client.py<br/>Client API MTGMelee<br/>[Python]]
        A3[Topdeck Platform<br/>https://topdeck.gg] -->|API calls| B3[topdeck_client.py<br/>Client API Topdeck<br/>[Python]]
        
        %% Cache et traitement
        B1 -->|Stores raw data| C1[MTG_decklistcache<br/>github.com/fbettega/MTG_decklistcache<br/>[Python]]
        B2 -->|Stores raw data| C1
        B3 -->|Stores raw data| C1
        C1 -->|Processes| F1[MTGODecklistCache<br/>github.com/Jiliac/MTGODecklistCache<br/>[Python]]
        
        %% Gestionnaire de cache unifié
        C1 -->|Managed by| G1[cache_manager.py<br/>Gestionnaire de Cache Unifié<br/>[Python]]
        F1 -->|Managed by| G1
        
        %% Legacy (désactivé)
        H1[Legacy: MTGODecklistCache.Tools<br/>github.com/Badaro/MTGODecklistCache.Tools<br/>⚠️ Retired by Badaro] -.->|Replaced by| B1
    end
    
    %% ===== ÉTAPE 2: TRAITEMENT DES DONNÉES =====
    subgraph "🔧 ÉTAPE 2: TRAITEMENT DES DONNÉES"
        F1 -->|Raw lists| I2[MTGOArchetypeParser<br/>github.com/Badaro/MTGOArchetypeParser<br/>[C#/.NET]]
        J2[MTGOFormatData<br/>github.com/Badaro/MTGOFormatData<br/>Règles d'Archétypes<br/>[JSON]] -->|Defines parsing logic| I2
        I2 -->|Categorized by archetype| K2[Processed Data<br/>by Format<br/>[JSON]]
        
        %% Mainteneurs
        L2[Maintainers:<br/>- Jiliac: Most formats<br/>- iamactuallylvl1: Vintage] -->|Maintains rules| J2
        
        %% Adapter Python pour C#
        M2[parser/main.py<br/>Adapter Python pour C#<br/>[Python]] -->|Calls| I2
    end
    
    %% ===== ÉTAPE 3: VISUALISATION =====
    subgraph "📈 ÉTAPE 3: VISUALISATION"
        K2 -->|Archetype data| N3[R-Meta-Analysis Fork<br/>github.com/Jiliac/R-Meta-Analysis<br/>[R]]
        N3 -->|Generates| O3[Matchup Matrix<br/>[HTML/PNG]]
        O3 -->|Published to| P3[Discord]
        
        %% Adapter Python pour R
        Q3[visualization/r-analysis/generate_matrix.R<br/>Adapter Python pour R<br/>[R]] -->|Calls| N3
        
        %% Original (désactivé)
        R3[Original: R-Meta-Analysis<br/>github.com/Aliquanto3/R-Meta-Analysis<br/>⚠️ Aliquanto left] -.->|Forked to| N3
    end
    
    %% ===== NOUVEAUX COMPOSANTS DE SORTIE =====
    subgraph "🎨 SORTIE ET ANALYSES"
        O3 -->|Stored in| S1[analyses/<br/>Dossier des Analyses<br/>[HTML/JSON/CSV]]
        S1 -->|Contains| S2[Rapports Complets<br/>[HTML]]
        S1 -->|Contains| S3[Graphiques Interactifs<br/>[HTML]]
        S1 -->|Contains| S4[Données Structurées<br/>[JSON/CSV]]
        
        %% Ouverture automatique
        S2 -->|Auto-opens| T1[Browser<br/>Affichage Automatique]
        S3 -->|Auto-opens| T1
    end
    
    %% ===== NOUVEAUX COMPOSANTS DE CONFIGURATION =====
    subgraph "⚙️ CONFIGURATION ET VALIDATION"
        O5 -->|Configures| U1[Sources de Données<br/>MTGO, MTGMelee, Topdeck]
        O5 -->|Configures| U2[Formats Supportés<br/>Standard, Modern, Legacy, etc.]
        O5 -->|Configures| U3[Paramètres de Scraping<br/>Rate limits, timeouts]
        
        O4 -->|Validates| V1[Connectivité Internet]
        O4 -->|Validates| V2[Dépendances Python]
        O4 -->|Validates| V3[Présence des Repositories]
        O4 -->|Validates| V4[Configuration Système]
    end
    
    %% ===== NOUVEAUX COMPOSANTS DE DOCUMENTATION =====
    subgraph "📚 DOCUMENTATION COMPLÈTE"
        W1[docs/JILIAC_SYSTEM_BIBLE.md<br/>Bible Complète du Système<br/>[Markdown]] -->|Documents| W2[Tous les Composants]
        W3[docs/ARCHITECTURE.md<br/>Architecture Détaillée<br/>[Markdown]] -->|Explique| W4[Flux de Données]
        W5[docs/DEPENDENCIES.md<br/>Guide des Dépendances<br/>[Markdown]] -->|Liste| W6[Toutes les Dépendances]
        W7[docs/REPO_ANALYSIS.md<br/>Analyse des Repositories<br/>[Markdown]] -->|Analyse| W8[6 Repositories GitHub]
    end
    
    %% ===== NOUVEAUX COMPOSANTS DE DÉVELOPPEMENT =====
    subgraph "🛠️ OUTILS DE DÉVELOPPEMENT"
        X1[setup.sh<br/>Installation Automatique<br/>[Bash]] -->|Clone| X2[6 Repositories GitHub]
        X3[setup.ps1<br/>Installation Windows<br/>[PowerShell]] -->|Clone| X2
        X4[requirements.txt<br/>Dépendances Python<br/>[Text]] -->|Installs| X5[Packages Python]
        X6[install_dependencies.R<br/>Dépendances R<br/>[R]] -->|Installs| X7[Packages R]
    end
    
    %% ===== FLUX PRINCIPAL =====
    O1 -->|Step 1| B1
    O1 -->|Step 1| B2
    O1 -->|Step 2| M2
    O1 -->|Step 3| Q3
    O1 -->|Output| S1
    
    %% ===== STYLES =====
    classDef orchestration fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef dataCollection fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef dataTreatment fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef visualization fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef config fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef docs fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef dev fill:#fafafa,stroke:#424242,stroke-width:2px
    classDef legacy fill:#ffebee,stroke:#b71c1c,stroke-width:1px,stroke-dasharray: 5 5
    
    %% Application des styles
    class O1,O2,O3,O4 orchestration
    class A1,A2,A3,B1,B2,B3,C1,F1,G1 dataCollection
    class I2,J2,K2,L2,M2 dataTreatment
    class N3,O3,P3,Q3 visualization
    class S1,S2,S3,S4,T1 output
    class O5,U1,U2,U3,V1,V2,V3,V4 config
    class W1,W2,W3,W4,W5,W6,W7,W8 docs
    class X1,X2,X3,X4,X5,X6,X7 dev
    class H1,R3 legacy
```

## Légende des Composants

### 🎯 **ORCHESTRATION UNIFIÉE**
- **orchestrator.py** : Pipeline principal qui coordonne toutes les étapes
- **analyze.py** : Interface utilisateur simplifiée pour lancer des analyses
- **generate_analysis.sh** : Script d'automatisation pour analyses batch
- **test_connections.py** : Validation complète du système
- **config/sources.json** : Configuration centralisée de toutes les sources

### 📊 **ÉTAPE 1: COLLECTE DE DONNÉES**
- **Sources multiples** : MTGO, MTGMelee, Topdeck
- **Clients spécialisés** : Chaque plateforme a son client dédié
- **Cache unifié** : Gestion centralisée des données brutes et traitées
- **Gestionnaire de cache** : Optimisation et préservation des données

### 🔧 **ÉTAPE 2: TRAITEMENT DES DONNÉES**
- **MTGOArchetypeParser** : Classification des archétypes (C#/.NET)
- **MTGOFormatData** : Règles de classification par format
- **Adapter Python** : Interface entre Python et C#
- **Données traitées** : Format JSON structuré

### 📈 **ÉTAPE 3: VISUALISATION**
- **R-Meta-Analysis** : Analyse statistique et visualisations (R)
- **Matrices de matchups** : Résultats principaux
- **Adapter R** : Interface entre Python et R
- **Publication Discord** : Diffusion des résultats

### 🎨 **SORTIE ET ANALYSES**
- **Dossier analyses** : Stockage organisé des résultats
- **Rapports complets** : HTML avec graphiques interactifs
- **Données structurées** : JSON/CSV pour traitement ultérieur
- **Ouverture automatique** : Affichage immédiat dans le navigateur

### ⚙️ **CONFIGURATION ET VALIDATION**
- **Sources configurées** : URLs, authentification, rate limits
- **Formats supportés** : Standard, Modern, Legacy, Vintage, Pioneer, Pauper
- **Tests de connectivité** : Validation Internet, dépendances, système

### 📚 **DOCUMENTATION COMPLÈTE**
- **Bible du système** : Documentation exhaustive de tous les composants
- **Architecture** : Flux de données et interactions
- **Dépendances** : Guide d'installation et maintenance
- **Analyse des repositories** : Détails de chaque repository GitHub

### 🛠️ **OUTILS DE DÉVELOPPEMENT**
- **Installation automatique** : Scripts pour Linux/Windows
- **Gestion des dépendances** : Python et R
- **Clonage des repositories** : 6 repositories GitHub intégrés

## Flux de Données Principal

1. **Orchestrator** lance la collecte de données depuis MTGO, MTGMelee, Topdeck
2. **Cache unifié** stocke les données brutes et traitées
3. **Parser C#** classifie les archétypes selon les règles définies
4. **Analyse R** génère les visualisations et matrices de matchups
5. **Sortie** produit des rapports complets dans le dossier analyses
6. **Validation** vérifie la connectivité et les dépendances
7. **Documentation** fournit une référence complète du système

## Avantages de l'Architecture Unifiée

- **✅ Centralisation** : Un seul point d'entrée pour toutes les analyses
- **✅ Automatisation** : Pipeline complet sans intervention manuelle
- **✅ Validation** : Tests automatiques de la configuration
- **✅ Documentation** : Référence complète et maintenue
- **✅ Flexibilité** : Support de multiples sources et formats
- **✅ Maintenabilité** : Structure claire et modulaire 