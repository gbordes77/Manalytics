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
