# 📚 Guide : Récupération des Decklists Melee

## 🎯 Vue d'ensemble

Ce guide explique comment récupérer les decklists complètes depuis Melee.gg, qui était initialement un problème car les fichiers ne contenaient que les métadonnées.

## ❌ Problème Initial

Les fichiers Melee existants ne contiennent **PAS les decklists** :
```json
{
  "DecklistId": "d8c294fc-a235-4a8e-970c-b320013ae20c",
  "PlayerName": "Noe Offman",
  "DeckName": "Izzet Otters",
  "Rank": 5,
  "Wins": 3,
  "IsValid": true
}
```

Pas de mainboard, pas de sideboard, juste les métadonnées !

## ✅ Solution : Les Decklists sont dans les Records !

La découverte clé : **Les decklists sont DÉJÀ incluses** dans la réponse de l'API de recherche, dans le champ `Records` !

### Structure des Records
```json
"Records": [
  {
    "l": "opt",           // slug de la carte
    "n": "Opt",           // nom de la carte
    "s": null,            // set (optionnel)
    "q": 4,               // quantité
    "c": 0,               // 0 = mainboard, 99 = sideboard
    "t": "Instant"        // type de carte
  },
  ...
]
```

### Comment ça marche

1. **Recherche des tournois** : `client.search_tournaments()` retourne TOUT
2. **Parser les Records** : 
   - `c = 0` → Carte du mainboard
   - `c = 99` → Carte du sideboard
3. **Pas besoin de `get_deck()`** : Tout est déjà là !

## 🚀 Script : `parse_melee_records.py`

Ce script récupère les tournois Melee avec les decklists complètes :

```python
def parse_decklist_from_records(records):
    """Parse les Records pour extraire mainboard et sideboard"""
    mainboard = []
    sideboard = []
    
    for card in records:
        # c = 0 pour mainboard, c = 99 pour sideboard
        is_sideboard = card.get('c', 0) == 99
        
        card_entry = {
            'Count': card.get('q', 0),
            'CardName': card.get('n', '')
        }
        
        if is_sideboard:
            sideboard.append(card_entry)
        else:
            mainboard.append(card_entry)
    
    return mainboard, sideboard
```

## 📊 Résultats

### Test du 25/07/2025
- **Période** : 7 derniers jours
- **Format** : Standard
- **Résultats** :
  - 918 entrées analysées
  - 37 tournois trouvés
  - 4 tournois Standard
  - 36 decklists complètes récupérées

### Exemple de sortie
```json
{
  "TournamentId": 342876,
  "TournamentName": "F2F Tour Toronto - Standard SQ",
  "TournamentStartDate": "2025-07-20T14:00:00Z",
  "FormatDescription": "Standard",
  "OrganizationName": "F2FTour.com",
  "TotalPlayers": 9,
  "Decks": [
    {
      "DeckId": "d8c294fc-a235-4a8e-970c-b320013ae20c",
      "PlayerName": "Noe Offman",
      "DeckName": "Izzet Otters",
      "Rank": 5,
      "Wins": 3,
      "Losses": 2,
      "Mainboard": [
        {"Count": 4, "CardName": "Opt"},
        {"Count": 4, "CardName": "Stormchaser's Talent"},
        // ... toutes les cartes
      ],
      "Sideboard": [
        {"Count": 2, "CardName": "Negate"},
        // ... toutes les cartes
      ]
    }
  ]
}
```

## 🔧 Utilisation

```bash
# Récupérer les tournois Melee avec decklists
python3 parse_melee_records.py

# Les fichiers sont sauvés dans :
data/raw/melee/standard_complete/
```

## 💡 Points Techniques Importants

1. **Pas de requêtes supplémentaires** : Tout est dans la première réponse
2. **Performance** : Beaucoup plus rapide (pas de requête par deck)
3. **Rate limiting** : Minimal car une seule API utilisée
4. **Pagination** : L'API retourne 50 entrées par page
5. **Authentification** : Toujours nécessaire (cookies valides 21 jours)

## 🐛 Problèmes Résolus

1. ❌ **Ancien problème** : `get_deck()` était commenté et ne fonctionnait pas
2. ✅ **Solution** : Utiliser les Records déjà présents
3. ❌ **Ancien problème** : Trop de requêtes (une par deck)
4. ✅ **Solution** : Une seule requête de recherche suffit

## 📈 Améliorations Possibles

1. **Filtrage avancé** : Par organisation, date précise, etc.
2. **Détection d'archétypes** : Utiliser les Attributes fournis
3. **Cache local** : Éviter de re-télécharger les mêmes tournois
4. **Export multiple** : CSV, Arena format, etc.

## 🎉 Conclusion

Les decklists Melee sont **100% récupérables** ! Il suffisait de comprendre que :
- Les Records contiennent déjà toutes les cartes
- Le champ `c` indique mainboard (0) ou sideboard (99)
- Pas besoin de requêtes supplémentaires

Le script `parse_melee_records.py` fait tout automatiquement et efficacement.