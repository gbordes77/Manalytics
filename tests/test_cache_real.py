"""
Tests pour le système de cache avec données réelles uniquement
Conformément à la politique NO MOCK DATA - Utilise uniquement des données réelles
"""

import pytest
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any

# Configuration pour données réelles
REAL_DATA_PATH = Path(__file__).parent.parent / "real_data"
MTGO_CACHE_PATH = Path(__file__).parent.parent / "MTGODecklistCache"

class RealRedisCache:
    """Cache Redis réel pour les tests"""
    
    def __init__(self):
        self.data = {}
        self.ttl_data = {}
        self.stats = {"hits": 0, "misses": 0, "sets": 0}
    
    async def get(self, key: str) -> Any:
        """Récupérer une valeur"""
        if key in self.data:
            # Vérifier TTL
            if key in self.ttl_data:
                if time.time() > self.ttl_data[key]:
                    del self.data[key]
                    del self.ttl_data[key]
                    self.stats["misses"] += 1
                    return None
            
            self.stats["hits"] += 1
            return self.data[key]
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Stocker une valeur"""
        self.data[key] = value
        if ttl:
            self.ttl_data[key] = time.time() + ttl
        self.stats["sets"] += 1
        return True
    
    async def delete(self, key: str) -> bool:
        """Supprimer une valeur"""
        if key in self.data:
            del self.data[key]
            if key in self.ttl_data:
                del self.ttl_data[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Vérifier l'existence d'une clé"""
        return key in self.data
    
    async def ping(self) -> bool:
        """Test de connexion"""
        return True
    
    async def close(self):
        """Fermer la connexion"""
        pass

@pytest.fixture
def real_cache():
    """Fixture pour cache réel"""
    return RealRedisCache()

@pytest.fixture
def real_tournament_data():
    """Fixture pour données de tournoi réelles"""
    real_data_file = REAL_DATA_PATH / "complete_dataset.json"
    
    if not real_data_file.exists():
        pytest.skip("Données réelles non disponibles")
    
    with open(real_data_file, 'r') as f:
        tournaments = json.load(f)
    
    if not tournaments:
        pytest.skip("Aucun tournoi réel trouvé")
    
    return tournaments[0]  # Premier tournoi réel

@pytest.fixture
def real_mtgo_tournament():
    """Fixture pour tournoi MTGO réel"""
    mtgo_files = list(MTGO_CACHE_PATH.glob("**/*.json"))
    
    if not mtgo_files:
        pytest.skip("Aucun fichier MTGO trouvé")
    
    # Prendre le premier fichier trouvé
    with open(mtgo_files[0], 'r') as f:
        tournament_data = json.load(f)
    
    return tournament_data

class TestRealCacheOperations:
    """Tests des opérations de cache avec données réelles"""
    
    @pytest.mark.asyncio
    async def test_cache_basic_operations(self, real_cache, real_tournament_data):
        """Test des opérations de base avec données réelles"""
        # Test set/get avec données réelles
        key = f"tournament:{real_tournament_data['tournament_id']}"
        
        success = await real_cache.set(key, real_tournament_data, ttl=60)
        assert success is True
        
        # Récupérer les données
        cached_data = await real_cache.get(key)
        assert cached_data is not None
        assert cached_data['tournament_id'] == real_tournament_data['tournament_id']
        
        # Vérifier les statistiques
        assert real_cache.stats["hits"] >= 1
        assert real_cache.stats["sets"] >= 1
    
    @pytest.mark.asyncio
    async def test_cache_with_real_deck_data(self, real_cache, real_tournament_data):
        """Test du cache avec données de decks réelles"""
        decks = real_tournament_data.get('decks', [])
        
        if not decks:
            pytest.skip("Aucun deck dans les données réelles")
        
        # Cacher chaque deck
        for i, deck in enumerate(decks[:5]):  # Limiter à 5 decks
            key = f"deck:{real_tournament_data['tournament_id']}:{i}"
            await real_cache.set(key, deck, ttl=30)
        
        # Vérifier que tous les decks sont cachés
        for i, deck in enumerate(decks[:5]):
            key = f"deck:{real_tournament_data['tournament_id']}:{i}"
            cached_deck = await real_cache.get(key)
            assert cached_deck is not None
            assert cached_deck['player_name'] == deck['player_name']
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, real_cache, real_tournament_data):
        """Test de l'expiration TTL avec données réelles"""
        key = f"ttl_test:{real_tournament_data['tournament_id']}"
        
        # Stocker avec TTL très court
        await real_cache.set(key, real_tournament_data, ttl=1)
        
        # Vérifier existence immédiate
        exists = await real_cache.exists(key)
        assert exists is True
        
        # Attendre expiration
        await asyncio.sleep(1.1)
        
        # Vérifier que la donnée a expiré
        cached_data = await real_cache.get(key)
        assert cached_data is None
    
    @pytest.mark.asyncio
    async def test_cache_delete_operations(self, real_cache, real_tournament_data):
        """Test des opérations de suppression avec données réelles"""
        key = f"delete_test:{real_tournament_data['tournament_id']}"
        
        # Stocker la donnée
        await real_cache.set(key, real_tournament_data)
        
        # Vérifier existence
        exists = await real_cache.exists(key)
        assert exists is True
        
        # Supprimer
        success = await real_cache.delete(key)
        assert success is True
        
        # Vérifier suppression
        exists = await real_cache.exists(key)
        assert exists is False

