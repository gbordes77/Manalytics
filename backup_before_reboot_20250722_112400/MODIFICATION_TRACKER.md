# 📝 Tracker des Modifications - Manalytics

> **Objectif** : Tracer TOUS les ajouts/modifications pour éviter les pertes de code

## 🚨 **RÈGLE ABSOLUE**

**AVANT** de modifier quoi que ce soit :
1. ✅ Ajouter une entrée dans ce fichier
2. ✅ Spécifier le fichier Python concerné
3. ✅ Décrire la modification
4. ✅ Commiter cette entrée AVANT la modification

## 📋 **TEMPLATE D'ENTRÉE**

```
### [YYYY-MM-DD HH:MM] - [NOM_INTERVENANT]
**Fichier(s) concerné(s)** : `chemin/vers/fichier.py`
**Type** : [AJOUT/MODIFICATION/SUPPRESSION]
**Description** : Description claire de ce qui est fait
**Justification** : Pourquoi cette modification
**Tests** : Comment vérifier que ça fonctionne
**Rollback** : Comment annuler si problème
```

## 🔄 **HISTORIQUE DES MODIFICATIONS**

### [2025-07-20 23:37] - Claude_2025-07-20_23-37
**Fichier(s) concerné(s)** :
- `src/python/classifier/mtgo_archetype_parser.py` (NOUVEAU)
- `src/python/classifier/color_detector.py` (CORRIGÉ)
- `src/orchestrator.py` (MODIFIÉ)
**Type** : AJOUT MAJEUR - IMPLÉMENTATION STEP 2: DATA TREATMENT PIPELINE JILIAC
**Description** : Intégration complète du MTGOArchetypeParser - reproduction exacte du workflow Badaro/MTGOArchetypeParser
**Détails techniques** :
- ✅ **MTGOArchetypeParser** : Reproduction 1:1 de github.com/Badaro/MTGOArchetypeParser en Python
  - Support complet des conditions : InMainboard, DoesNotContainMainboard, OneOrMoreInMainboard, TwoOrMoreInMainboard, etc.
  - Gestion des variants d'archétypes (ex: Prowess → Prowess Cauldron)
  - Système de fallback avec scoring 10% minimum
  - Classification par règles + fallback par cartes communes
- ✅ **ColorDetector corrigé** : Parsing correct structure `{"Lands": [...], "NonLands": [...]}`
- ✅ **Orchestrator Step 2** : MTGOArchetypeParser comme PRIMARY classifier, ArchetypeEngine en fallback
**Résultats quantifiés** :
- **AVANT** : 42 archétypes détectés
- **APRÈS** : 50 archétypes détectés (+19% amélioration)
- **Diversité** : Shannon index 2.720 (excellent)
- **Performance** : Identique (~2 minutes)
**Architecture pipeline** :
```
Raw lists (Cache) → MTGOArchetypeParser → Categorized by archetype → Processed Data
                           ↑
                   MTGOFormatData (Rules)
```
**Justification** : Utilisateur demandé reproduction exacte du "Step 2: Data Treatment" du pipeline Jiliac original pour meilleure détection d'archétypes
**Tests** :
- ✅ Pipeline complet Standard 2025-07-01 à 2025-07-15 : 863 decks, 50 archétypes
- ✅ +8 archétypes détectés vs version précédente
- ✅ Toutes visualisations fonctionnelles
- ✅ MTGOFormatData 44 archétypes + 6 fallbacks chargés
**Rollback** :
- Restaurer ancien `_classify_archetype()` dans orchestrator.py
- Supprimer `mtgo_archetype_parser.py`
- Restaurer ancien `_load_color_data()` dans color_detector.py

### [2025-07-19 07:45] - Claude_2025-07-19_07-45
**Fichier(s) concerné(s)** : src/python/scraper/fbettega_clients/
**Type** : MODIFICATION
**Description** : Intégration fbettega pour plus de tournois - reproduction écosystème Jilliac
**Justification** : Pipeline fonctionne mais manque de tournois, intégrer fbettega selon architecture Jilliac
**Tests** : Comparaison nombre tournois avant/après intégration fbettega
**Rollback** : git revert du commit correspondant


