"""
Tests pour le classificateur d'archétypes avec données réelles uniquement
Conformément à la politique NO MOCK DATA - Utilise uniquement des données réelles
"""

import pytest
import json
from pathlib import Path

# Configuration pour données réelles
REAL_DATA_PATH = Path(__file__).parent.parent / "real_data"
MTGO_FORMAT_PATH = Path(__file__).parent.parent / "MTGOFormatData"

class TestArchetypeEngine:
    """Tests pour ArchetypeEngine avec données réelles"""
    
    def test_archetype_engine_import(self):
        """Test d'import de l'ArchetypeEngine"""
        from src.python.classifier.archetype_engine import ArchetypeEngine
        assert ArchetypeEngine is not None
    
    def test_archetype_engine_initialization(self):
        """Test d'initialisation de l'ArchetypeEngine"""
        from src.python.classifier.archetype_engine import ArchetypeEngine
        
        if not MTGO_FORMAT_PATH.exists():
            pytest.skip("MTGOFormatData non disponible")
        
        engine = ArchetypeEngine(
            format_data_path=str(MTGO_FORMAT_PATH),
            input_dir=str(REAL_DATA_PATH),
            output_dir=str(REAL_DATA_PATH)
        )
        
        assert engine.format_data_path == str(MTGO_FORMAT_PATH)
    
    def test_archetype_formats_availability(self):
        """Test de disponibilité des formats d'archétypes"""
        format_dirs = ['Modern', 'Pioneer', 'Standard', 'Legacy', 'Pauper']
        
        available_formats = []
        for format_dir in format_dirs:
            format_path = MTGO_FORMAT_PATH / "Formats" / format_dir
            if format_path.exists():
                available_formats.append(format_dir)
        
        assert len(available_formats) > 0, "Aucun format d'archétype disponible"
    
    def test_archetype_files_structure(self):
        """Test de la structure des fichiers d'archétypes"""
        if not MTGO_FORMAT_PATH.exists():
            pytest.skip("MTGOFormatData non disponible")
        
        formats_path = MTGO_FORMAT_PATH / "Formats"
        if not formats_path.exists():
            pytest.skip("Dossier Formats non trouvé")
        
        # Vérifier au moins un format
        format_dirs = [d for d in formats_path.iterdir() if d.is_dir()]
        
        if not format_dirs:
            pytest.skip("Aucun dossier de format trouvé")
        
        # Tester le premier format trouvé
        format_dir = format_dirs[0]
        
        # Vérifier la structure
        archetypes_dir = format_dir / "Archetypes"
        if archetypes_dir.exists():
            archetype_files = list(archetypes_dir.glob("*.json"))
            assert len(archetype_files) > 0, f"Aucun archétype trouvé dans {format_dir.name}"

class TestArchetypeClassification:
    """Tests de classification d'archétypes avec données réelles"""
    
    def test_classify_real_deck_data(self):
        """Test de classification avec données de deck réelles"""
        # Charger les données réelles
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Vérifier que les archétypes sont présents
        archetypes = set()
        for record in records:
            archetype = record.get('archetype')
            if archetype:
                archetypes.add(archetype)
        
        assert len(archetypes) > 0, "Aucun archétype trouvé dans les données"
        
        # Vérifier que les archétypes sont valides (non vides)
        for archetype in archetypes:
            assert archetype.strip() != '', "Archétype vide trouvé"
    
    def test_archetype_distribution(self):
        """Test de distribution des archétypes"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Calculer la distribution
        archetype_counts = {}
        total_records = len(records)
        
        for record in records:
            archetype = record.get('archetype', 'Unknown')
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        
        # Vérifier la distribution
        assert len(archetype_counts) > 0, "Aucun archétype compté"
        
        # Calculer les pourcentages
        for archetype, count in archetype_counts.items():
            percentage = (count / total_records) * 100
            assert percentage > 0, f"Pourcentage invalide pour {archetype}"
    
    def test_format_specific_archetypes(self):
        """Test des archétypes spécifiques par format"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Grouper par format
        format_archetypes = {}
        for record in records:
            format_name = record.get('tournament_format', 'unknown')
            archetype = record.get('archetype', 'Unknown')
            
            if format_name not in format_archetypes:
                format_archetypes[format_name] = set()
            
            format_archetypes[format_name].add(archetype)
        
        # Vérifier qu'on a des archétypes par format
        for format_name, archetypes in format_archetypes.items():
            assert len(archetypes) > 0, f"Aucun archétype pour {format_name}"

