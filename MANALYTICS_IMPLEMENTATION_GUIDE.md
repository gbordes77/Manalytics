# Guide d'Implémentation Manalytics

Ce document explique comment notre implémentation Python doit reproduire exactement le comportement du code C# original de MTGOArchetypeParser.

## 1. Comprendre le Workflow Original

Le workflow original est composé de trois étapes principales :

1. **Step 1: Data Collection**
   - Scraping des decklists MTGO (fbettega/mtg_decklist_scrapper)
   - Stockage des données brutes (MTG_decklistcache)
   - Écoute des matchups (MTGO-listener + MTGOSDK)
   - Consolidation des données (MTGODecklistCache)

2. **Step 2: Data Treatment**
   - Classification des archétypes (MTGOArchetypeParser)
   - Application des règles de format (MTGOFormatData)

3. **Step 3: Visualization**
   - Génération des matrices matchup (R-Meta-Analysis)
   - Publication des résultats

## 2. Différences Technologiques

Le workflow original utilise plusieurs langages et technologies :

- **C#/.NET** : MTGODecklistCache.Tools, MTGOArchetypeParser
- **JSON** : MTGOFormatData (règles d'archétypes)
- **R** : R-Meta-Analysis (visualisations)

Notre implémentation utilise Python pour tout le workflow, ce qui nécessite une reproduction fidèle du comportement des composants originaux.

## 3. Reproduction du Comportement de MTGOArchetypeParser

### 3.1 Structure des Données

#### Deck (C#)
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

#### Python Equivalent
```python
class Deck:
    def __init__(self):
        self.date = None  # DateTime?
        self.result = ""  # string
        self.player = ""  # string
        self.anchor_uri = ""  # Uri
        self.mainboard = []  # DeckItem[]
        self.sideboard = []  # DeckItem[]
```

### 3.2 Algorithme de Détection d'Archétypes

Le cœur de MTGOArchetypeParser est la méthode `Detect` qui analyse un deck et détermine son archétype :

#### C# Original
```csharp
public static ArchetypeResult Detect(Card[] mainboardCards, Card[] sideboardCards, ArchetypeFormat format, double minSimiliarity = 0.1, ConflictSolvingMode conflictSolvingMode = ConflictSolvingMode.None)
{
    // 1. Extraire les archétypes spécifiques et génériques
    ArchetypeSpecific[] specificArchetypes = archetypeData.Where(a => a is ArchetypeSpecific && !(a is ArchetypeVariant)).Select(a => a as ArchetypeSpecific).ToArray();
    ArchetypeGeneric[] genericArchetypes = archetypeData.Where(a => a is ArchetypeGeneric).Select(a => a as ArchetypeGeneric).ToArray();

    // 2. Déterminer le companion et les couleurs
    ArchetypeCompanion? companion = GetCompanion(mainboardCards, sideboardCards);
    ArchetypeColor color = GetColors(mainboardCards, sideboardCards, landColors, cardColors);

    // 3. Tester les archétypes spécifiques
    List<ArchetypeMatch> results = new List<ArchetypeMatch>();
    foreach (ArchetypeSpecific archetype in specificArchetypes)
    {
        if (Test(mainboardCards, sideboardCards, color, archetype))
        {
            // Tester les variants
            bool isVariant = false;
            if (archetype.Variants != null)
            {
                foreach (ArchetypeSpecific variant in archetype.Variants)
                {
                    if (Test(mainboardCards, sideboardCards, color, variant))
                    {
                        isVariant = true;
                        results.Add(new ArchetypeMatch() { Archetype = archetype, Variant = variant, Similarity = 1 });
                    }
                }
            }
            if (!isVariant) results.Add(new ArchetypeMatch() { Archetype = archetype, Variant = null, Similarity = 1 });
        }
    }

    // 4. Si aucun archétype spécifique ne correspond, essayer les archétypes génériques
    if (results.Count == 0)
    {
        ArchetypeMatch genericArchetype = GetBestGenericArchetype(mainboardCards, sideboardCards, color, genericArchetypes);
        if (genericArchetype != null && genericArchetype.Similarity > minSimiliarity) results.Add(genericArchetype);
    }
    else
    {
        // 5. Résoudre les conflits si nécessaire
        if (results.Count > 1 && conflictSolvingMode == ConflictSolvingMode.PreferSimpler)
        {
            results = results.OrderBy(r => r.Archetype.GetComplexity() + (r.Variant != null ? r.Variant.GetComplexity() : 0)).Take(1).ToList();
        }
    }

    // 6. Retourner le résultat
    return new ArchetypeResult() { Matches = results.ToArray(), Color = color, Companion = companion };
}
```

#### Python Equivalent
```python
def detect(self, mainboard_cards, sideboard_cards, format_data, min_similarity=0.1, conflict_solving_mode=ConflictSolvingMode.NONE):
    """
    Détecte l'archétype d'un deck selon les règles du format

    Args:
        mainboard_cards: Liste des cartes du mainboard
        sideboard_cards: Liste des cartes du sideboard
        format_data: Données du format (archétypes, couleurs, etc.)
        min_similarity: Similarité minimum pour les archétypes génériques
        conflict_solving_mode: Mode de résolution des conflits

    Returns:
        ArchetypeResult avec les matches, couleurs et companion
    """
    # 1. Extraire les archétypes spécifiques et génériques
    specific_archetypes = [a for a in format_data.archetypes if isinstance(a, ArchetypeSpecific) and not isinstance(a, ArchetypeVariant)]
    generic_archetypes = [a for a in format_data.archetypes if isinstance(a, ArchetypeGeneric)]

    # 2. Déterminer le companion et les couleurs
    companion = self._get_companion(mainboard_cards, sideboard_cards)
    color = self._get_colors(mainboard_cards, sideboard_cards, format_data.lands, format_data.non_lands)

    # 3. Tester les archétypes spécifiques
    results = []
    for archetype in specific_archetypes:
        if self._test(mainboard_cards, sideboard_cards, color, archetype):
            # Tester les variants
            is_variant = False
            if archetype.variants:
                for variant in archetype.variants:
                    if self._test(mainboard_cards, sideboard_cards, color, variant):
                        is_variant = True
                        results.append(ArchetypeMatch(archetype=archetype, variant=variant, similarity=1.0))

            if not is_variant:
                results.append(ArchetypeMatch(archetype=archetype, variant=None, similarity=1.0))

    # 4. Si aucun archétype spécifique ne correspond, essayer les archétypes génériques
    if not results:
        generic_archetype = self._get_best_generic_archetype(mainboard_cards, sideboard_cards, color, generic_archetypes)
        if generic_archetype and generic_archetype.similarity > min_similarity:
            results.append(generic_archetype)
    else:
        # 5. Résoudre les conflits si nécessaire
        if len(results) > 1 and conflict_solving_mode == ConflictSolvingMode.PREFER_SIMPLER:
            results = sorted(results, key=lambda r: r.archetype.get_complexity() + (r.variant.get_complexity() if r.variant else 0))
            results = results[:1]

    # 6. Retourner le résultat
    return ArchetypeResult(matches=results, color=color, companion=companion)
```

### 3.3 Test des Conditions

Le cœur de la détection d'archétypes est la méthode `Test` qui vérifie si un deck correspond à un archétype :

#### C# Original
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
            case ArchetypeConditionType.InMainOrSideboard:
                if (!mainboardCards.Any(c => c.Name == condition.Cards[0]) && !sideboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            case ArchetypeConditionType.OneOrMoreInMainboard:
                if (!mainboardCards.Any(c => condition.Cards.Contains(c.Name))) return false;
                break;
            case ArchetypeConditionType.OneOrMoreInSideboard:
                if (!sideboardCards.Any(c => condition.Cards.Contains(c.Name))) return false;
                break;
            case ArchetypeConditionType.OneOrMoreInMainOrSideboard:
                if (!mainboardCards.Any(c => condition.Cards.Contains(c.Name)) && !sideboardCards.Any(c => condition.Cards.Contains(c.Name))) return false;
                break;
            case ArchetypeConditionType.TwoOrMoreInMainboard:
                if (mainboardCards.Where(c => condition.Cards.Contains(c.Name)).Count() < 2) return false;
                break;
            case ArchetypeConditionType.TwoOrMoreInSideboard:
                if (sideboardCards.Where(c => condition.Cards.Contains(c.Name)).Count() < 2) return false;
                break;
            case ArchetypeConditionType.TwoOrMoreInMainOrSideboard:
                if ((mainboardCards.Where(c => condition.Cards.Contains(c.Name)).Count() + sideboardCards.Where(c => condition.Cards.Contains(c.Name)).Count()) < 2) return false;
                break;
            case ArchetypeConditionType.DoesNotContain:
                if (mainboardCards.Any(c => c.Name == condition.Cards[0]) || sideboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            case ArchetypeConditionType.DoesNotContainMainboard:
                if (mainboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            case ArchetypeConditionType.DoesNotContainSideboard:
                if (sideboardCards.Any(c => c.Name == condition.Cards[0])) return false;
                break;
            default:
                throw new NotImplementedException();
        }
    }

    return true;
}
```

#### Python Equivalent
```python
def _test(self, mainboard_cards, sideboard_cards, color, archetype_data):
    """
    Teste si un deck correspond à un archétype selon ses conditions

    Args:
        mainboard_cards: Liste des cartes du mainboard
        sideboard_cards: Liste des cartes du sideboard
        color: Couleurs du deck
        archetype_data: Données de l'archétype à tester

    Returns:
        True si le deck correspond à l'archétype, False sinon
    """
    for condition in archetype_data.conditions:
        if not condition.cards or len(condition.cards) == 0:
            continue  # Skip broken condition

        if condition.type == ArchetypeConditionType.IN_MAINBOARD:
            if not any(c.name == condition.cards[0] for c in mainboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.IN_SIDEBOARD:
            if not any(c.name == condition.cards[0] for c in sideboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.IN_MAIN_OR_SIDEBOARD:
            if not any(c.name == condition.cards[0] for c in mainboard_cards) and not any(c.name == condition.cards[0] for c in sideboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.ONE_OR_MORE_IN_MAINBOARD:
            if not any(c.name in condition.cards for c in mainboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.ONE_OR_MORE_IN_SIDEBOARD:
            if not any(c.name in condition.cards for c in sideboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.ONE_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            if not any(c.name in condition.cards for c in mainboard_cards) and not any(c.name in condition.cards for c in sideboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.TWO_OR_MORE_IN_MAINBOARD:
            if len([c for c in mainboard_cards if c.name in condition.cards]) < 2:
                return False
        elif condition.type == ArchetypeConditionType.TWO_OR_MORE_IN_SIDEBOARD:
            if len([c for c in sideboard_cards if c.name in condition.cards]) < 2:
                return False
        elif condition.type == ArchetypeConditionType.TWO_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            if len([c for c in mainboard_cards if c.name in condition.cards]) + len([c for c in sideboard_cards if c.name in condition.cards]) < 2:
                return False
        elif condition.type == ArchetypeConditionType.DOES_NOT_CONTAIN:
            if any(c.name == condition.cards[0] for c in mainboard_cards) or any(c.name == condition.cards[0] for c in sideboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.DOES_NOT_CONTAIN_MAINBOARD:
            if any(c.name == condition.cards[0] for c in mainboard_cards):
                return False
        elif condition.type == ArchetypeConditionType.DOES_NOT_CONTAIN_SIDEBOARD:
            if any(c.name == condition.cards[0] for c in sideboard_cards):
                return False
        else:
            # Log unknown condition type
            logger.warning(f"Unknown condition type: {condition.type}")
            return False

    return True
```

## 4. Reproduction du Flux de Données

### 4.1 Chargement des Tournois

#### C# Original
```csharp
Tournament[] tournaments = TournamentLoader.GetTournamentsByDate(cacheFolder, startDate, filter);
```

#### Python Equivalent
```python
tournaments = tournament_loader.get_tournaments_by_date(cache_folder, start_date, filter_func)
```

### 4.2 Traitement des Decks

#### C# Original
```csharp
Record[] records = RecordLoader.GetRecords(tournaments, format, referenceFormat, includeDecklists, includeMatchups, maxDecksPerEvent, conflictSolvingMode);
```

#### Python Equivalent
```python
records = record_loader.get_records(tournaments, format_data, reference_format, include_decklists, include_matchups, max_decks_per_event, conflict_solving_mode)
```

### 4.3 Génération des Sorties

#### C# Original
```csharp
IOutput output = null;
switch (settings.OutputMode.ToLowerInvariant())
{
    case "csv":
        output = new CsvOutput(settings.OutputFile);
        break;
    case "json":
        output = new JsonOutput(settings.OutputFile);
        break;
    case "console":
        output = new ConsoleOutput();
        break;
    case "reddit":
        output = new RedditOutput(settings.OutputFile);
        break;
    default:
        throw new Exception($"Unknown output mode: {settings.OutputMode}");
}

output.Write(records);
```

#### Python Equivalent
```python
if output_mode == "csv":
    output = CsvOutput(output_file)
elif output_mode == "json":
    output = JsonOutput(output_file)
elif output_mode == "console":
    output = ConsoleOutput()
elif output_mode == "reddit":
    output = RedditOutput(output_file)
else:
    raise ValueError(f"Unknown output mode: {output_mode}")

output.write(records)
```

## 5. Conclusion

Pour reproduire fidèlement le comportement du code C# original dans notre implémentation Python, nous devons :

1. **Respecter les structures de données** : Utiliser les mêmes noms de champs et types de données
2. **Reproduire les algorithmes** : Implémenter les mêmes algorithmes de détection d'archétypes
3. **Maintenir le flux de données** : Assurer que les données circulent correctement entre les composants
4. **Gérer les erreurs** : Implémenter la même logique de gestion des erreurs et des cas limites

En suivant ce guide, nous pourrons assurer que notre implémentation Python reproduit fidèlement le comportement du code C# original, permettant ainsi une transition en douceur vers notre solution unifiée.
