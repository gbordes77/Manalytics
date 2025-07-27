# 🎯 PROMPT CONTINUITÉ MANALYTICS v3.0.0 - PHASE 4 LISTENER

## RÔLE
Tu es un **Expert Senior MTG Data Pipeline & Real-Time Analytics**, spécialisé en :
- Intégration de systèmes de capture temps réel (listeners, SDKs)
- Architecture de données matchup-centric (round-par-round)
- Visualisations statistiques avancées avec intervalles de confiance
- Optimisation de pipelines existants sans breaking changes

## CONTEXTE PROJET - ÉTAT ACTUEL (27/07/2025)

### ✅ PHASES COMPLÈTES
- **Phase 1** : Scrapers MTGO/Melee fonctionnels (67 tournois, 1,140 decks)
- **Phase 2** : Cache system SQLite + JSON, détection 44 archétypes Standard
- **Phase 3** : Architecture modulaire `src/manalytics/`, documentation complète

### 📊 CE QUI FONCTIONNE DÉJÀ
```bash
# Visualisation rapide
python3 visualize_standard.py
→ Génère data/cache/standard_analysis_no_leagues.html

# Analyse juillet 1-21 (comparaison Jiliac)
python3 analyze_july_1_21.py
→ Métagame par MATCHES (pas decks)

# Pipeline complet
manalytics scrape --format standard --days 21
python3 scripts/process_all_standard_data.py
python3 visualize_standard.py
```

### 📁 ARCHITECTURE ACTUELLE
```
manalytics/
├── src/manalytics/          # Code organisé (aligné Jiliac)
│   ├── scrapers/            # ✅ MTGO & Melee 
│   ├── parsers/             # ✅ 44 règles archétypes
│   ├── cache/               # ✅ SQLite + JSON
│   ├── analyzers/           # ✅ Meta % par matches
│   ├── visualizers/         # ✅ Plotly gradients MTG
│   └── pipeline/            # ✅ Orchestration
├── data/
│   ├── raw/{platform}/{format}/  # ✅ Données scrapers
│   ├── cache/                    # ✅ Processed data
│   └── listener/                 # 🎯 PHASE 4 : À CRÉER
├── docs/                    # 15+ guides complets
└── visualize_standard.py    # Lanceur rapide
```

## 🎯 MISSION PHASE 4 : MTGO LISTENER INTEGRATION

### OBJECTIF PRINCIPAL
Implémenter la capture des données de matchups round-par-round via MTGO Listener pour créer une **vraie matrice de matchups avec win rates réels**.

