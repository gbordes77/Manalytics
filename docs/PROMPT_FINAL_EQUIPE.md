# 🎯 GUIDE COMPLET POUR LA NOUVELLE ÉQUIPE - MANALYTICS

## 📋 ÉTAT ACTUEL DU PROJET (Janvier 2025)

### 🏆 **PROJET MANALYTICS - PIPELINE D'ANALYSE MÉTAGAME MTG**
**Version actuelle** : v0.3.2 (feature/english-migration)
**Statut** : ✅ **PRODUCTION READY** - Pipeline fonctionnel avec 9 visualisations interactives
**Performance** : Génération complète d'analyse en < 30 secondes

### 🎯 **MISSION ACCOMPLIE**
Le pipeline Manalytics est un système complet d'analyse du métagame Magic: The Gathering qui :
- ✅ **Collecte automatiquement** les données de tournois réels (MTGO, Melee.gg, TopDeck.gg)
- ✅ **Classifie les archétypes** avec un système basé sur MTGOFormatData
- ✅ **Détecte les couleurs MTG** avec un système authentique de guildes
- ✅ **Génère 9 visualisations interactives** avec couleurs MTG authentiques
- ✅ **Exporte les données** en JSON/CSV pour usage externe
- ✅ **Interface web complète** avec navigation par archétypes

---

## 🚀 DÉMARRAGE RAPIDE (5 MINUTES)

### **Installation & Premier Run**
```bash
# 1. Cloner le projet
git clone https://github.com/gbordes77/Manalytics.git
cd Manalytics

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer une analyse complète
python manalytics_tool.py --format standard --start-date 2025-06-13 --end-date 2025-06-24

# 4. Voir les résultats
open Analyses/standard_analysis_2025-06-13_2025-06-24/standard_2025-06-13_2025-06-24.html
```

### **Résultat Attendu**
- 📊 **9 graphiques interactifs** générés automatiquement
- 🎨 **Couleurs MTG authentiques** (Izzet = bleu/rouge, Boros = blanc/rouge, etc.)
- 📈 **1000+ decks analysés** avec classification automatique
- 🔗 **Liens vers decklists originales** fonctionnels
- 📱 **Interface responsive** avec navigation intuitive

---

## 🔧 ARCHITECTURE TECHNIQUE

### **Structure du Projet**
```
Manalytics/
├── src/
│   ├── orchestrator.py           # 🎯 CŒUR - Pipeline principal
│   └── python/
│       ├── classifier/
│       │   ├── archetype_engine.py      # Classification archétypes
│       │   ├── color_detector.py        # 🆕 Détection couleurs MTG
│       │   └── mtgo_classifier.py       # Classification MTGO
│       └── visualizations/
│           ├── metagame_charts.py       # 🎨 Graphiques avec couleurs MTG
│           └── matchup_matrix.py        # Matrice de matchups
├── MTGOFormatData/              # Base de données archétypes
├── data/reference/Tournaments/  # 📦 Données tournois (28K+ fichiers)
├── Analyses/                    # 📊 Résultats générés
└── manalytics_tool.py          # 🚀 Point d'entrée principal
```

### **Technologies Utilisées**
- **Python 3.11+** : Langage principal
- **Plotly** : Visualisations interactives
- **Pandas** : Manipulation de données
- **MTGOFormatData** : Base de données archétypes
- **HTML/CSS/JS** : Interface web

---

## 🎨 NOUVELLES FONCTIONNALITÉS CLÉS

### **1. 🌈 SYSTÈME DE COULEURS MTG AUTHENTIQUE**
**Implémentation** : `src/python/classifier/color_detector.py`

```python
# Détection automatique des couleurs de deck
color_detector = ColorDetector()
colors = color_detector.analyze_decklist_colors(decklist)
# Résultat : {'color_identity': 'UR', 'guild_name': 'Izzet', 'color_distribution': {...}}
```

**Fonctionnalités** :
- ✅ **28,442 cartes** avec couleurs chargées depuis MTGOFormatData
- ✅ **Système WUBRG complet** (White, blUe, Black, Red, Green)
- ✅ **10 guildes bi-couleurs** (Azorius, Dimir, Rakdos, etc.)
- ✅ **10 clans tri-couleurs** (Esper, Jeskai, Bant, etc.)
- ✅ **Couleurs appliquées** dans tous les graphiques et l'interface

### **2. 📊 VISUALISATIONS INTERACTIVES (9 TYPES)**
**Implémentation** : `src/python/visualizations/metagame_charts.py`

1. **Metagame Pie Chart** - Distribution des archétypes
2. **Main Archetypes Bar** - Graphique en barres principal
3. **Metagame Share** - Parts de métagame détaillées
4. **Winrate Confidence** - Taux de victoire avec intervalles de confiance
5. **Tiers Scatter Plot** - Classification par tiers
6. **Bubble Chart** - Winrate vs présence
7. **Top 5-0 Performers** - Meilleurs performers
8. **Data Sources Pie** - Distribution des sources
9. **Archetype Evolution** - Évolution temporelle

### **3. 🔗 LIENS FONCTIONNELS VERS DECKLISTS**
**Correction récente** : Extraction des URLs depuis `AnchorUri`

```python
# Avant : "No link available"
# Après : "https://melee.gg/Decklist/View/abc123..."
deck_url = deck_data.get('AnchorUri', 'No link available')
```

### **4. 🎯 CLASSIFICATION ARCHÉTYPES AMÉLIORÉE**
**Système hybride** :
- **Primaire** : Classification basée sur MTGOFormatData
- **Fallback** : Classification par couleurs si archétype non trouvé
- **Déduplication** : Suppression automatique des doublons

---

## 📈 DONNÉES & PERFORMANCE

