# MTG Analytics Pipeline

Un pipeline unifié pour l'analyse des données de tournois Magic: The Gathering.

## Structure du projet

Le projet est organisé en trois phases principales :
- **Collecte de données** : Scraping des données depuis MTGO et MTGMelee
- **Traitement des données** : Catégorisation des decks par archétypes
- **Visualisation** : Génération de matrices de matchups et analyses du métagame

## Installation

### Unix/Linux/macOS
```bash
cd manalytics
./setup.sh
```

### Windows
```powershell
cd manalytics
.\setup.ps1
```

## Utilisation

Pour générer une analyse :
```bash
cd manalytics
./generate_analysis.sh standard 7  # Analyse du format Standard sur les 7 derniers jours
```

## Fonctionnalités

- Collecte de données depuis MTGO et MTGMelee
- Traitement et catégorisation des decks par archétypes
- Génération de visualisations (matrices de matchups, répartition du métagame)
- Orchestrateur pour exécuter l'ensemble du pipeline