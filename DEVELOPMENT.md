# 💻 Guide de Développement - Manalytics

Guide complet pour comprendre, modifier et étendre le projet Manalytics.

## 📋 Table des Matières

1. [Architecture technique](#architecture-technique)
2. [Environnement de développement](#environnement-de-développement)
3. [Structure du code](#structure-du-code)
4. [Ajout de fonctionnalités](#ajout-de-fonctionnalités)
5. [Tests et qualité](#tests-et-qualité)
6. [Performance](#performance)
7. [Sécurité](#sécurité)
8. [Roadmap](#roadmap)

## 🏗️ Architecture Technique

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Future)                      │
├─────────────────────────────────────────────────────────────┤
│                    API REST (FastAPI)                         │
│  ┌─────────────┬──────────────┬──────────────┬────────────┐ │
│  │    Auth     │    Routes    │  Middleware  │   Models   │ │
│  └─────────────┴──────────────┴──────────────┴────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic                             │
│  ┌─────────────┬──────────────┬──────────────┬────────────┐ │
│  │  Scrapers   │   Parsers    │  Analyzers   │Visualizers │ │
│  └─────────────┴──────────────┴──────────────┴────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                 │
│  ┌─────────────────────┬─────────────────────────────────┐  │
│  │   PostgreSQL 16     │         Redis Cache             │  │
│  └─────────────────────┴─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

1. **Repository Pattern**: Isolation de la logique d'accès aux données
2. **Factory Pattern**: Création des scrapers selon la source
3. **Strategy Pattern**: Différentes stratégies de détection d'archétypes
4. **Observer Pattern**: Notifications des changements de méta

### Flux de données

```
Scraper → Parser → Detector → Database → Analyzer → API → Client
   ↓         ↓         ↓          ↓          ↓
  Logs    Validate  Rules     Cache    Visualize
```

## 💻 Environnement de Développement

### Setup local

```bash
# 1. Cloner le repo
git clone <repo-url>
cd Manalytics

# 2. Environnement virtuel Python
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Pre-commit hooks
pre-commit install

# 5. Variables d'environnement
cp .env.example .env.local
# Éditer .env.local
```

### VS Code configuration

**.vscode/settings.json**:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

### Docker dev mode

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  api:
    volumes:
      - ./src:/app/src
      - ./scripts:/app/scripts
    environment:
      - DEBUG=true
      - RELOAD=true
    command: uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Structure du Code

### Organisation des modules

```
src/
├── api/                 # Couche API
│   ├── routes/         # Endpoints organisés par domaine
│   │   ├── auth.py    # Authentication
│   │   ├── decks.py   # CRUD decks
│   │   └── analysis.py # Analyses
│   ├── models.py      # Modèles Pydantic
│   ├── auth.py        # JWT logic
│   └── deps.py        # Dependencies injection
├── scrapers/          # Collecte de données
│   ├── base_scraper.py # Classe abstraite
│   ├── mtgo_scraper.py # MTGO implementation
│   └── melee_scraper.py # Melee.gg implementation
├── parsers/           # Parsing et validation
│   ├── deck_parser.py # Parse decklists
│   └── archetype_engine.py # Moteur de règles
├── analyzers/         # Analyse de données
│   ├── meta_analyzer.py # Stats du méta
│   ├── archetype_detector.py # Détection
│   └── matchup_calculator.py # Calcul matchups
└── utils/             # Utilitaires
    ├── card_utils.py  # Normalisation cartes
    └── cache.py       # Gestion cache
```

### Conventions de code

1. **Naming**:
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`

2. **Docstrings** (Google style):
```python
def calculate_meta_share(archetype_id: int, format_name: str) -> float:
    """Calculate the meta share percentage for an archetype.
    
    Args:
        archetype_id: The archetype database ID
        format_name: MTG format name (modern, legacy, etc.)
        
    Returns:
        The meta share as a percentage (0-100)
        
    Raises:
        ValueError: If archetype not found
    """
```

3. **Type hints** obligatoires:
```python
from typing import List, Dict, Optional, Tuple

def parse_deck(content: str) -> Tuple[List[Card], List[Card]]:
    mainboard: List[Card] = []
    sideboard: List[Card] = []
    return mainboard, sideboard
```

## 🚀 Ajout de Fonctionnalités

### 1. Nouveau scraper

```python
# src/scrapers/new_source_scraper.py
from src.scrapers.base_scraper import BaseScraper
from typing import List, Dict, Any

class NewSourceScraper(BaseScraper):
    """Scraper for NewSource tournament results."""
    
    def __init__(self, format_name: str):
        super().__init__(format_name)
        self.base_url = "https://newsource.com"
        self.source_name = "newsource"
    
    def scrape_tournaments(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Implement tournament scraping logic."""
        tournaments = []
        # Implementation here
        return tournaments
    
    def _parse_tournament_page(self, content: str) -> Dict[str, Any]:
        """Parse a single tournament page."""
        # Implementation
        pass
```

### 2. Nouvel endpoint API

```python
# src/api/routes/stats.py
from fastapi import APIRouter, Depends, Query
from src.api.auth import get_current_user
from src.api.models import StatsResponse

router = APIRouter()

@router.get("/player/{player_name}/history", response_model=List[StatsResponse])
async def get_player_history(
    player_name: str,
    format: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user)
):
    """Get player performance history."""
    with get_db_connection() as conn:
        # Query logic
        return results
```

### 3. Nouvelle règle d'archétype

```python
# Ajouter dans archetype_rules
{
    "format": "modern",
    "archetype": "New Combo Deck",
    "rules": {
        "include": [
            {"name": "Key Card A", "min": 4},
            {"name": "Key Card B", "min": 3}
        ],
        "exclude": [
            {"name": "Card That Excludes This Deck"}
        ],
        "conditions": {
            "min_cards": 10,
            "color_identity": ["U", "R"]
        }
    }
}
```

### 4. Nouveau visualiseur

```python
# src/visualizations/win_rate_chart.py
import matplotlib.pyplot as plt
from typing import Dict, List

def generate_win_rate_timeline(
    archetype_id: int, 
    days: int = 30,
    output_path: str = None
) -> bool:
    """Generate win rate evolution chart."""
    with get_db_connection() as conn:
        # Get data
        data = fetch_win_rate_data(conn, archetype_id, days)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data['dates'], data['win_rates'], marker='o')
        
        # Styling
        ax.set_title(f'Win Rate Evolution - {data["archetype_name"]}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Win Rate %')
        ax.grid(True, alpha=0.3)
        
        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        return True
```

## 🧪 Tests et Qualité

### Structure des tests

```
tests/
├── unit/              # Tests unitaires
│   ├── test_parsers.py
│   ├── test_analyzers.py
│   └── test_utils.py
├── integration/       # Tests d'intégration
│   ├── test_api.py
│   ├── test_scrapers.py
│   └── test_database.py
├── e2e/              # Tests end-to-end
│   └── test_pipeline.py
└── fixtures/         # Données de test
    ├── sample_decks.json
    └── mock_responses.py
```

### Écrire des tests

```python
# tests/unit/test_deck_parser.py
import pytest
from src.parsers.deck_parser import DeckParser

class TestDeckParser:
    @pytest.fixture
    def parser(self):
        return DeckParser()
    
    def test_parse_valid_deck(self, parser):
        """Test parsing a valid decklist."""
        content = """
        4 Lightning Bolt
        4 Goblin Guide
        
        Sideboard
        3 Smash to Smithereens
        """
        mainboard, sideboard = parser.parse_decklist(content)
        
        assert len(mainboard) == 2
        assert mainboard[0]['quantity'] == 4
        assert mainboard[0]['name'] == 'Lightning Bolt'
        assert len(sideboard) == 1
    
    @pytest.mark.parametrize("invalid_content", [
        "",  # Empty
        "Not a valid deck",  # No quantities
        "5 Lightning Bolt",  # Invalid quantity
    ])
    def test_parse_invalid_deck(self, parser, invalid_content):
        """Test parsing invalid decklists."""
        with pytest.raises(ValueError):
            parser.parse_decklist(invalid_content)
```

### Commandes de test

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=src --cov-report=html

# Tests spécifiques
pytest tests/unit/test_parsers.py -v

# Tests marqués
pytest -m "not slow"

# Tests en parallèle
pytest -n auto
```

### Linting et formatage

```bash
# Formatage
black src/ tests/
isort src/ tests/

# Linting
pylint src/
mypy src/

# Security
bandit -r src/

# Tout en une fois
pre-commit run --all-files
```

## ⚡ Performance

### Profiling

```python
# Décorateur de profiling
import time
import functools
import logging

def profile_time(func):
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.info(f"{func.__name__} took {end - start:.3f}s")
        return result
    return wrapper

# Usage
@profile_time
def expensive_operation():
    # Code here
    pass
```

### Optimisations courantes

1. **Batch operations**:
```python
# ❌ Mauvais
for deck in decks:
    cursor.execute("INSERT INTO decklists ...", deck)

# ✅ Bon
cursor.executemany("INSERT INTO decklists ...", decks)
```

2. **Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_archetype_rules(format_name: str) -> Dict:
    # Expensive operation cached
    return fetch_rules_from_db(format_name)
```

3. **Async operations**:
```python
# Scraping parallèle
async def scrape_all_formats():
    tasks = [
        scrape_format(fmt) 
        for fmt in ['modern', 'legacy', 'standard']
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### Monitoring performance

```python
# src/api/middleware.py
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🔒 Sécurité

### Checklist sécurité

- [ ] Jamais de secrets dans le code
- [ ] Validation de toutes les entrées utilisateur
- [ ] Prepared statements pour SQL
- [ ] Rate limiting sur l'API
- [ ] HTTPS en production
- [ ] Logs sans données sensibles
- [ ] Dependencies à jour

### Exemples de sécurisation

```python
# 1. Validation d'entrée
from pydantic import BaseModel, validator

class DeckCreate(BaseModel):
    name: str
    format: str
    cards: List[Dict]
    
    @validator('name')
    def name_must_be_safe(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric')
        return v
    
    @validator('format')
    def format_must_be_valid(cls, v):
        valid_formats = ['standard', 'modern', 'legacy', 'vintage', 'pioneer', 'pauper']
        if v not in valid_formats:
            raise ValueError(f'Format must be one of {valid_formats}')
        return v

# 2. SQL injection prevention
def get_deck_by_id(deck_id: str):
    # ❌ Jamais faire ça
    query = f"SELECT * FROM decks WHERE id = '{deck_id}'"
    
    # ✅ Toujours utiliser des paramètres
    cursor.execute("SELECT * FROM decks WHERE id = %s", (deck_id,))

# 3. Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/expensive-operation")
@limiter.limit("5/minute")
async def expensive_operation(request: Request):
    return {"result": "ok"}
```

## 🗺️ Roadmap

### Phase 1: Stabilisation (Current)
- [x] Infrastructure Docker
- [x] API REST basique
- [x] Scrapers MTGO/Melee
- [x] Détection d'archétypes
- [x] Tests d'intégration
- [ ] Documentation complète
- [ ] CI/CD pipeline

### Phase 2: Fonctionnalités
- [ ] Websockets pour real-time
- [ ] GraphQL API
- [ ] Machine Learning pour détection
- [ ] Prédiction de méta
- [ ] API publique avec SDK
- [ ] Système de notifications

### Phase 3: Scaling
- [ ] Kubernetes deployment
- [ ] Microservices architecture
- [ ] Event sourcing
- [ ] Multi-région
- [ ] CDN pour assets

### Phase 4: Écosystème
- [ ] Plugin système
- [ ] Marketplace de règles
- [ ] Mobile apps
- [ ] Integration Twitch/Discord
- [ ] Tournament organizer tools

## 🤝 Contribution

### Process

1. Fork le repo
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

### Standards

- Tests pour toute nouvelle fonctionnalité
- Documentation mise à jour
- Respect des conventions de code
- Changelog maintenu
- Review par au moins 1 personne

### Commandes utiles

```bash
# Vérifier avant de commit
make lint
make test
make security-check

# Build local
make build

# Run local
make run-local

# Full check
make all
```

---

Pour des questions spécifiques, voir les autres guides ou créer une issue.