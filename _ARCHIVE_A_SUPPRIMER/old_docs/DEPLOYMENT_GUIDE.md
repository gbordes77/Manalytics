# 🚀 GUIDE DE DÉPLOIEMENT - MANALYTICS

## 📋 Prérequis système

### Environnement testé et fonctionnel
- **OS :** macOS 24.5.0 (Darwin)
- **Python :** 3.13.5
- **Shell :** /bin/zsh
- **Répertoire :** `/Volumes/DataDisk/_Projects/Manalytics`

### Dépendances Python requises
```bash
pip install fastapi uvicorn python-multipart
pip install pandas numpy matplotlib seaborn scikit-learn
pip install requests asyncio subprocess
```

## 🏃‍♂️ Démarrage rapide (PROCÉDURE TESTÉE)

### 1. Préparation de l'environnement
```bash
# Naviguer vers le projet
cd /Volumes/DataDisk/_Projects/Manalytics

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances critiques
pip install python-multipart
```

### 2. Nettoyage des processus existants
```bash
# Arrêter tous les processus FastAPI existants
pkill -f "python.*fastapi_app_simple"

# Vérifier qu'aucun processus n'utilise le port 8000
lsof -i :8000
```

### 3. Démarrage du serveur
```bash
# Naviguer vers le répertoire API
cd src/python/api

# Démarrer le serveur en arrière-plan
python fastapi_app_simple.py &

# Attendre 3 secondes pour le démarrage
sleep 3
```

### 4. Vérification du fonctionnement
```bash
# Test de santé (doit retourner status: healthy)
curl -s http://localhost:8000/health

# Test de l'interface web
curl -s http://localhost:8000/web | head -20

# Test du générateur d'analyses
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis
```

## 🔧 Configuration des services

### Structure des fichiers de configuration
```
Manalytics/
├── src/python/api/fastapi_app_simple.py    # Serveur principal
├── advanced_metagame_analyzer.py           # Moteur d'analyse
├── real_data/                             # Données sources
│   ├── standard_tournaments.json
│   ├── modern_tournaments.json
│   └── ...
├── analysis_output/                       # Sorties générées
└── venv/                                 # Environnement virtuel
```

### Variables d'environnement
```bash
# Répertoire du projet
export MANALYTICS_HOME="/Volumes/DataDisk/_Projects/Manalytics"

# Port du serveur
export MANALYTICS_PORT=8000

# Répertoire des données
export MANALYTICS_DATA_DIR="$MANALYTICS_HOME/real_data"

# Répertoire de sortie
export MANALYTICS_OUTPUT_DIR="$MANALYTICS_HOME/analysis_output"
```

## 🐳 Containerisation (Recommandée)

### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY advanced_metagame_analyzer.py .
COPY real_data/ ./real_data/

# Exposer le port
EXPOSE 8000

# Créer le répertoire de sortie
RUN mkdir -p analysis_output

# Commande de démarrage
CMD ["python", "src/python/api/fastapi_app_simple.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  manalytics:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./analysis_output:/app/analysis_output
      - ./real_data:/app/real_data
    environment:
      - PYTHONPATH=/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📊 Monitoring et logs

### Logs du serveur
```bash
# Suivre les logs en temps réel
tail -f /var/log/manalytics/server.log

# Logs des analyses
tail -f /var/log/manalytics/analysis.log
```

### Métriques importantes
- **Statut serveur :** `GET /health`
- **Utilisation mémoire :** Surveiller les analyses lourdes
- **Espace disque :** Répertoire `analysis_output/`
- **Processus :** `ps aux | grep fastapi_app_simple`

## 🔒 Sécurité

### Recommandations
1. **Firewall :** Restreindre l'accès au port 8000
2. **HTTPS :** Utiliser un reverse proxy (nginx/traefik)
3. **Authentification :** Ajouter JWT ou OAuth2
4. **Rate limiting :** Limiter les appels API

### Configuration nginx (exemple)
```nginx
server {
    listen 80;
    server_name manalytics.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚨 Dépannage

### Problèmes courants

#### 1. Port 8000 déjà utilisé
```bash
# Identifier le processus
lsof -i :8000

# Arrêter le processus
pkill -f "python.*fastapi_app_simple"
```

#### 2. Erreur python-multipart
```bash
# Installer la dépendance
pip install python-multipart

# Redémarrer le serveur
python src/python/api/fastapi_app_simple.py
```

#### 3. Erreur de clustering
```bash
# Vérifier les données
ls -la real_data/
head real_data/standard_tournaments.json

# Le clustering s'adapte automatiquement depuis la correction
```

#### 4. Données manquantes
```bash
# Vérifier la présence des fichiers de données
ls -la real_data/*.json

# Taille des fichiers (doivent être > 100KB)
du -h real_data/*.json
```

## 📈 Mise à l'échelle

### Optimisations recommandées
1. **Cache Redis :** Pour les analyses fréquentes
2. **Queue système :** Celery pour les analyses lourdes
3. **Load balancer :** Multiple instances FastAPI
4. **Base de données :** PostgreSQL pour les métadonnées

### Configuration haute disponibilité
```bash
# Multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  src.python.api.fastapi_app_simple:app \
  --bind 0.0.0.0:8000
```

## 🔄 Sauvegarde et restauration

### Données critiques à sauvegarder
- `real_data/` - Données sources
- `analysis_output/` - Analyses générées
- `src/` - Code source
- `requirements.txt` - Dépendances

### Script de sauvegarde
```bash
#!/bin/bash
BACKUP_DIR="/backups/manalytics/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Sauvegarder les données
cp -r real_data/ "$BACKUP_DIR/"
cp -r analysis_output/ "$BACKUP_DIR/"
cp -r src/ "$BACKUP_DIR/"
cp requirements.txt "$BACKUP_DIR/"

# Compresser
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
```

## 📞 Support et maintenance

### Commandes utiles
```bash
# Statut du serveur
curl http://localhost:8000/health

# Redémarrage complet
pkill -f fastapi_app_simple && sleep 2 && \
cd src/python/api && python fastapi_app_simple.py &

# Nettoyage des fichiers temporaires
rm -rf analysis_output/visualizations/*.png
rm -rf __pycache__/ src/__pycache__/
```

### Contacts
- **Équipe de développement :** [À compléter]
- **Administrateur système :** [À compléter]
- **Documentation :** Ce guide + HANDOFF_DOCUMENTATION.md

---
*Guide créé le 12 juillet 2025 - Testé et validé* 