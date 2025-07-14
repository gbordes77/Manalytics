# 📝 Changelog - Manalytics

> **Version History** - All improvements documented

## 🆕 **v0.3.4.1** - Data Visualization Excellence & Standardization (January 15, 2025)

### ✨ **MAJOR VISUALIZATION IMPROVEMENTS**

#### 🎨 **Matchup Matrix Color Correction**
- **ColorBrewer RdYlBu Palette** - Replaced poor green monochrome with scientifically-validated palette
- **Adaptive Text System** - White text on dark backgrounds, black text on light backgrounds
- **Accessibility Compliance** - Full colorblind support for 8% of population (WCAG AA standards)
- **Enhanced Readability** - Professional contrast ratios for all data cells
- **File**: `src/python/visualizations/matchup_matrix.py` - Complete color system overhaul

#### 📊 **Graph Size Standardization**
- **Unified Dimensions** - All pie charts standardized to 1000×700 pixels
- **Consistent UX** - Identical sizing across `metagame_pie.html`, `metagame_share.html`, `data_sources_pie.html`
- **Professional Layout** - Optimal viewing experience on all devices
- **Visual Coherence** - Seamless navigation between visualization pages

#### 🎯 **12 Archetype Maximum Rule**
- **Optimal Readability** - Scientific limit of 12 archetypes per visualization
- **Industry Standard** - Matches MTGGoldfish, 17lands, Untapped.gg conventions
- **Top Performer Focus** - Automatic filtering to show most relevant archetypes
- **Enhanced Titles** - Clear "Top 12" indicators in all affected charts
- **Methods Updated**: `create_metagame_pie_chart`, `create_main_archetypes_bar_chart`, `create_main_archetypes_bar_horizontal`

#### 🚫 **Absolute Pie Chart Rules (NON-NEGOTIABLE)**
- **Zero "Autres/Non classifiés"** - Complete prohibition in all pie charts
- **Maximum 12 Segments** - Strict limit for visual clarity
- **Hardcoded Enforcement** - Non-negotiable rules embedded in codebase
- **Professional Standards** - Matches industry best practices for pie chart design
- **Documentation Updated** - `DATA_VISUALIZATION_EXPERTISE.md` with NON-NEGOTIABLE section

#### 📏 **Final Height Standardization**
- **700px Standard** - All visualizations standardized to 700px height (except matchup matrix)
- **7 Methods Updated** - `create_winrate_confidence_chart`, `create_tiers_scatter_plot`, `create_bubble_chart_winrate_presence`, `create_top_5_0_chart`, `create_archetype_evolution_chart`, `create_main_archetypes_bar_chart`, `create_main_archetypes_bar_horizontal`
- **Consistent Experience** - Uniform height across main and MTGO analysis pages
- **Preserved Exceptions** - Matchup matrix maintains optimal dimensions for readability

### 🛠️ **Technical Implementation**

#### **Enhanced Module**: `src/python/visualizations/metagame_charts.py`
- **Standardized Dimensions** - All methods now use consistent 700px height
- **Optimized Performance** - Efficient rendering for standardized sizes
- **Maintained Quality** - High-resolution output preserved across all formats
- **Backward Compatibility** - Existing analysis functionality unchanged

#### **Enhanced Module**: `src/python/visualizations/matchup_matrix.py`
- **ColorBrewer Integration** - Professional-grade color palette implementation
- **Accessibility Features** - Colorblind-safe visualization with adaptive text
- **Performance Optimization** - Efficient color calculation and text rendering
- **Standards Compliance** - WCAG AA accessibility requirements met

### 📈 **Visual Quality Improvements**
- **Industry Standards** - Matches professional MTG analytics platforms
- **Accessibility First** - Full support for colorblind users (8% of population)
- **Consistent Branding** - Unified visual identity across all visualizations
- **Professional Presentation** - Publication-ready chart quality

### 🎯 **User Experience Enhancements**
- **Reduced Cognitive Load** - Maximum 12 archetypes prevents visual overload
- **Improved Navigation** - Consistent dimensions for smoother browsing
- **Enhanced Readability** - Scientific color palettes for better comprehension
- **Professional Aesthetics** - Industry-standard visualization quality

---

## 🆕 **v0.3.4** - Advanced Statistical Analysis Integration (July 13, 2025)

### ✨ **MAJOR NEW FEATURES**

