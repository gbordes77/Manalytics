# 🚫 POLITIQUE NO MOCK DATA - RÈGLES ABSOLUES

## 📢 MESSAGE DIRECT À L'ÉQUIPE

**❌ AUCUNE donnée inventée (test, mock, Player1, etc.)**  
**✅ UNIQUEMENT des données réelles (tournois scrapés)**

**Toute violation = Code rejeté automatiquement**

---

## 🎯 RÈGLES ABSOLUES

### ❌ INTERDIT
- Créer des données "test", "mock", "example", "fake", "dummy"
- Utiliser Player1, Player2, Deck1, Deck2, Card1, Card2
- Générer des IDs aléatoires ou génériques
- Hardcoder des decklists inventées
- Importer unittest.mock, pytest-mock, responses
- Utiliser @mock, @patch, Mock(), MagicMock()

### ✅ OBLIGATOIRE
- Utiliser MTGODecklistCache pour les données
- Scraper de vrais tournois depuis Melee.gg/MTGO
- Valider toutes les données avec RealDataValidator
- Minimum 10 tournois réels avant de lancer le pipeline
- Utiliser les fixtures `real_tournament_data`, `real_deck`, etc.

---

## 🔧 MISE EN PLACE IMMÉDIATE

### 1. Activer la politique
```bash
# Activer la politique NO MOCK DATA
python activate_no_mock_policy.py

# Configurer les variables d'environnement
export NO_MOCK_DATA=true
export REJECT_MOCK_DATA=true
export REQUIRE_REAL_SOURCES=true
```

### 2. Configurer Git hooks
```bash
# Le hook pre-commit est automatiquement configuré
# Il rejette tout commit avec données mockées
git add .
git commit -m "test"  # Sera rejeté si mock détecté
```

### 3. Obtenir des données réelles
```bash
# Option 1: Cloner le cache existant
git clone https://github.com/Jiliac/MTGODecklistCache data/real_cache

# Option 2: Scraper des vrais tournois
python fetch_tournament.py ./data 2024-01-01 2024-12-31 mtgo

# Vérifier qu'on a assez de données
ls -la data/real_cache/Tournaments/**/*.json | wc -l
# Doit afficher > 100 fichiers
```

---

## 👨‍💻 WORKFLOW DÉVELOPPEUR

### Avant TOUT développement
```bash
# 1. Vérifier les données réelles
python scripts/check_no_mocks.py

# 2. Activer le mode strict
python -c "from config.no_mock_policy import enforce_real_data_only; enforce_real_data_only()"

# 3. Valider l'environnement
python -c "from config.no_mock_policy import Settings; Settings.validate_environment()"
```

### Pour les tests
```python
# ❌ INTERDIT
def test_something():
    deck = {
        'player': 'TestPlayer',  # NON!
        'mainboard': [{'name': 'TestCard', 'count': 4}]  # NON!
    }

# ✅ OBLIGATOIRE
def test_something(real_tournament, validate_real_data):
    # Valider que les données sont réelles
    validate_real_data(real_tournament)
    
    # Utiliser de VRAIES données
    deck = real_tournament['decks'][0]  # Vraie donnée
    
    # Tester avec des données réelles
    assert deck['mainboard']
    assert len(deck['mainboard']) >= 60
```

### Pour le développement
```python
# ❌ INTERDIT
from unittest.mock import Mock
import pytest_mock

# ✅ OBLIGATOIRE
from config.no_mock_policy import get_real_tournament_data, real_data_only

@real_data_only
def process_tournament(tournament_data):
    # Fonction automatiquement validée
    return analyze_metagame(tournament_data)

# Utiliser des données réelles
tournaments = get_real_tournament_data()
result = process_tournament(tournaments[0])
```

---

## 🧪 FRAMEWORK DE TESTS

