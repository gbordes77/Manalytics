# 📊 RÉSUMÉ MÉTRIQUES - MANALYTICS vs JILLIAC

## 🎯 **PÉRIODE ANALYSÉE**
**2025-06-13 à 2025-06-24** (Standard)

---

## 📈 **MÉTRIQUES MANALYTICS**

### **Données Brutes**
- **Tournois** : 57
- **Decks** : 1,103 (502 doublons supprimés)
- **Archétypes uniques** : 33
- **Sources** : 4 (melee.gg, mtgo.com League/Challenge/General)

### **Indices de Diversité**
- **Shannon** : 1.754
- **Simpson** : 0.690
- **Archétypes effectifs** : 5.78
- **Herfindahl (concentration)** : 0.310
- **Équité** : 0.502

### **Top 5 Archétypes (Metagame Share)**
1. **Izzet Ramp** : 32.42% (378 decks)
2. **Azorius Omniscience** : 13.42% (148 decks)
3. **Mono Red Aggro** : 9.81% (115 decks)
4. **Mono Red Ramp** : 8.45% (110 decks)
5. **Dimir Ramp** : 5.71% (66 decks)

---

## 🎮 **ANALYSE MTGO SEULE**

### **Données MTGO**
- **Archétypes MTGO** : 17
- **Top MTGO** :
  1. **Izzet Ramp** : 30.69% (145 decks)
  2. **Mono Red Aggro** : 13.79% (65 decks)
  3. **Mono Red Ramp** : 13.45% (76 decks)
  4. **Azorius Omniscience** : 10.69% (46 decks)
  5. **Dimir Ramp** : 8.97% (39 decks)

---

## 🔍 **POINTS DE COMPARAISON AVEC JILLIAC**

### **À Vérifier**
- [ ] **Shannon Index** : 1.754 vs Jilliac (attendu ~1.8-2.0)
- [ ] **Simpson Index** : 0.690 vs Jilliac (attendu ~0.6-0.8)
- [ ] **Top Archétypes** : Izzet Ramp dominant (cohérent avec métagame Standard)
- [ ] **Classification** : 33 archétypes vs Jilliac (attendu ~20-40)
- [ ] **Sources** : Multi-sources vs MTGO seul (avantage Manalytics)

### **Avantages Manalytics**
- ✅ **Multi-sources** : MTGO + Melee + TopDeck (vs MTGO seul)
- ✅ **Déduplication** : 502 doublons supprimés automatiquement
- ✅ **Analyses avancées** : Clustering, corrélations, tendances
- ✅ **Visualisations** : 14 graphiques vs 6-8 Jilliac
- ✅ **Dashboard** : Navigation complète, pages par archétype

### **Points d'Amélioration**
- ⚠️ **Winrates** : Problème de calcul (tous à 0% ou très bas)
- ⚠️ **Données récentes** : 2025-06-13 à 2025-06-24 (futur)
- ⚠️ **Bug JSON** : Erreur dans export advanced_analysis.json

---

## 📋 **CHECKLIST COMPARAISON**

### **Fidélité Reproduction**
- [ ] Classification archétypes identique à MTGOArchetypeParser
- [ ] Intégration couleurs conforme à Aliquanto3
- [ ] Calculs statistiques équivalents à R-Meta-Analysis
- [ ] Visualisations standards MTGGoldfish/17lands

### **Améliorations**
- [ ] Performance pipeline (vitesse)
- [ ] Qualité des données (winrates)
- [ ] UX/UI (interactivité)
- [ ] Analyses ML (détection automatique)

---

## 🎯 **PROCHAINES ACTIONS**

1. **Comparer** avec données Jilliac réelles
2. **Corriger** bug winrates
3. **Valider** fidélité classification
4. **Optimiser** performance
5. **Ajouter** fonctionnalités avancées

---

*Généré le 2025-07-15 21:45*
