#!/bin/bash
# rollback_to_phase2.sh
# Script de rollback intelligent Phase 3 → Phase 2

echo "🔄 Rollback Manalytics: Phase 3 → Phase 2"
echo "==========================================="

# 1. Backup complet avant rollback
echo "📦 Création backup complet..."
BACKUP_DIR="backup_phase3_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r src/ $BACKUP_DIR/
cp -r tests/ $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/
cp package*.json $BACKUP_DIR/ 2>/dev/null || true
git add .
git commit -m "BACKUP: État Phase 3 avant rollback" || true
git tag phase3-complete

# 2. Identifier et supprimer les composants Phase 3
echo "🗑️  Suppression composants Phase 3..."

# Components Phase 3 à supprimer
PHASE3_DIRS=(
    "src/dashboard"           # Dashboard interactif
    "src/frontend"           # Frontend React/Next.js
    "src/python/ml"          # Machine Learning
    "src/predictions"        # Moteur de prédictions
    "src/nlp"               # Analyse NLP
    "src/marketplace"       # Marketplace
    "src/blockchain"        # Web3 integration
    "src/mobile"            # App mobile
    "src/content_generator" # Génération contenu
    "src/python/gamification" # Gamification
    "src/python/graphql"    # GraphQL
)

PHASE3_FILES=(
    "src/python/api/graphql_schema.py"    # GraphQL (garder REST)
    "src/python/api/websocket_server.py"  # WebSocket temps réel
    "src/python/api/subscription.py"      # Subscriptions
    "**/ml_*.py"                   # Fichiers ML
    "**/predict_*.py"              # Fichiers prédiction
    "docker-compose.full.yml"      # Config complete
)

# Supprimer directories
for dir in "${PHASE3_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  - Suppression $dir"
        rm -rf "$dir"
    fi
done

# Supprimer fichiers
for pattern in "${PHASE3_FILES[@]}"; do
    find . -path "$pattern" -type f -delete 2>/dev/null
done

# 3. Nettoyer les dépendances Phase 3
echo "📋 Nettoyage dépendances..."

# Créer nouveau requirements.txt Phase 2 only
cat > requirements_phase2.txt << 'EOF'
# Core Python - Phase 1 & 2
aiohttp==3.9.0
asyncio==3.4.3
beautifulsoup4==4.12.2
pandas==2.1.3
pyyaml==6.0.1
python-dateutil==2.8.2

# Phase 2 - Production
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
prometheus-client==0.19.0
structlog==23.2.0
tenacity==8.2.3  # Pour retry logic
circuitbreaker==2.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0

# Monitoring & Ops
psutil==5.9.6
python-dotenv==1.0.0
EOF

# Backup ancien requirements
mv requirements.txt requirements_phase3_full.txt
mv requirements_phase2.txt requirements.txt

# 4. Nettoyer les imports Phase 3
echo "🔧 Nettoyage imports..."

# Script Python pour nettoyer les imports
cat > clean_imports.py << 'EOF'
import os
import re
from pathlib import Path

PHASE3_IMPORTS = [
    'from src.ml',
    'from src.predictions',
    'from src.dashboard',
    'import torch',
    'import tensorflow',
    'from transformers',
    'import strawberry',  # GraphQL
    'from web3',
    'import streamlit',
    'import plotly',
]

def clean_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for imp in PHASE3_IMPORTS:
        content = re.sub(f'^.*{imp}.*$', '', content, flags=re.MULTILINE)
    
    # Remove empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Cleaned {filepath}")

# Clean all Python files
for py_file in Path('src').rglob('*.py'):
    clean_file(py_file)
EOF

python clean_imports.py
rm clean_imports.py

# 5. Ajuster la configuration
echo "⚙️  Ajustement configuration..."

# Créer config Phase 2
cat > config_phase2.yaml << 'EOF'
# Configuration Manalytics - Phase 2 Production
app_name: Manalytics
version: 2.0.0
environment: production

# Scraping
scraping:
  cache_folder: "./data"
  max_retries: 5
  rate_limit: 0.5
  timeout: 30

# API REST uniquement (pas de GraphQL)
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  cors_origins: ["*"]
  rate_limit: "100/minute"

# Cache Redis
redis:
  host: "localhost"
  port: 6379
  db: 0
  ttl_default: 3600

