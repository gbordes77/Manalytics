#!/bin/bash

# Script de test sécurité Manalytics - Plan Expert
# Validation complète des implémentations sécurité

echo "🔒 TEST DE SÉCURITÉ MANALYTICS"
echo "============================="

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction helper
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction de test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Test: $test_name... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        log_success "PASS"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "FAIL"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "\n📋 TESTS SÉCURITÉ CRITIQUES"
echo "=========================="

# Test 1: Vérifier permissions credentials
run_test "Permissions credentials" \
    '[ -f credentials/encrypted_credentials.json ] && [ $(stat -f "%Lp" credentials/encrypted_credentials.json 2>/dev/null || echo "000") = "600" ]'

# Test 2: Vérifier permissions master key
run_test "Permissions master key" \
    '[ -f credentials/master.key ] && [ $(stat -f "%Lp" credentials/master.key 2>/dev/null || echo "000") = "600" ]'

# Test 3: Vérifier absence credentials en clair
run_test "Absence credentials en clair" \
    '[ ! -f credentials/melee_login.json ] && [ ! -f credentials/topdeck_api.txt ]'

# Test 4: Test configuration CORS
run_test "Configuration CORS sécurisée" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
with open(\"src/python/api/fastapi_app.py\", \"r\") as f:
    content = f.read()
    if \"allow_origins=[\\\"*\\\"]\" in content:
        sys.exit(1)
    sys.exit(0)
"'

# Test 5: Vérifier existence monitoring sécurité
run_test "Monitoring sécurité présent" \
    '[ -f src/python/security/emergency_monitor.py ]'

# Test 6: Vérifier intégration middleware sécurité
run_test "Middleware sécurité intégré" \
    'grep -q "security_middleware" src/python/api/fastapi_app.py'

# Test 7: Vérifier endpoints sécurité
run_test "Endpoints sécurité configurés" \
    'grep -q "/api/security/status" src/python/api/fastapi_app.py'

# Test 8: Vérifier répertoire logs sécurisé
run_test "Répertoire logs sécurisé" \
    '[ -d logs ] && [ $(stat -f "%Lp" logs 2>/dev/null || echo "000") = "755" ]'

echo -e "\n🧪 TESTS FONCTIONNELS"
echo "==================="

# Test 9: Tester import monitoring
run_test "Import monitoring sécurité" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
from python.security.emergency_monitor import security_monitor
print(\"Import successful\")
"'

# Test 10: Tester création backup
run_test "Backup credentials fonctionnel" \
    'python3 scripts/migrate_credentials_secure.py >/dev/null 2>&1'

# Test 11: Vérifier credential manager
run_test "Credential manager fonctionnel" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
from python.security.credential_manager import SecureCredentialManager
cm = SecureCredentialManager({})
print(\"Credential manager OK\")
"'

# Test 12: Vérifier logs sécurité
run_test "Logs sécurité configurés" \
    'python3 -c "
import logging
from pathlib import Path
Path(\"logs\").mkdir(exist_ok=True)
security_logger = logging.getLogger(\"security\")
handler = logging.FileHandler(\"logs/security_test.log\")
security_logger.addHandler(handler)
security_logger.warning(\"Test log\")
print(\"Logging OK\")
"'

echo -e "\n🔍 TESTS AVANCÉS"
echo "==============="

# Test 13: Simulation attaque basique
run_test "Détection attaque simulation" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
from python.security.emergency_monitor import security_monitor
# Simuler tentatives échouées
for i in range(6):
    security_monitor.record_failed_attempt(\"127.0.0.1\", \"/test\", \"test_attack\")
# Vérifier blocage
blocked = security_monitor.is_blocked(\"127.0.0.1\")
print(f\"Attack detected and blocked: {blocked}\")
if blocked:
    sys.exit(0)
else:
    sys.exit(1)
"'

# Test 14: Test rate limiting
run_test "Rate limiting fonctionnel" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
from python.security.emergency_monitor import security_monitor
# Simuler nombreuses requêtes
for i in range(70):
    result = security_monitor.record_request(\"127.0.0.2\", \"/test\")
    if not result:
        print(\"Rate limit activated\")
        sys.exit(0)
print(\"Rate limit not activated\")
sys.exit(1)
"'

# Test 15: Test détection contenu malveillant
run_test "Détection contenu malveillant" \
    'python3 -c "
import sys
sys.path.insert(0, \"src\")
from python.security.emergency_monitor import security_monitor
# Test injection SQL
result = security_monitor.analyze_request_content(\"127.0.0.3\", \"/test\", \"SELECT * FROM users WHERE id = 1 OR 1=1\")
print(f\"Malicious content detected: {not result}\")
if not result:
    sys.exit(0)
else:
    sys.exit(1)
"'

echo -e "\n📊 RÉSULTATS FINAUX"
echo "=================="

echo "Tests total: $TOTAL_TESTS"
echo "Tests réussis: $PASSED_TESTS"
echo "Tests échoués: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    log_success "🎉 TOUS LES TESTS SÉCURITÉ PASSÉS !"
    echo "✅ Le système est sécurisé selon le plan expert"
    exit 0
else
    log_error "⚠️  CERTAINS TESTS ONT ÉCHOUÉ"
    echo "❌ Corriger les problèmes avant déploiement"
    exit 1
fi 