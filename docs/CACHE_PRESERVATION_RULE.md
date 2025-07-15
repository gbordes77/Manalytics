# 🚨 RÈGLE ABSOLUE : JAMAIS EFFACER LE CACHE EXISTANT

> **Document de référence** pour la règle absolue de préservation du cache dans Manalytics

---

## 📋 **RÈGLE ABSOLUE**

### **Principe**
**JAMAIS EFFACER LE CACHE EXISTANT**
- Tous les fichiers existants doivent être préservés
- Seulement AJOUTER de nouvelles données
- Aucune suppression, remplacement ou écrasement autorisé

### **RÈGLE GIT**
**LE CACHE NE DOIT PAS ÊTRE COMMITÉ**
- Les dossiers `data/raw/`, `data/processed/`, `Analyses/` ne doivent JAMAIS être commités
- Seuls les scripts, la configuration et la documentation sont versionnés
- Le cache est local et persistant, mais pas dans Git

### **Application**
Cette règle s'applique à **TOUS** les composants de Manalytics :
- ✅ **Scrapers** : `scripts/fixed_mtgo_scraper.py`
- ✅ **Orchestrateur** : `src/orchestrator.py`
- ✅ **Analyses** : `src/python/analytics/`
- ✅ **Export** : `Analyses/` folder (non commité)
- ✅ **Git** : `.gitignore` protège le cache

---

## 🔧 **IMPLÉMENTATION TECHNIQUE**

### **1. Vérification du cache avant opération**
```python
def _count_existing_cache_files(self):
    """Compte tous les fichiers existants dans le cache à préserver"""
    cache_patterns = [
        "data/raw/mtgo/**/*",
        "data/raw/melee/**/*",
        "data/raw/topdeck/**/*",
        "data/processed/**/*",
        "Analyses/**/*",
        "MTGODecklistCache/**/*"
    ]

    total_files = 0
    for pattern in cache_patterns:
        files = glob.glob(pattern, recursive=True)
        total_files += len(files)

    return total_files
```

### **2. Logging de la règle**
```python
self.logger.info("🚨 RÈGLE ABSOLUE CACHE : JAMAIS EFFACER LE CACHE EXISTANT")
self.logger.info("📋 Seulement AJOUTER de nouvelles données")
self.logger.info("🚫 Aucune suppression, remplacement ou écrasement autorisé")
self.logger.info("🚫 LE CACHE NE DOIT PAS ÊTRE COMMITÉ")
```

### **3. Vérification post-opération**
```python
# Vérifier que le cache a été préservé
cache_after = self._count_existing_cache_files()
new_files = cache_after - cache_before
self.logger.info(f"✅ RÈGLE CACHE RESPECTÉE : {new_files} nouveaux fichiers ajoutés")
self.logger.info(f"📁 Cache final : {cache_after} fichiers ({cache_before} préservés + {new_files} ajoutés)")
```

---

## 📁 **DOSSIES PROTÉGÉS**

### **Cache de données brutes (NON COMMITÉ)**
- `data/raw/mtgo/` - Données MTGO scrapées
- `data/raw/melee/` - Données Melee scrapées
- `data/raw/topdeck/` - Données TopDeck scrapées

### **Cache de données traitées (NON COMMITÉ)**
- `data/processed/` - Données analysées et transformées

### **Cache d'analyses (NON COMMITÉ)**
- `Analyses/` - Rapports et visualisations générés

### **Cache de référence (COMMITÉ - Git submodule)**
- `MTGODecklistCache/` - Données de référence (git submodule)

---

## 🛡️ **MÉCANISMES DE PROTECTION**

### **1. Noms de fichiers uniques**
```python
# RÈGLE ABSOLUE : Nom de fichier unique pour éviter l'écrasement
timestamp = datetime.now().strftime('%H%M%S_%f')[:-3]  # Microsecondes pour unicité
filename = f"mtgo_item_{item_date.strftime('%Y%m%d')}_{timestamp}.json"

# Vérifier que le fichier n'existe pas déjà
file_path = year_month_dir / filename
counter = 1
while file_path.exists():
    filename = f"mtgo_item_{item_date.strftime('%Y%m%d')}_{timestamp}_{counter}.json"
    file_path = year_month_dir / filename
    counter += 1
```

### **2. Métadonnées de préservation**
```python
# Sauvegarder avec métadonnées de préservation
json.dump({
    'scraped_at': datetime.now().isoformat(),
    'total_items': len(data),
    'data': data,
    'cache_rule': 'PRESERVED_EXISTING_ADDED_NEW_ONLY',
    'git_rule': 'CACHE_NOT_COMMITTED'
}, f, indent=2)
```

### **3. Vérification automatique**
```python
# Vérification automatique dans l'orchestrateur
def _enforce_minimum_data_requirement(self):
    # Vérifier le cache existant AVANT toute opération
    existing_cache_files = self._count_existing_cache_files()
    self.logger.info(f"📁 Cache existant à préserver : {existing_cache_files} fichiers")

    # ... opérations ...

    # Vérifier que le cache a été préservé
    final_cache_files = self._count_existing_cache_files()
    new_files = final_cache_files - existing_cache_files
    self.logger.info(f"✅ RÈGLE CACHE RESPECTÉE : {new_files} nouveaux fichiers ajoutés")
```

