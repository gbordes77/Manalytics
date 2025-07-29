# 🎯 Manalytics - MTG Tournament Analysis Platform

> **📖 RÔLE DE CE FICHIER README.md**
> 
> Ce fichier est la **documentation publique** du projet, destinée aux :
> - **Développeurs externes** qui veulent utiliser ou contribuer au projet
> - **Utilisateurs** qui veulent installer et utiliser l'application
> - **Visiteurs GitHub** qui découvrent le projet
> 
> **CE QUI DOIT ÊTRE DANS CE FICHIER :**
> - ✅ Description du projet et ses fonctionnalités
> - ✅ Instructions d'installation et d'utilisation
> - ✅ Documentation de l'API publique
> - ✅ Guide de contribution
> - ✅ Informations techniques générales
> 
> **CE QUI NE DOIT PAS ÊTRE ICI :**
> - ❌ Instructions spécifiques pour les assistants IA
> - ❌ État détaillé du développement en cours
> - ❌ Règles internes de travail
> - ❌ Informations sensibles ou temporaires
> 
> ➡️ **Pour les instructions IA, voir CLAUDE.md**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 3.3.0  
**Status**: 🚧 Major Restructuring (Architecture Consolidation)

A professional-grade platform for collecting, analyzing, and visualizing Magic: The Gathering tournament data from MTGO and Melee.gg. Features the **Jiliac Method** for accurate metagame analysis.

> **🚧 Current Focus**: Major architecture restructuring to consolidate 36+ scattered scripts into a unified, maintainable codebase. This will enable proper investigation of the Jiliac pipeline integration.

## 📚 Documentation