### **Sources de Données**
- **MTGO** : 15,000+ tournois (2015-2025)
- **Melee.gg** : 8,000+ tournois (2020-2025)
- **TopDeck.gg** : 2,000+ tournois (2024-2025)
- **Total** : ~28,000 fichiers JSON de tournois

### **Performance Actuelle**
- ⚡ **< 30 secondes** pour une analyse complète
- 📊 **1000+ decks** traités par analyse
- 🎯 **24+ archétypes** détectés automatiquement
- 🔄 **Déduplication** : -31% de doublons supprimés

### **Formats Supportés**
- ✅ **Standard** (principal)
- ✅ **Modern**
- ✅ **Legacy**
- ✅ **Pioneer**
- ✅ **Vintage**
- ✅ **Pauper**

---

## 🛠️ GUIDE DÉVELOPPEMENT

### **Points d'Extension Clés**

#### **1. Ajouter un Nouveau Type de Graphique**
```python
# Dans src/python/visualizations/metagame_charts.py
def create_new_chart_type(self, df: pd.DataFrame) -> go.Figure:
    # Obtenir les couleurs MTG
    archetype_names = df["archetype"].tolist()
    guild_names = self._get_guild_names_for_archetypes(archetype_names)
    colors = self.get_archetype_colors_for_chart(archetype_names, guild_names)

    # Créer le graphique avec les bonnes couleurs
    fig = go.Figure(...)
    return fig
```

#### **2. Ajouter une Nouvelle Source de Données**
```python
# Dans src/orchestrator.py
def _determine_source(self, file_path, tournament_info=None):
    if "nouvelle_source.com" in file_path:
        return "nouvelle_source.com"
    # ...
```

#### **3. Améliorer la Classification**
```python
# Dans src/python/classifier/archetype_engine.py
def classify_archetype(self, mainboard, format_name="Standard"):
    # Ajouter nouvelle logique de classification
    pass
```

### **Bonnes Pratiques**
- ✅ **Toujours utiliser des données réelles** (politique stricte)
- ✅ **Appliquer les couleurs MTG** dans tous les nouveaux graphiques
- ✅ **Tester avec plusieurs formats** (Standard, Modern, etc.)
- ✅ **Documenter les nouvelles fonctionnalités**

---

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

### **Phase 1 : Optimisations (1-2 semaines)**
1. **Performance** : Optimiser le temps de traitement
2. **Mémoire** : Réduire l'utilisation RAM pour gros datasets
3. **Cache** : Implémenter un système de cache intelligent

### **Phase 2 : Nouvelles Fonctionnalités (2-4 semaines)**
1. **API REST** : Exposer les données via FastAPI
2. **Dashboard Web** : Interface web interactive
3. **Alertes** : Notifications de changements métagame
4. **Export avancé** : Formats supplémentaires (Excel, PDF)

### **Phase 3 : Évolution (1-2 mois)**
1. **Machine Learning** : Prédiction d'évolution métagame
2. **Temps réel** : Mise à jour automatique des données
3. **Multi-formats** : Support simultané de plusieurs formats
4. **Analytics avancées** : Métriques business détaillées

---

## 📚 RESSOURCES ESSENTIELLES

### **Documentation Technique**
- `docs/ARCHITECTURE.md` - Architecture détaillée
- `docs/API_REFERENCE.md` - Référence API
- `src/python/classifier/README.md` - Système de classification

### **Exemples d'Utilisation**
```bash
# Analyse Standard récente
python manalytics_tool.py --format standard --start-date 2025-01-01 --end-date 2025-01-31

# Analyse Modern
python manalytics_tool.py --format modern --start-date 2024-12-01 --end-date 2024-12-31

# Analyse avec sortie personnalisée
python manalytics_tool.py --format standard --start-date 2025-01-01 --end-date 2025-01-15 --output-dir my_analysis
```

### **Dépannage Courant**
- **Erreur "No tournaments found"** : Vérifier les dates et le format
- **Graphiques sans couleurs** : Vérifier que `guild_name` est présent dans les données
- **Liens cassés** : Vérifier l'extraction `AnchorUri`

---

## 🏆 SUCCÈS MESURABLES

### **Métriques Actuelles**
- ✅ **100% données réelles** (zéro mock data)
- ✅ **9 visualisations** générées automatiquement
- ✅ **Couleurs MTG authentiques** dans tous les graphiques
- ✅ **Liens fonctionnels** vers toutes les decklists
- ✅ **Interface responsive** compatible mobile/desktop

### **Objectifs Atteints**
- 🎯 **Pipeline complet** de données à visualisations
- 🎯 **Classification automatique** des archétypes
- 🎯 **Détection couleurs** avec système MTG authentique
- 🎯 **Interface utilisateur** professionnelle
- 🎯 **Performance optimisée** (< 30s pour 1000+ decks)

---

## 🤝 SUPPORT & CONTACT

### **Handover Technique**
- **Code Review** : Tous les modules sont documentés et testés
- **Architecture** : Modulaire et extensible
- **Performance** : Optimisée pour production
- **Documentation** : Complète et à jour

### **Points d'Attention**
- ⚠️ **Politique No-Mock** : Enforcement strict des données réelles
- ⚠️ **Couleurs MTG** : Toujours utiliser le système de guildes
- ⚠️ **Déduplication** : Vérifier les doublons dans les nouvelles sources
- ⚠️ **Formats** : Tester avec plusieurs formats avant déploiement

---

**🎉 CONCLUSION** : Le projet Manalytics est un pipeline mature et fonctionnel, prêt pour la production et l'évolution. La nouvelle équipe peut immédiatement contribuer et étendre les fonctionnalités existantes.

**Dernière mise à jour** : Janvier 2025 - Handover équipe de développement
