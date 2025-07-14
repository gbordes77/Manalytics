# 🚀 Guide du Nouveau Workflow Manalytics

> **Objectif**: Workflow simplifié main-branch avec traçabilité complète pour éviter toute perte de code

## 🎯 **RÉSUMÉ DES CHANGEMENTS**

### ✅ **Ce qui a changé**
- **Fini les branches**: Tout se fait sur `main` directement
- **Traçabilité obligatoire**: Chaque modification doit être tracée
- **Nom avec date/heure**: Format `[NOM]_[YYYY-MM-DD_HH-MM]`
- **Scripts d'automatisation**: Outils pour simplifier le processus
- **Rollback immédiat**: Procédures d'urgence intégrées

### 🔧 **Outils disponibles**
- `python scripts/add_tracker_entry.py` - Ajouter une entrée de traçage
- `./scripts/create_backup_tag.sh` - Créer un tag de backup
- `./scripts/emergency_rollback.sh` - Rollback d'urgence

---

## 📋 **WORKFLOW STANDARD**

### **1. Préparer une modification**
```bash
# Étape 1: Créer une entrée de traçage
python scripts/add_tracker_entry.py

# Étape 2: Commiter le tracker
git add docs/MODIFICATION_TRACKER.md
git commit -m "track: preparing [description]"

# Étape 3: Créer un backup si modification importante
./scripts/create_backup_tag.sh "avant-modification-xyz"
```

### **2. Faire la modification**
```bash
# Modifier UN fichier à la fois
# Tester immédiatement
python run_full_pipeline.py --format Standard --start-date 2025-01-01 --end-date 2025-01-15

# Commiter avec référence au tracker
git add fichier-modifié.py
git commit -m "fix: correction xyz (tracked in MODIFICATION_TRACKER.md)"
```

### **3. Valider et pousser**
```bash
# Pousser vers main
git push origin main

# Si problème détecté, rollback immédiat
git revert <commit-hash>
git push origin main
```

---

## 🛠️ **GUIDE DES OUTILS**

### **📝 Script d'ajout de tracker**
```bash
python scripts/add_tracker_entry.py
```

**Utilisation interactive** :
- Demande le nom de l'intervenant
- Génère automatiquement le format `Nom_YYYY-MM-DD_HH-MM`
- Collecte tous les détails nécessaires
- Ajoute l'entrée dans `MODIFICATION_TRACKER.md`

**Exemple d'utilisation** :
```
🔧 Ajout d'une entrée dans MODIFICATION_TRACKER.md
==================================================
Nom de l'intervenant : Claude
Fichier(s) concerné(s) : src/orchestrator.py
Type de modification : 2
Description : Correction du bug de taille des graphiques
Justification : Uniformiser à 650px selon spécifications
Tests : Vérifier que tous les graphiques font 650px
Rollback : git revert du commit correspondant
```

### **💾 Script de backup**
```bash
./scripts/create_backup_tag.sh [description]
```

**Fonctionnalités** :
- Vérifie que vous êtes sur `main` et à jour
- Crée un tag avec timestamp
- Pousse le tag vers `origin`
- Affiche les instructions de rollback

**Exemples** :
```bash
./scripts/create_backup_tag.sh "avant-refactoring-visualisations"
./scripts/create_backup_tag.sh  # Backup automatique
```

### **🚨 Script de rollback d'urgence**
```bash
./scripts/emergency_rollback.sh [commit-hash|tag]
```

**Modes** :
- **Interactif** : `./scripts/emergency_rollback.sh`
- **Direct** : `./scripts/emergency_rollback.sh backup-xyz-20250114-1400`

**Sécurités** :
- Crée un backup d'urgence avant rollback
- Demande confirmation explicite
- Met à jour `MODIFICATION_TRACKER.md`
- Pousse automatiquement

---

## 📊 **FICHIER MODIFICATION_TRACKER.md**

### **Format d'entrée**
```markdown
### [YYYY-MM-DD HH:MM] - [NOM]_[YYYY-MM-DD_HH-MM]
**Fichier(s) concerné(s)** : `chemin/vers/fichier.py`
**Type** : [AJOUT/MODIFICATION/SUPPRESSION]
**Description** : Description claire de ce qui est fait
**Justification** : Pourquoi cette modification
**Tests** : Comment vérifier que ça fonctionne
**Rollback** : Comment annuler si problème
```