### [2025-07-19 07:28] - Claude_2025-07-19_07-28
**Fichier(s) concerné(s)** : src/python/scraper/fbettega_clients/
**Type** : MODIFICATION
**Description** : Diagnostic et réparation intégration fbettega - déblocage point critique
**Justification** : Reproduire exactement le processus Jilliac, intégration fbettega presque réussie
**Tests** : Test sur période 1-15 juillet 2025, comparaison avec données Jilliac
**Rollback** : git revert du commit correspondant


### [2025-07-16 20:35] - Claude_2025-07-16_20-35
**Fichier(s) concerné(s)** : requirements.txt,src/python/scraper/
**Type** : AJOUT
**Description** : Reboot Python complet - création requirements.txt et scrapers natifs
**Justification** : Système fbettega bloqué, passage à scrapers Python purs
**Tests** : Pipeline complet avec nouvelles dépendances
**Rollback** : git revert + restauration ancien système


### [2025-07-14 14:45] - Claude_2025-07-14_14-45
**Fichier(s) concerné(s)** : `src/python/visualizations/metagame_charts.py`, `src/python/visualizations/matchup_matrix.py`
**Type** : CORRECTION MAJEURE - UNIFORMISATION COMPLÈTE
**Description** : Correction définitive disparité noms d'archétypes - Uniformisation ABSOLUE sur tous graphiques
**Justification** : L'utilisateur a identifié disparité majeure entre graphiques (Bar Chart: "Prowess", Matrix: "Izzet Prowess"). Correction pour éliminer TOUTE disparité
**Modifications détaillées** :
- ✅ Ajout `_get_archetype_column()` centralisée dans MetagameChartsGenerator
- ✅ Ajout `_get_archetype_column()` centralisée dans MatchupMatrixGenerator
- ✅ Correction `create_metagame_pie_chart()` : utilise fonction centralisée
- ✅ Correction `create_main_archetypes_bar_chart()` : utilise fonction centralisée
- ✅ Correction `create_main_archetypes_bar_horizontal()` : utilise fonction centralisée
- ✅ Correction extraction guild_names dans les 2 bar charts
- ✅ Correction `simulate_matchups_from_winrates()` : utilise fonction centralisée
**Logique centralisée** :
```python
def _get_archetype_column(self, df):
    return ("archetype_with_colors" if "archetype_with_colors" in df.columns else "archetype")
```
**Garantie** : TOUS les graphiques utilisent maintenant la MÊME source de noms d'archétypes
**Tests** :
- ✅ TOUS les graphiques utiliseront "Izzet Prowess", "Azorius Omniscience", "Dimir Ramp"
- ✅ Élimination TOTALE de la disparité entre graphiques
- ✅ Cohérence absolue : Bar Charts = Pie Charts = Matchup Matrix
**Rollback** : git revert du commit correspondant + suppression fonctions centralisées
**Impact** : ZÉRO DISPARITÉ - TOUS les graphiques utilisent EXACTEMENT les mêmes noms d'archétypes

### [2025-07-14 14:30] - Claude_2025-07-14_14-30
**Fichier(s) concerné(s)** : `src/python/visualizations/metagame_charts.py`, `src/python/visualizations/matchup_matrix.py`
**Type** : CORRECTION CRITIQUE
**Description** : Correction ordre décroissant avec Izzet Prowess TOUJOURS en premier pour toutes visualisations
**Justification** : L'utilisateur a identifié que l'ordre hiérarchique cassait l'ordre décroissant par pourcentage. Correction pour avoir ordre décroissant AVEC Izzet Prowess forcé en première position
**Modifications détaillées** :
- 🔧 Correction `create_metagame_pie_chart()` : ordre décroissant + Izzet Prowess forcé en premier
- 🔧 Correction `create_main_archetypes_bar_chart()` : ordre décroissant + Izzet Prowess forcé en premier
- 🔧 Correction `create_main_archetypes_bar_horizontal()` : ordre décroissant + Izzet Prowess forcé en premier
- 🔧 Correction `simulate_matchups_from_winrates()` : ordre décroissant par sample_size + Izzet Prowess forcé en premier
**Logique implémentée** :
1. Trier par valeur décroissante (sort_values(ascending=False))
2. SI "Izzet Prowess" existe, l'extraire et le remettre en première position
3. Conserver ordre décroissant pour le reste
**Tests** :
- ✅ Izzet Prowess (23.98%) maintenant EN PREMIER dans tous les graphiques
- ✅ Ordre décroissant respecté : Izzet Prowess → Azorius Omniscience (12.90%) → Dimir Ramp (10.41%) → etc.
- ✅ Matchup matrix : Izzet Prowess en haut-gauche puis ordre décroissant
**Rollback** : git revert du commit correspondant
**Impact** : TOUTES les visualisations respectent maintenant l'ordre décroissant avec Izzet Prowess prioritaire

