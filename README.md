# 🎯 Manalytics - MTG Tournament Analysis Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version**: 3.1.0  
**Status**: ✅ Production Ready

A professional-grade platform for collecting, analyzing, and visualizing Magic: The Gathering tournament data from MTGO and Melee.gg.

## 📚 Documentation

**New to the project?** Start with our comprehensive guides:
- 📖 [Getting Started Guide](docs/ONBOARDING_GUIDE.md) - Complete onboarding for new developers
- 🏗️ [Architecture Overview](docs/MANALYTICS_COMPLETE_ARCHITECTURE.html) - Interactive system architecture
- 📊 [API Documentation](http://localhost:8000/docs) - Full API reference (when running)

## 🎯 Key Features

- **🔍 Multi-Platform Scraping**: Automated collection from MTGO and Melee.gg
- **🤖 Smart Archetype Detection**: Automatic deck categorization using community rules
- **📊 Advanced Analytics**: 
  - Metagame share tracking
  - Matchup win rate analysis
  - Innovation detection for emerging tech
  - Consensus deck generation from tournament results
- **🎨 Beautiful Visualizations**: Interactive charts with MTG color gradients
- **🚀 REST API**: Full-featured API with JWT authentication
- **💾 Efficient Storage**: Lightweight cache system with SQLite + JSON

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

### Scraping Tournaments

```bash
# Scrape both MTGO and Melee tournaments
python scrape_all.py --format standard --days 30

# Process and analyze data
python scripts/process_all_standard_data.py

# Generate visualizations
python visualize_standard.py
```

### Using the CLI

```bash
# Start the API server
manalytics serve

# Run a complete pipeline
manalytics run --format standard --days 7

# Generate analysis report
manalytics analyze --format standard --output report.html
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
├── src/manalytics/        # Main application code
│   ├── scrapers/          # MTGO & Melee scrapers
│   ├── parsers/           # Archetype detection
│   ├── cache/             # Cache system
│   ├── analyzers/         # Meta analysis
│   ├── visualizers/       # Chart generation
│   ├── pipeline/          # Orchestration
│   └── api/               # FastAPI endpoints
├── data/
│   ├── raw/               # Raw tournament data
│   └── cache/             # Processed data
├── scripts/               # Utility scripts
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

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Additional Documentation

For detailed documentation, see:
- [Scraping Guide](docs/SCRAPERS_COMPLETE_GUIDE.md) - Complete scraping documentation
- [API Reference](docs/API_REFERENCE.md) - Full API documentation
- [Development Guide](docs/DEVELOPMENT_GUIDE.md) - Contributing guidelines

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