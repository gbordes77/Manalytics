# 🎯 Manalytics - MTG Metagame Analytics Pipeline

> **Automated Magic: The Gathering metagame analysis** - Pipeline generating **9 interactive visualizations + advanced statistical analysis** in under 30 seconds

## ⚡ Lightning Tour (30 seconds)

```bash
# 1. Clone & Setup
git clone https://github.com/gbordes77/Manalytics.git && cd Manalytics
git checkout feature/english-migration  # Latest English version

# 2. Install
pip install -r requirements.txt

# 3. Run Analysis
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# 4. View Results (9 interactive charts + advanced analytics)
open Analyses/standard_analysis_2025-07-01_2025-07-07/standard_2025-07-01_2025-07-07.html
```

**Result**: 9 interactive HTML charts + comprehensive statistical analysis generated automatically

---

## 🚀 Onboarding Kit - Guided Journey (2h total)

> **⚠️ NEW DEVELOPER?** Start with the [**✅ VALIDATION CHECKLIST**](docs/ONBOARDING_CHECKLIST.md) to self-assess at each step.

### 📋 **STEP 1: Project Understanding** (15 min)
👉 **Read**: [**ROADMAP.md**](docs/ROADMAP.md) - Product vision v0.3.2 → v1.0

### 🏗️ **STEP 2: Technical Architecture** (30 min)
👉 **Read**: [**ARCHITECTURE_QUICKREAD.md**](docs/ARCHITECTURE_QUICKREAD.md) - Modular design & extension points

### ⚙️ **STEP 3: Development Setup** (45 min)
👉 **Follow**: [**SETUP_DEV.md**](docs/SETUP_DEV.md) - Environment setup & first pipeline run

### 🎯 **STEP 4: First Contribution** (30 min)
👉 **Follow**: [**INSTRUCTIONS_NOUVELLE_EQUIPE.md**](docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md) - Make your first PR

**✅ SUCCESS**: After 2h, you're operational and ready to contribute effectively!

---

## 🌟 What's New in v0.3.4

### 🔬 **Advanced Statistical Analysis**
- **Shannon & Simpson Diversity**: Metagame diversity indices with effective archetype count
- **Temporal Trend Analysis**: Rising/Declining/Volatile/Stable archetype categorization
- **K-means Clustering**: Archetype grouping based on performance metrics
- **Correlation Analysis**: Statistical significance testing for archetype relationships
- **Card Usage Statistics**: Comprehensive card frequency and meta analysis
- **Key Insights Extraction**: Automated interpretation of statistical patterns

### 🎨 **NEW: Data Visualization Excellence (v0.3.4.1)**
- **Industry Standards**: Matches MTGGoldfish, 17lands, Untapped.gg professional quality
- **Accessibility Compliance**: Full colorblind support (8% population) with WCAG AA standards
- **Matchup Matrix Revolution**: ColorBrewer RdYlBu palette with adaptive text system
- **Visual Consistency**: All visualizations standardized to 700px height for seamless navigation
- **Absolute Pie Chart Rules**: Zero "Autres/Non classifiés" in pie charts, maximum 12 segments
- **Professional Aesthetics**: Scientific color palettes and optimal readability

### 📊 **R-Meta-Analysis Integration**
- **GitHub Integration**: Connected to [Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3) R-Meta-Analysis repository
- **Statistical Replication**: Reproduces R-based metagame analysis in Python
- **Academic Standards**: Implements peer-reviewed statistical methodologies
- **Comprehensive Output**: JSON exports with all 18 analytical features

### 🧮 **Advanced Metrics**
- **Diversity Indices**: Shannon entropy, Simpson index, effective archetype count
- **Trend Classification**: Automated categorization of archetype trajectories
- **Clustering Analysis**: K-means grouping with silhouette scoring
- **Correlation Matrix**: Pearson correlation with p-value significance testing
- **Performance Insights**: Automated key findings extraction

### 🌈 **Authentic MTG Color System**
- **Guild Colors**: Authentic MTG colors throughout interface (Izzet=blue/red, Boros=white/red, etc.)
- **28,442 Cards**: Complete color database from MTGOFormatData
- **Visual Enhancement**: Mana symbols and color-coded archetype names
- **Chart Integration**: All 9 visualizations use authentic MTG guild colors

