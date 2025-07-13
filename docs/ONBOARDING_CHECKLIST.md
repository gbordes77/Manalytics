# ✅ Checklist On-boarding - Validation Étape par Étape

> **Objectif** : Garantir que chaque nouveau développeur maîtrise parfaitement Manalytics

## 🎯 **ÉTAPE 1 : Compréhension Projet** (15 min)

**📋 Avant de continuer, validez que vous savez répondre à :**
- [ ] Quelle est la différence entre v0.3 et v1.0 ?
- [ ] Pourquoi utilise-t-on du scraping multi-sources ?
- [ ] Quels sont les 3 formats supportés ?
- [ ] Quel est l'objectif des 9 visualisations ?
- [ ] **🆕 Pourquoi différencier MTGO Challenge vs League ?**
- [ ] **🆕 Comment accéder directement aux tournois depuis le dashboard ?**

**🔗 Lu** : [ROADMAP.md](ROADMAP.md) | **➡️ Suivant** : [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md)

---

## 🏗️ **ÉTAPE 2 : Architecture Technique** (30 min)

**📋 Avant de continuer, validez que vous savez répondre à :**
- [ ] Comment les données passent de MTGO à l'analyseur ?
- [ ] Où ajouter un nouveau scraper ?
- [ ] Comment fonctionne le classifier d'archétypes ?
- [ ] Quels sont les 4 modules principaux ?

**🔗 Lu** : [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md) | **➡️ Suivant** : [SETUP_DEV.md](SETUP_DEV.md)

---

## ⚙️ **ÉTAPE 3 : Setup Développement** (5 min)

**📋 Avant de continuer, validez que vous avez :**
- [ ] Cloné le repo et checkout v0.3.1
- [ ] Installé les dépendances Python
- [ ] Installé les hooks pre-commit
- [ ] Lancé avec succès un pipeline de test
- [ ] Vu les 9 graphiques générés
- [ ] **🆕 Testé les badges colorés des sources sous "Analyse complète"**
- [ ] **🆕 Cliqué sur le lien "Tournois analysés" et testé les URLs**
- [ ] **🆕 Vérifié la distinction MTGO Challenge vs League 5-0**

**🔗 Exécuté** : [SETUP_DEV.md](SETUP_DEV.md) | **➡️ Suivant** : Première PR

---

## 🎯 **ÉTAPE 4 : Première Contribution** (Jour 1)

**📋 Avant de considérer l'onboarding terminé, validez que vous avez :**
- [ ] Créé une branche feature
- [ ] Modifié un fichier (ex: documentation)
- [ ] Commité avec les hooks automatiques
- [ ] Créé une PR avec le template
- [ ] **Coché la case appropriée** dans le template PR
- [ ] Reçu une review et mergé la PR

**🔗 Suivi** : [Workflow dans SETUP_DEV.md](SETUP_DEV.md#workflow-développement)

---

## 🏆 **ONBOARDING TERMINÉ** ✅

**Félicitations !** Vous maîtrisez maintenant :
- ✅ Vision produit et architecture
- ✅ Environnement de développement
- ✅ Workflow de contribution
- ✅ Système de gouvernance documentaire

**🎯 KPI Atteints** : Compréhension ≤ 2h • Premier run ≤ 15 min • Première PR Jour 1

---

## 🆘 **Aide & Support**

**Bloqué ?** Consultez dans l'ordre :
1. [SETUP_DEV.md - Troubleshooting](SETUP_DEV.md#troubleshooting-express)
2. [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md) - Guide complet
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée

**Template PR non respecté ?** Le [workflow CI](../.github/workflows/onboarding-guard.yml) bloquera automatiquement.

---

*Dernière mise à jour : 13 juillet 2025* 