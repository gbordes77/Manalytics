# 🎯 Manalytics - MTG Metagame Analytics Pipeline

> **Analyse automatisée du métagame Magic: The Gathering** - Pipeline générant **9 visualisations interactives** en moins de 30 secondes

## ⚡ Lightning Tour (30 secondes)

```bash
# 1. Clone & Setup
git clone https://github.com/gbordes77/Manalytics.git && cd Manalytics
git checkout v0.3.0  # Clean baseline

# 2. Install
pip install -r requirements.txt

# 3. Run Analysis
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# 4. View Results (9 interactive charts)
open standard_analysis_2025-07-01_2025-07-07/index.html
```

**Résultat** : 9 graphiques HTML interactifs générés automatiquement (métagame, matchups, winrates, tiers, évolution temporelle...)

---

## 🚀 On-boarding Kit - Parcours Guidé (2h total)

> **⚠️ NOUVEAU DÉVELOPPEUR ?** Commencez par la [**✅ CHECKLIST DE VALIDATION**](docs/ONBOARDING_CHECKLIST.md) pour vous auto-évaluer à chaque étape.

### 📋 **ÉTAPE 1 : Compréhension Projet** (15 min)
➡️ **Lisez d'abord** : [**📋 ROADMAP**](docs/ROADMAP.md)
- Vision produit v0.3 → v1.0
- Décisions architecturales clés
- ✅ **Checkpoint** : Vous comprenez l'objectif final

### 🏗️ **ÉTAPE 2 : Architecture Technique** (30 min)
➡️ **Lisez ensuite** : [**🏗️ ARCHITECTURE_QUICKREAD**](docs/ARCHITECTURE_QUICKREAD.md)
- Pipeline scraping → analyse → visualisation
- Modules clés et points d'extension
- ✅ **Checkpoint** : Vous savez où modifier le code

### ⚙️ **ÉTAPE 3 : Setup Développement** (5 min)
➡️ **Exécutez** : [**⚙️ SETUP_DEV**](docs/SETUP_DEV.md)
- Clone, install, hooks, test pipeline
- Premier run réussi
- ✅ **Checkpoint** : Environnement opérationnel

### 🎯 **ÉTAPE 4 : Première Contribution** (Jour 1)
➡️ **Suivez le workflow** dans [SETUP_DEV.md](docs/SETUP_DEV.md#workflow-développement)
- Créer branche feature
- Modifier du code
- Première PR avec template obligatoire
- ✅ **Checkpoint** : PR mergée avec succès

---

**🎯 KPI On-boarding** : Compréhension ≤ 2h • Premier run ≤ 15 min • Première PR Jour 1

**⚠️ ORDRE OBLIGATOIRE** : Suivre les étapes 1→2→3→4 dans cet ordre. Chaque étape prépare la suivante.

## 📊 Résultat

✨ **9 graphiques interactifs générés automatiquement :**

1. **Distribution du métagame** - Camembert des archétypes
2. **Matrice de matchups** - Heatmap des winrates
3. **Analyse des winrates** - Barres avec intervalles de confiance
4. **Classification par tiers** - Scatter plot performance/popularité
5. **Bubble chart** - Performance vs Présence
6. **Top 5-0** - Meilleurs résultats
7. **Évolution temporelle** - Tendances des archétypes
8. **Bar chart archétypes** - Top archétypes du format
9. **Sources de données** - Répartition des tournois

## 🆕 Nouvelles fonctionnalités v0.3.1

### 🎯 **Différenciation MTGO**
- **MTGO Challenge** vs **MTGO League 5-0** - Distinction claire pour comparaison avec Jiliac
- **Badges colorés** - Identification visuelle immédiate des sources
- **Analyse précise** - Séparation des environnements compétitifs

### 🔗 **Accès direct aux tournois**
- **URLs cliquables** - Accès direct aux pages des tournois
- **Boutons stylisés** - Interface professionnelle avec icônes
- **Ouverture nouvel onglet** - Navigation fluide

### 📊 **Export & Organisation**
- **Export CSV** - Données tournois exportables (en développement)
- **Dossier Analyses/** - Organisation claire avec préfixes format/date
- **Navigation intuitive** - Boutons retour dashboard fonctionnels

### 🎨 **Interface améliorée**
- **Sources visibles** - Badges sous "Analyse complète" pour transparence
- **Couleurs distinctives** - Turquoise (melee.gg), Rouge (Challenge), Vert (League)
- **UX optimisée** - Accès tournois en 1 clic depuis dashboard

## 📖 Documentation

| Document | Description | Pour qui ? |
|----------|-------------|------------|
| [**Guide Utilisateur**](docs/GUIDE_UTILISATEUR.md) | Comment utiliser le pipeline | Utilisateurs finaux |
| [**Architecture Technique**](docs/ARCHITECTURE.md) | Comment ça fonctionne | Développeurs |
| [**Guide Développeur**](docs/GUIDE_DEVELOPPEUR.md) | Comment contribuer | Contributeurs |
| [**API Reference**](docs/API_REFERENCE.md) | Documentation des modules | Mainteneurs |

## 🏗️ Architecture Simplifiée

```
Input (CLI) → Scraping → Classification → Analysis → Visualization → Output (HTML)
```

**Détails complets dans [ARCHITECTURE.md](docs/ARCHITECTURE.md)**

## ⚡ Performance

- **12,000+ decks/seconde** - Classification ultra-rapide
- **100% taux de classification** - Aucun deck non identifié
- **88% tests coverage** - Robustesse assurée

## 🤝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT - Voir [LICENSE](LICENSE)
