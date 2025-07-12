# 📚 RÉFÉRENCE API - MANALYTICS

## 🌐 URL de base
```
http://localhost:8000
```

## 📋 Endpoints disponibles

### 1. Health Check
**Endpoint :** `GET /health`
**Description :** Vérification du statut du serveur
**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-12T18:09:20.281406",
  "data_status": "loaded",
  "total_decks": 123
}
```

### 2. Interface Web
**Endpoint :** `GET /web`
**Description :** Interface utilisateur complète
**Réponse :** Page HTML avec :
- Timeline chronologique Magic
- Générateur d'analyses interactif
- 4 cartes de fonctionnalités
- Design responsive

### 3. Générateur d'analyses (PRINCIPAL)
**Endpoint :** `POST /generate-analysis`
**Description :** Génère une analyse complète de métagame
**Content-Type :** `application/json`

**Paramètres :**
```json
{
  "format": "Standard",           // Required: Standard, Modern, Pioneer, Legacy, Vintage, Pauper
  "start_date": "2025-01-01",    // Required: YYYY-MM-DD
  "end_date": "2025-07-12"       // Required: YYYY-MM-DD
}
```

**Réponse succès (200) :**
```json
{
  "message": "Analyse générée avec succès",
  "command": "python advanced_metagame_analyzer.py --data real_data/standard_tournaments.json --output analysis_output",
  "stdout": "🚀 Lancement de l'analyse complète\n============================================================\n📊 Chargement des données depuis real_data/standard_tournaments.json\n✅ Données chargées: 1383 decks de 20 tournois\n\n1️⃣ Calcul des performances par archétype\n📊 Calcul des performances par archétype\n✅ Performances calculées pour 3 archétypes\n\n2️⃣ Calcul de la matrice de matchups\n🥊 Calcul de la matrice de matchups\n✅ Matrice de matchups calculée: 3x3\n\n3️⃣ Analyse des tendances temporelles\n📈 Calcul des tendances temporelles\n✅ Tendances calculées pour 3 archétypes\n\n4️⃣ Analyses statistiques avancées\n🔬 Analyses statistiques avancées\n✅ Analyses statistiques terminées\n\n5️⃣ Création des visualisations\n🎨 Création des visualisations complètes\n✅ 4 visualisations créées dans analysis_output/visualizations/\n\n6️⃣ Génération du dashboard interactif\n🌐 Création du dashboard interactif\n✅ Dashboard interactif créé: analysis_output/dashboard.html\n\n7️⃣ Génération du rapport final\n📋 Génération du rapport complet\n✅ Rapport complet généré: analysis_output/complete_report.json\n\n============================================================\n🎉 ANALYSE COMPLÈTE TERMINÉE\n============================================================\n📁 Dossier de sortie: analysis_output\n📊 Rapport JSON: analysis_output/complete_report.json\n🌐 Dashboard interactif: analysis_output/dashboard.html\n🎨 Visualisations: 4 fichiers créés\n📈 Archétypes analysés: 3\n🏆 Tournois analysés: 20\n\n✅ Analyse terminée avec succès!\n📁 Consultez les résultats dans: analysis_output\n",
  "stderr": ""
}
```

**Erreurs possibles :**
- `400` : Paramètres manquants ou invalides
- `500` : Erreur lors de l'exécution de l'analyse

### 4. Données métagame
**Endpoint :** `GET /metagame`
**Description :** Récupère les données de métagame
**Paramètres optionnels :**
- `format` : Format de jeu (Standard, Modern, etc.)
- `start_date` : Date de début (YYYY-MM-DD)
- `end_date` : Date de fin (YYYY-MM-DD)

**Exemple :**
```bash
GET /metagame?format=standard&start_date=2025-01-01&end_date=2025-07-12
```

### 5. Informations sur les données
**Endpoint :** `GET /real-data`
**Description :** Informations sur les données réelles disponibles
**Réponse :**
```json
{
  "total_decks": 123,
  "total_tournaments": 3,
  "formats_available": ["Standard", "Modern", "Pioneer"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-07-12"
  }
}
```

## 🔧 Formats de données

### Formats supportés
- **Standard** : 1383 decks, 20 tournois
- **Modern** : [Données disponibles]
- **Pioneer** : [Données disponibles]
- **Legacy** : [Données disponibles]
- **Vintage** : [Données disponibles]
- **Pauper** : [Données disponibles]

### Structure des données d'entrée
```json
{
  "tournaments": [
    {
      "id": "tournament_001",
      "name": "Tournament Name",
      "date": "2025-01-15",
      "format": "Standard",
      "decks": [
        {
          "player": "Player Name",
          "archetype": "Archetype Name",
          "wins": 5,
          "losses": 2,
          "mainboard": [...],
          "sideboard": [...]
        }
      ]
    }
  ]
}
```

## 📊 Sorties générées

### Fichiers créés par `/generate-analysis`
1. **analysis_output/complete_report.json** - Rapport complet
2. **analysis_output/dashboard.html** - Dashboard interactif (4.6 MB)
3. **analysis_output/visualizations/** - 4 visualisations PNG :
   - `archetype_performance_analysis.png`
   - `matchup_matrix.png`
   - `statistical_analysis.png`
   - `temporal_trends_analysis.png`

### Structure du rapport JSON
```json
{
  "metadata": {
    "generation_time": "2025-07-12T18:10:15",
    "total_decks": 1383,
    "total_tournaments": 20,
    "archetype_count": 3
  },
  "archetype_performance": {
    "archetype_name": {
      "meta_share": 0.35,
      "overall_winrate": 0.52,
      "deck_count": 150,
      "avg_wins_per_deck": 2.1
    }
  },
  "matchup_matrix": {
    "archetype_a_vs_archetype_b": 0.65
  },
  "statistical_analysis": {
    "correlations": {...},
    "clustering": {...},
    "diversity_metrics": {...}
  }
}
```

## 🚨 Gestion d'erreurs

### Codes d'erreur HTTP
- **200** : Succès
- **400** : Requête invalide
- **404** : Endpoint non trouvé
- **500** : Erreur serveur interne

### Messages d'erreur typiques
```json
{
  "detail": "Format, start_date et end_date sont requis"
}
```

```json
{
  "detail": "Format de date invalide. Utilisez YYYY-MM-DD"
}
```

```json
{
  "detail": "Erreur lors de l'exécution de la commande: [détails]"
}
```

## 🔍 Exemples d'utilisation

### Test complet avec curl
```bash
# 1. Vérifier la santé
curl http://localhost:8000/health

