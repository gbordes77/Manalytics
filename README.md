# 🎯 Manalytics - Analyseur de Métagame Magic: The Gathering

[![Status](https://img.shields.io/badge/Status-Fonctionnel-brightgreen)](http://localhost:8000/health)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![Données](https://img.shields.io/badge/Données-Réelles-orange)](./real_data)

## 🚀 Démarrage rapide

### Méthode recommandée (Script automatique)
```bash
# Démarrer le serveur
./start_server.sh

# Accéder à l'interface web
open http://localhost:8000/web

# Arrêter le serveur
./stop_server.sh
```

### Méthode manuelle (Testée et validée)
```bash
# 1. Nettoyer les processus
pkill -f "python.*fastapi_app_simple"

# 2. Installer les dépendances
pip install python-multipart

# 3. Démarrer le serveur
cd src/python/api && python fastapi_app_simple.py &

# 4. Tester
curl http://localhost:8000/health
```

## 📊 Données réelles confirmées

- **1383 decks** analysés
- **20 tournois** réels
- **6 formats** supportés (Standard, Modern, Pioneer, Legacy, Vintage, Pauper)
- **Aucune donnée factice** - Politique stricte de données réelles

## 🎨 Interface utilisateur

### Fonctionnalités principales
- **Timeline chronologique** Magic avec historique des sets et bans
- **Générateur d'analyses** interactif avec sélection de format et dates
- **4 cartes de fonctionnalités** en disposition horizontale
- **Design moderne** avec gradients et animations

### Captures d'écran
L'interface inclut :
- Sidebar avec timeline Magic interactive
- Formulaire de génération avec calendriers
- Affichage des résultats en temps réel
- Design responsive pour mobile et desktop

## 🔧 Architecture technique

### Backend
- **FastAPI** - API REST moderne et rapide
- **Python 3.13** - Dernière version stable
- **Pandas/NumPy** - Traitement des données
- **Scikit-learn** - Clustering et analyse statistique
- **Matplotlib/Seaborn** - Visualisations

### Frontend
- **HTML5/CSS3/JavaScript** - Interface web native
- **Design responsive** - Compatible mobile/desktop
- **Animations CSS** - Expérience utilisateur fluide

### Données
- **Format JSON** - Stockage des tournois
- **Archétypes identifiés** - Classification automatique
- **Métriques calculées** - Winrates, meta shares, tendances

## 📈 Analyses générées

### Visualisations (PNG haute résolution)
1. **Performance des archétypes** - Meta shares et winrates
2. **Matrice de matchups** - Heatmap des confrontations
3. **Analyses statistiques** - Corrélations et clustering
4. **Tendances temporelles** - Évolution du métagame

### Rapports
- **Dashboard interactif** (HTML, 4.6 MB)
- **Rapport complet** (JSON structuré)
- **Métriques détaillées** par archétype

## 🛠️ API Reference

### Endpoints principaux
```bash
# Santé du serveur
GET /health

# Interface web
GET /web

# Générer une analyse
POST /generate-analysis
Content-Type: application/json
{
  "format": "Standard",
  "start_date": "2025-01-01",
  "end_date": "2025-07-12"
}

# Données métagame
GET /metagame?format=standard

# Informations sur les données
GET /real-data
```

## 🔍 Résolution de problèmes

### Problèmes courants
1. **Port 8000 occupé** → `pkill -f "python.*fastapi_app_simple"`
2. **Erreur multipart** → `pip install python-multipart`
3. **Clustering insuffisant** → ✅ Déjà corrigé (adaptation automatique)
4. **Répertoire incorrect** → Vérifier être dans le répertoire racine

### Scripts de diagnostic
```bash
# Test complet du système
./test_system.sh

# Logs du serveur
tail -f logs/server.log

# Statut des processus
ps aux | grep fastapi_app_simple
```

## 📋 État fonctionnel confirmé

### ✅ Dernière validation (12 juillet 2025, 18:10)
- **Serveur** : ✅ Fonctionnel
- **Interface web** : ✅ Accessible
- **Générateur** : ✅ Opérationnel
- **Analyses** : ✅ 1383 decks traités
- **Visualisations** : ✅ 4 fichiers générés
- **Dashboard** : ✅ 4.6 MB créé

### Commande de test validée
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis
```

## 📁 Structure du projet

```
Manalytics/
├── src/python/api/
│   └── fastapi_app_simple.py      # ✅ Serveur principal
├── advanced_metagame_analyzer.py  # ✅ Moteur d'analyse
├── real_data/                     # ✅ Données réelles
├── analysis_output/               # ✅ Résultats
├── start_server.sh               # ✅ Script de démarrage
├── stop_server.sh                # ✅ Script d'arrêt
├── requirements.txt              # ✅ Dépendances
└── docs/                         # ✅ Documentation complète
```

## 📚 Documentation complète

- **[HANDOFF_DOCUMENTATION.md](HANDOFF_DOCUMENTATION.md)** - Documentation complète de handoff
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guide de déploiement
- **[API_REFERENCE.md](API_REFERENCE.md)** - Référence API complète
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Guide de dépannage

## 🎯 Prochaines étapes

1. **Stabilisation** - Monitoring et logs avancés
2. **Sécurité** - Authentification et HTTPS
3. **Performance** - Cache et optimisations
4. **Déploiement** - Containerisation Docker
5. **Tests** - Suite de tests automatisés

## 🤝 Contribution

Ce projet utilise **uniquement des données réelles** de tournois Magic. Aucune donnée factice n'est autorisée (politique stricte avec enforcement via pre-commit hooks).

## 📞 Support

- **Documentation** : Voir les fichiers `.md` dans le répertoire
- **Logs** : `logs/server.log`
- **Statut** : `curl http://localhost:8000/health`

## 📜 Licence

Projet interne - Tous droits réservés

---

**🎉 Manalytics est prêt à l'utilisation !**

*Dernière mise à jour : 12 juillet 2025* 