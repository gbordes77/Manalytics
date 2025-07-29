# 🚨 PLAN DE RESTRUCTURATION URGENTE - MANALYTICS

**Date**: 29/07/2025  
**Priorité**: CRITIQUE  
**Objectif**: Résoudre le chaos architectural pour permettre la reproduction des résultats Jiliac

## 🎯 STRATÉGIE : "CONSOLIDATION PROGRESSIVE"

Au lieu de tout casser, nous allons **identifier et consolider** progressivement.

## 📋 PHASE 1 : IDENTIFICATION DES SCRIPTS DE RÉFÉRENCE (IMMÉDIAT)

### 1.1 Créer le Fichier de Référence Officiel

```bash
# Créer le guide officiel
touch SCRIPTS_OFFICIELS.md
```

### 1.2 Tester les Scripts Candidats

#### Test A : Script Jiliac Method
```bash
python analyze_july_jiliac_method.py > test_jiliac_method.txt 2>&1
```

#### Test B : Script Complete Final  
```bash
python analyze_july_complete_final.py > test_complete_final.txt 2>&1
```

#### Test C : Script All 6 Visualizations
```bash
python analyze_july_all_6_visualizations.py > test_all_6_viz.txt 2>&1
```

### 1.3 Comparer les Résultats
```bash
# Voir quel script donne les résultats les plus proches de Jiliac
grep -i "izzet" test_*.txt
grep -i "dimir" test_*.txt
```

## 📋 PHASE 2 : CONSOLIDATION IMMÉDIATE (AUJOURD'HUI)

### 2.1 Créer le Dossier de Référence
```bash
mkdir -p reference_scripts/
```

### 2.2 Identifier et Copier les Scripts de Référence
```bash
# Une fois identifiés, copier les bons scripts
cp analyze_july_jiliac_method.py reference_scripts/analyze_reference.py
cp scrape_all.py reference_scripts/scrape_reference.py  
cp visualize_standard.py reference_scripts/visualize_reference.py
```

### 2.3 Créer des Alias Simples
```bash
# Créer des scripts simples à la racine
echo "python reference_scripts/analyze_reference.py" > analyze.sh
echo "python reference_scripts/scrape_reference.py" > scrape.sh
echo "python reference_scripts/visualize_reference.py" > visualize.sh
chmod +x *.sh
```

## 📋 PHASE 3 : NETTOYAGE PROGRESSIF (CETTE SEMAINE)

### 3.1 Créer les Dossiers d'Archive
```bash
mkdir -p _archive/
mkdir -p _archive/analyze_scripts/
mkdir -p _archive/scrape_scripts/
mkdir -p _archive/obsolete_structure/
```

### 3.2 Archiver les Scripts Non-Référence
```bash
# Déplacer tous les scripts sauf les références
mv analyze_july_*.py _archive/analyze_scripts/ 
mv scrape_*.py _archive/scrape_scripts/
# Garder seulement les références
```

### 3.3 Documenter les Choix
```bash
# Créer un log des décisions
echo "Scripts archivés le $(date)" > _archive/ARCHIVE_LOG.md
echo "Raison: Consolidation architecture" >> _archive/ARCHIVE_LOG.md
```

## 📋 PHASE 4 : STANDARDISATION (SEMAINE PROCHAINE)

### 4.1 Migration vers src/manalytics/
```bash
# Migrer les scripts de référence vers la structure moderne
mv reference_scripts/analyze_reference.py src/manalytics/cli/analyze.py
mv reference_scripts/scrape_reference.py src/manalytics/cli/scrape.py
mv reference_scripts/visualize_reference.py src/manalytics/cli/visualize.py
```

### 4.2 Créer les Points d'Entrée Uniques
```python
# src/manalytics/cli/main.py
import argparse

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    # Commande analyze
    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.set_defaults(func=analyze_command)
    
    # Commande scrape  
    scrape_parser = subparsers.add_parser('scrape')
    scrape_parser.set_defaults(func=scrape_command)
    
    # Commande visualize
    viz_parser = subparsers.add_parser('visualize') 
    viz_parser.set_defaults(func=visualize_command)
```

## 🚨 ACTIONS IMMÉDIATES (MAINTENANT)

### 1. Tester les 3 Scripts Candidats
```bash
# Test immédiat pour identifier LE bon script
python analyze_july_jiliac_method.py
python analyze_july_complete_final.py  
python analyze_july_all_6_visualizations.py
```

### 2. Comparer avec les Résultats Jiliac Attendus
- **Izzet Cauldron**: 20.4% (pas 29%)
- **Dimir Midrange**: 17.9% (pas 25.4%)

### 3. Documenter le Gagnant
```bash
# Une fois identifié, créer immédiatement
touch SCRIPT_REFERENCE_OFFICIEL.md
```

## 🎯 CRITÈRES DE SÉLECTION

### Script de Référence DOIT :
1. ✅ **Donner les résultats les plus proches de Jiliac**
2. ✅ **Utiliser la structure moderne** (`src/manalytics/`)
3. ✅ **Être documenté** et compréhensible
4. ✅ **Fonctionner sans erreur**
5. ✅ **Avoir une logique claire** et traçable

### Script de Référence NE DOIT PAS :
1. ❌ Avoir des imports cassés
2. ❌ Utiliser des chemins hardcodés
3. ❌ Dépendre de fichiers manquants
4. ❌ Avoir une logique obscure
5. ❌ Être un "fix temporaire"

## 📊 MÉTRIQUES DE SUCCÈS

### Avant Restructuration :
- ❌ 21 scripts d'analyse différents
- ❌ 15 scripts de scraping différents  
- ❌ 3 architectures conflictuelles
- ❌ Résultats incohérents

### Après Restructuration :
- ✅ 1 script d'analyse de référence
- ✅ 1 script de scraping de référence
- ✅ 1 architecture unifiée
- ✅ Résultats reproductibles

## 🚀 BÉNÉFICES ATTENDUS

1. **Résolution du mystère des matchups** : Une seule logique = résultats cohérents
2. **Maintenance simplifiée** : Un seul endroit à modifier
3. **Onboarding facile** : Nouveau développeur sait quoi utiliser
4. **Debugging possible** : Logique traçable et documentée
5. **Évolution contrôlée** : Changements versionnés et testés

---

**CONCLUSION** : Le chaos architectural est probablement la vraie cause du "mystère des matchups". En consolidant sur UNE logique de référence, nous devrions pouvoir reproduire exactement les résultats de Jiliac.

**PROCHAINE ÉTAPE** : Tester immédiatement les 3 scripts candidats et identifier le gagnant.