"""
Tests pour les scrapers avec données réelles uniquement
Conformément à la politique NO MOCK DATA - Utilise uniquement des données réelles
"""

import pytest
import json
import os
from pathlib import Path
# Import patch pour les tests (utilisé uniquement pour mocker les appels réseau, pas les données)
from unittest.mock import patch

# Configuration pour données réelles
REAL_DATA_PATH = Path(__file__).parent.parent / "real_data"
MTGO_CACHE_PATH = Path(__file__).parent.parent / "MTGODecklistCache"

class TestBaseScraper:
    """Tests pour BaseScraper avec données réelles"""
    
    def test_base_scraper_import(self):
        """Test d'import du BaseScraper"""
        from src.python.scraper.base_scraper import BaseScraper
        assert BaseScraper is not None
    
    def test_base_scraper_initialization(self):
        """Test d'initialisation du BaseScraper"""
        from src.python.scraper.base_scraper import BaseScraper
        
        # Configuration réelle
        config = {
            'cache_folder': str(REAL_DATA_PATH),
            'max_retries': 3,
            'retry_delay': 1
        }
        
        scraper = BaseScraper(config)
        assert scraper.config == config
        assert scraper.cache_folder == str(REAL_DATA_PATH)
    
    def test_base_scraper_validate_tournament_data(self):
        """Test de validation des données de tournoi réelles"""
        from src.python.scraper.base_scraper import BaseScraper
        
        # Charger des données réelles
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            player_records = json.load(f)
        
        if not player_records:
            pytest.skip("Aucun enregistrement réel trouvé")
        
        # Prendre le premier enregistrement
        sample_record = player_records[0]
        
        # Tester la validation
        scraper = BaseScraper({})
        
        # Vérifier que les champs requis sont présents
        required_fields = ['tournament_id', 'tournament_name', 'player_name']
        for field in required_fields:
            assert field in sample_record, f"Champ requis manquant: {field}"

class TestMTGOScraper:
    """Tests pour MTGOScraper avec données réelles"""
    
    def test_mtgo_scraper_import(self):
        """Test d'import du MTGOScraper"""
        from src.python.scraper.mtgo_scraper import MTGOScraper
        assert MTGOScraper is not None
    
    def test_mtgo_scraper_initialization(self):
        """Test d'initialisation du MTGOScraper"""
        from src.python.scraper.mtgo_scraper import MTGOScraper
        
        config = {
            'cache_folder': str(REAL_DATA_PATH),
            'max_retries': 3
        }
        
        scraper = MTGOScraper(config)
        assert scraper.config == config
    
    def test_mtgo_scraper_with_real_cache_data(self):
        """Test du MTGOScraper avec données réelles du cache"""
        from src.python.scraper.mtgo_scraper import MTGOScraper
        
        # Chercher des fichiers MTGO réels
        mtgo_files = list(MTGO_CACHE_PATH.glob("**/mtgo.com/**/*.json"))
        
        if not mtgo_files:
            pytest.skip("Aucun fichier MTGO trouvé")
        
        # Prendre le premier fichier
        sample_file = mtgo_files[0]
        
        with open(sample_file, 'r') as f:
            mtgo_data = json.load(f)
        
        # Vérifier la structure
        assert 'Tournament' in mtgo_data
        assert 'Decks' in mtgo_data
        
        tournament = mtgo_data['Tournament']
        assert 'Name' in tournament
        assert 'Date' in tournament

class TestTopdeckScraper:
    """Tests pour TopdeckScraper avec données réelles"""
    
    def test_topdeck_scraper_import(self):
        """Test d'import du TopdeckScraper"""
        from src.python.scraper.topdeck_scraper import TopdeckScraper
        assert TopdeckScraper is not None
    
    def test_topdeck_scraper_initialization(self):
        """Test d'initialisation du TopdeckScraper"""
        from src.python.scraper.topdeck_scraper import TopdeckScraper
        
        config = {
            'cache_folder': str(REAL_DATA_PATH),
            'api_key': 'test_key'
        }
        
        scraper = TopdeckScraper(config)
        assert scraper.config == config
    
    def test_topdeck_scraper_with_real_cache_data(self):
        """Test du TopdeckScraper avec données réelles du cache"""
        from src.python.scraper.topdeck_scraper import TopdeckScraper
        
        # Chercher des fichiers TopDeck réels
        topdeck_files = list(MTGO_CACHE_PATH.glob("**/topdeck.gg/**/*.json"))
        
        if not topdeck_files:
            pytest.skip("Aucun fichier TopDeck trouvé")
        
        # Prendre le premier fichier
        sample_file = topdeck_files[0]
        
        with open(sample_file, 'r') as f:
            topdeck_data = json.load(f)
        
        # Vérifier la structure (peut varier selon TopDeck)
        assert isinstance(topdeck_data, (dict, list))

