# 👤 GUIDE UTILISATEUR MANALYTICS
## Manuel d'utilisation simple et pratique

---

## 🎯 **QU'EST-CE QUE MANALYTICS ?**

Manalytics est un outil d'analyse automatique du métagame Magic: The Gathering qui génère des rapports HTML avec des graphiques interactifs.

**En une commande, vous obtenez :**
- 📊 Analyse complète du métagame
- 🎨 9 graphiques interactifs
- 📈 Statistiques détaillées
- 💾 Exports CSV/JSON
- 🌐 Rapport HTML professionnel

---

## 🚀 **UTILISATION RAPIDE**

### **Commande de Base**
```bash
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07
```

### **Exemples Pratiques**
```bash
# Analyse Standard de la semaine dernière
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# Analyse Modern du mois
python run_full_pipeline.py --format Modern --start-date 2025-07-01 --end-date 2025-07-31

# Analyse Pioneer récente
python run_full_pipeline.py --format Pioneer --start-date 2025-07-10 --end-date 2025-07-15
```

---

## 📋 **FORMATS DISPONIBLES**

| Format | Description | Exemple |
|--------|-------------|---------|
| **Standard** | Format Standard actuel | `--format Standard` |
| **Modern** | Format Modern | `--format Modern` |
| **Pioneer** | Format Pioneer | `--format Pioneer` |
| **Legacy** | Format Legacy | `--format Legacy` |
| **Vintage** | Format Vintage | `--format Vintage` |
| **Pauper** | Format Pauper | `--format Pauper` |

---

## 📅 **GESTION DES DATES**

### **Format des Dates**
- **Format** : `YYYY-MM-DD`
- **Exemple** : `2025-07-01`

### **Conseils**
- **Période courte** : 1-7 jours pour analyses détaillées
- **Période moyenne** : 1-4 semaines pour tendances
- **Période longue** : 1-3 mois pour évolution

### **Exemples**
```bash
# Analyse d'une journée
--start-date 2025-07-01 --end-date 2025-07-01

# Analyse d'une semaine
--start-date 2025-07-01 --end-date 2025-07-07

# Analyse d'un mois
--start-date 2025-07-01 --end-date 2025-07-31
```

---

## 📊 **RÉSULTATS GÉNÉRÉS**

### **Structure des Dossiers**
```
{format}_analysis_{start_date}_{end_date}/
├── {format}_{start_date}_{end_date}.html    # 📄 Rapport principal
├── index.html                               # 📄 Copie de compatibilité
└── visualizations/                          # 📁 Graphiques individuels
    ├── metagame_pie.html                   # 🥧 Répartition du métagame
    ├── main_archetypes_bar.html            # 📊 Archétypes principaux
    ├── matchup_matrix.html                 # 🔥 Matrice de matchups
    ├── winrate_confidence.html             # 🎯 Winrates + IC
    ├── tiers_scatter.html                  # 🏆 Classification tiers
    ├── bubble_winrate_presence.html        # 💫 Winrate vs Présence
    ├── top_5_0.html                        # 🌟 Top performers
    ├── archetype_evolution.html            # 📈 Évolution temporelle
    ├── data_sources_pie.html               # 🔍 Sources de données
    ├── archetype_stats.csv                 # 📋 Données CSV
    ├── archetype_stats.json                # 📋 Données JSON
    └── matchup_matrix.csv                  # 📋 Matchups CSV
```

---

## 🎨 **COMPRENDRE LES GRAPHIQUES**

### **1. 🥧 Répartition du Métagame**
- **Utilité** : Part de marché des archétypes
- **Lecture** : Plus le segment est grand, plus l'archétype est joué
- **Astuce** : Cliquez sur la légende pour filtrer

### **2. 📊 Archétypes Principaux**
- **Utilité** : Classement des archétypes les plus joués
- **Lecture** : Barres horizontales, du plus joué au moins joué
- **Astuce** : Survol pour voir les détails

### **3. 🔥 Matrice de Matchups**
- **Utilité** : Winrates entre archétypes
- **Lecture** : Vert = favorable, Rouge = défavorable
- **Astuce** : Lignes = votre deck, Colonnes = adversaire

### **4. 🎯 Winrates avec Intervalles de Confiance**
- **Utilité** : Fiabilité des winrates
- **Lecture** : Points + barres d'erreur
- **Astuce** : Barres courtes = données fiables

### **5. 🏆 Classification par Tiers**
- **Utilité** : Classement par performance
- **Lecture** : Tier 1 = meilleurs, Tier 3 = moins bons
- **Astuce** : Position Y = performance, X = popularité

