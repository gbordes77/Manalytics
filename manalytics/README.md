# MTG Analytics Pipeline - Pipeline Unifié

Un pipeline unifié pour l'analyse des données de tournois Magic: The Gathering, intégrant 6 repositories GitHub dans une architecture modulaire et extensible.

## 🎯 Vue d'Ensemble

Le pipeline MTG Analytics est un système complet qui :
- **Collecte** les données depuis MTGO, MTGMelee, Topdeck et Manatraders
- **Traite** et catégorise les decks par archétypes
- **Visualise** les données avec des matrices de matchups et analyses du métagame

## 🏗️ Architecture

```
manalytics/
├── data-collection/           # Étape 1 : Collecte de données
│   ├── scraper/
│   │   ├── mtgo/             # mtg_decklist_scrapper (fbettega)
│   │   └── mtgmelee/         # Extension API MTGMelee
│   ├── raw-cache/            # MTG_decklistcache (fbettega)
│   └── processed-cache/      # MTGODecklistCache (Jiliac)
├── data-treatment/           # Étape 2 : Traitement
│   ├── parser/               # MTGOArchetypeParser (Badaro)
│   └── format-rules/         # MTGOFormatData (Badaro)
├── visualization/            # Étape 3 : Visualisation
│   └── r-analysis/           # R-Meta-Analysis (Jiliac)
├── config/                   # Configuration
├── docs/                     # Documentation
├── data/                     # Données traitées
└── analyses/                 # Rapports générés
```

## 🚀 Installation Rapide

### Prérequis Système
- **Git** : Gestion des repositories
- **Python 3.8+** : Scripts de collecte et orchestration
- **.NET Runtime 8.0** : MTGOArchetypeParser
- **R 4.0+** : Visualisations et analyses

### Installation Automatique

#### Linux/macOS
```bash
# Cloner le projet
git clone https://github.com/your-username/manalytics.git
cd manalytics

# Installation automatique
./setup.sh
```

#### Windows
```powershell
# Cloner le projet
git clone https://github.com/your-username/manalytics.git
cd manalytics

# Installation automatique
.\setup.ps1
```

### Installation Manuelle
```bash
# 1. Installer les dépendances système
# Ubuntu/Debian
sudo apt-get install git python3 python3-pip r-base dotnet-runtime-8.0

# macOS
brew install git python3 r dotnet

# 2. Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\Activate.ps1  # Windows

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Installer les dépendances R
Rscript install_dependencies.R
```

## 📋 Vérification de l'Installation

### Test de Connectivité
```bash
# Tester tous les composants
python test_connections.py

# Vérifier les dépendances
python -c "import requests, beautifulsoup4, numpy; print('✅ Python OK')"
dotnet --version
R --version
```

### Test des Repositories
```bash
# Vérifier que tous les repositories sont clonés
ls -la data-collection/scraper/mtgo/
ls -la data-collection/raw-cache/
ls -la data-treatment/parser/
ls -la visualization/r-analysis/
```

## 🔧 Configuration

### Fichiers de Configuration

#### 1. Sources de Données (`config/sources.json`)
```json
{
  "mtgo": {
    "base_url": "https://www.mtgo.com/decklists",
    "scraping_config": {
      "rate_limit": 1,
      "retry_attempts": 5
    }
  },
  "mtgmelee": {
    "base_url": "https://melee.gg",
    "authentication": {
      "login_url": "https://melee.gg/login"
    }
  }
}
```

#### 2. Credentials MTGMelee (`data-collection/scraper/mtgo/melee_login.json`)
```json
{
  "login": "your-email@example.com",
  "mdp": "your-password"
}
```

#### 3. API Topdeck (`data-collection/scraper/mtgo/Api_token_and_login/api_topdeck.txt`)
```
your-api-key-here
```

## 📊 Utilisation

### Analyse Simple
```bash
# Analyser le format Standard sur les 7 derniers jours
./generate_analysis.sh standard 7

# Analyser le format Modern sur les 30 derniers jours
./generate_analysis.sh modern 30
```

### Analyse Avancée
```bash
# Utiliser l'orchestrateur Python
python orchestrator.py --format standard --days 7 --output analyses/standard_analysis

# Collecter des données spécifiques
python data-collection/scraper/mtgo/main.py --format standard --days 7

# Traiter les données
python data-treatment/parser/main.py --format standard --input data/raw --output data/processed

# Générer les visualisations
Rscript visualization/r-analysis/generate_matrix.R --format standard --output analyses/
```

### Formats Supportés
- **Standard** : Format actuel
- **Modern** : Format étendu
- **Legacy** : Format vintage
- **Vintage** : Format restreint
- **Pioneer** : Format intermédiaire
- **Pauper** : Format commun

## 📈 Exemples de Sortie

### Matrice de Matchups
```
           Burn  Spirits  Shadow  Rakdos  Amulet  Heliod
Burn       0.50    0.45    0.55    0.60    0.40    0.65
Spirits    0.55    0.50    0.48    0.52    0.58    0.42
Shadow     0.45    0.52    0.50    0.47    0.53    0.49
Rakdos     0.40    0.48    0.53    0.50    0.45    0.55
Amulet     0.60    0.42    0.47    0.55    0.50    0.51
Heliod     0.35    0.58    0.51    0.45    0.49    0.50
```

