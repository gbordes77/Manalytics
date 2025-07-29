ou # 🔍 AUDIT SCRIPTS ACTIFS - MANALYTICS

**Date**: 29/07/2025  
**Objectif**: Identifier quel script fait quoi et lequel est le "bon"

## 📊 STATISTIQUES ALARMANTES

- **21 scripts d'analyse** différents
- **15 scripts de scraping** différents  
- **3 architectures** coexistantes
- **Résultat**: Chaos total !

## 🎯 SCRIPTS D'ANALYSE (21 scripts)

### Scripts Récents/Actifs (basé sur les noms)
1. `analyze_july_jiliac_method.py` ⭐ **RÉFÉRENCE JILIAC**
2. `analyze_july_complete_final.py` ⭐ **VERSION "FINALE"**
3. `analyze_july_all_6_visualizations.py` ⭐ **6 VISUALISATIONS**
4. `analyze_july_maximum_coverage.py` ⭐ **COVERAGE MAXIMUM**

### Scripts Spécialisés
- `analyze_melee_*.py` → Analyse spécifique Melee
- `analyze_mtgodata_*.py` → Analyse listener MTGO
- `analyze_*_no_leagues.py` → Exclusion leagues

### Scripts Legacy/Obsolètes
- `analyze_july_fixed.py` → Probablement remplacé
- `analyze_july_centralized_fix.py` → Fix temporaire
- `analyze_competitive_only.py` → Logique ancienne

## 🌐 SCRIPTS DE SCRAPING (15 scripts)

### Scripts Unifiés (Recommandés)
1. `scrape_all.py` ⭐ **SCRAPER UNIFIÉ**
2. `scrape_all_with_decklists.py` ⭐ **AVEC DECKLISTS**

### Scripts Spécialisés MTGO
- `scrape_mtgo_flexible.py` → Flexible
- `scrape_mtgo_complete.py` → Complet
- `scrape_mtgo_json.py` → Format JSON
- `scrape_mtgo_with_decklists.py` → Avec decklists

### Scripts Spécialisés Melee
- `scrape_melee_flexible.py` → Flexible
- `scrape_melee_with_rounds.py` → Avec rounds
- `scrape_melee_with_proper_rounds.py` → Rounds "propres"

## 🔍 ANALYSE DES IMPORTS

### Structure Moderne (src/manalytics/)
```python
# Scripts qui utilisent la structure moderne
from src.manalytics.visualizers import create_standard_analysis_visualization
from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
```

### Structure Legacy (scrapers/)
```python
# Scripts qui utilisent l'ancienne structure
from scrapers.mtgo_scraper_enhanced import MTGOEnhancedScraper
```

### Scripts Autonomes
```python
# Scripts qui n'utilisent aucune structure
import requests
from bs4 import BeautifulSoup
# Logique inline
```

## 🎯 IDENTIFICATION DU SCRIPT DE RÉFÉRENCE

### Pour l'Analyse Jiliac
**Script de référence**: `analyze_july_jiliac_method.py`
- ✅ Nom explicite
- ✅ Utilise structure moderne
- ✅ Méthode Jiliac documentée

### Pour le Scraping Unifié  
**Script de référence**: `scrape_all.py`
- ✅ Nom explicite "all"
- ✅ Logique unifiée
- ✅ Arguments standardisés

### Pour les Visualisations
**Script de référence**: `visualize_standard.py`
- ✅ Utilise `src.manalytics.visualizers`
- ✅ Structure moderne
- ✅ Nom simple et clair

## 🚨 PROBLÈMES CRITIQUES IDENTIFIÉS

### 1. Aucune Documentation sur "Quel Script Utiliser"
- Nouveau développeur ne sait pas quoi choisir
- Même l'équipe actuelle semble perdue

### 2. Scripts Contradictoires
- `analyze_july_fixed.py` vs `analyze_july_complete_final.py`
- Lequel est vraiment "final" ?

### 3. Versions Multiples Sans Numérotation
- `analyze_july_complete_with_all_visuals.py`
- `analyze_july_complete_with_all_visuals_v2.py`
- Pas de système de versioning clair

## 📋 ACTIONS RECOMMANDÉES

### 1. Créer un Fichier SCRIPTS_REFERENCE.md
```markdown
# SCRIPTS DE RÉFÉRENCE - À UTILISER

## Analyse Standard
- **Script**: `analyze_july_jiliac_method.py`
- **Usage**: `python analyze_july_jiliac_method.py`

## Scraping Complet  
- **Script**: `scrape_all.py`
- **Usage**: `python scrape_all.py --format standard --days 21`

## Visualisation
- **Script**: `visualize_standard.py`  
- **Usage**: `python visualize_standard.py`
```

### 2. Marquer les Scripts Obsolètes
```bash
mkdir _obsolete_scripts/
mv analyze_july_fixed.py _obsolete_scripts/
mv analyze_july_centralized_fix.py _obsolete_scripts/
# etc.
```

### 3. Créer des Alias/Symlinks
```bash
ln -s analyze_july_jiliac_method.py analyze.py
ln -s scrape_all.py scrape.py
ln -s visualize_standard.py visualize.py
```

## 🎯 CONCLUSION

**Le mystère des matchups** pourrait être résolu simplement en :
1. **Identifiant LE bon script** à utiliser
2. **Documentant sa logique** exacte
3. **Supprimant les alternatives** qui créent la confusion

**Recommandation**: Commencer par tester `analyze_july_jiliac_method.py` car il semble être le plus récent et spécifiquement conçu pour reproduire la méthode Jiliac.