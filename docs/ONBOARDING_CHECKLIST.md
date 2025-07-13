# ✅ Onboarding Checklist - Step-by-Step Validation

> **Objective**: Ensure every new developer masters Manalytics perfectly

## 🎯 **STEP 1: Project Understanding** (15 min)

**📋 Before continuing, validate that you can answer:**
- [ ] What's the difference between v0.3.2 and v1.0?
- [ ] Why do we use multi-source scraping?
- [ ] What are the 3 supported formats?
- [ ] What's the purpose of the 9 visualizations?
- [ ] **🆕 Why distinguish MTGO Challenge vs League?**
- [ ] **🆕 How to access tournaments directly from the dashboard?**
- [ ] **🆕 What changed in the English migration (v0.3.2)?**
- [ ] **🆕 How does the improved archetype classification work?**

**🔗 Read**: [ROADMAP.md](ROADMAP.md) | **➡️ Next**: [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md)

---

## 🏗️ **STEP 2: Technical Architecture** (30 min)

**📋 Before continuing, validate that you can answer:**
- [ ] How does data flow from MTGO to analyzer?
- [ ] Where to add a new scraper?
- [ ] How does the archetype classifier work?
- [ ] What are the 4 main modules?
- [ ] **🆕 Where are the English interface elements located?**
- [ ] **🆕 How does the source attribution system work?**

**🔗 Read**: [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md) | **➡️ Next**: [SETUP_DEV.md](SETUP_DEV.md)

---

## ⚙️ **STEP 3: Development Setup** (45 min)

**📋 Before continuing, validate that you successfully:**
- [ ] Cloned the repo and checked out the right version ✅ (already done)
- [ ] Installed Python dependencies
- [ ] Installed pre-commit hooks
- [ ] Successfully ran a test pipeline
- [ ] **🆕 Verified the dashboard interface is in English**
- [ ] **🆕 Confirmed the Analyses/ folder structure is created**
- [ ] **🆕 Checked that archetype classification works correctly**
- [ ] Saw the 9 graphs generated in the output folder

**🔗 Followed**: [SETUP_DEV.md](SETUP_DEV.md) | **➡️ Next**: First Contribution

---

## 🎯 **STEP 4: First Contribution** (30 min)

**📋 Your onboarding is complete when:**
- [ ] Your branch is created
- [ ] Your modification is committed
- [ ] Your PR is created with template filled
- [ ] Your PR is reviewed and merged
- [ ] **🆕 Your name is added to the team list**

**🔗 Followed**: [INSTRUCTIONS_NOUVELLE_EQUIPE.md](INSTRUCTIONS_NOUVELLE_EQUIPE.md) workflow

---

## 📋 **VALIDATION COMPLETE**

**✅ You now master:**
- ✅ Manalytics v0.3.2 → v1.0 product vision
- ✅ Technical architecture and extension points
- ✅ Operational development environment
- ✅ Contribution workflow and governance
- ✅ **🆕 English interface and improved features**
- ✅ **🆕 Enhanced archetype classification system**
- ✅ **🆕 MTGO source attribution improvements**

**🚀 You're ready to contribute effectively to the project!**

---

## 🚨 **TROUBLESHOOTING**

### **Step 1-2: Reading Issues**
- **Problem**: Documentation unclear
- **Solution**: Re-read carefully, consult [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md)

### **Step 3: Setup Issues**
- **Problem**: Dependencies or pipeline fails
- **Solution**: Check [SETUP_DEV.md - Troubleshooting](SETUP_DEV.md#troubleshooting-express)

### **Step 4: PR Issues**
- **Problem**: PR blocked or template unclear
- **Solution**: Each checkbox corresponds to a documentation section

### **English Interface Issues**
- **Problem**: Some elements still in French
- **Solution**: Check if you're on the right branch (feature/english-migration or v0.3.2+)

### **Archetype Classification Issues**
- **Problem**: Unexpected archetype assignments
- **Solution**: Check if non-Standard archetypes are correctly classified as "Others"

---

*Checklist created: July 13, 2025*
*Version: v0.3.2*
*Last updated: July 13, 2025*