#### 🔬 **Advanced Statistical Analysis Engine**
- **Shannon Diversity Index** - Metagame diversity measurement using information theory
- **Simpson Index** - Alternative diversity metric focusing on dominance
- **Effective Archetype Count** - Practical measure of functional diversity (`e^H'`)
- **Temporal Trend Analysis** - Rising/Declining/Volatile/Stable archetype categorization
- **K-means Clustering** - Archetype grouping based on performance characteristics
- **Correlation Analysis** - Statistical relationship analysis with significance testing
- **Card Usage Statistics** - Comprehensive card frequency and meta analysis
- **Key Insights Extraction** - Automated interpretation of statistical patterns

#### 📊 **R-Meta-Analysis Integration**
- **GitHub Integration** - Connected to [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3) R-Meta-Analysis repository
- **Statistical Replication** - Python implementation of R-based metagame analysis
- **Academic Standards** - Implements peer-reviewed statistical methodologies
- **Comprehensive Output** - JSON exports with all 18 analytical features

#### 🧮 **Machine Learning Integration**
- **Scikit-learn Integration** - Professional-grade clustering algorithms
- **Silhouette Analysis** - Cluster validation and quality assessment
- **Statistical Significance** - P-value calculation for correlations (α = 0.05)
- **Reproducible Results** - Fixed random state for consistent clustering

#### 📈 **Advanced Metrics Implementation**
- **Diversity Indices** - Shannon entropy, Simpson index, effective archetype count
- **Trend Classification** - Linear regression analysis for archetype trajectories
- **Clustering Analysis** - K-means with 3 clusters (high performers, meta staples, niche picks)
- **Correlation Matrix** - Pearson correlation with significance indicators
- **Performance Insights** - Automated key findings extraction

### 🛠️ **Technical Implementation**

#### **New Module**: `src/python/analytics/advanced_metagame_analyzer.py`
- **Class**: `AdvancedMetagameAnalyzer` - Complete statistical analysis engine
- **Methods**: 7 core analysis functions covering all 18 features
- **Integration**: Seamless integration with existing pipeline
- **Performance**: Optimized for large datasets (1000+ decks)

#### **Enhanced Orchestrator**: `src/orchestrator.py`
- **New Method**: `_perform_advanced_analysis()` - Execute statistical analysis
- **New Method**: `_extract_key_insights()` - Generate automated insights
- **JSON Export**: `advanced_analysis.json` with comprehensive statistics
- **Logging**: Detailed progress tracking for all analytical steps

#### **Dependencies Added**
- **scikit-learn** - Machine learning and clustering algorithms
- **scipy** - Statistical functions and significance testing
- **numpy** - Enhanced mathematical operations for statistics

### 📊 **Output Enhancements**
- **JSON Export** - Complete statistical analysis in machine-readable format
- **18 Analytical Features** - All features from original execution plan implemented
- **Key Insights** - Automated interpretation of statistical patterns
- **Comprehensive Coverage** - Diversity, clustering, correlation, trends, cards