### Répartition du Métagame
```
Archetype      Count  Percentage
Burn              1      7.69%
Spirits           1      7.69%
Shadow Prowess    2     15.38%
Rakdos Midrange   1      7.69%
Amulet Titan      2     15.38%
Heliod Combo      2     15.38%
```

## 🔍 Structure des Données

### Format Raw (MTG_decklistcache)
```json
{
  "Tournament": {
    "date": "2025-01-15",
    "name": "MTGO Standard Challenge",
    "uri": "https://www.mtgo.com/decklists/...",
    "formats": ["Standard"]
  },
  "Decks": [
    {
      "player": "yamakiller",
      "result": "5-0",
      "mainboard": [
        {"count": 4, "card_name": "Lightning Bolt"}
      ],
      "sideboard": [
        {"count": 2, "card_name": "Fury"}
      ]
    }
  ]
}
```

### Format Processed (MTGOArchetypeParser)
```json
{
  "tournament_id": "mtgo-standard-20250115",
  "format": "Standard",
  "decks": [
    {
      "player_name": "yamakiller",
      "archetype": "Burn",
      "result": "5-0",
      "mainboard": [...],
      "sideboard": [...]
    }
  ]
}
```

## 🛠️ Développement

### Structure du Code
```
manalytics/
├── orchestrator.py           # Orchestrateur principal
├── analyze.py               # Script d'analyse
├── test_connections.py      # Tests de connectivité
├── requirements.txt         # Dépendances Python
├── install_dependencies.R   # Dépendances R
└── generate_analysis.sh     # Script d'analyse bash
```

### Ajout d'un Nouveau Format
1. **Créer les règles d'archétypes** dans `data-treatment/format-rules/Formats/NouveauFormat/`
2. **Ajouter la configuration** dans `config/sources.json`
3. **Tester la collecte** avec `python test_connections.py`
4. **Valider le parsing** avec `python data-treatment/parser/main.py`

### Extension MTGMelee
Le module MTGMelee doit être étendu pour :
- Authentification API
- Récupération des tournois
- Extraction des decklists
- Formatage des données

## 📚 Documentation

### Guides Détaillés
- [📖 Architecture](docs/ARCHITECTURE.md) - Architecture complète du pipeline
- [📊 Formats de Données](docs/DATA_FORMATS.md) - Spécifications des formats
- [🔧 Dépendances](docs/DEPENDENCIES.md) - Guide d'installation des dépendances
- [📋 Analyse des Repositories](docs/REPO_ANALYSIS.md) - Documentation des 6 repositories

### API Reference
- **MTGO Scraper** : `data-collection/scraper/mtgo/README.md`
- **Archetype Parser** : `data-treatment/parser/README.md`
- **Format Rules** : `data-treatment/format-rules/README.md`
- **R Analysis** : `visualization/r-analysis/README.md`

## 🐛 Résolution de Problèmes

### Problèmes Courants

#### Erreur de Connectivité
```bash
# Tester la connectivité
python test_connections.py

# Vérifier les URLs dans config/sources.json
# Vérifier les credentials MTGMelee
```

#### Erreur de Dépendances
```bash
# Réinstaller les dépendances Python
pip install -r requirements.txt

# Réinstaller les dépendances R
Rscript install_dependencies.R

# Vérifier .NET
dotnet --version
```

#### Erreur de Parsing
```bash
# Vérifier les règles d'archétypes
ls data-treatment/format-rules/Formats/Standard/

# Tester le parser manuellement
python data-treatment/parser/main.py --format standard --input test_data.json
```

### Logs et Debugging
```bash
# Activer les logs détaillés
export MANALYTICS_DEBUG=1
python orchestrator.py --verbose

# Vérifier les logs de scraping
tail -f data-collection/scraper/mtgo/log_scraping.txt
```

## 🤝 Contribution

### Maintainers
- **Jiliac** : Formats Standard, Modern, Legacy, Pioneer, Pauper
- **IamActuallyLvL1** : Format Vintage
- **fbettega** : Scraping et cache des données

### Workflow de Contribution
1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Créer** une Pull Request

### Standards de Code
- **Python** : PEP 8, Black, Flake8
- **R** : Style guide tidyverse
- **Documentation** : Markdown avec exemples
- **Tests** : Pytest pour Python, testthat pour R

## 📄 Licence

Ce projet intègre plusieurs repositories sous différentes licences :
- **mtg_decklist_scrapper** : MIT License
- **MTG_decklistcache** : MIT License
- **MTGOArchetypeParser** : MIT License
- **MTGOFormatData** : MIT License
- **R-Meta-Analysis** : MIT License

## 🙏 Remerciements

- **fbettega** : Scraping et cache des données
- **Badaro** : Moteur de parsing d'archétypes
- **Jiliac** : Maintenance des formats et visualisations
- **IamActuallyLvL1** : Format Vintage
- **Aliquanto3** : Base du projet R-Meta-Analysis

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/your-username/manalytics/issues)
- **Discussions** : [GitHub Discussions](https://github.com/your-username/manalytics/discussions)
- **Documentation** : [Wiki](https://github.com/your-username/manalytics/wiki)

---

**🚀 Prêt à analyser le métagame MTG ? Commencez par `./setup.sh` !**