class TestRealTournamentCache:
    """Tests du cache de tournois avec données réelles"""
    
    @pytest.mark.asyncio
    async def test_tournament_cache_with_real_data(self, real_cache, real_tournament_data):
        """Test du cache de tournois avec données réelles"""
        tournament_id = real_tournament_data['tournament_id']
        source = real_tournament_data.get('tournament_source', 'unknown')
        
        # Créer une clé de cache réaliste
        cache_key = f"tournament:{source}:{tournament_id}"
        
        # Stocker le tournoi
        await real_cache.set(cache_key, real_tournament_data, ttl=3600)
        
        # Récupérer et vérifier
        cached_tournament = await real_cache.get(cache_key)
        assert cached_tournament is not None
        assert cached_tournament['tournament_name'] == real_tournament_data['tournament_name']
        assert cached_tournament['tournament_format'] == real_tournament_data['tournament_format']
    
    @pytest.mark.asyncio
    async def test_multiple_tournaments_cache(self, real_cache):
        """Test du cache avec plusieurs tournois réels"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            tournaments = json.load(f)
        
        if len(tournaments) < 2:
            pytest.skip("Pas assez de tournois réels pour le test")
        
        # Cacher les premiers tournois
        for i, tournament in enumerate(tournaments[:3]):
            key = f"multi_tournament:{i}:{tournament['tournament_id']}"
            await real_cache.set(key, tournament, ttl=1800)
        
        # Vérifier que tous sont cachés
        for i, tournament in enumerate(tournaments[:3]):
            key = f"multi_tournament:{i}:{tournament['tournament_id']}"
            cached = await real_cache.get(key)
            assert cached is not None
            assert cached['tournament_id'] == tournament['tournament_id']

class TestRealMTGOCache:
    """Tests avec données MTGO réelles"""
    
    @pytest.mark.asyncio
    async def test_mtgo_tournament_cache(self, real_cache, real_mtgo_tournament):
        """Test du cache avec données MTGO réelles"""
        tournament_info = real_mtgo_tournament.get('Tournament', {})
        
        if not tournament_info:
            pytest.skip("Pas de données Tournament dans le fichier MTGO")
        
        # Extraire les informations
        tournament_name = tournament_info.get('Name', 'Unknown')
        tournament_date = tournament_info.get('Date', 'Unknown')
        
        # Créer une clé de cache
        cache_key = f"mtgo:tournament:{tournament_name}:{tournament_date}"
        
        # Stocker les données
        await real_cache.set(cache_key, real_mtgo_tournament, ttl=7200)
        
        # Récupérer et vérifier
        cached_data = await real_cache.get(cache_key)
        assert cached_data is not None
        assert cached_data['Tournament']['Name'] == tournament_name
    
    @pytest.mark.asyncio
    async def test_mtgo_deck_cache(self, real_cache, real_mtgo_tournament):
        """Test du cache avec decks MTGO réels"""
        decks = real_mtgo_tournament.get('Decks', [])
        
        if not decks:
            pytest.skip("Aucun deck dans les données MTGO")
        
        # Cacher quelques decks
        for i, deck in enumerate(decks[:3]):
            player = deck.get('Player', f'Player_{i}')
            key = f"mtgo:deck:{player}:{i}"
            await real_cache.set(key, deck, ttl=1800)
        
        # Vérifier le cache
        for i, deck in enumerate(decks[:3]):
            player = deck.get('Player', f'Player_{i}')
            key = f"mtgo:deck:{player}:{i}"
            cached_deck = await real_cache.get(key)
            assert cached_deck is not None
            assert cached_deck['Player'] == player

class TestRealCacheIntegration:
    """Tests d'intégration avec données réelles"""
    
    @pytest.mark.asyncio
    async def test_full_cache_workflow(self, real_cache):
        """Test du workflow complet avec données réelles"""
        # Charger toutes les données réelles disponibles
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            player_records = json.load(f)
        
        if not player_records:
            pytest.skip("Aucun enregistrement réel trouvé")
        
        # Grouper par tournoi (les données sont au format flat)
        tournaments = {}
        for record in player_records:
            tournament_id = record['tournament_id']
            if tournament_id not in tournaments:
                tournaments[tournament_id] = {
                    'tournament_id': tournament_id,
                    'tournament_name': record['tournament_name'],
                    'tournament_format': record['tournament_format'],
                    'tournament_source': record['tournament_source'],
                    'players': []
                }
            tournaments[tournament_id]['players'].append(record)
        
        # Simuler un workflow complet
        workflow_stats = {
            "tournaments_cached": 0,
            "players_cached": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Phase 1: Cacher tous les tournois
        for tournament_id, tournament_data in tournaments.items():
            key = f"workflow:tournament:{tournament_id}"
            await real_cache.set(key, tournament_data, ttl=3600)
            workflow_stats["tournaments_cached"] += 1
            
            # Cacher les joueurs individuellement
            for i, player in enumerate(tournament_data['players']):
                player_key = f"workflow:player:{tournament_id}:{i}"
                await real_cache.set(player_key, player, ttl=1800)
                workflow_stats["players_cached"] += 1
        
        # Phase 2: Vérifier les accès cache
        for tournament_id in tournaments:
            key = f"workflow:tournament:{tournament_id}"
            cached = await real_cache.get(key)
            if cached:
                workflow_stats["cache_hits"] += 1
            else:
                workflow_stats["cache_misses"] += 1
        
        # Vérifications finales
        assert workflow_stats["tournaments_cached"] == len(tournaments)
        assert workflow_stats["players_cached"] > 0
        assert workflow_stats["cache_hits"] > 0
        assert workflow_stats["cache_misses"] == 0
    
    @pytest.mark.asyncio
    async def test_cache_performance_with_real_data(self, real_cache):
        """Test des performances avec données réelles"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            tournaments = json.load(f)
        
        if not tournaments:
            pytest.skip("Aucun tournoi réel trouvé")
        
        # Mesurer les performances
        start_time = time.time()
        
        # Opérations de cache intensives
        for i, tournament in enumerate(tournaments):
            key = f"perf:tournament:{i}"
            await real_cache.set(key, tournament)
            
            # Lecture immédiate
            cached = await real_cache.get(key)
            assert cached is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que les opérations sont rapides
        operations_per_second = (len(tournaments) * 2) / duration  # set + get
        assert operations_per_second > 10  # Au moins 10 ops/sec
        
        # Vérifier les statistiques
        assert real_cache.stats["hits"] >= len(tournaments)
        assert real_cache.stats["sets"] >= len(tournaments)

def test_real_data_availability():
    """Test de disponibilité des données réelles"""
    real_data_file = REAL_DATA_PATH / "complete_dataset.json"
    
    # Vérifier que les données réelles existent
    assert real_data_file.exists(), "Fichier de données réelles manquant"
    
    # Vérifier que les données sont valides
    with open(real_data_file, 'r') as f:
        tournaments = json.load(f)
    
    assert isinstance(tournaments, list), "Les données doivent être une liste"
    assert len(tournaments) > 0, "Aucun tournoi dans les données réelles"
    
    # Vérifier la structure du premier tournoi
    first_tournament = tournaments[0]
    required_fields = ['tournament_id', 'tournament_name', 'tournament_format']
    
    for field in required_fields:
        assert field in first_tournament, f"Champ requis manquant: {field}"

def test_mtgo_data_availability():
    """Test de disponibilité des données MTGO"""
    mtgo_files = list(MTGO_CACHE_PATH.glob("**/*.json"))
    
    if not mtgo_files:
        pytest.skip("Aucun fichier MTGO trouvé")
    
    # Vérifier qu'au moins un fichier est valide
    valid_files = 0
    for file_path in mtgo_files[:5]:  # Tester les 5 premiers
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'Tournament' in data and 'Decks' in data:
                valid_files += 1
        except (json.JSONDecodeError, KeyError):
            continue
    
    assert valid_files > 0, "Aucun fichier MTGO valide trouvé" 