# 📋 Roadmap Manalytics - Product Vision

> **Mission**: Democratize MTG metagame analysis through complete automation

## 🏁 Key Tags & Milestones

### ✅ **v0.3.0** - Clean Baseline
- **Date**: July 13, 2025
- **Achieved**: Professional repository, secured hooks, complete documentation
- **Key Decision**: Modular `src/` architecture for future scalability
- **Impact**: Team can onboard in <2h, collaborative development possible

### ✅ **v0.3.1** - UX Improvements
- **Date**: July 13, 2025
- **Achieved**: Enhanced user interface, MTGO differentiation, optimized navigation
- **Features**: Colored source badges, clickable URLs, CSV export, Analyses/ organization
- **Key Decision**: Challenge/League distinction for precise Jiliac comparison
- **Impact**: 1-click navigation to tournaments, immediate source visibility

### ✅ **v0.3.2** - English Migration & Classification Fixes
- **Date**: July 13, 2025
- **Achieved**: Complete French → English interface migration, improved archetype classification
- **Features**: Full English UI, better Standard archetype handling, fixed MTGO source attribution
- **Key Decision**: International-ready English interface for broader accessibility
- **Impact**: Professional English experience, improved archetype accuracy, consistent source classification

### ✅ **v0.3.3** - MTG Color System & Link Fixes
- **Date**: January 15, 2025
- **Achieved**: Authentic MTG color system, functional decklist links, data deduplication
- **Features**: Guild-based color palette, working links, 31% duplicate removal, enhanced visualizations

### ✅ **v0.3.4** - Advanced Statistical Analysis Integration
- **Date**: July 13, 2025
- **Achieved**: Complete advanced analytics with R-Meta-Analysis integration, comprehensive documentation
- **Features**: Shannon/Simpson diversity, temporal trends, K-means clustering, correlation analysis, 18 statistical features
- **Key Decision**: Academic-grade statistical analysis with GitHub integration to Jiliac/Aliquanto3
- **Impact**: Professional statistical insights, automated trend analysis, complete documentation ecosystem
- **Key Decision**: Authentic MTG branding with guild colors throughout interface
- **Impact**: Professional MTG-authentic experience, functional navigation, improved data quality

### ✅ **v0.3.5** - Critical Matchup Matrix Corrections (Current)
- **Date**: January 15, 2025
- **Achieved**: Perfect visualization consistency and hierarchical ordering across all charts
- **Features**: Izzet Prowess first position, unified archetype naming, hierarchical axis ordering
- **Key Decision**: Centralized ordering system for all visualizations
- **Impact**: Professional consistency, improved user experience, elimination of naming disparities

### 🚧 **v0.4.0** - Interactive Dashboard (Q3 2025)
- **Objective**: Real-time web interface
- **Features**: FastAPI + React, format/date selection, PDF export
- **Key Decision**: API-first design for frontend/backend decoupling
- **KPI**: Reduce analysis time from 15min → 30s

### 🎯 **v1.0.0** - SaaS Ready (Q4 2025)
- **Vision**: Multi-user platform
- **Features**: Auth, Redis cache, metagame alerts, public API
- **Business**: Freemium model, premium analyses
- **Scalability**: Support 1000+ simultaneous users

## 🧭 Architectural Decisions

### **Why Multi-Source Scraping**
- **Problem**: No official Wizards API
- **Solution**: MTGO + Melee + TopDeck aggregation
- **Benefit**: Complete data, resilience to failures

### **Why Real Data Only**
- **Problem**: Unreliable analyses with fake data
- **Solution**: Strict enforcement of tournament data only
- **Benefit**: Credible results, professional credibility

### **Why English Interface** (v0.3.2)
- **Problem**: French interface limited international adoption
- **Solution**: Complete migration to English while preserving functionality
- **Benefit**: International accessibility, professional appearance

### **Why Source Classification Accuracy** (v0.3.2)
- **Problem**: Confusion between archetype classification and data sources
- **Solution**: Fixed MTGO source attribution, improved archetype handling
- **Benefit**: Clear source understanding, accurate Standard classification

## 🎯 Strategic Priorities

### **Q3 2025 - User Experience**
- **Real-time dashboard**: Instant format switching
- **Visual improvements**: Modern React components
- **Export capabilities**: PDF reports, data downloads
- **Performance**: <30s analysis time

### **Q4 2025 - Platform Readiness**
- **Multi-user support**: Authentication system
- **API ecosystem**: Public endpoints for developers
- **Business model**: Freemium with premium features
- **Scalability**: Cloud-ready architecture

### **2026 - Market Expansion**
- **Mobile app**: iOS/Android applications
- **AI insights**: Predictive metagame analysis
- **Community features**: User-contributed data
- **Global reach**: Multi-language support

## 🔄 Version Strategy

### **Incremental Value**
Each version adds measurable user value:
- **v0.3.x**: Foundation and migration
- **v0.4.x**: Interactive experience
- **v1.0.x**: SaaS platform

### **Backward Compatibility**
- **Data formats**: Preserved across versions
- **API endpoints**: Versioned for stability
- **User workflows**: Gradually enhanced

### **Quality Gates**
- **Testing**: 90%+ code coverage
- **Documentation**: Living docs with each release
- **Performance**: Sub-minute analysis times
- **User feedback**: Continuous improvement

---

## 🚀 Next Steps

### **Immediate (July 2025)**
1. **Complete v0.3.2 stabilization**
2. **User feedback collection**
3. **Performance optimization**
4. **API design planning**

### **Short-term (Q3 2025)**
1. **FastAPI backend development**
2. **React frontend prototyping**
3. **Real-time features implementation**
4. **Beta user testing**

### **Long-term (Q4 2025)**
1. **SaaS platform launch**
2. **Business model implementation**
3. **User acquisition strategy**
4. **Scaling infrastructure**

---

*Last updated: July 13, 2025*
*Current: v0.3.2*
*Next milestone: v0.4.0 Interactive Dashboard*
