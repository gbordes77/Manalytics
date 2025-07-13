# 👩‍💻 Guide Développeur Manalytics

## 🚀 Setup Développement

### 1. Clone et Setup

```bash
git clone https://github.com/gbordes77/Manalytics.git
cd Manalytics
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils dev
```

### 2. Pre-commit Hooks

```bash
pre-commit install
# Vérifie : formatting, linting, tests avant commit
```

## 🏗️ Architecture du Code

### Principe SOLID Appliqué

- **Single Responsibility** : 1 module = 1 responsabilité
- **Open/Closed** : Extension via classes abstraites
- **Liskov Substitution** : Scrapers interchangeables
- **Interface Segregation** : Interfaces minimales
- **Dependency Inversion** : Injection de dépendances

### Patterns Utilisés

```python
# Factory Pattern pour scrapers
scraper = ScraperFactory.create(source="MTGO")

# Strategy Pattern pour analyses
analyzer = AnalyzerStrategy(method="bayesian")

# Observer Pattern pour logs
logger.attach(ConsoleObserver())
logger.attach(FileObserver("app.log"))
```

## 📝 Standards de Code

### Python Style

```python
# ✅ BON : Noms explicites, docstrings
def calculate_archetype_winrate(
    matches: List[Match],
    archetype: str,
    confidence_level: float = 0.95
) -> Tuple[float, float, float]:
    """
    Calculate winrate with confidence interval.
    
    Args:
        matches: List of match results
        archetype: Archetype name to analyze
        confidence_level: Statistical confidence (default 95%)
        
    Returns:
        Tuple of (winrate, lower_bound, upper_bound)
    """
    pass

# ❌ MAUVAIS : Noms obscurs, pas de doc
def calc_wr(m, a, c=0.95):
    pass
```

### Conventions de Nommage

- **Classes** : PascalCase
- **Fonctions/variables** : snake_case
- **Constantes** : UPPER_SNAKE_CASE
- **Modules** : lowercase

## 🧪 Tests

### Structure des Tests

```
tests/
├── unit/           # Tests unitaires isolés
├── integration/    # Tests d'intégration
├── e2e/           # Tests end-to-end
└── fixtures/      # Données de test
```

### Écrire un Test

```python
# tests/unit/test_classifier.py
import pytest
from src.classifier import Classifier

class TestClassifier:
    @pytest.fixture
    def classifier(self):
        return Classifier(rules_path="tests/fixtures/test_rules.json")
    
    def test_classify_known_archetype(self, classifier):
        deck = ["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"]
        result = classifier.classify(deck)
        assert result == "Red Deck Wins"
    
    def test_classify_unknown_returns_other(self, classifier):
        deck = ["Random Card 1", "Random Card 2"]
        result = classifier.classify(deck)
        assert result == "Other"
```

### Coverage Minimum

- **Global** : 80%
- **Core modules** : 90%
- **Nouvelles features** : 95%

## 🔧 Workflow de Développement

### 1. Nouvelle Feature

```bash
# 1. Créer branche
git checkout -b feature/add-vintage-support

# 2. Développer avec TDD
# - Écrire test qui fail
# - Implémenter jusqu'à ce que ça passe
# - Refactorer

# 3. Vérifier qualité
pytest
flake8 src/
black src/
mypy src/

# 4. Commit atomique
git add -p
git commit -m "feat: add Vintage format support

- Add VintageScraper class
- Update classifier rules for Vintage
- Add Vintage-specific tests

Closes #123"

# 5. Push et PR
git push origin feature/add-vintage-support
```

### 2. Bug Fix

```bash
# 1. Reproduire avec test
pytest tests/test_failing_case.py

# 2. Fix minimal
# Ne corriger QUE le bug

# 3. Vérifier régression
./run_all_tests.sh

# 4. Commit
git commit -m "fix: handle empty tournament data

Prevent KeyError when tournament has no decks

Fixes #456"
```

## 📊 Debugging

### Logs Structurés

```python
import structlog

logger = structlog.get_logger()

# Usage
logger.info(
    "scraping_completed",
    source="MTGO",
    tournaments_found=42,
    duration_seconds=12.3
)
```

### Performance Profiling

```bash
# CPU profiling
python -m cProfile -o profile.stats run_full_pipeline.py
snakeviz profile.stats

# Memory profiling
mprof run run_full_pipeline.py
mprof plot
```

## 🚀 Optimisation

### Checklist Performance

- ✅ Utiliser cache pour requêtes répétées
- ✅ Vectoriser calculs avec NumPy
- ✅ Paralléliser tâches indépendantes
- ✅ Lazy loading pour gros datasets
- ✅ Index sur structures fréquemment accédées

### Exemple Optimisation

```python
# ❌ LENT : Boucles Python
winrates = {}
for archetype in archetypes:
    wins = 0
    total = 0
    for match in matches:
        if match.archetype == archetype:
            total += 1
            if match.won:
                wins += 1
    winrates[archetype] = wins / total if total > 0 else 0

# ✅ RAPIDE : Vectorisé NumPy
import numpy as np
import pandas as pd

df = pd.DataFrame(matches)
winrates = df.groupby('archetype')['won'].agg(['sum', 'count'])
winrates['winrate'] = winrates['sum'] / winrates['count']
```

## 🌐 API Future

### Design RESTful Prévu

```
GET  /api/v1/metagame/{format}
GET  /api/v1/archetypes/{format}
GET  /api/v1/matchups/{format}/{archetype}
POST /api/v1/analyze
```

### GraphQL Schema Prévu

```graphql
type Query {
  metagame(format: Format!, startDate: Date!, endDate: Date!): Metagame
  archetype(name: String!): Archetype
  matchups(archetype: String!): [Matchup]
}

type Metagame {
  format: Format!
  dateRange: DateRange!
  archetypes: [Archetype]!
  totalDecks: Int!
}
```

## 📚 Ressources

### Documentation Externe

- [Plotly Python](https://plotly.com/python/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Pandas Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)

### Outils Recommandés

- **IDE** : VSCode avec extensions Python
- **Linting** : Flake8 + Black + isort
- **Testing** : Pytest + Coverage
- **Debugging** : PDB++ ou VSCode debugger 