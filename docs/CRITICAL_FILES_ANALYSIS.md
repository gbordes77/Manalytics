# 🔒 Analyse des Fichiers Critiques vs Obsolètes

## ✅ FICHIERS CRITIQUES - NE PAS TOUCHER

### 1. Scrapers Fonctionnels
```
✅ scrape_melee_working_v2.py
   - Scraper Melee 100% fonctionnel (25/07/2025)
   - Dépendances : AUCUNE dépendance locale, que des libs Python
   - Utilise : api_credentials/melee_login.json
   - Génère : api_credentials/melee_cookies.json
   - Output : data/raw/melee/standard/*.json

✅ scrape_mtgo_tournaments_enhanced.py
   - Scraper MTGO fonctionnel avec IDs uniques
   - Dépendances : scrapers/mtgo_scraper_enhanced.py
   - Output : data/raw/mtgo/{format}/*.json

✅ scrapers/mtgo_scraper_enhanced.py
   - Classe MTGOEnhancedScraper utilisée par le script ci-dessus
   - CRITIQUE : Ne pas déplacer sans mettre à jour l'import
```

### 2. Fichiers de Support Critiques
```
✅ api_credentials/
   ├── melee_login.json      # Credentials Melee
   └── melee_cookies.json    # Cookies auto-générés

✅ src/utils/data_loader.py
   - Utilisé par : scripts/run_pipeline_with_existing_data.py
   - Charge les données depuis data/raw/

✅ test_melee_auth_simple.py
   - Test d'authentification Melee
   - Utile pour débugger les problèmes de connexion
```

### 3. Modèles de Données Utilisés
```
✅ scrapers/models/base_model.py
   - Classes : Tournament, Standing, Round, Deck, etc.
   - Utilisé par : le code original du scraper Melee

✅ scrapers/models/Melee_model.py
   - Classes spécifiques Melee
   - Référencé dans le code original
```

### 4. Documentation Essentielle
```
✅ CLAUDE.md
✅ docs/MELEE_SCRAPING_GUIDE.md
✅ docs/SCRAPING_BEST_PRACTICES.md
✅ docs/PROJECT_ANALYSIS_COMPLETE.md
```

## ❌ FICHIERS OBSOLÈTES - PEUVENT ÊTRE DÉPLACÉS

### 1. Tests et Debug à la Racine (30+ fichiers)
```
❌ test_melee_*.py (SAUF test_melee_auth_simple.py)
   - test_melee_basic.py
   - test_melee_debug.py
   - test_melee_direct_standard.py
   - test_melee_final.py
   - test_melee_fixed.py
   - test_melee_form_encoded.py
   - test_melee_html.py
   - test_melee_minimal.py
   - test_melee_real.py
   - test_melee_scraper_new.py
   - test_melee_scraper.py
   - test_melee_simple_working.py
   - test_melee_simple.py
   - test_melee_web_auth.py

❌ debug_*.py (TOUS)
   - debug_melee_api.py
   - debug_melee_auth_search.py
   - debug_melee_auth.py
   - debug_melee_js.py
   - debug_melee_response.py
   - debug_melee_search.py
   - debug_mtgo_js.py
   - debug_mtgo_scraper.py
   - debug_mtgo_simple.py

❌ test_*.py (autres)
   - test_format_comparison.py
   - test_manual_login.py
   - test_mtgo_formats.py
   - test_mtgo_july.py
   - test_mtgo_scraper_direct.py
   - test_mtgo_urls.py
   - test_scraper_direct.py
   - test_scraper_exact.py
   - test_scraper_modern.py
   - test_scraper.py
   - test_scrapers.py
```

### 2. Anciennes Versions de Scrapers
```
❌ scrape_melee_simple.py
❌ scrape_melee_tournaments_complete_v2.py
❌ scrape_melee_tournaments_complete.py
❌ scrape_melee_tournaments_robust.py
❌ scrape_melee_working.py (v1)
❌ scrape_mtgo_tournaments_robust.py
❌ scrape_mtgo_tournaments.py
❌ scrape_standard_tournaments_fixed.py
❌ scrape_standard_tournaments.py
❌ mtgo_scraper_fixed.py
```

### 3. Scripts de Collecte/Analyse Obsolètes
```
❌ analyze_melee_search_page.py
❌ analyze_tournament_search.py
❌ check_melee_site.py
❌ collect_all_tournaments.py
❌ collect_tournaments_simple.py
❌ explore_melee_data.py
❌ extract_mtgo_final.py
❌ generate_cache_report_simple.py
❌ generate_complete_report.py
❌ generate_tournament_cache_report.py
❌ melee_search_fix.py
❌ run_melee_scraper.py
❌ run_melee_simple.py
❌ show_existing_mtgo_data.py
❌ show_melee_tournaments_july.py
❌ move_scraped_data.py
```

### 4. Dans src/scrapers/ - Versions Non Utilisées
```
❌ src/scrapers/archive/ (tout le dossier)
❌ src/scrapers/melee_scraper_httpx.py
❌ src/scrapers/melee_scraper_simple_backup.py
❌ src/scrapers/melee_scraper_simple.py
❌ src/scrapers/melee_scraper_working.py

⚠️ src/scrapers/melee_scraper.py - INCERTAIN (vérifier si utilisé par pipeline)
⚠️ src/scrapers/mtgo_scraper.py - INCERTAIN (vérifier si utilisé par pipeline)
```

### 5. Dans scrapers/ - Duplicatas
```
❌ scrapers/melee_scraper_complete.py
❌ scrapers/melee_scraper_robust.py
❌ scrapers/mtgo_scraper_robust.py
❌ scrapers/mtgo_scraper_v2.py
```

## ⚠️ FICHIERS À VÉRIFIER AVANT DE DÉPLACER

### Pipeline Principal
```
⚠️ scripts/run_pipeline.py
   - Import : from src.scrapers.mtgo_scraper import MTGOScraper
   - Import : from src.scrapers.melee_scraper import MeleeScraper
   - ATTENTION : Utilise les scrapers dans src/, pas ceux à la racine!

⚠️ src/scrapers/mtgo_scraper.py
⚠️ src/scrapers/melee_scraper.py
   - Si run_pipeline.py est utilisé, ces fichiers sont CRITIQUES
   - Sinon, ils sont obsolètes
```

## 🔍 VÉRIFICATION NÉCESSAIRE

Avant de déplacer quoi que ce soit, il faut vérifier :

1. **Est-ce que scripts/run_pipeline.py est utilisé ?**
   - Si OUI : src/scrapers/mtgo_scraper.py et melee_scraper.py sont CRITIQUES
   - Si NON : Ils peuvent être déplacés

2. **Est-ce que l'API Docker utilise certains fichiers ?**
   - Vérifier le Dockerfile et docker-compose.yml

3. **Est-ce que certains scripts dans scripts/ sont encore utilisés ?**
   - Particulièrement ceux mentionnés dans README.md