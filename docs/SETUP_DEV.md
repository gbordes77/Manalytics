# ⚙️ Setup Dev - Environnement en 5 Minutes

> **Objectif** : Développeur opérationnel sur Manalytics en ≤5 min

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
ls standard_analysis_2025-07-01_2025-07-07/  # Doit afficher 13 fichiers
open standard_analysis_2025-07-01_2025-07-07/index.html
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
