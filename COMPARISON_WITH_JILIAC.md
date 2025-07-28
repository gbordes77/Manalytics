# 📊 COMPARAISON MANALYTICS VS JILIAC - ANALYSE JUILLET 1-21, 2025

## RÉSUMÉ EXÉCUTIF

### Jiliac
- **25 tournois** (17 MTGO + 8 Melee)
- Utilise **MTGODecklistCache** + **Melee scrapers**
- Pas de données de matchs (estimation basée sur decks)

### Manalytics (Notre analyse)
- **25 tournois** couverts au total
  - 22 avec données de matchs complètes (listener + cache)
  - 3 avec decklists uniquement (cache-only)
- **1,167 matchs réels analysés** (vs 0 pour Jiliac)
- **88% de couverture** avec données complètes

## DIFFÉRENCES CLÉS

### 1. SOURCE DES DONNÉES
**Jiliac** : Utilise uniquement les decklists publiques
- MTGO : Scrape depuis mtgo.com
- Melee : Scrape depuis melee.gg
- **Limitation** : Pas de résultats de matchs

**Manalytics** : Données hybrides
- **Listener MTGO** : Capture en temps réel des matchs
- **Cache local** : Stockage optimisé des decklists
- **Avantage** : Vrais résultats de matchs, pas d'estimations

### 2. TOURNOIS MANQUÉS

**Tournois Jiliac non présents dans notre listener** :
```
- 12801623: Standard Challenge 32 2025-07-03
- 12802789: Standard Challenge 32 2025-07-11
```
→ Mais présents dans notre cache ! Donc couverts.

**Tournois Melee** (8 au total) :
- Jiliac les a tous
- Nous n'en avons aucun dans le listener
- Potentiel d'amélioration pour Manalytics

### 3. TOURNOIS SUPPLÉMENTAIRES

**Nous avons des tournois que Jiliac n'a pas** :
```
- Plusieurs Standard Preliminaries
- Standard Challenge du 20-21 juillet
```

## MÉTRIQUES DE COMPARAISON

| Métrique | Jiliac | Manalytics |
|----------|---------|------------|
| Tournois totaux | 25 | 25 |
| Tournois MTGO | 17 | 25 |
| Tournois Melee | 8 | 0 |
| Matchs analysés | 0 (estimés) | 1,167 (réels) |
| Type d'analyse | Estimation | Données réelles |
| Matrice de matchups | Théorique | Basée sur vrais matchs |

## AVANTAGES DE MANALYTICS

1. **Données réelles vs estimations**
   - Win rates basés sur de vrais matchs
   - Intervalles de confiance précis
   - Pas de biais d'estimation

2. **Granularité**
   - Analyse par round
   - Performance temporelle
   - Détails joueur par joueur

3. **Visualisations avancées**
   - 7 types de graphiques interactifs
   - Données cliquables
   - Export HTML moderne

## AMÉLIORATIONS POSSIBLES

1. **Intégrer Melee**
   - Ajouter un listener Melee
   - Ou au minimum scraper les standings

2. **Couverture à 100%**
   - S'assurer que le listener capture TOUS les tournois MTGO
   - Backup automatique via scraping si manqué

3. **Synchronisation**
   - Aligner notre période d'analyse exactement sur Jiliac
   - Utiliser les mêmes IDs de tournois

## CONCLUSION

**Manalytics offre une analyse supérieure** grâce aux données de matchs réelles, mais pourrait améliorer sa couverture en intégrant les tournois Melee. La combinaison listener + cache nous donne un avantage décisif sur l'analyse purement basée sur les decklists.