# 📐 MÉTHODE DE RÉFÉRENCE - CALCULS JILIAC

> **⚠️ DOCUMENT DE RÉFÉRENCE OFFICIEL**
> 
> CE DOCUMENT DÉFINIT LA **SEULE ET UNIQUE** MÉTHODE DE CALCUL À UTILISER
> POUR TOUTES LES ANALYSES DE MÉTAGAME DANS LE PROJET MANALYTICS
> 
> **TOUTE ANALYSE DOIT UTILISER CES FORMULES EXACTES**

## 🎯 MÉTHODE JILIAC - FORMULES OFFICIELLES

### 1. CALCUL DE LA PRÉSENCE (Presence)

```python
def calculate_presence(archetype_matches: int, total_matches_all_archetypes: int) -> float:
    """
    FORMULE OFFICIELLE de la présence dans le métagame
    
    Args:
        archetype_matches: Nombre de matches joués par l'archétype
        total_matches_all_archetypes: Somme totale des matches de TOUS les archétypes
    
    Returns:
        Pourcentage de présence dans le métagame
    """
    return (archetype_matches / total_matches_all_archetypes) * 100
```

**⚠️ ATTENTION** : 
- `archetype_matches` = wins + losses + draws de l'archétype
- `total_matches_all_archetypes` = somme de TOUS les matches de TOUS les archétypes
- Chaque match est compté 2 fois (1 fois par joueur)

### 2. CALCUL DU WIN RATE

```python
def calculate_win_rate(wins: int, losses: int) -> float:
    """
    FORMULE OFFICIELLE du win rate
    
    IMPORTANT: Les draws ne sont PAS inclus dans le calcul !
    
    Args:
        wins: Nombre de victoires
        losses: Nombre de défaites
    
    Returns:
        Pourcentage de victoire
    """
    total_games = wins + losses
    if total_games == 0:
        return 50.0
    return (wins * 100) / total_games
```

**⚠️ RÈGLE ABSOLUE** : Les draws (matchs nuls) NE COMPTENT PAS dans le win rate

### 3. NORMALISATION DES MÉTRIQUES

```python
def normalize_presence(presences: List[float]) -> List[float]:
    """
    FORMULE OFFICIELLE de normalisation de la présence
    Utilise une transformation logarithmique
    """
    min_presence = min(presences)
    # Étape 1 : Transformation log
    log_presences = [np.log(p) - np.log(min_presence) for p in presences]
    # Étape 2 : Normalisation [0,1]
    max_log = max(log_presences)
    if max_log == 0:
        return [0] * len(presences)
    return [lp / max_log for lp in log_presences]

def normalize_win_rate(win_rates: List[float]) -> List[float]:
    """
    FORMULE OFFICIELLE de normalisation du win rate
    Transformation linéaire simple
    """
    min_wr = min(win_rates)
    # Étape 1 : Décalage au zéro
    shifted_wrs = [wr - min_wr for wr in win_rates]
    # Étape 2 : Normalisation [0,1]
    max_shifted = max(shifted_wrs)
    if max_shifted == 0:
        return [0] * len(win_rates)
    return [swr / max_shifted for swr in shifted_wrs]
```

### 4. SCORE COMPOSITE

```python
def calculate_composite_score(normalized_presence: float, normalized_win_rate: float) -> float:
    """
    FORMULE OFFICIELLE du score composite
    """
    return normalized_presence + normalized_win_rate
```

### 5. INTERVALLES DE CONFIANCE

```python
def calculate_wilson_ci(wins: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    FORMULE OFFICIELLE pour l'intervalle de confiance Wilson
    """
    if total == 0:
        return 0, 100
        
    p = wins / total
    z = 1.96  # Pour 95% de confiance
    
    denominator = 1 + z**2/total
    center = (p + z**2/(2*total)) / denominator
    margin = z * math.sqrt(p*(1-p)/total + z**2/(4*total**2)) / denominator
    
    ci_lower = max(0, (center - margin) * 100)
    ci_upper = min(100, (center + margin) * 100)
    
    return ci_lower, ci_upper
```

