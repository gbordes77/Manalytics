"""
Configuration pytest pour forcer données réelles dans les tests
AUCUNE donnée mockée autorisée
"""

import pytest
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.no_mock_policy import (
    NoMockDataError, 
    RealDataEnforcer, 
    Settings, 
    get_real_tournament_data,
    enforce_real_data_only
)

# Activer le mode strict dès le début
enforce_real_data_only()

@pytest.fixture(scope='session', autouse=True)
def enforce_no_mock_data():
    """Fixture automatique qui interdit tout mock"""
    
    # Désactiver unittest.mock
    try:
        import unittest.mock
        unittest.mock.Mock = None
        unittest.mock.MagicMock = None
        unittest.mock.patch = None
        unittest.mock.mock_open = None
    except ImportError:
        pass
    
    # Désactiver pytest-mock
    try:
        import pytest_mock
        pytest_mock.MockFixture = None
        pytest_mock.mocker = None
    except ImportError:
        pass
    
    # Désactiver responses
    try:
        import responses
        responses.mock = None
        responses.RequestsMock = None
    except ImportError:
        pass
    
    print("✅ Mode strict activé - Aucun mock autorisé")
    yield
    
    # Pas de restauration - on garde le mode strict

@pytest.fixture(scope='session')
def real_tournament_data() -> List[Dict]:
    """Fournit de VRAIES données de tournoi pour les tests"""
    try:
        tournaments = get_real_tournament_data()
        print(f"✅ {len(tournaments)} tournois réels chargés pour les tests")
        return tournaments
    except Exception as e:
        pytest.skip(f"❌ Impossible de charger les données réelles: {e}")

@pytest.fixture
def real_tournament(real_tournament_data) -> Dict:
    """Fournit un seul tournoi réel pour les tests"""
    if not real_tournament_data:
        pytest.skip("❌ Aucun tournoi réel disponible")
    return real_tournament_data[0]

@pytest.fixture
def real_deck(real_tournament) -> Dict:
    """Fournit un deck réel pour les tests"""
    decks = real_tournament.get('decks', [])
    if not decks:
        pytest.skip("❌ Aucun deck réel disponible")
    return decks[0]

@pytest.fixture
def real_decklist(real_deck) -> List[Dict]:
    """Fournit une decklist réelle pour les tests"""
    mainboard = real_deck.get('mainboard', [])
    if not mainboard:
        pytest.skip("❌ Aucune decklist réelle disponible")
    return mainboard

@pytest.fixture
def multiple_real_tournaments(real_tournament_data) -> List[Dict]:
    """Fournit plusieurs tournois réels pour les tests"""
    if len(real_tournament_data) < 3:
        pytest.skip("❌ Pas assez de tournois réels (minimum 3)")
    return real_tournament_data[:10]  # Limiter à 10 pour les performances

@pytest.fixture
def real_mtgo_tournament(real_tournament_data) -> Dict:
    """Fournit un tournoi MTGO réel"""
    mtgo_tournaments = [
        t for t in real_tournament_data 
        if 'mtgo' in str(t.get('source', '')).lower()
    ]
    if not mtgo_tournaments:
        pytest.skip("❌ Aucun tournoi MTGO réel disponible")
    return mtgo_tournaments[0]

@pytest.fixture
def real_melee_tournament(real_tournament_data) -> Dict:
    """Fournit un tournoi Melee réel"""
    melee_tournaments = [
        t for t in real_tournament_data 
        if 'melee' in str(t.get('source', '')).lower()
    ]
    if not melee_tournaments:
        pytest.skip("❌ Aucun tournoi Melee réel disponible")
    return melee_tournaments[0]

@pytest.fixture
def real_standard_data(real_tournament_data) -> List[Dict]:
    """Fournit des données Standard réelles"""
    standard_tournaments = [
        t for t in real_tournament_data 
        if str(t.get('format', '')).lower() == 'standard'
    ]
    if not standard_tournaments:
        pytest.skip("❌ Aucun tournoi Standard réel disponible")
    return standard_tournaments