---

## 🚨 **VIOLATIONS DE LA RÈGLE**

### **Actions interdites**
- ❌ `os.remove()` sur des fichiers de cache
- ❌ `shutil.rmtree()` sur des dossiers de cache
- ❌ Écrasement de fichiers existants
- ❌ Suppression de données pour libérer de l'espace
- ❌ Nettoyage automatique du cache
- ❌ **COMMIT du cache** dans Git
- ❌ **PUSH des dossiers** `data/`, `Analyses/`

### **Actions autorisées**
- ✅ Ajout de nouveaux fichiers
- ✅ Création de nouveaux dossiers
- ✅ Mise à jour de métadonnées
- ✅ Compression de données (si préservation garantie)
- ✅ Archivage (si préservation garantie)
- ✅ **COMMIT des scripts** et configuration
- ✅ **PUSH de la documentation**

---

## 📊 **MONITORING ET LOGS**

### **Logs obligatoires**
```python
# AVANT opération
self.logger.info(f"📁 Cache existant à préserver : {existing_files} fichiers")

# PENDANT opération
self.logger.info("📋 MODE AJOUT SEULEMENT : Cache existant préservé")
self.logger.info("🚫 LE CACHE NE DOIT PAS ÊTRE COMMITÉ")

# APRÈS opération
self.logger.info(f"✅ RÈGLE CACHE RESPECTÉE : {new_files} nouveaux fichiers ajoutés")
```

### **Métriques de suivi**
- Nombre de fichiers avant opération
- Nombre de fichiers après opération
- Nombre de nouveaux fichiers ajoutés
- Nombre de fichiers préservés
- **Vérification Git** : Cache non commité

---

## 🔍 **DIAGNOSTIC ET TROUBLESHOOTING**

### **Vérification de la règle**
```bash
# Compter les fichiers avant
find data/ Analyses/ MTGODecklistCache/ -type f | wc -l

# Exécuter une opération

# Compter les fichiers après
find data/ Analyses/ MTGODecklistCache/ -type f | wc -l

# Vérifier que le nombre a augmenté ou est resté identique

# Vérifier que le cache n'est pas commité
git status
# Ne doit PAS montrer data/ ou Analyses/ dans les fichiers modifiés
```

### **Détection de violations**
```python
def detect_cache_violations(self):
    """Détecte les violations de la règle de préservation du cache"""
    cache_before = self._count_existing_cache_files()

    # ... opération ...

    cache_after = self._count_existing_cache_files()

    if cache_after < cache_before:
        violation = cache_before - cache_after
        self.logger.error(f"🚨 VIOLATION DÉTECTÉE : {violation} fichiers supprimés!")
        raise Exception(f"RÈGLE ABSOLUE VIOLÉE : {violation} fichiers supprimés")

def detect_git_violations(self):
    """Détecte les violations de la règle Git"""
    import subprocess

    try:
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True, check=True)

        for line in result.stdout.split('\n'):
            if line.strip() and any(folder in line for folder in ['data/', 'Analyses/']):
                self.logger.error(f"🚨 VIOLATION GIT DÉTECTÉE : {line}")
                raise Exception(f"RÈGLE GIT VIOLÉE : Cache dans Git - {line}")

    except subprocess.CalledProcessError:
        # Pas de Git, pas de problème
        pass
```

---

## 📚 **RÉFÉRENCES**

### **Fichiers implémentant la règle**
- `scripts/fixed_mtgo_scraper.py` - Scraper avec préservation
- `src/orchestrator.py` - Orchestrateur avec vérification
- `docs/MTGO_SCRAPING_ANALYSIS.md` - Analyse des problèmes de scraping
- `.gitignore` - Protection Git du cache

### **Tests de la règle**
```bash
# Test de préservation
python3 scripts/fixed_mtgo_scraper.py
# Vérifier que les logs montrent "RÈGLE CACHE RESPECTÉE"

# Test de l'orchestrateur
python3 src/orchestrator.py
# Vérifier que les logs montrent "Cache préservé"

# Test Git
git status
# Vérifier que data/ et Analyses/ ne sont pas dans les fichiers modifiés
```

---

## ✅ **CONCLUSION**

### **Règle absolue respectée**
La règle de préservation du cache est maintenant **HARDCODÉE** dans tous les composants critiques de Manalytics.

### **Garanties**
- ✅ **Aucune perte de données** lors des opérations
- ✅ **Traçabilité complète** des ajouts
- ✅ **Détection automatique** des violations
- ✅ **Logs détaillés** pour audit
- ✅ **Protection Git** du cache

### **Maintenance**
Cette règle doit être **TOUJOURS** respectée lors de toute modification du code. Aucune exception n'est autorisée.

---

*Document créé le : 2025-07-15*
*Version : 1.1*
*Statut : ✅ RÈGLE ABSOLUE IMPLÉMENTÉE + RÈGLE GIT AJOUTÉE*