### 🔗 **Functional Decklist Links**
- **100% Working Links**: All decklist links now functional via AnchorUri extraction
- **Multi-Source Support**: Links work for MTGO, Melee.gg, and TopDeck.gg
- **Direct Navigation**: Click-through to original decklists from all interfaces

### 🎯 **Data Quality Improvements**
- **Deduplication System**: Automatic removal of duplicate tournament entries
- **31% Reduction**: Typical duplicate removal (e.g., 1,605 → 1,103 unique decks)
- **Better Accuracy**: More precise metagame percentages after deduplication

### 🌍 **Complete English Migration**
- **Full Interface**: All user messages, charts, and UI elements now in English
- **International Ready**: Professional English experience for global users
- **Maintainable**: English code comments for international development teams

---

## 🎨 Features Overview

### 📊 **9 Interactive Visualizations**
1. **Metagame Pie Chart** - Archetype distribution overview
2. **Metagame Bar Chart** - Detailed share percentages
3. **Winrate Confidence** - Performance with statistical confidence
4. **Tiers Scatter Plot** - Archetype tier classification
5. **Bubble Chart** - Winrate vs metagame presence
6. **Top Performers** - Highest winrate archetypes
7. **Data Sources** - Tournament source distribution
8. **Temporal Evolution** - Archetype trends over time
9. **Matchup Matrix** - Head-to-head performance analysis

### 🔬 **Advanced Statistical Analysis**
- **Shannon Diversity Index** - Metagame diversity measurement
- **Simpson Index** - Alternative diversity metric
- **Effective Archetype Count** - Practical diversity measure
- **Temporal Trend Analysis** - Rising/Declining/Volatile/Stable categorization
- **K-means Clustering** - Archetype performance grouping
- **Correlation Matrix** - Statistical relationship analysis
- **Card Usage Statistics** - Comprehensive card frequency analysis
- **Key Insights Extraction** - Automated interpretation of patterns

### 🎯 **Multi-Source Data**
- **MTGO**: Challenge, League 5-0, and general tournaments
- **Melee.gg**: Paper tournament results
- **TopDeck.gg**: Additional tournament coverage

### 🔄 **Real-Time Processing**
- **Under 30s**: Complete analysis generation including advanced statistics
- **Real Data Only**: No mock data policy enforced
- **Scalable**: Handles thousands of tournaments efficiently

---

## 🛠️ Technical Stack

### **Core Technologies**
- **Python 3.11+**: Main programming language
- **Plotly**: Interactive visualizations
- **Pandas**: Data processing and analysis
- **Scikit-learn**: Machine learning and clustering
- **Scipy**: Statistical analysis and significance testing
- **FastAPI**: API endpoints (for future web interface)