# Monitoring
monitoring:
  prometheus_port: 9090
  log_level: "INFO"
  sentry_dsn: ""  # À configurer

# Pas de ML, Dashboard, WebSocket, etc.
features:
  enable_ml: false
  enable_dashboard: false
  enable_realtime: false
  enable_predictions: false
EOF

# 6. Ajuster les tests
echo "🧪 Ajustement tests..."

# Supprimer tests Phase 3
find tests/ -name "*ml*" -delete
find tests/ -name "*prediction*" -delete
find tests/ -name "*dashboard*" -delete
find tests/ -name "*websocket*" -delete

# 7. Mettre à jour orchestrator
echo "🔄 Mise à jour orchestrator..."

# Créer version simplifiée
cat > src/orchestrator_phase2.py << 'EOF'
"""
Orchestrator Manalytics - Phase 2 (Production-Ready)
Sans ML, Dashboard, ou fonctionnalités avancées
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from src.python.scraper import ScraperFactory
from src.python.classifier import ArchetypeEngine
from src.python.cache import RedisCache
from src.python.api import create_app
from src.python.monitoring import MetricsCollector

class ManalyticsOrchestrator:
    """Orchestrateur Phase 2 - Stable et Production-Ready"""
    
    def __init__(self, config_file='config_phase2.yaml'):
        self.config = self.load_config(config_file)
        self.cache = RedisCache(self.config['redis'])
        self.metrics = MetricsCollector()
        
    async def run_pipeline(self, format: str, start_date: str, end_date: str):
        """Pipeline Phase 2 sans ML ni prédictions"""
        try:
            # 1. Scraping avec cache
            await self.run_scrapers(format, start_date, end_date)
            
            # 2. Classification
            self.run_classifier(format)
            
            # 3. Analyse basique (pas de R avancé)
            self.generate_metagame_json(format)
            
            # 4. Update cache & metrics
            await self.update_cache()
            self.metrics.record_pipeline_run(format)
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            raise
EOF

mv src/orchestrator.py src/orchestrator_phase3.py
mv src/orchestrator_phase2.py src/orchestrator.py

# 8. Docker simplifié
echo "🐳 Simplification Docker..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
      
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
EOF

# 9. Mettre à jour README
echo "📝 Mise à jour documentation..."

cat > README_PHASE2.md << 'EOF'
# Manalytics - Phase 2 (Production-Ready)

## État actuel : Phase 2 Complète

### ✅ Fonctionnalités Phase 2
- Pipeline robuste avec retry & circuit breaker
- API REST complète avec FastAPI
- Cache Redis intelligent
- Monitoring Prometheus/Grafana
- Tests complets (unit, integration, e2e)
- CI/CD GitHub Actions
- Documentation OpenAPI

### ❌ Fonctionnalités Phase 3 (Supprimées)
- Dashboard interactif
- ML & Prédictions
- GraphQL & WebSocket
- Mobile app
- Blockchain integration

## Installation

```bash
pip install -r requirements.txt
docker-compose up -d
```

## Utilisation

```bash
python orchestrator.py --format modern --days 7
```

## API

```bash
# Docs API
http://localhost:8000/docs

# Endpoints principaux
GET /api/v1/metagame/{format}
GET /api/v1/archetype/{format}/{archetype}
GET /api/v1/health
```
EOF

# 10. Commit final
echo "💾 Sauvegarde état Phase 2..."

git add .
git commit -m "ROLLBACK: Phase 3 → Phase 2 (Production-Ready)

- Supprimé: ML, Dashboard, GraphQL, WebSocket, Mobile
- Conservé: API REST, Cache, Monitoring, Tests, CI/CD
- État stable pour production
- Performance maintenue
"

git tag phase2-stable

echo "✅ Rollback terminé !"
echo ""
echo "📊 Résumé:"
echo "  - État sauvegardé : tag 'phase3-complete'"
echo "  - Nouvel état : tag 'phase2-stable'"
echo "  - Backup complet : $BACKUP_DIR/"
echo ""
echo "🚀 Prochaines étapes:"
echo "  1. Relancer les tests : ./run_all_tests.sh"
echo "  2. Redémarrer services : docker-compose up -d"
echo "  3. Vérifier API : http://localhost:8000/docs" 