# 🎯 Manalytics - MTG Metagame Analytics Pipeline

> **Automated Magic: The Gathering metagame analysis** - Pipeline generating **9 interactive visualizations** in under 30 seconds

## ⚡ Lightning Tour (30 seconds)

```bash
# 1. Clone & Setup
git clone https://github.com/gbordes77/Manalytics.git && cd Manalytics
git checkout feature/english-migration  # Latest English version

# 2. Install
pip install -r requirements.txt

# 3. Run Analysis
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# 4. View Results (9 interactive charts)
open Analyses/standard_analysis_2025-07-01_2025-07-07/standard_2025-07-01_2025-07-07.html
```

**Result**: 9 interactive HTML charts generated automatically (metagame share, matchups, winrates, tiers, temporal evolution...)

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

## 🌟 What's New in v0.3.2

### 🌍 **Complete English Migration**
- **Full Interface**: All user messages, charts, and UI elements now in English
- **International Ready**: Professional English experience for global users
- **Maintainable**: English code comments for international development teams

### 🎯 **Improved Classification**
- **Standard Focus**: Removed non-Standard archetypes (Storm, Splinter Twin, etc.)
- **Better "Others"**: Improved handling of generic/monocolor archetypes
- **Source Clarity**: Fixed MTGO source attribution (no more confusion)

### 🔧 **Enhanced Experience**
- **Consistent UI**: Unified English terminology across all components
- **Accurate Data**: Better archetype classification for Standard format
- **Clear Sources**: Distinct MTGO Challenge/League/General classification

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

### 🎯 **Multi-Source Data**
- **MTGO**: Challenge, League 5-0, and general tournaments
- **Melee.gg**: Paper tournament results
- **TopDeck.gg**: Additional tournament coverage

### 🔄 **Real-Time Processing**
- **Under 30s**: Complete analysis generation
- **Real Data Only**: No mock data policy enforced
- **Scalable**: Handles thousands of tournaments efficiently

---

## 🛠️ Technical Stack

### **Core Technologies**
- **Python 3.11+**: Main programming language
- **Plotly**: Interactive visualizations
- **Pandas**: Data processing and analysis
- **FastAPI**: API endpoints (for future web interface)

### **Data Processing**
- **Multi-format Support**: Standard, Modern, Legacy
- **Real Tournament Data**: MTGODecklistCache integration
- **Intelligent Classification**: Advanced archetype detection
- **Performance Optimized**: Efficient data pipeline

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
   # Latest English version (recommended)
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
   - Check the `Analyses/` folder for all outputs

---

## 🎯 Project Vision

### **Mission**
Democratize MTG metagame analysis through complete automation, providing professional-grade insights to players, organizers, and content creators.

### **Current State (v0.3.2)**
- Complete English interface for international use
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
- [**Team Instructions**](docs/INSTRUCTIONS_NOUVELLE_EQUIPE.md) - Complete onboarding guide
- [**Architecture Guide**](docs/ARCHITECTURE_QUICKREAD.md) - System design overview
- [**Development Setup**](docs/SETUP_DEV.md) - Environment configuration
- [**Project Roadmap**](docs/ROADMAP.md) - Product vision and milestones

### **Quick Help**
- **Setup Issues**: Check [troubleshooting guide](docs/SETUP_DEV.md#troubleshooting)
- **Architecture Questions**: Review [architecture docs](docs/ARCHITECTURE_QUICKREAD.md)
- **Contribution Guide**: Follow [development workflow](docs/SETUP_DEV.md#development-workflow)

---

## 🎉 Success Metrics

- **✅ English Migration**: Complete international-ready interface
- **✅ Real Data Only**: No mock data policy enforced
- **✅ Fast Analysis**: <30s for complete metagame analysis
- **✅ Multi-Source**: MTGO, Melee.gg, TopDeck.gg integration
- **✅ Interactive**: 9 dynamic visualizations
- **✅ Professional**: Production-ready code and documentation

---

*Last updated: July 13, 2025*
*Version: v0.3.2*
*Status: Ready for next development phase*
