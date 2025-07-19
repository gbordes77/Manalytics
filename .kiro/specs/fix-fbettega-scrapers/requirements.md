# Requirements Document - Correction des Scrapers Fbettega

## Introduction

Les scrapers fbettega actuels trouvent bien les tournois mais ne récupèrent pas les données des decks/standings car ils utilisent des URLs incorrectes et des méthodes de parsing inadéquates. Cette spec vise à corriger les scrapers pour qu'ils fonctionnent comme le pipeline original de Jilliac/Fbettega et récupèrent réellement les données des tournois.

## Requirements

### Requirement 1 - Correction du scraper MTGO

**User Story:** En tant qu'utilisateur du pipeline, je veux que le scraper MTGO fbettega récupère les vraies données des tournois, afin d'avoir des analyses complètes avec des decks réels.

#### Acceptance Criteria

1. WHEN le scraper MTGO est exécuté THEN il SHALL utiliser les vraies URLs MTGO (format: `https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1512802868`)
2. WHEN le scraper parse une page de tournoi THEN il SHALL extraire correctement les decks avec Player, Result, Mainboard, Sideboard
3. WHEN le scraper trouve un tournoi THEN il SHALL vérifier que les standings ne sont pas vides avant de l'ajouter
4. WHEN le scraper rencontre une erreur de parsing THEN il SHALL logger l'erreur et continuer avec les autres tournois
5. WHEN le scraper termine THEN il SHALL retourner uniquement les tournois avec des données valides (standings_count > 0)

### Requirement 2 - Correction du scraper Melee

**User Story:** En tant qu'utilisateur du pipeline, je veux que le scraper Melee fbettega récupère les vraies données des tournois Melee.gg, afin d'avoir une couverture complète des sources de données.

#### Acceptance Criteria

1. WHEN le scraper Melee est exécuté THEN il SHALL utiliser l'API Melee.gg ou parser correctement les pages HTML
2. WHEN le scraper accède à un tournoi Melee THEN il SHALL extraire les standings avec positions et decks
3. WHEN le scraper parse un deck Melee THEN il SHALL convertir le format au format standard (Player, Result, Mainboard, Sideboard)
4. WHEN le scraper rencontre des credentials manquants THEN il SHALL fonctionner en mode anonyme avec limitations
5. WHEN le scraper termine THEN il SHALL retourner les tournois avec des données complètes

### Requirement 3 - Amélioration de l'intégrateur fbettega

**User Story:** En tant qu'utilisateur du pipeline, je veux que l'intégrateur fbettega filtre et valide les données récupérées, afin d'éviter les tournois vides dans les analyses.

#### Acceptance Criteria

1. WHEN l'intégrateur reçoit des données des scrapers THEN il SHALL filtrer les tournois avec standings_count = 0
2. WHEN l'intégrateur valide un tournoi THEN il SHALL vérifier que chaque deck a au minimum Player et Mainboard
3. WHEN l'intégrateur détecte des doublons THEN il SHALL les éliminer en gardant la version la plus complète
4. WHEN l'intégrateur termine THEN il SHALL générer un rapport avec le nombre de tournois valides vs vides
5. WHEN l'intégrateur échoue sur un scraper THEN il SHALL continuer avec les autres sources disponibles

### Requirement 4 - Compatibilité avec l'architecture Jilliac

**User Story:** En tant que développeur, je veux que les scrapers fbettega respectent l'architecture originale de Jilliac, afin de maintenir la compatibilité et la cohérence du système.

#### Acceptance Criteria

1. WHEN les scrapers sont exécutés THEN ils SHALL utiliser la même structure de données que l'original Jilliac
2. WHEN les scrapers retournent des données THEN elles SHALL être compatibles avec le format MTGODecklistCache
3. WHEN les scrapers utilisent le cache THEN ils SHALL respecter la structure de cache de Jilliac
4. WHEN les scrapers loggent des informations THEN ils SHALL utiliser le même format de logs que Jilliac
5. WHEN les scrapers gèrent les erreurs THEN ils SHALL suivre les patterns de gestion d'erreur de Jilliac

### Requirement 5 - Tests et validation

**User Story:** En tant que développeur, je veux pouvoir tester et valider que les scrapers fbettega fonctionnent correctement, afin de m'assurer de la qualité des données récupérées.

#### Acceptance Criteria

1. WHEN je teste un scraper THEN il SHALL pouvoir être testé individuellement avec des données de test
2. WHEN je valide les données THEN le système SHALL fournir des métriques de qualité (% tournois valides, nb decks par tournoi)
3. WHEN je compare avec l'original THEN les données SHALL être cohérentes avec celles de MTGODecklistCache
4. WHEN je lance les tests THEN ils SHALL couvrir les cas d'erreur (URLs invalides, parsing échoué, etc.)
5. WHEN je génère un rapport THEN il SHALL inclure les statistiques de succès/échec par source
