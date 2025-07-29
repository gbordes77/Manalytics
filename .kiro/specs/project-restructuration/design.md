# Design Document - Restructuration Projet Manalytics

## Overview

Cette restructuration vise à transformer le projet Manalytics d'un état chaotique avec 36+ scripts éparpillés vers une architecture claire, modulaire et maintenable. Le design privilégie la simplicité, la traçabilité et la facilitation de l'investigation du pipeline Jiliac.

## Architecture

### Structure Cible

```
manalytics/
├── src/manalytics/              # Package principal (structure moderne)
│   ├── cli/                     # Points d'entrée uniques
│   │   ├── analyze.py          # Script d'analyse de référence
│   │   ├── scrape.py           # Script de scraping de référence  
│   │   └── visualize.py        # Script de visualisation de référence
│   ├── core/                   # Logique métier centrale
│   │   ├── analyzers/          # Analyseurs de données
│   │   ├── scrapers/           # Scrapers MTGO/Melee
│   │   ├── parsers/            # Parseurs d'archétypes
│   │   └── visualizers/        # Générateurs de visualisations
│   ├── data/                   # Modèles de données
│   ├── utils/                  # Utilitaires partagés
│   └── config/                 # Configuration centralisée
├── investigation/              # Espace dédié investigation Jiliac
│   ├── jiliac_repos/          # Repos clonés (R-Meta-Analysis, etc.)
│   ├── experiments/           # Tests et hypothèses
│   ├── findings/              # Découvertes documentées
│   └── comparisons/           # Comparaisons avec Jiliac
├── data/                      # Données du projet
│   ├── raw/                   # Données brutes
│   ├── processed/             # Données traitées
│   └── cache/                 # Cache système
├── _archive/                  # Scripts archivés
│   ├── analyze_scripts/       # 21 scripts d'analyse archivés
│   ├── scrape_scripts/        # 15 scripts de scraping archivés
│   └── migration_log.md       # Log de la migration
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Architecture détaillée
│   ├── SCRIPTS_REFERENCE.md   # Guide des scripts de référence
│   └── ONBOARDING.md          # Guide d'onboarding
└── tests/                     # Tests automatisés
```

### Principes de Design

1. **Single Source of Truth** : Un seul script de référence par fonction
2. **Separation of Concerns** : Logique métier séparée des points d'entrée
3. **Traceability First** : Chaque transformation de données est traçable
4. **Investigation Friendly** : Structure facilitant la recherche sur Jiliac
5. **Backward Compatibility** : Préservation des fonctionnalités existantes

## Components and Interfaces

### 1. CLI Layer (Points d'Entrée)

#### analyze.py
```python
class AnalyzeCommand:
    """Point d'entrée unique pour toutes les analyses"""
    
    def execute(self, format: str, period: str, method: str = "jiliac"):
        """
        Execute analysis with specified parameters
        
        Args:
            format: MTG format (standard, modern, etc.)
            period: Analysis period (july_1_21, last_30_days, etc.)
            method: Analysis method (jiliac, custom)
        """
        
    def get_available_methods(self) -> List[str]:
        """Return list of available analysis methods"""
        
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters"""
```

#### scrape.py
```python
class ScrapeCommand:
    """Point d'entrée unique pour tous les scrapings"""
    
    def execute(self, platforms: List[str], format: str, days: int):
        """
        Execute scraping from specified platforms
        
        Args:
            platforms: List of platforms (mtgo, melee)
            format: MTG format
            days: Number of days to scrape
        """
        
    def get_available_platforms(self) -> List[str]:
        """Return list of available platforms"""
        
    def estimate_duration(self, **kwargs) -> int:
        """Estimate scraping duration in minutes"""
```

#### visualize.py
```python
class VisualizeCommand:
    """Point d'entrée unique pour toutes les visualisations"""
    
    def execute(self, analysis_id: str, output_format: str = "html"):
        """
        Generate visualizations from analysis results
        
        Args:
            analysis_id: ID of the analysis to visualize
            output_format: Output format (html, png, pdf)
        """
        
    def get_available_templates(self) -> List[str]:
        """Return list of available visualization templates"""
```

### 2. Core Layer (Logique Métier)

#### DataTracker
```python
class DataTracker:
    """Système de traçabilité des données"""
    
    def track_source(self, data_id: str, source: str, timestamp: datetime):
        """Track data source and collection time"""
        
    def track_transformation(self, input_id: str, output_id: str, 
                           transformation: str, parameters: dict):
        """Track data transformation with parameters"""
        
    def get_lineage(self, data_id: str) -> DataLineage:
        """Get complete data lineage for traceability"""
```

#### AnalysisEngine
```python
class AnalysisEngine:
    """Moteur d'analyse centralisé"""
    
    def analyze_with_jiliac_method(self, data: MatchupData) -> AnalysisResult:
        """Execute analysis using exact Jiliac methodology"""
        
    def compare_with_reference(self, result: AnalysisResult, 
                             reference: JiliacReference) -> ComparisonReport:
        """Compare results with Jiliac reference data"""
        
    def validate_results(self, result: AnalysisResult) -> ValidationReport:
        """Validate analysis results for consistency"""
```

### 3. Investigation Layer

