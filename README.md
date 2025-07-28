# 🎯 Manalytics - MTG Tournament Analysis Platform

> **"Chaque visualisation doit raconter une histoire. Pas de graphs pour faire joli - uniquement des insights actionnables pour gagner des tournois."**
> 
> **Chaque visualisation doit apporter de la valeur compétitive réelle.**

## 📚 IMPORTANT : GUIDE D'INTÉGRATION POUR NOUVEAUX DÉVELOPPEURS

**👋 NOUVEAU SUR LE PROJET ? COMMENCEZ ICI :**
- **[docs/ONBOARDING_GUIDE.md](docs/ONBOARDING_GUIDE.md)** - Guide d'intégration complet avec parcours de lecture structuré
- Ce guide vous dira EXACTEMENT quoi lire et dans quel ordre (2-3h pour tout comprendre)
- **NE PAS COMMENCER À CODER SANS AVOIR LU CE GUIDE**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 3.0.0  
**Status**: ✅ Phase 1 Complete (Data Collection) | ✅ Phase 2 Complete (Cache & Analysis) | ✅ Phase 3 Complete (Architecture & Docs) | 📋 Phase 4 Next (MTGO Listener)  
**Last Update**: July 27, 2025

A professional-grade platform for collecting, analyzing, and visualizing Magic: The Gathering tournament data from MTGO and Melee.gg.

## 🎯 What Makes Us Different

