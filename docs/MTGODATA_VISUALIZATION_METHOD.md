# 📊 Méthode de Visualisation MTGOData - Guide Définitif

## 🎯 Objectif
Créer des visualisations avec l'apparence EXACTE du template de référence `standard_analysis_no_leagues.html` mais en utilisant les données MTGOData avec calcul par MATCHES.

## 📁 Scripts Clés

### 1. **Script Principal : `create_mtgodata_perfect_template.py`**
C'est le script qui génère la visualisation avec :
- Header violet gradient (#667eea → #764ba2)
- 6 stat boxes blanches avec effet hover
- Graphiques Plotly (pie, bar, timeline, table)
- Données MTGOData avec calcul par MATCHES

### 2. **Module Listener : `src/manalytics/listener/listener_reader.py`**
- Lit les données depuis `/Volumes/DataDisk/_VMs/Shared-VM/MTGOData`
- Structure : `year/month/day/tournament_id.json`
- Fournit les matches round par round

### 3. **Template de Référence**
- Fichier : `file:///Volumes/DataDisk/_Downloads/standard_analysis_no_leagues.html`
- Caractéristiques visuelles :
  - Header avec gradient violet
  - Stat boxes individuelles (pas dans une annotation)
  - Design moderne avec rounded corners
  - Effets hover sur les stat boxes

## 🔧 Structure HTML Exacte

```html
<!-- Header avec gradient -->
<div class="header">
    <h1>🎯 Manalytics - Interactive Metagame Analysis</h1>
    <p>Hover for details • Export to PNG/SVG • MTG Color Gradients Preserved</p>
    <div class="controls">
        <button onclick="downloadCSV()">📊 Download CSV</button>
    </div>
</div>

<!-- Stat boxes individuelles -->
<div class="stats">
    <div class="stat-box">
        <div class="stat-value">42</div>
        <div class="stat-label">Total Tournaments</div>
    </div>
    <!-- ... autres stat boxes ... -->
</div>
```

## 🎨 CSS Critique

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.stat-box {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
}

.stat-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-color: #667eea;
}
```

## 📈 Méthode de Calcul par MATCHES

```python
def _calculate_meta_by_matches(self, merged_data: Dict) -> Dict:
    """Calculate meta percentages by MATCHES"""
    archetype_matches = defaultdict(int)
    
    # Chaque match compte pour les 2 archétypes
    for match in merged_data['all_matches']:
        archetype_matches[match['arch1']] += 1
        archetype_matches[match['arch2']] += 1
    
    # Pourcentage basé sur le total des apparitions dans les matches
    total_match_count = sum(archetype_matches.values())
```

## 🚀 Commande d'Exécution

```bash
python3 create_mtgodata_perfect_template.py
```

## 📊 Données Générées
- **Tournois** : 22 (Standard, sans leagues)
- **Decks** : 24 uniques
- **Matches** : 41 valides
- **Période** : 1-21 Juillet 2025

## ⚠️ Points d'Attention
1. **NE PAS** utiliser `archetype_charts.py` - il n'a pas les stat boxes
2. **NE PAS** mettre les stats dans une annotation Plotly
3. **TOUJOURS** avoir le header violet gradient
4. **TOUJOURS** avoir les 6 stat boxes séparées

## 📝 Note Finale
Cette méthode combine :
- L'apparence moderne du template de référence
- Les données MTGOData (listener)
- Le calcul par MATCHES (méthodologie Jiliac)
- Les visualisations Plotly interactives

C'est LA méthode à utiliser pour toutes les visualisations MTGOData futures.