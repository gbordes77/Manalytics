# Architecture Manalytics - Résumé Factuel

## 🏗️ Architecture Actuelle

### Stockage des Données
- **Données principales** : Fichiers JSON dans `data/raw/{platform}/{format}/`
  - ~385 fichiers MTGO
  - ~129 fichiers Melee
  - Total : ~3,667 decklists complètes
  
- **Cache minimal** : SQLite (`data/cache/tournaments.db`)
  - Uniquement pour metadata des tournois
  - Structure simple : tournaments, decklists (metadata seulement)
  - Les données réelles des decks restent dans les JSON

### Traitement
1. **Scrapers** → Fichiers JSON
2. **Scripts de visualisation** → Lisent directement les JSON
3. **Output** → Fichiers HTML avec graphiques interactifs

Note: Un cache SQLite existe mais les visualisations lisent les JSON directement

### Scripts Principaux
- `scripts/create_archetype_visualization.py` - Génère les visualisations HTML
- `scripts/process_all_standard_data.py` - Process les données vers le cache
- `scripts/show_cache_stats.py` - Affiche les statistiques

## ❌ Ce qui N'EXISTE PAS
- Pas de PostgreSQL
- Pas de migrations
- Pas de base de données relationnelle complète
- Pas de tables complexes (cards, matchups, etc.)

## ✅ Pourquoi cette Architecture Fonctionne
- Volume de données gérable (~3,667 decks)
- Performance excellente (<500ms par tournoi)
- Simplicité de maintenance
- Pas de dépendances lourdes

## 📊 Résultat Final
- Visualisations HTML interactives avec Chart.js
- Pie chart avec labels dans les parts
- Pourcentages partout
- Exclusion automatique des leagues