### Fixtures disponibles
```python
# Fixtures automatiquement disponibles dans tous les tests
def test_classification(real_tournament):
    # Un tournoi réel complet
    pass

def test_deck_analysis(real_deck):
    # Un deck réel avec mainboard/sideboard
    pass

def test_archetype_detection(real_decklist):
    # Une decklist réelle (mainboard)
    pass

def test_multiple_formats(real_standard_data, real_modern_data):
    # Données réelles par format
    pass

def test_validation(validate_real_data):
    # Fonction de validation
    data = get_some_data()
    validate_real_data(data)  # Lève une exception si mock
```

### Exemple complet
```python
def test_metagame_analysis(real_tournament_data, validate_real_data):
    """Test avec données réelles uniquement"""
    
    # Valider les données d'entrée
    validate_real_data(real_tournament_data)
    
    # Utiliser l'analyseur avec de vraies données
    analyzer = MetagameAnalyzer()
    results = analyzer.analyze(real_tournament_data)
    
    # Valider les résultats
    validate_real_data(results)
    
    # Assertions sur des données réelles
    assert len(results['archetypes']) > 0
    assert all(archetype != 'TestArchetype' for archetype in results['archetypes'])
```

---

## 🚀 CI/CD ENFORCEMENT

### GitHub Actions
Le workflow `.github/workflows/no-mock-validation.yml` :
- Scanne automatiquement le code pour détecter les mocks
- Valide que les données réelles sont disponibles
- Rejette les PR avec données mockées
- Génère un rapport de validation

### Validation automatique
```yaml
# Chaque push/PR déclenche:
- name: Check for mock data
  run: python scripts/check_no_mocks.py

- name: Validate real data usage
  run: python -c "from config.no_mock_policy import Settings; Settings.validate_environment()"
```

---

## 📊 SOURCES DE DONNÉES AUTORISÉES

### ✅ Sources approuvées
1. **MTGODecklistCache** : `./MTGODecklistCache/Tournaments/`
2. **Données scrapées** : `./data/raw/`
3. **API Scryfall** : `https://api.scryfall.com`
4. **Scraping direct** : Melee.gg, MTGO.com, TopDeck.gg

### 📁 Structure des données réelles
```
MTGODecklistCache/
└── Tournaments/
    ├── mtgo/
    │   └── 2024/
    │       └── 01/
    │           └── 15/
    │               └── modern-challenge-2024-01-15.json
    └── melee.gg/
        └── 2024/
            └── 07/
                └── 02/
                    └── standard-showdown-2024-07-02.json
```

### 🔍 Validation des données
```python
# Chaque fichier JSON doit contenir:
{
    "id": "modern-challenge-2024-01-15",  # ID réel
    "date": "2024-01-15",
    "format": "Modern",
    "source": "mtgo",
    "decks": [
        {
            "player": "RealPlayerName",  # Nom réel
            "archetype": "Burn",  # Archétype réel
            "mainboard": [
                {"name": "Lightning Bolt", "count": 4}  # Cartes réelles
            ]
        }
    ]
}
```

---

## 🛠️ OUTILS ET COMMANDES

### Scripts disponibles
```bash
# Vérifier le codebase
python scripts/check_no_mocks.py

# Vérifier un fichier spécifique
python scripts/check_no_mocks.py src/classifier/archetype_engine.py

# Vérifier les fichiers staged
python scripts/check_no_mocks.py --staged

# Activer la politique
python activate_no_mock_policy.py

# Valider l'environnement
python -c "from enforcement.strict_mode import enforce_real_data_only; enforce_real_data_only()"
```

### Commandes de validation
```bash
# Vérifier les données réelles disponibles
find MTGODecklistCache/Tournaments -name "*.json" | wc -l

# Tester les fixtures
python -m pytest tests/test_real_data_fixtures.py -v

# Valider un tournoi
python -c "
from config.no_mock_policy import RealDataEnforcer
import json
with open('path/to/tournament.json') as f:
    data = json.load(f)
RealDataEnforcer.validate_tournament_data(data)
"
```

---

