# 🔬 Advanced Analytics Documentation

> **Comprehensive statistical analysis** integrated with R-Meta-Analysis methodology

## 📋 Overview

The Manalytics pipeline now includes **18 advanced analytical features** that provide academic-level statistical insights into MTG metagame data. These features are integrated with the [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3) R-Meta-Analysis repository to ensure consistency with established statistical methodologies.

## 🎯 Key Features Summary

### 🔬 **Statistical Diversity Metrics**
- **Shannon Diversity Index**: Measures metagame diversity using information theory
- **Simpson Index**: Alternative diversity metric focusing on dominance
- **Effective Archetype Count**: Practical measure of functional diversity

### 📈 **Temporal Analysis**
- **Rising Archetypes**: Identify growing metagame trends
- **Declining Archetypes**: Detect archetypes losing popularity
- **Volatile Archetypes**: Track inconsistent performance patterns
- **Stable Archetypes**: Identify consistent metagame pillars

### 🧮 **Machine Learning Integration**
- **K-means Clustering**: Group archetypes by performance characteristics
- **Silhouette Analysis**: Validate clustering quality
- **Correlation Matrix**: Statistical relationship analysis
- **Significance Testing**: P-value calculation for correlations

### 📊 **Card Usage Analytics**
- **Comprehensive Card Statistics**: Frequency analysis across all decks
- **Meta-level Insights**: Card popularity trends and patterns
- **Archetype-specific Usage**: Card distribution by deck type

### 🎨 **Visualization Consistency (v0.3.5)**
- **Hierarchical Ordering**: Izzet Prowess always appears first across all visualizations
- **Unified Naming**: Perfect alignment between bar charts and matchup matrix
- **Professional Standards**: Industry-grade consistency matching MTGGoldfish standards
- **Centralized Methods**: `sort_archetypes_by_hierarchy()` and `_get_archetype_column()`

---

## 🔧 Technical Implementation

### **Core Module**: `src/python/analytics/advanced_metagame_analyzer.py`

```python
class AdvancedMetagameAnalyzer:
    """
    Advanced statistical analysis for MTG metagame data
    
    Integrates with Jiliac/Aliquanto3 R-Meta-Analysis methodology
    to provide academic-level insights.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data = None
        
    def load_data(self, df: pd.DataFrame) -> bool:
        """Load tournament data for analysis"""
        
    def calculate_diversity_metrics(self) -> Dict[str, float]:
        """Calculate Shannon and Simpson diversity indices"""
        
    def analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze archetype trends over time"""
        
    def perform_archetype_clustering(self) -> Dict[str, Any]:
        """K-means clustering of archetypes"""
        
    def calculate_correlations(self) -> Dict[str, Any]:
        """Statistical correlation analysis"""
        
    def analyze_card_usage(self) -> Dict[str, Any]:
        """Comprehensive card usage statistics"""
        
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate complete statistical report"""
```

### **Integration Point**: `src/orchestrator.py`

```python
def _perform_advanced_analysis(self, processed_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute advanced statistical analysis
    
    Generates comprehensive report with all 18 analytical features
    """
    analyzer = AdvancedMetagameAnalyzer()
    
    if not analyzer.load_data(processed_data):
        return {}
    
    return analyzer.generate_comprehensive_analysis()
```

---

## 📊 Feature Breakdown

### 1. **Shannon Diversity Index**
- **Formula**: `H' = -Σ(pi * ln(pi))`
- **Purpose**: Measures metagame diversity using information theory
- **Output**: Numerical value (higher = more diverse)
- **Interpretation**: 
  - `< 1.0`: Low diversity (1-2 dominant archetypes)
  - `1.0-2.0`: Moderate diversity (3-7 competitive archetypes)
  - `> 2.0`: High diversity (8+ viable archetypes)

### 2. **Simpson Index**
- **Formula**: `D = 1 - Σ(pi²)`
- **Purpose**: Alternative diversity metric focusing on dominance
- **Output**: Value between 0 and 1 (higher = more diverse)
- **Interpretation**: Probability that two randomly selected decks are different archetypes

### 3. **Effective Archetype Count**
- **Formula**: `e^H'` (exponential of Shannon index)
- **Purpose**: Intuitive measure of functional diversity
- **Output**: Number representing "effective" archetypes
- **Interpretation**: Number of equally-abundant archetypes needed to produce observed diversity

### 4. **Temporal Trend Analysis**
- **Method**: Linear regression analysis over time periods
- **Categories**:
  - **Rising**: Positive trend with R² > 0.5
  - **Declining**: Negative trend with R² > 0.5
  - **Volatile**: High variance, low predictability
  - **Stable**: Consistent performance over time
