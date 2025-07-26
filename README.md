# 🎯 Manalytics - MTG Tournament Analysis Platform

> **"Chaque visualisation doit raconter une histoire. Pas de graphs pour faire joli - uniquement des insights actionnables pour gagner des tournois."**
> 
> **Chaque visualisation doit apporter de la valeur compétitive réelle.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 3.0.0  
**Status**: ✅ Phase 1 Complete (Data Collection) | ✅ Phase 2 Complete (Cache & Analysis) | 🚀 Phase 3 In Progress (Advanced Visualizations) | 📋 Phase 4 Planned (MTGO Listener)  
**Last Update**: July 26, 2025

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

### 📊 Current Standard Metagame (July 1-20, 2025)
Based on competitive tournaments only (excluding casual/fun events):
1. **Dimir Midrange** - 22.4% (1,197 matches)
2. **Izzet Cauldron** - 21.9% (1,172 matches)
3. **Mono White Caretaker** - 6.1% (326 matches)
4. **Boros Convoke** - 4.9% (260 matches)
5. **Golgari Midrange** - 4.6% (247 matches)

*Note: Percentages based on match count following community standards (Jiliac methodology)*

### 🚀 Phase 3: In Progress - Advanced Visualizations

**⚠️ LIMITATION CRITIQUE DÉCOUVERTE (26/07/2025)** :
- Nous n'avons accès qu'aux données **Top 8 (brackets)** - PAS aux matchups round-par-round
- Sans ces données, impossible de créer une vraie matrice de matchups statistique
- C'est LA fonctionnalité qui différencie les outils compétitifs
- **Plotly visualization delivered** : `data/cache/standard_analysis_no_leagues.html` - Full interactive charts
- **Accurate percentages** : Real meta share calculations (not just top 10)
- **Timeline evolution** : 30-day meta evolution tracking
- **Export functionality** : CSV export for further analysis
- **Complete archetype table** : All 70 archetypes with trend indicators
- **Mobile responsive** : Works perfectly on tournament phones
- **Next steps** : MTGO Listener implementation (PRIORITÉ ABSOLUE), consensus deck generator

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
# Process all new tournaments through cache
python3 scripts/process_all_standard_data.py

# Generate Plotly visualization (MANDATORY UNLESS CONTRARY REQUESTED)
python3 scripts/create_archetype_visualization_plotly.py

# Generate Chart.js visualization (alternative)
python3 scripts/create_archetype_visualization.py

# View cache statistics
python3 scripts/show_cache_stats.py

# Old standalone scrapers (if needed)
python3 scrape_mtgo_standalone.py
python3 scrape_melee_from_commit.py
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
├── src/manalytics/     # Main package
│   ├── scrapers/       # Tournament scrapers
│   ├── parsers/        # Deck parsers
│   ├── analyzers/      # Data analysis
│   ├── api/            # REST API
│   └── models/         # Data models
├── tests/              # Test suite
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── data/               # Data storage
    ├── raw/            # Raw scraped data
    └── processed/      # Processed data
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

### Core Guides
- [MTGO Scraping Guide](docs/MTGO_SCRAPING_GUIDE.md) - Complete MTGO scraping guide
- [Melee Scraping Guide](docs/MELEE_SCRAPING_GUIDE.md) - Complete Melee scraping guide  
- [Scraping Best Practices](docs/SCRAPING_BEST_PRACTICES.md) - Critical lessons learned
- [Jiliac Comparison Analysis](docs/JILIAC_COMPARISON_FINDINGS.md) - Why our data differs & how to match

### Phase 2 Implementation
- [Cache System Implementation](docs/CACHE_SYSTEM_IMPLEMENTATION.md) - Complete cache architecture

### Phase 3 Visualizations (Coming Soon)
- [Phase 3 Roadmap](docs/PHASE3_VISUALIZATIONS_ROADMAP.md) - 30+ planned visualizations
- [Consensus Deck Generator](docs/CONSENSUS_DECK_GENERATOR.md) - Auto-generate optimal lists
- [Innovation Detector](docs/INNOVATION_DETECTOR_CONCEPT.md) - Detect emerging tech
- [Deck Comparison](docs/DECK_COMPARISON_FEATURE.md) - Visual deck differences
- [Project Differentiators](docs/PROJECT_SUMMARY_DIFFERENTIATORS.md) - What makes us unique

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