### **6. 💫 Winrate vs Présence**
- **Utilité** : Relation performance/popularité
- **Lecture** : Bulles = archétypes, taille = nombre de joueurs
- **Astuce** : Coin supérieur droit = archétypes dominants

### **7. 🌟 Top Performers**
- **Utilité** : Archétypes avec le plus de 5-0
- **Lecture** : Barres = nombre de résultats parfaits
- **Astuce** : Indique les decks "hot" du moment

### **8. 📈 Évolution Temporelle**
- **Utilité** : Tendances dans le temps
- **Lecture** : Lignes = évolution de la popularité
- **Astuce** : Pentes = changements rapides

### **9. 🔍 Sources de Données**
- **Utilité** : Origine des données analysées
- **Lecture** : Segments = plateformes (MTGO, Melee, etc.)
- **Astuce** : Vérification de la représentativité

---

## 🛠️ **RÉSOLUTION DE PROBLÈMES**

### **Erreurs Courantes**

#### **"No tournaments found"**
```bash
# Problème : Aucun tournoi trouvé
# Solution : Vérifiez les dates et le format
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07
```

#### **"Invalid date format"**
```bash
# Problème : Format de date incorrect
# Mauvais : --start-date 01/07/2025
# Correct : --start-date 2025-07-01
```

#### **"Format not supported"**
```bash
# Problème : Format non supporté
# Mauvais : --format standard (minuscule)
# Correct : --format Standard (majuscule)
```

### **Vérifications Rapides**
```bash
# Vérifier que Python fonctionne
python --version

# Vérifier que les dépendances sont installées
pip list | grep plotly

# Vérifier l'aide
python run_full_pipeline.py --help
```

---

## 📖 **CONSEILS D'UTILISATION**

### **Pour Débuter**
1. **Commencez simple** : Analysez 1 semaine de Standard
2. **Explorez les graphiques** : Cliquez, survolez, zoomez
3. **Exportez les données** : CSV pour Excel, JSON pour code
4. **Comparez les périodes** : Lancez plusieurs analyses

### **Pour Approfondir**
1. **Analysez les matchups** : Matrice pour comprendre le métagame
2. **Suivez les tendances** : Évolution temporelle
3. **Identifiez les tiers** : Classification pour investissements
4. **Trouvez les niches** : Archétypes peu joués mais performants

### **Pour Optimiser**
1. **Périodes courtes** : Plus précis mais moins de données
2. **Périodes longues** : Plus de données mais moins précis
3. **Formats populaires** : Plus de données (Standard, Modern)
4. **Formats de niche** : Moins de données (Vintage, Legacy)

---

## 🎯 **EXEMPLES D'ANALYSES**

### **Analyse Standard Hebdomadaire**
```bash
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07
```
**Utilité** : Métagame actuel, choix de deck pour tournoi

### **Analyse Modern Mensuelle**
```bash
python run_full_pipeline.py --format Modern --start-date 2025-07-01 --end-date 2025-07-31
```
**Utilité** : Tendances long terme, investissements cartes

### **Analyse Pioneer Récente**
```bash
python run_full_pipeline.py --format Pioneer --start-date 2025-07-10 --end-date 2025-07-15
```
**Utilité** : Impact nouveau set, métagame post-ban

---

## 🚀 **WORKFLOW RECOMMANDÉ**

### **1. Préparation**
```bash
# Activer l'environnement
source venv/bin/activate

# Vérifier les mises à jour
git pull origin main
```

### **2. Analyse**
```bash
# Lancer l'analyse
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07
```

### **3. Exploration**
- **Ouvrir le fichier HTML** généré
- **Explorer les graphiques** interactifs
- **Prendre des notes** sur les tendances

### **4. Export**
- **Télécharger les CSV** pour analyse externe
- **Sauvegarder les insights** importants
- **Partager les résultats** avec l'équipe

---

## 📞 **SUPPORT**

### **Documentation**
- **Ce guide** : Utilisation quotidienne
- **GUIDE_ADMIN_MANALYTICS.md** : Configuration avancée
- **DOCUMENTATION_EQUIPE_MANALYTICS.md** : Détails techniques

### **Ressources**
- **GitHub** : https://github.com/gbordes77/Manalytics
- **Logs** : Dossier `logs/` pour debugging
- **Tests** : `python -m pytest tests/`

---

## 🎉 **CONCLUSION**

Manalytics vous permet d'analyser le métagame Magic en quelques secondes. Avec une simple commande, vous obtenez des analyses professionnelles et des graphiques interactifs.

**Commande magique** :
```bash
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07
```

**Résultat** : Rapport HTML complet avec 9 graphiques interactifs !

---

*Guide créé le 13/07/2025*
*Version: 1.0*
*Pour utilisateurs finaux* 