- **Output**: Archetype categorization with trend metrics

### 5. **K-means Clustering**
- **Algorithm**: Scikit-learn KMeans with n_clusters=3
- **Features**: Win rate, metagame share, temporal stability
- **Validation**: Silhouette score calculation
- **Output**: Archetype groupings with cluster characteristics

### 6. **Correlation Analysis**
- **Method**: Pearson correlation coefficient
- **Significance**: P-value calculation (α = 0.05)
- **Features**: Win rate, metagame share, temporal trends
- **Output**: Correlation matrix with significance indicators

### 7. **Card Usage Statistics**
- **Scope**: All cards across all decks in dataset
- **Metrics**: Frequency, percentage, archetype distribution
- **Analysis**: Most/least played cards, meta patterns
- **Output**: Comprehensive card usage report

---

## 🔗 GitHub Integration

### **Primary Repository Connections**

#### 1. **[Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3)** - R-Meta-Analysis
- **Purpose**: Statistical methodology reference
- **Integration**: Python implementation of R-based analysis
- **Features**: Diversity indices, correlation analysis, trend detection
- **Academic Standards**: Peer-reviewed statistical approaches

#### 2. **[Jiliac/MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache)** - Data Source
- **Purpose**: Raw tournament data provider
- **Integration**: Direct data pipeline integration
- **Coverage**: MTGO, Melee.gg, TopDeck.gg tournaments
- **Real Data Policy**: Strict enforcement of authentic tournament data

#### 3. **[Badaro/MTGOFormatData](https://github.com/Badaro/MTGOFormatData)** - Classification Rules
- **Purpose**: Archetype classification and card database
- **Integration**: Official archetype detection rules
- **Coverage**: 105+ Modern, 77+ Pioneer, 50+ Legacy archetypes
- **Accuracy**: ~95% classification precision

---

## 📈 Output Format

### **JSON Export Structure**
```json
{
  "metadata": {
    "generated_at": "2025-07-13T10:30:00Z",
    "total_decks": 5521,
    "unique_archetypes": 15,
    "date_range": {
      "start": "2025-05-08",
      "end": "2025-06-09"
    }
  },
  "diversity_metrics": {
    "shannon_index": 1.9812,
    "simpson_index": 0.8137,
    "effective_archetype_count": 7.25
  },
  "temporal_trends": {
    "rising": ["Boros Energy", "Izzet Midrange"],
    "declining": ["Mono-Red Aggro"],
    "volatile": ["Esper Control"],
    "stable": ["Dimir Midrange", "Gruul Aggro"]
  },
  "clustering_analysis": {
    "silhouette_score": 0.67,
    "clusters": {
      "high_performers": ["Boros Energy", "Izzet Midrange"],
      "meta_staples": ["Dimir Midrange", "Gruul Aggro"],
      "niche_picks": ["Esper Control", "Mono-Red Aggro"]
    }
  },
  "correlation_analysis": {
    "significant_correlations": [
      {
        "archetype1": "Boros Energy",
        "archetype2": "Izzet Midrange",
        "correlation": 0.73,
        "p_value": 0.001,
        "significant": true
      }
    ]
  },
  "card_analysis": {
    "most_played_cards": [
      {"name": "Lightning Bolt", "frequency": 0.85},
      {"name": "Thoughtseize", "frequency": 0.72}
    ],
    "meta_insights": {
      "aggro_cards": 1247,
      "control_cards": 892,
      "midrange_cards": 1653
    }
  },
  "key_insights": [
    "Metagame shows moderate diversity with 7.25 effective archetypes",
    "Boros Energy and Izzet Midrange are rising in popularity",
    "Strong correlation between aggressive strategies"
  ]
}
```

---

## 🎯 Usage Examples

### **Basic Integration**
```python
# In your analysis pipeline
from src.python.analytics.advanced_metagame_analyzer import AdvancedMetagameAnalyzer

analyzer = AdvancedMetagameAnalyzer()
analyzer.load_data(processed_tournament_data)
results = analyzer.generate_comprehensive_analysis()

# Access specific metrics
diversity = results['diversity_metrics']['shannon_index']
trends = results['temporal_trends']['rising']
clusters = results['clustering_analysis']['clusters']
```

### **Diversity Analysis**
```python
# Calculate metagame diversity
diversity_metrics = analyzer.calculate_diversity_metrics()

print(f"Shannon Index: {diversity_metrics['shannon_index']:.3f}")
print(f"Simpson Index: {diversity_metrics['simpson_index']:.3f}")
print(f"Effective Archetypes: {diversity_metrics['effective_archetype_count']:.2f}")
```

