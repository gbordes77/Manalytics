# 🚨 Règles de Développement - Manalytics

> **Objectif** : Éviter TOUTE perte de code et garantir la stabilité du projet

## 🔴 **RÈGLES CRITIQUES - ABSOLUES**

### 1. **MODIFICATION_TRACKER.md OBLIGATOIRE**
```bash
# ❌ INTERDIT
git add src/orchestrator.py
git commit -m "fix: something"

# ✅ OBLIGATOIRE
# 1. Ajouter entrée dans MODIFICATION_TRACKER.md
# 2. Commiter le tracker
git add docs/MODIFICATION_TRACKER.md
git commit -m "track: preparing orchestrator modification"
# 3. Faire la modification
# 4. Commiter la modification
git add src/orchestrator.py
git commit -m "fix: something (tracked in MODIFICATION_TRACKER.md)"
```

### 2. **MAIN BRANCH UNIQUEMENT**
```bash
# ❌ INTERDIT
git checkout -b feature/my-feature

# ✅ OBLIGATOIRE
git checkout main
git pull origin main
# Travailler directement sur main
```

### 3. **ROLLBACK IMMÉDIAT SI PROBLÈME**
```bash
# Si votre commit cause des problèmes
git revert <commit-hash>
git push origin main

# Puis mettre à jour MODIFICATION_TRACKER.md
```

### 4. **BACKUP AVANT MODIFICATION MAJEURE**
```bash
# Avant toute modification importante
git tag backup-before-[description]-$(date +%Y%m%d-%H%M)
git push origin --tags
```

---

## 🛡️ **SYSTÈME DE PROTECTION**

### **Étape 1 : Planification**
- [ ] Lire le fichier concerné entièrement
- [ ] Comprendre l'impact de la modification
- [ ] Identifier tous les fichiers dépendants
- [ ] Prévoir les tests de validation

### **Étape 2 : Traçabilité**
- [ ] Ajouter entrée dans MODIFICATION_TRACKER.md
- [ ] Spécifier le rollback exact
- [ ] Commiter le tracker

### **Étape 3 : Modification**
- [ ] Modifier UN seul fichier à la fois
- [ ] Tester immédiatement
- [ ] Commiter avec référence au tracker

### **Étape 4 : Validation**
- [ ] Tester le pipeline complet
- [ ] Vérifier que rien n'est cassé
- [ ] Documenter le résultat

---

## 📋 **CHECKLIST AVANT CHAQUE MODIFICATION**

### **Questions Obligatoires**
- [ ] **Quoi** : Qu'est-ce que je modifie exactement ?
- [ ] **Pourquoi** : Quelle est la justification ?
- [ ] **Impact** : Quels autres fichiers sont affectés ?
- [ ] **Test** : Comment je valide que ça marche ?
- [ ] **Rollback** : Comment j'annule si problème ?

### **Fichiers à Vérifier**
- [ ] `src/orchestrator.py` - Pipeline principal
- [ ] `src/python/visualizations/` - Graphiques
- [ ] `src/python/classifier/` - Classification
- [ ] `docs/MODIFICATION_TRACKER.md` - Traçabilité

---

## 🚀 **TYPES DE MODIFICATIONS**

### **🟢 MODIFICATION SIMPLE** (1 fichier, impact limité)
```bash
# Exemple : Corriger un bug dans un seul fichier
1. Ajouter entrée MODIFICATION_TRACKER.md
2. Commiter tracker
3. Modifier le fichier
4. Tester localement
5. Commiter avec référence
```

### **🟡 MODIFICATION MOYENNE** (2-5 fichiers, impact modéré)
```bash
# Exemple : Ajouter une nouvelle visualisation
1. Créer tag backup
2. Ajouter entrée MODIFICATION_TRACKER.md détaillée
3. Commiter tracker
4. Modifier fichier par fichier
5. Tester à chaque étape
6. Commiter chaque fichier séparément
```

### **🔴 MODIFICATION MAJEURE** (>5 fichiers, impact fort)
```bash
# Exemple : Refactoring complet
1. Créer branche temporaire pour développement
2. Développer et tester complètement
3. Merger d'un coup vers main
4. Supprimer la branche temporaire
5. Créer tag stable
```

---

## 📊 **MONITORING ET MÉTRIQUES**

### **Indicateurs à Surveiller**
- Nombre de commits par jour
- Taille des modifications
- Fréquence des rollbacks
- Temps entre modification et validation

### **Alertes**
- 🚨 Plus de 3 rollbacks en 24h → STOP, analyser
- 🚨 Modification >1000 lignes → Review obligatoire
- 🚨 Fichier non tracé → Commit bloqué

---

## 🔧 **OUTILS ET SCRIPTS**

### **Script de Validation Pré-Commit**
```bash
# scripts/pre-commit-validation.sh
#!/bin/bash
# Vérifier que MODIFICATION_TRACKER.md est à jour
# Vérifier que les tests passent
# Vérifier le formatting
```

### **Script de Rollback d'Urgence**
```bash
# scripts/emergency-rollback.sh
#!/bin/bash
# Rollback immédiat vers le dernier tag stable
# Notification automatique
```

### **Script de Backup Quotidien**
```bash
# scripts/daily-backup.sh
#!/bin/bash
# Créer tag de sauvegarde quotidien
# Sauvegarder sur service externe
```

---

## 🎯 **BONNES PRATIQUES**

### **DO (À FAIRE)**
- ✅ Modifier un fichier à la fois
- ✅ Tester immédiatement après modification
- ✅ Commiter souvent avec messages clairs
- ✅ Utiliser le MODIFICATION_TRACKER.md systématiquement
- ✅ Créer des tags de sauvegarde pour modifications importantes

### **DON'T (NE PAS FAIRE)**
- ❌ Modifier plusieurs fichiers sans tests
- ❌ Commiter sans mettre à jour le tracker
- ❌ Créer des branches feature (sauf modifications majeures)
- ❌ Modifier des fichiers sans comprendre l'impact
- ❌ Ignorer les erreurs de pre-commit

---

## 🆘 **PROCÉDURES D'URGENCE**

### **En cas de Perte de Code**
1. **NE PAS PANIQUER**
2. Vérifier les tags de backup : `git tag --list | grep backup`
3. Consulter MODIFICATION_TRACKER.md pour l'historique
4. Restaurer depuis le dernier tag stable
5. Analyser la cause pour éviter la répétition

### **En cas de Bug en Production**
1. **ROLLBACK IMMÉDIAT** : `git revert <commit-hash>`
2. Pousser le rollback : `git push origin main`
3. Mettre à jour MODIFICATION_TRACKER.md
4. Analyser et corriger à tête reposée

### **En cas de Conflit**
1. Depuis main uniquement, conflits rares
2. Si conflit : `git status` pour identifier
3. Résoudre manuellement
4. Documenter dans MODIFICATION_TRACKER.md

---

## 📈 **ÉVOLUTION DU SYSTÈME**

### **Métriques de Succès**
- 0 perte de code en 30 jours
- Temps de rollback < 5 minutes
- 100% des modifications tracées
- Satisfaction développeur élevée

### **Améliorations Futures**
- Intégration CI/CD avec validation automatique
- Dashboard de monitoring des modifications
- Alertes Slack/Email pour rollbacks
- Backup automatique cloud

---

*Règles créées le : 2025-01-14*
*Version : 1.0*
*Mise à jour : Auto avec chaque modification*
