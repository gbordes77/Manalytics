# Requirements Document

## Introduction

Ce projet vise à reconstruire et unifier le pipeline de données pour l'analyse des tournois Magic: The Gathering (MTG). Le système actuel est fragmenté à travers plusieurs repositories GitHub et nécessite une consolidation pour faciliter la maintenance et l'extension. Le pipeline complet comprend trois étapes principales : la collecte de données depuis les plateformes MTGO et MTGMelee, le traitement et la catégorisation des decks par archétypes, et enfin la visualisation des données pour analyse.

## Requirements

### Requirement 1: Consolidation des Repositories

**User Story:** En tant que développeur, je veux consolider les 6 repositories GitHub existants dans une structure unifiée, afin de simplifier la maintenance et l'évolution du système.

#### Acceptance Criteria

1. WHEN le script d'installation est exécuté THEN le système SHALL cloner les 6 repositories GitHub dans la structure de dossiers définie.
2. WHEN les repositories sont clonés THEN le système SHALL préserver l'intégrité du code original sans modifications initiales.
3. WHEN la structure est créée THEN le système SHALL organiser les fichiers selon l'architecture définie (data-collection, data-treatment, visualization).
4. WHEN la consolidation est terminée THEN le système SHALL fournir une documentation complète sur l'architecture et les dépendances.

### Requirement 2: Collecte de Données MTGO

**User Story:** En tant qu'analyste de données MTG, je veux collecter automatiquement les données de tournois depuis la plateforme MTGO, afin d'avoir des données à jour pour mes analyses.

#### Acceptance Criteria

1. WHEN le module de scraping MTGO est exécuté THEN le système SHALL extraire les decklists des tournois récents.
2. WHEN les données sont scrapées THEN le système SHALL les stocker dans le format approprié dans le cache brut.
3. WHEN des erreurs de scraping surviennent THEN le système SHALL les journaliser et tenter de récupérer sans interruption complète.
4. WHEN de nouvelles données sont collectées THEN le système SHALL éviter les duplications avec les données existantes.
5. WHEN le scraping est terminé THEN le système SHALL générer un rapport de statut avec les statistiques de collecte.

### Requirement 3: Intégration de l'API MTGMelee

**User Story:** En tant qu'analyste de données MTG, je veux intégrer les données de tournois depuis la plateforme MTGMelee via son API, afin d'élargir la couverture des données d'analyse.

#### Acceptance Criteria

1. WHEN le module MTGMelee est configuré THEN le système SHALL se connecter à l'API avec les identifiants appropriés.
2. WHEN l'API MTGMelee est appelée THEN le système SHALL respecter les limites de taux (rate limits) imposées.
3. WHEN les données MTGMelee sont récupérées THEN le système SHALL les convertir dans le même format que les données MTGO pour un traitement unifié.
4. WHEN l'API MTGMelee est indisponible THEN le système SHALL journaliser l'erreur et continuer avec les autres sources de données.
5. WHEN de nouvelles données MTGMelee sont collectées THEN le système SHALL les intégrer au cache existant sans conflits.

### Requirement 4: Traitement et Catégorisation des Données

**User Story:** En tant qu'analyste de métagame, je veux que le système catégorise automatiquement les decks par archétypes, afin d'analyser les tendances du métagame.

#### Acceptance Criteria

1. WHEN les données brutes sont disponibles THEN le système SHALL utiliser MTGOArchetypeParser pour catégoriser les decks.
2. WHEN la catégorisation est effectuée THEN le système SHALL utiliser les règles définies dans MTGOFormatData.
3. WHEN de nouveaux archétypes émergent THEN le système SHALL permettre la mise à jour des règles de catégorisation.
4. WHEN des decks ne correspondent à aucun archétype connu THEN le système SHALL les marquer pour révision manuelle.
5. WHEN le traitement est terminé THEN le système SHALL organiser les données par format de jeu (Standard, Modern, etc.).

### Requirement 5: Visualisation des Données

**User Story:** En tant qu'analyste de métagame, je veux générer des visualisations des données de matchups, afin de comprendre les forces et faiblesses des différents archétypes.

#### Acceptance Criteria

1. WHEN les données traitées sont disponibles THEN le système SHALL utiliser les scripts R pour générer des matrices de matchups.
2. WHEN les visualisations sont générées THEN le système SHALL produire des graphiques de haute qualité adaptés à la publication.
3. WHEN de nouvelles données sont ajoutées THEN le système SHALL permettre la mise à jour des visualisations existantes.
4. WHEN des erreurs surviennent dans la génération de visualisations THEN le système SHALL fournir des messages d'erreur détaillés.
5. WHEN les visualisations sont terminées THEN le système SHALL faciliter leur exportation pour publication sur Discord ou autres plateformes.

### Requirement 6: Documentation et Maintenance

**User Story:** En tant que développeur ou contributeur, je veux une documentation complète du système, afin de pouvoir comprendre, maintenir et étendre le pipeline.

#### Acceptance Criteria

1. WHEN le système est installé THEN le système SHALL fournir une documentation claire sur l'architecture globale.
2. WHEN des modifications sont apportées THEN le système SHALL faciliter la mise à jour de la documentation.
3. WHEN de nouveaux contributeurs rejoignent le projet THEN le système SHALL offrir un guide de démarrage rapide.
4. WHEN des problèmes surviennent THEN le système SHALL documenter les erreurs connues et leurs solutions.
5. WHEN de nouvelles fonctionnalités sont ajoutées THEN le système SHALL inclure des tests pour valider leur fonctionnement.

### Requirement 7: Tests et Validation

**User Story:** En tant que développeur, je veux des tests automatisés pour le pipeline, afin d'assurer la fiabilité et la qualité des données produites.

#### Acceptance Criteria

1. WHEN le système est installé THEN le système SHALL inclure des tests de connectivité pour valider l'accès aux sources de données.
2. WHEN des données sont collectées THEN le système SHALL valider leur format et leur intégrité.
3. WHEN le traitement est effectué THEN le système SHALL vérifier la cohérence des catégorisations.
4. WHEN des visualisations sont générées THEN le système SHALL valider leur exactitude par rapport aux données sources.
5. WHEN des modifications sont apportées au code THEN le système SHALL exécuter les tests pour éviter les régressions.