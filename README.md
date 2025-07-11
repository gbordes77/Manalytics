# 🧙‍♂️ Manalytics - Pipeline d'Analyse de Métagame MTG

Manalytics est un pipeline hybride Python/R pour l'analyse automatisée du métagame Magic: The Gathering. Il fusionne les fonctionnalités de plusieurs projets de référence pour créer un système complet d'acquisition, classification et analyse des données de tournois.

## 🎯 Fonctionnalités

- **Scraping Multi-Sources** : Collecte automatisée depuis Melee.gg, MTGO et Topdeck
- **Classification d'Archétypes** : Moteur de règles basé sur MTGOFormatData
- **Analyse Statistique** : Calcul des métriques de métagame et matrices de matchups
- **Pipeline Orchestré** : Exécution automatisée de bout en bout
- **Format de Sortie Standard** : Compatible avec le schéma MTGODecklistCache

## 🏗️ Architecture

```
Manalytics/
├── orchestrator.py          # Point d'entrée principal
├── config.yaml             # Configuration centralisée
├── requirements.txt        # Dépendances Python
├── renv.lock              # Dépendances R
├── src/
│   ├── python/
│   │   ├── scraper/       # Modules de scraping
│   │   ├── classifier/    # Moteur de classification
│   │   └── utils/         # Utilitaires communs
│   └── r/
│       ├── analysis/      # Scripts d'analyse R
│       └── utils/         # Fonctions R communes
├── data/
│   ├── raw/              # Données brutes scrapées
│   ├── processed/        # Données enrichies
│   └── output/           # Résultats finaux (metagame.json)
├── logs/                 # Journalisation
└── MTGOFormatData/       # Règles d'archétypes (submodule)
```

## 🚀 Installation

### Prérequis

- Python 3.9+
- R 4.0+
- Git

### Installation des Dépendances

#### Python
```bash
pip install -r requirements.txt
```

#### R
```bash
# Installer les packages R requis
Rscript -e "install.packages(c('jsonlite', 'dplyr', 'tidyr', 'purrr', 'lubridate', 'ggplot2', 'readr'))"

# Ou utiliser renv pour la reproductibilité
Rscript -e "renv::restore()"
```

### Configuration Initiale

1. **Cloner les dépôts de référence** (déjà fait si vous avez suivi l'installation)
   
2. **Configurer les credentials** :
   ```bash
   # Credentials Melee.gg (optionnel)
   echo '{"login": "votre_email", "mdp": "votre_mot_de_passe"}' > credentials/melee_login.json
   
   # API Key Topdeck (optionnel)
   echo "VOTRE_API_KEY" > credentials/topdeck_api.txt
   ```

3. **Vérifier la configuration** :
   ```bash
   # Tester que R est accessible
   Rscript --version
   
   # Tester que les modules Python se chargent
   python -c "import yaml, aiohttp, structlog; print('OK')"
   ```

## 📖 Utilisation

### Commande de Base

```bash
python orchestrator.py --format Modern --start-date 2025-01-01 --end-date 2025-01-31
```

### Options Avancées

```bash
python orchestrator.py \
  --format Modern \
  --start-date 2025-01-01 \
  --end-date 2025-01-31 \
  --config config.yaml \
  --skip-scraping \          # Ignorer le scraping (utiliser données existantes)
  --skip-classification      # Ignorer la classification (utiliser données classifiées)
```

### Formats Supportés

- Modern
- Legacy
- Standard
- Pioneer
- Vintage
- Pauper

*Note: La disponibilité dépend des règles d'archétypes dans MTGOFormatData*

### Exemples d'Utilisation

#### Analyse du métagame Modern de la semaine dernière
```bash
python orchestrator.py --format Modern
```

#### Analyse Legacy avec données existantes
```bash
python orchestrator.py --format Legacy --skip-scraping --start-date 2025-01-01
```

#### Pipeline complet pour Pioneer
```bash
python orchestrator.py --format Pioneer --start-date 2025-01-01 --end-date 2025-01-31
```

## 📊 Format de Sortie

Le pipeline génère un fichier `metagame.json` dans `data/output/` avec la structure suivante :

```json
{
  "metadata": {
    "generated_at": "2025-01-15T10:30:00Z",
    "total_decks": 1247,
    "total_tournaments": 23,
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-01-31"
    },
    "formats": ["Modern"],
    "sources": ["mtgo.com", "melee.gg"]
  },
  "archetype_performance": [
    {
      "archetype": "Burn",
      "deck_count": 89,
      "win_rate": 0.573,
      "meta_share": 0.071,
      "tournaments_appeared": 18
    }
  ],
  "matchup_matrix": [
    {
      "archetype_a": "Burn",
      "archetype_b": "Control",
      "estimated_win_rate": 0.62,
      "confidence": "high"
    }
  ],
  "temporal_trends": { ... },
  "source_statistics": { ... }
}
```

## ⚙️ Configuration

Le fichier `config.yaml` permet de personnaliser tous les aspects du pipeline :

```yaml
# Sources de données à utiliser
enabled_sources: ["melee", "mtgo", "topdeck"]

# Paramètres de scraping
scraping:
  max_retries: 5
  concurrent_requests: 10
  rate_limit_delay: 0.5

# Paramètres de classification
classification:
  min_confidence: 0.8
  unknown_threshold: 5

# Paramètres d'analyse
analysis:
  min_matches_for_matchup: 10
  min_decks_for_archetype: 5
```

## 🔧 Développement

### Structure du Code

- **Scrapers** : Classes héritant de `BaseScraper` pour chaque source
- **Classifier** : Moteur de règles réimplémentant la logique MTGOArchetypeParser
- **Analysis** : Scripts R adaptés de R-Meta-Analysis
- **Orchestrator** : Coordination et gestion d'erreurs

### Ajouter un Nouveau Scraper

1. Créer une classe héritant de `BaseScraper`
2. Implémenter `authenticate()`, `discover_tournaments()` et `fetch_tournament()`
3. Ajouter la source dans `config.yaml`
4. Mettre à jour l'orchestrateur

### Tests

```bash
# Tests Python
python -m pytest tests/

# Tests R
Rscript tests/test_analysis.R
```

## 📝 Logging

Les logs sont automatiquement générés dans `logs/` avec :
- Timestamp de chaque opération
- Détails des erreurs et retry
- Statistiques de performance
- Format JSON structuré

## 🤝 Contribution

Ce projet s'appuie sur le travail excellent de :
- [fbettega/mtg_decklist_scrapper](https://github.com/fbettega/mtg_decklist_scrapper)
- [Jiliac/MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache)
- [Badaro/MTGOArchetypeParser](https://github.com/Badaro/MTGOArchetypeParser)
- [Jiliac/R-Meta-Analysis](https://github.com/Jiliac/R-Meta-Analysis)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour des questions ou problèmes :
1. Vérifiez les logs dans `logs/`
2. Consultez la configuration dans `config.yaml`
3. Testez chaque phase individuellement avec les options `--skip-*`

---

**Manalytics** - Transformez vos données de tournois en insights stratégiques ! 🎯 