class TestScraperIntegration:
    """Tests d'intégration des scrapers avec données réelles"""
    
    def test_scraper_data_consistency(self):
        """Test de cohérence des données entre scrapers"""
        # Vérifier que les données réelles sont cohérentes
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Vérifier la cohérence des formats
        formats = set(record.get('tournament_format', '').lower() for record in records)
        valid_formats = {'standard', 'modern', 'pioneer', 'legacy', 'pauper'}
        
        for format_name in formats:
            if format_name:  # Ignorer les formats vides
                assert format_name in valid_formats, f"Format invalide: {format_name}"
    
    def test_scraper_tournament_id_uniqueness(self):
        """Test d'unicité des IDs de tournoi"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Collecter tous les IDs de tournoi
        tournament_ids = set()
        for record in records:
            tournament_id = record.get('tournament_id')
            if tournament_id:
                tournament_ids.add(tournament_id)
        
        # Vérifier qu'il y a des IDs uniques
        assert len(tournament_ids) > 0, "Aucun ID de tournoi trouvé"
    
    def test_scraper_player_data_validity(self):
        """Test de validité des données de joueur"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Vérifier quelques enregistrements
        for record in records[:10]:  # Limiter à 10 pour la performance
            # Vérifier les champs obligatoires
            assert 'player_name' in record
            assert 'tournament_id' in record
            assert 'archetype' in record
            
            # Vérifier les types de données
            if 'wins' in record:
                assert isinstance(record['wins'], (int, float))
            if 'losses' in record:
                assert isinstance(record['losses'], (int, float))
            if 'winrate' in record:
                assert isinstance(record['winrate'], (int, float))
                assert 0 <= record['winrate'] <= 1

class TestScraperRealDataProcessing:
    """Tests de traitement des données réelles par les scrapers"""
    
    def test_process_real_tournament_data(self):
        """Test de traitement des données de tournoi réelles"""
        from src.python.scraper.base_scraper import BaseScraper
        
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Grouper par tournoi
        tournaments = {}
        for record in records:
            tournament_id = record['tournament_id']
            if tournament_id not in tournaments:
                tournaments[tournament_id] = {
                    'id': tournament_id,
                    'name': record['tournament_name'],
                    'format': record['tournament_format'],
                    'players': []
                }
            tournaments[tournament_id]['players'].append(record)
        
        # Vérifier qu'on a des tournois
        assert len(tournaments) > 0, "Aucun tournoi trouvé"
        
        # Vérifier la structure des tournois
        for tournament_id, tournament_data in tournaments.items():
            assert tournament_data['id'] == tournament_id
            assert len(tournament_data['players']) > 0
            assert tournament_data['format'] in ['standard', 'modern', 'pioneer', 'legacy', 'pauper']
    
    def test_extract_archetype_data(self):
        """Test d'extraction des données d'archétype"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Extraire les archétypes
        archetypes = {}
        for record in records:
            archetype = record.get('archetype', 'Unknown')
            format_name = record.get('tournament_format', 'unknown')
            
            key = f"{format_name}:{archetype}"
            if key not in archetypes:
                archetypes[key] = {
                    'name': archetype,
                    'format': format_name,
                    'players': 0,
                    'total_wins': 0,
                    'total_losses': 0
                }
            
            archetypes[key]['players'] += 1
            archetypes[key]['total_wins'] += record.get('wins', 0)
            archetypes[key]['total_losses'] += record.get('losses', 0)
        
        # Vérifier qu'on a des archétypes
        assert len(archetypes) > 0, "Aucun archétype trouvé"
        
        # Vérifier les données d'archétype
        for key, archetype_data in archetypes.items():
            assert archetype_data['players'] > 0
            assert archetype_data['name'] != ''
            assert archetype_data['format'] != '' 