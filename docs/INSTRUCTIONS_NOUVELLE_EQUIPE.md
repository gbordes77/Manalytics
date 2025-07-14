# 👋 Instructions for New Team - Manalytics

> **Welcome!** You're joining the **Manalytics v0.3.4** project - Magic: The Gathering metagame analysis platform with **advanced statistical analysis and authentic MTG color system**

## 🎯 **CLEAR MISSION**

Your goal is to become **operational in 2 hours maximum** and make your **first contribution on day one**.

**KPIs to achieve**:
- ✅ Complete project understanding ≤ 2h
- ✅ First pipeline run ≤ 15 min
- ✅ First contribution merged Day 1

---

## 📋 **STRICT GUIDELINES - READ CAREFULLY**

### ⚠️ **RULE #1: MANDATORY ORDER**
You **MUST** follow steps **1→2→3→4** in this exact order. Each step prepares the next one.

### ⚠️ **RULE #2: VALIDATION REQUIRED**
At each step, you **MUST** validate your understanding with the checklist before continuing.

### ⚠️ **RULE #3: LIVING DOCUMENTATION**
The onboarding system is **self-monitored**. Any code modification without doc update will be **automatically blocked**.

### ⚠️ **RULE #4: MAIN BRANCH ONLY**
All work is done directly on `main` branch. No feature branches. This simplifies rollbacks and avoids merge conflicts.

---

## 🚀 **ONBOARDING JOURNEY (2h max)**

### **BEFORE STARTING**
1. Clone the repository: `git clone https://github.com/gbordes77/Manalytics.git`
2. Enter the folder: `cd Manalytics`
3. **IMPORTANT - Always work on main**:
   - `git checkout main`
   - `git pull origin main` (ensure you have latest changes)

**⚠️ BRANCH POLICY**:
- **ONLY main branch** - No feature branches
- **Direct commits** to main after validation
- **Immediate rollback** if issues via `git revert`

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
1. **IMPORTANT**: Check [MODIFICATION_TRACKER.md](MODIFICATION_TRACKER.md) and add your entry BEFORE modifying
2. Stay on main: `git status` (should show "On branch main")
3. Modify this file (`INSTRUCTIONS_NOUVELLE_EQUIPE.md`): add your name in the "Team" section below
4. Commit: `git add . && git commit -m "docs: add [YOUR_NAME_DATETIME] to team"`
5. Push: `git push origin main`
6. **NO PR NEEDED** - Direct commit to main

**📝 VALIDATION**: Your onboarding is complete when:
- [ ] Your entry is added to MODIFICATION_TRACKER.md
- [ ] Your modification is committed to main
- [ ] Your name is added to the team list
- [ ] Your commit is pushed successfully

**✅ FINAL CHECKPOINT**: First contribution successful!

---

## 🏆 **TEAM - Add your name here after your first contribution**

*Format: [YOUR_NAME]_[YYYY-MM-DD_HH-MM] - Brief description*

*Developers who successfully completed Manalytics v0.3.4 onboarding:*

- Claude_Sonnet_4_2025-07-13_14-30 - AI Assistant, onboarding system setup
- Assistant_AI_2025-01-14_13-45 - Workflow simplification and tracking system
- [Your name here after your first contribution]

---

## 🆘 **HELP & SUPPORT**

### **Stuck on Steps 1-2?**
Read carefully. If still stuck, consult [GUIDE_DEVELOPPEUR.md](GUIDE_DEVELOPPEUR.md)

### **Stuck on Step 3?**
Consult [SETUP_DEV.md - Troubleshooting](SETUP_DEV.md#troubleshooting-express)

### **Stuck on Step 4?**
Check [MODIFICATION_TRACKER.md](MODIFICATION_TRACKER.md) for examples of proper entries.

### **Commit blocked by CI?**
Ensure you've updated [MODIFICATION_TRACKER.md](MODIFICATION_TRACKER.md) before your change.

---

## ⚡ **CRITICAL REMINDERS**

1. **MANDATORY ORDER**: 1→2→3→4 (each step prepares the next)
2. **VALIDATION REQUIRED**: Use the checklist at each step
3. **MAIN BRANCH ONLY**: No feature branches, direct commits to main
4. **MODIFICATION TRACKER**: Always update before making changes
5. **LIVING DOCUMENTATION**: Self-monitored system to guarantee quality
6. **IMMEDIATE ROLLBACK**: Use `git revert` if issues detected

---

## 🌍 **WORKFLOW SIMPLIFICATION**

### **What Changed in v0.3.4**
- **Main Branch Only**: No more feature branches to avoid merge conflicts
- **Direct Commits**: Faster integration, immediate rollback if needed
- **Modification Tracker**: Full traceability of all changes
- **Enhanced Safety**: Pre-commit hooks + rollback procedures

### **Why This Approach**
- ✅ **Faster Development**: No branch management overhead
- ✅ **Easier Rollbacks**: `git revert` is simpler than merge conflicts
- ✅ **Better Tracking**: MODIFICATION_TRACKER.md provides full history
- ✅ **Reduced Complexity**: One branch to rule them all

---

## 🔄 **ROLLBACK PROCEDURES**

### **If Your Change Causes Issues**
1. Identify the commit hash: `git log --oneline`
2. Revert the change: `git revert <commit-hash>`
3. Push the revert: `git push origin main`
4. Update MODIFICATION_TRACKER.md with rollback entry

### **If You Need to Undo Multiple Changes**
1. Use `git revert` for each commit in reverse order
2. Or use `git reset --hard <last-good-commit>` (⚠️ DANGEROUS)
3. Force push only if absolutely necessary: `git push --force-with-lease`

---

## 🎯 **SUCCESS**

**Congratulations!** If you followed these instructions, you now master:
- ✅ Manalytics v0.3.4 product vision
- ✅ Technical architecture and extension points
- ✅ Operational development environment
- ✅ Simplified main-branch workflow
- ✅ Modification tracking system

**You're ready to contribute effectively to the project!**

---

*Instructions created on: July 13, 2025*
*Updated for main-branch workflow: January 14, 2025*
*Self-maintained onboarding system*
