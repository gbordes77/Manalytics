# 📊 Guide des Graphiques Manalytics

Ce guide explique comment lire et interpréter chaque visualisation générée par Manalytics.

## 🎨 Palette de Couleurs

Toutes les visualisations utilisent la **palette heatmap** standardisée :

- **Violet foncé (#762a83)** : Performance très faible (< 40%)
- **Violet moyen (#a66fb0)** : Performance faible (40-45%)
- **Violet clair (#d6b3de)** : Performance légèrement faible (45-50%)
- **Gris neutre (#f7f7f7)** : Performance équilibrée (50%)
- **Vert clair (#c7e9c0)** : Performance légèrement élevée (50-55%)
- **Vert moyen (#7bc87c)** : Performance élevée (55-60%)
- **Vert foncé (#1b7837)** : Performance très élevée (> 60%)

## 📊 1. Matrice de Matchups

### Comment lire
- **Axe X** : Archétype adversaire
- **Axe Y** : Votre archétype
- **Couleur** : Winrate du matchup (violet = défavorable, vert = favorable)
- **Pourcentage** : Winrate exact dans chaque cellule

### Interprétation
- **> 55%** : Matchup favorable (vert)
- **45-55%** : Matchup équilibré (gris)
- **< 45%** : Matchup défavorable (violet)

### Tooltips
Survolez une cellule pour voir :
- Winrate exact
- Intervalle de confiance 95%
- Nombre de matchs simulés

### Exemple
Si Control vs Aggro affiche **62%** en vert, cela signifie que Control gagne 62% de ses matchs contre Aggro.

## 📈 2. Part de Métagame

### Comment lire
- **Barres horizontales** : Pourcentage de présence dans le métagame
- **Seuil** : Seuls les archétypes ≥ 5% sont affichés
- **Couleurs** : Chaque archétype a sa couleur distinctive

### Interprétation
- **> 20%** : Archétype dominant
- **10-20%** : Archétype populaire
- **5-10%** : Archétype viable
- **< 5%** : Archétype de niche (non affiché)

### Tooltips
Survolez pour voir :
- Pourcentage exact
- Nombre de joueurs
- Winrate moyen

## 🎯 3. Winrates avec Intervalles de Confiance

### Comment lire
- **Points** : Winrate moyen de chaque archétype
- **Barres d'erreur** : Intervalle de confiance 95%
- **Ligne pointillée** : Seuil d'équilibre (50%)

### Interprétation
- **Point au-dessus de 50%** : Archétype performant
- **Barres d'erreur courtes** : Résultats fiables (beaucoup de données)
- **Barres d'erreur longues** : Incertitude élevée (peu de données)

### Statistiques
- **Méthode** : Intervalle de confiance Wilson
- **Niveau** : 95% de confiance
- **Signification** : 95% de chances que le vrai winrate soit dans cet intervalle

## 🏆 4. Classification par Tiers

### Comment lire
- **Axe X** : Part de métagame (%)
- **Axe Y** : Borne inférieure de l'intervalle de confiance
- **Couleurs** : Tier de l'archétype
- **Lignes horizontales** : Seuils des tiers

### Tiers définis
- **Tier 1** (vert foncé) : Borne inf. > 55%
- **Tier 2** (vert clair) : Borne inf. 50-55%
- **Tier 3** (violet clair) : Borne inf. 45-50%
- **Tier 4** (violet foncé) : Borne inf. < 45%

### Interprétation
- **Tier 1** : Archétypes meta, très performants
- **Tier 2** : Archétypes solides, compétitifs
- **Tier 3** : Archétypes viables, situationnels
- **Tier 4** : Archétypes faibles, à éviter

## 💫 5. Winrate vs Présence (Bubble Chart)

### Comment lire
- **Axe X** : Part de métagame (%)
- **Axe Y** : Winrate moyen
- **Taille des bulles** : Nombre de joueurs
- **Couleurs** : Tier de l'archétype

### Zones d'intérêt
- **Haut-droite** : Archétypes populaires ET performants (méta)
- **Haut-gauche** : Archétypes performants mais peu joués (sleepers)
- **Bas-droite** : Archétypes populaires mais peu performants (overrated)
- **Bas-gauche** : Archétypes peu joués ET peu performants

### Stratégie
- **Cherchez** : Bulles vertes en haut-gauche (archétypes sous-estimés)
- **Évitez** : Bulles violettes en bas-droite (archétypes surévalués)

## 🌟 6. Top Archétypes Performants

### Comment lire
- **Barres verticales** : Nombre de joueurs avec winrate ≥ 80%
- **Couleurs** : Chaque archétype a sa couleur
- **Nombres** : Comptage exact sur les barres

### Critères
- **Winrate ≥ 80%** : Performances exceptionnelles
- **Ou 5-0** : Score parfait (si disponible)

### Interprétation
- **Barres hautes** : Archétypes avec potentiel de top performances
- **Absence** : Archétype difficile à maîtriser ou structurellement faible

## 🔍 Conseils d'Analyse

### 1. Analyse Croisée
Combinez plusieurs graphiques pour une vision complète :
- Matrice + Tiers = Comprendre pourquoi un archétype est dans son tier
- Métagame + Winrate = Identifier les archétypes sous/sur-évalués
- Bubble chart = Vue d'ensemble pour choix stratégiques

### 2. Intervalles de Confiance
- **Larges** : Peu de données, résultats incertains
- **Étroits** : Beaucoup de données, résultats fiables
- **Chevauchement** : Pas de différence significative entre archétypes

### 3. Taille d'Échantillon
- **< 10 matchs** : Données insuffisantes
- **10-30 matchs** : Tendances émergentes
- **> 30 matchs** : Résultats fiables

### 4. Évolution Temporelle
- Comparez avec les analyses précédentes
- Identifiez les tendances (montée/descente d'archétypes)
- Adaptez votre stratégie aux changements du méta

## 📊 Exports de Données

### Formats Disponibles
- **CSV** : Pour analyses dans Excel/Google Sheets
- **JSON** : Pour intégration dans d'autres outils
- **HTML** : Pour partage et présentation

### Données Exportées
- **Statistiques par archétype** : Winrates, IC, parts de métagame
- **Matrice de matchups** : Tous les matchups avec détails
- **Top performers** : Joueurs avec meilleures performances

## ⚠️ Limitations

### Données Simulées
- Les matchups directs sont simulés à partir des winrates globaux
- Basés sur des performances réelles mais pas des matchups head-to-head
- Méthode Monte Carlo pour générer des résultats cohérents

### Taille d'Échantillon
- Résultats plus fiables avec plus de données
- Archétypes rares peuvent avoir des IC très larges
- Privilégiez les archétypes avec > 20 joueurs

### Biais Potentiels
- Méta local vs méta global
- Skill des joueurs variable
- Évolution du méta dans le temps

## 🎯 Utilisation Stratégique

### Pour Choisir un Deck
1. **Consultez les tiers** : Tier 1-2 pour compétition
2. **Vérifiez la matrice** : Évitez les archétypes avec trop de matchups défavorables
3. **Analysez la popularité** : Préparez-vous aux archétypes fréquents

### Pour Préparer un Tournoi
1. **Identifiez le méta** : Graphique de parts de métagame
2. **Étudiez les matchups** : Matrice pour votre archétype
3. **Anticipez les surprises** : Bubble chart pour sleepers

### Pour Analyser le Méta
1. **Tendances générales** : Diversité vs concentration
2. **Équilibre** : Répartition des tiers
3. **Opportunités** : Archétypes sous-représentés mais performants

---

*Généré automatiquement par Manalytics • Données 100% réelles • Mise à jour continue* 