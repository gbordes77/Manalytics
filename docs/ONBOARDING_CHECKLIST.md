# ✅ Onboarding Checklist - Step-by-Step Validation

> **Objective**: Ensure every new developer masters Manalytics perfectly

## 🎯 **STEP 1: Project Understanding** (15 min)

**📋 Before continuing, validate that you can answer:**
- [ ] What's the difference between v0.3.4 and v1.0?
- [ ] Why do we use multi-source scraping?
- [ ] What are the 3 supported formats?
- [ ] What's the purpose of the 9 visualizations?
- [ ] **🆕 What is Shannon diversity and how is it calculated?**
- [ ] **🆕 How does temporal trend analysis categorize archetypes?**
- [ ] **🆕 What's the purpose of K-means clustering in archetype analysis?**
- [ ] **🆕 How does the R-Meta-Analysis integration work with Jiliac/Aliquanto3?**
- [ ] **🆕 What are the 18 analytical features implemented in v0.3.4?**

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
- [ ] **🆕 Why do we work only on main branch?**
- [ ] **🆕 What is the MODIFICATION_TRACKER.md file for?**

**🔗 Read**: [ARCHITECTURE_QUICKREAD.md](ARCHITECTURE_QUICKREAD.md) | **➡️ Next**: [SETUP_DEV.md](SETUP_DEV.md)

---

## ⚙️ **STEP 3: Development Setup** (45 min)

**📋 Before continuing, validate that you successfully:**
- [ ] Cloned the repo and checked out main branch ✅
- [ ] Installed Python dependencies
- [ ] Installed pre-commit hooks
- [ ] Successfully ran a test pipeline
- [ ] **🆕 Verified the dashboard interface is in English**
- [ ] **🆕 Confirmed the Analyses/ folder structure is created**
- [ ] **🆕 Checked that archetype classification works correctly**
- [ ] **🆕 Understood the main-branch-only workflow**
- [ ] Saw the 9 graphs generated in the output folder

**🔗 Followed**: [SETUP_DEV.md](SETUP_DEV.md) | **➡️ Next**: First Contribution

---

## 🎯 **STEP 4: First Contribution** (30 min)

**📋 Your onboarding is complete when:**
- [ ] **🆕 You've added your entry to MODIFICATION_TRACKER.md BEFORE modifying**
- [ ] You're working on main branch (no feature branch)
- [ ] Your modification is committed to main
- [ ] Your commit is pushed to main
- [ ] **🆕 Your name is added to the team list with [NAME]_[YYYY-MM-DD_HH-MM] format**
- [ ] **🆕 You understand the rollback procedure if needed**

**🔗 Followed**: [INSTRUCTIONS_NOUVELLE_EQUIPE.md](INSTRUCTIONS_NOUVELLE_EQUIPE.md) workflow

---

## 📋 **VALIDATION COMPLETE**

**✅ You now master:**
- ✅ Manalytics v0.3.4 → v1.0 product vision
- ✅ Technical architecture and extension points
- ✅ Operational development environment
- ✅ **🆕 Main-branch-only workflow and rollback procedures**
- ✅ **🆕 Modification tracking system**
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

### **Step 4: Contribution Issues**
- **Problem**: Confused about main-branch workflow
- **Solution**: No branches needed, just commit directly to main after validation

### **Modification Tracker Issues**
- **Problem**: Don't understand the MODIFICATION_TRACKER.md format
- **Solution**: Check existing entries in the file for examples

### **English Interface Issues**
- **Problem**: Some elements still in French
- **Solution**: Check if you're on main branch with latest changes

### **Archetype Classification Issues**
- **Problem**: Unexpected archetype assignments
- **Solution**: Check if non-Standard archetypes are correctly classified as "Others"

### **Rollback Issues**
- **Problem**: Need to undo changes
- **Solution**: Use `git revert <commit-hash>` and update MODIFICATION_TRACKER.md

---

*Checklist created: July 13, 2025*
*Version: v0.3.4*
*Updated for main-branch workflow: January 14, 2025*
