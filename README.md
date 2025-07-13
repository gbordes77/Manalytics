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

## 🚀 On-boarding Kit - Équipe Future

| Document | Objectif | Temps |
|----------|----------|-------|
| [**📋 ROADMAP**](docs/ROADMAP.md) | Vision produit, tags clés v0.3→v1.0 | 15 min |
| [**🏗️ ARCHITECTURE_QUICKREAD**](docs/ARCHITECTURE_QUICKREAD.md) | Compréhension technique rapide | 30 min |
| [**⚙️ SETUP_DEV**](docs/SETUP_DEV.md) | Environnement dev en 5 min | 5 min |

**KPI On-boarding** : Compréhension projet ≤ 2h • Premier run ≤ 15 min • Première PR Jour 1

---

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