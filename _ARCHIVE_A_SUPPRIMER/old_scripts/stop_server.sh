#!/bin/bash
# Script d'arrêt Manalytics
# Créé le 12 juillet 2025

set -e

# Configuration
PROJECT_DIR="/Volumes/DataDisk/_Projects/Manalytics"
PID_FILE="$PROJECT_DIR/server.pid"
PORT=8000

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Arrêter le serveur par PID
stop_by_pid() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "Arrêt du serveur (PID: $PID)..."
            kill "$PID"
            
            # Attendre l'arrêt gracieux
            for i in {1..10}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    success "Serveur arrêté proprement"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Forcer l'arrêt si nécessaire
            warning "Arrêt forcé du serveur..."
            kill -9 "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
            success "Serveur arrêté de force"
        else
            warning "PID $PID non trouvé, nettoyage du fichier PID"
            rm -f "$PID_FILE"
        fi
    else
        warning "Fichier PID non trouvé"
    fi
}

# Arrêter tous les processus FastAPI
stop_all_processes() {
    log "Arrêt de tous les processus FastAPI..."
    
    # Arrêter par nom de processus
    pkill -f "python.*fastapi_app_simple" 2>/dev/null || true
    
    # Attendre un peu
    sleep 2
    
    # Vérifier s'il reste des processus
    if pgrep -f "python.*fastapi_app_simple" &>/dev/null; then
        warning "Arrêt forcé des processus restants..."
        pkill -9 -f "python.*fastapi_app_simple" 2>/dev/null || true
    fi
    
    success "Processus FastAPI arrêtés"
}

# Libérer le port
free_port() {
    if lsof -i :$PORT &>/dev/null; then
        log "Libération du port $PORT..."
        lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
        sleep 1
        
        if lsof -i :$PORT &>/dev/null; then
            error "Impossible de libérer le port $PORT"
            return 1
        else
            success "Port $PORT libéré"
        fi
    else
        log "Port $PORT déjà libre"
    fi
}

# Nettoyer les fichiers temporaires
cleanup_temp_files() {
    log "Nettoyage des fichiers temporaires..."
    
    # Nettoyer les caches Python
    find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
    
    # Nettoyer les logs anciens (optionnel)
    if [ -d "$PROJECT_DIR/logs" ]; then
        find "$PROJECT_DIR/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    success "Fichiers temporaires nettoyés"
}

# Afficher le statut final
show_status() {
    log "Vérification du statut final..."
    
    # Vérifier les processus
    if pgrep -f "python.*fastapi_app_simple" &>/dev/null; then
        error "❌ Des processus FastAPI sont encore actifs"
        pgrep -f "python.*fastapi_app_simple"
        return 1
    else
        success "✅ Aucun processus FastAPI actif"
    fi
    
    # Vérifier le port
    if lsof -i :$PORT &>/dev/null; then
        error "❌ Port $PORT encore utilisé"
        lsof -i :$PORT
        return 1
    else
        success "✅ Port $PORT libre"
    fi
    
    # Vérifier le fichier PID
    if [ -f "$PID_FILE" ]; then
        error "❌ Fichier PID encore présent"
        return 1
    else
        success "✅ Fichier PID supprimé"
    fi
    
    success "🎉 Manalytics arrêté complètement"
}

# Fonction principale
main() {
    log "🛑 Arrêt de Manalytics..."
    
    stop_by_pid
    stop_all_processes
    free_port
    cleanup_temp_files
    show_status
    
    echo ""
    log "Manalytics est maintenant arrêté"
    log "Pour redémarrer, utilisez: ./start_server.sh"
}

# Gestion des signaux
trap 'error "Interruption détectée"; exit 1' INT TERM

# Exécuter le script principal
main "$@" 