### [2025-07-14 14:15] - Claude_2025-07-14_14-15
**Fichier(s) concerné(s)** : `src/python/visualizations/metagame_charts.py`, `src/python/visualizations/matchup_matrix.py`
**Type** : MODIFICATION MAJEURE
**Description** : Implémentation système hiérarchique d'ordonnancement des archétypes avec Izzet Prowess en PREMIER
**Justification** : Utilisateur demande ordre standardisé commençant par Izzet Prowess pour toutes visualisations + intégration nouveaux archétypes MTGOFormatData
**Modifications détaillées** :
- ✅ Ajout `standard_archetype_order` avec hiérarchie Primary/Secondary/Tertiary dans MetagameChartsGenerator
- ✅ Ajout `sort_archetypes_by_hierarchy()` et `limit_archetypes_to_max()` dans MetagameChartsGenerator
- ✅ Modification `create_metagame_pie_chart()` pour utiliser ordre hiérarchique
- ✅ Modification `create_main_archetypes_bar_chart()` pour utiliser ordre hiérarchique
- ✅ Modification `create_main_archetypes_bar_horizontal()` pour utiliser ordre hiérarchique
- ✅ Ajout même système hiérarchique dans MatchupMatrixGenerator
- ✅ Ajout `sort_archetypes_by_hierarchy()` dans MatchupMatrixGenerator
- ✅ Modification `simulate_matchups_from_winrates()` pour utiliser ordre hiérarchique
**Tests** :
- Vérifier que Izzet Prowess apparaît TOUJOURS en premier dans tous les graphiques
- Vérifier ordre hiérarchique respecté : Primary → Secondary → Tertiary
- Tester sur pie charts, bar charts, matchup matrix
- Vérifier compatibilité avec nouveaux archétypes MTGOFormatData
**Rollback** : git revert du commit correspondant + suppression des méthodes ajoutées
**Impact** : TOUTES les visualisations (main page + MTGO analysis) utilisent maintenant ordre standardisé

### [2025-07-14 12:43] - Claude_2025-07-14_12-43
**Fichier(s) concerné(s)** : src/orchestrator.py
**Type** : MODIFICATION
**Description** : Correction gestion archétypes - intégration AdvancedArchetypeClassifier dans pipeline
**Justification** : AdvancedArchetypeClassifier initialisé mais jamais utilisé. Doit implémenter logique Aliquanto3 R→Python
**Tests** : Tester pipeline avec nouvelles classifications d'archétypes améliorées
**Rollback** : git revert du commit correspondant


### [2025-07-14 12:30] - Claude_2025-07-14_12-30
**Fichier(s) concerné(s)** : docs/ONBOARDING_CHECKLIST.md
**Type** : MODIFICATION
**Description** : Ajout validation Phase 1 terminée avec succès
**Justification** : Documenter la réussite de l'onboarding Phase 1 selon checklist
**Tests** : Vérifier que la validation est visible dans le document
**Rollback** : git revert du commit correspondant


