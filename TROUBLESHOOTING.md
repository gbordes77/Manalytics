# 🔧 GUIDE DE DÉPANNAGE - MANALYTICS

## 🚨 Problèmes courants et solutions

### 1. Port 8000 déjà utilisé
**Symptôme :**
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): [errno 48] address already in use
```

**Solution :**
```bash
# Identifier le processus utilisant le port
lsof -i :8000

# Arrêter tous les processus FastAPI
pkill -f "python.*fastapi_app_simple"

# Vérifier qu'aucun processus n'utilise le port
lsof -i :8000

# Redémarrer le serveur
cd src/python/api && python fastapi_app_simple.py &
```

### 2. Erreur python-multipart
**Symptôme :**
```
ERROR:fastapi:Form data requires "python-multipart" to be installed.
```

**Solution :**
```bash
# Installer la dépendance manquante
pip install python-multipart

# Redémarrer le serveur
pkill -f fastapi_app_simple
cd src/python/api && python fastapi_app_simple.py &
```

### 3. Erreur de clustering
**Symptôme :**
```
ValueError: n_samples=3 should be >= n_clusters=4.
```

**Solution :**
✅ **DÉJÀ CORRIGÉ** dans `advanced_metagame_analyzer.py`
Le clustering s'adapte automatiquement au nombre d'archétypes disponibles.

Si le problème persiste :
```bash
# Vérifier les données
head real_data/standard_tournaments.json

