# 📚 Documentation API Melee.gg

## 🔓 Endpoints Publics (SANS Authentification)

### 1. Tournament Search
**Endpoint**: `/Tournament/SearchResults`  
**Méthode**: POST  
**Type**: API publique

**Payload DataTables**:
```javascript
{
  "draw": "1",
  "columns[0][data]": "ID",
  "columns[0][name]": "ID",
  "columns[0][searchable]": "false",
  "columns[0][orderable]": "false",
  "columns[1][data]": "Name",
  "columns[1][name]": "Name",
  "columns[1][searchable]": "true",
  "columns[1][orderable]": "true",
  "columns[2][data]": "StartDate",
  "columns[2][name]": "StartDate",
  "columns[2][searchable]": "false",
  "columns[2][orderable]": "true",
  "columns[3][data]": "Status",
  "columns[3][name]": "Status",
  "columns[3][searchable]": "true",
  "columns[3][orderable]": "true",
  "columns[4][data]": "Format",
  "columns[4][name]": "Format",
  "columns[4][searchable]": "true",
  "columns[4][orderable]": "true",
  "columns[5][data]": "OrganizationName",
  "columns[5][name]": "OrganizationName",
  "columns[5][searchable]": "true",
  "columns[5][orderable]": "true",
  "columns[6][data]": "Decklists",
  "columns[6][name]": "Decklists",
  "columns[6][searchable]": "true",
  "columns[6][orderable]": "true",
  "order[0][column]": "2",
  "order[0][dir]": "desc",
  "start": "{offset}",
  "length": "25",
  "search[value]": "",
  "search[regex]": "false",
  "startDate": "{startDate}T00:00:00.000Z",
  "endDate": "{endDate}T23:59:59.999Z"
}
```

### 2. Round Standings
**Endpoint**: `/Standing/GetRoundStandings`  
**Méthode**: POST  
**Type**: API publique

**Payload**:
```javascript
{
  "draw": "1",
  "columns[0][data]": "Rank",
  "columns[1][data]": "Player",
  "columns[2][data]": "Decklists",
  "columns[3][data]": "MatchRecord",
  "columns[4][data]": "GameRecord",
  "columns[5][data]": "Points",
  "columns[6][data]": "OpponentMatchWinPercentage",
  "columns[7][data]": "TeamGameWinPercentage",
  "columns[8][data]": "OpponentGameWinPercentage",
  "start": "{start}",
  "length": "25",
  "roundId": "{roundId}"
}
```

### 3. Decklist Details
**Endpoint**: `/Decklist/GetDecklistDetails`  
**Méthode**: GET/POST  
**Type**: API publique  
**Paramètre**: `deckId`

### 4. Decklist View (HTML)
**URL**: `/Decklist/View/{deckId}`  
**Méthode**: GET  
**Type**: Page HTML publique

## 🔐 Endpoints Nécessitant Authentification

- Tournois privés
- Données utilisateur spécifiques  
- Certains tournois premium

## ⚠️ Important : Authentification Recommandée

Même si ces endpoints semblent publics dans la documentation, **nos tests ont montré que l'authentification est souvent nécessaire** pour :

1. ⚠️ **Tournament Search** : Peut retourner des résultats vides sans auth
2. ⚠️ **Round Standings** : Peut nécessiter auth pour certains tournois
3. ⚠️ **Decklist Details** : Peut être limité sans auth
4. ✅ **Decklist View** : Page HTML généralement accessible

**Recommandation** : TOUJOURS utiliser l'authentification par cookies pour garantir l'accès aux données.

## 🚀 Stratégie d'Implémentation

### Phase 1 : Récupération des Tournois
```python
async def search_tournaments(start_date, end_date):
    payload = build_datatables_payload(start_date, end_date)
    response = await client.post("/Tournament/SearchResults", data=payload)
    return response.json()
```

### Phase 2 : Récupération des Standings
```python
async def get_round_standings(round_id):
    payload = {
        "roundId": round_id,
        "start": "0",
        "length": "100"  # Récupérer plus de résultats
    }
    response = await client.post("/Standing/GetRoundStandings", data=payload)
    return response.json()
```

### Phase 3 : Récupération des Decklists
```python
async def get_decklist_details(deck_id):
    # Option 1: API JSON
    response = await client.get(f"/Decklist/GetDecklistDetails?deckId={deck_id}")
    
    # Option 2: Parser HTML
    response = await client.get(f"/Decklist/View/{deck_id}")
    return parse_deck_html(response.text)
```

## 📊 Données Disponibles

### Tournament Search Response
- ID du tournoi
- Nom
- Date de début
- Statut
- Format
- Organisation
- Nombre de decklists

### Round Standings Response
- Rang
- Joueur
- Decklists (ID)
- Match Record (W-L-D)
- Game Record
- Points
- Tiebreakers (OMW%, GW%, OGW%)

### Decklist Details
- Mainboard complet
- Sideboard complet
- Métadonnées du deck