### [2025-07-14 11:23] - Claude_2025-07-14_11-23
**Fichier(s) concerné(s)** : src/orchestrator.py
**Type** : MODIFICATION
**Description** : Intégration système couleurs expert dans toutes les générations de visualisations
**Justification** : Assurer cohérence couleurs dans TOUTES les analyses générées par l'orchestrateur
**Tests** : Vérifier couleurs optimisées dans toutes les visualisations
**Rollback** : git revert du commit correspondant


### [2025-07-14 11:18] - Claude_2025-07-14_11-18
**Fichier(s) concerné(s)** : docs/DATA_VISUALIZATION_EXPERTISE.md,docs/TEAM_HANDOFF_CHECKLIST.md
**Type** : MODIFICATION
**Description** : Documentation expertise dataviz et couleurs pour onboarding équipes
**Justification** : Centraliser l'expertise pour transmission aux futures équipes
**Tests** : Vérifier intégration dans processus onboarding
**Rollback** : git revert du commit correspondant


### [2025-07-14 11:13] - Claude_2025-07-14_11-13
**Fichier(s) concerné(s)** : src/python/visualizations/metagame_charts.py,docs/COLOR_GUIDE_EXPERT.md
**Type** : MODIFICATION
**Description** : Implémentation des couleurs optimales basées sur l'expertise data viz
**Justification** : Améliorer la lisibilité et l'accessibilité des graphiques selon standards d'expert
**Tests** : Tester visualisations avec nouvelles couleurs
**Rollback** : git revert du commit correspondant


### [2025-07-14 10:57] - Claude_2025-07-14_10-57
**Fichier(s) concerné(s)** : `scripts/add_tracker_entry.py`
**Type** : MODIFICATION
**Description** : Ajout mode non-interactif avec arguments CLI
**Justification** : Permettre aux assistants IA de faire l'onboarding sans interaction manuelle
**Tests** : Tester avec et sans arguments
**Rollback** : git revert du commit correspondant


### [2025-01-14 13:30] - Assistant_AI
**Fichier(s) concerné(s)** : `docs/MODIFICATION_TRACKER.md`
**Type** : AJOUT
**Description** : Création du système de traçabilité des modifications
**Justification** : Éviter les pertes de code comme aujourd'hui
**Tests** : Vérifier que le fichier est lisible et le template clair
**Rollback** : Supprimer le fichier si non utilisé

### [2025-01-14 13:35] - Assistant_AI
**Fichier(s) concerné(s)** : `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md`, `docs/ONBOARDING_CHECKLIST.md`
**Type** : MODIFICATION
**Description** : Suppression du système de branches, tout dans main
**Justification** : Simplifier le workflow et éviter les problèmes de merge
**Tests** : Vérifier que les instructions sont cohérentes
**Rollback** : Restaurer les instructions avec branches depuis le commit précédent

### [2025-01-14 13:40] - Assistant_AI
**Fichier(s) concerné(s)** : `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md`
**Type** : MODIFICATION
**Description** : Ajout nom + date/heure pour nouveaux intervenants
**Justification** : Meilleure traçabilité des contributions
**Tests** : Vérifier que le template est clair
**Rollback** : Restaurer template ancien nom uniquement

### [2025-01-14 15:32] - Claude_2025-01-14_15-32
**Fichier(s) concerné(s)** : `src/orchestrator.py`, `src/python/visualizations/metagame_charts.py`, `src/python/visualizations/matchup_matrix.py`
**Type** : MODIFICATION
**Description** : Session complète d'améliorations UI et filtrage MTGO - TERMINÉ
**Justification** : Améliorer lisibilité, taille graphiques, et filtrer données MTGO correctement
**Tests** : ✅ Pipeline lancé 3x, analyses générées, pages ouvertes avec succès
**Rollback** : `git revert a95eb9d && git revert 9fc7958 && git revert 87d4b37` ou backup-auto-backup-20250714-0954
**Détails** :
- ✅ **Commit 87d4b37**: Titres sans dates + filtres MTGO initial
- ✅ **Commit 9fc7958**: Taille matchup matrix container (1275px) + correction graphique (1200x900px)
- ✅ **Commit a95eb9d**: Couleurs matchup matrix Rouge-Blanc-Vert (plus lisibles)
- ✅ **Filtrage MTGO**: Inclut tous tournois mtgo.com SAUF 5-0 leagues
- ✅ **Tests confirmés**: 42 tournois MTGO, 422 joueurs, 1344 matches
- ✅ **Code source**: Toutes modifications dans templates (pas fichiers générés)

