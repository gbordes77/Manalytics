# 📚 Documentation Complète Manalytics v3.0.0

## 🎯 Objectif Principal
Analyser le métagame Magic: The Gathering Standard pour fournir des insights compétitifs.

## ⚠️ RÈGLES CRITIQUES À RETENIR

### 📅 **PÉRIODE D'ANALYSE OBLIGATOIRE**
```
Du 1er au 21 juillet 2025
```
- **Pourquoi** : Pour comparer avec la dernière publication de Jiliac
- **TOUJOURS** utiliser ces dates pour les analyses
- **NE JAMAIS** analyser au-delà du 21 juillet

### 🚫 **EXCLUSION DES LEAGUES**
- Les leagues (5-0) sont **TOUJOURS** exclues
- Triple protection dans le code
- Stockées dans un dossier `leagues/` séparé

### 🎨 **TEMPLATE VISUEL OBLIGATOIRE**
- Fichier de référence : `data/cache/standard_analysis_no_leagues.html`
- Header avec gradient purple (#667eea → #764ba2)
- Gradients MTG pour les archétypes multi-couleurs
- Document de référence : `docs/VISUALIZATION_TEMPLATE_REFERENCE.md`

## 📁 Structure du Projet

```
Manalytics/
├── src/manalytics/          # CODE PRINCIPAL
│   ├── scrapers/            # Scrapers MTGO & Melee
│   ├── parsers/             # Détection archétypes
│   ├── cache/               # Système de cache
│   ├── analyzers/           # Analyses métagame
│   ├── visualizers/         # Génération HTML
│   ├── pipeline/            # Orchestration
│   └── api/                 # FastAPI endpoints
│
├── data/                    # DONNÉES
│   ├── raw/                 # Données brutes scrapers
│   ├── cache/               # Données processées
│   └── listener/            # Future: données Jiliac
│
├── scripts/                 # UTILITAIRES ONE-SHOT
│   └── _archive_2025_07_27/ # Anciens scripts
│
├── docs/                    # DOCUMENTATION
│   ├── CLAUDE.md            # Instructions IA
│   ├── DATA_FLOW_VISUALIZATION.html
│   ├── FILE_DISCOVERY_PROCESS.html
│   └── [Tous les guides...]
│
└── visualize_standard.py    # LANCEUR RAPIDE
```

## 🚀 Commandes Essentielles

### Pour générer la visualisation de référence
```bash
python3 visualize_standard.py
```
→ Génère `data/cache/standard_analysis_no_leagues.html`

### Pour analyser juillet 1-21
```bash
python3 analyze_july_1_21.py
```

### Pipeline complet
```bash
# 1. Scraper les données
manalytics scrape --format standard --days 21

# 2. Processer le cache
python3 scripts/process_all_standard_data.py

# 3. Générer la visualisation
python3 visualize_standard.py
```

## 📊 Documents Générés

### 1. **Visualisations HTML**
- `DATA_FLOW_VISUALIZATION.html` - Flux de données interactif
- `FILE_DISCOVERY_PROCESS.html` - Comment on trouve les fichiers
- `JILIAC_INTEGRATION_SCHEMAS.html` - Architecture Jiliac
- `standard_analysis_no_leagues.html` - **LA visualisation de référence**

### 2. **Guides Techniques**
- `MELEE_SCRAPING_GUIDE.md` - Scraper Melee avec auth
- `MTGO_SCRAPING_GUIDE.md` - Scraper MTGO
- `CACHE_SYSTEM_IMPLEMENTATION.md` - Architecture cache
- `SCRAPING_BEST_PRACTICES.md` - Leçons apprises

### 3. **Documentation Architecture**
- `JILIAC_R_ARCHITECTURE_ANALYSIS.md` - Analyse de l'architecture R
- `JILIAC_VISUALIZATIONS_GAP_ANALYSIS.md` - Ce qui nous manque
- `VISUALIZATION_TEMPLATE_REFERENCE.md` - **RÈGLES VISUELLES ABSOLUES**
- `REORGANIZATION_SUMMARY.md` - Résumé du nettoyage

### 4. **Roadmaps**
- `PHASE3_VISUALIZATIONS_ROADMAP.md` - 30+ visualisations planifiées
- `CONSENSUS_DECK_GENERATOR.md` - Feature unique ML
- `INNOVATION_DETECTOR_CONCEPT.md` - Détection tech choices

## 🔄 Flux de Données

1. **Scraping** → `data/raw/{platform}/{format}/`
2. **Processing** → Cache SQLite + JSON
3. **Analysis** → Meta percentages, trends
4. **Visualization** → HTML interactif

### Filtrage Standard
- Au scraping : dossier `/standard/`
- Au processing : `WHERE format='standard'`
- Exclusion leagues : 3 niveaux de protection

## 🎯 Ce qui Fonctionne Actuellement

✅ **Scrapers**
- MTGO : Challenges, Qualifiers (pas d'auth requise)
- Melee : Tous tournois (auth cookie 21 jours)

✅ **Cache System**
- SQLite pour metadata rapide
- JSON pour decklists complètes
- Partitionnement par mois

✅ **Visualisation**
- Plotly interactif avec gradients MTG
- Export CSV/PNG/SVG
- Mobile responsive

✅ **Analyses**
- Par decks ET par matches (méthode Jiliac)
- Exclusion automatique tournois casual
- Trends temporelles

## ❌ Ce qui Manque (vs Jiliac)

1. **MTGO Listener** - Capture matchups round-par-round
2. **Mustache Graph** - Win rates avec intervalles de confiance
3. **Tier Scatterplot** - Classification automatique
4. **Performance Scatter** - Trouver les hidden gems
5. **Matchup Matrix** - Heatmap des win rates

## 🔑 Points Clés pour les Prochaines Équipes

1. **TOUJOURS** analyser du 1er au 21 juillet 2025
2. **JAMAIS** inclure les leagues dans les analyses
3. **UTILISER** le template visuel de référence
4. **LIRE** `docs/CLAUDE.md` pour les règles IA
5. **TESTER** avec `visualize_standard.py` d'abord

## 📝 Auto-Commit Obligatoire

Après CHAQUE modification :
```bash
git add -A && git commit -m "auto: $(date +%Y%m%d_%H%M%S)"
```

## 🚨 Contacts & Support

- Issues : github.com/anthropics/claude-code/issues
- Références : github.com/Jiliac/R-Meta-Analysis
- Pipeline communautaire : Voir CLAUDE.md pour liens

---

**Dernière mise à jour** : 27 juillet 2025
**Version** : 3.0.0
**Status** : Phase 3 - Visualisations Avancées