### **Exemple concret**
```markdown
### [2025-01-14 14:30] - Claude_2025-01-14_14-30
**Fichier(s) concerné(s)** : `src/orchestrator.py`
**Type** : MODIFICATION
**Description** : Correction taille graphiques à 650px
**Justification** : Uniformiser selon spécifications UI
**Tests** : Vérifier hauteur des divs dans HTML généré
**Rollback** : git revert a9890a0
```

---

## 🔄 **PROCÉDURES D'URGENCE**

### **Rollback immédiat**
```bash
# Identifier le commit problématique
git log --oneline -10

# Rollback simple
git revert <commit-hash>
git push origin main

# Rollback multiple (ordre inverse)
git revert <commit3> <commit2> <commit1>
git push origin main
```

### **Rollback complet vers tag**
```bash
# Utiliser le script d'urgence
./scripts/emergency_rollback.sh

# Ou manuellement
git reset --hard backup-xyz-20250114-1400
git push --force-with-lease origin main
```

### **Récupération après perte**
```bash
# Lister les backups
git tag -l "backup-*"

# Restaurer depuis un backup
git checkout backup-xyz-20250114-1400
git checkout -b recovery-branch
# Examiner le code
# Copier ce qui est nécessaire vers main
```

---

## 📈 **MÉTRIQUES ET MONITORING**

### **Indicateurs de santé**
- ✅ **0 perte de code** depuis implémentation
- ✅ **100% traçabilité** des modifications
- ✅ **Rollback < 5 min** en cas de problème
- ✅ **Workflow simplifié** sans branches

### **Vérifications régulières**
```bash
# Vérifier les dernières modifications
tail -20 docs/MODIFICATION_TRACKER.md

# Vérifier les backups
git tag -l "backup-*" | tail -10

# Vérifier l'état de main
git status
git log --oneline -5
```

---

## 🎯 **BONNES PRATIQUES**

### **✅ À FAIRE**
- Toujours utiliser `python scripts/add_tracker_entry.py`
- Créer un backup avant modification importante
- Tester immédiatement après chaque modification
- Commiter avec des messages clairs et référence au tracker
- Utiliser le format `[NOM]_[YYYY-MM-DD_HH-MM]`

### **❌ À NE PAS FAIRE**
- Modifier sans ajouter d'entrée dans le tracker
- Créer des branches (sauf cas exceptionnel)
- Commiter plusieurs fichiers en même temps sans test
- Ignorer les erreurs de pipeline
- Pousser sans vérifier l'état de `main`

---

## 🚀 **ONBOARDING RAPIDE**

### **Pour un nouvel intervenant**
1. Lire ce guide entièrement
2. Vérifier les outils : `python scripts/add_tracker_entry.py --help`
3. Faire un test : ajouter son nom à la liste des contributeurs
4. Créer sa première entrée dans le tracker
5. Commiter et pousser

### **Premier test**
```bash
# 1. Préparer
python scripts/add_tracker_entry.py
# (Ajouter une entrée pour "ajout nom à la liste")

# 2. Modifier
# Ajouter votre nom dans docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md

# 3. Commiter
git add docs/MODIFICATION_TRACKER.md docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md
git commit -m "onboarding: add [VOTRE_NOM] to team (tracked)"
git push origin main
```

---

## 🔍 **DÉPANNAGE**

### **Script ne fonctionne pas**
```bash
# Vérifier les permissions
ls -la scripts/
chmod +x scripts/*.sh

# Vérifier Python
python --version
python scripts/add_tracker_entry.py
```

### **Problème de Git**
```bash
# Vérifier l'état
git status
git branch

# Retourner sur main
git checkout main
git pull origin main
```

### **Tracker corrompu**
```bash
# Vérifier le format
head -20 docs/MODIFICATION_TRACKER.md

# Restaurer depuis backup si nécessaire
git checkout backup-xyz-20250114-1400 -- docs/MODIFICATION_TRACKER.md
```

---

## 🎉 **AVANTAGES DU NOUVEAU SYSTÈME**

### **🚀 Simplicité**
- Un seul branch (`main`)
- Pas de merge conflicts
- Workflow linéaire

### **🔒 Sécurité**
- Traçabilité complète
- Backups automatiques
- Rollback immédiat

### **⚡ Rapidité**
- Pas de review process
- Intégration immédiate
- Scripts automatisés

### **📊 Transparence**
- Historique visible
- Responsabilité claire
- Procédures documentées

---

*Guide créé le : 2025-01-14*
*Version du système : 1.0*
*Compatible avec : Manalytics v0.3.4+* 