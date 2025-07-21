# MTGOArchetypeParser C# → Python Mapping

Ce document détaille le mapping exact entre le code C# original de MTGOArchetypeParser et notre implémentation Python pour assurer une reproduction fidèle du workflow original.

## 1. Structures de Données

### Deck (C#)
```csharp
public class Deck
{
    [JsonProperty("Date")]
    public DateTime? Date { get; set; }
    [JsonProperty("Result")]
    public string Result { get; set; }
    [JsonProperty("Player")]
    public string Player { get; set; }
    [JsonProperty("AnchorUri")]
    public Uri AnchorUri { get; set; }
    [JsonProperty("Mainboard")]
    public DeckItem[] Mainboard { get; set; }
    [JsonProperty("Sideboard")]
    public DeckItem[] Sideboard { get; set; }
}
```

### DeckItem (C#)
```csharp
public class DeckItem
{
    [JsonProperty("Count")]
    public int Count { get; set; }
    [JsonProperty("CardName")]
    public string Card { get; set; }
}
```

### Python Equivalent
```python
class Deck:
    def __init__(self):
        self.date = None  # DateTime?
        self.result = ""  # string
        self.player = ""  # string
        self.anchor_uri = ""  # Uri
        self.mainboard = []  # DeckItem[]
        self.sideboard = []  # DeckItem[]

class DeckItem:
    def __init__(self):
        self.count = 0  # int
        self.card = ""  # string
```

## 2. Flux de Données

### Chargement des Tournois (C#)
```csharp
Tournament[] tournaments = TournamentLoader.GetTournamentsByDate(cacheFolder, startDate, filter);
```

### Python Equivalent
```python
tournaments = tournament_loader.get_tournaments_by_date(cache_folder, start_date, filter_func)
```

### Détection d'Archétypes (C#)
```csharp
var detectionResult = ArchetypeAnalyzer.Detect(
    deck.Mainboard.Select(i => new Card() { Name = i.Card, Count = i.Count }).ToArray(),
    deck.Sideboard.Select(i => new Card() { Name = i.Card, Count = i.Count }).ToArray(),
    format,
    0.1,
    conflictMode
);
```

### Python Equivalent
```python
detection_result = archetype_analyzer.detect(
    [Card(name=item.card, count=item.count) for item in deck.mainboard],
    [Card(name=item.card, count=item.count) for item in deck.sideboard],
    format_data,
    min_similarity=0.1,
    conflict_solving_mode=conflict_mode
)
```

## 3. Algorithme de Détection d'Archétypes

### Test des Conditions (C#)
```csharp
private static bool Test(Card[] mainboardCards, Card[] sideboardCards, ArchetypeColor color, ArchetypeSpecific archetypeData)
{
    foreach (var condition in archetypeData.Conditions)
    {
        if (condition.Cards == null || condition.Cards.Length == 0) continue; // Skips broken condition

        switch (condition.Type)
        {
            case ArchetypeConditionType.InMainboard:
                if (!mainboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            case ArchetypeConditionType.InSideboard:
                if (!sideboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            // ... autres conditions
        }
    }
    return true;
}
```

### Python Equivalent
```python
def test_conditions(mainboard_cards, sideboard_cards, color, archetype_data):
    for condition in archetype_data.conditions:
        if not condition.cards or len(condition.cards) == 0:
            continue  # Skip broken condition

        if condition.type == ArchetypeConditionType.IN_MAINBOARD:
            if not any(c.name == condition.cards[0] for c in mainboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.IN_SIDEBOARD:
            if not any(c.name == condition.cards[0] for c in sideboard_cards):
                return False
        # ... autres conditions

    return True
```

## 4. Structure de Sortie

### Record (C#)
```csharp
tournamentRecords.Add(new Record()
{
    TournamentFile = Path.GetFileNameWithoutExtension(tournament.File),
    Tournament = tournament.Information.Name,
    Meta = metaID,
    Week = weekID,
    Date = tournament.Decks.First().Date.Value,
    Result = tournament.Decks[i].Result,
    Points = points,
    Wins = wins,
    Losses = losses,
    Draws = draws,
    Player = tournament.Decks[i].Player,
    AnchorUri = tournament.Decks[i].AnchorUri,
    Archetype = archetype,
    ReferenceArchetype = referenceArchetype,
    Mainboard = includeDecklists ? tournament.Decks[i].Mainboard : null,
    Sideboard = includeDecklists ? tournament.Decks[i].Sideboard : null,
    Matchups = null
});
```

### Python Equivalent
```python
tournament_records.append({
    "tournament_file": os.path.splitext(tournament.file)[0],
    "tournament_name": tournament.information.name,
    "meta": meta_id,
    "week": week_id,
    "tournament_date": tournament.decks[0].date,
    "result": tournament.decks[i].result,
    "points": points,
    "wins": wins,
    "losses": losses,
    "draws": draws,
    "player_name": tournament.decks[i].player,
    "deck_url": tournament.decks[i].anchor_uri,
    "archetype": archetype,
    "reference_archetype": reference_archetype,
    "mainboard": tournament.decks[i].mainboard if include_decklists else None,
    "sideboard": tournament.decks[i].sideboard if include_decklists else None,
    "matchups": None
})
```

## 5. Corrections Critiques pour Notre Implémentation

1. **Noms de Colonnes**
   - Utiliser `mainboard` et `sideboard` au lieu de `deck_cards`
   - Utiliser `tournament_name` au lieu de `tournament`
   - Utiliser `player_name` au lieu de `player`
   - Utiliser `deck_url` au lieu de `anchor_uri`

2. **Structure des Cartes**
   - Chaque carte doit avoir `count` et `card` (ou `name`)
   - Utiliser des listes d'objets plutôt que des dictionnaires

3. **Détection d'Archétypes**
   - Implémenter toutes les conditions exactement comme dans le code C#
   - Utiliser le même algorithme pour déterminer les couleurs
   - Respecter la logique de résolution des conflits

4. **Format de Sortie JSON**
   - Inclure tous les champs du Record C# dans notre JSON
   - Utiliser les mêmes noms de champs (avec camelCase pour Python)
   - Préserver la structure hiérarchique

## 6. Modifications Nécessaires dans Notre Code

1. **src/python/classifier/mtgo_archetype_parser.py**
   - Reproduire exactement la logique de `ArchetypeAnalyzer.Detect`
   - Implémenter toutes les conditions d'archétypes
   - Utiliser les mêmes noms de méthodes et paramètres

2. **src/orchestrator.py**
   - Corriger le mapping des colonnes dans `_process_deck`
   - Assurer que `tournament_source` est toujours présent
   - Corriger la génération du JSON de sortie

3. **src/python/scraper/fbettega_integrator.py**
   - Assurer que les données sont structurées comme attendu par MTGOArchetypeParser
   - Mapper correctement les champs entre les sources et le format attendu
