# 👋 Instructions for New Team - Manalytics

> **Welcome!** You're joining the **Manalytics v0.3.2** project - Magic: The Gathering metagame analysis platform

## 🎯 **CLEAR MISSION**

Your goal is to become **operational in 2 hours maximum** and make your **first contribution on day one**.

**KPIs to achieve**:
- ✅ Complete project understanding ≤ 2h
- ✅ First pipeline run ≤ 15 min
- ✅ First PR merged Day 1

---

## 📋 **STRICT GUIDELINES - READ CAREFULLY**

### ⚠️ **RULE #1: MANDATORY ORDER**
You **MUST** follow steps **1→2→3→4** in this exact order. Each step prepares the next one.

### ⚠️ **RULE #2: VALIDATION REQUIRED**
At each step, you **MUST** validate your understanding with the checklist before continuing.

### ⚠️ **RULE #3: LIVING DOCUMENTATION**
The onboarding system is **self-monitored**. Any code modification without doc update will be **automatically blocked**.

---

## 🚀 **ONBOARDING JOURNEY (2h max)**

### **BEFORE STARTING**
1. Clone the repository: `git clone https://github.com/gbordes77/Manalytics.git`
2. Enter the folder: `cd Manalytics`
3. **IMPORTANT - Version choice**:
   - **Recommended**: `git checkout feature/english-migration` (latest with English interface)
   - **Alternative**: `git checkout v0.3.2` (stable version)
   - **Legacy**: `git checkout v0.3.1` (if you need French interface)

**⚠️ COMPATIBILITY**:
- If using **feature/english-migration** → follow these instructions exactly (latest)
- If using **v0.3.2** → interface is fully in English, pipeline is stable
- If using **v0.3.1** → interface is in French, check for French documentation

4. Open the [**✅ VALIDATION CHECKLIST**](ONBOARDING_CHECKLIST.md) in a separate tab

---

### 📋 **STEP 1: Product Vision** (15 min)

**🎯 ACTION**: Read **ENTIRELY** the document [**ROADMAP.md**](ROADMAP.md)

**📝 CONCRETE TASK**:
- Understand the v0.3.2 → v1.0 progression
- Identify 3 key architectural decisions
- Note your understanding of the "why scraping multi-sources" rationale

**✅ VALIDATION**: Open [ONBOARDING_CHECKLIST.md](ONBOARDING_CHECKLIST.md) and check the "Step 1" boxes

---

### 🏗️ **STEP 2: Technical Architecture** (30 min)

**🎯 ACTION**: Read **ENTIRELY** the document [**ARCHITECTURE_QUICKREAD.md**](ARCHITECTURE_QUICKREAD.md)

**📝 CONCRETE TASK**:
- Understand the modular `src/` structure
- Identify the 3 main data sources (MTGO, Melee, TopDeck)
- Locate the pipeline entry point (`run_full_pipeline.py`)
- Understand the English interface migration (v0.3.2 feature)

**✅ VALIDATION**: Check the "Step 2" boxes in your checklist

---

### 💻 **STEP 3: Development Setup** (45 min)

**🎯 ACTION**: Follow **ENTIRELY** the document [**SETUP_DEV.md**](SETUP_DEV.md)

**📝 CONCRETE TASK**:
1. Install dependencies: `pip install -r requirements-dev.txt`
2. Setup pre-commit hooks: `pre-commit install`
3. Run your first pipeline: `python run_full_pipeline.py --format Standard --start-date 2025-01-01 --end-date 2025-01-15`
4. Verify English interface in generated dashboard
5. Check that `Analyses/` folder is created with proper structure

**✅ VALIDATION**: Check the "Step 3" boxes in your checklist

---

### 🎯 **STEP 4: First Contribution** (30 min)

**🎯 ACTION**: Make your first contribution to prove operational readiness

**📝 CONCRETE TASK**:
1. Create a branch: `git checkout -b feature/my-first-change`
2. Modify this file (`INSTRUCTIONS_NOUVELLE_EQUIPE.md`): add your name in the "Team" section below
3. Commit: `git add . && git commit -m "docs: add [YOUR_NAME] to team"`
4. Push: `git push origin feature/my-first-change`
5. Create a PR on GitHub
6. **IMPORTANT**: In the PR template, check the "README Lightning Tour" box (since you're modifying documentation)

**📝 VALIDATION**: Your onboarding is complete when:
- [ ] Your branch is created
- [ ] Your modification is committed
- [ ] Your PR is created with template filled
- [ ] Your PR is reviewed and merged

**✅ FINAL CHECKPOINT**: First contribution successful!

---

## 🏆 **TEAM - Add your name here after your first PR**

*Developers who successfully completed Manalytics v0.3.2 onboarding:*

- Claude Sonnet 4 (AI Assistant) - onboarding completed on 2025-07-13
- [Your name here after your first PR]

---

## 🆘 **HELP & SUPPORT**

### **Stuck on Steps 1-2?**
Read carefully. If still stuck, consult [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md)

### **Stuck on Step 3?**
Consult [SETUP_DEV.md - Troubleshooting](SETUP_DEV.md#troubleshooting-express)

### **Stuck on Step 4?**
The PR template guides you. Each checkbox corresponds to a documentation section.

### **PR blocked by CI?**
The `onboarding-guard` workflow detected that you're modifying code without updating documentation. This is normal! Check the right box in the PR template.

---

## ⚡ **CRITICAL REMINDERS**

1. **MANDATORY ORDER**: 1→2→3→4 (each step prepares the next)
2. **VALIDATION REQUIRED**: Use the checklist at each step
3. **FIRST PR MANDATORY**: Add your name to this file
4. **PR TEMPLATE**: Always check a box (or n/a with justification)
5. **LIVING DOCUMENTATION**: Self-monitored system to guarantee quality
6. **VERSIONING**: These instructions are for v0.3.2+. Future versions will include their own updated instructions.

---

## 🌍 **ENGLISH MIGRATION COMPLETED**

### **What Changed in v0.3.2**
- **Complete Interface Translation**: All user messages, charts, and UI elements are now in English
- **Improved Classification**: Better archetype handling, removed non-Standard archetypes
- **Source Attribution**: Fixed MTGO source classification issues
- **Professional Experience**: Unified English interface for international use

### **What Stayed the Same**
- **All Functionality**: Complete feature parity with French version
- **Real Data**: Still uses only real tournament data (no mock data)
- **Pipeline Performance**: Same speed and reliability
- **File Structure**: Analyses/ folder structure preserved

---

## 🔄 **ONBOARDING KIT EVOLUTION**

**How this system evolves**:
- Each new version (v0.3.3, v0.4.0, etc.) may have updated onboarding instructions
- **Golden Rule**: Always use the instructions from the version you checked out
- If no instructions in your version → go back to v0.3.2 which is guaranteed stable

**Why this approach**:
- ✅ Guarantees instructions match the code
- ✅ Avoids version compatibility issues
- ✅ Allows onboarding process evolution

---

## 🎯 **SUCCESS**

**Congratulations!** If you followed these instructions, you now master:
- ✅ Manalytics v0.3.2 → v1.0 product vision
- ✅ Technical architecture and extension points
- ✅ Operational development environment
- ✅ Contribution workflow and governance
- ✅ English interface and improved classification system

**You're ready to contribute effectively to the project!**

---

*Instructions created on: July 13, 2025*
*Baseline: v0.3.2*
*Self-maintained onboarding system*
