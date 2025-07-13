# 👋 Instructions pour la Nouvelle Équipe Manalytics

> **Bienvenue !** Vous rejoignez le projet **Manalytics v0.3.1** - Plateforme d'analyse du métagame Magic: The Gathering

## 🎯 **MISSION CLAIRE**

Votre objectif est de devenir **opérationnel en 2 heures maximum** et faire votre **première contribution le premier jour**.

**KPI à atteindre** :
- ✅ Compréhension complète du projet ≤ 2h
- ✅ Premier run du pipeline ≤ 15 min
- ✅ Première PR mergée Jour 1

---

## 📋 **CONSIGNES STRICTES - LISEZ ATTENTIVEMENT**

### ⚠️ **RÈGLE N°1 : ORDRE OBLIGATOIRE**
Vous **DEVEZ** suivre les étapes **1→2→3→4** dans cet ordre exact. Chaque étape prépare la suivante.

### ⚠️ **RÈGLE N°2 : VALIDATION REQUISE**
À chaque étape, vous **DEVEZ** valider votre compréhension avec la checklist avant de continuer.

### ⚠️ **RÈGLE N°3 : DOCUMENTATION VIVANTE**
Le système d'onboarding est **auto-surveillé**. Toute modification de code sans mise à jour de doc sera **automatiquement bloquée**.

---

## 🚀 **PARCOURS D'ONBOARDING (2h max)**

### **AVANT DE COMMENCER**
1. Clonez le repository : `git clone https://github.com/gbordes77/Manalytics.git`
2. Entrez dans le dossier : `cd Manalytics`
3. **IMPORTANT - Choix de version** :
   - **Recommandé** : `git checkout v0.3.1` (version testée avec ces instructions)
   - **Alternatif** : `git checkout v0.3.2` ou supérieur (si disponible)

**⚠️ COMPATIBILITÉ** :
- Si vous utilisez **v0.3.1** → suivez ces instructions exactement
- Si vous utilisez **v0.3.2+** → vérifiez d'abord si le fichier `docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md` existe dans votre version
  - ✅ **Si il existe** → suivez les instructions de VOTRE version (plus récentes)
  - ❌ **Si il n'existe pas** → revenez à v0.3.1 : `git checkout v0.3.1`

4. Ouvrez la [**✅ CHECKLIST DE VALIDATION**](ONBOARDING_CHECKLIST.md) dans un onglet séparé

---

### 📋 **ÉTAPE 1 : Vision Produit** (15 min)

**🎯 ACTION** : Lisez **ENTIÈREMENT** le document [**ROADMAP.md**](ROADMAP.md)

**📝 VALIDATION** : Avant de continuer, vous **DEVEZ** savoir répondre à :
- [ ] Quelle est la différence entre v0.3 et v1.0 ?
- [ ] Pourquoi utilise-t-on du scraping multi-sources ?
- [ ] Quels sont les 3 formats supportés ?
- [ ] Quel est l'objectif des 9 visualisations ?

**✅ CHECKPOINT** : Vous comprenez maintenant l'objectif final de Manalytics

**➡️ SUIVANT** : Une fois validé, passez à l'Étape 2

---

### 🏗️ **ÉTAPE 2 : Architecture Technique** (30 min)

**🎯 ACTION** : Lisez **ENTIÈREMENT** le document [**ARCHITECTURE_QUICKREAD.md**](ARCHITECTURE_QUICKREAD.md)

**📝 VALIDATION** : Avant de continuer, vous **DEVEZ** savoir répondre à :
- [ ] Comment les données passent de MTGO à l'analyseur ?
- [ ] Où ajouter un nouveau scraper ?
- [ ] Comment fonctionne le classifier d'archétypes ?
- [ ] Quels sont les 4 modules principaux ?

**✅ CHECKPOINT** : Vous savez maintenant où modifier le code et comment le système fonctionne

**➡️ SUIVANT** : Une fois validé, passez à l'Étape 3

---

### ⚙️ **ÉTAPE 3 : Setup Développement** (5 min)

**🎯 ACTION** : Exécutez **TOUTES** les commandes du document [**SETUP_DEV.md**](SETUP_DEV.md)

