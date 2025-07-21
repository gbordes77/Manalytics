# Corrections Nécessaires pour Manalytics

Ce document détaille les corrections nécessaires pour résoudre les problèmes de mapping entre le code C# original de MTGOArchetypeParser et notre implémentation Python.

## 1. Problème Principal Identifié

Le problème principal est une incohérence dans les noms de colonnes et la structure des données entre le Step 1 (collecte de données) et le Step 2 (traitement des archétypes).

### Problème Spécifique
Dans la fonction `_process_deck` de l'orchestrateur, les cartes sont stockées dans `deck_cards` :
```python
"deck_cards": deck.get("Mainboard", deck.get("mainboard", []))
```

Mais dans la génération du JSON de sortie, les cartes sont attendues dans `mainboard` et `sideboard` :
```python
"mainboard": row.get("mainboard", []),
"sideboard": row.get("sideboard", [])
```

## 2. Corrections Nécessaires

### 2.1 Correction dans `_process_deck`

Modifier la fonction `_process_deck` pour stocker les cartes dans `mainboard` et `sideboard` au lieu de `deck_cards` :

```python
# AVANT
"deck_cards": deck.get("Mainboard", deck.get("mainboard", [])),

# APRÈS
"mainboard": deck.get("Mainboard", deck.get("mainboard", [])),
"sideboard": deck.get("Sideboard", deck.get("sideboard", [])),
```

### 2.2 Assurer la Présence de `tournament_source`

Assurer que la colonne `tournament_source` est toujours présente dans les données :

```python
# Dans _process_deck, assurer que source est toujours défini
source = self._determine_source(file_path, tournament_info)
if not source:
    source = "Unknown"  # Valeur par défaut
```

### 2.3 Correction dans `mtgo_archetype_parser.py`

Assurer que la fonction `_extract_card_names` traite correctement les différents formats de cartes :

```python
def _extract_card_names(self, decklist: List[Dict]) -> List[str]:
    """Extrait les noms de cartes d'une decklist"""
    card_names = []
    for card in decklist:
        # Support des formats:
        # {"Name": "...", "Quantity": ...}
        # {"CardName": "...", "Count": ...}
        # {"Card": "...", "Count": ...}
        card_name = card.get("Name", card.get("CardName", card.get("Card", "")))
        if card_name:
            card_names.append(card_name)
    return card_names
```

### 2.4 Correction dans la Génération du JSON de Sortie

Assurer que le JSON de sortie inclut toutes les informations nécessaires :

```python
deck_data = {
    "deck_id": f"{row.get('tournament_id', 'unknown')}_{row.get('player_name', 'unknown')}",
    "archetype": row.get("archetype", "Unknown"),
    "archetype_with_colors": row.get("archetype_with_colors", row.get("archetype", "Unknown")),
    "color_identity": row.get("color_identity", ""),
    "guild_name": row.get("guild_name", ""),
    "player_name": row.get("player_name", "Unknown"),
    "tournament_name": row.get("tournament_name", "Unknown"),
    "tournament_date": tournament_date,
    "tournament_source": row.get("tournament_source", "Unknown"),
    "deck_url": row.get("deck_url", ""),
    "mainboard": row.get("mainboard", []),
    "sideboard": row.get("sideboard", []),
    "wins": row.get("wins", 0),
    "losses": row.get("losses", 0),
    "draws": row.get("draws", 0),
    "matches_played": row.get("matches_played", 0),
    "winrate": row.get("winrate", 0.0),
}
```

## 3. Implémentation des Corrections

### 3.1 Correction dans `src/orchestrator.py`

```python
def _process_deck(self, deck, tournament_info, tournament_date, file_path):
    """Traiter un deck individual (comme l'ancien système)"""
    # Extraire les wins/losses
    wins, losses = self._extract_results(deck)

    # Get mainboard and sideboard for analysis
    mainboard = deck.get("Mainboard", deck.get("mainboard", []))
    sideboard = deck.get("Sideboard", deck.get("sideboard", []))

    # Classify archetype with Advanced Archetype Classifier (already includes color integration)
    archetype_with_colors = self._classify_archetype(mainboard)

    # Analyze deck colors for additional metadata
    color_analysis = self.color_detector.analyze_decklist_colors(mainboard)

    # Extract simple archetype name (without colors) for backwards compatibility
    archetype = self._extract_simple_archetype_name(archetype_with_colors)

    # DEBUG: Log archetype classification for troubleshooting
    self.logger.debug(
        f"Deck classification: '{archetype_with_colors}' -> '{archetype}'"
    )

    # Determine source with MTGO differentiation
    source = self._determine_source(file_path, tournament_info)
    if not source:
        source = "Unknown"  # Valeur par défaut

    # Extract deck URL from AnchorUri field
    deck_url = deck.get("AnchorUri", deck.get("anchor_uri", ""))

    return {
        "tournament_id": tournament_info.get(
            "Uri", tournament_info.get("id", file_path)
        ),
        "tournament_name": tournament_info.get(
            "Name", tournament_info.get("name", "Tournoi")
        ),
        "tournament_date": tournament_date,
        "tournament_source": source,
        "format": self.format,
        "player_name": deck.get("Player", deck.get("player", "")),
        "archetype": archetype,
        "archetype_with_colors": archetype_with_colors,
        "color_identity": color_analysis["identity"],
        "guild_name": color_analysis["guild_name"],
        "color_distribution": color_analysis["color_distribution"],
        "wins": wins,
        "losses": losses,
        "draws": deck.get("draws", 0),
        "matches_played": wins + losses,
        "winrate": wins / max(1, wins + losses) if (wins + losses) > 0 else 0,
        "placement": deck.get("placement", 0),
        "mainboard": mainboard,  # CORRECTION: Utiliser mainboard au lieu de deck_cards
        "sideboard": sideboard,  # AJOUT: Inclure sideboard
        "deck_url": deck_url,
    }
```

### 3.2 Correction dans la Génération du JSON de Sortie

```python
# Prepare detailed export data
export_data = []
for _, row in df.iterrows():
    # Convert Timestamp to string for JSON serialization
    tournament_date = row.get("tournament_date", "Unknown")
    if hasattr(tournament_date, "strftime"):
        tournament_date = tournament_date.strftime("%Y-%m-%d")
    elif tournament_date != "Unknown":
        tournament_date = str(tournament_date)

    # Assurer que tournament_source est présent
    tournament_source = row.get("tournament_source", "Unknown")

    deck_data = {
        "deck_id": f"{row.get('tournament_id', 'unknown')}_{row.get('player_name', 'unknown')}",
        "archetype": row.get("archetype", "Unknown"),
        "archetype_with_colors": row.get("archetype_with_colors", row.get("archetype", "Unknown")),
        "color_identity": row.get("color_identity", ""),
        "guild_name": row.get("guild_name", ""),
        "player_name": row.get("player_name", "Unknown"),
        "tournament_name": row.get("tournament_name", "Unknown"),
        "tournament_date": tournament_date,
        "tournament_source": tournament_source,
        "deck_url": row.get("deck_url", ""),
        "mainboard": row.get("mainboard", []),
        "sideboard": row.get("sideboard", []),
        "wins": row.get("wins", 0),
        "losses": row.get("losses", 0),
        "draws": row.get("draws", 0),
    }
    export_data.append(deck_data)
```

## 4. Conclusion

Ces corrections permettront de résoudre les problèmes de mapping entre le code C# original et notre implémentation Python, assurant ainsi que les données sont correctement structurées pour le Step 2 (traitement des archétypes) et que le JSON de sortie contient toutes les informations nécessaires.