### **Temporal Trends**
```python
# Analyze archetype trends over time
trends = analyzer.analyze_temporal_trends()

rising_archetypes = trends['categorization']['rising']
declining_archetypes = trends['categorization']['declining']

print(f"Rising archetypes: {rising_archetypes}")
print(f"Declining archetypes: {declining_archetypes}")
```

---

## 🔧 Configuration

### **Analysis Parameters**
```python
# Clustering configuration
N_CLUSTERS = 3  # Number of archetype clusters
RANDOM_STATE = 42  # Reproducible results

# Correlation significance threshold
ALPHA = 0.05  # P-value threshold for significance

# Temporal analysis windows
MIN_TOURNAMENTS = 5  # Minimum tournaments for trend analysis
TREND_THRESHOLD = 0.5  # R² threshold for trend classification
```

### **Data Requirements**
- **Minimum Dataset**: 100+ decks for meaningful analysis
- **Recommended**: 500+ decks for robust statistics
- **Optimal**: 1000+ decks for comprehensive insights
- **Time Period**: At least 2 weeks for temporal analysis

---

## 🎨 Visualization Consistency System (v0.3.5)

### **Critical Enhancement: Perfect Visual Alignment**

Version 0.3.5 introduces a revolutionary centralized system ensuring perfect consistency across all visualizations.

#### **Problem Solved**
- **Before**: Bar charts showed "Prowess" while matchup matrix showed "Izzet Prowess"
- **Before**: Different ordering between chart types created confusion
- **Before**: Inconsistent archetype positioning across visualizations

#### **Solution Architecture**

##### **Centralized Ordering System**
```python
def sort_archetypes_by_hierarchy(self, archetypes: List[str]) -> List[str]:
    """
    Ensures consistent hierarchical ordering across ALL visualizations
    
    Priority:
    1. Izzet Prowess (always first if present)
    2. Descending by frequency/percentage
    3. Alphabetical for ties
    """
```

##### **Unified Naming System**
```python
def _get_archetype_column(self, df: pd.DataFrame) -> str:
    """
    Centralized column selection for consistent archetype naming
    
    Logic:
    - Prefers 'archetype_with_colors' (e.g., "Izzet Prowess")
    - Falls back to 'archetype' if not available
    - Ensures identical naming across all chart types
    """
```

#### **Implementation Impact**

##### **Affected Visualizations**
- **MetagameChartsGenerator**: All pie charts and bar charts
- **MatchupMatrixGenerator**: Complete matchup matrix system
- **Integration**: Seamless orchestrator integration

##### **Technical Benefits**
- **Zero Configuration**: Consistency applied automatically
- **Maintainable**: Centralized logic prevents future inconsistencies
- **Professional**: Industry-standard presentation quality
- **Extensible**: New visualizations inherit consistent behavior

#### **User Experience Improvements**

##### **Navigation**
- **Logical Flow**: Same archetype order across all charts
- **Professional**: Izzet Prowess consistently leads when present
- **Intuitive**: Cross-chart comparison becomes effortless

##### **Analysis Benefits**
- **Reduced Confusion**: No more wondering about different orders
- **Faster Insights**: Consistent positioning speeds up analysis
- **Professional Reports**: Industry-standard consistency

#### **Performance Impact**
- **Speed**: No performance degradation
- **Memory**: Minimal overhead from centralized methods
- **Compatibility**: Fully backward compatible

---

## 🚀 Future Enhancements

### **Planned Features**
- **Bayesian Analysis**: Advanced statistical inference
- **Network Analysis**: Archetype relationship mapping
- **Predictive Modeling**: Future metagame forecasting
- **Interactive Visualizations**: Real-time statistical dashboards

### **Research Integration**
- **Academic Papers**: Integration with MTG research publications
- **Conference Presentations**: Data for competitive analysis
- **Pro Tour Analysis**: Professional tournament insights
- **Community Research**: Open-source statistical contributions

---

## 📚 References

### **Statistical Methods**
- Shannon, C.E. (1948). "A Mathematical Theory of Communication"
- Simpson, E.H. (1949). "Measurement of Diversity"
- MacArthur, R.H. (1965). "Patterns of Species Diversity"

### **Implementation References**
- [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3) - R-Meta-Analysis methodology
- [Scikit-learn Documentation](https://scikit-learn.org/) - Machine learning algorithms
- [SciPy Documentation](https://scipy.org/) - Statistical functions

### **MTG Analysis Literature**
- Competitive metagame analysis methodologies
- Statistical approaches to card game analysis
- Diversity metrics in competitive gaming

---

*Last updated: July 13, 2025*
*Version: v0.3.4*
*Integration: R-Meta-Analysis compatible* 