### 6. SYSTÈME DE TIERS JILIAC

```python
def assign_tier(ci_lower: float, mean_ci: float, sd_ci: float) -> str:
    """
    FORMULE OFFICIELLE d'assignation des tiers
    Basée sur la borne inférieure de l'intervalle de confiance
    
    Args:
        ci_lower: Borne inférieure de l'IC du win rate
        mean_ci: Moyenne des CI lower de tous les archétypes
        sd_ci: Écart-type des CI lower
    
    Returns:
        Tier assigné (0, 0.5, 1, 1.5, 2, 2.5, 3, ou Other)
    """
    if ci_lower >= mean_ci + 3 * sd_ci:
        return "0"     # Elite
    elif ci_lower >= mean_ci + 2 * sd_ci:
        return "0.5"   # Très fort
    elif ci_lower >= mean_ci + 1 * sd_ci:
        return "1"     # Fort
    elif ci_lower >= mean_ci:
        return "1.5"   # Au-dessus de la moyenne
    elif ci_lower >= mean_ci - 1 * sd_ci:
        return "2"     # Moyen
    elif ci_lower >= mean_ci - 2 * sd_ci:
        return "2.5"   # Faible
    elif ci_lower >= mean_ci - 3 * sd_ci:
        return "3"     # Très faible
    else:
        return "Other" # Hors catégorie
```

## 📊 EXEMPLE D'APPLICATION COMPLÈTE

```python
# 1. Calculer les métriques de base pour chaque archétype
for archetype in archetypes:
    presence = calculate_presence(archetype.matches, total_matches)
    win_rate = calculate_win_rate(archetype.wins, archetype.losses)
    ci_lower, ci_upper = calculate_wilson_ci(archetype.wins, archetype.wins + archetype.losses)

# 2. Filtrer les archétypes > 2% de présence
filtered = [arch for arch in archetypes if arch.presence > 2.0]

# 3. Normaliser
all_presences = [arch.presence for arch in filtered]
all_win_rates = [arch.win_rate for arch in filtered]
norm_presences = normalize_presence(all_presences)
norm_win_rates = normalize_win_rate(all_win_rates)

# 4. Calculer les scores composites
for i, arch in enumerate(filtered):
    arch.normalized_presence = norm_presences[i]
    arch.normalized_win_rate = norm_win_rates[i]
    arch.composite_score = calculate_composite_score(norm_presences[i], norm_win_rates[i])

# 5. Calculer les tiers
ci_lowers = [arch.ci_lower for arch in filtered]
mean_ci = np.mean(ci_lowers)
sd_ci = np.std(ci_lowers, ddof=1)  # Écart-type échantillon

for arch in filtered:
    arch.tier = assign_tier(arch.ci_lower, mean_ci, sd_ci)
```

## ⚠️ ERREURS À NE JAMAIS FAIRE

1. ❌ **NE JAMAIS** inclure les draws dans le calcul du win rate
2. ❌ **NE JAMAIS** oublier de diviser par 2 si on veut le nombre de matches uniques
3. ❌ **NE JAMAIS** utiliser une autre méthode de normalisation
4. ❌ **NE JAMAIS** calculer les tiers autrement que par la borne inférieure de l'IC
5. ❌ **NE JAMAIS** utiliser un seuil autre que 2% pour filtrer

## 📝 RÉFÉRENCES

- **Source originale** : [R-Meta-Analysis de Jiliac](https://github.com/Jiliac/R-Meta-Analysis)
- **Fichier principal** : `Scripts/Imports/Functions/03-Metagame_Data_Treatment.R`
- **Lignes clés** :
  - Presence : ligne 224
  - Win Rate : lignes 227-228
  - Normalisation : lignes 333-356
  - Tiers : lignes 427-445

---

**CE DOCUMENT FAIT LOI. TOUTE DÉVIATION DOIT ÊTRE JUSTIFIÉE ET DOCUMENTÉE.**