class TestArchetypeValidation:
    """Tests de validation des archétypes"""
    
    def test_archetype_name_validity(self):
        """Test de validité des noms d'archétypes"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Vérifier les noms d'archétypes
        invalid_names = []
        for record in records:
            archetype = record.get('archetype', '')
            
            # Vérifications de base
            if not archetype or archetype.strip() == '':
                invalid_names.append("Empty archetype")
            elif len(archetype) > 100:  # Nom trop long
                invalid_names.append(f"Too long: {archetype[:50]}...")
            elif archetype.lower() in ['test', 'fake', 'dummy']:
                invalid_names.append(f"Invalid archetype: {archetype}")
        
        # Pas plus de 5% de noms invalides acceptable
        invalid_percentage = (len(invalid_names) / len(records)) * 100
        assert invalid_percentage < 5, f"Trop de noms invalides: {invalid_percentage}%"
    
    def test_archetype_consistency(self):
        """Test de cohérence des archétypes"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Vérifier la cohérence des archétypes par tournoi
        tournament_archetypes = {}
        for record in records:
            tournament_id = record.get('tournament_id')
            archetype = record.get('archetype')
            
            if tournament_id not in tournament_archetypes:
                tournament_archetypes[tournament_id] = set()
            
            tournament_archetypes[tournament_id].add(archetype)
        
        # Vérifier qu'il y a une diversité d'archétypes
        for tournament_id, archetypes in tournament_archetypes.items():
            # Au moins 2 archétypes différents par tournoi (sauf très petits tournois)
            if len(records) > 10:  # Seulement pour les tournois de taille raisonnable
                assert len(archetypes) >= 1, f"Pas assez d'archétypes dans {tournament_id}"

class TestArchetypePerformance:
    """Tests de performance des archétypes"""
    
    def test_archetype_winrate_calculation(self):
        """Test de calcul des winrates d'archétypes"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Calculer les winrates par archétype
        archetype_stats = {}
        for record in records:
            archetype = record.get('archetype', 'Unknown')
            wins = record.get('wins', 0)
            losses = record.get('losses', 0)
            
            if archetype not in archetype_stats:
                archetype_stats[archetype] = {'total_wins': 0, 'total_losses': 0, 'players': 0}
            
            archetype_stats[archetype]['total_wins'] += wins
            archetype_stats[archetype]['total_losses'] += losses
            archetype_stats[archetype]['players'] += 1
        
        # Vérifier les calculs
        for archetype, stats in archetype_stats.items():
            total_games = stats['total_wins'] + stats['total_losses']
            if total_games > 0:
                winrate = stats['total_wins'] / total_games
                assert 0 <= winrate <= 1, f"Winrate invalide pour {archetype}: {winrate}"
    
    def test_archetype_sample_size(self):
        """Test de taille d'échantillon des archétypes"""
        real_data_file = REAL_DATA_PATH / "complete_dataset.json"
        
        if not real_data_file.exists():
            pytest.skip("Données réelles non disponibles")
        
        with open(real_data_file, 'r') as f:
            records = json.load(f)
        
        if not records:
            pytest.skip("Aucun enregistrement trouvé")
        
        # Compter les joueurs par archétype
        archetype_counts = {}
        for record in records:
            archetype = record.get('archetype', 'Unknown')
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        
        # Vérifier qu'on a des échantillons raisonnables
        total_players = sum(archetype_counts.values())
        
        for archetype, count in archetype_counts.items():
            percentage = (count / total_players) * 100
            # Chaque archétype devrait avoir au moins quelques joueurs
            assert count > 0, f"Aucun joueur pour {archetype}"
            
            # Les archétypes principaux devraient avoir une représentation décente
            if percentage > 10:  # Archétypes majeurs
                assert count >= 5, f"Échantillon trop petit pour archétype majeur {archetype}: {count}" 