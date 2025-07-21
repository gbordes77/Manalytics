# Plan de Test : Pipeline Manalytics Step 1 + Step 2

## Objectif

Évaluer la viabilité d'une analyse utilisant uniquement les étapes 1 (collecte de données) et 2 (traitement/classification) du pipeline Manalytics, sans l'étape 3 (visualisation R). Cette évaluation permettra de déterminer si les données traitées sont suffisantes pour une analyse de qualité et combien de tournois sont correctement pris en compte.

## Contexte

Actuellement, le pipeline Manalytics comprend trois étapes principales :
1. **Step 1 (Collecte)** : Scraping des decklists MTGO via mtg_decklist_scrapper
2. **Step 2 (Traitement)** : Classification des archétypes via MTGOArchetypeParser (C#)
3. **Step 3 (Visualisation)** : Analyse statistique et visualisation via R-Meta-Analysis (R)

Nous envisageons de migrer le code C# (Step 2) vers Python, mais nous devons d'abord évaluer si les données produites par Step 1 + Step 2 sont suffisantes sans Step 3.

## Métriques à Collecter

### 1. Couverture des Données
- **Nombre total de tournois** traités
- **Nombre total de decks** classifiés
- **Période couverte** (date début - date fin)
- **Formats couverts** (Modern, Pioneer, Legacy, etc.)

### 2. Qualité de Classification
- **Taux de classification réussi** (% de decks avec archétype identifié)
- **Distribution des archétypes** (nombre de decks par archétype)
- **Taux d'archétypes "Unknown"** ou non classifiés

### 3. Performance
- **Temps d'exécution total** du pipeline Step 1 + Step 2
- **Temps par étape** (collecte vs traitement)
- **Utilisation ressources** (mémoire, CPU)

### 4. Comparaison avec Pipeline Complet
- **Différence en nombre de tournois** traités
- **Différence en insights** générés
- **Manques critiques** identifiés

## Procédure de Test

### Préparation
1. **Configurer environnement isolé**
   ```bash
   # Créer environnement de test
   python -m venv test_env
   source test_env/bin/activate

   # Installer dépendances
   pip install -r requirements.txt
   ```

2. **Configurer pipeline sans Step 3**
   ```python
   # Modifier config.py
   ENABLE_STEP3 = False
   ```

### Exécution
1. **Lancer collecte de données** (Step 1)
   ```bash
   python src/collectors/mtgo_collector.py --days 30
   ```

2. **Lancer traitement des données** (Step 2)
   ```bash
   python src/orchestrator.py --skip-visualization
   ```

3. **Collecter métriques**
   ```bash
   python src/tools/metrics_collector.py --output metrics_step1_step2.json
   ```

### Analyse
1. **Générer rapport de base**
   ```bash
   python src/tools/generate_basic_report.py --input processed_data/ --output basic_report.html
   ```

2. **Comparer avec pipeline complet**
   ```bash
   python src/tools/compare_pipelines.py --baseline full_pipeline_metrics.json --test metrics_step1_step2.json
   ```

## Critères de Succès

Le test sera considéré comme réussi si :

1. **Au moins 90%** des tournois sont correctement traités
2. **Au moins 85%** des decks sont correctement classifiés
3. **Le temps d'exécution** est réduit d'au moins 30% par rapport au pipeline complet
4. **Les données de base** (archétypes, winrates) sont disponibles même sans analyses avancées

## Scénarios de Décision

### Scénario 1 : Test Réussi avec Excellents Résultats
- **Résultat :** >95% tournois traités, >90% decks classifiés
- **Décision :** Procéder à la migration C# → Python, conserver R pour analyses avancées uniquement

### Scénario 2 : Test Réussi avec Résultats Acceptables
- **Résultat :** 90-95% tournois traités, 85-90% decks classifiés
- **Décision :** Procéder à la migration C# → Python, envisager approche hybride pour Step 3

### Scénario 3 : Test Partiellement Réussi
- **Résultat :** 80-90% tournois traités, 75-85% decks classifiés
- **Décision :** Procéder à la migration C# → Python, maintenir R pour Step 3 complet

### Scénario 4 : Test Échoué
- **Résultat :** <80% tournois traités, <75% decks classifiés
- **Décision :** Réévaluer l'approche, potentiellement maintenir architecture actuelle

## Rapport de Test

Le rapport de test devra inclure :

1. **Résumé exécutif** avec recommandation claire
2. **Métriques détaillées** collectées
3. **Visualisations de base** des données traitées
4. **Comparaison** avec pipeline complet
5. **Recommandations** pour la suite du projet

## Timeline

- **Configuration environnement :** 1 jour
- **Exécution des tests :** 1-2 jours
- **Analyse des résultats :** 1-2 jours
- **Préparation rapport :** 1 jour
- **Réunion de décision :** 0.5 jour

**Total estimé :** 4.5-6.5 jours ouvrés

## Équipe Requise

- 1 développeur senior Python
- 1 data scientist / analyste
- 1 testeur

## Prochaines Étapes Post-Test

Selon les résultats du test, l'équipe procédera à :

1. **Migration C# → Python** (Step 2)
2. **Décision finale** concernant Step 3 (R → Python ou maintien R)
3. **Mise à jour du plan de projet** avec timeline révisée

---

**Préparé par :** Équipe Manalytics
**Date :** 21 juillet 2025
**Version :** 1.0
