# 🎼 Orchestrator Integration Guide

> **How advanced analytics integrates with the main Manalytics pipeline**

## 📋 Overview

The `src/orchestrator.py` file serves as the central conductor for the Manalytics pipeline, orchestrating data processing, analysis, and visualization. With v0.3.4, it now includes seamless integration with the advanced analytics module.

## 🔧 Key Integration Functions

### `_perform_advanced_analysis(self, data: pd.DataFrame) -> Dict[str, Any]`

**Purpose**: Execute comprehensive advanced statistical analysis on processed tournament data.

**Algorithm**:
1. Initialize `AdvancedMetagameAnalyzer` instance
2. Load tournament data into analyzer
3. Execute full analysis pipeline
4. Handle errors gracefully with logging
5. Save results to JSON file

**Integration Point**: Called automatically during `run_analysis()` after basic processing.

**Code Location**: `src/orchestrator.py` ~line 180

**Example Output**:
```python
{
    "metadata": {
        "generated_at": "2025-07-13T10:30:00",
        "total_decks": 5521,
        "unique_archetypes": 15,
        "date_range": {"start": "2025-05-08", "end": "2025-06-09"}
    },
    "diversity_metrics": {
        "shannon_diversity": 1.9812,
        "simpson_diversity": 0.8137,
        "effective_archetypes": 7.25
    },
    "temporal_trends": {
        "temporal_analysis": {...},
        "trend_summary": {"Rising": 3, "Declining": 2, "Volatile": 6, "Stable": 4}
    },
    "clustering_analysis": {...},
    "correlation_analysis": {...},
    "card_analysis": {...},
    "summary_insights": [...]
}
```

---

### `_extract_key_insights(self, analysis_results: Dict[str, Any]) -> List[str]`

**Purpose**: Extract human-readable insights from advanced analysis results.

**Algorithm**:
1. Analyze diversity metrics for metagame health
2. Identify trending archetypes from temporal analysis
3. Detect dominant clusters from clustering analysis
4. Highlight significant correlations
5. Format as actionable insights

**Insight Categories**:
- **Diversity Assessment**: Metagame health evaluation
- **Trend Analysis**: Rising/declining archetype identification
- **Cluster Insights**: Archetype grouping patterns
- **Correlation Findings**: Statistical relationships
- **Meta Stability**: Overall format stability

**Example Insights**:
```python
[
    "🎯 Metagame Health: Healthy diversity (Shannon=1.98, 7.25 effective archetypes)",
    "📈 Rising Archetypes: Domain Zoo (+12.3%), Jeskai Control (+8.7%)",
    "📉 Declining Archetypes: Rakdos Midrange (-15.2%), Mono-Red Aggro (-9.1%)",
    "🎪 Volatile Archetypes: 6 archetypes show high variance (>0.05)",
    "🔗 Strong Correlation: Winrate vs Meta Share (r=0.73, p<0.001)"
]
```

---

### `save_analysis_results(self, results: Dict[str, Any], output_dir: str)`

**Purpose**: Save advanced analysis results to structured output files.

**Files Created**:
- `advanced_analysis.json`: Complete analysis results
- `insights_summary.txt`: Human-readable insights
- `diversity_metrics.csv`: Diversity metrics table
- `temporal_trends.csv`: Trend analysis data
- `cluster_assignments.csv`: Archetype clustering results

**File Structure**:
```
analysis_output/
├── advanced_analysis.json      # Complete analysis data
├── insights_summary.txt        # Key insights list
├── diversity_metrics.csv       # Diversity metrics
├── temporal_trends.csv         # Trend analysis
├── cluster_assignments.csv     # Clustering results
└── correlation_matrix.csv      # Correlation data
```

---

## 🔄 Pipeline Integration Flow

```mermaid
graph TD
    A[🎯 run_full_pipeline.py] --> B[🎼 Orchestrator.run_analysis()]
    B --> C[🕷️ Data Collection]
    C --> D[🏷️ Classification]
    D --> E[📊 Basic Analysis]
    E --> F[🔬 Advanced Analysis]
    F --> G[📈 Visualization]
    G --> H[💾 Output Generation]

    F --> F1[Shannon Diversity]
    F --> F2[Temporal Trends]
    F --> F3[K-means Clustering]
    F --> F4[Correlation Analysis]
    F --> F5[Card Usage Analysis]

    F1 --> I[📋 Insights Extraction]
    F2 --> I
    F3 --> I
    F4 --> I
    F5 --> I

    I --> J[💾 JSON + CSV Output]
    J --> K[📄 HTML Integration]
```

## 🎯 Automatic Integration Points

### 1. **Data Processing Stage**
```python
# In orchestrator.py
def run_analysis(self, format_name, start_date, end_date):
    # ... existing data processing ...

    # NEW: Advanced analysis integration
    if len(processed_data) > 0:
        advanced_results = self._perform_advanced_analysis(processed_data)
        insights = self._extract_key_insights(advanced_results)
        self.save_analysis_results(advanced_results, self.output_dir)
```

### 2. **HTML Report Integration**
```python
# Advanced analysis results are automatically included in HTML reports
def generate_html_report(self):
    # ... existing HTML generation ...

    # NEW: Include advanced analytics section
    if os.path.exists(f"{self.output_dir}/advanced_analysis.json"):
        with open(f"{self.output_dir}/advanced_analysis.json") as f:
            advanced_data = json.load(f)

        # Add advanced analytics section to HTML
        self.add_advanced_analytics_section(advanced_data)
```

