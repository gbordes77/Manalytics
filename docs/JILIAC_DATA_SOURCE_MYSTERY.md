Jil# 🔍 LE MYSTÈRE DES DONNÉES DE MATCHUPS DE JILIAC

> **Investigation complète** : D'où viennent exactement les données de matchups utilisées par Jiliac ?

## 🎯 CE QUE NOUS SAVONS

### 1. Le code R EXIGE des matchups pré-calculés

```r
# Dans 01-Tournament_Data_Import.R
recalculate_wins_losses = function(df) {
  for (i in 1:nrow(df)) {
    if (!is.null(df$Matchups[[i]])) {  # <-- Les Matchups DOIVENT déjà exister !
      matchups = df$Matchups[[i]]
      df$Wins[i] = sum(matchups$Wins == 2)
      df$Losses[i] = sum(matchups$Losses == 2)
    }
  }
}
```

### 2. Structure JSON attendue

```json
{
  "Tournament": "Standard Challenge 64",
  "Player": "rollo1993",
  "Archetype": {
    "Archetype": "Azorius Control",
    "Color": "WU"
  },
  "Mainboard": [...],
  "Sideboard": [...],
  "Wins": 6,
  "Losses": 1,
  "Matchups": [
    {
      "OpponentArchetype": "Dimir Midrange",
      "Wins": 2,
      "Losses": 0
    },
    {
      "OpponentArchetype": "Mono Red Aggro",
      "Wins": 2,
      "Losses": 1
    }
  ]
}
```

### 3. Sources examinées

#### ❌ MTGODecklistCache
- Contient : Decklists uniquement
- Ne contient PAS : Matchups détaillés

#### ❌ MTGOArchetypeParser  
- Détecte les archétypes
- Ne génère PAS les matchups

#### ❌ MTGO-listener (nos données)
- Contient : Rounds et résultats (Player1 vs Player2 : 2-0)
- Ne contient PAS : Archétypes des adversaires

#### ❌ MTGO-Tracker
- Outil d'analyse personnel de logs
- Pas le bon format pour R-Meta-Analysis

---

## 🤔 HYPOTHÈSES

### Hypothèse 1 : Traitement personnalisé par Jiliac

Jiliac pourrait avoir un script qui :
1. Prend les decklists de MTGODecklistCache
2. Prend les rounds du listener MTGO
3. Applique MTGOArchetypeParser pour détecter les archétypes
4. Combine tout pour créer les matchups avec archétypes
5. Génère le JSON enrichi pour R

### Hypothèse 2 : Source de données différente

Il existe peut-être une autre source qui fournit directement :
- Les résultats de tournois avec matchups détaillés
- Les archétypes déjà identifiés
- Format : Melee.gg API complète ? MTGO API privée ?

### Hypothèse 3 : Pipeline communautaire non documenté

Un outil ou script partagé sur le Discord mais pas sur GitHub qui fait la fusion des données.

---

## 📊 INDICES DANS LES VISUALISATIONS

Les graphiques de Jiliac montrent :
- **143 matches** Izzet Cauldron vs Dimir Midrange
- Des données très détaillées par matchup
- Exactement 15 archétypes (seuil 1.2%)

Cela suggère une base de données COMPLÈTE avec tous les matchups round par round.

---

## 🔴 PROBLÈME POUR NOUS

Sans comprendre exactement comment Jiliac obtient ses données de matchups :
1. Nous ne pouvons pas reproduire ses résultats exacts
2. Nos pourcentages seront différents (29% vs 20.4% pour Izzet Cauldron)
3. Nos matrices de matchups seront incomplètes

---

## 💡 SOLUTIONS POSSIBLES

### Option 1 : Reconstruire les matchups nous-mêmes
```python
def build_matchups_from_listener_and_scrapers():
    # 1. Pour chaque tournoi
    for tournament in tournaments:
        # 2. Matcher listener rounds avec scraped decklists
        rounds = listener_data[tournament.id]
        decklists = scraper_data[tournament.id]
        
        # 3. Pour chaque match
        for match in rounds:
            player1_deck = find_deck(decklists, match.player1)
            player2_deck = find_deck(decklists, match.player2)
            
            # 4. Détecter les archétypes
            player1_archetype = detect_archetype(player1_deck)
            player2_archetype = detect_archetype(player2_deck)
            
            # 5. Enregistrer le matchup
            add_matchup(player1, player2_archetype, match.result)
```

### Option 2 : Demander à Jiliac directement

Sur le Discord ou GitHub, demander :
- D'où viennent exactement les données de matchups ?
- Existe-t-il un script de préparation des données ?
- Comment sont générés les JSON d'entrée pour R ?

### Option 3 : Analyser plus de code

- Chercher dans les autres repos du pipeline communautaire
- Regarder les scripts Python dans R-Meta-Analysis
- Explorer le Discord pour des indices

---

## 📌 CONCLUSION

**Le mystère reste entier** : Nous n'avons pas trouvé la source exacte des données de matchups de Jiliac.

**Ce qui est certain** :
- R-Meta-Analysis CONSOMME des données avec matchups pré-calculés
- Ces données ne viennent NI de MTGODecklistCache NI de MTGOArchetypeParser seuls
- Il existe une étape de traitement/fusion que nous n'avons pas identifiée

**Prochaine étape critique** : Soit reconstruire cette logique, soit obtenir plus d'informations sur le pipeline exact.