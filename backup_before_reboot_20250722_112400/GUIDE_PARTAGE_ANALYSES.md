# 📦 Guide de Partage des Analyses Manalytics

> **Comment partager facilement vos analyses MTG avec d'autres personnes**

## 🎯 **Principe**

Chaque analyse Manalytics est **complètement autonome** et peut être partagée facilement en zip. Toutes les ressources (HTML, graphiques, données) sont incluses et les liens sont relatifs.

## 🚀 **Méthode Simple**

### 1. **Localiser votre analyse**
```bash
# Vos analyses sont dans le dossier :
Analyses/
├── standard_analysis_2025-07-01_2025-07-07/
├── modern_analysis_2025-07-01_2025-07-15/
└── ...
```

### 2. **Créer un zip**
```bash
# Depuis le dossier Analyses
cd Analyses
zip -r analysis_standard_2025-07-01_2025-07-07.zip standard_analysis_2025-07-01_2025-07-07/
```

### 3. **Partager le zip**
- 📧 **Email** : Attachez le fichier zip
- 💾 **Cloud** : Uploadez sur Google Drive, Dropbox, etc.
- 🔗 **Chat** : Envoyez directement dans Slack, Discord, etc.

## 🎁 **Réception et Consultation**

### **Pour celui qui reçoit le zip :**

1. **Dézipper le fichier**
   ```bash
   unzip analysis_standard_2025-07-01_2025-07-07.zip
   ```

2. **Ouvrir le dashboard**
   - 🖱️ **Double-cliquer** sur `standard_2025-07-01_2025-07-07.html`
   - 🌐 **Navigateur** : Ouvre automatiquement dans votre navigateur par défaut

3. **Naviguer dans l'analyse**
   - ✅ **Tous les graphiques** fonctionnent parfaitement
   - ✅ **Données interactives** disponibles
   - ✅ **Liste des tournois** avec URLs cliquables
   - ✅ **Aucune dépendance** externe requise

## 📋 **Contenu du zip**

```
standard_analysis_2025-07-01_2025-07-07/
├── 📄 standard_2025-07-01_2025-07-07.html           # Dashboard principal
├── 📄 standard_2025-07-01_2025-07-07_tournaments_list.html  # Liste tournois
└── 📁 visualizations/                                # Graphiques interactifs
    ├── 📊 metagame_pie.html                          # Camembert métagame
    ├── 📊 matchup_matrix.html                        # Matrice matchups
    ├── 📊 winrate_confidence.html                    # Winrates avec confiance
    ├── 📊 tiers_scatter.html                         # Classification tiers
    ├── 📊 bubble_winrate_presence.html               # Bubble chart
    ├── 📊 top_5_0.html                               # Top performers
    ├── 📊 archetype_evolution.html                   # Évolution temporelle
    ├── 📊 main_archetypes_bar.html                   # Bar chart archétypes
    ├── 📊 data_sources_pie.html                      # Sources de données
    ├── 📋 archetype_stats.csv                        # Données CSV
    ├── 📋 matchup_matrix.csv                         # Matrice CSV
    ├── 📋 top_performers.csv                         # Performances CSV
    └── 📋 *.json                                     # Données JSON
```

## ✅ **Avantages**

- 🎯 **Autonome** : Aucune installation requise
- 🔄 **Compatible** : Fonctionne sur Windows, Mac, Linux
- 📱 **Responsive** : S'adapte à tous les écrans
- 🌐 **Navigateur** : Ouverture dans n'importe quel navigateur moderne
- 💾 **Compact** : Les fichiers HTML sont compressés efficacement

## 🚨 **Important**

- ✅ **Gardez la structure** : Ne déplacez pas les fichiers dans le zip
- ✅ **Ouvrez le bon fichier** : `{format}_{start}_{end}.html` (dashboard principal)
- ✅ **Navigateur moderne** : Chrome, Firefox, Safari, Edge
- ✅ **JavaScript activé** : Pour les graphiques interactifs

## 🎉 **Exemple d'Usage**

```bash
# Créer une analyse
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# Zipper pour partage
cd Analyses
zip -r "Standard_Analysis_July_2025.zip" standard_analysis_2025-07-01_2025-07-07/

# Partager le zip
# → La personne n'a qu'à dézipper et ouvrir le .html principal !
```

---

🎯 **Résultat** : Vos analyses MTG sont maintenant **facilement partageables** avec n'importe qui, sans aucune dépendance technique !
