# 🎯 Manalytics - MTG Tournament Analysis Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 1.0.0  
**Status**: ✅ Scrapers Fonctionnels - Pipeline en développement  
**Last Update**: July 25, 2025

A professional-grade platform for collecting, analyzing, and visualizing Magic: The Gathering tournament data from MTGO and Melee.gg.

## 🎉 Achievements (25/07/2025)

- ✅ **Scrapers 100% fonctionnels** : MTGO + Melee avec toutes les données de juillet 2025
- ✅ **493 tournois collectés** : 363 MTGO + 130 Melee avec organisation par format
- ✅ **Validation communautaire** : 386 tournois correspondent avec fbettega/MTG_decklistcache
- ✅ **Documentation complète** : Guides détaillés pour MTGO et Melee dans `docs/`
- ✅ **Scripts standalone** : Scrapers indépendants sans dépendances complexes

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
# Scraper MTGO (standalone)
python3 scrape_mtgo_standalone.py

# Scraper Melee (standalone)  
python3 scrape_melee_from_commit.py

# Valider contre le cache communautaire
python3 scripts/validate_against_decklistcache.py --platform all

# Ancienne méthode (si besoin)
python3 scripts/scrape_all_platforms.py --format standard --days 7
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

- [MTGO Scraping Guide](docs/MTGO_SCRAPING_GUIDE.md) - Guide complet du scraping MTGO
- [Melee Scraping Guide](docs/MELEE_SCRAPING_GUIDE.md) - Guide complet du scraping Melee
- [Scraping Best Practices](docs/SCRAPING_BEST_PRACTICES.md) - Leçons critiques apprises
- [Architecture Overview](docs/architecture/README.md)
- [Development Guide](docs/guides/development.md)

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