## 🚨 GESTION DES VIOLATIONS

### Détection automatique
- **Git hook** : Rejette les commits avec mocks
- **CI/CD** : Échoue les builds avec données mockées
- **Tests** : Échouent si des mocks sont détectés
- **Import** : Bloque les imports de modules de mock

### Messages d'erreur typiques
```
❌ DONNÉES MOCKÉES DÉTECTÉES! Mot-clé interdit: 'mock'
📋 Règle: TOUTES les données doivent être RÉELLES (scraping/API)
🔧 Action: Remplacer par des données réelles depuis MTGODecklistCache

❌ PATTERN MOCKÉ DÉTECTÉ: Player\d+
📋 Données suspectes: {'player': 'Player1', 'deck': 'TestDeck'}
🔧 Action: Utiliser de vraies données de tournois

❌ MODULE INTERDIT: unittest.mock
📋 Règle: Aucun mock autorisé
🔧 Utiliser des données réelles uniquement
```

### Actions correctives
1. **Remplacer** toutes les données mockées par des données réelles
2. **Utiliser** MTGODecklistCache pour les tests
3. **Supprimer** tous les imports de mock
4. **Valider** avec `python scripts/check_no_mocks.py`

---

## 📚 EXEMPLES PRATIQUES

### Migration d'un test mocké
```python
# AVANT (❌ INTERDIT)
def test_archetype_classification():
    mock_deck = {
        'player': 'TestPlayer',
        'mainboard': [{'name': 'TestCard', 'count': 4}]
    }
    result = classifier.classify(mock_deck)
    assert result == 'TestArchetype'

# APRÈS (✅ CORRECT)
def test_archetype_classification(real_deck, validate_real_data):
    # Valider que le deck est réel
    validate_real_data(real_deck)
    
    # Utiliser le classificateur avec de vraies données
    result = classifier.classify(real_deck)
    
    # Valider le résultat
    validate_real_data(result)
    
    # Assertions sur des données réelles
    assert result in ['Burn', 'Control', 'Aggro', 'Midrange']
    assert result != 'TestArchetype'
```

### Scraping de nouvelles données
```python
# Obtenir de vraies données pour un nouveau format
def get_pioneer_data():
    scraper = MeleeScraper()
    tournaments = scraper.fetch_tournaments(
        format='Pioneer',
        start_date='2024-01-01',
        end_date='2024-12-31'
    )
    
    # Valider que les données sont réelles
    for tournament in tournaments:
        RealDataEnforcer.validate_tournament_data(tournament)
    
    return tournaments
```

---

## 🎯 RÉSUMÉ POUR L'ÉQUIPE

### ✅ CE QU'IL FAUT FAIRE
1. **Utiliser** `real_tournament_data` dans tous les tests
2. **Scraper** de vrais tournois pour les nouvelles données
3. **Valider** avec `validate_real_data()` dans les tests
4. **Consulter** MTGODecklistCache pour des exemples
5. **Tester** avec `python scripts/check_no_mocks.py`

### ❌ CE QU'IL NE FAUT PAS FAIRE
1. **Créer** des données Player1, TestDeck, etc.
2. **Importer** unittest.mock, pytest-mock
3. **Utiliser** @mock, @patch, Mock()
4. **Hardcoder** des decklists inventées
5. **Ignorer** les erreurs de validation

### 🚀 WORKFLOW QUOTIDIEN
```bash
# Chaque matin
export NO_MOCK_DATA=true
python scripts/check_no_mocks.py

# Avant chaque commit
git add .
git commit -m "feature: nouvelle fonctionnalité"
# Le hook vérifie automatiquement

# Avant chaque PR
python -m pytest tests/ -v
# Les tests utilisent automatiquement des données réelles
```

---

**Cette politique garantit que PERSONNE ne peut introduire de données mockées dans le projet ! 💪**

*Toute question ? Consulter `config/no_mock_policy.py` pour les détails techniques.* 