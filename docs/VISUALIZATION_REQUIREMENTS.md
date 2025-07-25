# 📊 VISUALIZATION REQUIREMENTS - Manalytics Phase 3

> **"Chaque visualisation doit raconter une histoire. Pas de graphs pour faire joli - uniquement des insights actionnables pour gagner des tournois."**
> 
> **Chaque visualisation doit apporter de la valeur compétitive réelle.**

## 🎯 Vision Globale

Transformer les données brutes de tournois en **avantages compétitifs mesurables** pour les joueurs. Chaque visualisation répond à une question stratégique précise.

## 📈 État Actuel (Base de Travail)

D'après notre visualisation actuelle, nous avons :
- **67 Tournois** analysés
- **1,140 Decks** complets (mainboard + sideboard)
- **70 Archétypes** uniques détectés

### Métagame Actuel
1. **Izzet Prowess (Cauldron)** - 223 decks (19.56%)
2. **Dimir Midrange** - 221 decks (19.39%)
3. **Mono White Caretaker** - 53 decks (4.65%)
4. **Golgari Midrange** - 50 decks (4.39%)
5. **Boros Convoke** - 41 decks (3.60%)

## 🔥 10 VISUALISATIONS PRIORITAIRES

### 1. **Metagame Evolution Timeline** 
**Question**: "Comment le méta évolue-t-il semaine après semaine ?"
- **Type**: Stacked Area Chart animé
- **Insight**: Identifier les decks en croissance/déclin
- **Action**: Anticiper le méta du prochain tournoi
- **Filtres**: Par période, format, type de tournoi

### 2. **Matchup Matrix Heatmap**
**Question**: "Quel deck bat quel deck ?"
- **Type**: Heatmap interactive avec % win rate
- **Insight**: Forces/faiblesses de chaque archétype
- **Action**: Choisir le deck avec les meilleurs matchups
- **Features**: Drill-down par match, sample size visible

### 3. **Innovation Radar**
**Question**: "Quelles sont les nouvelles tech cards qui émergent ?"
- **Type**: Bubble chart temporel
- **Insight**: Détecter les innovations avant qu'elles deviennent mainstream
- **Action**: Adapter sa liste ou son sideboard
- **Métriques**: Adoption rate, win rate delta

### 4. **Deck Performance Scatter**
**Question**: "Quel est le rapport popularité/performance ?"
- **Type**: Scatter plot (X: Meta%, Y: Win%)
- **Insight**: Identifier les decks sous-joués mais performants
- **Action**: Exploiter les decks "sleeper"
- **Quadrants**: Overplayed, Underplayed, Optimal, Trap

### 5. **Sideboard Guide Matrix**
**Question**: "Que sideboard contre chaque matchup ?"
- **Type**: Matrix IN/OUT interactive
- **Insight**: Patterns de sideboard des top joueurs
- **Action**: Optimiser son plan de sideboard
- **Data**: Agrégation des 10+ meilleures performances

### 6. **Tournament Meta Predictor**
**Question**: "À quoi ressemblera le méta du prochain tournoi ?"
- **Type**: Forecast avec confidence intervals
- **Insight**: Anticipation basée sur tendances + événements
- **Action**: Préparer le bon deck/sideboard
- **ML**: Time series + event detection

### 7. **Card Inclusion Trends**
**Question**: "Comment évoluent les ratios de cartes clés ?"
- **Type**: Multi-line chart avec annotations
- **Insight**: Ajustements fins des top joueurs
- **Action**: Optimiser ses ratios (lands, removal, threats)
- **Exemples**: 3 vs 4 Fatal Push, 24 vs 25 lands

### 8. **Player Performance Tracker**
**Question**: "Qui sont les joueurs à suivre et que jouent-ils ?"
- **Type**: Leaderboard + deck history
- **Insight**: Identifier les innovateurs et spécialistes
- **Action**: S'inspirer des meilleurs
- **Métriques**: Win rate, consistency, innovation score

### 9. **Meta Clock Visualization**
**Question**: "Où en est le cycle aggro/midrange/control ?"
- **Type**: Circular radar chart animé
- **Insight**: Position actuelle dans le meta cycle
- **Action**: Anticiper la prochaine rotation
- **Theory**: Rock-Paper-Scissors du métagame

### 10. **Consensus Deck Builder**
**Question**: "Quelle est LA liste optimale de cet archétype ?"
- **Type**: Visual deck builder avec % consensus
- **Insight**: Version "crowd-sourced" optimale
- **Action**: Partir d'une base solide et éprouvée
- **Algorithm**: Weighted average des top performances