# Redémarrer avec données propres
rm -rf analysis_output/*
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis
```

### 4. Erreur de répertoire
**Symptôme :**
```
FileNotFoundError: [Errno 2] No such file or directory: 'advanced_metagame_analyzer.py'
```

**Solution :**
```bash
# Vérifier le répertoire de travail
pwd

# Doit être dans le répertoire racine du projet
cd /Volumes/DataDisk/_Projects/Manalytics

# Vérifier la présence du fichier
ls -la advanced_metagame_analyzer.py

# Redémarrer le serveur
cd src/python/api && python fastapi_app_simple.py &
```

### 5. Données manquantes
**Symptôme :**
```
FileNotFoundError: real_data/standard_tournaments.json not found
```

**Solution :**
```bash
# Vérifier les fichiers de données
ls -la real_data/

# Vérifier la taille des fichiers (doivent être > 100KB)
du -h real_data/*.json

# Si les fichiers sont corrompus ou manquants
# Contacter l'équipe pour restaurer les données
```

### 6. Erreur de timeout
**Symptôme :**
```
TimeoutError: Analysis took too long to complete
```

**Solution :**
```bash
# Vérifier l'utilisation des ressources
top | grep python

# Redémarrer avec moins de données
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-06-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis
```

### 7. Interface web ne se charge pas
**Symptôme :**
Page blanche ou erreur 500 sur `/web`

**Solution :**
```bash
# Vérifier le statut du serveur
curl http://localhost:8000/health

# Vérifier les logs
tail -f /var/log/manalytics/server.log

# Redémarrer le serveur
pkill -f fastapi_app_simple
cd src/python/api && python fastapi_app_simple.py &

# Tester l'interface
curl -I http://localhost:8000/web
```

## 🔍 Diagnostic système

### Vérifications de base
```bash
# 1. Statut du serveur
curl -s http://localhost:8000/health

# 2. Processus en cours
ps aux | grep fastapi_app_simple

# 3. Utilisation du port
lsof -i :8000

# 4. Espace disque
df -h

# 5. Mémoire disponible
free -h
```

### Logs et monitoring
```bash
# Logs du serveur (si configurés)
tail -f /var/log/manalytics/server.log

# Logs Python (sortie console)
ps aux | grep fastapi_app_simple

# Surveiller les ressources
top -p $(pgrep -f fastapi_app_simple)
```

## 🧪 Tests de validation

### Test complet du système
```bash
#!/bin/bash
echo "🔍 Test complet du système Manalytics"

# 1. Test de santé
echo "1. Test de santé..."
health_response=$(curl -s http://localhost:8000/health)
if [[ $health_response == *"healthy"* ]]; then
    echo "✅ Serveur en bonne santé"
else
    echo "❌ Serveur non disponible"
    exit 1
fi

# 2. Test de l'interface web
echo "2. Test de l'interface web..."
web_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/web)
if [[ $web_response == "200" ]]; then
    echo "✅ Interface web accessible"
else
    echo "❌ Interface web non accessible"
fi

# 3. Test du générateur d'analyses
echo "3. Test du générateur d'analyses..."
analysis_response=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis)

if [[ $analysis_response == *"Analyse générée avec succès"* ]]; then
    echo "✅ Générateur d'analyses fonctionnel"
else
    echo "❌ Erreur dans le générateur d'analyses"
    echo "Réponse: $analysis_response"
fi

# 4. Vérification des fichiers générés
echo "4. Vérification des fichiers générés..."
if [[ -f "analysis_output/complete_report.json" ]]; then
    echo "✅ Rapport JSON généré"
else
    echo "❌ Rapport JSON manquant"
fi

if [[ -f "analysis_output/dashboard.html" ]]; then
    echo "✅ Dashboard HTML généré"
else
    echo "❌ Dashboard HTML manquant"
fi

if [[ -d "analysis_output/visualizations" ]]; then
    viz_count=$(ls analysis_output/visualizations/*.png 2>/dev/null | wc -l)
    if [[ $viz_count -ge 4 ]]; then
        echo "✅ Visualisations générées ($viz_count fichiers)"
    else
        echo "❌ Visualisations incomplètes ($viz_count/4 fichiers)"
    fi
else
    echo "❌ Répertoire visualisations manquant"
fi

echo "🎉 Test terminé"
```

## 🔄 Procédures de récupération

### Récupération rapide
```bash
#!/bin/bash
echo "🚀 Récupération rapide du système"

# Arrêter tous les processus
pkill -f fastapi_app_simple

# Nettoyer les fichiers temporaires
rm -rf __pycache__/ src/__pycache__/

# Vérifier les dépendances
pip install python-multipart

# Redémarrer le serveur
cd src/python/api && python fastapi_app_simple.py &

# Attendre le démarrage
sleep 5

# Tester
curl -s http://localhost:8000/health
```

### Récupération complète
```bash
#!/bin/bash
echo "🔧 Récupération complète du système"

# 1. Arrêter tous les processus
pkill -f python

# 2. Nettoyer complètement
rm -rf __pycache__/ src/__pycache__/
rm -rf analysis_output/*

# 3. Vérifier l'environnement
source venv/bin/activate

# 4. Réinstaller les dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install python-multipart

# 5. Vérifier les données
ls -la real_data/
du -h real_data/*.json

# 6. Redémarrer
cd src/python/api && python fastapi_app_simple.py &

# 7. Test complet
sleep 10
curl -s http://localhost:8000/health
```

## 📊 Métriques de performance

### Temps de réponse normaux
- **Health check :** < 100ms
- **Interface web :** < 500ms
- **Génération d'analyse :** 30-60 secondes
- **Visualisations :** 10-15 secondes

### Utilisation des ressources
- **RAM :** 200-500 MB pendant l'analyse
- **CPU :** 50-80% pendant l'analyse
- **Disque :** 10-20 MB par analyse

## 🆘 Escalade des problèmes

### Niveau 1 : Redémarrage simple
```bash
pkill -f fastapi_app_simple
cd src/python/api && python fastapi_app_simple.py &
```

### Niveau 2 : Nettoyage et redémarrage
```bash
pkill -f fastapi_app_simple
rm -rf __pycache__/ analysis_output/*
pip install python-multipart
cd src/python/api && python fastapi_app_simple.py &
```

### Niveau 3 : Récupération complète
Utiliser le script de récupération complète ci-dessus

### Niveau 4 : Contact équipe
Si les niveaux 1-3 échouent, contacter l'équipe avec :
- Logs d'erreur complets
- Sortie de `curl http://localhost:8000/health`
- Sortie de `ps aux | grep python`
- Espace disque disponible

## 📞 Contacts d'urgence

- **Équipe de développement :** [À compléter]
- **Administrateur système :** [À compléter]
- **Documentation :** HANDOFF_DOCUMENTATION.md

---
*Guide de dépannage créé le 12 juillet 2025* 