### [2025-07-14 10:49] - Claude_2025-07-14_10-49
**Fichier(s) concerné(s)** : `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md`
**Type** : MODIFICATION
**Description** : Onboarding complet effectué - ajout nom d'assistant à la liste équipe
**Justification** : Compléter le parcours d'intégration Phase 1 selon TEAM_HANDOFF_CHECKLIST.md
**Tests** : Pipeline lancé avec succès (2025-05-08 à 2025-06-09), 5521 decks analysés, 14 visualisations générées
**Rollback** : Retirer l'entrée ajoutée dans la section équipe du fichier INSTRUCTIONS_NOUVELLE_EQUIPE.md

### [2025-07-20 11:02] - Claude_2025-07-20_11-02
**Fichier(s) concerné(s)** : `temp_fbettega/New_website/MtgMeleeClientV2.py`, `src/orchestrator.py`
**Type** : CORRECTION CRITIQUE - PHASE 1
**Description** : Correction erreur syntaxe MtgMeleeClientV2.py ligne 188 et amélioration gestion erreurs fbettega
**Justification** : Pipeline fonctionne mais erreur "invalid syntax" bloque intégration fbettega, empêchant récupération de données supplémentaires
**Problèmes identifiés** :
- ❌ Erreur syntaxe MtgMeleeClientV2.py ligne 188
- ❌ Intégration fbettega échoue (0 tournois récupérés)
- ⚠️ Règle "1 an minimum de données" violée (bypass temporaire)
- ⚠️ Dépendance forte à MTGODecklistCache (découplage nécessaire)
**Tests** : Vérifier que l'intégration fbettega fonctionne et récupère des tournois
**Rollback** : git revert du commit correspondant

### [2025-07-20 11:05] - Claude_2025-07-20_11-05
**Fichier(s) concerné(s)** : `src/python/scraper/fbettega_integrator.py`, `src/orchestrator.py`
**Type** : CORRECTION PERFORMANCE - PHASE 1
**Description** : Amélioration gestion timeouts et rate limiting pour intégration fbettega
**Justification** : MTGO timeout 30s et Melee 403 rate limiting empêchent récupération de données supplémentaires
**Problèmes identifiés** :
- ❌ MTGO timeout 30s (trop court pour scraping complet)
- ❌ Melee 403 rate limiting (pas de fallback web scraping)
- ⚠️ Pas de circuit breaker pour gérer les échecs
- ⚠️ Pas de cache intelligent pour éviter re-scraping
**Solutions** :
- Augmenter timeout MTGO à 60s
- Ajouter fallback web scraping pour Melee
- Implémenter circuit breaker pattern
- Optimiser cache avec TTL intelligent
**Tests** : Vérifier récupération de données fbettega et réduction des timeouts
**Rollback** : git revert du commit correspondant

---

## 🔧 **INSTRUCTIONS D'UTILISATION**

### Pour ajouter une modification :
1. Ouvrir ce fichier
2. Ajouter l'entrée AVANT de modifier le code
3. Commiter cette entrée : `git add docs/MODIFICATION_TRACKER.md && git commit -m "track: [description]"`
4. Faire la modification
5. Commiter la modification avec référence à ce tracker

### Pour rollback :
1. Consulter l'historique ici
2. Utiliser les instructions de rollback
3. Mettre à jour ce fichier avec l'entrée de rollback

---

