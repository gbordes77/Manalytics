# 🔬 Advanced Analytics API Reference

> **Complete function documentation** for the `AdvancedMetagameAnalyzer` class

## 📋 Table of Contents

1. [Class Overview](#class-overview)
2. [Core Functions](#core-functions)
3. [Statistical Analysis Functions](#statistical-analysis-functions)
4. [Clustering & Correlation Functions](#clustering--correlation-functions)
5. [Utility Functions](#utility-functions)
6. [Usage Examples](#usage-examples)

---

## 🎯 Class Overview

### `AdvancedMetagameAnalyzer`

**Purpose**: Enhanced statistical analysis for MTG metagame data, providing academic-grade analytics including diversity indices, temporal trends, clustering, and correlation analysis.

**Attributes**:
- `data`: DataFrame containing tournament data
- `archetype_performance`: Cached archetype performance metrics
- `temporal_trends`: Cached temporal trend analysis
- `statistical_analysis`: Cached statistical analysis results
- `card_analysis`: Cached card usage analysis

---

## 🔧 Core Functions

### `__init__(self)`

**Purpose**: Initialize the analyzer with empty data structures and configure logging.

**Parameters**: None

**Returns**: None

**Example**:
```python
analyzer = AdvancedMetagameAnalyzer()
```

---

### `load_data(self, df: pd.DataFrame) -> bool`

**Purpose**: Load and preprocess tournament data for analysis.

**Parameters**:
- `df` (pd.DataFrame): Tournament data with columns: `tournament_date`, `archetype`, `wins`, `losses`, `winrate`

**Algorithm**:
1. Creates a copy of the input DataFrame
2. Converts `tournament_date` to datetime format
3. Creates weekly periods for temporal analysis
4. Calculates `matches_played` as `wins + losses`

**Returns**:
- `bool`: True if successful, False on error

**Output Structure**:
```python
# Data processing adds:
# - tournament_date: datetime
# - period: weekly periods
# - matches_played: int
```

**Example**:
```python
success = analyzer.load_data(tournament_df)
if success:
    print("Data loaded successfully")
```

---

## 📊 Statistical Analysis Functions

### `calculate_diversity_metrics(self) -> Dict[str, float]`

**Purpose**: Calculate comprehensive diversity metrics for the metagame using established ecological diversity indices.

**Algorithm**:
1. **Shannon Diversity Index**: H' = -Σ(pi × ln(pi))
2. **Simpson Diversity Index**: D = 1 - Σ(pi²)
3. **Effective Number of Archetypes**: e^H'
4. **Herfindahl-Hirschman Index**: HHI = Σ(pi²)
5. **Evenness**: H' / ln(S) where S = number of archetypes

**Returns**:
```python
{
    "shannon_diversity": float,      # Information theory diversity
    "simpson_diversity": float,      # Probability-based diversity
    "effective_archetypes": float,   # Practical archetype count
    "herfindahl_index": float,      # Market concentration
    "total_archetypes": int,        # Raw archetype count
    "evenness": float               # Distribution evenness
}
```

**Interpretation**:
- **Shannon**: Higher values = more diverse metagame (typically 0-4)
- **Simpson**: Higher values = more diverse metagame (0-1)
- **Effective Archetypes**: Intuitive "number of equally common archetypes"
- **HHI**: Lower values = less concentrated metagame (0-1)
- **Evenness**: 1 = perfectly even distribution, 0 = completely uneven

**Example**:
```python
diversity = analyzer.calculate_diversity_metrics()
print(f"Shannon Diversity: {diversity['shannon_diversity']}")
print(f"Effective Archetypes: {diversity['effective_archetypes']}")
```

---

### `analyze_temporal_trends(self) -> Dict[str, Any]`

**Purpose**: Analyze how archetype popularity changes over time and categorize trends.

**Algorithm**:
1. Groups data by weekly periods and archetype
2. Calculates period-over-period changes
3. Fits linear regression to identify trends
4. Categorizes each archetype as: Rising, Declining, Volatile, or Stable

**Classification Criteria**:
- **Rising**: Positive slope, R² > 0.3
- **Declining**: Negative slope, R² > 0.3
- **Volatile**: R² < 0.3, high variance
- **Stable**: R² < 0.3, low variance

**Returns**:
```python
{
    "temporal_analysis": {
        "archetype_name": {
            "trend_category": str,        # Rising/Declining/Volatile/Stable
            "slope": float,               # Linear regression slope
            "r_squared": float,           # Goodness of fit
            "mean_share": float,          # Average meta share
            "variance": float,            # Variance in meta share
            "peak_period": str,           # Period of maximum share
            "min_period": str            # Period of minimum share
        }
    },
    "trend_summary": {
        "Rising": int,                   # Count of rising archetypes
        "Declining": int,                # Count of declining archetypes
        "Volatile": int,                 # Count of volatile archetypes
        "Stable": int                    # Count of stable archetypes
    }
}
```

**Example**:
```python
trends = analyzer.analyze_temporal_trends()
rising_archetypes = [
    name for name, data in trends["temporal_analysis"].items()
    if data["trend_category"] == "Rising"
]
```

---

## 🎯 Clustering & Correlation Functions

### `perform_archetype_clustering(self, n_clusters: int = 3) -> Dict[str, Any]`

**Purpose**: Group archetypes based on performance characteristics using K-means clustering.

**Parameters**:
- `n_clusters` (int): Number of clusters to create (default: 3)

**Algorithm**:
1. Calculates archetype performance metrics:
   - Meta share (popularity)
   - Overall winrate (performance)
   - Dominance score (popularity × performance)
2. Standardizes features using StandardScaler
3. Applies K-means clustering with random_state=42
4. Analyzes cluster profiles

**Returns**:
```python
{
    "archetype_clusters": {
        "archetype_name": int           # Cluster assignment (0, 1, 2...)
    },
    "cluster_profiles": pd.DataFrame,   # Statistical profile of each cluster
    "cluster_centers": np.array,        # Cluster centroids in feature space
    "inertia": float,                  # Within-cluster sum of squares
    "archetype_stats": pd.DataFrame     # Complete archetype statistics
}
```

**Cluster Interpretation**:
- **Cluster 0**: Typically "Meta Leaders" (high share, high winrate)
- **Cluster 1**: Typically "Niche Performers" (low share, high winrate)
- **Cluster 2**: Typically "Popular Underperformers" (high share, low winrate)

**Example**:
```python
clustering = analyzer.perform_archetype_clustering(n_clusters=4)
for archetype, cluster in clustering["archetype_clusters"].items():
    print(f"{archetype}: Cluster {cluster}")
```

---

### `calculate_correlations(self) -> Dict[str, Any]`

**Purpose**: Calculate correlation matrix and perform statistical significance tests.

**Algorithm**:
1. Selects numeric columns: wins, losses, winrate, matches_played
2. Calculates Pearson correlation coefficients
3. Performs normality tests using `scipy.stats.normaltest`
4. Identifies strongest correlations

**Returns**:
```python
{
    "correlation_matrix": pd.DataFrame,  # Correlation coefficients
    "significance_tests": {
        "column_normality": {
            "statistic": float,          # Test statistic
            "p_value": float,           # P-value
            "is_normal": bool           # True if p > 0.05
        }
    },
    "strongest_correlations": [
        {
            "variable_1": str,
            "variable_2": str,
            "correlation": float,
            "strength": str             # Strong/Moderate/Weak
        }
    ]
}
```

**Correlation Strength Scale**:
- **Strong**: |r| > 0.7
- **Moderate**: 0.3 < |r| ≤ 0.7
- **Weak**: |r| ≤ 0.3

**Example**:
```python
correlations = analyzer.calculate_correlations()
strong_corrs = [
    corr for corr in correlations["strongest_correlations"]
    if corr["strength"] == "Strong"
]
```

---

## 🃏 Card Analysis Functions

### `analyze_card_usage(self) -> Dict[str, Any]`

**Purpose**: Analyze card usage patterns and meta statistics (when card data is available).

**Algorithm**:
1. Attempts to extract card information from deck data
2. Calculates usage frequencies and meta penetration
3. Identifies format staples and trending cards

**Returns**:
```python
{
    "card_analysis": {
        "total_unique_cards": int,
        "average_cards_per_deck": float,
        "most_played_cards": [
            {
                "card_name": str,
                "usage_count": int,
                "meta_penetration": float
            }
        ]
    },
    "format_staples": [str],            # Cards in >50% of decks
    "archetype_signatures": {
        "archetype_name": [str]         # Characteristic cards
    }
}
```

**Note**: This function requires card-level data in the input DataFrame. If not available, returns basic statistics.

**Example**:
```python
card_analysis = analyzer.analyze_card_usage()
staples = card_analysis["format_staples"]
print(f"Format staples: {staples}")
```

---

## 📋 Comprehensive Analysis

### `generate_comprehensive_analysis(self) -> Dict[str, Any]`

**Purpose**: Generate complete analysis report combining all analytical modules.

**Algorithm**:
1. Runs all individual analysis functions
2. Combines results into comprehensive report
3. Adds metadata and generation timestamp

**Returns**:
```python
{
    "metadata": {
        "generated_at": str,            # ISO timestamp
        "total_decks": int,
        "unique_archetypes": int,
        "date_range": {
            "start": str,               # YYYY-MM-DD
            "end": str                  # YYYY-MM-DD
        }
    },
    "diversity_metrics": dict,          # From calculate_diversity_metrics()
    "temporal_trends": dict,            # From analyze_temporal_trends()
    "clustering_analysis": dict,        # From perform_archetype_clustering()
    "correlation_analysis": dict,       # From calculate_correlations()
    "card_analysis": dict,             # From analyze_card_usage()
    "summary_insights": [str]          # Key insights list
}
```

**Example**:
```python
full_analysis = analyzer.generate_comprehensive_analysis()
print(f"Analysis generated at: {full_analysis['metadata']['generated_at']}")
print(f"Key insights: {full_analysis['summary_insights']}")
```

---

## 🎯 Usage Examples

### Complete Analysis Workflow

```python
# Initialize analyzer
analyzer = AdvancedMetagameAnalyzer()

# Load data
success = analyzer.load_data(tournament_dataframe)
if not success:
    print("Failed to load data")
    return

# Individual analyses
diversity = analyzer.calculate_diversity_metrics()
trends = analyzer.analyze_temporal_trends()
clustering = analyzer.perform_archetype_clustering(n_clusters=4)
correlations = analyzer.calculate_correlations()
cards = analyzer.analyze_card_usage()

# Complete analysis
full_report = analyzer.generate_comprehensive_analysis()

# Access results
print(f"Shannon Diversity: {diversity['shannon_diversity']}")
print(f"Rising archetypes: {trends['trend_summary']['Rising']}")
print(f"Cluster assignments: {clustering['archetype_clusters']}")
```

### Interpreting Results

```python
# Check metagame health
if diversity['shannon_diversity'] > 2.0:
    print("Healthy, diverse metagame")
elif diversity['shannon_diversity'] < 1.0:
    print("Concentrated metagame, potential balance issues")

# Identify trending archetypes
rising = [name for name, data in trends["temporal_analysis"].items()
          if data["trend_category"] == "Rising"]
print(f"Watch these rising archetypes: {rising}")

# Find correlation patterns
strong_correlations = [
    corr for corr in correlations["strongest_correlations"]
    if abs(corr["correlation"]) > 0.7
]
```

---

## 🔗 References

- **Shannon Diversity**: Shannon, C. E. (1948). "A Mathematical Theory of Communication"
- **Simpson Diversity**: Simpson, E. H. (1949). "Measurement of Diversity"
- **K-means Clustering**: MacQueen, J. (1967). "Some Methods for Classification and Analysis"
- **Herfindahl Index**: Herfindahl, O. C. (1950). "Concentration in the Steel Industry"

---

## 🚀 Integration with Manalytics Pipeline

This module integrates seamlessly with the main Manalytics pipeline through `src/orchestrator.py`:

```python
# In orchestrator.py
from src.python.analytics.advanced_metagame_analyzer import AdvancedMetagameAnalyzer

def _perform_advanced_analysis(self, data):
    analyzer = AdvancedMetagameAnalyzer()
    if analyzer.load_data(data):
        return analyzer.generate_comprehensive_analysis()
    return {}
```

The results are automatically saved to `analysis_output/advanced_analysis.json` and integrated into the HTML reports.

---

## 🎨 Visualization Integration (v0.3.4.1)

The advanced analytics results are visualized using the enhanced visualization modules:

### **Professional-Grade Visualizations**
- **Module**: `src/python/visualizations/metagame_charts.py`
- **Standards**: Industry-level quality (MTGGoldfish/17lands/Untapped.gg)
- **Accessibility**: Full colorblind support with WCAG AA compliance
- **Consistency**: All visualizations standardized to 700px height

### **Enhanced Modules**
- **`MetagameChartsGenerator`**: 7 methods updated with 700px standardization
- **`MatchupMatrixGenerator`**: ColorBrewer RdYlBu palette with adaptive text
- **Absolute Rules**: Zero "Autres/Non classifiés" in pie charts, maximum 12 segments

### **Technical Excellence**
- **Color Science**: ColorBrewer palettes for accessibility
- **Adaptive Text**: White text on dark, black text on light backgrounds
- **Performance**: Optimized rendering for standardized dimensions
- **Maintenance**: Hardcoded non-negotiable rules for consistency

For detailed visualization documentation, see `docs/DATA_VISUALIZATION_EXPERTISE.md`
