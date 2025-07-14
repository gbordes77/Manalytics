#!/bin/bash
# Script pour créer automatiquement des tags de backup
# Usage: ./scripts/create_backup_tag.sh [description]

set -e

# Fonction d'aide
show_help() {
    echo "🔧 Script de création de tags de backup"
    echo "Usage: $0 [description]"
    echo ""
    echo "Exemples:"
    echo "  $0 'avant-refactoring-orchestrator'"
    echo "  $0 'avant-modification-visualisations'"
    echo "  $0  # Sans description (backup automatique)"
    echo ""
}

# Vérifier qu'on est dans le bon répertoire
if [[ ! -f "docs/MODIFICATION_TRACKER.md" ]]; then
    echo "❌ Veuillez exécuter ce script depuis la racine du projet Manalytics"
    exit 1
fi

# Vérifier qu'on est sur main et à jour
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo "❌ Vous devez être sur la branche main"
    echo "🔧 Exécutez: git checkout main"
    exit 1
fi

# Vérifier qu'il n'y a pas de modifications non commitées
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "❌ Vous avez des modifications non commitées"
    echo "🔧 Commitez vos changements avant de créer un backup"
    exit 1
fi

# Récupérer les derniers changements
echo "🔄 Récupération des derniers changements..."
git fetch origin main

# Vérifier qu'on est à jour
if ! git diff --quiet HEAD origin/main; then
    echo "⚠️  Votre branche main n'est pas à jour"
    echo "🔧 Exécutez: git pull origin main"
    exit 1
fi

# Créer le nom du tag
timestamp=$(date +"%Y%m%d-%H%M")
description=${1:-"auto-backup"}

# Nettoyer la description (remplacer espaces par des tirets)
clean_description=$(echo "$description" | sed 's/ /-/g' | sed 's/[^a-zA-Z0-9-]//g')

tag_name="backup-${clean_description}-${timestamp}"

# Créer le tag
echo "🏷️  Création du tag de backup: $tag_name"
git tag -a "$tag_name" -m "Backup créé le $(date): $description"

# Pousser le tag vers origin
echo "📤 Envoi du tag vers origin..."
git push origin "$tag_name"

echo "✅ Tag de backup créé avec succès!"
echo "📝 Nom du tag: $tag_name"
echo "📅 Date: $(date)"
echo "💾 Description: $description"

# Montrer les derniers tags
echo ""
echo "📋 Derniers tags de backup:"
git tag -l "backup-*" | tail -5

# Instructions de rollback
echo ""
echo "🔄 Pour restaurer ce backup plus tard:"
echo "   git checkout $tag_name"
echo "   git checkout -b restore-from-backup"
echo "   # Ou pour un rollback complet:"
echo "   git reset --hard $tag_name"

echo ""
echo "🎉 Backup terminé! Vous pouvez maintenant faire vos modifications en sécurité." 