### **Data Processing**
- **Multi-format Support**: Standard, Modern, Legacy
- **Real Tournament Data**: MTGODecklistCache integration
- **Intelligent Classification**: Advanced archetype detection using [MTGOFormatData](https://github.com/Badaro/MTGOFormatData)
- **Statistical Analysis**: Advanced metagame metrics and trend analysis
- **Performance Optimized**: Efficient data pipeline

### **Essential Dependencies**
- **[MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache)**: Raw tournament data source
- **[MTGOFormatData](https://github.com/Badaro/MTGOFormatData)**: Official archetype classification rules and card database
- **[Jiliac/Aliquanto3](https://github.com/Jiliac/Aliquanto3)**: R-Meta-Analysis repository for statistical methodology
- **Real Data Only**: Strict policy enforced via pre-commit hooks

### **Quality Assurance**
- **Pre-commit Hooks**: Automated code quality (black, flake8, isort)
- **No Mock Data**: Strict real data policy
- **Testing**: Comprehensive test coverage
- **Documentation**: Living documentation system

---

## 📈 Getting Started

### **Prerequisites**
- Python 3.11 or higher
- Git
- ~2GB disk space for tournament data

### **Quick Setup**
1. **Clone the repository**
   ```bash
   git clone https://github.com/gbordes77/Manalytics.git
   cd Manalytics
   ```

2. **Choose your version**
   ```bash
   # Latest English version with advanced analytics (recommended)
   git checkout feature/english-migration

   # Or stable release
   git checkout v0.3.2
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pre-commit install
   ```

4. **Run your first analysis**
   ```bash
   python run_full_pipeline.py --format Standard --start-date 2025-01-01 --end-date 2025-01-15
   ```

5. **View results**
   - Open the generated HTML dashboard
   - Explore the 9 interactive visualizations
   - Check the `advanced_analysis.json` for statistical insights
   - Review the `Analyses/` folder for all outputs

---

## 🎯 Project Vision

### **Mission**
Democratize MTG metagame analysis through complete automation, providing professional-grade insights with academic-level statistical analysis to players, organizers, and content creators.

### **Current State (v0.3.4)**
- Complete English interface for international use
- Advanced statistical analysis with R-Meta-Analysis integration
- 18 analytical features including diversity indices and clustering
- Robust multi-source data pipeline
- 9 interactive visualization types
- Professional documentation system
- Ready for next development phase

### **Next Steps (v0.4.0)**
- Real-time web dashboard
- Interactive format/date selection
- Enhanced user experience
- API-first architecture

### **Long-term Vision (v1.0)**
- SaaS platform with authentication
- Multi-user support
- Premium analytics features
- Mobile applications

---

## 🤝 Contributing

### **For New Contributors**
1. **Complete Onboarding**: Follow the [guided journey](docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md)
2. **Read Architecture**: Understand the [system design](docs/ARCHITECTURE_QUICKREAD.md)
3. **Setup Environment**: Follow the [development setup](docs/SETUP_DEV.md)
4. **Make First PR**: Add your name to the team list

### **Development Workflow**
- **Branch Strategy**: Feature branches from latest
- **Code Quality**: Pre-commit hooks enforced
- **Documentation**: Living docs updated with each PR
- **Testing**: Comprehensive test coverage required

---

## 📞 Support & Resources

### **Documentation**

#### **📋 Core Documentation**
- [**Team Instructions**](docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md) - Complete onboarding guide
- [**Architecture Guide**](docs/ARCHITECTURE_QUICKREAD.md) - System design overview
- [**Development Setup**](docs/SETUP_DEV.md) - Environment configuration
- [**Project Roadmap**](docs/ROADMAP.md) - Product vision and milestones
- [**Advanced Analytics Guide**](docs/ADVANCED_ANALYTICS.md) - Statistical analysis documentation

#### **🔧 Developer Documentation**
- [**API Reference**](docs/API_REFERENCE_ADVANCED_ANALYTICS.md) - Complete function documentation
- [**Orchestrator Integration**](docs/ORCHESTRATOR_INTEGRATION.md) - Pipeline integration guide
- [**Implementation Summary**](docs/IMPLEMENTATION_SUMMARY_v0.3.4.md) - Complete v0.3.4 details

#### **👥 User Documentation**
- [**User Guide**](docs/USER_GUIDE_ADVANCED_ANALYTICS.md) - Practical usage and interpretation
- [**Changelog**](docs/CHANGELOG.md) - Version history and improvements

#### **🔄 Team Management**
- [**Team Handoff Checklist**](docs/TEAM_HANDOFF_CHECKLIST.md) - Complete transition guide
- [**Onboarding Checklist**](docs/ONBOARDING_CHECKLIST.md) - Self-assessment validation

### **Quick Help**
- **Setup Issues**: Check [troubleshooting guide](docs/SETUP_DEV.md#troubleshooting)
- **Architecture Questions**: Review [architecture docs](docs/ARCHITECTURE_QUICKREAD.md)
- **Contribution Guide**: Follow [development workflow](docs/SETUP_DEV.md#development-workflow)

---

## 🎉 Success Metrics

- **✅ Advanced Analytics**: 18 statistical features with R-Meta-Analysis integration
- **✅ English Migration**: Complete international-ready interface
- **✅ Real Data Only**: No mock data policy enforced
- **✅ Fast Analysis**: <30s for complete metagame analysis + statistical insights
- **✅ Multi-Source**: MTGO, Melee.gg, TopDeck.gg integration
- **✅ Interactive**: 9 dynamic visualizations + comprehensive statistics
- **✅ Professional**: Production-ready code and documentation

---

*Last updated: July 13, 2025*
*Version: v0.3.4*
*Status: Advanced analytics integrated - Ready for next development phase*