# 2. Générer une analyse
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"format":"Standard","start_date":"2025-01-01","end_date":"2025-07-12"}' \
  http://localhost:8000/generate-analysis

# 3. Récupérer les données métagame
curl "http://localhost:8000/metagame?format=standard"

# 4. Accéder à l'interface web
curl http://localhost:8000/web
```

### Intégration JavaScript
```javascript
// Générer une analyse
const response = await fetch('/generate-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    format: 'Standard',
    start_date: '2025-01-01',
    end_date: '2025-07-12'
  })
});

const result = await response.json();
console.log(result.message);
```

### Intégration Python
```python
import requests

# Générer une analyse
response = requests.post(
    'http://localhost:8000/generate-analysis',
    json={
        'format': 'Standard',
        'start_date': '2025-01-01',
        'end_date': '2025-07-12'
    }
)

if response.status_code == 200:
    result = response.json()
    print(result['message'])
else:
    print(f"Erreur: {response.status_code}")
```

## 🔒 Authentification

**Statut actuel :** Aucune authentification requise
**Recommandation :** Implémenter JWT ou OAuth2 pour la production

## 📈 Limites et performances

### Limites actuelles
- **Timeout :** 5 minutes par analyse
- **Formats simultanés :** 1 analyse à la fois
- **Taille des données :** Optimisé pour <2000 decks

### Performances observées
- **Analyse Standard :** ~30 secondes pour 1383 decks
- **Génération visualisations :** ~10 secondes
- **Dashboard interactif :** ~5 secondes

## 🔄 Versioning

**Version actuelle :** 1.0 (Stable)
**Compatibilité :** Rétrocompatible
**Changelog :** Voir CHANGELOG.md

---
*Documentation API créée le 12 juillet 2025* 