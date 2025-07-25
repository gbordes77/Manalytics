# 🚀 Guide de Démarrage Rapide pour le Prochain Développeur

## 📌 Ce qu'il faut savoir ABSOLUMENT

### 1. Architecture Réelle (pas de SQL!)
```
Données → Fichiers JSON → Scripts Python → Visualisations HTML
```

- **PAS de base de données** (malgré ce que certains vieux docs pourraient dire)
- **PAS de migrations** 
- Les données sont dans `data/raw/` en JSON (~3,667 decklists)
- Les scripts lisent DIRECTEMENT les fichiers JSON
- Un petit cache SQLite existe mais n'est PAS utilisé pour les visualisations

### 2. Scripts qui fonctionnent VRAIMENT

```bash
# 1. Traiter les données JSON vers le cache
python3 scripts/process_all_standard_data.py

# 2. Générer la visualisation HTML (avec camembert et pourcentages)
python3 scripts/create_archetype_visualization.py

# 3. Voir les stats du cache
python3 scripts/show_cache_stats.py
```

### 3. Fichiers de sortie
- `data/cache/standard_analysis_no_leagues.html` - LA visualisation principale
- Ouvre ce fichier dans ton navigateur pour voir les graphiques

### 4. Structure des données
```
data/
├── raw/                    # Fichiers JSON des tournois
│   ├── mtgo/              
│   │   └── standard/       # ~385 fichiers
│   └── melee/             
│       └── standard/       # ~129 fichiers
└── cache/                  # Cache SQLite + HTML générés
    ├── tournaments.db      # Metadata seulement!
    └── *.html             # Visualisations
```

### 5. ⚠️ IMPORTANT : Les Leagues
- Les fichiers dans `*/leagues/` sont EXCLUS des analyses
- C'est voulu! Les leagues ne sont pas des vrais tournois compétitifs

### 6. Ce qui a été fait en Phase 3
- ✅ Camembert avec noms d'archétypes DANS les parts
- ✅ Pourcentages partout dans toutes les visualisations
- ✅ Exclusion automatique des leagues
- ✅ Support des noms de guildes (Izzet, Dimir, etc.)

## 🎯 Pour continuer le projet

1. **Lire** : `docs/PHASE3_VISUALIZATIONS_ROADMAP.md` - 30+ idées de visualisations
2. **Priorité** : Heatmap de matchups (win rates entre archétypes)
3. **Innovation** : Consensus Deck Generator (voir `docs/CONSENSUS_DECK_GENERATOR.md`)

## 🛑 Pièges à éviter

1. **NE PAS** essayer de créer une vraie base SQL - c'est inutile pour ce volume
2. **NE PAS** toucher aux fichiers dans `obsolete/`
3. **TOUJOURS** exclure les leagues des analyses
4. **UTILISER** `create_archetype_visualization.py` comme base pour nouvelles viz

## 📞 Contact
Si tu es perdu, les docs essentielles sont :
- `CLAUDE.md` - Contexte complet du projet
- `docs/ARCHITECTURE_SUMMARY.md` - Architecture factuelle
- `docs/CACHE_SYSTEM_IMPLEMENTATION.md` - Comment marche le cache

Bon courage! 🎉