# Implementation Plan - Correction des Scrapers Fbettega

- [ ] 1. Analyser et corriger le scraper MTGO
  - Analyser les vraies URLs MTGO utilisées dans MTGODecklistCache
  - Corriger les méthodes de récupération des URLs de tournois
  - Implémenter le parsing correct des pages de tournois MTGO
  - Tester la récupération des decks avec données réelles
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. Corriger le parsing des données MTGO
  - Analyser la structure HTML réelle des pages MTGO
  - Corriger les sélecteurs CSS/XPath pour extraire les decks
  - Implémenter l'extraction correcte des Player, Result, Mainboard, Sideboard
  - Gérer les différents formats de résultats (1st Place, 5-0, etc.)
  - _Requirements: 1.2, 1.3_

- [ ] 3. Améliorer la validation des données MTGO
  - Ajouter la validation des tournois avant de les retourner
  - Filtrer les tournois avec standings_count = 0
  - Logger les erreurs de parsing sans arrêter le processus
  - Implémenter des fallbacks pour les données manquantes
  - _Requirements: 1.3, 1.4, 1.5_

- [ ] 4. Corriger le scraper Melee
  - Analyser l'API Melee.gg ou la structure HTML des pages
  - Corriger les méthodes d'authentification si nécessaire
  - Implémenter le parsing correct des standings Melee
  - Convertir les données Melee au format standard
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 5. Améliorer l'intégrateur fbettega
  - Ajouter la validation des données avant intégration
  - Implémenter le filtrage des tournois vides
  - Améliorer la déduplication des tournois
  - Générer des rapports de qualité des données
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6. Tester les corrections avec des données réelles
  - Tester le scraper MTGO avec des tournois récents
  - Tester le scraper Melee avec des tournois connus
  - Valider que les données sont compatibles avec l'orchestrateur
  - Comparer les résultats avec MTGODecklistCache existant
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Optimiser les performances et la robustesse
  - Ajouter la gestion des timeouts et retry
  - Implémenter le cache intelligent pour éviter les requêtes répétées
  - Optimiser les requêtes HTTP avec session pooling
  - Ajouter la gestion des rate limits
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. Intégrer et tester le pipeline complet
  - Intégrer les scrapers corrigés dans l'orchestrateur
  - Tester le pipeline complet avec la période 1-15 juillet 2025
  - Valider que les analyses sont générées avec des données réelles
  - Comparer les métriques avant/après correction
  - _Requirements: 4.1, 4.2, 5.2, 5.5_
