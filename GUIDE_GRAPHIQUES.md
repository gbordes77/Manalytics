# 📊 Guide d'Utilisation - Générateur de Graphiques Métagame

## 🎯 Vue d'ensemble

Le générateur de graphiques Manalytics permet de créer des visualisations complètes du métagame MTG pour n'importe quel format et période.

## 🚀 Utilisation Rapide

### Méthode 1: Ligne de commande
```bash
python graph_generator.py [FORMAT] [DATE] --days [NOMBRE_JOURS]
```

**Exemples:**
```bash
# Standard depuis le 15 janvier 2024, 30 jours
python graph_generator.py Standard 2024-01-15 --days 30

# Modern depuis le 1er mars 2024, 45 jours  
python graph_generator.py Modern 2024-03-01 --days 45

# Legacy depuis le 10 juin 2024, 21 jours
python graph_generator.py Legacy 2024-06-10 --days 21
```

### Méthode 2: Interface interactive
```bash
python graph_interactive.py
```
Interface conviviale avec menus guidés.

## 📋 Formats Supportés

| Format | Archétypes Typiques |
|--------|-------------------|
| **Standard** | Aggro, Control, Combo, Midrange, Tempo |
| **Modern** | Aggro, Control, Combo, Midrange, Tempo, Ramp |
| **Legacy** | Combo, Control, Aggro, Prison, Tempo |
| **Pioneer** | Aggro, Control, Combo, Midrange, Tribal |
| **Vintage** | Combo, Control, Prison, Aggro |
| **Pauper** | Aggro, Control, Combo, Tempo |

## 📊 Types de Graphiques Générés

### 1. Évolution des Parts de Marché
- **Fichier**: `metagame_shares_[FORMAT]_[DATE].png`
- **Contenu**: Courbes d'évolution des parts de marché par archétype
- **Utilité**: Identifier les tendances et cycles du métagame

### 2. Analyse des Winrates
- **Fichier**: `winrate_analysis_[FORMAT]_[DATE].png`
- **Contenu**: Évolution des winrates + moyennes par archétype
- **Utilité**: Détecter les archétypes performants

### 3. Heatmap de Popularité
- **Fichier**: `popularity_heatmap_[FORMAT]_[DATE].png`
- **Contenu**: Carte de chaleur de la popularité dans le temps
- **Utilité**: Visualiser les pics d'intérêt

### 4. Dashboard Complet
- **Fichier**: `dashboard_[FORMAT]_[DATE].png`
- **Contenu**: Vue d'ensemble avec 6 visualisations
- **Utilité**: Analyse complète en un coup d'œil

## 🎨 Caractéristiques Techniques

### Qualité
- **Résolution**: 300 DPI (haute qualité)
- **Format**: PNG avec transparence
- **Taille**: Optimisée pour impression et web

### Couleurs
- **Palette**: Couleurs distinctives par archétype
- **Cohérence**: Même couleur pour un archétype sur tous les graphiques
- **Lisibilité**: Contrastes optimisés

## 💡 Conseils d'Utilisation

### Choix de la Période
- **7-14 jours**: Tendances récentes, événements spécifiques
- **30 jours**: Analyse mensuelle standard (recommandé)
- **60+ jours**: Tendances long terme, évolution saisonnière

### Interprétation
- **Parts de marché**: > 20% = archétype dominant
- **Winrates**: > 55% = archétype fort, < 45% = archétype faible
- **Tendances**: Variations > 10% = changement significatif

### Cas d'Usage
- **Préparation tournoi**: Analyser le méta actuel
- **Deck building**: Identifier les archétypes émergents
- **Analyse post-tournoi**: Comprendre les résultats
- **Contenu**: Créer des articles/vidéos avec données

## 🔧 Exemples Pratiques

### Exemple 1: Préparation GP
```bash
# Analyser le méta Standard des 3 dernières semaines
python graph_generator.py Standard 2024-05-15 --days 21
```

### Exemple 2: Suivi Legacy
```bash
# Évolution Legacy sur 2 mois
python graph_generator.py Legacy 2024-04-01 --days 60
```

### Exemple 3: Analyse Pioneer
```bash
# Méta Pioneer récent (2 semaines)
python graph_generator.py Pioneer 2024-06-01 --days 14
```

## 📈 Interprétation des Résultats

### Dashboard - Sections
1. **Évolution Parts**: Tendances temporelles
2. **Winrates Moyens**: Performance relative
3. **Parts Actuelles**: Distribution actuelle (camembert)
4. **Tendances**: Variation sur la période (%)
5. **Corrélations**: Relations entre archétypes
6. **Statistiques**: Résumé numérique

### Signaux Importants
- **📈 Archétype émergent**: Part croissante + winrate élevé
- **📉 Archétype déclinant**: Part décroissante + winrate faible
- **⚖️ Méta équilibré**: Parts similaires + winrates ~50%
- **🔥 Méta déséquilibré**: Un archétype > 40% de parts

## 🛠️ Dépannage

### Erreurs Communes
```bash
# Format de date invalide
❌ Format de date invalide. Utilisez YYYY-MM-DD

# Date dans le futur
❌ La date ne peut pas être dans le futur

# Dépendances manquantes
❌ No module named 'matplotlib'
```

### Solutions
```bash
# Installer les dépendances
pip install matplotlib seaborn pandas numpy

# Vérifier le format de date
python -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d'))"
```

## 🎯 Cas d'Usage Avancés

### Comparaison Multi-Formats
```bash
# Générer pour plusieurs formats
python graph_generator.py Standard 2024-06-01 --days 30
python graph_generator.py Modern 2024-06-01 --days 30
python graph_generator.py Pioneer 2024-06-01 --days 30
```

### Analyse Temporelle
```bash
# Comparer différentes périodes
python graph_generator.py Modern 2024-01-01 --days 30  # Janvier
python graph_generator.py Modern 2024-03-01 --days 30  # Mars
python graph_generator.py Modern 2024-06-01 --days 30  # Juin
```

### Suivi Événement
```bash
# Avant/après un ban ou un nouveau set
python graph_generator.py Standard 2024-05-15 --days 14  # Avant
python graph_generator.py Standard 2024-06-01 --days 14  # Après
```

## 🎉 Résultats Attendus

Après exécution, vous obtiendrez:
- ✅ 4 graphiques PNG haute qualité
- ✅ Données simulées réalistes
- ✅ Analyses statistiques complètes
- ✅ Visualisations prêtes à partager

---

*Générateur développé dans le cadre de Manalytics Phase 3*  
*Intelligence Avancée pour l'analyse du métagame MTG* 