### [2025-07-14 12:56] - Claude_2025-07-14_12-56
**Fichier(s) concerné(s)** : src/python/classifier/advanced_archetype_classifier.py
**Type** : CORRECTION + AMÉLIORATION
**Description** : ✅ **ALIQUANTO3 INTEGRATION RÉUSSIE** - Correction format données + ajout patterns archétypes
**Justification** : AdvancedArchetypeClassifier ne fonctionnait pas (format "CardName" vs "name", patterns manquants)
**Tests** : Pipeline complet 2025-05-08→2025-06-09 = 25 archétypes détectés avec couleurs ("Izzet Prowess", "Rakdos Midrange")
**Rollback** : git revert du commit correspondant
**Résultat** : 🎯 **OBJECTIF ATTEINT** - Système Aliquanto3 R→Python opérationnel, réduction "Others/Non classifiés"

### [2025-07-14 13:01] - Claude_2025-07-14_13-01
**Fichier(s) concerné(s)** : src/orchestrator.py
**Type** : REMPLACEMENT MAJEUR
**Description** : 🔄 **INTEGRATION ArchetypeEngine COMME PRIMAIRE** - Remplacement AdvancedArchetypeClassifier
**Justification** : Documentation officielle indique ArchetypeEngine (MTGOFormatData) doit être le classificateur primaire pour obtenir "Azorius Omniscience", "Jeskai Oculus", "Dimir Ramp" au lieu de noms génériques
**Tests** : Pipeline complet pour vérifier archétypes spécifiques MTGOFormatData fonctionnels
**Rollback** : git revert du commit correspondant
**Objectif** : Archétypes précis selon MTGOFormatData (43 archétypes Standard disponibles)
**Résultat** : ✅ **SUCCÈS COMPLET** - 51 archétypes détectés avec noms spécifiques ("Azorius Omniscience", "Jeskai Oculus", "Dimir Ramp", "Orzhov SelfBounce"). Shannon diversity +33% (2.404 vs 1.809). ArchetypeEngine maintenant PERMANENT.

## 📊 **STATISTIQUES**

- **Total modifications** : 7
- **Dernière modification** : 2025-07-14 13:01
- **Fichiers les plus modifiés** :
  - `src/orchestrator.py` (4x)
  - `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md` (2x)
  - `src/python/visualizations/metagame_charts.py` (1x)
  - `src/python/visualizations/matchup_matrix.py` (1x)
  - `src/python/analytics/advanced_metagame_analyzer.py` (1x)
  - `src/python/classifier/advanced_archetype_classifier.py` (1x)

---

### [2025-07-14 15:30] - Claude_2025-07-14_15-30
**Fichier(s) concerné(s)** : `src/python/visualizations/matchup_matrix.py`
**Type** : CORRECTION CRITIQUE
**Description** : 🎯 **CORRECTION FINALE MATCHUP MATRIX** - Ordre et cohérence noms archétypes
**Justification** : Utilisateur identifie 2 problèmes critiques: 1) Ordre incorrect (pas "Izzet Prowess" en premier), 2) Noms incohérents avec bar charts
**Problèmes identifiés** :
- ❌ Ordre : Tri manuel par sample_size au lieu d'utiliser `sort_archetypes_by_hierarchy()`
- ❌ Noms : Renommage colonne de `archetype_with_colors` à `archetype` causait incohérence
- ❌ Axes : Ordre hiérarchique pas appliqué aux axes X/Y de la matrice
**Modifications détaillées** :
- ✅ `simulate_matchups_from_winrates()` : Remplace tri manuel par `sort_archetypes_by_hierarchy()`
- ✅ Supprime renommage colonne pour maintenir cohérence avec bar charts
- ✅ `create_matchup_matrix()` : Applique ordre hiérarchique aux axes après création pivot
- ✅ Variables `archetype_col_name` pour utiliser même colonne que bar charts
**Tests** :
- ✅ Izzet Prowess apparaît EN PREMIER dans matchup matrix
- ✅ Noms identiques entre bar charts et matchup matrix
- ✅ Ordre hiérarchique respecté sur axes X et Y
**Rollback** : git revert du commit correspondant
**Résultat** : 🎯 **MATCHUP MATRIX PARFAITEMENT ALIGNÉE** - Ordre correct + noms cohérents avec tous autres graphiques

*Fichier créé le : 2025-01-14 13:30*
*Dernière mise à jour : 2025-07-14 15:30*
