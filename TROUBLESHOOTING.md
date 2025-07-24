# 🔧 Guide de Dépannage - Manalytics

Ce guide vous aidera à résoudre les problèmes courants rencontrés avec Manalytics.

## 📋 Table des Matières

1. [Problèmes de démarrage](#problèmes-de-démarrage)
2. [Erreurs Docker](#erreurs-docker)
3. [Problèmes de base de données](#problèmes-de-base-de-données)
4. [Erreurs API](#erreurs-api)
5. [Échecs de scraping](#échecs-de-scraping)
6. [Problèmes de performance](#problèmes-de-performance)
7. [Erreurs d'authentification](#erreurs-dauthentification)
8. [Debug avancé](#debug-avancé)

## 🚨 Problèmes de Démarrage

### Les conteneurs ne démarrent pas

**Symptôme**: `docker-compose up` échoue

**Solutions**:

```bash
# 1. Vérifier les logs
docker-compose logs

# 2. Nettoyer et redémarrer
docker-compose down -v
docker system prune -f
docker-compose up -d

# 3. Vérifier les ports
sudo lsof -i :8000  # API
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# 4. Tuer les processus bloquants
sudo kill -9 $(sudo lsof -t -i:8000)
```

### "Waiting for postgres to be ready..." indéfiniment

**Cause**: PostgreSQL met du temps à initialiser

**Solution**:
```bash
# Augmenter le timeout dans docker-compose.yml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U manalytics"]
  interval: 5s
  timeout: 10s  # Augmenter à 10s
  retries: 10   # Augmenter à 10
```

## 🐳 Erreurs Docker

### "No space left on device"

**Solution**:
```bash
# 1. Nettoyer les images inutilisées
docker system prune -a --volumes

# 2. Vérifier l'espace
df -h /var/lib/docker

# 3. Déplacer Docker data (si nécessaire)
sudo systemctl stop docker
sudo mv /var/lib/docker /new/path/docker
sudo ln -s /new/path/docker /var/lib/docker
sudo systemctl start docker
```

### "Cannot connect to Docker daemon"

**Solution**:
```bash
# Linux
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker

# macOS
open -a Docker
```

## 🗄️ Problèmes de Base de Données

### "FATAL: password authentication failed"

**Cause**: Mauvais mot de passe dans .env

**Solution**:
```bash
# 1. Vérifier .env
cat .env | grep DATABASE_URL

# 2. Recréer la DB
docker-compose down -v
docker-compose up -d db
docker exec -it manalytics-db-1 psql -U postgres -c "
CREATE USER manalytics WITH PASSWORD 'changeme';
CREATE DATABASE manalytics OWNER manalytics;"
```

### "relation does not exist"

**Cause**: Schema non initialisé

**Solution**:
```bash
# Réinitialiser le schema
docker exec -it manalytics-db-1 psql -U manalytics < database/schema.sql

# Vérifier
docker exec manalytics-db-1 psql -U manalytics -c "\dt manalytics.*"
```

### Erreurs de migration

**Symptôme**: "column archetype_rules.format does not exist"

**Solution**:
```bash
# La table utilise archetype_id, pas format
# Utiliser la version corrigée de migrate_rules.py
docker cp scripts/migrate_rules.py manalytics-api-1:/app/scripts/
docker exec manalytics-api-1 python scripts/migrate_rules.py
```

## 🌐 Erreurs API

### API retourne 404

**Vérifications**:
```bash
# 1. L'API est-elle lancée?
docker-compose ps api
curl http://localhost:8000/health

# 2. Logs API
docker-compose logs api --tail 50

# 3. Redémarrer
docker-compose restart api
```

### "Internal Server Error" (500)

**Debug**:
```bash
# 1. Voir l'erreur complète
docker-compose logs api | grep -A 10 "ERROR"

# 2. Mode debug
docker-compose down
DEBUG=true docker-compose up api
```

### CORS errors

**Solution dans src/api/app.py**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou liste spécifique
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📥 Échecs de Scraping

### MTGO retourne 404

**Cause normale**: Les URLs MTGO changent quotidiennement

**Vérification**:
```bash
# Tester manuellement l'URL du jour
curl -I "https://magic.wizards.com/en/articles/archive/mtgo-standings/modern-league-$(date +%Y-%m-%d)"
```

### Melee.gg authentication failed

**Solutions**:

1. **Vérifier les credentials**:
```bash
grep MELEE .env
```

2. **Tester manuellement**:
```python
docker exec -it manalytics-api-1 python -c "
from src.scrapers.melee_scraper import MeleeScraper
scraper = MeleeScraper('modern')
# Vérifier les logs
"
```

3. **Réinitialiser le token**:
```bash
docker exec manalytics-db-1 psql -U manalytics -c "
DELETE FROM manalytics.api_tokens WHERE source = 'melee';"
```

### Timeout errors

**Solution**:
```python
# Augmenter timeouts dans scrapers
self.session = httpx.Client(timeout=30.0)  # 30 secondes
```

## ⚡ Problèmes de Performance

### API très lente

**Diagnostic**:
```bash
# 1. Vérifier les ressources
docker stats

# 2. Analyser les requêtes lentes
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC LIMIT 5;"
```

**Solutions**:
- Ajouter des index
- Augmenter la RAM des conteneurs
- Activer le cache Redis

### Base de données surchargée

**Solutions**:
```bash
# 1. VACUUM
docker exec manalytics-db-1 psql -U manalytics -c "VACUUM ANALYZE;"

# 2. Augmenter les connexions
# Dans postgresql.conf
max_connections = 200
shared_buffers = 256MB
```

## 🔐 Erreurs d'Authentification

### "Invalid token"

**Causes possibles**:
1. Token expiré (30 min)
2. SECRET_KEY changé
3. Token malformé

**Debug**:
```bash
# Vérifier le SECRET_KEY
docker exec manalytics-api-1 python -c "
from config.settings import settings
print(f'SECRET_KEY: {settings.SECRET_KEY[:10]}...')
"

# Générer un nouveau token
curl -X POST http://localhost:8000/api/auth/token \
  -d "username=admin&password=changeme"
```

### "User not found"

**Solution**:
```bash
# Créer l'utilisateur
docker exec -it manalytics-api-1 python -c "
from src.api.auth import create_user, UserCreate
user = UserCreate(
    username='admin',
    email='admin@manalytics.com',
    password='changeme',
    full_name='Admin User'
)
create_user(user)
"
```

## 🔍 Debug Avancé

### Activer tous les logs

```bash
# 1. Variables d'environnement
export PYTHONUNBUFFERED=1
export LOG_LEVEL=DEBUG

# 2. Relancer avec logs verbeux
docker-compose down
docker-compose up
```

### Inspecter un conteneur

```bash
# Shell dans le conteneur
docker exec -it manalytics-api-1 bash

# Tester le code directement
python -c "
from database.db_pool import get_db_connection
with get_db_connection() as conn:
    print('DB OK!')
"
```

### Tracer une requête

```python
# Ajouter dans l'API
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    print(f"{request.method} {request.url} - {time.time() - start:.3f}s")
    return response
```

### Profiler les performances

```bash
# 1. Installer py-spy
pip install py-spy

# 2. Profiler l'API
docker exec manalytics-api-1 py-spy top -- python -m uvicorn src.api.app:app

# 3. Générer flamegraph
docker exec manalytics-api-1 py-spy record -o profile.svg -- python scripts/run_pipeline.py
```

## 📊 Commandes de Diagnostic

### Check-list complète

```bash
# Script de diagnostic
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== MANALYTICS DIAGNOSTIC ==="
echo ""
echo "1. Docker Status:"
docker-compose ps
echo ""
echo "2. API Health:"
curl -s http://localhost:8000/health | jq .
echo ""
echo "3. Database Connection:"
docker exec manalytics-db-1 psql -U manalytics -c "SELECT version();"
echo ""
echo "4. Redis Status:"
docker exec manalytics-redis-1 redis-cli ping
echo ""
echo "5. Disk Space:"
df -h | grep -E "(Filesystem|docker)"
echo ""
echo "6. Recent Errors:"
docker-compose logs --tail 20 | grep -i error
echo ""
echo "7. Test Suite:"
docker exec manalytics-api-1 python scripts/final_integration_test.py | grep "Success rate"
EOF

chmod +x diagnose.sh
./diagnose.sh
```

## 🆘 Problèmes Non Résolus?

Si votre problème persiste:

1. **Collecter les logs**:
```bash
docker-compose logs > logs_debug.txt
./diagnose.sh > diagnostic.txt
```

2. **Informations système**:
```bash
uname -a
docker --version
docker-compose --version
```

3. **Créer une issue** avec:
- Description du problème
- Étapes pour reproduire
- Logs et diagnostic
- Configuration (.env sans secrets)

---

Pour les opérations normales, voir [OPERATIONS.md](./OPERATIONS.md).