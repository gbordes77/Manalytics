# ⚠️ SCRIPTS OBSOLÈTES - NE PAS UTILISER

Ce dossier contient des scripts qui ne sont plus utilisés dans le projet Manalytics.
Ils sont conservés uniquement pour référence historique.

## Scripts Obsolètes

### Scrapers Remplacés
- `scrape_mtgo_standalone.py` → Utiliser `scrape_mtgo_flexible.py` ou `scrape_all.py`
- `scrape_melee_from_commit.py` → Utiliser `scrape_melee_flexible.py` ou `scrape_all.py`

## ⛔ IMPORTANT

**NE JAMAIS UTILISER CES SCRIPTS**

Les nouveaux scripts offrent :
- Support multi-formats
- Dates personnalisables
- Mode incrémental (futur)
- Meilleure gestion d'erreurs

## Scripts Actuels à Utiliser

Pour scraper les données, utilisez :
```bash
# Recommandé - Scraper unifié
python scrape_all.py --format standard --days 21

# Ou scrapers individuels si nécessaire
python scrape_mtgo_flexible.py --format standard --days 21
python scrape_melee_flexible.py --format standard --days 21
```

Voir `docs/SCRAPERS_COMPLETE_GUIDE.md` pour la documentation complète.