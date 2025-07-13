#!/bin/bash
# Script de démarrage Manalytics
# Créé le 12 juillet 2025 - Testé et validé

set -e  # Arrêter en cas d'erreur

# Configuration
PROJECT_DIR="/Volumes/DataDisk/_Projects/Manalytics"
VENV_DIR="$PROJECT_DIR/venv"
API_DIR="$PROJECT_DIR/src/python/api"
LOG_DIR="$PROJECT_DIR/logs"
PORT=8000

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
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

# Vérifier les prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier le répertoire du projet
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Répertoire du projet non trouvé: $PROJECT_DIR"
        exit 1
    fi
    
    # Vérifier l'environnement virtuel
    if [ ! -d "$VENV_DIR" ]; then
        error "Environnement virtuel non trouvé: $VENV_DIR"
        exit 1
    fi
    
    # Vérifier les fichiers critiques
    if [ ! -f "$PROJECT_DIR/advanced_metagame_analyzer.py" ]; then
        error "Fichier critique manquant: advanced_metagame_analyzer.py"
        exit 1
    fi
    
    if [ ! -f "$API_DIR/fastapi_app_simple.py" ]; then
        error "Fichier critique manquant: fastapi_app_simple.py"
        exit 1
    fi
    
    success "Prérequis vérifiés"
}

# Nettoyer les processus existants
cleanup_processes() {
    log "Nettoyage des processus existants..."
    
    # Arrêter les processus FastAPI existants
    pkill -f "python.*fastapi_app_simple" 2>/dev/null || true
    
    # Attendre que les processus se terminent
    sleep 2
    
    # Vérifier que le port est libre
    if lsof -i :$PORT &> /dev/null; then
        warning "Port $PORT encore utilisé, tentative de libération..."
        lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    success "Processus nettoyés"
}

# Préparer l'environnement
setup_environment() {
    log "Préparation de l'environnement..."
    
    # Naviguer vers le répertoire du projet
    cd "$PROJECT_DIR"
    
    # Activer l'environnement virtuel
    source "$VENV_DIR/bin/activate"
    
    # Créer le répertoire de logs
    mkdir -p "$LOG_DIR"
    
    # Créer le répertoire de sortie
    mkdir -p "$PROJECT_DIR/analysis_output"
    
    success "Environnement préparé"
}

# Installer les dépendances
install_dependencies() {
    log "Installation des dépendances..."
    
    # Installer python-multipart (critique)
    pip install python-multipart &> /dev/null
    
    # Installer les autres dépendances si requirements.txt existe
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt" &> /dev/null
    fi
    
    success "Dépendances installées"
}

# Démarrer le serveur
start_server() {
    log "Démarrage du serveur Manalytics..."
    
    # Naviguer vers le répertoire API
    cd "$API_DIR"
    
    # Démarrer le serveur en arrière-plan
    nohup python fastapi_app_simple.py > "$LOG_DIR/server.log" 2>&1 &
    SERVER_PID=$!
    
    # Sauvegarder le PID
    echo $SERVER_PID > "$PROJECT_DIR/server.pid"
    
    log "Serveur démarré avec PID: $SERVER_PID"
    
    # Attendre que le serveur démarre
    log "Attente du démarrage du serveur..."
    for i in {1..30}; do
        if curl -s http://localhost:$PORT/health &> /dev/null; then
            success "Serveur démarré avec succès!"
            return 0
        fi
        sleep 1
    done
    
    error "Échec du démarrage du serveur"
    return 1
}

# Tester le serveur
test_server() {
    log "Test du serveur..."
    
    # Test de santé
    health_response=$(curl -s http://localhost:$PORT/health)
    if [[ $health_response == *"healthy"* ]]; then
        success "✅ Test de santé réussi"
    else
        error "❌ Test de santé échoué"
        return 1
    fi
    
    # Test de l'interface web
    web_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/web)
    if [[ $web_code == "200" ]]; then
        success "✅ Interface web accessible"
    else
        error "❌ Interface web non accessible (code: $web_code)"
        return 1
    fi
    
    success "Tous les tests sont réussis"
}

# Afficher les informations de connexion
show_connection_info() {
    log "Informations de connexion:"
    echo ""
    echo "🌐 Interface web:     http://localhost:$PORT/web"
    echo "🏥 Health check:     http://localhost:$PORT/health"
    echo "📚 Documentation:    http://localhost:$PORT/docs"
    echo "📊 Générateur:       POST http://localhost:$PORT/generate-analysis"
    echo ""
    echo "📁 Répertoire projet: $PROJECT_DIR"
    echo "📝 Logs serveur:      $LOG_DIR/server.log"
    echo "🔢 PID serveur:       $(cat $PROJECT_DIR/server.pid 2>/dev/null || echo 'Non disponible')"
    echo ""
    success "Manalytics est prêt à l'utilisation!"
}

# Fonction principale
main() {
    log "🚀 Démarrage de Manalytics..."
    
    check_prerequisites
    cleanup_processes
    setup_environment
    install_dependencies
    
    if start_server; then
        if test_server; then
            show_connection_info
        else
            error "Les tests ont échoué"
            exit 1
        fi
    else
        error "Échec du démarrage"
        exit 1
    fi
}

# Gestion des signaux
trap 'error "Interruption détectée"; exit 1' INT TERM

# Exécuter le script principal
main "$@" 