### 3. **Visualization Enhancement (v0.3.4.1)**
```python
# Professional-grade visualizations with industry standards
def create_enhanced_charts(self):
    # ... existing basic charts with 700px standardization ...

    # ENHANCED: Industry-standard visualizations
    self.create_diversity_timeline()           # 1000×700 standardized
    self.create_trend_analysis_chart()         # 800×700 standardized
    self.create_cluster_visualization()        # 800×700 standardized
    self.create_correlation_heatmap()          # 800×700 standardized

    # NEW: Accessibility-compliant visualizations
    self.create_matchup_matrix()               # ColorBrewer RdYlBu palette
    self.create_metagame_pie_chart()           # Zero "Autres", max 12 segments
    self.create_professional_bar_charts()     # WCAG AA compliance
```

#### **Key Integration Enhancements**:
- **Standardization**: All charts automatically use 700px height
- **Accessibility**: ColorBrewer palettes for 8% colorblind population
- **Professional Quality**: MTGGoldfish/17lands/Untapped.gg standards
- **Absolute Rules**: Hardcoded pie chart rules (no "Autres", max 12 segments)
- **Performance**: Optimized rendering for consistent dimensions

## 🚀 Usage in Practice

### Automatic Execution (Recommended)
```bash
# Advanced analytics run automatically
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# Results automatically saved to:
# - Analyses/standard_analysis_2025-07-01_2025-07-07/
# - analysis_output/advanced_analysis.json
# - analysis_output/insights_summary.txt
```

### Manual Integration
```python
from src.orchestrator import Orchestrator
from src.python.analytics.advanced_metagame_analyzer import AdvancedMetagameAnalyzer

# Initialize orchestrator
orchestrator = Orchestrator()

# Load your data
data = orchestrator.load_tournament_data("Standard", "2025-07-01", "2025-07-07")

# Run advanced analysis
advanced_results = orchestrator._perform_advanced_analysis(data)

# Extract insights
insights = orchestrator._extract_key_insights(advanced_results)

# Save results
orchestrator.save_analysis_results(advanced_results, "custom_output/")
```

## 🔧 Configuration Options

### Analysis Parameters
```python
# In orchestrator.py - customizable parameters
ADVANCED_ANALYSIS_CONFIG = {
    "clustering_clusters": 3,           # Number of K-means clusters
    "trend_r_squared_threshold": 0.3,   # Threshold for trend significance
    "correlation_strength_threshold": 0.7, # Strong correlation threshold
    "diversity_health_threshold": 2.0,  # Healthy diversity threshold
    "temporal_window": "W"              # Temporal aggregation window
}
```

### Output Options
```python
# Customize output formats
OUTPUT_CONFIG = {
    "save_json": True,          # Save complete JSON analysis
    "save_csv": True,           # Save CSV summaries
    "save_insights": True,      # Save human-readable insights
    "include_in_html": True,    # Include in HTML reports
    "create_charts": True       # Generate advanced charts
}
```

## 📊 Performance Characteristics

### Execution Time
- **Basic Analysis**: ~5-10 seconds
- **Advanced Analysis**: ~10-20 seconds additional
- **Total Pipeline**: ~30-40 seconds for typical dataset

### Memory Usage
- **Data Processing**: ~50-100 MB
- **Advanced Analysis**: ~20-50 MB additional
- **Peak Memory**: ~150-200 MB for large datasets

### Scalability
- **Small Dataset** (< 1,000 decks): < 10 seconds
- **Medium Dataset** (1,000-10,000 decks): 10-30 seconds
- **Large Dataset** (> 10,000 decks): 30-60 seconds

## 🔗 GitHub Integration

### R-Meta-Analysis Connection
The orchestrator integrates with methodologies from [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3):

```python
# Statistical methods aligned with R-Meta-Analysis
def calculate_diversity_metrics(self):
    # Uses Shannon diversity formula from ecology R packages
    # Matches diversity() function from vegan package

def analyze_temporal_trends(self):
    # Implements time series analysis similar to forecast package
    # Compatible with R's ts() and lm() functions
```

### Data Export Compatibility
```python
# Export formats compatible with R analysis
def export_for_r_analysis(self):
    # CSV format compatible with R data.frame
    # JSON structure matches R list objects
    # Statistical results follow R statistical output format
```

## 🎯 Best Practices

### 1. **Data Quality Checks**
```python
# Orchestrator includes automatic data validation
def validate_data_quality(self, data):
    if len(data) < 100:
        self.logger.warning("Small dataset - statistical results may be unreliable")

    if data['archetype'].nunique() < 5:
        self.logger.warning("Low archetype diversity - some analyses may be skipped")
```

### 2. **Error Handling**
```python
# Graceful degradation if advanced analysis fails
try:
    advanced_results = self._perform_advanced_analysis(data)
except Exception as e:
    self.logger.error(f"Advanced analysis failed: {e}")
    # Continue with basic analysis only
    advanced_results = {}
```

### 3. **Performance Optimization**
```python
# Caching for repeated analyses
@lru_cache(maxsize=10)
def cached_analysis(self, data_hash):
    # Cache expensive computations
    return self._perform_advanced_analysis(data)
```

## 🎪 Conclusion

The orchestrator integration provides seamless access to advanced analytics while maintaining the simplicity of the original pipeline. Users get enhanced insights automatically, while developers can customize and extend the analysis capabilities as needed.

For detailed function documentation, see [API_REFERENCE_ADVANCED_ANALYTICS.md](API_REFERENCE_ADVANCED_ANALYTICS.md).
