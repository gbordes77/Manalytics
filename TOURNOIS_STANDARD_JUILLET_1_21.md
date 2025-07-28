# 📊 Tournois Standard du 1er au 21 Juillet 2025

## 📈 Résumé
- **MTGO** : 47 tournois
- **Melee** : 8 tournois  
- **TOTAL** : 55 tournois

---

## 🎮 MTGO (47 tournois)

- 2025-07-01_standard-challenge-64-2025-07-0112801190
- 2025-07-01_standard-league-2025-07-019382
- 2025-07-02_standard-league-2025-07-029382
- 2025-07-03_standard-challenge-32-2025-07-0312801623
- 2025-07-03_standard-league-2025-07-039382
- 2025-07-04_standard-challenge-32-2025-07-0412801637
- 2025-07-04_standard-challenge-32-2025-07-0412801647
- 2025-07-04_standard-league-2025-07-049382
- 2025-07-05_standard-challenge-32-2025-07-0512801654
- 2025-07-05_standard-challenge-32-2025-07-0512801659
- 2025-07-05_standard-league-2025-07-059382
- 2025-07-06_standard-challenge-32-2025-07-0612801677
- 2025-07-06_standard-league-2025-07-069382
- 2025-07-07_standard-challenge-64-2025-07-0712801688
- 2025-07-07_standard-league-2025-07-079382
- 2025-07-08_standard-challenge-64-2025-07-0812801696
- 2025-07-08_standard-league-2025-07-089382
- 2025-07-09_standard-league-2025-07-099382
- 2025-07-10_standard-challenge-32-2025-07-1012802771
- 2025-07-10_standard-league-2025-07-109382
- 2025-07-11_standard-challenge-32-2025-07-1112802789
- 2025-07-11_standard-challenge-32-2025-07-1112802801
- 2025-07-11_standard-league-2025-07-119382
- 2025-07-11_standard-rc-qualifier-2025-07-1112802761
- 2025-07-12_standard-challenge-32-2025-07-1212802811
- 2025-07-12_standard-challenge-32-2025-07-1212802816
- 2025-07-12_standard-league-2025-07-129382
- 2025-07-13_standard-challenge-32-2025-07-1312802841
- 2025-07-13_standard-league-2025-07-139382
- 2025-07-14_standard-challenge-64-2025-07-1412802856
- 2025-07-14_standard-league-2025-07-149382
- 2025-07-15_standard-challenge-64-2025-07-1512802868
- 2025-07-15_standard-league-2025-07-159382
- 2025-07-16_standard-league-2025-07-169382
- 2025-07-17_standard-challenge-32-2025-07-1712803657
- 2025-07-17_standard-league-2025-07-179382
- 2025-07-18_standard-challenge-32-2025-07-1812803671
- 2025-07-18_standard-challenge-32-2025-07-1812803681
- 2025-07-18_standard-league-2025-07-189382
- 2025-07-19_standard-challenge-32-2025-07-1912803688
- 2025-07-19_standard-challenge-32-2025-07-1912803693
- 2025-07-19_standard-league-2025-07-199382
- 2025-07-20_standard-challenge-32-2025-07-2012803712
- 2025-07-20_standard-league-2025-07-209382
- 2025-07-21_standard-challenge-64-2025-07-2112803723
- 2025-07-21_standard-league-2025-07-219382
- Standard Challenge 32 (12801654)_2025-07-05

## 🎯 Melee (8 tournois)
- 2025-07-02_TheGathering.gg Standard Post-BNR Celebration #2
- 2025-07-02_TheGathering.gg Standard Post-BNR Celebration
- 2025-07-06_F2F Tour Red Deer - Sunday Super Qualifier
- 2025-07-12_Valley Dasher's Bishkek Classic #1
- 2025-07-19_Boa Qualifier #2 2025 (standard)
- 2025-07-06_第2回シングルスター杯　サブイベント
- 2025-07-06_Jaffer's Tarkir Dragonstorm Mosh Pit
- 2025-07-13_Jaffer's Final Fantasy Mosh Pit

---

## 🚨 Analyse du Problème de Matching

### Données Disponibles vs Matchées
- **Tournois scraped** : 55 (47 MTGO + 8 Melee)
- **Tournois Standard dans MTGOData** : 25 
- **Tournois matchés** : 22 seulement
- **Taux de matching** : 88% sur MTGOData, mais seulement 40% sur total scraped

### Raisons Possibles du Faible Matching
1. **Leagues incluses** : 21 leagues MTGO dans les données (à exclure)
2. **IDs non correspondants** : Les IDs entre MTGOData et cache peuvent différer
3. **Tournois manquants dans MTGOData** : Pas tous les tournois sont capturés par le listener
4. **Problème de format de date** : Désynchronisation des dates entre sources

### Tournois Réellement Compétitifs (sans leagues)
- **MTGO Challenges/Qualifiers** : 26 tournois
- **Melee** : 8 tournois
- **TOTAL sans leagues** : 34 tournois

### Impact sur les Données
- Avec seulement 22 tournois sur 34 possibles = **35% de données manquantes**
- Cela explique les 41 matches ridicules (devrait être ~500-1000 matches)

---

## 📂 Tournois Standard dans MTGOData (25 tournois)

