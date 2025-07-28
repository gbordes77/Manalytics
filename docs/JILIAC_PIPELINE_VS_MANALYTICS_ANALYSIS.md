# 🔍 Analyse Comparative : Pipeline Jiliac vs Manalytics

## 📊 Vue d'ensemble

Ce document analyse en détail les différences entre notre implémentation actuelle et le pipeline complet de Jiliac.

## 🚨 PROBLÉMATIQUES CRITIQUES IDENTIFIÉES

### 1. **Volume de Données Insuffisant**
- **Manalytics** : 183 matches sur 21 jours (~9 matches/jour)
- **Jiliac** : Probablement 10,000+ matches (inclut les leagues)
- **Impact** : Intervalles de confiance énormes, statistiques non fiables

### 2. **Absence du MTGO Listener**
- **Critique pour** : La matrice de matchups
- **Manque** : Qui a battu qui, round par round
- **Conséquence** : Pas de vraie analyse de matchups

### 3. **Détection d'Archétypes Faible**
- **Taux "Unknown"** : Trop élevé
- **Manque** : Les règles MTGOFormatData
- **Impact** : Métagame mal représenté

## 📋 COMPARAISON DÉTAILLÉE DU PIPELINE

### Step 1: Data Collection

| Composant | Jiliac | Manalytics | Status |
|-----------|---------|------------|---------|
| **mtg_decklist_scrapper** | ✅ Complet | ✅ Implémenté | ✅ OK |
| **MTG_decklistcache** | ✅ Stockage centralisé | ✅ Cache SQLite/JSON | ✅ OK |
| **MTGO-listener** | ✅ Capture matchups live | ❌ Phase 4 planifiée | 🚨 **MANQUANT** |
| **MTGOSDK** | ✅ Pour le listener | ❌ Pas implémenté | 🚨 **MANQUANT** |
| **Données Leagues** | ✅ Incluses | ❌ Exclues | 🚨 **PROBLÈME** |

### Step 2: Data Treatment

| Composant | Jiliac | Manalytics | Status |
|-----------|---------|------------|---------|
| **MTGOArchetypeParser** | ✅ Parser de Badaro | ⚠️ Parser simplifié | ⚠️ **PARTIEL** |
| **MTGOFormatData** | ✅ Règles complètes | ⚠️ 44 règles seulement | 🚨 **INCOMPLET** |
| **Standardisation noms** | ✅ Cohérent | ❌ Incohérent | 🚨 **PROBLÈME** |
| **Validation decks** | ✅ Stricte | ✅ Implémentée | ✅ OK |

### Step 3: Visualization

| Composant | Jiliac | Manalytics | Status |
|-----------|---------|------------|---------|
| **Pie Chart** | ✅ R/ggplot2 | ✅ Plotly | ✅ OK |
| **Bar Chart** | ✅ R/ggplot2 | ✅ Plotly | ✅ OK |
| **Win Rate CI** | ✅ Par matchup | ⚠️ Par deck global | 🚨 **INCORRECT** |
| **Box Plot** | ✅ Distribution réelle | ⚠️ Simulée | ⚠️ **APPROXIMATIF** |
| **Tier Scatter** | ✅ Score complexe | ⚠️ Score simplifié | ⚠️ **DIFFÉRENT** |
| **WR vs Presence** | ✅ 2 versions | ✅ 2 versions | ✅ OK |
| **Matchup Matrix** | ✅ Données réelles | ❌ Placeholder | 🚨 **MANQUANT** |

## 🔧 CE QUI DOIT ÊTRE CORRIGÉ

### PRIORITÉ 1 - CRITIQUE
1. **Inclure les Leagues** (ou au moins une partie)
   - Actuellement : 183 matches
   - Objectif : 5000+ matches minimum

2. **Implémenter le MTGO Listener**
   - Sans ça, pas de vraie analyse de matchups
   - Nécessaire pour la matrice

3. **Améliorer la détection d'archétypes**
   - Intégrer MTGOFormatData complet
   - Réduire le taux d'Unknown < 5%

### PRIORITÉ 2 - IMPORTANT
4. **Standardiser les noms d'archétypes**
   - "Mono White Caretaker" vs "MonoWhite Humans" = même deck
   - Créer un mapping de synonymes

5. **Recalculer les win rates correctement**
   - Par matchup, pas par deck global
   - Nécessite le listener

6. **Augmenter la période d'analyse**
   - 21 jours → 30-60 jours pour plus de données

### PRIORITÉ 3 - AMÉLIORATION
7. **Optimiser les visualisations**
   - Couleurs MTG cohérentes
   - Tooltips plus informatifs
   - Export en haute résolution

8. **Ajouter des métriques supplémentaires**
   - Conversion rate (Day 1 → Top 8)
   - Performance par tournoi type
   - Évolution temporelle

## 📊 MÉTRIQUES DE COMPARAISON

| Métrique | Jiliac (estimé) | Manalytics | Écart |
|----------|----------------|------------|-------|
| Matches analysés | ~10,000 | 183 | -98% |
| Archétypes détectés | ~30-40 | 21 | -40% |
| Taux Unknown | <5% | ~20% | +300% |
| Précision matchups | 95%+ | 0% | -100% |
| Leagues incluses | Oui | Non | ❌ |

## 🎯 PLAN D'ACTION RECOMMANDÉ

### Phase 1 : Données (1 semaine)
- [ ] Inclure les leagues (au moins partiellement)
- [ ] Augmenter la période à 30 jours
- [ ] Améliorer le parser d'archétypes

### Phase 2 : Listener (2-3 semaines)
- [ ] Implémenter MTGO-listener
- [ ] Intégrer MTGOSDK
- [ ] Capturer les vrais matchups

### Phase 3 : Visualisations (1 semaine)
- [ ] Recalculer avec les vraies données
- [ ] Générer la matrice de matchups
- [ ] Affiner les graphiques

## 📝 CONCLUSION

Notre implémentation actuelle est une **preuve de concept** qui démontre la capacité technique, mais elle manque cruellement de :
1. **Volume de données** (98% de moins que Jiliac)
2. **Données de matchups** (0% vs 100%)
3. **Précision d'archétypes** (trop d'Unknown)

Sans ces éléments, nos analyses ne peuvent pas rivaliser avec la qualité de Jiliac.