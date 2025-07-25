# 🎯 Manalytics - MTG Tournament Analysis Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 2.0.0  
**Status**: ✅ Phase 1 Complete (Data Collection) | ✅ Phase 2 Complete (Cache & Analysis) | 📋 Phase 3 (Advanced Visualizations)  
**Last Update**: July 25, 2025

A professional-grade platform for collecting, analyzing, and visualizing Magic: The Gathering tournament data from MTGO and Melee.gg.

## 🎯 What Makes Us Different

### Unique Features (Nobody Else Has):
- **🤖 Consensus Deck Generator** - Automatically generates THE optimal decklist from 20+ tournament results
- **🔍 Innovation Detector** - Real-time detection of emerging tech choices before they go mainstream
- **📊 Multi-Deck Visual Comparison** - See exactly why some decks win and others don't
- **🎯 Unified MTGO + Melee Analysis** - Most sites do one OR the other, we do both

## 🎉 Current Status (Phase 1 & 2 Complete!)

### ✅ Phase 1: Data Collection
- **Full decklists collection** : MTGO (enhanced scraper) + Melee (Records field parsing)
- **July 2025 scraped** : 67 tournaments = 1,140 complete decklists
- **Fixed initial issue** : Now retrieving complete mainboard + sideboard data

### ✅ Phase 2: Cache System & Analysis (NEW!)
- **Archetype Detection** : 44 Standard rules from MTGOFormatData integrated
- **Color Detection** : 28,000+ cards database for accurate color identification
- **Performance** : <500ms per tournament processing with SQLite cache
- **Guild Names** : Full support (Izzet, Dimir, Naya, Jeskai, etc.)
- **Interactive Visualization** : HTML charts with pie chart labels & percentages
- **Meta Snapshot** : Real-time metagame breakdown

### 📊 Current Standard Metagame (July 2025)
1. **Izzet Prowess (Cauldron)** - 19.6%
2. **Dimir Midrange** - 19.4%
3. **Mono White Caretaker** - 4.6%
4. **Golgari Midrange** - 4.4%
5. **Boros Convoke** - 3.6%

### 📋 Phase 3: Ready to Start
- **Phase 3 documentation ready** : 30+ planned visualizations in `docs/`

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
- PostgreSQL 13+
- Redis (optional, for caching)
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

4. **Run migrations**
   ```bash
   make migrate
   ```

5. **Start the application**
   ```bash
   make run
   ```

Visit http://localhost:8000/docs for API documentation.

## 🎮 Usage

### Scraping Tournaments

```bash
# Process all new tournaments through cache
python3 scripts/process_all_standard_data.py

# Generate visualization
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
# Database
DATABASE_URL=postgresql://user:pass@localhost/manalytics

# Melee.gg credentials
MELEE_EMAIL=your_email@example.com
MELEE_PASSWORD=your_password

# API settings
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