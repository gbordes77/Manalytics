# 🔧 Détails Techniques : API Round Standings Melee

## 🎯 Problème Initial

Lors de l'implémentation initiale, plusieurs erreurs ont été rencontrées :

1. **Erreur 500** : Mauvais format de round ID
2. **Erreur 500** : Payload incorrect
3. **Pas de données** : Mauvais endpoint

## 📊 Solution Technique

### 1. Découverte des Round IDs

Les round IDs ne sont PAS séquentiels (1, 2, 3) mais des identifiants uniques :

```python
# ❌ INCORRECT
round_ids = ["1", "2", "3", "4"]

# ✅ CORRECT
round_ids = ["1060187", "1060188", "1060189", "1060190"]
```

### 2. Extraction depuis HTML

```python
def get_tournament_round_ids(self, tournament_id: int) -> List[str]:
    """Récupérer les IDs des rounds depuis la page HTML du tournoi"""
    
    # Charger la page du tournoi
    url = f"https://melee.gg/Tournament/Details/{tournament_id}"
    response = self.session.get(url)
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Sélecteur CSS spécifique pour les boutons de rounds
    round_nodes = soup.select('button.btn.btn-gray.round-selector[data-is-completed="True"]')
    
    # Extraire les data-id
    round_ids = [node.get('data-id') for node in round_nodes if node.get('data-id')]
    
    return round_ids
```

### 3. Format du Payload API

Le payload DOIT être une string URL-encoded, PAS un dictionnaire :

```python
# ❌ INCORRECT - Dict Python
payload = {
    "draw": 1,
    "columns[0][data]": "Rank",
    "start": 0,
    "roundId": round_id
}

# ✅ CORRECT - String URL-encoded
payload_str = "draw=1&columns%5B0%5D%5Bdata%5D=Rank&columns%5B0%5D%5Bname%5D=Rank..."
```

### 4. Headers Requis

```python
headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}
```

## 📝 Code Complet de la Méthode

```python
def get_round_standings(self, tournament_id: int, round_id: str) -> Dict:
    """Récupérer les standings d'un round spécifique"""
    
    # Utiliser le template depuis les constants
    payload_template = MtgMeleeConstants.ROUND_PAGE_PARAMETERS
    
    # Remplacer les placeholders
    payload_str = payload_template.replace("{start}", "0").replace("{roundId}", round_id)
    
    try:
        response = self.session.post(
            MtgMeleeConstants.ROUND_PAGE,
            data=payload_str,  # String, pas dict!
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraire les standings
            standings = []
            for entry in data.get('data', []):
                standings.append({
                    'Rank': entry.get('Rank'),
                    'Player': entry.get('Team', {}).get('Players', [{}])[0].get('DisplayName'),
                    'MatchRecord': entry.get('MatchRecord'),
                    'GameRecord': entry.get('GameRecord'),
                    'Points': entry.get('Points')
                })
            
            return {
                'round': int(round_id) if round_id.isdigit() else 1,
                'round_id': round_id,
                'standings': standings
            }
```

## 🔍 Format de la Réponse API

```json
{
    "draw": 1,
    "recordsTotal": 16,
    "recordsFiltered": 16,
    "data": [
        {
            "Rank": 1,
            "Team": {
                "Players": [
                    {
                        "DisplayName": "Clément Pintout",
                        "DeckName": "Izzet Combo"
                    }
                ]
            },
            "MatchRecord": "1-0-0",
            "GameRecord": "2-1-0",
            "Points": 3
        }
    ]
}
```

## 🚨 Points Critiques

1. **Authentification requise** : Doit être connecté à Melee
2. **Round IDs depuis HTML** : Pas d'API directe pour les obtenir
3. **Format DataTables** : Utilise le standard jQuery DataTables
4. **URL encoding** : Les caractères `[` et `]` deviennent `%5B` et `%5D`

## 📋 Checklist de Debug

Si l'API retourne une erreur :

- [ ] Vérifier l'authentification (`ensure_authenticated()`)
- [ ] Confirmer le round ID est correct (depuis HTML)
- [ ] Payload est une string URL-encoded
- [ ] Headers incluent `X-Requested-With: XMLHttpRequest`
- [ ] Content-Type est `application/x-www-form-urlencoded`

## 🔧 Constants Utilisées

Depuis `scrapers/models/Melee_model.py` :

```python
class MtgMeleeConstants:
    ROUND_PAGE = "https://melee.gg/Round/GetRoundStandings"
    ROUND_PAGE_PARAMETERS = "draw=1&columns%5B0%5D%5Bdata%5D=Rank..."
```

Cette documentation technique servira de référence pour toute personne devant travailler avec l'API Round Standings de Melee à l'avenir.