@pytest.fixture
def real_modern_data(real_tournament_data) -> List[Dict]:
    """Fournit des données Modern réelles"""
    modern_tournaments = [
        t for t in real_tournament_data 
        if str(t.get('format', '')).lower() == 'modern'
    ]
    if not modern_tournaments:
        pytest.skip("❌ Aucun tournoi Modern réel disponible")
    return modern_tournaments

@pytest.fixture
def validate_real_data():
    """Fixture pour valider que les données sont réelles"""
    def _validate(data):
        try:
            RealDataEnforcer.validate_no_mock_data(data)
            return True
        except NoMockDataError as e:
            pytest.fail(f"❌ Données mockées détectées: {e}")
    
    return _validate

# Hook pytest pour valider chaque test
def pytest_runtest_setup(item):
    """Valide avant chaque test qu'aucun mock n'est utilisé"""
    
    # Vérifier les marqueurs de test
    if hasattr(item, 'pytestmark'):
        for mark in item.pytestmark:
            if mark.name in ['mock', 'patch', 'monkeypatch']:
                pytest.fail(
                    f"❌ Test {item.name} utilise des mocks interdits\n"
                    f"📋 Règle: Utiliser uniquement des données réelles\n"
                    f"🔧 Utiliser les fixtures real_tournament_data, real_deck, etc."
                )

def pytest_runtest_call(pyfuncitem):
    """Valide pendant l'exécution du test"""
    
    # Vérifier que les modules de mock ne sont pas importés
    forbidden_modules = [
        'unittest.mock',
        'mock', 
        'pytest_mock',
        'responses',
        'httpretty'
    ]
    
    for module_name in forbidden_modules:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'Mock') and module.Mock is not None:
                pytest.fail(
                    f"❌ Module de mock détecté: {module_name}\n"
                    f"📋 Règle: Aucun mock autorisé\n"
                    f"🔧 Utiliser des données réelles uniquement"
                )

# Configuration pytest globale
def pytest_configure(config):
    """Configuration globale pytest"""
    
    # Marquer les tests qui utilisent des mocks comme xfail
    config.addinivalue_line(
        "markers", 
        "mock: mark test as using mocks (will fail)"
    )
    
    # Vérifier que les données réelles sont disponibles
    try:
        Settings.validate_environment()
        print("✅ Environnement validé pour les données réelles")
    except RuntimeError as e:
        print(f"❌ {e}")
        pytest.exit("Configuration invalide - Données réelles requises")

# Rapport de fin
def pytest_sessionfinish(session, exitstatus):
    """Rapport final de la session de tests"""
    
    if exitstatus == 0:
        print("\n✅ TOUS LES TESTS VALIDÉS AVEC DONNÉES RÉELLES")
        print("📊 Aucune donnée mockée utilisée")
    else:
        print("\n❌ Certains tests ont échoué")
        print("📋 Vérifier que seules des données réelles sont utilisées")

# Exemple d'utilisation dans les tests :
"""
def test_tournament_classification(real_tournament, validate_real_data):
    # Valider que les données sont réelles
    validate_real_data(real_tournament)
    
    # Utiliser le tournoi réel
    assert real_tournament['decks']
    assert len(real_tournament['decks']) >= 8
    
    # Pas de mock - utiliser les vraies données
    for deck in real_tournament['decks']:
        assert deck['mainboard']
        assert len(deck['mainboard']) >= 60

def test_archetype_detection(real_deck, validate_real_data):
    # Valider que le deck est réel
    validate_real_data(real_deck)
    
    # Tester avec de vraies données
    classifier = ArchetypeClassifier()
    archetype = classifier.classify(real_deck)
    
    # Vérifier que l'archétype n'est pas mocké
    validate_real_data(archetype)
    assert archetype != "TestArchetype"
""" 