**New to the project?** Start with our comprehensive guides:
- 📖 [Getting Started Guide](docs/ONBOARDING_GUIDE.md) - Complete onboarding for new developers
- 🏗️ [Architecture Overview](docs/MANALYTICS_COMPLETE_ARCHITECTURE.html) - Interactive system architecture
- 📊 [API Documentation](http://localhost:8000/docs) - Full API reference (when running)

## 🎯 Key Features

- **🔍 Multi-Platform Scraping**: Automated collection from MTGO and Melee.gg
- **🤖 Smart Archetype Detection**: Automatic deck categorization using community rules
- **📊 Advanced Analytics**: 
  - Metagame share tracking with Jiliac Method
  - Wilson confidence intervals (90%) for win rates
  - Tier assignment based on CI lower bounds
  - Matchup win rate analysis with exact matchup reconstruction
  - Innovation detection for emerging tech
  - Consensus deck generation from tournament results
- **🎨 Beautiful Visualizations**: Interactive charts with MTG color gradients
- **🚀 REST API**: Full-featured API with JWT authentication
- **💾 Efficient Storage**: Lightweight cache system with SQLite + JSON
- **📐 Reference Implementation**: Exact reproduction of [Jiliac's R-Meta-Analysis](https://github.com/Jiliac/R-Meta-Analysis)
- **🔄 Community Pipeline Integration**: Compatible with MTGODecklistCache and MTGOArchetypeParser

## 🎮 Supported Formats

- Standard
- Modern  
- Legacy
- Pioneer
- Pauper
- Vintage
- Commander (Melee only)

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
   # Edit .env with your Melee.gg credentials
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

> **⚠️ Note**: The project is currently undergoing major restructuring. The commands below represent the current temporary interface. A unified CLI is being developed.

### Current Usage (Temporary)

```bash
# Scrape both MTGO and Melee tournaments
python scrape_all.py --format standard --days 30

# Analyze data using Jiliac method
python analyze_july_jiliac_method.py

# Generate visualizations
python visualize_standard.py
```

### Future CLI (In Development)

```bash
# Unified command interface (coming soon)
manalytics scrape --format standard --days 30
manalytics analyze --method jiliac --period july_1_21
manalytics visualize --format html --output report.html
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

> **⚠️ Architecture Restructuring in Progress**: The project structure is being consolidated from 36+ scattered scripts into a unified architecture.

### Current Structure (Temporary)
```
manalytics/
├── src/manalytics/        # Modern architecture (partial)
├── analyze_*.py           # 21 analysis scripts (being consolidated)
├── scrape_*.py            # 15 scraping scripts (being consolidated)
├── visualize_*.py         # Visualization scripts (being consolidated)
├── data/                  # Tournament data and cache
├── docs/                  # Documentation
└── _archive/              # Archived scripts (post-restructuring)
```

### Target Structure (In Development)
```
manalytics/
├── src/manalytics/        # Unified main package
│   ├── cli/               # Single entry points
│   │   ├── analyze.py     # Unified analysis command
│   │   ├── scrape.py      # Unified scraping command
│   │   └── visualize.py   # Unified visualization command
│   ├── core/              # Core business logic
│   │   ├── analyzers/     # Analysis engines
│   │   ├── scrapers/      # Data collection
│   │   └── visualizers/   # Chart generation
│   └── utils/             # Shared utilities
├── investigation/         # Jiliac pipeline research
├── data/                  # Data storage
├── docs/                  # Documentation
└── tests/                 # Test suite
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

The application will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/meta` | Current metagame breakdown |
| `GET /api/decks` | Browse decklists |
| `GET /api/tournaments` | Tournament results |
| `GET /api/matchups` | Matchup analysis |
| `GET /api/trends` | Historical trends |

Full documentation at `/api/docs` when running.

## 🚧 Current Development Status

### Architecture Restructuring (Phase 7)

The project is currently undergoing a major restructuring to address architectural inconsistencies:

- **Problem Identified**: 36+ scattered scripts (21 analysis + 15 scraping) with conflicting logic
- **Solution**: Consolidation into unified architecture with single entry points
- **Progress**: Specification complete, implementation in progress
- **Timeline**: Restructuring before resuming Jiliac pipeline investigation

### What This Means for Contributors

- **New Features**: Please wait for restructuring completion
- **Bug Fixes**: Focus on critical issues only
- **Documentation**: Updates welcome, especially for the new architecture
- **Testing**: Help validate that consolidated scripts produce consistent results

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

> **Note**: During restructuring, please coordinate with maintainers before starting major work to avoid conflicts.

## 📚 Additional Documentation

### Core Documentation
- [Jiliac Method Reference](docs/JILIAC_METHOD_REFERENCE.md) - Complete methodology documentation
- [Scraping Guide](docs/SCRAPERS_COMPLETE_GUIDE.md) - Complete scraping documentation
- [Development Guide](docs/DEVELOPMENT_GUIDE.md) - Contributing guidelines

### Research & Investigation
- [Pipeline Analysis](docs/JILIAC_PIPELINE_COMPLETE_ANALYSIS.md) - Deep dive into the community pipeline
- [All Calculation Methods](docs/JILIAC_ALL_CALCULATION_METHODS.md) - 264+ calculation combinations
- [Data Source Mystery](docs/JILIAC_DATA_SOURCE_MYSTERY.md) - Investigation into matchup data sources

### Project Status & Architecture
- [Architecture Restructuring Spec](.kiro/specs/project-restructuration/) - Complete restructuring plan
- [Project Structure Diagnosis](DIAGNOSTIC_STRUCTURE_PROJET.md) - Analysis of current architectural issues
- [Scripts Audit](AUDIT_SCRIPTS_ACTIFS.md) - Inventory of existing scripts

> **Note**: Some documentation may be temporarily outdated during the restructuring process. Please refer to CLAUDE.md for the most current development status.

## 🔒 Security

- Credentials stored in environment variables
- JWT authentication for API
- Rate limiting on all endpoints
- Input validation and sanitization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Jiliac](https://github.com/Jiliac) for the R-Meta-Analysis methodology
- MTG community for archetype definitions
- Original scrapers from mtg_decklist_scrapper
- [Badaro](https://github.com/Badaro) for MTGOArchetypeParser
- All contributors and testers

---

Built with ❤️ for the Magic: The Gathering community