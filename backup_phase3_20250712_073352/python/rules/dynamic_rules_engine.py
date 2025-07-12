"""
Dynamic rules engine with hot-reload capabilities.
"""

import subprocess
import os
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import logging
from .rules_loader import RulesLoader
from .file_watcher import create_file_watcher

logger = logging.getLogger(__name__)


class DynamicRulesEngine:
    """Rules engine with hot-reload capabilities."""
    
    def __init__(self, rules_repo_path: str, auto_pull: bool = True):
        """
        Initialize dynamic rules engine.
        
        Args:
            rules_repo_path: Path to rules repository
            auto_pull: Whether to auto-pull git changes
        """
        self.rules_repo = Path(rules_repo_path)
        self.auto_pull = auto_pull
        self.rules_cache = {}
        self.rules_loader = RulesLoader()
        self.file_watcher = None
        self.last_reload_time = {}
        self.reload_callbacks = []
        self.is_running = False
        self._lock = threading.RLock()
        
        # Initialize rules
        self._initial_load()
        
    def _initial_load(self):
        """Perform initial load of all rules."""
        try:
            logger.info("Performing initial rules load...")
            self.rules_cache = self.rules_loader.load_all_formats(str(self.rules_repo))
            logger.info(f"Loaded rules for {len(self.rules_cache)} formats")
            
            # Initialize last reload times
            current_time = time.time()
            for format_name in self.rules_cache:
                self.last_reload_time[format_name] = current_time
                
        except Exception as e:
            logger.error(f"Error during initial rules load: {e}")
            self.rules_cache = {}
    
    def start_watching(self, use_polling: bool = False):
        """
        Start watching for file changes.
        
        Args:
            use_polling: Whether to use polling instead of inotify
        """
        if self.is_running:
            logger.warning("File watcher already running")
            return
            
        try:
            self.file_watcher = create_file_watcher(
                self.on_rules_change, 
                use_polling=use_polling
            )
            
            # Add rules repository to watch
            self.file_watcher.add_path(str(self.rules_repo), recursive=True)
            
            self.file_watcher.start()
            self.is_running = True
            logger.info("Started watching for rules changes")
            
        except Exception as e:
            logger.error(f"Error starting file watcher: {e}")
            # Fall back to manual reload
            self.is_running = False
    
    def stop_watching(self):
        """Stop watching for file changes."""
        if self.file_watcher and self.is_running:
            self.file_watcher.stop()
            self.is_running = False
            logger.info("Stopped watching for rules changes")
    
    def on_rules_change(self, changed_files: List[str]):
        """
        Handle rules file changes.
        
        Args:
            changed_files: List of changed file paths
        """
        try:
            logger.info(f"Detected changes in {len(changed_files)} files")
            
            # Extract affected formats
            affected_formats = set()
            for file_path in changed_files:
                format_name = self.extract_format_from_path(file_path)
                if format_name:
                    affected_formats.add(format_name)
            
            if not affected_formats:
                logger.warning("No format detected from changed files")
                return
            
            # Pull latest changes if enabled
            if self.auto_pull:
                self._pull_git_changes()
            
            # Reload affected formats
            for format_name in affected_formats:
                self.reload_format_rules(format_name)
            
            # Notify callbacks
            self._notify_callbacks(list(affected_formats))
            
        except Exception as e:
            logger.error(f"Error handling rules changes: {e}")
    
    def extract_format_from_path(self, file_path: str) -> Optional[str]:
        """
        Extract format name from file path.
        
        Args:
            file_path: Path to changed file
            
        Returns:
            Format name or None
        """
        try:
            # Use rules loader to extract format
            format_name = self.rules_loader.get_format_from_path(file_path)
            if format_name:
                return format_name
            
            # Fallback: check if path is within a format directory
            relative_path = Path(file_path).relative_to(self.rules_repo)
            
            # First directory component might be the format
            if relative_path.parts:
                potential_format = relative_path.parts[0].lower()
                if potential_format in ['modern', 'legacy', 'vintage', 'standard', 'pioneer', 'historic']:
                    return potential_format
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting format from path {file_path}: {e}")
            return None
    
    def reload_format_rules(self, format_name: str):
        """
        Reload rules for a specific format.
        
        Args:
            format_name: Name of format to reload
        """
        with self._lock:
            try:
                logger.info(f"Reloading rules for format: {format_name}")
                
                format_dir = self.rules_repo / format_name
                if not format_dir.exists():
                    # Try case-insensitive search
                    for item in self.rules_repo.iterdir():
                        if item.is_dir() and item.name.lower() == format_name.lower():
                            format_dir = item
                            break
                    else:
                        logger.warning(f"Format directory not found: {format_name}")
                        return
                
                # Load new rules
                new_rules = self.rules_loader.load_format_rules(str(format_dir))
                
                if new_rules and new_rules.get('archetypes'):
                    # Update cache
                    old_count = len(self.rules_cache.get(format_name, {}).get('archetypes', []))
                    self.rules_cache[format_name] = new_rules
                    new_count = len(new_rules['archetypes'])
                    
                    self.last_reload_time[format_name] = time.time()
                    
                    logger.info(f"Reloaded {format_name}: {old_count} -> {new_count} archetypes")
                else:
                    logger.warning(f"No valid rules found for format: {format_name}")
                    
            except Exception as e:
                logger.error(f"Error reloading rules for {format_name}: {e}")
    
    def _pull_git_changes(self):
        """Pull latest changes from git repository."""
        try:
            logger.info("Pulling latest rules from git...")
            
            result = subprocess.run(
                ['git', 'pull'],
                cwd=str(self.rules_repo),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Successfully pulled git changes")
                logger.debug(f"Git output: {result.stdout}")
            else:
                logger.warning(f"Git pull failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Git pull timed out")
        except Exception as e:
            logger.error(f"Error pulling git changes: {e}")
    
    def get_rules(self, format_name: str) -> Dict[str, Any]:
        """
        Get rules for a specific format.
        
        Args:
            format_name: Name of format
            
        Returns:
            Rules dictionary
        """
        with self._lock:
            rules = self.rules_cache.get(format_name.lower(), {})
            if not rules:
                logger.warning(f"No rules found for format: {format_name}")
                # Try to load on-demand
                self.reload_format_rules(format_name.lower())
                rules = self.rules_cache.get(format_name.lower(), {})
            
            return rules.copy()  # Return copy to prevent external modification
    
    def get_archetypes(self, format_name: str) -> List[Dict[str, Any]]:
        """
        Get archetypes for a specific format.
        
        Args:
            format_name: Name of format
            
        Returns:
            List of archetype definitions
        """
        rules = self.get_rules(format_name)
        return rules.get('archetypes', [])
    
    def classify_deck(self, deck: Dict[str, Any], format_name: str) -> Optional[str]:
        """
        Classify a deck using current rules.
        
        Args:
            deck: Deck data
            format_name: Format name
            
        Returns:
            Archetype name or None
        """
        archetypes = self.get_archetypes(format_name)
        
        if not archetypes:
            logger.warning(f"No archetypes available for format: {format_name}")
            return None
        
        # Extract deck cards
        mainboard = {card.get('name', ''): card.get('count', 0) 
                    for card in deck.get('mainboard', [])}
        sideboard = {card.get('name', ''): card.get('count', 0) 
                    for card in deck.get('sideboard', [])}
        
        # Try to match archetypes
        for archetype in archetypes:
            if self._matches_conditions(mainboard, sideboard, archetype.get('conditions', [])):
                return archetype.get('name')
        
        return None
    
    def _matches_conditions(self, mainboard: Dict[str, int], sideboard: Dict[str, int], 
                           conditions: List[Dict[str, Any]]) -> bool:
        """
        Check if deck matches archetype conditions.
        
        Args:
            mainboard: Mainboard cards
            sideboard: Sideboard cards
            conditions: Archetype conditions
            
        Returns:
            True if all conditions match
        """
        for condition in conditions:
            if not self._matches_condition(mainboard, sideboard, condition):
                return False
        return True
    
    def _matches_condition(self, mainboard: Dict[str, int], sideboard: Dict[str, int], 
                          condition: Dict[str, Any]) -> bool:
        """Check if deck matches a single condition."""
        condition_type = condition.get('type')
        cards = condition.get('cards', [])
        
        if condition_type == 'contains':
            min_count = condition.get('min', 1)
            total = sum(mainboard.get(card, 0) + sideboard.get(card, 0) for card in cards)
            return total >= min_count
            
        elif condition_type == 'excludes':
            total = sum(mainboard.get(card, 0) + sideboard.get(card, 0) for card in cards)
            return total == 0
            
        elif condition_type == 'count':
            min_count = condition.get('min', 1)
            max_count = condition.get('max', float('inf'))
            total = sum(mainboard.get(card, 0) + sideboard.get(card, 0) for card in cards)
            return min_count <= total <= max_count
            
        elif condition_type == 'ratio':
            # More complex ratio-based matching
            target_ratio = condition.get('ratio', 0.5)
            total_deck = sum(mainboard.values())
            if total_deck == 0:
                return False
            
            card_count = sum(mainboard.get(card, 0) for card in cards)
            actual_ratio = card_count / total_deck
            tolerance = condition.get('tolerance', 0.1)
            
            return abs(actual_ratio - target_ratio) <= tolerance
        
        return False
    
    def add_reload_callback(self, callback: Callable[[List[str]], None]):
        """
        Add callback to be called when rules are reloaded.
        
        Args:
            callback: Function to call with list of affected formats
        """
        self.reload_callbacks.append(callback)
    
    def _notify_callbacks(self, affected_formats: List[str]):
        """Notify all registered callbacks."""
        for callback in self.reload_callbacks:
            try:
                callback(affected_formats)
            except Exception as e:
                logger.error(f"Error in reload callback: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the rules engine."""
        with self._lock:
            stats = {
                'total_formats': len(self.rules_cache),
                'total_archetypes': sum(len(rules.get('archetypes', [])) 
                                      for rules in self.rules_cache.values()),
                'formats': {},
                'is_watching': self.is_running,
                'last_reload_times': self.last_reload_time.copy()
            }
            
            for format_name, rules in self.rules_cache.items():
                stats['formats'][format_name] = {
                    'archetypes': len(rules.get('archetypes', [])),
                    'last_reload': self.last_reload_time.get(format_name, 0)
                }
            
            return stats
    
    def force_reload_all(self):
        """Force reload of all format rules."""
        logger.info("Force reloading all rules...")
        
        if self.auto_pull:
            self._pull_git_changes()
        
        with self._lock:
            old_cache = self.rules_cache.copy()
            self.rules_cache = self.rules_loader.load_all_formats(str(self.rules_repo))
            
            current_time = time.time()
            for format_name in self.rules_cache:
                self.last_reload_time[format_name] = current_time
        
        # Notify callbacks
        affected_formats = list(self.rules_cache.keys())
        self._notify_callbacks(affected_formats)
        
        logger.info(f"Force reloaded {len(affected_formats)} formats")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_watching()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_watching() 