## 🎨 Design System

### Palette de Couleurs MTG
```css
--white: #FFFBD5;
--blue: #0E68AB;
--black: #150B00;
--red: #D3202A;
--green: #00733E;
--colorless: #BFB7AB;
--multicolor: linear-gradient(45deg, gold, orange);
--dark-bg: #1a1a1a;
--card-bg: #2d2d2d;
```

### Principes UX
1. **Mobile-first**: Utilisable pendant les tournois
2. **Dark mode**: Par défaut pour réduire la fatigue
3. **Interactions**: Hover, click, drill-down partout
4. **Performance**: <100ms pour toute interaction
5. **Bookmarkable**: États partageables par URL

### Accessibility
- Modes daltoniens (deuteranopia, protanopia)
- Navigation clavier complète
- ARIA labels sur tous les éléments interactifs
- Contrast ratio WCAG AA minimum

## 📊 Stack Technique Recommandé

### Frontend
```javascript
// Core
- Next.js 14 + TypeScript
- React Query (data fetching)
- Zustand (state management)

// Visualizations
- D3.js (custom complex viz)
- Recharts (standard charts)
- Visx (hybrid approach)
- Framer Motion (animations)

// UI
- TailwindCSS + shadcn/ui
- Radix UI (accessible components)
```

### Data Processing
```python
# Analytics Pipeline
- Pandas (data manipulation)
- NumPy (calculations)
- Scikit-learn (ML predictions)
- Apache Arrow (fast serialization)
```

### Performance
- React.memo sur tous les composants lourds
- Virtual scrolling pour les listes
- Web Workers pour calculs complexes
- CDN pour assets statiques
- Redis cache pour API responses

## 🚀 Roadmap d'Implémentation

### Sprint 1 (1 semaine)
- [ ] Setup Next.js + TypeScript + D3
- [ ] Metagame Evolution Timeline
- [ ] Matchup Matrix Heatmap
- [ ] API endpoints de base

### Sprint 2 (1 semaine)
- [ ] Innovation Radar
- [ ] Deck Performance Scatter
- [ ] Sideboard Guide Matrix

### Sprint 3 (2 semaines)
- [ ] Tournament Meta Predictor (ML)
- [ ] Consensus Deck Builder
- [ ] Player Performance Tracker

### Sprint 4 (1 semaine)
- [ ] Polish & optimizations
- [ ] Mobile responsive
- [ ] Export/sharing features
- [ ] Documentation

## 🎯 KPIs de Succès

### Usage
- 1000+ utilisateurs actifs/semaine
- 5+ minutes temps moyen de session
- 50%+ returning users

### Performance
- Lighthouse score > 95
- Load time < 2s (3G)
- 0 erreurs JS en production

### Business
- 10+ pros utilisent pour prep tournoi
- 3+ articles/reviews positifs
- 100+ membres communauté Discord

## 💡 Features Différenciantes

### Ce que personne d'autre ne fait :
1. **Consensus Deck Generator** - Auto-génération de LA liste optimale
2. **Innovation Detector** - Alertes sur tech choices émergentes
3. **Meta Predictor ML** - Prévisions basées sur patterns historiques
4. **Sideboard Intelligence** - Suggestions data-driven
5. **Multi-source** - MTGO + Melee data unifiée

## 📝 Notes d'Implémentation

### Chaque visualisation DOIT avoir :
1. **Titre explicite** avec la question à laquelle elle répond
2. **Légende interactive** (cliquer = filter)
3. **Export** en PNG/SVG/CSV
4. **Partage** par URL unique
5. **Aide contextuelle** (? icon)
6. **Loading skeleton** pendant fetch
7. **Error boundary** avec fallback

### Patterns de Code
```typescript
// Chaque viz est un module autonome
interface VizModule {
  component: React.FC<VizProps>
  fetcher: () => Promise<VizData>
  transformer: (raw: RawData) => VizData
  config: VizConfig
  exports: ExportFormats[]
}
```

## 🔗 Intégrations

### Discord Bot
```
!meta standard
!matchup "Izzet Prowess" vs "Dimir Midrange"
!predict next-tournament
```

### API Publique
```
GET /api/v1/meta?format=standard&days=7
GET /api/v1/matchups?deck1=X&deck2=Y
GET /api/v1/consensus/:archetype
```

### Webhooks
- Nouveau tournoi détecté
- Changement majeur de meta (>5%)
- Innovation détectée (nouvelle carte top8)

---

**Remember**: Pas de vanity metrics. Chaque pixel doit aider à gagner des matchs. 🏆