### Fichiers présents :
- 2025/07/01/standard-challenge-64-12801190.json
- 2025/07/02/standard-preliminary-12801619.json
- 2025/07/04/standard-challenge-32-12801637.json
- 2025/07/05/standard-challenge-32-12801654.json
- 2025/07/05/standard-challenge-32-12801659.json
- 2025/07/06/standard-challenge-32-12801677.json
- 2025/07/07/standard-challenge-64-12801688.json
- 2025/07/08/standard-challenge-64-12801696.json
- 2025/07/10/standard-challenge-32-12802771.json
- 2025/07/10/standard-preliminary-12802775.json
- 2025/07/10/standard-preliminary-12802782.json
- 2025/07/11/standard-challenge-32-12802801.json
- 2025/07/11/standard-rc-qualifier-12802761.json
- 2025/07/12/standard-challenge-32-12802811.json
- 2025/07/12/standard-challenge-32-12802816.json
- 2025/07/13/standard-challenge-32-12802841.json
- 2025/07/14/standard-challenge-64-12802856.json
- 2025/07/15/standard-challenge-64-12802868.json
- 2025/07/17/standard-challenge-32-12803657.json
- 2025/07/18/standard-challenge-32-12803671.json
- 2025/07/18/standard-challenge-32-12803681.json
- 2025/07/19/standard-challenge-32-12803688.json
- 2025/07/19/standard-challenge-32-12803693.json
- 2025/07/20/standard-challenge-32-12803712.json
- 2025/07/21/standard-challenge-64-12803723.json

### Observations
- **Pas de leagues dans MTGOData** ✅ (seulement Challenges, Preliminaries, Qualifiers)
- **Pas de tournois Melee** ❌ (MTGOData = MTGO uniquement)
- **Manque certains challenges** qui sont dans nos scrapers

---

## 🎯 Analyse des Tournois Melee (>16 joueurs)

### Tournois Melee significatifs (3 sur 8) :
- ✅ **2025-07-06 Jaffer's Tarkir Dragonstorm Mosh Pit** : 91 joueurs
- ✅ **2025-07-06 第2回シングルスター杯　サブイベント** : 53 joueurs  
- ✅ **2025-07-13 Jaffer's Final Fantasy Mosh Pit** : 29 joueurs

### Tournois Melee trop petits (≤16 joueurs) :
- ❌ 2025-07-19 Boa Qualifier #2 : 16 joueurs
- ❌ 2025-07-02 TheGathering.gg Post-BNR #2 : 11 joueurs
- ❌ 2025-07-06 F2F Tour Red Deer : 8 joueurs
- ❌ 2025-07-02 TheGathering.gg Post-BNR : 8 joueurs
- ❌ 2025-07-12 Valley Dasher's Bishkek : 5 joueurs

### Impact
- **Tournois Melee manqués** : 3 gros tournois (173 joueurs total)
- Ces tournois auraient ajouté ~300-500 matches supplémentaires

---

## 📊 Comparaison avec la liste de Jiliac

### Tournois Melee dans la liste de Jiliac (8/8 - TOUS INCLUS) :
1. ✅ **TheGathering.gg Standard Post-BNR Celebration** (2 juillet)
2. ✅ **TheGathering.gg Standard Post-BNR Celebration #2** (2 juillet)
3. ✅ **第2回シングルスター杯　サブイベント** (6 juillet) - 53 joueurs
4. ✅ **Jaffer's Tarkir Dragonstorm Mosh Pit** (6 juillet) - 91 joueurs
5. ✅ **F2F Tour Red Deer - Sunday Super Qualifier** (6 juillet)
6. ✅ **Valley Dasher's Bishkek Classic #1** (12 juillet)
7. ✅ **Jaffer's Final Fantasy Mosh Pit** (13 juillet) - 29 joueurs
8. ✅ **Boa Qualifier #2 2025 (standard)** (19 juillet)

### Observation CRITIQUE :
**Jiliac inclut TOUS les tournois Melee, même ceux avec ≤16 joueurs !**
- Cela explique pourquoi Jiliac a plus de données
- Notre code actuel ne récupère aucun tournoi Melee (MTGOData = MTGO only)
- Nous manquons donc 8 tournois Melee complets

---

## 🎯 Recommandation : Tournois Melee à Retenir

### TOURNOIS À GARDER (≥16 joueurs ou événements qualificatifs) :

1. **✅ Jaffer's Tarkir Dragonstorm Mosh Pit** (6 juillet)
   - 91 joueurs - Gros tournoi communautaire
   - DOIT être inclus

2. **✅ 第2回シングルスター杯　サブイベント** (6 juillet)
   - 53 joueurs - Tournoi japonais significatif
   - DOIT être inclus

3. **✅ Jaffer's Final Fantasy Mosh Pit** (13 juillet)
   - 29 joueurs - Tournoi moyen mais significatif
   - DOIT être inclus

4. **✅ Boa Qualifier #2 2025** (19 juillet)
   - 16 joueurs - Qualifier = compétitif même si petit
   - Devrait être inclus (événement qualificatif)

5. **✅ F2F Tour Red Deer - Sunday Super Qualifier** (6 juillet)
   - 8 joueurs MAIS c'est un Super Qualifier
   - Devrait être inclus (événement qualificatif officiel)

### TOURNOIS À EXCLURE (<16 joueurs ET casual) :

6. **❌ TheGathering.gg Post-BNR Celebration** (2 juillet)
   - 8 joueurs - Trop petit et casual

7. **❌ TheGathering.gg Post-BNR Celebration #2** (2 juillet)
   - 11 joueurs - Trop petit et casual

8. **❌ Valley Dasher's Bishkek Classic #1** (12 juillet)
   - 5 joueurs - Beaucoup trop petit

### Résumé des critères de sélection :
- **Inclure si** : ≥16 joueurs OU événement qualificatif/officiel
- **Exclure si** : <16 joueurs ET tournoi casual
- **Total recommandé** : 5 tournois sur 8
