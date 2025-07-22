# 🎨 GESTION COMPLÈTE DES COULEURS D'ARCHÉTYPES

> **Document critique pour le handoff** - Système de couleurs/guildes pour classification automatique

---

## 🎯 **VUE D'ENSEMBLE DU SYSTÈME**

### **Problème résolu :**
Transformer les archétypes simples ("Prowess") en archétypes avec couleurs ("Izzet Prowess") pour améliorer la classification et réduire les catégories "Autres/Non classifiés".

### **Objectif :**
- **Réduction des "Autres"** : De 15% à 5% des decks
- **Classification précise** : "Prowess" → "Izzet Prowess", "Grixis Prowess", etc.
- **Cohérence visuelle** : Couleurs cohérentes dans tous les graphiques
- **Standards industrie** : Niveau MTGGoldfish, 17lands, Untapped.gg

---

## 🏗️ **ARCHITECTURE DU SYSTÈME**

### **Composants principaux :**
```python
# Architecture du système de couleurs
src/python/classifier/
├── archetype_engine.py
│   ├── ColorIntegrationSystem
│   ├── detect_deck_colors()
│   ├── integrate_colors_with_archetype()
│   └── apply_color_overrides()
├── color_overrides.json      # Règles spéciales
├── guild_mapping.json        # Mapping couleurs → guildes
└── color_detection_rules.py  # Logique de détection
```

### **Workflow complet :**
```
1. Deck Input → 2. Color Detection → 3. Archetype Classification → 4. Color Integration → 5. Final Archetype
```

---

## 🔍 **ÉTAPE 1 : DÉTECTION DES COULEURS**

### **Algorithme de détection :**
```python
def detect_deck_colors(self, deck):
    """Détecte les couleurs d'un deck basé sur les cartes"""

    # 1. Extraction des cartes
    mainboard = deck.get("Mainboard", [])
    sideboard = deck.get("Sideboard", [])
    all_cards = mainboard + sideboard

    # 2. Détection des couleurs par carte
    color_counts = {
        "W": 0, "U": 0, "B": 0, "R": 0, "G": 0
    }

    for card in all_cards:
        card_colors = self.get_card_colors(card["Name"])
        for color in card_colors:
            color_counts[color] += card["Count"]

    # 3. Détermination des couleurs principales
    threshold = sum(color_counts.values()) * 0.1  # 10% minimum
    deck_colors = [
        color for color, count in color_counts.items()
        if count >= threshold
    ]

    return sorted(deck_colors)  # Ordre WUBRG
```

### **Règles de détection :**
```python
# Règles de détection des couleurs
COLOR_DETECTION_RULES = {
    "Lands": {
        "Plains": ["W"],
        "Island": ["U"],
        "Swamp": ["B"],
        "Mountain": ["R"],
        "Forest": ["G"],
        "Steam Vents": ["U", "R"],
        "Blood Crypt": ["B", "R"],
        # ... etc
    },
    "Spells": {
        "Lightning Bolt": ["R"],
        "Thoughtseize": ["B"],
        "Path to Exile": ["W"],
        "Counterspell": ["U"],
        "Llanowar Elves": ["G"],
        # ... etc
    }
}
```

---

## 🎨 **ÉTAPE 2 : MAPPING COULEURS → GUILDES**

### **Système de guildes :**
```python
# Mapping des couleurs vers les guildes
GUILD_MAPPING = {
    # Mono-color
    ["W"]: "White",
    ["U"]: "Blue",
    ["B"]: "Black",
    ["R"]: "Red",
    ["G"]: "Green",

    # Dual-color (guildes)
    ["W", "U"]: "Azorius",
    ["W", "B"]: "Orzhov",
    ["W", "R"]: "Boros",
    ["W", "G"]: "Selesnya",
    ["U", "B"]: "Dimir",
    ["U", "R"]: "Izzet",
    ["U", "G"]: "Simic",
    ["B", "R"]: "Rakdos",
    ["B", "G"]: "Golgari",
    ["R", "G"]: "Gruul",

    # Tri-color (shards/wedges)
    ["W", "U", "B"]: "Esper",
    ["W", "U", "R"]: "Jeskai",
    ["W", "U", "G"]: "Bant",
    ["W", "B", "R"]: "Mardu",
    ["W", "B", "G"]: "Abzan",
    ["W", "R", "G"]: "Naya",
    ["U", "B", "R"]: "Grixis",
    ["U", "B", "G"]: "Sultai",
    ["U", "R", "G"]: "Temur",
    ["B", "R", "G"]: "Jund",

    # 4+ couleurs
    ["W", "U", "B", "R"]: "Yore-Tiller",
    ["W", "U", "B", "G"]: "Ink-Treader",
    ["W", "U", "R", "G"]: "Glint-Eye",
    ["W", "B", "R", "G"]: "Dune-Brood",
    ["U", "B", "R", "G"]: "Witch-Maw",
    ["W", "U", "B", "R", "G"]: "5-Color"
}
```

