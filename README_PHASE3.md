# Manalytics Phase 3 - Produit & Intelligence Avancée

## 🚀 Vue d'ensemble

La Phase 3 de Manalytics transforme le pipeline de données en une **plateforme complète d'intelligence artificielle** pour Magic: The Gathering. Cette phase apporte des fonctionnalités avancées d'IA, de gamification, et une architecture microservices complète.

## 🎯 Nouvelles Fonctionnalités

### 🤖 Intelligence Artificielle & ML
- **Prédiction de Métagame LSTM** : Modèle deep learning pour prédire l'évolution du métagame
- **Système de Recommandation** : Recommandations personnalisées basées sur le style de jeu
- **Analyse NLP** : Traitement du langage naturel pour l'analyse de contenu
- **Détection d'Innovation** : IA pour identifier les nouvelles stratégies

### 🌐 API & Backend Avancé
- **API FastAPI** : Backend haute performance avec WebSocket temps réel
- **GraphQL Avancé** : API GraphQL avec subscriptions et types complexes
- **WebSocket Temps Réel** : Mises à jour en direct du métagame
- **Microservices** : Architecture distribuée et scalable

### 🎮 Gamification & Engagement
- **Système d'Achievements** : Déblocage de récompenses et badges
- **Leaderboards** : Classements compétitifs
- **Prédictions Compétitives** : Concours de prédictions avec prix
- **Profils Utilisateurs** : Tracking détaillé des performances

### 📊 Dashboard Interactif
- **Interface Streamlit** : Dashboard moderne et interactif
- **Visualisations Avancées** : Graphiques temps réel avec Plotly
- **Métriques Business** : KPIs et analytics pour les décideurs
- **Alertes Intelligentes** : Notifications contextuelles

## 🏗️ Architecture

```
Manalytics Phase 3 - Architecture Microservices
├── API Layer
│   ├── FastAPI Backend (Port 8000)
│   ├── GraphQL Endpoint
│   └── WebSocket Service
├── ML/AI Layer
│   ├── LSTM Predictor
│   ├── Recommendation Engine
│   └── NLP Analyzer
├── Gamification Layer
│   ├── Achievement System
│   ├── Prediction League
│   └── Leaderboard
├── Frontend Layer
│   ├── Streamlit Dashboard (Port 8501)
│   └── Interactive Visualizations
└── Data Layer
    ├── Redis Cache
    ├── PostgreSQL Database
    └── Time Series Data
```

## 🛠️ Installation & Démarrage

### Prérequis
```bash
# Python 3.9+
python --version

# Redis Server
redis-server --version

# PostgreSQL (optionnel)
psql --version
```

### Installation
```bash
# Cloner le repository
git clone <repository-url>
cd Manalytics

# Installer les dépendances
pip install -r requirements.txt

# Démarrer Redis
redis-server

# Créer les dossiers nécessaires
mkdir -p logs models data
```

### Démarrage Phase 3
```bash
# Démarrage complet
python start_phase3.py

# Services disponibles :
# - API FastAPI: http://localhost:8000
# - Documentation API: http://localhost:8000/docs
# - Dashboard Streamlit: http://localhost:8501
# - GraphQL Playground: http://localhost:8000/graphql
```

## 🔧 Configuration

### Variables d'environnement
```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API
API_HOST=0.0.0.0
API_PORT=8000

# ML Models
MODEL_PATH=models/
TORCH_DEVICE=cpu

# Gamification
POINTS_MULTIPLIER=1.0
ACHIEVEMENTS_ENABLED=true
```

### Configuration des Services
```yaml
# config/phase3.yaml
services:
  api:
    host: "0.0.0.0"
    port: 8000
    workers: 1
    
  ml:
    model_path: "models/"
    prediction_interval: 3600  # 1 heure
    
  gamification:
    leaderboard_size: 100
    achievement_checks: true
    
  cache:
    ttl_default: 300  # 5 minutes
    max_connections: 100
```

## 📡 API Endpoints

### REST API (FastAPI)
```python
# Métagame
GET /metagame/{format}
GET /metagame/{format}/trends

# Prédictions
POST /predictions/submit
GET /predictions/{tournament_id}

# Utilisateurs
GET /users/{user_id}/profile
GET /users/{user_id}/achievements

# Temps réel
WebSocket /ws/metagame/{format}
WebSocket /ws/tournament/{tournament_id}
```

### GraphQL API
```graphql
# Queries
query {
  metagameSnapshot(format: "modern") {
    name
    metaShare
    winRate
    trending
  }
  
  predictMetagame(format: "modern", weeksAhead: 2) {
    predictedShares
    emergingDecks
    confidence
  }
}

# Mutations
mutation {
  submitPrediction(input: {
    tournamentId: "123"
    top8Predictions: ["Burn", "Control"]
    confidence: 0.8
  })
}

# Subscriptions
subscription {
  metagameUpdates(format: "modern") {
    type
    data
    timestamp
  }
}
```

