# 🚨 RÈGLES ABSOLUES DE DEBUG - PROJET MANALYTICS

## 📋 RÈGLE FONDAMENTALE

**QUAND QUELQUE CHOSE NE MARCHE PAS COMME CHEZ JILLIAC/FBETTEGA :**

### ❌ INTERDIT
- ❌ Faire des suppositions
- ❌ Faire des investigations aveugles
- ❌ Tester des URLs au hasard
- ❌ Inventer des méthodes

### ✅ OBLIGATOIRE
1. **ALLER DIRECTEMENT SUR LES GITHUB PUBLICS**
2. **LIRE LE CODE SOURCE RÉEL**
3. **COPIER LA MÉTHODE EXACTE**

## 🔗 GITHUB DE RÉFÉRENCE OBLIGATOIRES

### Jilliac (Maintainer principal)
- **MTGODecklistCache** : `https://github.com/Jiliac/MTGODecklistCache`
- **MTGO-listener** : `https://github.com/Jiliac/MTGO-listener`
- **R-Meta-Analysis** : `https://github.com/Jiliac/R-Meta-Analysis`

### Fbettega (Scraping)
- **mtg_decklist_scrapper** : `https://github.com/fbettega/mtg_decklist_scrapper`
- **MTG_decklistcache** : `https://github.com/fbettega/MTG_decklistcache`

### Badaro (Classification & Parsing)
- **MTGOArchetypeParser** : `https://github.com/Badaro/MTGOArchetypeParser`
- **MTGOFormatData** : `https://github.com/Badaro/MTGOFormatData`
- **MTGODecklistCache.Tools** : `https://github.com/Badaro/MTGODecklistCache.Tools` (⚠️ Retired)

### Videre Project (SDK)
- **MTGOSDK** : `https://github.com/videre-project/MTGOSDK`

### Aliquanto3 (Analyse statistique)
- **R-Meta-Analysis** : `https://github.com/Aliquanto3/R-Meta-Analysis` (⚠️ Aliquanto left)

## 🎯 WORKFLOW OBLIGATOIRE

### Étape 1 : Identifier le problème
- Quel composant ne fonctionne pas ?
- Quel repository correspond ?

### Étape 2 : Cloner le repository
```bash
git clone https://github.com/[owner]/[repo].git temp_[repo]
```

### Étape 3 : Analyser le code
- Lire les fichiers principaux
- Identifier les méthodes utilisées
- Noter les endpoints/APIs/paramètres

### Étape 4 : Reproduire exactement
- Copier la méthode
- Utiliser les mêmes paramètres
- Respecter la même logique

### Étape 5 : Tester avec les vraies données
- Utiliser les mêmes périodes de test
- Vérifier les résultats

## 📚 EXEMPLES D'APPLICATION

### Exemple 1 : Problème Melee API
❌ **Mauvaise approche** : Tester `https://melee.gg/api/tournaments`
✅ **Bonne approche** :
1. Cloner `fbettega/mtg_decklist_scrapper`
2. Lire `Client/MtgMeleeClientV2.py`
3. Découvrir `https://melee.gg/Decklist/SearchDecklists` avec payload DataTables
4. Reproduire exactement

### Exemple 2 : Problème Classification
❌ **Mauvaise approche** : Inventer des règles d'archétypes
✅ **Bonne approche** :
1. Cloner `Badaro/MTGOArchetypeParser`
2. Lire `ArchetypeAnalyzer.cs`
3. Reproduire la logique en Python

### Exemple 3 : Problème Analyse Statistique
❌ **Mauvaise approche** : Créer ses propres métriques
✅ **Bonne approche** :
1. Cloner `Jiliac/R-Meta-Analysis`
2. Lire les scripts R
3. Porter en Python avec les mêmes formules

## ⚡ GAINS DE CETTE APPROCHE

- **Temps** : 10x plus rapide que les suppositions
- **Fiabilité** : 100% compatible avec l'écosystème existant
- **Maintenance** : Évite les bugs et incompatibilités
- **Apprentissage** : Comprendre les vraies méthodes

## 🚨 SANCTIONS

**Si cette règle n'est pas respectée :**
- Perte de temps considérable
- Code incompatible avec l'écosystème
- Bugs difficiles à déboguer
- Frustration de l'équipe

## ✅ VALIDATION

**Avant de dire "ça ne marche pas" :**
1. ✅ J'ai cloné le repository correspondant
2. ✅ J'ai lu le code source
3. ✅ J'ai reproduit la méthode exacte
4. ✅ J'ai testé avec les mêmes paramètres

**Seulement après ces 4 étapes, on peut investiguer plus loin.**

---

*Cette règle est ABSOLUE et NON-NÉGOCIABLE pour le projet Manalytics.*