#### JiliacInvestigator
```python
class JiliacInvestigator:
    """Système d'investigation du pipeline Jiliac"""
    
    def clone_repositories(self) -> List[str]:
        """Clone all Jiliac-related repositories"""
        
    def analyze_pipeline(self) -> PipelineAnalysis:
        """Analyze Jiliac pipeline structure"""
        
    def test_hypothesis(self, hypothesis: Hypothesis) -> TestResult:
        """Test hypothesis about matchup data source"""
        
    def document_finding(self, finding: Finding):
        """Document investigation finding"""
```

## Data Models

### Core Data Models

```python
@dataclass
class MatchupData:
    """Structure de données pour les matchups"""
    player: str
    archetype: str
    wins: int
    losses: int
    matchups: List[Matchup]
    source: DataSource
    timestamp: datetime
    
@dataclass  
class Matchup:
    """Structure d'un matchup individuel"""
    opponent_archetype: str
    wins: int
    losses: int
    rounds: List[Round]
    
@dataclass
class DataLineage:
    """Traçabilité complète d'une donnée"""
    data_id: str
    sources: List[DataSource]
    transformations: List[Transformation]
    final_state: dict
    
@dataclass
class AnalysisResult:
    """Résultat d'analyse standardisé"""
    analysis_id: str
    method: str
    parameters: dict
    metagame_breakdown: Dict[str, float]
    matchup_matrix: Dict[Tuple[str, str], float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    metadata: AnalysisMetadata
```

### Investigation Models

```python
@dataclass
class Hypothesis:
    """Hypothèse sur la source des données Jiliac"""
    id: str
    description: str
    test_method: str
    expected_outcome: str
    
@dataclass
class Finding:
    """Découverte d'investigation"""
    id: str
    hypothesis_id: Optional[str]
    description: str
    evidence: List[str]
    confidence_level: float
    implications: List[str]
```

## Error Handling

### Stratégie d'Erreur

1. **Graceful Degradation** : Si un composant échoue, les autres continuent
2. **Detailed Logging** : Chaque erreur est loggée avec contexte complet
3. **Recovery Mechanisms** : Tentatives de récupération automatique
4. **User-Friendly Messages** : Messages d'erreur compréhensibles

### Exception Hierarchy

```python
class ManalyticsError(Exception):
    """Base exception for all Manalytics errors"""
    
class DataSourceError(ManalyticsError):
    """Errors related to data sources (MTGO, Melee)"""
    
class AnalysisError(ManalyticsError):
    """Errors during data analysis"""
    
class InvestigationError(ManalyticsError):
    """Errors during Jiliac pipeline investigation"""
```

## Testing Strategy

### Test Pyramid

1. **Unit Tests** : Test de chaque composant isolément
2. **Integration Tests** : Test des interactions entre composants  
3. **End-to-End Tests** : Test des workflows complets
4. **Regression Tests** : Garantir que les résultats restent cohérents

### Test Data Strategy

```python
class TestDataManager:
    """Gestionnaire de données de test"""
    
    def create_synthetic_matchups(self, archetype_distribution: dict) -> MatchupData:
        """Create synthetic but realistic matchup data"""
        
    def load_jiliac_reference_data(self) -> JiliacReference:
        """Load known Jiliac results for comparison"""
        
    def create_test_scenarios(self) -> List[TestScenario]:
        """Create various test scenarios"""
```

### Validation Framework

```python
class ResultValidator:
    """Validation des résultats d'analyse"""
    
    def validate_metagame_percentages(self, breakdown: dict) -> ValidationResult:
        """Validate that metagame percentages sum to 100%"""
        
    def validate_matchup_consistency(self, matrix: dict) -> ValidationResult:
        """Validate matchup matrix consistency (A vs B = inverse of B vs A)"""
        
    def compare_with_jiliac(self, result: AnalysisResult) -> ComparisonResult:
        """Compare results with known Jiliac benchmarks"""
```

## Migration Strategy

### Phase 1: Structure Setup
1. Créer la nouvelle structure de dossiers
2. Identifier les scripts de référence actuels
3. Créer les interfaces des nouveaux composants

### Phase 2: Core Migration  
1. Migrer la logique des scripts de référence vers les nouveaux composants
2. Créer les nouveaux points d'entrée CLI
3. Implémenter le système de traçabilité

### Phase 3: Investigation Setup
1. Cloner tous les repos Jiliac dans investigation/
2. Créer les outils d'investigation
3. Documenter les hypothèses actuelles

### Phase 4: Archive & Cleanup
1. Archiver tous les anciens scripts
2. Créer la documentation de migration
3. Valider que toutes les fonctionnalités sont préservées

### Phase 5: Testing & Validation
1. Créer la suite de tests complète
2. Valider les résultats contre les références connues
3. Documenter les différences avec Jiliac

## Performance Considerations

### Caching Strategy
- Cache intelligent des données scrapées
- Cache des résultats d'analyse pour éviter les recalculs
- Cache des transformations de données coûteuses

### Memory Management
- Streaming des gros datasets
- Garbage collection explicite après traitement
- Monitoring de l'utilisation mémoire

### Parallel Processing
- Scraping parallèle des différentes sources
- Analyse parallèle des différents archétypes
- Génération parallèle des visualisations