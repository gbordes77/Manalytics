"""
Parallel processor for high-performance tournament data processing.
"""

import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Union
import logging
import time
from functools import partial
import pickle

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """High-performance parallel processor for tournament data."""
    
    def __init__(self, num_workers: int = None, use_processes: bool = True):
        """
        Initialize parallel processor.
        
        Args:
            num_workers: Number of worker processes/threads
            use_processes: Whether to use processes (True) or threads (False)
        """
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.use_processes = use_processes
        self.executor = None
        self.active_tasks = []
        
        logger.info(f"Initialized parallel processor: {self.num_workers} workers, "
                   f"mode: {'processes' if use_processes else 'threads'}")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
    
    def start(self):
        """Start the executor."""
        if self.executor is None:
            if self.use_processes:
                self.executor = ProcessPoolExecutor(max_workers=self.num_workers)
            else:
                self.executor = ThreadPoolExecutor(max_workers=self.num_workers)
            logger.info("Parallel processor started")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the executor."""
        if self.executor:
            self.executor.shutdown(wait=wait)
            self.executor = None
            logger.info("Parallel processor shutdown")
    
    async def process_tournaments_batch(self, tournaments: List[str], 
                                       process_func: Callable[[str], Any],
                                       timeout: int = 300) -> List[Any]:
        """
        Process tournaments in parallel batches.
        
        Args:
            tournaments: List of tournament identifiers
            process_func: Function to process each tournament
            timeout: Timeout per task in seconds
            
        Returns:
            List of processing results
        """
        if not self.executor:
            self.start()
        
        # Create chunks for parallel processing
        chunks = self.chunk_tournaments(tournaments, self.num_workers)
        
        # Submit tasks
        futures = []
        for chunk in chunks:
            if self.use_processes:
                # For processes, we need to use a wrapper function
                future = self.executor.submit(self._process_chunk_wrapper, chunk, process_func)
            else:
                # For threads, we can use the function directly
                future = self.executor.submit(self._process_chunk, chunk, process_func)
            futures.append(future)
        
        # Collect results
        results = []
        for future in as_completed(futures, timeout=timeout):
            try:
                chunk_results = future.result(timeout=timeout)
                results.extend(chunk_results)
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                # Continue with other chunks
        
        return results
    
    def chunk_tournaments(self, tournaments: List[str], num_chunks: int) -> List[List[str]]:
        """
        Split tournaments into chunks for parallel processing.
        
        Args:
            tournaments: List of tournament identifiers
            num_chunks: Number of chunks to create
            
        Returns:
            List of tournament chunks
        """
        if not tournaments:
            return []
        
        chunk_size = max(1, len(tournaments) // num_chunks)
        chunks = []
        
        for i in range(0, len(tournaments), chunk_size):
            chunk = tournaments[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def _process_chunk_wrapper(self, chunk: List[str], process_func: Callable[[str], Any]) -> List[Any]:
        """
        Wrapper for processing chunks in separate processes.
        
        Args:
            chunk: List of tournament identifiers
            process_func: Function to process each tournament
            
        Returns:
            List of processing results
        """
        # This function runs in a separate process
        results = []
        
        for tournament_id in chunk:
            try:
                result = process_func(tournament_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing tournament {tournament_id}: {e}")
                results.append(None)
        
        return results
    
    def _process_chunk(self, chunk: List[str], process_func: Callable[[str], Any]) -> List[Any]:
        """
        Process a chunk of tournaments (for thread-based processing).
        
        Args:
            chunk: List of tournament identifiers
            process_func: Function to process each tournament
            
        Returns:
            List of processing results
        """
        results = []
        
        for tournament_id in chunk:
            try:
                result = process_func(tournament_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing tournament {tournament_id}: {e}")
                results.append(None)
        
        return results
    
    async def process_with_progress(self, tournaments: List[str], 
                                   process_func: Callable[[str], Any],
                                   progress_callback: Optional[Callable[[int, int], None]] = None,
                                   timeout: int = 300) -> List[Any]:
        """
        Process tournaments with progress tracking.
        
        Args:
            tournaments: List of tournament identifiers
            process_func: Function to process each tournament
            progress_callback: Optional callback for progress updates
            timeout: Timeout per task in seconds
            
        Returns:
            List of processing results
        """
        if not self.executor:
            self.start()
        
        # Submit individual tasks for better progress tracking
        futures = {}
        for tournament_id in tournaments:
            if self.use_processes:
                future = self.executor.submit(process_func, tournament_id)
            else:
                future = self.executor.submit(process_func, tournament_id)
            futures[future] = tournament_id
        
        # Process results as they complete
        results = []
        completed = 0
        
        for future in as_completed(futures, timeout=timeout):
            try:
                result = future.result(timeout=timeout)
                results.append(result)
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(tournaments))
                    
            except Exception as e:
                tournament_id = futures[future]
                logger.error(f"Error processing tournament {tournament_id}: {e}")
                results.append(None)
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(tournaments))
        
        return results
    
    def process_sync(self, tournaments: List[str], 
                    process_func: Callable[[str], Any],
                    timeout: int = 300) -> List[Any]:
        """
        Synchronous version of parallel processing.
        
        Args:
            tournaments: List of tournament identifiers
            process_func: Function to process each tournament
            timeout: Timeout per task in seconds
            
        Returns:
            List of processing results
        """
        if not self.executor:
            self.start()
        
        # Submit all tasks
        futures = []
        for tournament_id in tournaments:
            if self.use_processes:
                future = self.executor.submit(process_func, tournament_id)
            else:
                future = self.executor.submit(process_func, tournament_id)
            futures.append(future)
        
        # Wait for all to complete
        results = []
        for future in futures:
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in parallel processing: {e}")
                results.append(None)
        
        return results
    
    def get_optimal_chunk_size(self, total_items: int, processing_time_estimate: float = 1.0) -> int:
        """
        Calculate optimal chunk size based on number of items and processing time.
        
        Args:
            total_items: Total number of items to process
            processing_time_estimate: Estimated processing time per item (seconds)
            
        Returns:
            Optimal chunk size
        """
        if total_items <= self.num_workers:
            return 1
        
        # Target: each chunk should take 10-60 seconds to process
        target_chunk_time = 30.0  # seconds
        items_per_chunk = max(1, int(target_chunk_time / processing_time_estimate))
        
        # Ensure we have at least as many chunks as workers
        max_chunk_size = total_items // self.num_workers
        
        return min(items_per_chunk, max_chunk_size)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            'num_workers': self.num_workers,
            'use_processes': self.use_processes,
            'is_active': self.executor is not None,
            'active_tasks': len(self.active_tasks)
        }


class AsyncParallelProcessor:
    """Async version of parallel processor using asyncio."""
    
    def __init__(self, max_concurrent: int = 10):
        """
        Initialize async parallel processor.
        
        Args:
            max_concurrent: Maximum concurrent tasks
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks = set()
        
    async def process_tournaments_async(self, tournaments: List[str],
                                       process_func: Callable[[str], Any]) -> List[Any]:
        """
        Process tournaments asynchronously.
        
        Args:
            tournaments: List of tournament identifiers
            process_func: Async function to process each tournament
            
        Returns:
            List of processing results
        """
        # Create tasks with semaphore control
        tasks = []
        for tournament_id in tournaments:
            task = asyncio.create_task(
                self._process_with_semaphore(tournament_id, process_func)
            )
            tasks.append(task)
            self.active_tasks.add(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clean up completed tasks
        for task in tasks:
            self.active_tasks.discard(task)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing tournament {tournaments[i]}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_with_semaphore(self, tournament_id: str, 
                                     process_func: Callable[[str], Any]) -> Any:
        """Process tournament with semaphore control."""
        async with self.semaphore:
            try:
                if asyncio.iscoroutinefunction(process_func):
                    return await process_func(tournament_id)
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, process_func, tournament_id)
            except Exception as e:
                logger.error(f"Error processing tournament {tournament_id}: {e}")
                raise
    
    async def process_with_progress_async(self, tournaments: List[str],
                                         process_func: Callable[[str], Any],
                                         progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Any]:
        """Process tournaments with progress tracking."""
        results = []
        completed = 0
        
        # Process in batches to control memory usage
        batch_size = min(self.max_concurrent, len(tournaments))
        
        for i in range(0, len(tournaments), batch_size):
            batch = tournaments[i:i + batch_size]
            batch_results = await self.process_tournaments_async(batch, process_func)
            results.extend(batch_results)
            completed += len(batch)
            
            if progress_callback:
                progress_callback(completed, len(tournaments))
        
        return results
    
    def cancel_all_tasks(self):
        """Cancel all active tasks."""
        for task in self.active_tasks:
            task.cancel()
        self.active_tasks.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get async processor statistics."""
        return {
            'max_concurrent': self.max_concurrent,
            'active_tasks': len(self.active_tasks)
        }


# Utility functions for common processing patterns

def process_tournament_classification(tournament_data: Dict[str, Any], 
                                     classifier_func: Callable[[Dict[str, Any]], str]) -> Dict[str, Any]:
    """
    Process tournament for archetype classification.
    
    Args:
        tournament_data: Tournament data
        classifier_func: Function to classify decks
        
    Returns:
        Tournament data with classified archetypes
    """
    try:
        players = tournament_data.get('players', [])
        
        for player in players:
            deck = player.get('deck', {})
            if deck and not deck.get('archetype'):
                archetype = classifier_func(deck)
                deck['archetype'] = archetype
        
        return tournament_data
        
    except Exception as e:
        logger.error(f"Error in tournament classification: {e}")
        return tournament_data


def process_tournament_validation(tournament_data: Dict[str, Any],
                                 validator_func: Callable[[Dict[str, Any]], bool]) -> Dict[str, Any]:
    """
    Process tournament for validation.
    
    Args:
        tournament_data: Tournament data
        validator_func: Function to validate tournament
        
    Returns:
        Tournament data with validation results
    """
    try:
        is_valid = validator_func(tournament_data)
        tournament_data['validation'] = {
            'is_valid': is_valid,
            'validated_at': time.time()
        }
        
        return tournament_data
        
    except Exception as e:
        logger.error(f"Error in tournament validation: {e}")
        tournament_data['validation'] = {
            'is_valid': False,
            'error': str(e),
            'validated_at': time.time()
        }
        return tournament_data 