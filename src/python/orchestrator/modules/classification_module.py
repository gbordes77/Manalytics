"""
Classification Module - Module de Classification des Archétypes
============================================================

Module spécialisé pour la classification des archétypes de decks MTG.
Utilise la configuration centralisée et le système de classification hiérarchique.

Responsabilités:
- Classification hiérarchique des archétypes
- Intégration des couleurs
- Optimisation parallèle
- Monitoring des performances
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
import pandas as pd

from ...utils.logging_manager import ManalyticsLogger
from ...classifier.advanced_archetype_classifier import AdvancedArchetypeClassifier
from ...classifier.archetype_engine import ArchetypeEngine
from ...classifier.color_detector import ColorDetector
from ...classifier.mtgo_classifier import MTGOClassifier


class ClassificationModule:
    """
    Module spécialisé pour la classification des archétypes
    
    🔧 CONFIGURATION CENTRALISÉE:
    - Utilise config_manager pour tous les paramètres
    - Seuils de confiance configurables
    - Nombre maximum d'archétypes configurable
    - Système de couleurs configurable
    
    🎯 CLASSIFICATION HIÉRARCHIQUE:
    1. ArchetypeEngine (MTGOFormatData) - Priorité 1
    2. MTGO Classifier - Fallback
    3. Advanced Classifier - Fallback final
    4. Color Detection - Fallback ultime
    """
    
    def __init__(self, config_manager, enable_parallel: bool = True):
        """
        Initialiser le module de classification
        
        Args:
            config_manager: Gestionnaire de configuration centralisé
            enable_parallel: Activer la classification parallèle
        """
        self.config_manager = config_manager
        self.enable_parallel = enable_parallel
        self.logger = ManalyticsLogger()
        
        # Configuration depuis config_manager
        self.min_cards_for_archetype = self.config_manager.get_value("classification", "min_cards_for_archetype", 10)
        self.confidence_threshold = self.config_manager.get_value("classification", "confidence_threshold", 0.8)
        self.max_archetypes_display = self.config_manager.get_value("classification", "max_archetypes_display", 12)
        
        # Configuration des chemins
        self.mtgo_format_data_path = self.config_manager.get_value("paths", "mtgo_cache_path", "./MTGOFormatData")
        
        # Statistiques
        self.stats = {
            'total_classified': 0,
            'archetype_engine_success': 0,
            'mtgo_classifier_success': 0,
            'advanced_classifier_success': 0,
            'color_fallback_success': 0,
            'unknown_classifications': 0,
            'classification_time': 0
        }
        
        # Initialiser les classificateurs
        self._initialize_classifiers()
        
        self.logger.success("✅ ClassificationModule initialisé")
        self.logger.data_info(f"🎯 Seuil de confiance: {self.confidence_threshold}")
        self.logger.data_info(f"🔢 Max archétypes: {self.max_archetypes_display}")
    
    def _initialize_classifiers(self):
        """Initialiser tous les classificateurs"""
        try:
            # 1. ArchetypeEngine (priorité 1)
            self.archetype_engine = ArchetypeEngine(
                self.mtgo_format_data_path, "./input", "./output"
            )
            
            # 2. MTGO Classifier (fallback)
            self.mtgo_classifier = MTGOClassifier()
            
            # 3. Advanced Classifier (fallback final)
            self.advanced_classifier = AdvancedArchetypeClassifier()
            
            # 4. Color Detector (fallback ultime)
            self.color_detector = ColorDetector()
            
            self.logger.success("✅ Tous les classificateurs initialisés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation classificateurs: {e}")
            raise
    
    async def classify_all_decks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifier tous les decks dans le DataFrame
        
        Args:
            df: DataFrame contenant les données de decks
            
        Returns:
            DataFrame avec les archétypes classifiés
        """
        if df.empty:
            return df
        
        start_time = time.time()
        
        self.logger.info(f"🔍 Classification de {len(df)} decks")
        
        try:
            if self.enable_parallel:
                df = await self._classify_parallel(df)
            else:
                df = await self._classify_sequential(df)
            
            # Post-traitement
            df = self._post_process_classifications(df)
            
            # Statistiques
            classification_time = time.time() - start_time
            self.stats['classification_time'] += classification_time
            self.stats['total_classified'] += len(df)
            
            self.logger.success(f"✅ Classification terminée: {len(df)} decks en {classification_time:.2f}s")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Erreur classification: {e}")
            raise
    
    async def _classify_parallel(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classification parallèle des decks"""
        self.logger.info("🚀 Classification parallèle activée")
        
        # Pour l'instant, utilisation séquentielle
        # TODO: Implémenter la vraie parallélisation avec asyncio
        return await self._classify_sequential(df)
    
    async def _classify_sequential(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classification séquentielle des decks"""
        self.logger.info("🐌 Classification séquentielle")
        
        for idx, row in df.iterrows():
            try:
                maindeck = row.get('maindeck', {})
                archetype = await self._classify_single_deck(maindeck)
                df.at[idx, 'archetype'] = archetype
                df.at[idx, 'archetype_confidence'] = self._calculate_confidence(archetype)
                
            except Exception as e:
                self.logger.warning(f"⚠️  Erreur classification deck {idx}: {e}")
                df.at[idx, 'archetype'] = 'Unknown'
                df.at[idx, 'archetype_confidence'] = 0.0
        
        return df
    
    async def _classify_single_deck(self, maindeck: Dict) -> str:
        """
        Classifier un deck unique avec système hiérarchique
        
        Args:
            maindeck: Dict contenant les cartes du maindeck
            
        Returns:
            Nom de l'archétype classifié
        """
        if not maindeck:
            return 'Unknown'
        
        # 1. Essayer ArchetypeEngine (priorité 1)
        try:
            archetype = self.archetype_engine.classify_deck(maindeck)
            if archetype and archetype != 'Unknown':
                # Appliquer l'intégration des couleurs
                archetype = self._apply_color_integration(archetype, maindeck)
                self.stats['archetype_engine_success'] += 1
                return archetype
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur ArchetypeEngine: {e}")
        
        # 2. Essayer MTGO Classifier (fallback)
        try:
            archetype = self.mtgo_classifier.classify_deck(maindeck)
            if archetype and archetype != 'Unknown':
                archetype = self._apply_color_integration(archetype, maindeck)
                self.stats['mtgo_classifier_success'] += 1
                return archetype
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur MTGO Classifier: {e}")
        
        # 3. Essayer Advanced Classifier (fallback final)
        try:
            archetype = self.advanced_classifier.classify_deck(maindeck)
            if archetype and archetype != 'Unknown':
                archetype = self._apply_color_integration(archetype, maindeck)
                self.stats['advanced_classifier_success'] += 1
                return archetype
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur Advanced Classifier: {e}")
        
        # 4. Fallback couleurs (ultime)
        try:
            colors = self.color_detector.detect_colors(list(maindeck.keys()))
            if colors:
                archetype = self._create_color_archetype(colors)
                self.stats['color_fallback_success'] += 1
                return archetype
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur Color Detection: {e}")
        
        # 5. Échec total
        self.stats['unknown_classifications'] += 1
        return 'Unknown'
    
    def _apply_color_integration(self, archetype: str, maindeck: Dict) -> str:
        """
        Appliquer l'intégration des couleurs à un archétype
        
        Args:
            archetype: Archétype de base
            maindeck: Cartes du maindeck
            
        Returns:
            Archétype avec intégration des couleurs
        """
        try:
            # Détecter les couleurs du deck
            colors = self.color_detector.detect_colors(list(maindeck.keys()))
            
            if not colors:
                return archetype
            
            # Appliquer les règles d'intégration des couleurs
            # (logique spécifique à implémenter selon les besoins)
            color_prefix = self._get_color_prefix(colors)
            
            # Éviter les doublons de couleurs
            if color_prefix.lower() not in archetype.lower():
                return f"{color_prefix} {archetype}"
            
            return archetype
            
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur intégration couleurs: {e}")
            return archetype
    
    def _get_color_prefix(self, colors: List[str]) -> str:
        """Obtenir le préfixe de couleur approprié"""
        if not colors:
            return ""
        
        # Mapping des guildes communes
        guild_mapping = {
            frozenset(['White', 'Blue']): 'Azorius',
            frozenset(['Blue', 'Black']): 'Dimir',
            frozenset(['Black', 'Red']): 'Rakdos',
            frozenset(['Red', 'Green']): 'Gruul',
            frozenset(['Green', 'White']): 'Selesnya',
            frozenset(['White', 'Black']): 'Orzhov',
            frozenset(['Blue', 'Red']): 'Izzet',
            frozenset(['Black', 'Green']): 'Golgari',
            frozenset(['Red', 'White']): 'Boros',
            frozenset(['Green', 'Blue']): 'Simic'
        }
        
        color_set = frozenset(colors)
        
        # Guildes (2 couleurs)
        if len(colors) == 2 and color_set in guild_mapping:
            return guild_mapping[color_set]
        
        # Mono-couleur
        if len(colors) == 1:
            return colors[0]
        
        # Multi-couleurs (3+)
        if len(colors) >= 3:
            return f"{len(colors)}-Color"
        
        return ""
    
    def _create_color_archetype(self, colors: List[str]) -> str:
        """Créer un archétype basé uniquement sur les couleurs"""
        if not colors:
            return 'Colorless'
        
        color_prefix = self._get_color_prefix(colors)
        
        if color_prefix:
            return f"{color_prefix} Control"  # Archétype générique
        
        return 'Multi-Color'
    
    def _calculate_confidence(self, archetype: str) -> float:
        """Calculer la confiance d'une classification"""
        if archetype == 'Unknown':
            return 0.0
        elif 'Control' in archetype and len(archetype.split()) == 2:
            return 0.5  # Fallback couleurs
        else:
            return 0.8  # Classification normale
    
    def _post_process_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        """Post-traitement des classifications"""
        if df.empty:
            return df
        
        # Compter les archétypes
        archetype_counts = df['archetype'].value_counts()
        
        # Limiter le nombre d'archétypes affichés
        top_archetypes = archetype_counts.head(self.max_archetypes_display - 1)
        
        # Regrouper les archétypes rares en "Others"
        others_mask = ~df['archetype'].isin(top_archetypes.index)
        df.loc[others_mask, 'archetype'] = 'Others'
        
        # Statistiques finales
        final_archetype_counts = df['archetype'].value_counts()
        self.logger.data_info(f"🎯 Archétypes finaux: {len(final_archetype_counts)}")
        
        return df
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du module"""
        return {
            **self.stats,
            'success_rates': {
                'archetype_engine': self.stats['archetype_engine_success'] / max(self.stats['total_classified'], 1),
                'mtgo_classifier': self.stats['mtgo_classifier_success'] / max(self.stats['total_classified'], 1),
                'advanced_classifier': self.stats['advanced_classifier_success'] / max(self.stats['total_classified'], 1),
                'color_fallback': self.stats['color_fallback_success'] / max(self.stats['total_classified'], 1),
                'unknown_rate': self.stats['unknown_classifications'] / max(self.stats['total_classified'], 1)
            },
            'configuration': {
                'min_cards_for_archetype': self.min_cards_for_archetype,
                'confidence_threshold': self.confidence_threshold,
                'max_archetypes_display': self.max_archetypes_display,
                'enable_parallel': self.enable_parallel
            }
        }
    
    def reset_stats(self):
        """Réinitialiser les statistiques"""
        self.stats = {
            'total_classified': 0,
            'archetype_engine_success': 0,
            'mtgo_classifier_success': 0,
            'advanced_classifier_success': 0,
            'color_fallback_success': 0,
            'unknown_classifications': 0,
            'classification_time': 0
        }
        self.logger.success("✅ Statistiques réinitialisées") 