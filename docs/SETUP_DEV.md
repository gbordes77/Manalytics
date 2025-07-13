# ⚙️ Setup Dev - Environnement en 5 Minutes

> **Objectif** : Développeur opérationnel sur Manalytics en ≤5 min

## 🆕 Nouvelles Fonctionnalités v0.3.4

> **Mise à jour du 13 juillet 2025** - Analyses statistiques avancées et intégration R-Meta-Analysis

### **Analyses Statistiques Avancées**
- **Shannon & Simpson Diversity** : Indices de diversité du métagame
- **Temporal Trends** : Analyse des tendances temporelles (Rising/Declining/Volatile/Stable)
- **K-means Clustering** : Groupement d'archétypes par performance
- **Correlation Analysis** : Analyse des corrélations avec tests de significativité
- **R-Meta-Analysis Integration** : Intégration avec [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3)

### **Documentation Complète**
- **API Reference** : Documentation complète des fonctions analytiques
- **User Guide** : Guide d'utilisation et d'interprétation
- **Orchestrator Integration** : Guide d'intégration pipeline
- **Team Handoff Checklist** : Système de transition d'équipe

### **Différenciation MTGO**
- **Challenge vs League** : Distinction claire des types de tournois MTGO
- **Badges colorés** : Rouge (Challenge), Vert (League), Turquoise (melee.gg)
- **Analyse précise** : Comparaison directe avec les données Jiliac

### **Navigation améliorée**
- **URLs cliquables** : Accès direct aux tournois depuis le dashboard
- **Boutons fonctionnels** : Retour dashboard + Export CSV (en travaux)
- **Organisation** : Analyses dans dossier `Analyses/` avec préfixes

### **Interface utilisateur**
- **Sources visibles** : Badges sous "Analyse complète"
- **Accès tournois** : Clic sur "XX Tournois analysés"
- **Navigation fluide** : Ouverture nouvel onglet

## 🚀 Setup Express

### 1. **Clone & Baseline** (30s)
```bash
git clone https://github.com/gbordes77/Manalytics.git
cd Manalytics
git checkout v0.3.0  # Clean baseline - 13 juillet 2025
```

### 2. **Python Environment** (2 min)
```bash
# Python 3.8+ requis
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils dev optionnels
```

### 3. **Quality Hooks** (30s)
```bash
pre-commit install  # Installe black, flake8, isort 6.0.1
echo "Hooks installés : formatage automatique au commit"
```

### 4. **Test Pipeline** (1 min)
```bash
# Test rapide avec données existantes
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# Vérification
ls Analyses/standard_analysis_2025-07-01_2025-07-07/  # Doit afficher 13 fichiers
open Analyses/standard_analysis_2025-07-01_2025-07-07/index.html

# 🆕 Tester les nouvelles fonctionnalités v0.3.1
echo "🎯 Testez les nouvelles fonctionnalités :"
echo "1. Dashboard -> Badges colorés sous 'Analyse complète'"
echo "2. Cliquer sur 'XX Tournois analysés' -> URLs cliquables"
echo "3. Vérifier distinction MTGO Challenge vs League 5-0"
echo "4. Bouton 'Retour au Dashboard' fonctionnel"
```

### 5. **Validation Setup** (30s)
```bash
# Test hooks qualité
echo "print('hello')" > test_file.py
git add test_file.py
git commit -m "test hooks"  # Doit formater automatiquement
rm test_file.py

echo "✅ Setup terminé ! Prêt à développer"
```

## 🛠️ Outils Recommandés

### **IDE Configuration**
```bash
# VS Code extensions utiles
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff

# Settings workspace (.vscode/settings.json)
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true
}
```

### **Aliases Utiles**
```bash
# Ajouter au ~/.zshrc ou ~/.bashrc
alias mana-run="python run_full_pipeline.py"
alias mana-test="python -m pytest tests/"
alias mana-lint="pre-commit run --all-files"
```

## 🔧 Workflow Développement

### **Première Contribution**
```bash
# 1. Créer branche feature
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer avec hooks automatiques
# ... modifications code ...

# 3. Tests locaux
python -m pytest tests/
pre-commit run --all-files

# 4. Commit & Push
git add .
git commit -m "feat: ajoute nouvelle fonctionnalité"  # Hooks auto
git push origin feature/nouvelle-fonctionnalite

# 5. Créer PR sur GitHub
```

### **Tests Rapides**
```bash
# Test pipeline complet
python run_full_pipeline.py --format Modern --start-date 2025-07-01 --end-date 2025-07-03

# Test module spécifique
python -m pytest tests/test_classifier.py -v

# Test performance
time python run_full_pipeline.py --format Standard --start-date 2025-07-12 --end-date 2025-07-12
```

## 🐛 Troubleshooting Express

| Problème | Solution Rapide |
|----------|----------------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Hooks pre-commit échouent | `pre-commit run --all-files` puis fix |
| Pipeline lent | Vérifier dates (max 7 jours recommandé) |
| Données manquantes | Vérifier accès internet + credentials |
| Tests échouent | `git reset --hard v0.3.0` (baseline propre) |

## 📚 Next Steps

1. **Lire** [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md) (15 min)
2. **Explorer** modules dans `src/python/` selon intérêt
3. **Première PR** : Fix documentation, ajout test, petite feature
4. **Architecture complète** : [ARCHITECTURE.md](ARCHITECTURE.md) quand nécessaire

---

**🎯 KPI Setup** : ≤5 min • Premier test pipeline ≤15 min total • Première PR Jour 1

*Questions ? Voir [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md) ou [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md)*

---

## 🎯 **ÉTAPE 3 TERMINÉE** ✅

**Checkpoint** : Votre environnement est opérationnel et vous avez fait votre premier run avec succès

### ➡️ **ÉTAPE SUIVANTE** : Première Contribution (Jour 1)
👉 **Suivez le workflow** ci-dessus section [🔧 Workflow Développement](#workflow-développement)

**Actions concrètes** :
1. Créer une branche `feature/mon-premier-changement`
2. Modifier un fichier de documentation (ex: corriger une typo)
3. Commiter avec les hooks automatiques
4. Créer une PR avec le template obligatoire
5. **Cocher la case appropriée** dans le template PR

**Pourquoi cette étape** : Validez que vous maîtrisez le processus complet de contribution.

---

*Parcours complet : [README Lightning Tour](../README.md) → [ROADMAP](ROADMAP.md) → [ARCHITECTURE](ARCHITECTURE_QUICKREAD.md) → **SETUP_DEV** → Première PR*
