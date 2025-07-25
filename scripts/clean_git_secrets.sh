#!/bin/bash
# 🔒 Script de nettoyage des secrets de l'historique Git
# ⚠️  ATTENTION: Ce script modifie l'historique Git!

echo "🔒 Nettoyage des secrets de l'historique Git"
echo "==========================================="
echo ""
echo "⚠️  AVERTISSEMENT: Ce script va:"
echo "  - Modifier l'historique Git"
echo "  - Nécessiter un force push"
echo "  - Affecter tous les clones du repo"
echo ""
read -p "Êtes-vous sûr de vouloir continuer? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 1
fi

# Créer un backup avant modification
echo "📦 Création d'un backup..."
git bundle create ../manalytics-backup-$(date +%Y%m%d-%H%M%S).bundle --all

# Liste des fichiers à supprimer de l'historique
FILES_TO_REMOVE=(
    "api_credentials/melee_login.json"
    "api_credentials/melee_cookies.json"
    "Api_token_and_login/melee_login.json"
    "melee_login.json"
    "melee_cookies.json"
    "**/*_login.json"
    "**/*_cookies.json"
)

echo ""
echo "🧹 Suppression des fichiers sensibles..."

# Utiliser git filter-branch (plus compatible que BFG)
for file in "${FILES_TO_REMOVE[@]}"; do
    echo "  - Suppression de: $file"
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch $file" \
        --prune-empty --tag-name-filter cat -- --all 2>/dev/null
done

echo ""
echo "🗑️  Nettoyage des refs..."

# Nettoyer les références
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Nettoyage terminé!"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Vérifier que tout fonctionne: git log --oneline"
echo "  2. Force push: git push --force --all"
echo "  3. Force push tags: git push --force --tags"
echo ""
echo "⚠️  IMPORTANT:"
echo "  - Tous les collaborateurs devront re-cloner le repo"
echo "  - Les anciennes références peuvent persister dans les forks"
echo "  - Révoquez tous les secrets exposés immédiatement"