## 🤖 Modèles ML

### Prédicteur de Métagame
```python
from ml.metagame_predictor import MetagamePredictor

# Initialiser le modèle
predictor = MetagamePredictor()

# Entraîner avec des données historiques
training_data = load_historical_data()
predictor.train(training_data, epochs=100)

# Faire des prédictions
current_meta = get_current_metagame("modern")
prediction = predictor.predict_next_week(current_meta)

print(f"Confiance: {prediction.confidence}")
print(f"Archétypes émergents: {prediction.emerging_decks}")
```

### Système de Recommandation
```python
from ml.recommendation_engine import PersonalizedRecommender

# Analyser le style d'un joueur
recommender = PersonalizedRecommender()
player_profile = recommender.analyze_player_style("player123", match_history)

# Recommander des decks
recommendations = recommender.recommend_deck("player123", "modern", budget=500)

for rec in recommendations:
    print(f"{rec.archetype}: {rec.match_score:.2f}")
```

## 🎮 Gamification

### Système d'Achievements
```python
from gamification.gamification_engine import GamificationEngine

engine = GamificationEngine()

# Tracker une action
action = await engine.track_user_action("user123", "prediction_success", {
    "confidence": 0.8,
    "tournament_id": "PT_123"
})

print(f"Points gagnés: {action.points_earned}")
print(f"Achievements: {action.achievements_unlocked}")
```

### Concours de Prédictions
```python
# Créer un concours
contest = await engine.create_prediction_contest("PT_123", {
    "prize_pool": 1000,
    "scoring_rules": {
        "exact_top8": 100,
        "winner_prediction": 200
    }
})

# Soumettre une prédiction
success = await engine.submit_prediction("user123", "PT_123", {
    "top8": ["Burn", "Control", "Combo"],
    "winner": "Burn"
})
```

## 📊 Métriques & Monitoring

### Métriques Temps Réel
- **Connexions WebSocket actives**
- **Prédictions par minute**
- **Précision des modèles ML**
- **Engagement utilisateur**

### Dashboards
- **Métagame en temps réel**
- **Performance des prédictions**
- **Classements et achievements**
- **Métriques business**

## 🔒 Sécurité

### Authentification
```python
# JWT Token authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    # Validation du token
    return user
```

### Rate Limiting
```python
# Limitation des requêtes
from slowapi import Limiter, _rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/predictions")
@limiter.limit("10/minute")
async def get_predictions():
    return predictions
```

## 🧪 Tests

### Tests Unitaires
```bash
# Lancer tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_ml_predictor.py
pytest tests/test_gamification.py
pytest tests/test_api.py
```

### Tests d'Intégration
```bash
# Tests API
pytest tests/integration/test_api_endpoints.py

# Tests WebSocket
pytest tests/integration/test_websocket.py
```

## 🚀 Déploiement

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["python", "start_phase3.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  manalytics:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    depends_on:
      - redis
      - postgres
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
      
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: manalytics
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

## 📈 Performance

### Optimisations
- **Cache Redis intelligent** avec TTL adaptatif
- **Traitement parallèle** des prédictions
- **Compression des WebSocket** pour réduire la latence
- **Modèles ML optimisés** avec quantification

### Benchmarks
- **API Response Time**: < 100ms (95th percentile)
- **WebSocket Latency**: < 50ms
- **ML Prediction Time**: < 2s
- **Cache Hit Rate**: > 85%

## 🛣️ Roadmap

### Phase 3.1 - Extensions
- [ ] Mobile App (React Native)
- [ ] Blockchain Integration (Web3)
- [ ] Advanced NLP (GPT Integration)
- [ ] Real-time Tournament Integration

### Phase 3.2 - Scaling
- [ ] Kubernetes Deployment
- [ ] Multi-region Support
- [ ] Advanced Analytics
- [ ] Enterprise Features

## 🤝 Contribution

### Développement
```bash
# Setup développement
git clone <repo>
cd Manalytics
pip install -e .
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Lancer les tests
pytest
```

### Guidelines
- Code style: Black + flake8
- Documentation: Docstrings obligatoires
- Tests: Coverage > 80%
- Type hints: mypy compatible

## 📞 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **GraphQL Playground**: http://localhost:8000/graphql
- **Streamlit Dashboard**: http://localhost:8501

### Issues & Bugs
- Créer une issue GitHub avec le template approprié
- Inclure les logs et la configuration
- Spécifier la version et l'environnement

## 📜 License

MIT License - Voir le fichier LICENSE pour plus de détails.

---

**Manalytics Phase 3** - Transforming Magic: The Gathering data into actionable intelligence through advanced AI and gamification. 🎯✨ 