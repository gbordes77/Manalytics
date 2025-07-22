# 🎨 **GUIDE EXPERT : COULEURS OPTIMALES POUR MANALYTICS**

## 🎯 **PHILOSOPHIE GÉNÉRALE**

### **Principe #1 : Hiérarchie Visuelle**
- **Couleurs primaires** → Archétypes dominants (>10% meta share)
- **Couleurs secondaires** → Archétypes moyens (5-10% meta share)
- **Couleurs tertiaires** → Archétypes mineurs (<5% meta share)

### **Principe #2 : Logique Cohérente**
- **Rouge** → Aggro (énergie, vitesse)
- **Bleu** → Contrôle (patience, intelligence)
- **Vert** → Midrange (équilibre, nature)
- **Violet** → Combo (mystère, complexité)
- **Gris** → "Autres/Non classifiés"

---

## 🏆 **PALETTE MANALYTICS OPTIMALE**

### **🎨 Couleurs Primaires (Archétypes Dominants)**
```python
PRIMARY_COLORS = {
    "Izzet Prowess": "#E74C3C",      # Rouge vif - Aggro dominant
    "Azorius Control": "#3498DB",     # Bleu profond - Contrôle dominant
    "Mono Red Aggro": "#C0392B",      # Rouge foncé - Aggro pur
    "Jeskai Control": "#9B59B6",      # Violet - Contrôle complexe
}
```

### **🎨 Couleurs Secondaires (Archétypes Moyens)**
```python
SECONDARY_COLORS = {
    "Dimir Ramp": "#2C3E50",          # Bleu-noir - Contrôle sombre
    "Jeskai Oculus": "#E67E22",       # Orange - Combo-contrôle
    "Azorius Omniscience": "#5DADE2", # Bleu clair - Contrôle alternatif
    "Mono Black Demons": "#34495E",   # Noir - Midrange sombre
}
```

### **🎨 Couleurs Tertiaires (Archétypes Mineurs)**
```python
TERTIARY_COLORS = {
    "Orzhov Selfbounce": "#BDC3C7",   # Gris clair
    "Orzhov Demons": "#85929E",       # Gris moyen
    "Azorius Ramp": "#AED6F1",        # Bleu très clair
    "Mono Red Ramp": "#F1948A",       # Rouge clair
}
```

### **🎨 Couleur Spéciale**
```python
SPECIAL_COLOR = {
    "Autres/Non classifiés": "#95A5A6"  # Gris neutre - JAMAIS couleur vive
}
```

---

## 🔬 **SCIENCE DES COULEURS - POURQUOI CES CHOIX**

### **🧠 Psychologie des Couleurs en Gaming**
- **Rouge** : Agression, vitesse, danger → Parfait pour Aggro
- **Bleu** : Calme, contrôle, intelligence → Parfait pour Contrôle
- **Vert** : Équilibre, nature → Parfait pour Midrange
- **Violet** : Mystère, complexité → Parfait pour Combo
- **Gris** : Neutralité → Parfait pour "Autres"

### **🎨 Contraste et Accessibilité**
- **Deuteranopia** (daltonisme rouge-vert) : Éviter rouge/vert adjacents
- **Protanopia** (daltonisme rouge) : Utiliser bleu/orange comme alternative
- **Tritanopia** (daltonisme bleu-jaune) : Éviter bleu/jaune adjacents

---

## 🏆 **MATRICES DE MATCHUPS - SYSTÈME EXPERT**

### **❌ Problème Actuel :**
- Échelle vert-jaune-rouge = 8% de la population ne peut pas distinguer
- Pas assez de contraste entre valeurs proches
- Rouge utilisé pour 60%+ (pas assez extrême)

### **✅ Solution Experte :**
```python
MATCHUP_MATRIX_COLORS = {
    "scale": "RdYlBu_r",  # Recommandation ColorBrewer
    "range": [0, 100],
    "midpoint": 50,
    "colors": {
        "0-35%": "#D73027",    # Rouge intense - Défavorable
        "35-45%": "#F46D43",   # Orange-rouge - Légèrement défavorable
        "45-55%": "#FEE08B",   # Jaune clair - Équilibré
        "55-65%": "#D9EF8B",   # Vert clair - Légèrement favorable
        "65-100%": "#4575B4",  # Bleu intense - Très favorable
    }
}
```

---

## 🎯 **IMPLÉMENTATION PRATIQUE**

### **🔧 Code Plotly Optimisé**
```python
import plotly.express as px
import plotly.graph_objects as go

# Couleurs optimales par archétype
MANALYTICS_COLORS = {
    "Izzet Prowess": "#E74C3C",
    "Azorius Control": "#3498DB",
    "Mono Red Aggro": "#C0392B",
    "Jeskai Control": "#9B59B6",
    "Dimir Ramp": "#2C3E50",
    "Jeskai Oculus": "#E67E22",
    "Azorius Omniscience": "#5DADE2",
    "Mono Black Demons": "#34495E",
    "Autres/Non classifiés": "#95A5A6"
}

def create_optimized_pie_chart(data):
    # Trier par pourcentage pour hiérarchie visuelle
    data_sorted = data.sort_values('percentage', ascending=False)

    # Couleurs selon la hiérarchie
    colors = [MANALYTICS_COLORS.get(arch, "#BDC3C7") for arch in data_sorted['archetype']]

    fig = go.Figure(data=[go.Pie(
        labels=data_sorted['archetype'],
        values=data_sorted['percentage'],
        marker=dict(colors=colors),
        textfont=dict(size=12, color='white')
    )])

    return fig
```

---

## 📊 **CHECKLIST COULEURS AVANT PUBLICATION**

### **✅ Questions à se poser :**
1. **Hiérarchie** : Les couleurs les plus vives sont-elles sur les données importantes ?
2. **Logique** : Y a-t-il une cohérence dans l'attribution des couleurs ?
3. **Accessibilité** : Un daltonien peut-il comprendre le graphique ?
4. **Contraste** : Peut-on distinguer toutes les valeurs facilement ?
5. **Légende** : La légende est-elle claire et ordonnée ?

### **✅ Tests de Validation :**
```python
# Test daltonisme
from colorspacious import cspace_convert
def test_colorblind_accessibility(colors):
    # Convertir en espace colorimétrique accessible
    pass

# Test contraste
def test_contrast_ratio(color1, color2):
    # Calculer ratio de contraste WCAG
    pass
```

---

## 🎨 **RESSOURCES AVANCÉES**

### **🔗 Outils Recommandés :**
- **ColorBrewer 2.0** : Palettes scientifiquement validées
- **Coblis** : Simulateur de daltonisme
- **Contrast Checker** : Validation WCAG
- **Adobe Color** : Création de palettes harmonieuses

### **📚 Références Scientifiques :**
- Cynthia Brewer : "Designing Better Maps with ColorBrewer"
- Maureen Stone : "A Field Guide to Digital Color"
- Edward Tufte : "The Visual Display of Quantitative Information"

---

## 🏆 **CONCLUSION**

Ces recommandations transformeront vos visualisations en outils professionnels, accessibles et percutants. L'objectif est que chaque graphique raconte une histoire claire grâce à des couleurs optimisées.

**Prochaine étape** : Implémentation dans le code Manalytics !
