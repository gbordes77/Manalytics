# 📊 Manalytics Visualization Patterns & Standards

> **"Une viz sans insight = inutile"**

## 🎨 Color Standards for MTG

### Guild Colors (Two-Color Combinations)
```javascript
const GUILD_COLORS = {
    // Allied Guilds
    'Azorius': '#0080FF',    // White-Blue (Control)
    'Dimir': '#0F1B3C',      // Blue-Black (Mill/Control)
    'Rakdos': '#8B0000',     // Black-Red (Aggro)
    'Gruul': '#FF6B35',      // Red-Green (Aggro)
    'Selesnya': '#90EE90',   // Green-White (Tokens)
    
    // Enemy Guilds
    'Orzhov': '#FFD700',     // White-Black (Midrange)
    'Izzet': '#C41E3A',      // Blue-Red (Spells)
    'Golgari': '#7C9A2E',    // Black-Green (Graveyard)
    'Boros': '#FFA500',      // Red-White (Aggro)
    'Simic': '#40E0D0'       // Green-Blue (Ramp)
};
```

### Shard/Wedge Colors (Three-Color Combinations)
```javascript
const TRICOLOR_COMBOS = {
    // Shards
    'Bant': '#87CEEB',       // GWU (Control)
    'Esper': '#4B0082',      // WUB (Control)
    'Grixis': '#483D8B',     // UBR (Control)
    'Jund': '#8B4513',       // BRG (Midrange)
    'Naya': '#FFB6C1',       // RGW (Aggro)
    
    // Wedges
    'Abzan': '#F0E68C',      // WBG (Midrange)
    'Jeskai': '#FF69B4',     // URW (Control)
    'Sultai': '#2F4F4F',     // BGU (Midrange)
    'Mardu': '#DC143C',      // RWB (Aggro)
    'Temur': '#20B2AA'       // GUR (Ramp)
};
```

### Mono Colors
```javascript
const MONO_COLORS = {
    'Mono White': '#FFFDD0',
    'Mono Blue': '#4169E1',
    'Mono Black': '#2F4F4F',
    'Mono Red': '#DC143C',
    'Mono Green': '#228B22',
    'Colorless': '#A9A9A9'
};
```

## 📐 Visualization Types & When to Use Them

### 1. **Pie/Donut Chart** - Meta Distribution
**Quand l'utiliser** : Vue globale du métagame actuel
**Insights fournis** : "Quel deck est le plus joué ?"
**Interactivité requise** :
- Click sur une part → Filtrer tous les graphs sur cet archétype
- Hover → Détails (count, %, top players)
- Animation → Transition temporelle

### 2. **Line Chart** - Temporal Evolution
**Quand l'utiliser** : Tendances dans le temps
**Insights fournis** : "Quel deck monte/descend ?"
**Interactivité requise** :
- Zoom temporel (semaine/mois)
- Toggle archetypes on/off
- Hover → Point = tournoi spécifique

### 3. **Heatmap** - Matchup Matrix
**Quand l'utiliser** : Win rates entre archétypes
**Insights fournis** : "Contre quoi mon deck est fort/faible ?"
**Interactivité requise** :
- Click cell → Détails des matchs
- Sort by winrate
- Filter par nombre minimum de matchs

### 4. **Stacked Bar** - Tournament Composition
**Quand l'utiliser** : Composition par tournoi
**Insights fournis** : "Ce tournoi était-il représentatif ?"
**Interactivité requise** :
- Click bar → Voir les decklists
- Compare deux tournois
- Filter par type (Challenge/Qualifier)

### 5. **Scatter Plot** - Performance vs Popularity
**Quand l'utiliser** : Relation entre popularité et succès
**Insights fournis** : "Les decks populaires gagnent-ils ?"
**Interactivité requise** :
- Size = deck count
- Color = archetype
- Click → Deck details

## 🎯 Interaction Patterns

### Click Actions
- **Single Click** : Focus/Filter sur cet élément
- **Double Click** : Reset view
- **Right Click** : Context menu (export, details)

### Hover Effects
- **Always show** : Valeur exacte + contexte
- **Delay** : 200ms (éviter les tooltips accidentels)
- **Position** : Ne jamais cacher la data

### Mobile Gestures
- **Swipe** : Navigate timeline
- **Pinch** : Zoom in/out
- **Tap & Hold** : Equivalent to hover

## 📱 Responsive Design Rules

### Breakpoints
```css
/* Mobile First */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1400px) { /* Wide */ }
```

### Mobile Optimizations
- **Font sizes** : Min 14px
- **Touch targets** : Min 44x44px
- **Graphs** : Stack vertically on mobile
- **Tables** : Horizontal scroll with sticky first column

## ⚡ Performance Guidelines

### Data Loading
- **Initial Load** : < 2s (show skeleton)
- **Interactions** : < 100ms response
- **Animations** : 60fps required

### Progressive Enhancement
1. **Core** : Static image fallback
2. **Enhanced** : Interactive charts
3. **Full** : Real-time updates

## 🚫 Anti-Patterns to Avoid

### ❌ DON'T
- 3D charts (difficiles à lire)
- Animations gratuites (distrayantes)
- Plus de 10 couleurs (confusing)
- Légendes éloignées (context loss)
- Moyennes sans variance (misleading)

### ✅ DO
- 2D avec profondeur via ombres
- Animations avec purpose
- Palette cohérente MTG
- Labels directs quand possible
- Montrer distribution + moyenne

## 📊 Standard Chart Configs

### Chart.js Base Config
```javascript
const BASE_CHART_CONFIG = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 15,
                font: { size: 12 },
                generateLabels: customLabelsWithCounts
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            padding: 12,
            cornerRadius: 8,
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 12 },
            callbacks: {
                label: contextualTooltip
            }
        }
    }
};
```

### Export Options
```javascript
const EXPORT_FORMATS = {
    'PNG': { quality: 0.9, scale: 2 },  // High-res for presentations
    'CSV': { separator: ',', headers: true },
    'JSON': { pretty: true }
};
```

## 🔧 Utility Functions

### Format Percentages
```javascript
function formatPercent(value, total) {
    const pct = (value / total * 100).toFixed(1);
    return `${pct}%`;
}
```

### Adaptive Truncation
```javascript
function truncateLabel(label, maxWidth) {
    // Mobile: 15 chars
    // Tablet: 25 chars  
    // Desktop: Full
    const charLimit = maxWidth < 768 ? 15 : maxWidth < 1024 ? 25 : 100;
    return label.length > charLimit ? 
        label.substring(0, charLimit - 3) + '...' : label;
}
```

## 🎯 Checklist Before Shipping

- [ ] Mobile test on real device
- [ ] Load time < 2s
- [ ] All interactions < 100ms
- [ ] Colors follow MTG standards
- [ ] Export works (PNG/CSV)
- [ ] Tested with 10x data
- [ ] Pro player approved the insight
- [ ] Accessibility (keyboard nav)

---

Remember: **"Comment un pro utiliserait cette viz ?"** should drive every decision.