#!/bin/bash
# Script de rollback d'urgence
# Usage: ./scripts/emergency_rollback.sh [commit-hash|tag]

set -e

# Fonction d'aide
show_help() {
    echo "🚨 Script de rollback d'urgence"
    echo "Usage: $0 [commit-hash|tag]"
    echo ""
    echo "Exemples:"
    echo "  $0                    # Rollback interactif"
    echo "  $0 abc123             # Rollback vers un commit spécifique"
    echo "  $0 backup-test-20250114-1400  # Rollback vers un tag"
    echo ""
}

# Vérifier qu'on est dans le bon répertoire
if [[ ! -f "docs/MODIFICATION_TRACKER.md" ]]; then
    echo "❌ Veuillez exécuter ce script depuis la racine du projet Manalytics"
    exit 1
fi

# Vérifier qu'on est sur main
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo "❌ Vous devez être sur la branche main"
    echo "🔧 Exécutez: git checkout main"
    exit 1
fi

# Fonction pour afficher l'historique récent
show_recent_history() {
    echo "📋 Historique récent des commits:"
    git log --oneline -10
    echo ""
    echo "📋 Tags de backup disponibles:"
    git tag -l "backup-*" | tail -10
}

# Fonction pour rollback interactif
interactive_rollback() {
    echo "🚨 ROLLBACK D'URGENCE - Mode interactif"
    echo "=" * 50
    
    show_recent_history
    
    echo ""
    echo "🔍 Que voulez-vous faire?"
    echo "1. Rollback vers le dernier tag de backup"
    echo "2. Rollback vers un commit spécifique"
    echo "3. Rollback vers un tag spécifique"
    echo "4. Annuler (quitter)"
    
    read -p "Votre choix (1-4): " choice
    
    case $choice in
        1)
            latest_backup=$(git tag -l "backup-*" | tail -1)
            if [[ -z "$latest_backup" ]]; then
                echo "❌ Aucun tag de backup trouvé"
                exit 1
            fi
            rollback_target="$latest_backup"
            ;;
        2)
            show_recent_history
            read -p "Entrez le hash du commit: " commit_hash
            if [[ -z "$commit_hash" ]]; then
                echo "❌ Hash de commit requis"
                exit 1
            fi
            rollback_target="$commit_hash"
            ;;
        3)
            echo "Tags de backup disponibles:"
            git tag -l "backup-*"
            read -p "Entrez le nom du tag: " tag_name
            if [[ -z "$tag_name" ]]; then
                echo "❌ Nom du tag requis"
                exit 1
            fi
            rollback_target="$tag_name"
            ;;
        4)
            echo "🔄 Opération annulée"
            exit 0
            ;;
        *)
            echo "❌ Choix invalide"
            exit 1
            ;;
    esac
}

# Fonction pour effectuer le rollback
perform_rollback() {
    local target=$1
    
    echo "🚨 ATTENTION: Rollback vers $target"
    echo "⚠️  Ceci va annuler TOUS les changements depuis ce point"
    echo "⚠️  Assurez-vous que c'est ce que vous voulez faire"
    
    read -p "Êtes-vous sûr? (tapez 'ROLLBACK' pour confirmer): " confirmation
    
    if [[ "$confirmation" != "ROLLBACK" ]]; then
        echo "🔄 Rollback annulé"
        exit 0
    fi
    
    # Créer un tag de backup avant le rollback
    emergency_tag="emergency-backup-$(date +%Y%m%d-%H%M)"
    echo "💾 Création d'un tag de backup d'urgence: $emergency_tag"
    git tag -a "$emergency_tag" -m "Backup d'urgence avant rollback vers $target"
    git push origin "$emergency_tag"
    
    # Effectuer le rollback
    echo "🔄 Rollback vers $target..."
    git reset --hard "$target"
    
    # Forcer le push (dangereux mais nécessaire en urgence)
    echo "📤 Envoi du rollback vers origin..."
    git push --force-with-lease origin main
    
    echo "✅ Rollback terminé!"
    echo "📝 Rollback vers: $target"
    echo "💾 Backup d'urgence créé: $emergency_tag"
    
    # Ajouter entrée dans MODIFICATION_TRACKER.md
    echo "📋 Ajout d'une entrée dans MODIFICATION_TRACKER.md..."
    add_tracker_entry "$target" "$emergency_tag"
}

# Fonction pour ajouter une entrée dans le tracker
add_tracker_entry() {
    local target=$1
    local backup_tag=$2
    
    entry="
### [$(date +"%Y-%m-%d %H:%M")] - System_Emergency_Rollback
**Fichier(s) concerné(s)** : \`TOUS\`
**Type** : ROLLBACK
**Description** : Rollback d'urgence vers $target
**Justification** : Problème critique nécessitant un rollback immédiat
**Tests** : Vérifier que le système fonctionne après rollback
**Rollback** : Restaurer depuis le tag de backup $backup_tag
"
    
    # Ajouter l'entrée au début de l'historique
    if [[ -f "docs/MODIFICATION_TRACKER.md" ]]; then
        temp_file=$(mktemp)
        awk '
            /^## 🔄 \*\*HISTORIQUE DES MODIFICATIONS\*\*$/ {
                print $0
                print "'"$entry"'"
                next
            }
            { print }
        ' docs/MODIFICATION_TRACKER.md > "$temp_file"
        mv "$temp_file" docs/MODIFICATION_TRACKER.md
        
        # Commiter la modification du tracker
        git add docs/MODIFICATION_TRACKER.md
        git commit -m "track: emergency rollback to $target"
        git push origin main
    fi
}

# Main
main() {
    # Vérifier les arguments
    if [[ $# -eq 0 ]]; then
        interactive_rollback
    else
        rollback_target=$1
        if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
            show_help
            exit 0
        fi
    fi
    
    # Vérifier que la cible existe
    if ! git rev-parse --verify "$rollback_target" >/dev/null 2>&1; then
        echo "❌ Cible de rollback invalide: $rollback_target"
        exit 1
    fi
    
    # Effectuer le rollback
    perform_rollback "$rollback_target"
    
    echo ""
    echo "🎉 Rollback d'urgence terminé!"
    echo "🔍 Vérifiez que tout fonctionne correctement"
    echo "📋 Consultez MODIFICATION_TRACKER.md pour l'historique"
}

# Lancer le script
main "$@" 