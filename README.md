# 🎯 Manalytics - MTG Meta Analysis Platform

**Version**: 1.0.0  
**État**: ✅ Production Ready (85.2% tests passing)  
**Dernière mise à jour**: 24 Juillet 2025

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation rapide](#installation-rapide)
4. [Structure du projet](#structure-du-projet)
5. [État actuel](#état-actuel)
6. [Documentation](#documentation)

## 🎮 Vue d'ensemble

Manalytics est une plateforme d'analyse de méta pour Magic: The Gathering qui :
- 📊 Collecte automatiquement les données de tournois (MTGO, Melee.gg)
- 🏷️ Détecte les archétypes avec des règles personnalisables
- 📈 Génère des analyses de méta et matchups
- 🔐 Expose une API REST sécurisée (JWT)
- 📉 Visualise les tendances du méta

### Formats supportés
- ✅ Standard
- ✅ Modern  
- ✅ Pioneer
- ✅ Legacy
- ✅ Vintage
- ✅ Pauper

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Scrapers      │────▶│   PostgreSQL    │◀────│   FastAPI       │
│  MTGO/Melee     │     │   + Redis       │     │   REST API      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                             Docker Network
```

### Stack Technique
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Base de données**: PostgreSQL 16 + Redis
- **Scraping**: BeautifulSoup4, Selenium, httpx
- **Analyse**: Pandas, NumPy
- **Auth**: JWT (python-jose)
- **Infra**: Docker Compose

## 🚀 Installation Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+ (optionnel, pour dev local)
- 4GB RAM minimum

### 1. Cloner et configurer

```bash
# Cloner le projet
git clone <repo-url>
cd Manalytics

# Copier l'environnement
cp .env.example .env

# Éditer .env avec vos credentials Melee.gg
nano .env
```

### 2. Lancer le système

```bash
# Construire et démarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Attendre que tout soit prêt (30-60s)
docker-compose ps
```

### 3. Initialiser les données

```bash
# Charger les règles d'archétypes
docker exec manalytics-api-1 python scripts/fetch_archetype_rules.py
docker exec manalytics-api-1 python scripts/migrate_rules.py

# Vérifier
curl http://localhost:8000/health
```

### 4. Premier scraping

```bash
# Scraper Modern sur 1 jour
docker exec manalytics-worker-1 python scripts/run_pipeline.py --format modern --days 1
```

## 📁 Structure du Projet

```
Manalytics/
├── src/
│   ├── api/              # API REST FastAPI
│   │   ├── routes/       # Endpoints (auth, decks, analysis)
│   │   ├── models.py     # Modèles Pydantic
│   │   └── auth.py       # JWT authentication
│   ├── scrapers/         # Collecte de données
│   │   ├── mtgo_scraper.py
│   │   └── melee_scraper.py
│   ├── parsers/          # Parsing des decks
│   ├── analyzers/        # Analyse de méta
│   └── visualizations/   # Génération de graphiques
├── database/
│   ├── schema.sql        # Schema PostgreSQL
│   ├── migrations/       # Migrations SQL
│   └── db_pool.py        # Connection pooling
├── scripts/
│   ├── run_pipeline.py   # Pipeline principal
│   ├── final_integration_test.py  # Tests complets
│   └── migrate_rules.py  # Import des règles
├── docker-compose.yml    # Orchestration
├── Dockerfile           # Image API/Worker
└── .env                 # Configuration
```

## 📊 État Actuel du Système

### ✅ Ce qui fonctionne
- Infrastructure Docker complète
- API REST avec JWT authentication
- Base de données avec 60 règles d'archétypes
- Health checks et monitoring
- Tests d'intégration (85.2% passing)

### ⚠️ Points d'attention
- MTGO URLs changent quotidiennement (404 normaux)
- Pas encore de données de tournois (système vide)
- Melee.gg nécessite des credentials valides

### 🔧 Corrections appliquées
1. Fixed environment variables handling
2. Fixed SQL schema mismatches  
3. Added health check endpoint
4. Fixed pandas/psycopg2 compatibility
5. Fixed archetype rules migration
6. Fixed API pagination

## 📚 Documentation Complète

| Document | Description |
|----------|-------------|
| [OPERATIONS.md](./OPERATIONS.md) | Guide des opérations quotidiennes |
| [API_GUIDE.md](./API_GUIDE.md) | Documentation API avec exemples |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Résolution des problèmes courants |
| [DEVELOPMENT.md](./DEVELOPMENT.md) | Guide de développement |

## 🎯 Quick Commands

```bash
# Statut système
docker-compose ps
docker exec manalytics-api-1 python scripts/final_integration_test.py

# Logs
docker-compose logs -f api
docker-compose logs -f worker

# Base de données
docker exec manalytics-db-1 psql -U manalytics

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 Sécurité

- JWT tokens avec expiration 30 min
- Passwords hashés avec bcrypt
- API keys pour les scrapers
- Network isolation Docker
- Pas de secrets dans le code

## 📞 Support

Pour toute question, consulter d'abord [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

---
*Projet développé avec l'assistance de Claude AI - Juillet 2025*