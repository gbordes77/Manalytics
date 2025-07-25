# MTG Tournament Scrapers Integration

Ce document explique comment utiliser les scrapers MTGO et MTG Melee intégrés dans le projet Manalytics.

## Structure du projet

```
Manalytics/
├── scrapers/
│   ├── clients/          # Clients de scraping
│   │   ├── MTGOclient.py
│   │   └── MtgMeleeClientV2.py
│   ├── models/           # Modèles de données
│   │   ├── base_model.py
│   │   ├── Melee_model.py
│   │   └── Topdeck_model.py
│   └── tools/            # Outils communs
│       ├── tools.py
│       └── mana_trader_unmask.py
├── api_credentials/      # Identifiants (ne pas commit!)
│   └── melee_login.json
├── data/tournaments/     # Données téléchargées
│   ├── mtgo/
│   └── melee/
└── test_scrapers.py      # Script de test
```

## Installation des dépendances

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux

# Installer les dépendances
pip install -r requirements_scrapers.txt
```

## Configuration

### MTGO
Aucune configuration requise - pas d'authentification nécessaire.

### MTG Melee
Les identifiants sont déjà configurés dans `api_credentials/melee_login.json`.

## Utilisation

### Script de test
```bash
python test_scrapers.py
```

### Utilisation programmatique

```python
from datetime import datetime, timezone
from scrapers.clients.MTGOclient import TournamentList as MTGOClient
from scrapers.clients.MtgMeleeClientV2 import TournamentList as MeleeClient

# Définir la période
start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2025, 1, 31, tzinfo=timezone.utc)

# Scraper MTGO
mtgo_tournaments = MTGOClient.DL_tournaments(start_date, end_date)
print(f"Trouvé {len(mtgo_tournaments)} tournois MTGO")

# Scraper Melee
melee_tournaments = MeleeClient.DL_tournaments(start_date, end_date)
print(f"Trouvé {len(melee_tournaments)} tournois Melee")

# Obtenir les détails d'un tournoi
if mtgo_tournaments:
    loader = MTGOClient()
    details = loader.get_tournament_details(mtgo_tournaments[0])
    print(f"Decks: {len(details.decks)}")
```

## Formats supportés

- Standard
- Modern
- Pioneer
- Legacy
- Vintage
- Pauper
- Commander
- Premodern (Melee uniquement)

## Notes importantes

1. **Rate limiting**: Les scrapers incluent des mécanismes de retry automatique
2. **Cache**: MTGO re-télécharge automatiquement les leagues des 3 derniers jours
3. **Cookies Melee**: Expiration après 7 jours, renouvellement automatique
4. **Stockage**: Les tournois sont sauvegardés en JSON dans `data/tournaments/`

## Dépannage

### Erreur d'authentification Melee
- Vérifier que `api_credentials/melee_login.json` existe
- Vérifier les identifiants
- Supprimer `api_credentials/melee_cookies.json` si présent

### Pas de tournois trouvés
- Vérifier la plage de dates (Melee limite à 2020+)
- Vérifier la connexion Internet
- Essayer une plage de dates plus récente

## Exemple de données récupérées

```json
{
  "tournament": {
    "name": "Modern Challenge",
    "date": "2025-01-24",
    "format": "Modern",
    "uri": "https://www.mtgo.com/..."
  },
  "decks": [
    {
      "player": "Player1",
      "result": "1st Place",
      "mainboard": [...],
      "sideboard": [...]
    }
  ],
  "standings": [...],
  "rounds": [...]
}
```