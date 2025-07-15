import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Imports des composants existants
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python.cache.smart_cache import smart_cache
from python.parallel.parallel_data_loader import ParallelDataLoader
from python.analytics.advanced_metagame_analyzer import AdvancedMetagameAnalyzer
from python.visualizations.metagame_charts import MetagameChartsGenerator
from python.visualizations.matchup_matrix import MatchupMatrixGenerator

logger = logging.getLogger(__name__)

class ParallelOrchestrator:
    """Orchestrateur optimisé avec parallélisation complète
    
    🚀 OBJECTIFS PLAN EXPERT :
    - Pipeline global : 2s → <1s (60% amélioration)
    - Chargement parallèle : 0.5s → 0.2s
    - Classification batch : 0.3s → 0.18s
    - Analyse & visualisation : 0.7s → 0.3s
    - Cache hit rate : >80%
    - Parallélisation complète avec async/await
    """
    
    def __init__(self, max_workers: int = 4, enable_cache: bool = True):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.enable_cache = enable_cache
        self.cache = smart_cache if enable_cache else None
        
        # Composants
        self.data_loader = ParallelDataLoader(max_workers=max_workers)
        self.analyzer = AdvancedMetagameAnalyzer()
        self.charts_generator = MetagameChartsGenerator()
        self.matchup_generator = MatchupMatrixGenerator()
        
        # Métriques de performance
        self.performance_metrics = {
            'total_time': 0,
            'data_loading_time': 0,
            'classification_time': 0,
            'analysis_time': 0,
            'visualization_time': 0,
            'cache_hit_rate': 0
        }
        
        logger.info("ParallelOrchestrator initialized", extra={
            'max_workers': max_workers,
            'cache_enabled': enable_cache
        })
    
    async def run_parallel_pipeline(
        self, 
        format_name: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Pipeline parallélisé - Objectif: <1 seconde
        Amélioration: 60% par rapport au pipeline séquentiel
        """
        
        pipeline_start = time.time()
        cache_key = f"pipeline_{format_name}_{start_date}_{end_date}"
        
        logger.info(f"Starting parallel pipeline for {format_name} ({start_date} to {end_date})")
        
        # Vérifier cache complet
        if self.enable_cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info("Complete pipeline result found in cache")
                return {
                    **cached_result,
                    "cache_hit": True,
                    "performance": {
                        "total_time": time.time() - pipeline_start,
                        "source": "cache"
                    }
                }
        
        try:
            # PHASE 1: Chargement parallèle des données (0.5s → 0.2s)
            data_start = time.time()
            tournament_data = await self._parallel_data_loading(format_name, start_date, end_date)
            data_time = time.time() - data_start
            
            # PHASE 2: Classification par batch (0.3s → 0.18s)
            class_start = time.time()
            classified_data = await self._parallel_classification(tournament_data)
            class_time = time.time() - class_start
            
            # PHASE 3: Analyse et visualisation parallèles (0.7s → 0.3s)
            viz_start = time.time()
            analysis, visualizations = await self._parallel_analysis_viz(classified_data)
            viz_time = time.time() - viz_start
            
            total_time = time.time() - pipeline_start
            
            # Construire résultat
            result = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "format": format_name,
                "date_range": f"{start_date} to {end_date}",
                "data": {
                    "analysis": analysis,
                    "visualizations": visualizations,
                    "tournament_count": len(tournament_data),
                    "deck_count": sum(len(t.get("decks", [])) for t in tournament_data)
                },
                "performance": {
                    "total_time": total_time,
                    "data_loading": data_time,
                    "classification": class_time,
                    "analysis_viz": viz_time,
                    "improvement_vs_sequential": f"{max(0, (2.0 - total_time) / 2.0 * 100):.1f}%",
                    "objective_met": total_time < 1.0
                },
                "cache_hit": False
            }
            
            # Mettre en cache si objectif atteint
            if self.enable_cache and total_time < 1.2:  # Petit buffer
                await self.cache.set(cache_key, result, ttl=1800)  # 30 minutes
            
            # Mettre à jour métriques
            self._update_performance_metrics(data_time, class_time, viz_time, total_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "performance": {
                    "total_time": time.time() - pipeline_start,
                    "objective_met": False
                }
            }
    
    async def _parallel_data_loading(
        self, 
        format_name: str, 
        start_date: str, 
        end_date: str
    ) -> List[Dict]:
        """Chargement parallèle depuis toutes les sources"""
        
        cache_key = f"tournaments_{format_name}_{start_date}_{end_date}"
        
        # Vérifier cache
        if self.enable_cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info("Tournament data found in cache")
                return cached_data
        
        # Créer les tâches pour chaque source
        tasks = [
            self._load_source_data("mtgo", format_name, start_date, end_date),
            self._load_source_data("melee", format_name, start_date, end_date),
            self._load_source_data("topdeck", format_name, start_date, end_date),
        ]
        
        # Exécuter en parallèle avec gestion d'erreurs
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Consolider les résultats
        all_tournaments = []
        for i, result in enumerate(results):
            source = ["MTGO", "Melee", "TopDeck"][i]
            if isinstance(result, Exception):
                logger.warning(f"Failed to load from {source}: {result}")
            else:
                all_tournaments.extend(result)
                logger.info(f"Loaded {len(result)} tournaments from {source}")
        
        # Mettre en cache
        if self.enable_cache and all_tournaments:
            await self.cache.set(cache_key, all_tournaments, ttl=3600)
        
        return all_tournaments
    
    async def _load_source_data(
        self, 
        source: str, 
        format_name: str, 
        start_date: str, 
        end_date: str
    ) -> List[Dict]:
        """Charger données d'une source spécifique"""
        
        try:
            # Utiliser le data loader parallèle existant
            loop = asyncio.get_event_loop()
            
            # Exécuter dans un thread pour éviter le blocage
            result = await loop.run_in_executor(
                self.executor,
                self.data_loader.load_data,
                format_name,
                start_date,
                end_date
            )
            
            # Filtrer par source si nécessaire
            if hasattr(result, 'iterrows'):
                # Si c'est un DataFrame
                tournaments = []
                for _, row in result.iterrows():
                    if source.lower() in str(row.get('source', '')).lower():
                        tournaments.append(row.to_dict())
                return tournaments
            else:
                # Si c'est déjà une liste
                return result if isinstance(result, list) else []
                
        except Exception as e:
            logger.error(f"Error loading {source} data: {e}")
            return []
    
    async def _parallel_classification(self, tournaments: List[Dict]) -> List[Dict]:
        """Classification par batch avec parallélisation"""
        
        if not tournaments:
            return []
        
        cache_key = f"classification_{len(tournaments)}_{hash(str(tournaments[:5]))}"
        
        # Vérifier cache
        if self.enable_cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info("Classification data found in cache")
                return cached_data
        
        # Extraire tous les decks
        all_decks = []
        deck_to_tournament = {}
        
        for t_idx, tournament in enumerate(tournaments):
            for d_idx, deck in enumerate(tournament.get("decks", [])):
                deck_id = f"{t_idx}_{d_idx}"
                all_decks.append((deck_id, deck))
                deck_to_tournament[deck_id] = (t_idx, d_idx)
        
        if not all_decks:
            return tournaments
        
        # Classifier par chunks en parallèle
        chunk_size = 50  # Optimisé pour performance
        chunks = [all_decks[i:i+chunk_size] for i in range(0, len(all_decks), chunk_size)]
        
        # Traitement parallèle
        classification_tasks = [
            self._classify_deck_chunk(chunk) for chunk in chunks
        ]
        
        classified_chunks = await asyncio.gather(*classification_tasks)
        
        # Réassembler les résultats
        for chunk_results in classified_chunks:
            for deck_id, archetype in chunk_results:
                if deck_id in deck_to_tournament:
                    t_idx, d_idx = deck_to_tournament[deck_id]
                    if t_idx < len(tournaments) and d_idx < len(tournaments[t_idx].get("decks", [])):
                        tournaments[t_idx]["decks"][d_idx]["archetype"] = archetype
        
        # Mettre en cache
        if self.enable_cache:
            await self.cache.set(cache_key, tournaments, ttl=3600)
        
        return tournaments
    
    async def _classify_deck_chunk(self, chunk: List[Tuple]) -> List[Tuple]:
        """Classification d'un chunk de decks"""
        
        # Utiliser ThreadPoolExecutor pour CPU-bound work
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._classify_decks_sync,
            chunk
        )
    
    def _classify_decks_sync(self, chunk: List[Tuple]) -> List[Tuple]:
        """Classification synchrone pour executor"""
        
        results = []
        for deck_id, deck in chunk:
            try:
                # Simulation classification (remplacer par vraie logique)
                archetype = self._classify_single_deck(deck)
                results.append((deck_id, archetype))
            except Exception as e:
                logger.error(f"Classification error for deck {deck_id}: {e}")
                results.append((deck_id, "Unknown"))
        
        return results
    
    def _classify_single_deck(self, deck: Dict) -> str:
        """Classification d'un seul deck (simulation)"""
        
        # TODO: Utiliser le vrai système de classification
        # Pour l'instant, simulation basique
        
        cards = deck.get("cards", [])
        if not cards:
            return "Unknown"
        
        # Logique de classification simplifiée
        if any("Lightning Bolt" in str(card) for card in cards):
            return "Burn"
        elif any("Counterspell" in str(card) for card in cards):
            return "Control"
        elif any("Tarmogoyf" in str(card) for card in cards):
            return "Midrange"
        else:
            return "Unknown"
    
    async def _parallel_analysis_viz(
        self, 
        classified_data: List[Dict]
    ) -> Tuple[Dict, Dict]:
        """Analyse et visualisation en parallèle"""
        
        if not classified_data:
            return {}, {}
        
        # Clés de cache
        analysis_key = f"analysis_{len(classified_data)}_{hash(str(classified_data[:3]))}"
        viz_key = f"visualizations_{len(classified_data)}_{hash(str(classified_data[:3]))}"
        
        # Vérifier cache pour analyse
        analysis_cached = None
        viz_cached = None
        
        if self.enable_cache:
            analysis_cached = await self.cache.get(analysis_key)
            viz_cached = await self.cache.get(viz_key)
        
        # Lancer analyse et visualisations de base en parallèle
        tasks = []
        
        if not analysis_cached:
            tasks.append(self._run_analysis(classified_data))
        
        if not viz_cached:
            tasks.append(self._generate_basic_visualizations(classified_data))
        
        # Exécuter les tâches non cachées
        results = []
        if tasks:
            results = await asyncio.gather(*tasks)
        
        # Récupérer résultats
        if analysis_cached:
            analysis = analysis_cached
        else:
            analysis = results[0] if results else {}
        
        if viz_cached:
            basic_viz = viz_cached
        else:
            basic_viz = results[-1] if results else {}
        
        # Générer visualisations avancées basées sur l'analyse
        advanced_viz = await self._generate_advanced_visualizations(analysis)
        
        # Combiner toutes les visualisations
        all_visualizations = {**basic_viz, **advanced_viz}
        
        # Mettre en cache
        if self.enable_cache:
            if not analysis_cached:
                await self.cache.set(analysis_key, analysis, ttl=1800)
            if not viz_cached:
                await self.cache.set(viz_key, basic_viz, ttl=900)
        
        return analysis, all_visualizations
    
    async def _run_analysis(self, data: List[Dict]) -> Dict:
        """Analyse du métagame"""
        
        loop = asyncio.get_event_loop()
        
        # Exécuter analyse dans un thread
        analysis = await loop.run_in_executor(
            self.executor,
            self._analyze_metagame_sync,
            data
        )
        
        return analysis
    
    def _analyze_metagame_sync(self, data: List[Dict]) -> Dict:
        """Analyse synchrone du métagame"""
        
        try:
            # Utiliser l'analyzeur existant
            df = pd.DataFrame(data)
            
            # Calculer métriques basiques
            total_tournaments = len(data)
            total_decks = sum(len(t.get("decks", [])) for t in data)
            
            # Analyser archétypes
            archetype_counts = {}
            for tournament in data:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype", "Unknown")
                    archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            
            # Calculer diversité
            diversity = len(archetype_counts) / max(1, total_decks)
            
            # Top archétypes
            top_archetypes = sorted(
                archetype_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            return {
                "total_tournaments": total_tournaments,
                "total_decks": total_decks,
                "diversity_index": diversity,
                "top_archetypes": top_archetypes,
                "archetype_distribution": archetype_counts,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                "error": str(e),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_basic_visualizations(self, data: List[Dict]) -> Dict:
        """Génération visualisations de base"""
        
        # Générer en parallèle avec ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        
        tasks = [
            loop.run_in_executor(self.executor, self._create_pie_chart, data),
            loop.run_in_executor(self.executor, self._create_bar_chart, data),
            loop.run_in_executor(self.executor, self._create_trend_chart, data),
        ]
        
        pie, bar, trend = await asyncio.gather(*tasks)
        
        return {
            "pie_chart": pie,
            "bar_chart": bar,
            "trend_chart": trend
        }
    
    async def _generate_advanced_visualizations(self, analysis: Dict) -> Dict:
        """Génération visualisations avancées"""
        
        if not analysis or "error" in analysis:
            return {}
        
        loop = asyncio.get_event_loop()
        
        # Générer visualisations avancées
        tasks = [
            loop.run_in_executor(self.executor, self._create_matchup_matrix, analysis),
            loop.run_in_executor(self.executor, self._create_diversity_chart, analysis),
        ]
        
        matchup, diversity = await asyncio.gather(*tasks)
        
        return {
            "matchup_matrix": matchup,
            "diversity_chart": diversity
        }
    
    def _create_pie_chart(self, data: List[Dict]) -> Dict:
        """Création graphique camembert"""
        
        try:
            # Utiliser le générateur existant
            archetype_counts = {}
            for tournament in data:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype", "Unknown")
                    archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            
            return {
                "type": "pie",
                "title": "Archetype Distribution",
                "data": archetype_counts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pie chart generation error: {e}")
            return {"type": "pie", "error": str(e)}
    
    def _create_bar_chart(self, data: List[Dict]) -> Dict:
        """Création graphique barres"""
        
        try:
            # Top 10 archétypes
            archetype_counts = {}
            for tournament in data:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype", "Unknown")
                    archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            
            top_archetypes = sorted(
                archetype_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            return {
                "type": "bar",
                "title": "Top 10 Archetypes",
                "data": dict(top_archetypes),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bar chart generation error: {e}")
            return {"type": "bar", "error": str(e)}
    
    def _create_trend_chart(self, data: List[Dict]) -> Dict:
        """Création graphique tendances"""
        
        try:
            # Analyser tendances par date
            date_counts = {}
            for tournament in data:
                date = tournament.get("date", "unknown")
                date_counts[date] = date_counts.get(date, 0) + 1
            
            return {
                "type": "line",
                "title": "Tournament Trends",
                "data": date_counts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trend chart generation error: {e}")
            return {"type": "line", "error": str(e)}
    
    def _create_matchup_matrix(self, analysis: Dict) -> Dict:
        """Création matrice matchups"""
        
        try:
            # Simulation matrice matchups
            top_archetypes = analysis.get("top_archetypes", [])[:5]
            
            matrix = {}
            for arch1, _ in top_archetypes:
                matrix[arch1] = {}
                for arch2, _ in top_archetypes:
                    # Simulation win rate
                    if arch1 == arch2:
                        matrix[arch1][arch2] = 0.5
                    else:
                        matrix[arch1][arch2] = 0.45 + (hash(arch1 + arch2) % 20) / 100
            
            return {
                "type": "matrix",
                "title": "Matchup Matrix",
                "data": matrix,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Matchup matrix generation error: {e}")
            return {"type": "matrix", "error": str(e)}
    
    def _create_diversity_chart(self, analysis: Dict) -> Dict:
        """Création graphique diversité"""
        
        try:
            diversity_index = analysis.get("diversity_index", 0)
            
            return {
                "type": "gauge",
                "title": "Meta Diversity Index",
                "data": {
                    "value": diversity_index,
                    "max": 1.0,
                    "label": f"{diversity_index:.2f}"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Diversity chart generation error: {e}")
            return {"type": "gauge", "error": str(e)}
    
    def _update_performance_metrics(self, data_time: float, class_time: float, 
                                   viz_time: float, total_time: float):
        """Mettre à jour les métriques de performance"""
        
        self.performance_metrics.update({
            'total_time': total_time,
            'data_loading_time': data_time,
            'classification_time': class_time,
            'analysis_time': viz_time * 0.6,  # Estimation
            'visualization_time': viz_time * 0.4,  # Estimation
            'cache_hit_rate': self.cache.get_stats().get('hit_rate', '0%') if self.cache else '0%'
        })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtenir statistiques de performance"""
        
        cache_stats = self.cache.get_stats() if self.cache else {}
        
        return {
            "pipeline_metrics": self.performance_metrics,
            "cache_stats": cache_stats,
            "objectives": {
                "target_total_time": "< 1.0s",
                "target_hit_rate": "> 80%",
                "current_total_time": f"{self.performance_metrics['total_time']:.2f}s",
                "objective_met": self.performance_metrics['total_time'] < 1.0
            },
            "optimization_status": "active"
        }
    
    def __del__(self):
        """Cleanup lors de la destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Instance globale optimisée
parallel_orchestrator = ParallelOrchestrator(
    max_workers=4,
    enable_cache=True
) 