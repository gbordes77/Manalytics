# 📊 Manalytics Project Audit Summary

**Date**: 2025-07-25T08:18:44.220874

## 📈 Statistics

- Total files: 264
- Total size: 9,553,568 bytes
- Python files: 113
- Test files: 23
- Documentation: 28

## 🔒 Security Issues Found

- **connection_string** in `scripts/audit_project.py` (medium severity)
- **hardcoded_password** in `scripts/test_melee_simple.py` (medium severity)
- **hardcoded_password** in `scripts/manage_users.py` (medium severity)
- **hardcoded_password** in `scripts/stress_test.py` (medium severity)
- **hardcoded_password** in `scripts/final_integration_test.py` (medium severity)

## 🔄 Duplicate Files Found: 7

- 2 copies: Api_token_and_login/melee_login.json, api_credentials/melee_login.json
- 12 copies: database/__init__.py, config/__init__.py, tests/__init__.py
- 8 copies: mtg_decklist_scrapper/__init__.py, scrapers/__init__.py, scrapers/clients/__init__.py
- 3 copies: data/reports/mtgo_metagame_20250725_004340.csv, data/reports/mtgo_metagame_20250725_010555.csv, data/reports/mtgo_metagame_20250725_011634.csv
- 3 copies: data/raw/mtgo/standard/leagues/.DS_Store, data/raw/mtgo/standard/challenge/.DS_Store, data/raw/melee/standard/.DS_Store

## 📁 Project Structure

Key directories present: src, tests, scripts, data, docs, database, scrapers