**📝 VALIDATION** : Avant de continuer, vous **DEVEZ** avoir réussi :
- [ ] Cloné le repo et checkout v0.3.1 ✅ (déjà fait)
- [ ] Installé les dépendances Python
- [ ] Installé les hooks pre-commit
- [ ] Lancé avec succès un pipeline de test
- [ ] Vu les 9 graphiques générés dans le dossier de sortie

**✅ CHECKPOINT** : Votre environnement est opérationnel

**➡️ SUIVANT** : Une fois validé, passez à l'Étape 4

---

### 🎯 **ÉTAPE 4 : Première Contribution** (Jour 1)

**🎯 ACTION** : Suivez le [**Workflow de Développement**](SETUP_DEV.md#workflow-développement)

**📝 TÂCHE CONCRÈTE** :
1. Créez une branche : `git checkout -b feature/mon-premier-changement`
2. Modifiez ce fichier (`INSTRUCTIONS_NOUVELLE_EQUIPE.md`) : ajoutez votre nom dans la section "Équipe" ci-dessous
3. Commitez : `git add . && git commit -m "docs: add [VOTRE_NOM] to team"`
4. Poussez : `git push origin feature/mon-premier-changement`
5. Créez une PR sur GitHub
6. **IMPORTANT** : Dans le template PR, cochez la case "README Lightning Tour" (car vous modifiez la documentation)

**📝 VALIDATION** : Votre onboarding est terminé quand :
- [ ] Votre branche est créée
- [ ] Votre modification est commitée
- [ ] Votre PR est créée avec template rempli
- [ ] Votre PR est reviewée et mergée

**✅ CHECKPOINT FINAL** : Première contribution réussie !

---

## 🏆 **ÉQUIPE - Ajoutez votre nom ici après votre première PR**

*Développeurs ayant complété avec succès l'onboarding Manalytics v0.3.1 :*

- Claude Sonnet 4 (AI Assistant) - onboarding terminé le 2025-07-13
- [Votre nom ici après votre première PR]

---

## 🆘 **AIDE & SUPPORT**

### **Bloqué sur l'Étape 1-2 ?**
Relisez attentivement. Si toujours bloqué, consultez [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md)

### **Bloqué sur l'Étape 3 ?**
Consultez [SETUP_DEV.md - Troubleshooting](SETUP_DEV.md#troubleshooting-express)

### **Bloqué sur l'Étape 4 ?**
Le template PR vous guide. Chaque case correspond à une section de documentation.

### **PR bloquée par la CI ?**
Le workflow `onboarding-guard` a détecté que vous modifiez du code sans mettre à jour la documentation. C'est normal ! Cochez la bonne case dans le template PR.

---

## ⚡ **RAPPELS CRITIQUES**

1. **ORDRE OBLIGATOIRE** : 1→2→3→4 (chaque étape prépare la suivante)
2. **VALIDATION REQUISE** : Utilisez la checklist à chaque étape
3. **PREMIÈRE PR OBLIGATOIRE** : Ajoutez votre nom dans ce fichier
4. **TEMPLATE PR** : Toujours cocher une case (ou n/a avec justification)
5. **DOCUMENTATION VIVANTE** : Système auto-surveillé pour garantir la qualité
6. **VERSIONING** : Ces instructions sont pour v0.3.1+. Les versions futures incluront leurs propres instructions mises à jour.

---

## 🔄 **ÉVOLUTION DU KIT D'ONBOARDING**

**Comment ce système évolue** :
- Chaque nouvelle version (v0.3.2, v0.4.0, etc.) peut avoir des instructions d'onboarding mises à jour
- **Règle d'or** : Utilisez toujours les instructions de la version que vous avez checkout
- Si pas d'instructions dans votre version → revenez à v0.3.1 qui est garantie stable

**Pourquoi cette approche** :
- ✅ Garantit que les instructions correspondent au code
- ✅ Évite les incompatibilités entre versions
- ✅ Permet l'évolution du processus d'onboarding

---

## 🎯 **SUCCÈS**

**Félicitations !** Si vous avez suivi ces instructions, vous maîtrisez maintenant :
- ✅ Vision produit Manalytics v0.3 → v1.0
- ✅ Architecture technique et points d'extension
- ✅ Environnement de développement opérationnel
- ✅ Workflow de contribution et gouvernance

**Vous êtes prêt à contribuer efficacement au projet !**

---

*Instructions créées le : 13 juillet 2025*
*Baseline : v0.3.1*
*Système d'onboarding auto-maintenu*
