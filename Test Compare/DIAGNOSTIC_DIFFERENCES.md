# 🔍 DIAGNOSTIC DES DIFFÉRENCES : JILLIAC vs MANALYTICS

## 🚨 **PROBLÈMES CRITIQUES IDENTIFIÉS**

### **1. ❌ ERREUR MAJEURE : Classification d'Archétypes**

**PROBLÈME** : Notre système classifie "Izzet Prowess" comme "Izzet Ramp"

**CAUSE RACINE** :
- **Ordre alphabétique** : `Ramp.json` (R) vient avant `RUGProwess.json` (R) et `URProwess.json` (U)
- **Premier match** : Notre moteur s'arrête au premier archétype qui match
- **Conditions Ramp** : `"OneOrMoreInMainboard": ["Lumra, Bellow of the Woods", "Outcaster Trailblazer"]`
- **Conditions Prowess** : Plus spécifiques mais testées après

**IMPACT** :
- **JILLIAC** : Izzet Prowess (40.1%) - CORRECT
- **MANALYTICS** : Izzet Ramp (32.4%) - INCORRECT

### **2. ❌ PROBLÈME : Période de Données**

**PROBLÈME** : Nous analysons des données futures
- **Période** : 2025-06-13 à 2025-06-24
- **Date actuelle** : 2025-07-15
- **Impact** : Données inexistantes ou incorrectes

### **3. ❌ PROBLÈME : Winrates à 0%**

**PROBLÈME** : Tous les winrates sont à 0% ou très bas
- **Cause** : Erreur dans le calcul des winrates
- **Impact** : Analyses de performance inutilisables

---

## 📊 **COMPARAISON DÉTAILLÉE**

### **Top 5 Archétypes**

| Position | **JILLIAC** | **MANALYTICS** | **Différence** | **Cause** |
|----------|-------------|----------------|----------------|-----------|
| 1 | **Izzet Prowess** : 40.1% | **Izzet Ramp** : 32.4% | ❌ Archétype différent | Ordre alphabétique |
| 2 | **Azorius Omniscience** : 19.6% | **Mono Red Ramp** : 17.0% | ❌ Ordre différent | Classification incorrecte |
| 3 | **Mono Red Aggro** : 12.9% | **Mono Red Aggro** : 14.5% | ✅ Similaire | OK |
| 4 | **Domain** : 4.1% | **Azorius Omniscience** : 10.3% | ❌ Archétype différent | Classification incorrecte |
| 5 | **Golgari Graveyard** : 4.1% | **Dimir Ramp** : 8.7% | ❌ Archétype différent | Classification incorrecte |

---

## 🔧 **SOLUTIONS IDENTIFIÉES**

### **Solution 1 : Priorité des Archétypes**
**PROBLÈME** : Ordre alphabétique des fichiers
**SOLUTION** : Implémenter un système de priorité

```python
# Dans ArchetypeEngine
def load_format_rules(self, format_name: str, format_path: Path):
    # Charger avec priorité
    archetype_priority = {
        "Prowess": 1,  # Haute priorité
        "Ramp": 10,    # Basse priorité
        "Control": 5,
        "Aggro": 3
    }

    # Trier par priorité avant traitement
    sorted_archetypes = sorted(
        archetypes.items(),
        key=lambda x: archetype_priority.get(x[1]["Name"], 100)
    )
```

### **Solution 2 : Conditions Plus Spécifiques**
**PROBLÈME** : Conditions Ramp trop génériques
**SOLUTION** : Rendre les conditions plus spécifiques

```json
// Ramp.json - Conditions plus strictes
{
  "Name": "Ramp",
  "IncludeColorInName": true,
  "Conditions": [
    {
      "Type": "OneOrMoreInMainboard",
      "Cards": ["Lumra, Bellow of the Woods", "Outcaster Trailblazer"]
    },
    {
      "Type": "DoesNotContain",
      "Cards": ["Vivi Ornitier", "Valley Floodcaller"]  // Exclure Prowess
    }
  ]
}
```

### **Solution 3 : Période de Données Réelles**
**PROBLÈME** : Données futures
**SOLUTION** : Utiliser des données réelles

```bash
# Utiliser des données réelles
python run_full_pipeline.py --format Standard --start-date 2024-06-13 --end-date 2024-06-24
```

---

## 📋 **PLAN DE CORRECTION**

### **Phase 1 : Correction Immédiate**
1. **Corriger l'ordre de priorité** des archétypes
2. **Ajouter des exclusions** dans les conditions Ramp
3. **Tester avec données réelles** (2024 au lieu de 2025)

### **Phase 2 : Validation**
1. **Comparer** avec Jilliac sur même période
2. **Valider** la fidélité de classification
3. **Corriger** les winrates

### **Phase 3 : Optimisation**
1. **Améliorer** les conditions d'archétypes
2. **Ajouter** des tests unitaires
3. **Documenter** les règles de priorité

---

## 🎯 **MÉTRIQUES DE SUCCÈS**

### **Objectifs de Correction**
- [ ] **Classification Prowess** : 95%+ de précision
- [ ] **Top 5 archétypes** : Correspondance 80%+ avec Jilliac
- [ ] **Winrates** : Calculs corrects
- [ ] **Données** : Période réelle

### **Indicateurs de Qualité**
- **Shannon Index** : 1.8-2.0 (comme Jilliac)
- **Simpson Index** : 0.6-0.8 (comme Jilliac)
- **Archétypes dominants** : Izzet Prowess > 35%

---

## 🔍 **PROCHAINES ÉTAPES**

1. **Implémenter** le système de priorité des archétypes
2. **Corriger** les conditions Ramp vs Prowess
3. **Tester** avec données réelles
4. **Comparer** avec Jilliac
5. **Valider** la correction

---

*Diagnostic généré le 2025-07-15 21:50*
