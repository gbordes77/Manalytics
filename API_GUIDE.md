# 📚 Guide API - Manalytics

Documentation complète de l'API REST Manalytics avec exemples pratiques.

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Endpoints publics](#endpoints-publics)
4. [Endpoints protégés](#endpoints-protégés)
5. [Modèles de données](#modèles-de-données)
6. [Exemples complets](#exemples-complets)
7. [SDK Python](#sdk-python)
8. [Limites et quotas](#limites-et-quotas)

## 🌐 Vue d'ensemble

### Base URL
```
http://localhost:8000/api
```

### Documentation interactive
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Format des réponses
- Toutes les réponses sont en JSON
- Dates au format ISO 8601
- Pagination standard sur les listes

### Codes de statut
- `200`: Succès
- `201`: Créé
- `400`: Erreur de validation
- `401`: Non authentifié
- `403`: Non autorisé
- `404`: Non trouvé
- `500`: Erreur serveur

## 🔐 Authentification

### Obtenir un token JWT

**Endpoint**: `POST /auth/token`

```bash
# Requête
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# Réponse
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Utiliser le token

Ajouter le header `Authorization: Bearer <token>` à toutes les requêtes protégées:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Informations utilisateur

**Endpoint**: `GET /auth/me`

```bash
# Réponse
{
  "username": "testuser",
  "email": "test@manalytics.com",
  "full_name": "Test User",
  "is_active": true,
  "is_admin": false
}
```

## 📖 Endpoints Publics

### 1. Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health

# Réponse
{
  "status": "healthy",
  "timestamp": "2025-07-24T09:32:43.885914"
}
```

### 2. Liste des archétypes

**Endpoint**: `GET /archetypes/`

**Paramètres**:
- `format` (string): Filtrer par format (modern, standard, etc.)
- `limit` (int): Nombre de résultats (défaut: 50)

```bash
curl "http://localhost:8000/api/archetypes/?format=modern&limit=10"

# Réponse
[
  {
    "id": 1,
    "name": "BurnRDW",
    "display_name": "Burn",
    "color_identity": "R",
    "meta_share": 12.5,
    "deck_count": 145,
    "avg_win_rate": 52.3
  },
  ...
]
```

### 3. Analyse du méta

**Endpoint**: `GET /analysis/meta/{format}`

**Paramètres**:
- `days` (int): Nombre de jours à analyser (défaut: 30)

```bash
curl "http://localhost:8000/api/analysis/meta/modern?days=7"

# Réponse
{
  "format": "modern",
  "date_from": "2025-07-17",
  "date_to": "2025-07-24",
  "total_decks": 1243,
  "total_tournaments": 47,
  "archetypes": [
    {
      "id": 1,
      "name": "BurnRDW",
      "display_name": "Burn",
      "color_identity": "R",
      "meta_share": 12.5,
      "deck_count": 155,
      "avg_win_rate": 52.3
    },
    ...
  ]
}
```

## 🔒 Endpoints Protégés

### 1. Liste des decks

**Endpoint**: `GET /decks/`

**Paramètres**:
- `page` (int): Numéro de page (défaut: 1)
- `size` (int): Taille de page (défaut: 50, max: 100)
- `format` (string): Filtrer par format
- `archetype` (string): Filtrer par archétype
- `player` (string): Recherche par nom de joueur
- `date_from` (date): Date de début
- `date_to` (date): Date de fin
- `min_wins` (int): Nombre minimum de victoires

```bash
# Obtenir un token d'abord
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -d "username=testuser&password=testpass123" | jq -r .access_token)

# Requête avec filtres
curl "http://localhost:8000/api/decks/?format=modern&archetype=Burn&page=1&size=20" \
  -H "Authorization: Bearer $TOKEN"

# Réponse
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "player": "PlayerName",
      "archetype": "BurnRDW",
      "tournament_name": "Modern League 2025-07-24",
      "tournament_date": "2025-07-24",
      "position": 1,
      "wins": 5,
      "losses": 0,
      "mainboard": [
        {"quantity": 4, "name": "Lightning Bolt"},
        {"quantity": 4, "name": "Goblin Guide"},
        ...
      ],
      "sideboard": [
        {"quantity": 3, "name": "Smash to Smithereens"},
        ...
      ]
    },
    ...
  ],
  "total": 155,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### 2. Détail d'un deck

**Endpoint**: `GET /decks/{deck_id}`

```bash
curl "http://localhost:8000/api/decks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Statistiques joueur

**Endpoint**: `GET /players/{player_name}/stats`

```bash
curl "http://localhost:8000/api/players/LSV/stats" \
  -H "Authorization: Bearer $TOKEN"

# Réponse
{
  "player_name": "LSV",
  "total_decks": 47,
  "total_wins": 203,
  "total_losses": 32,
  "win_rate": 86.4,
  "favorite_archetype": "UW Control",
  "formats_played": ["modern", "legacy", "vintage"],
  "recent_results": [...]
}
```

## 📊 Modèles de Données

### Card
```json
{
  "quantity": 4,
  "name": "Lightning Bolt"
}
```

### Decklist
```json
{
  "id": "uuid",
  "player": "string",
  "archetype": "string",
  "tournament_name": "string",
  "tournament_date": "date",
  "position": "int",
  "wins": "int",
  "losses": "int",
  "mainboard": ["Card"],
  "sideboard": ["Card"]
}
```

### Archetype
```json
{
  "id": "int",
  "name": "string",
  "display_name": "string",
  "color_identity": "string",
  "meta_share": "float",
  "deck_count": "int",
  "avg_win_rate": "float"
}
```

### PaginatedResponse
```json
{
  "items": ["T"],
  "total": "int",
  "page": "int",
  "size": "int",
  "pages": "int"
}
```

## 🚀 Exemples Complets

### Workflow complet d'analyse

```bash
#!/bin/bash
# Script: analyze_meta.sh

# Configuration
API_URL="http://localhost:8000/api"
USERNAME="testuser"
PASSWORD="testpass123"
FORMAT="modern"

# 1. Authentification
echo "🔐 Authentication..."
TOKEN=$(curl -s -X POST "$API_URL/auth/token" \
  -d "username=$USERNAME&password=$PASSWORD" | jq -r .access_token)

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

# 2. Récupérer les stats du méta
echo "📊 Fetching meta analysis..."
META=$(curl -s "$API_URL/analysis/meta/$FORMAT?days=7" \
  -H "Authorization: Bearer $TOKEN")

echo "$META" | jq '.archetypes[:5]'

# 3. Récupérer les decks du top archétype
TOP_ARCHETYPE=$(echo "$META" | jq -r '.archetypes[0].name')
echo "🏆 Top archetype: $TOP_ARCHETYPE"

DECKS=$(curl -s "$API_URL/decks/?format=$FORMAT&archetype=$TOP_ARCHETYPE&size=5" \
  -H "Authorization: Bearer $TOKEN")

echo "$DECKS" | jq '.items[].player'

# 4. Analyser un deck spécifique
DECK_ID=$(echo "$DECKS" | jq -r '.items[0].id')
DECK_DETAIL=$(curl -s "$API_URL/decks/$DECK_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "📋 Deck details:"
echo "$DECK_DETAIL" | jq '{player, wins, losses, mainboard: .mainboard[:5]}'
```

### Monitoring du méta en temps réel

```python
#!/usr/bin/env python3
# Script: meta_monitor.py

import httpx
import asyncio
import json
from datetime import datetime

API_URL = "http://localhost:8000/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

async def get_token(client):
    """Obtenir un token JWT."""
    resp = await client.post(f"{API_URL}/auth/token", data={
        "username": USERNAME,
        "password": PASSWORD
    })
    return resp.json()["access_token"]

async def monitor_meta():
    """Surveiller les changements du méta."""
    async with httpx.AsyncClient() as client:
        token = await get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        while True:
            # Récupérer les données actuelles
            resp = await client.get(
                f"{API_URL}/analysis/meta/modern?days=1",
                headers=headers
            )
            meta = resp.json()
            
            # Afficher le top 5
            print(f"\n📊 Meta Update - {datetime.now()}")
            print("-" * 50)
            for i, arch in enumerate(meta["archetypes"][:5], 1):
                print(f"{i}. {arch['display_name']}: {arch['meta_share']:.1f}% ({arch['deck_count']} decks)")
            
            # Attendre 5 minutes
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(monitor_meta())
```

## 🐍 SDK Python

### Installation

```bash
pip install httpx pydantic
```

### Client API

```python
# manalytics_client.py
import httpx
from typing import Optional, List, Dict
from datetime import date

class ManalyticsClient:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.client = httpx.Client()
        self._token = None
    
    def login(self, username: str, password: str) -> bool:
        """Authentification et stockage du token."""
        resp = self.client.post(f"{self.base_url}/auth/token", data={
            "username": username,
            "password": password
        })
        if resp.status_code == 200:
            self._token = resp.json()["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self._token}"
            return True
        return False
    
    def get_meta(self, format_name: str, days: int = 30) -> Dict:
        """Récupérer l'analyse du méta."""
        resp = self.client.get(f"{self.base_url}/analysis/meta/{format_name}", params={
            "days": days
        })
        resp.raise_for_status()
        return resp.json()
    
    def get_decks(self, **filters) -> Dict:
        """Récupérer la liste des decks avec filtres."""
        resp = self.client.get(f"{self.base_url}/decks/", params=filters)
        resp.raise_for_status()
        return resp.json()
    
    def get_deck(self, deck_id: str) -> Dict:
        """Récupérer le détail d'un deck."""
        resp = self.client.get(f"{self.base_url}/decks/{deck_id}")
        resp.raise_for_status()
        return resp.json()

# Utilisation
client = ManalyticsClient()
if client.login("testuser", "testpass123"):
    # Analyser le méta Modern
    meta = client.get_meta("modern", days=7)
    print(f"Total decks: {meta['total_decks']}")
    
    # Récupérer des decks
    decks = client.get_decks(format="modern", archetype="Burn", page=1)
    for deck in decks["items"]:
        print(f"{deck['player']}: {deck['wins']}-{deck['losses']}")
```

## 📏 Limites et Quotas

### Limites par défaut

- **Taux de requêtes**: 100 req/min par IP
- **Taille de page max**: 100 items
- **Durée du token**: 30 minutes
- **Taille max requête**: 10MB

### Headers de quota

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1627058400
```

### Gestion des erreurs

```python
async def safe_request(url: str, headers: dict) -> dict:
    """Requête avec retry automatique."""
    for attempt in range(3):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers)
                
                # Vérifier le rate limit
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                return resp.json()
                
        except httpx.HTTPError as e:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)
```

## 🔗 Webhooks (Future)

### Configuration

```json
POST /api/webhooks/
{
  "url": "https://your-server.com/webhook",
  "events": ["deck.created", "tournament.completed"],
  "format": "modern"
}
```

### Format des événements

```json
{
  "event": "deck.created",
  "timestamp": "2025-07-24T10:30:00Z",
  "data": {
    "deck_id": "550e8400-e29b-41d4-a716-446655440000",
    "player": "PlayerName",
    "archetype": "BurnRDW",
    "format": "modern"
  }
}
```

---

Pour plus de détails techniques, voir [DEVELOPMENT.md](./DEVELOPMENT.md).