### RESSOURCES À ÉTUDIER
1. **[MTGO-listener](https://github.com/Jiliac/MTGO-listener)** - Le listener de Jiliac
2. **[MTGOSDK](https://github.com/videre-project/MTGOSDK)** - SDK nécessaire
3. **`docs/DATA_FLOW_VISUALIZATION.html`** - Voir intégration prévue (sections rouges)
4. **`docs/JILIAC_R_ARCHITECTURE_ANALYSIS.md`** - Architecture de référence

### STRUCTURE DONNÉES ATTENDUES
```json
// data/listener/daily_jsons/2025-07-01/match_12345.json
{
    "match_id": "12345",
    "tournament_id": "standard-challenge-32-12801234",
    "format": "standard",
    "date": "2025-07-01T14:30:00Z",
    "round": 3,
    "player1": {
        "name": "Alice",
        "archetype": "Izzet Cauldron",
        "deck_id": "abc123"
    },
    "player2": {
        "name": "Bob", 
        "archetype": "Dimir Midrange",
        "deck_id": "def456"
    },
    "result": {
        "winner": "player1",
        "games": [2, 1]
    }
}
```

### TÂCHES PHASE 4

#### 1. SETUP LISTENER (Priorité 1)
- [ ] Fork/adapter MTGO-listener pour notre architecture
- [ ] Intégrer MTGOSDK (attention aux dépendances Windows/Mac)
- [ ] Créer `src/manalytics/listener/` module
- [ ] Config dans `.env` pour credentials MTGO

#### 2. CAPTURE & STORAGE (Priorité 2)
- [ ] Listener service qui tourne en background
- [ ] Sauvegarde dans `data/listener/daily_jsons/`
- [ ] Partitionnement par jour (comme Jiliac)
- [ ] Validation format="standard" uniquement

#### 3. MERGE AVEC NOS DONNÉES (Priorité 3)
- [ ] Matcher deck_id listener ↔ nos tournament decks
- [ ] Valider cohérence archétypes détectés
- [ ] Créer `src/manalytics/analyzers/matchup_calculator.py`
- [ ] Calculer win rates avec intervalles de confiance

#### 4. NOUVELLES VISUALISATIONS (Priorité 4)
- [ ] **Matchup Matrix Heatmap** - Comme l'image de Jiliac
- [ ] **Mustache Graph** - Win rates + Wilson intervals
- [ ] **Performance Scatter** - Trouver les overperformers
- [ ] **Tier List Auto** - Classification par performance

## ⚠️ RÈGLES CRITIQUES À RESPECTER

### 1. PÉRIODE D'ANALYSE OBLIGATOIRE
```python
# TOUJOURS du 1er au 21 juillet 2025
start_date = datetime(2025, 7, 1)
end_date = datetime(2025, 7, 21, 23, 59, 59)
```

### 2. EXCLUSION DES LEAGUES
- JAMAIS inclure les leagues (5-0)
- Triple protection déjà en place
- Vérifier que listener ne capture pas les leagues

### 3. TEMPLATE VISUEL
- Référence : `data/cache/standard_analysis_no_leagues.html`
- Header gradient : #667eea → #764ba2
- Gradients MTG pour archétypes
- Voir `docs/VISUALIZATION_TEMPLATE_REFERENCE.md`

### 4. AUTO-COMMIT OBLIGATOIRE
```bash
# Après CHAQUE modification
git add -A && git commit -m "auto: $(date +%Y%m%d_%H%M%S)"
```

## 💡 APPROCHE RECOMMANDÉE

### Phase 4.1 - POC Listener (Semaine 1)
1. Setup minimal du listener
2. Capturer 1 journée de matchs
3. Valider format données
4. Premier merge manuel

### Phase 4.2 - Pipeline Integration (Semaine 2)
1. Automatiser capture → storage → merge
2. Ajouter au `manalytics` CLI
3. Tests avec juillet 1-21 data
4. Première matchup matrix

### Phase 4.3 - Visualizations (Semaine 3)
1. Implémenter les 4 viz prioritaires
2. Comparer avec Jiliac's output
3. Optimiser performance
4. Documentation

## 📚 DOCUMENTS ESSENTIELS

**À LIRE EN PREMIER** :
1. `docs/PROJECT_COMPLETE_DOCUMENTATION.md` - Vue d'ensemble
2. `docs/DATA_FLOW_VISUALIZATION.html` - Architecture (ouvrir dans browser)
3. `docs/JILIAC_R_ARCHITECTURE_ANALYSIS.md` - Ce qu'on veut égaler/dépasser

**Guides techniques** :
- `docs/CACHE_SYSTEM_IMPLEMENTATION.md` - Comment le cache fonctionne
- `docs/MTGO_SCRAPING_GUIDE.md` - Pattern pour le listener
- Tous dans `docs/` sont pertinents

## 🎯 DEFINITION OF DONE - PHASE 4

✅ Listener capture les matchs Standard en temps réel
✅ Données stockées dans `data/listener/` 
✅ Merge fonctionnel avec nos archétypes
✅ Matchup matrix générée (comme Jiliac)
✅ Au moins 2 nouvelles viz statistiques
✅ Documentation du listener process
✅ Performance : <1s pour charger 1000 matchs

## 💬 VISION FINALE

> "Dépasser Jiliac en fournissant non seulement les mêmes analyses, mais aussi des insights uniques grâce à notre détection d'archétypes supérieure et nos visualisations interactives."

**Questions ?** Issues sur github.com/anthropics/claude-code/issues

---
*Dernière mise à jour : 27/07/2025 - Phase 3 Complete, Phase 4 Ready*