### **Fichier de configuration :**
```json
// guild_mapping.json
{
  "mono": {
    "W": "White",
    "U": "Blue",
    "B": "Black",
    "R": "Red",
    "G": "Green"
  },
  "dual": {
    "WU": "Azorius",
    "WB": "Orzhov",
    "WR": "Boros",
    "WG": "Selesnya",
    "UB": "Dimir",
    "UR": "Izzet",
    "UG": "Simic",
    "BR": "Rakdos",
    "BG": "Golgari",
    "RG": "Gruul"
  },
  "tri": {
    "WUB": "Esper",
    "WUR": "Jeskai",
    "WUG": "Bant",
    "WBR": "Mardu",
    "WBG": "Abzan",
    "WRG": "Naya",
    "UBR": "Grixis",
    "UBG": "Sultai",
    "URG": "Temur",
    "BRG": "Jund"
  }
}
```

---

## 🔧 **ÉTAPE 3 : INTÉGRATION COULEURS + ARCHÉTYPES**

### **Système d'intégration :**
```python
class ColorIntegrationSystem:
    def __init__(self):
        self.color_overrides = self.load_color_overrides()
        self.guild_mapping = self.load_guild_mapping()

    def integrate_colors_with_archetype(self, archetype, deck_colors):
        """Intègre les couleurs avec l'archétype"""

        # 1. Vérifier les overrides
        if archetype in self.color_overrides:
            return self.apply_color_override(archetype, deck_colors)

        # 2. Détecter la guilde
        guild = self.detect_guild(deck_colors)

        # 3. Construire le nom final
        if guild and guild != "5-Color":
            return f"{guild} {archetype}"
        else:
            return archetype

    def apply_color_override(self, archetype, deck_colors):
        """Applique les règles spéciales"""
        override = self.color_overrides[archetype]

        if override["type"] == "force_color":
            return f"{override['color']} {archetype}"
        elif override["type"] == "conditional":
            if self.matches_condition(deck_colors, override["condition"]):
                return f"{override['color']} {archetype}"
            else:
                return archetype
```

### **Règles spéciales (overrides) :**
```json
// color_overrides.json
{
  "Burn": {
    "type": "conditional",
    "condition": "contains_red",
    "color": "Red",
    "description": "Burn est toujours Red sauf si pas de rouge"
  },
  "Control": {
    "type": "conditional",
    "condition": "blue_dominant",
    "color": "Blue",
    "description": "Control est Blue si majorité de bleu"
  },
  "Tron": {
    "type": "force_color",
    "color": "Green",
    "description": "Tron est toujours Green"
  },
  "Prowess": {
    "type": "guild_based",
    "description": "Prowess prend la guilde dominante"
  }
}
```

---

## 📊 **ÉTAPE 4 : VALIDATION ET COHÉRENCE**

### **Système de validation :**
```python
def validate_color_integration(self, original_archetype, final_archetype, deck_colors):
    """Valide la cohérence de l'intégration"""

    validation_rules = {
        "color_consistency": self.check_color_consistency(final_archetype, deck_colors),
        "naming_convention": self.check_naming_convention(final_archetype),
        "guild_accuracy": self.check_guild_accuracy(final_archetype, deck_colors),
        "override_compliance": self.check_override_compliance(original_archetype, final_archetype)
    }

    return validation_rules

def check_color_consistency(self, archetype, deck_colors):
    """Vérifie que les couleurs correspondent"""
    archetype_colors = self.extract_colors_from_archetype(archetype)
    return set(archetype_colors).issubset(set(deck_colors))
```

### **Métriques de qualité :**
```python
# Métriques de validation
VALIDATION_METRICS = {
    "color_accuracy": 0.95,      # 95% de précision
    "guild_consistency": 0.92,   # 92% de cohérence
    "override_compliance": 0.98, # 98% de respect des règles
    "naming_standard": 0.90      # 90% de conformité
}
```

---

## 🎯 **EXEMPLES CONCRETS**

### **Exemple 1 : Prowess → Izzet Prowess**
```python
# Input
deck_colors = ["U", "R"]
original_archetype = "Prowess"

# Processus
guild = detect_guild(["U", "R"])  # "Izzet"
final_archetype = f"{guild} {original_archetype}"  # "Izzet Prowess"

# Validation
check_color_consistency("Izzet Prowess", ["U", "R"])  # ✅ True
```

### **Exemple 2 : Burn → Red Burn**
```python
# Input
deck_colors = ["R"]
original_archetype = "Burn"

# Processus
override = color_overrides["Burn"]  # force_color: "Red"
final_archetype = f"{override['color']} {original_archetype}"  # "Red Burn"

# Validation
check_override_compliance("Burn", "Red Burn")  # ✅ True
```

### **Exemple 3 : Control → Blue Control**
```python
# Input
deck_colors = ["U", "W", "B"]
original_archetype = "Control"

# Processus
if blue_dominant(deck_colors):  # True (U majoritaire)
    final_archetype = "Blue Control"
else:
    final_archetype = "Control"

# Validation
check_guild_accuracy("Blue Control", ["U", "W", "B"])  # ✅ True
```

