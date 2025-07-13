# 📋 Roadmap Manalytics - Vision Produit

> **Mission** : Démocratiser l'analyse métagame MTG par l'automatisation complète

## 🏁 Tags Clés & Jalons

### ✅ **v0.3.0** - Clean Baseline (Actuel)
- **Date** : 13 juillet 2025
- **Réalisé** : Repository professionnel, hooks sécurisés, documentation complète
- **Décision clé** : Architecture modulaire `src/` pour scalabilité future
- **Impact** : Équipe peut onboard en <2h, développement collaboratif possible

### 🚧 **v0.4.0** - Interactive Dashboard (Q3 2025)
- **Objectif** : Interface web temps réel
- **Features** : FastAPI + React, sélection formats/dates, export PDF
- **Décision clé** : API-first design pour découplage frontend/backend
- **KPI** : Réduction temps analyse de 15min → 30s

### 🎯 **v1.0.0** - SaaS Ready (Q4 2025)
- **Vision** : Plateforme multi-utilisateurs
- **Features** : Auth, cache Redis, alertes métagame, API publique
- **Business** : Freemium model, analyses premium
- **Scalabilité** : Support 1000+ utilisateurs simultanés

## 🧭 Décisions d'Architecture Marquantes

### **Why Scraping Multi-Sources**
- **Problème** : Aucune API officielle Wizards
- **Solution** : Agrégation MTGO + Melee + TopDeck
- **Bénéfice** : Données complètes, résilience aux pannes

### **Why Real Data Only**
- **Problème** : Analyses peu fiables avec données fictives
- **Solution** : Politique "No Mock Data" stricte avec hooks Git
- **Bénéfice** : Confiance utilisateurs, insights marketing réels

### **Why Modular `src/` Structure**
- **Problème** : Monolithe difficile à maintenir
- **Solution** : Separation classifier/scraper/visualizer
- **Bénéfice** : Extensibilité (nouveau format = 1 nouveau module)

### **Why HTML/Plotly vs Dashboard**
- **Phase 1** : Fichiers statiques → déploiement simple
- **Phase 2** : Dashboard → interaction temps réel
- **Migration** : Code visualisation réutilisable

## 🎪 Use Cases Futurs

- **Joueurs Compétitifs** : Préparation tournois, meta tracking
- **Organisateurs** : Analytics événements, formats émergents  
- **Créateurs Contenu** : Données visuelles, articles stratégie
- **Wizards R&D** : Monitoring santé formats (partenariat potentiel)

---
*Dernière mise à jour : 13 juillet 2025* 