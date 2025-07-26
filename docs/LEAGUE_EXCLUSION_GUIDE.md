# 🚫 Guide d'Exclusion des Leagues - Manalytics

> **RÈGLE ABSOLUE** : Les leagues (5-0) ne sont PAS des tournois compétitifs et doivent TOUJOURS être exclues des analyses.

## 📋 Table des Matières

1. [Pourquoi exclure les leagues ?](#pourquoi-exclure-les-leagues)
2. [Comment identifier les leagues](#comment-identifier-les-leagues)
3. [Scraping sans leagues](#scraping-sans-leagues)
4. [Nettoyage des leagues existantes](#nettoyage-des-leagues-existantes)
5. [Vérifications régulières](#vérifications-régulières)
6. [Troubleshooting](#troubleshooting)
7. [Checklist complète](#checklist-complète)

---

## 🤔 Pourquoi exclure les leagues ?

Les **MTGO Leagues** sont des résultats filtrés qui ne représentent PAS la réalité du métagame :

- ❌ **Biais de sélection** : Seuls les résultats 5-0 sont publiés
- ❌ **Pas de structure suisse** : Ce sont des matchs de ladder, pas un tournoi
- ❌ **Données incomplètes** : On ne voit pas les decks qui ont perdu
- ❌ **Fausse représentation** : Un deck peut avoir 200 joueurs mais seulement 5 publiés

**Seuls les VRAIS tournois** (Challenges, Qualifiers, Showcases) donnent une image fidèle du métagame.

---

## 🔍 Comment identifier les leagues

### Caractéristiques des fichiers leagues :

1. **Dans le nom du fichier** : Contiennent toujours "league"
   ```
   2025-07-10_vintage-league-2025-07-109390.json
   ```

2. **Dans un dossier séparé** : Souvent dans `leagues/`
   ```
   data/raw/mtgo/standard/leagues/
   ```

3. **Structure des données** : Toujours exactement 5 joueurs (5-0)

### Commande pour les trouver :
```bash
# Lister toutes les leagues
find data/raw -name "*league*" -type f

# Compter les leagues
find data/raw -name "*league*" -type f | wc -l

# Voir les dossiers leagues
find data/raw -type d -name "leagues"
```

---

## ✅ Scraping sans leagues

### 1. **MTGO Scraper - Configuration par défaut**

Le scraper MTGO **exclut les leagues par défaut** ! Il faut juste NE PAS ajouter le flag.

```bash
# ✅ BONNE commande (sans leagues)
python scripts/scrape_all_platforms.py --format standard --days 7

# ❌ MAUVAISE commande (inclut les leagues)
python scripts/scrape_all_platforms.py --format standard --days 7 --include-leagues
```

### 2. **Scraping format par format**

```bash
# Standard sans leagues
python scripts/scrape_mtgo_standalone.py --format standard --days 7

# Modern sans leagues  
python scripts/scrape_mtgo_standalone.py --format modern --days 7

# Legacy sans leagues
python scripts/scrape_mtgo_standalone.py --format legacy --days 7
```

### 3. **Vérifier le code du scraper**

Le scraper a cette logique :
```python
# Dans src/manalytics/scrapers/mtgo/scraper.py
if tournament.tournament_type == "league":
    format_path = format_path / "leagues"  # Stocke dans un dossier séparé

# Et dans les arguments :
parser.add_argument("--include-leagues", action="store_true",
                   help="Include league tournaments")

# Par défaut : args.include_leagues = False
```

---

## 🧹 Nettoyage des leagues existantes

### Méthode complète de nettoyage :

```bash
# 1. D'abord, voir ce qu'on va supprimer
find data/raw -name "*league*" -type f | head -20

# 2. Supprimer TOUS les fichiers leagues
find data/raw -name "*league*" -type f -delete

# 3. Supprimer TOUS les dossiers leagues
find data/raw -type d -name "leagues" -exec rm -rf {} +

# 4. Vérifier que c'est clean
find data/raw -name "*league*" | wc -l  # Doit afficher 0
```

### Après le nettoyage, TOUJOURS reconstruire le cache :

```bash
# 1. Supprimer l'ancien cache
rm -f data/cache/tournaments.db
rm -rf data/cache/decklists/

# 2. Reconstruire avec les données clean
python3 scripts/process_all_standard_data.py

# 3. Régénérer les visualisations
python3 scripts/generate_interactive_viz.py --format standard
```

---

## 🔄 Vérifications régulières

### Script de vérification automatique

Créez ce script `check_leagues.sh` :

```bash
#!/bin/bash
echo "🔍 Vérification des leagues dans le système..."

# Compter les leagues dans raw
LEAGUE_COUNT=$(find data/raw -name "*league*" -type f | wc -l)
echo "Fichiers leagues dans raw: $LEAGUE_COUNT"

if [ $LEAGUE_COUNT -gt 0 ]; then
    echo "⚠️  ATTENTION: Des leagues ont été détectées!"
    echo "Exécutez: find data/raw -name '*league*' -type f -delete"
else
    echo "✅ Aucune league détectée dans raw"
fi

# Vérifier dans la base de données
if [ -f "data/cache/tournaments.db" ]; then
    LEAGUE_DB=$(sqlite3 data/cache/tournaments.db "SELECT COUNT(*) FROM tournaments WHERE name LIKE '%league%';")
    echo "Leagues dans la DB: $LEAGUE_DB"
    
    if [ $LEAGUE_DB -gt 0 ]; then
        echo "⚠️  Des leagues sont dans le cache! Reconstruisez-le."
    fi
fi
```

### Commandes de diagnostic

```bash
# Voir la répartition des tournois par type
sqlite3 data/cache/tournaments.db "
SELECT 
    CASE 
        WHEN name LIKE '%league%' THEN 'league'
        WHEN name LIKE '%challenge%' THEN 'challenge'
        WHEN name LIKE '%qualifier%' THEN 'qualifier'
        ELSE 'other'
    END as type,
    COUNT(*) as count
FROM tournaments 
GROUP BY type;"

# Voir combien de tournois par format (sans leagues)
sqlite3 data/cache/tournaments.db "
SELECT format, COUNT(*) as count 
FROM tournaments 
WHERE name NOT LIKE '%league%'
GROUP BY format 
ORDER BY count DESC;"
```

---

## 🔧 Troubleshooting

### Problème : "Ma visualisation montre 0 decks"

**Cause** : Les decklists n'ont pas été chargées correctement.

**Solution** :
```bash
# 1. Vérifier que les decklists existent
ls -la data/cache/decklists/

# 2. Si le fichier JSON mensuel existe, vérifier son contenu
python3 -c "
import json
data = json.load(open('data/cache/decklists/2025-07.json'))
print(f'Total tournaments: {len(data)}')
standard = [t for t,d in data.items() if d.get('format')=='standard']
print(f'Standard tournaments: {len(standard)}')
"

# 3. Reconstruire le cache si nécessaire
rm -rf data/cache/
python3 scripts/process_all_standard_data.py
```

### Problème : "J'ai scrapé avec --include-leagues par erreur"

**Solution rapide** :
```bash
# Nettoyer et reconstruire en une commande
find data/raw -name "*league*" -type f -delete && \
rm -f data/cache/tournaments.db && \
rm -rf data/cache/decklists/ && \
python3 scripts/process_all_standard_data.py
```

### Problème : "Comment savoir si mon analyse inclut des leagues ?"

**Vérification** :
```bash
# Dans la visualisation HTML
grep -i "league" data/cache/interactive_meta_timeline.html

# Dans la base de données
sqlite3 data/cache/tournaments.db "SELECT name FROM tournaments WHERE name LIKE '%league%' LIMIT 5;"
```

---

## ✅ Checklist complète

### Avant chaque scraping :

- [ ] NE PAS utiliser `--include-leagues`
- [ ] Vérifier qu'il n'y a pas de leagues existantes : `find data/raw -name "*league*" | wc -l`
- [ ] Utiliser la bonne commande : `python scripts/scrape_all_platforms.py --format standard --days X`

### Après chaque scraping :

- [ ] Vérifier l'absence de leagues : `find data/raw -name "*league*"`
- [ ] Si leagues présentes, les supprimer
- [ ] Reconstruire le cache : `python3 scripts/process_all_standard_data.py`

### Pour les analyses :

- [ ] Toujours exclure les tournois avec "league" dans le nom
- [ ] Se concentrer sur : Challenges, Qualifiers, Showcases, PTQs
- [ ] Vérifier les stats : au moins 8 joueurs par tournoi (les leagues en ont toujours 5)

---

## 🎯 Résumé en 3 commandes

```bash
# 1. Scraper SANS leagues
python scripts/scrape_all_platforms.py --format standard --days 7

# 2. Si des leagues existent, les nettoyer
find data/raw -name "*league*" -type f -delete

# 3. Reconstruire le cache propre
rm -f data/cache/tournaments.db && python3 scripts/process_all_standard_data.py
```

---

## 📝 Notes importantes

1. **Le cache lit TOUT** ce qui est dans `data/raw/`, donc si des leagues y sont, elles seront incluses
2. **Les leagues sont stockées séparément** dans des dossiers `leagues/` pour faciliter leur exclusion
3. **Toujours vérifier** après un scraping qu'aucune league n'a été incluse par erreur
4. **En cas de doute**, mieux vaut nettoyer et reconstruire que d'avoir des données biaisées

---

*Dernière mise à jour : 26 Juillet 2025*

*"Les leagues sont l'ennemi d'une analyse compétitive sérieuse. Excluez-les TOUJOURS."*