---

## 🔧 **CONFIGURATION ET MAINTENANCE**

### **Fichiers de configuration :**
```bash
# Structure des fichiers de configuration
config/
├── color_overrides.json     # Règles spéciales
├── guild_mapping.json       # Mapping couleurs → guildes
├── color_detection_rules.py # Logique de détection
└── validation_rules.py      # Règles de validation
```

### **Maintenance des règles :**
```python
# Ajouter une nouvelle règle
def add_color_override(self, archetype, override_rule):
    """Ajoute une nouvelle règle de couleur"""
    self.color_overrides[archetype] = override_rule
    self.save_color_overrides()

# Exemple d'ajout
new_rule = {
    "type": "conditional",
    "condition": "contains_black",
    "color": "Black",
    "description": "Nouvel archétype noir"
}
add_color_override("NewArchetype", new_rule)
```

### **Tests et validation :**
```python
# Tests unitaires pour le système de couleurs
def test_color_integration():
    test_cases = [
        {
            "deck_colors": ["U", "R"],
            "archetype": "Prowess",
            "expected": "Izzet Prowess"
        },
        {
            "deck_colors": ["R"],
            "archetype": "Burn",
            "expected": "Red Burn"
        },
        {
            "deck_colors": ["U", "W", "B"],
            "archetype": "Control",
            "expected": "Blue Control"
        }
    ]

    for test in test_cases:
        result = integrate_colors_with_archetype(
            test["archetype"],
            test["deck_colors"]
        )
        assert result == test["expected"]
```

---

## 🚨 **POINTS CRITIQUES POUR LE HANDOFF**

### **⚠️ Règles absolues :**
1. **"Autres/Non classifiés"** : Toujours en gris neutre #95A5A6
2. **Ordre des couleurs** : WUBRG (White, Blue, Black, Red, Green)
3. **Cohérence** : Même nom d'archétype partout
4. **Validation** : Toujours vérifier la cohérence

### **🔧 Code critique :**
```python
# Fichiers essentiels à comprendre
src/python/classifier/archetype_engine.py
├── ColorIntegrationSystem class
├── detect_deck_colors() method
├── integrate_colors_with_archetype() method
└── apply_color_overrides() method

config/
├── color_overrides.json
└── guild_mapping.json
```

### **📊 Données critiques :**
```python
# Données à maintenir
color_overrides.json  # Règles spéciales
guild_mapping.json    # Mapping couleurs → guildes
color_detection_rules.py  # Logique de détection
```

### **🎯 Tests obligatoires :**
```bash
# Tests à exécuter avant tout changement
python -m pytest tests/test_color_integration.py
python -m pytest tests/test_archetype_classification.py
python scripts/validate_color_consistency.py
```

---

## 📈 **MÉTRIQUES DE PERFORMANCE**

### **Objectifs de qualité :**
```yaml
Performance targets:
  color_accuracy: 95%      # Précision de détection
  guild_consistency: 92%   # Cohérence des guildes
  override_compliance: 98% # Respect des règles
  naming_standard: 90%     # Conformité des noms
  reduction_others: 70%    # Réduction des "Autres"
```

### **Monitoring :**
```python
# Métriques à surveiller
def monitor_color_system():
    metrics = {
        "color_detection_accuracy": calculate_accuracy(),
        "guild_classification_rate": calculate_guild_rate(),
        "others_reduction": calculate_others_reduction(),
        "naming_consistency": calculate_consistency()
    }
    return metrics
```

---

## 🎯 **CHECKLIST POUR LE NOUVEL ÉQUIPIER**

### **✅ Compréhension du système :**
- [ ] Comprend le workflow de détection des couleurs
- [ ] Maîtrise le mapping couleurs → guildes
- [ ] Connaît les règles d'override
- [ ] Sait valider la cohérence

### **✅ Maintenance :**
- [ ] Peut ajouter de nouvelles règles
- [ ] Sait modifier le mapping des guildes
- [ ] Connaît les tests à exécuter
- [ ] Maîtrise la validation

### **✅ Dépannage :**
- [ ] Sait diagnostiquer les problèmes de couleurs
- [ ] Connaît les logs de debug
- [ ] Peut corriger les incohérences
- [ ] Sait valider les corrections

---

## 🚀 **PROCHAINES ÉTAPES**

### **Améliorations prévues :**
1. **ML pour détection** : Classification automatique des couleurs
2. **Validation avancée** : Tests de cohérence automatisés
3. **Interface admin** : Gestion des règles via interface web
4. **Analytics** : Métriques détaillées de performance

### **Maintenance continue :**
1. **Mise à jour des règles** : Nouveaux archétypes
2. **Validation régulière** : Tests hebdomadaires
3. **Monitoring** : Surveillance des métriques
4. **Documentation** : Mise à jour des règles

---

*Document créé pour le handoff - Système critique pour la classification des archétypes*

*Dernière mise à jour : 14 janvier 2025*
*Status : Système opérationnel - Maintenance requise*