### 🔗 **GitHub Repository Integration**
- **[Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3)** - R-Meta-Analysis methodology source
- **[Jiliac/MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache)** - Tournament data source
- **[Badaro/MTGOFormatData](https://github.com/Badaro/MTGOFormatData)** - Classification rules and card database

### 📈 **Performance Improvements**
- **Optimized Processing** - Efficient statistical calculations for large datasets
- **Memory Management** - Optimized data structures for statistical analysis
- **Parallel Processing** - Concurrent analysis execution where possible
- **Caching** - Intelligent caching of statistical computations

### 🎯 **User Experience**
- **Automated Analysis** - No additional user configuration required
- **Comprehensive Results** - Complete statistical profile of every analysis
- **Academic Quality** - Professional-grade statistical insights
- **JSON Export** - Machine-readable format for further analysis

---

## 🆕 **v0.3.3** - MTG Color System & Link Fixes (January 15, 2025)

### ✨ **MAJOR NEW FEATURES**

#### 🌈 **Authentic MTG Color System**
- **Color Detection Engine** - New `ColorDetector` class analyzing 28,442 cards from MTGOFormatData
- **Complete WUBRG System** - Full White, blUe, Black, Red, Green color analysis
- **Guild Recognition** - 10 two-color guilds (Azorius, Dimir, Rakdos, Gruul, Selesnya, etc.)
- **Tri-Color Clans** - 10 three-color combinations (Esper, Jeskai, Bant, Mardu, etc.)
- **Visual Integration** - Authentic MTG colors applied to ALL charts and interface
- **Archetype Enhancement** - "Izzet Prowess" instead of "Prowess", "Boros Ramp" instead of "Ramp"

#### 🔗 **Functional Decklist Links**
- **Link Extraction Fixed** - All decklist links now functional via `AnchorUri` parsing
- **100% Coverage** - Links work for MTGO, Melee.gg, and TopDeck.gg sources
- **Direct Navigation** - Click-through to original decklists from all interfaces

#### 📊 **Enhanced Visualizations**
- **Color-Coded Charts** - All 9 chart types now use authentic MTG guild colors
- **Consistent Palette** - Izzet=blue/red, Boros=white/red, Azorius=white/blue, etc.
- **Visual Clarity** - Mana symbols and color borders in archetype overview
- **Professional Look** - MTG-authentic color scheme throughout interface

#### 🎯 **Data Quality Improvements**
- **Deduplication System** - Automatic removal of duplicate tournament entries
- **31% Reduction** - Typical 31% duplicate removal (e.g., 1,605 → 1,103 unique decks)
- **Better Accuracy** - More precise metagame percentages after deduplication
- **Source Validation** - Improved tournament data validation and processing

### 🛠️ **Technical Implementation**
- **`src/python/classifier/color_detector.py`** - New color detection engine
- **`src/python/visualizations/metagame_charts.py`** - Updated with MTG color system
- **`src/orchestrator.py`** - Enhanced with color analysis and deduplication
- **Helper Functions** - `_get_guild_names_for_archetypes()` for consistent color application

### 🎨 **User Experience**
- **Authentic MTG Feel** - Colors match official MTG guild identities
- **Functional Links** - All decklist links now work correctly
- **Visual Consistency** - Same color scheme across all charts and pages
- **Professional Polish** - Production-ready interface with MTG branding

---

## 🆕 **v0.3.2** - English Migration & Classification Fixes (July 13, 2025)

### ✨ **Major Changes**

#### 🌍 **Complete French → English Migration**
- **Interface Translation** - All user-facing messages, buttons, labels translated
- **Chart Titles** - All visualization titles in English (metagame share, winrates, etc.)
- **Code Comments** - Critical comments and docstrings translated
- **API Documentation** - FastAPI endpoints and error messages in English
- **Log Messages** - All pipeline logs and CLI output in English
- **HTML Generation** - Dashboard templates and UI elements in English

#### 🎯 **Archetype Classification Improvements**
- **Standard Focus** - Removed non-Standard archetypes (Storm, Splinter Twin, Death Shadow)
- **"Others" Classification** - Improved generic/monocolor archetype handling
- **Source Attribution** - Fixed MTGO source classification (no more "mtgo.com (Other)")
- **Accuracy Enhancement** - Better differentiation between Challenge/League/General MTGO

#### 🔧 **Technical Improvements**
- **Pipeline Stability** - English interface with maintained functionality
- **Data Integrity** - All real tournament data preserved during migration
- **UI Consistency** - Unified English experience across all components
- **Code Quality** - Improved maintainability with English comments

### 🛠️ **Migration Process**
- **Systematic Approach** - 6-phase migration with testing at each step
- **Quality Assurance** - 100% verification of translated elements
- **Backward Compatibility** - All existing functionality preserved
- **Documentation** - Complete translation mapping created

### 🎨 **User Experience**
- **Professional Interface** - Consistent English terminology
- **Chart Clarity** - English titles improve international accessibility
- **Error Messages** - Clear English diagnostics and logging
- **Dashboard Polish** - Cohesive English user experience

---

## 🆕 **v0.3.1** - UX Improvements (July 13, 2025)

### ✨ **New Features**

#### 🎯 **MTGO Differentiation**
- **MTGO Challenge** vs **MTGO League 5-0** - Precise environment distinction
- **Intelligent Parsing** - Automatic detection via URL patterns
- **Jiliac Compatibility** - Reliable comparison with external data

#### 🔗 **Enhanced Navigation**
- **Clickable URLs** - Direct access to tournaments from dashboard
- **Styled Buttons** - Professional interface with icons 🔗
- **New Tab Opening** - Smooth navigation without context loss

#### 📊 **Export & Organization**
- **CSV Export** - Complete JavaScript function (in development)
- **Analyses/ Folder** - Organized structure with format/date prefixes
- **Functional Buttons** - Dashboard return + data export

#### 🎨 **User Interface**
- **Colored Badges** - Sources visible under "Complete Analysis"
- **Distinctive Colors** - Turquoise (melee.gg), Red (Challenge), Green (League)
- **Immediate Visibility** - Source understanding at a glance

### 🔧 **Technical Improvements**

#### **Orchestrator** (`src/orchestrator.py`)
- **Fonction `_determine_source()`