### 🎮 Phase 4 PLANIFIÉE : MTGO Listener
Pour obtenir les vraies données de matchups et créer une matrice statistique :
- Implementation basée sur [MTGO-listener](https://github.com/Jiliac/MTGO-listener)
- Utilisation de [MTGOSDK](https://github.com/videre-project/MTGOSDK)
- Capture temps réel : qui joue contre qui, résultats round-par-round
- Permettra ENFIN la création d'une vraie matrice de matchups

### Unique Features (Nobody Else Has):
- **🤖 Consensus Deck Generator** - Automatically generates THE optimal decklist from 20+ tournament results
- **🔍 Innovation Detector** - Real-time detection of emerging tech choices before they go mainstream
- **📊 Multi-Deck Visual Comparison** - See exactly why some decks win and others don't
- **🎯 Unified MTGO + Melee Analysis** - Most sites do one OR the other, we do both
- **🎨 MTG Color Gradients** - Beautiful gradient visualizations respecting MTG color identity
- **📈 Match-Based Analysis** - Following community standards (Jiliac methodology) for accurate meta %

## 🎉 Current Status (Phase 1 & 2 Complete!)

### ✅ Phase 1: Data Collection
- **Full decklists collection** : MTGO (enhanced scraper) + Melee (Records field parsing)
- **July 2025 scraped** : 67 tournaments = 1,140 complete decklists
- **Fixed initial issue** : Now retrieving complete mainboard + sideboard data

### ✅ Phase 2: Cache System & Analysis (NEW!)
- **Archetype Detection** : 44 Standard rules from MTGOFormatData integrated
- **Color Detection** : 28,000+ cards database for accurate color identification
- **Performance** : <500ms per tournament processing
- **Cache System** : Lightweight SQLite for tournament metadata only (JSON files contain actual data)
- **Guild Names** : Full support (Izzet, Dimir, Naya, Jeskai, etc.)
- **Interactive Visualization** : HTML charts with pie chart labels & percentages
- **Meta Snapshot** : Real-time metagame breakdown

### 📊 Period d'Analyse Standard: July 1-21, 2025

⚠️ **IMPORTANT**: Toutes les analyses doivent être effectuées du **1er au 21 juillet 2025** pour permettre la comparaison avec les données de Jiliac.

**Exemple de métagame** (données partielles - scraping MTGO nécessaire):
1. **Izzet Cauldron** - ~22%
2. **Dimir Midrange** - ~20%
3. **Mono White Caretaker** - ~6%

*Note: Analyse par MATCHES (pas par decks) suivant la méthodologie Jiliac*

### ✅ Phase 3: Complete - Architecture & Documentation

**Réalisations Phase 3**:
- ✅ **Architecture modulaire** alignée avec Jiliac (src/manalytics/)
- ✅ **Visualisation de référence** : `data/cache/standard_analysis_no_leagues.html`
- ✅ **Documentation complète** : 15+ guides techniques créés
- ✅ **Scripts réorganisés** : De 54 → 29 scripts utilitaires
- ✅ **Quick launcher** : `python3 visualize_standard.py`

**Documentation créée**:
- `docs/PROJECT_COMPLETE_DOCUMENTATION.md` - Guide complet pour les équipes
- `docs/DATA_FLOW_VISUALIZATION.html` - Flux de données interactif
- `docs/FILE_DISCOVERY_PROCESS.html` - Comment on trouve les fichiers
- `docs/VISUALIZATION_TEMPLATE_REFERENCE.md` - Règles visuelles ABSOLUES

## 📋 Features

- **🔍 Tournament Scraping**: Automated collection from MTGO and Melee.gg
- **📊 Metagame Analysis**: Track deck performance and meta share
- **🎨 Archetype Detection**: Automatic deck categorization
- **📈 Visualizations**: Heatmaps, charts, and trend analysis
- **🚀 REST API**: Full-featured API for data access
- **🐳 Docker Support**: Easy deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- No database required - works directly with JSON files
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/manalytics.git
   cd manalytics
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install dependencies**
   ```bash
   make install-dev
   ```

4. **Start the application**
   ```bash
   make run
   ```

Visit http://localhost:8000/docs for API documentation.

## 🎮 Usage

### Scraping Tournaments

```bash
# Quick visualization (RECOMMANDÉ)
python3 visualize_standard.py

# Pipeline complet (nouveau scraper unifié!)
python scrape_all.py --format standard --days 21  # Scrape MTGO + Melee
python3 scripts/process_all_standard_data.py      # Process cache
python3 visualize_standard.py                     # Generate viz

# Analyse juillet 1-21 (pour comparaison Jiliac)
python3 analyze_july_1_21.py
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run only unit tests
make test-unit
```

### Code Quality

```bash
# Run linters
make lint

# Format code
make format

# Full check
make check
```

## 📁 Project Structure

```
manalytics/
├── src/manalytics/        # CODE PRINCIPAL (organisé)
│   ├── scrapers/          # MTGO & Melee scrapers
│   ├── parsers/           # Archetype detection
│   ├── cache/             # Cache system (SQLite + JSON)
│   ├── analyzers/         # Meta analysis
│   ├── visualizers/       # Chart generation
│   ├── pipeline/          # Orchestration
│   └── api/               # FastAPI
├── data/
│   ├── raw/               # Données brutes
│   │   ├── mtgo/standard/ # ⚠️ Exclut leagues/
│   │   └── melee/standard/
│   └── cache/             # Données processées
│       └── standard_analysis_no_leagues.html  # 📊 RÉFÉRENCE
├── scripts/               # Utilitaires one-shot
│   └── _archive_2025_07_27/  # Anciens scripts
├── docs/                  # DOCUMENTATION COMPLÈTE
└── visualize_standard.py  # 🚀 LANCEUR RAPIDE
```

## 🔧 Configuration

Key environment variables:

```bash
# Melee.gg credentials
MELEE_EMAIL=your_email@example.com
MELEE_PASSWORD=your_password

# API settings (optional)
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

See `.env.example` for all options.

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/meta` | Current metagame breakdown |
| `GET /api/decks` | Browse decklists |
| `GET /api/tournaments` | Tournament results |
| `GET /api/matchups` | Matchup analysis |
| `GET /api/trends` | Historical trends |

Full documentation at `/api/docs` when running.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

### 📚 Documentation Essentielle

**👋 NOUVEAU ? Commencez par** :
- 🎓 **[ONBOARDING GUIDE](docs/ONBOARDING_GUIDE.md)** - **GUIDE D'INTÉGRATION COMPLET**
  - Parcours de lecture structuré
  - Ordre exact des documents à lire
  - Scripts actuels vs obsolètes
  - Quick Start guidé

**Documentation principale** :
- 🎯 [PROJECT COMPLETE DOCUMENTATION](docs/PROJECT_COMPLETE_DOCUMENTATION.md) - Vue d'ensemble complète
- 🏗️ [MANALYTICS COMPLETE ARCHITECTURE](docs/MANALYTICS_COMPLETE_ARCHITECTURE.html) - Architecture interactive
- 🕷️ [SCRAPERS COMPLETE GUIDE](docs/SCRAPERS_COMPLETE_GUIDE.md) - Tout sur les scrapers
- 🎨 [VISUALIZATION TEMPLATE REFERENCE](docs/VISUALIZATION_TEMPLATE_REFERENCE.md) - Standards visuels

**Flux et processus** :
- 📊 [DATA FLOW VISUALIZATION](docs/DATA_FLOW_VISUALIZATION.html) - Flux de données interactif
- 🔍 [FILE DISCOVERY PROCESS](docs/FILE_DISCOVERY_PROCESS.html) - Découverte des fichiers
- 💾 [CACHE SYSTEM IMPLEMENTATION](docs/CACHE_SYSTEM_IMPLEMENTATION.md) - Architecture cache

**Roadmaps & Concepts** :
- [Phase 3 Visualizations Roadmap](docs/PHASE3_VISUALIZATIONS_ROADMAP.md) - 30+ visualisations
- [Consensus Deck Generator](docs/CONSENSUS_DECK_GENERATOR.md) - Feature ML unique
- [Innovation Detector](docs/INNOVATION_DETECTOR_CONCEPT.md) - Détection tech choices

## 🔒 Security

- Credentials stored in environment variables
- JWT authentication for API
- Rate limiting on all endpoints
- Input validation and sanitization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MTG community for archetype definitions
- Original scrapers from mtg_decklist_scrapper
- All contributors and testers

---

Built with ❤️ for the Magic: The Gathering community