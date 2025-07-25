# 📚 Guide : Différence entre les Scrapers MTGO

## 🚨 Problème Initial

> "MTGO : Nous avons seulement les métadonnées (pas les decklists)"

Ce problème vient du fait qu'il existe **deux scrapers MTGO différents** dans le projet, et le mauvais était utilisé.

## 📁 Les Deux Scrapers

### 1. ❌ **Scraper Basique** : `scrape_mtgo_standalone.py`
- **Ce qu'il fait** : Récupère UNIQUEMENT les métadonnées des tournois
- **Données récupérées** :
  - Nom du tournoi
  - Date
  - URL
  - Format
  - ID du tournoi
- **Problème** : Ne va PAS chercher les decklists sur chaque page de tournoi
- **Résultat** : Fichiers JSON de ~500 bytes sans cartes

Exemple de sortie :
```json
{
  "source": "mtgo",
  "format": "standard",
  "name": "Standard Challenge 32",
  "date": "2025-07-25",
  "url": "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-2512804868",
  "tournament_id": "standard-challenge-32-2025-07-2512804868",
  "scraped_at": "2025-07-25T11:38:42.371767"
}
```

### 2. ✅ **Scraper Amélioré** : `scrapers/mtgo_scraper_enhanced.py`
- **Ce qu'il fait** : Récupère les métadonnées ET les decklists complètes
- **Données récupérées** :
  - Toutes les métadonnées ci-dessus
  - **+ Decklists complètes** (mainboard + sideboard)
  - **+ Standings** (classements)
  - **+ Métriques** (couleurs, types de cartes)
  - **+ Analyse du métagame**
- **Comment** : Va chercher chaque page de tournoi et parse le JSON interne
- **Résultat** : Fichiers JSON de 20-100KB avec toutes les cartes

Exemple de sortie :
```json
{
  "source": "mtgo",
  "format": "standard",
  "name": "Standard Challenge 32",
  "date": "2025-07-25",
  "url": "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-2512804868",
  "tournament_id": "standard-challenge-32-2025-07-2512804868",
  "scraped_at": "2025-07-25T10:11:57.273000+00:00",
  "total_players": 32,
  "decks": [
    {
      "player": "slaxx",
      "result": "7-1",
      "mainboard": [
        {"count": 2, "card_name": "Agatha's Soul Cauldron"},
        {"count": 4, "card_name": "Dragon Sniper"},
        // ... toutes les cartes
      ],
      "sideboard": [
        {"count": 3, "card_name": "Duress"},
        // ... toutes les cartes
      ],
      "metrics": {
        "total_cards": 60,
        "unique_cards": 23,
        "color_identity": ["B", "G"],
        "card_types": {"Land": 20, "Creature": 25, ...}
      }
    },
    // ... 31 autres decks
  ],
  "standings": [...],
  "metagame_breakdown": {...}
}
```

## 🎯 Solution : Utiliser le Bon Scraper

### Script Créé : `scrape_mtgo_with_decklists.py`
Ce script utilise le scraper amélioré pour récupérer les decklists complètes.

```python
from scrapers.mtgo_scraper_enhanced import MTGOEnhancedScraper

# Utilise le scraper amélioré
scraper = MTGOEnhancedScraper()
results = scraper.scrape_tournaments(
    start_date=start_date,
    end_date=end_date,
    format_filter="standard"
)
```

## 📊 Résultats de Test

- **17 tournois récupérés** en 2 minutes 30 secondes
- **334 decklists complètes** avec toutes les cartes
- Fichiers de 20-100KB chacun (vs 500 bytes sans decklists)
- Inclut standings, métriques et analyse du métagame

## 🚀 Comment Utiliser

### Pour récupérer des tournois MTGO avec decklists :
```bash
# Utiliser le nouveau script
python3 scrape_mtgo_with_decklists.py

# OU utiliser directement le scraper amélioré
python3 -c "
from scrapers.mtgo_scraper_enhanced import MTGOEnhancedScraper
from datetime import datetime, timedelta, timezone

scraper = MTGOEnhancedScraper()
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=7)

results = scraper.scrape_tournaments(
    start_date=start_date,
    end_date=end_date,
    format_filter='standard'
)
print(f'Récupéré {len(results)} tournois')
"
```

### ⚠️ Ne PAS utiliser :
```bash
# ❌ Ceci ne récupère QUE les métadonnées
python3 scrape_mtgo_standalone.py
```

## 🔍 Comment Vérifier

Pour vérifier si un fichier contient des decklists :
```bash
# Si le fichier fait moins de 1KB = pas de decklists
ls -lh data/raw/mtgo/standard/*.json

# Vérifier le contenu
jq '.decks[0]' fichier.json
# Si "decks" n'existe pas = pas de decklists
```

## 📝 Résumé

- **Problème** : Le scraper basique ne récupérait que les métadonnées
- **Solution** : Utiliser le scraper amélioré (`mtgo_scraper_enhanced.py`)
- **Résultat** : Decklists complètes avec mainboard, sideboard, standings et métriques
- **Script prêt** : `scrape_mtgo_with_decklists.py` fait tout automatiquement

Les decklists MTGO sont bien disponibles et accessibles, il suffit d'utiliser le bon scraper !