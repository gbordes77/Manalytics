"""
File watcher for monitoring rule changes and triggering hot-reload.
"""

import os
import time
import threading
from typing import Callable, List, Dict, Any
from pathlib import Path
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class RulesFileHandler(FileSystemEventHandler):
    """Handler for file system events on rules files."""
    
    def __init__(self, callback: Callable[[List[str]], None]):
        """
        Initialize handler.
        
        Args:
            callback: Function to call when files change
        """
        self.callback = callback
        self.last_modified = {}
        self.debounce_time = 2  # seconds
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Filter for relevant files
        if not self._is_rules_file(file_path):
            return
            
        # Debounce rapid changes
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
                
        self.last_modified[file_path] = current_time
        
        logger.info(f"Rules file modified: {file_path}")
        self.callback([file_path])
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._is_rules_file(event.src_path):
            logger.info(f"Rules file created: {event.src_path}")
            self.callback([event.src_path])
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and self._is_rules_file(event.src_path):
            logger.info(f"Rules file deleted: {event.src_path}")
            self.callback([event.src_path])
    
    def _is_rules_file(self, file_path: str) -> bool:
        """Check if file is a rules file."""
        path = Path(file_path)
        return (path.suffix.lower() in ['.json', '.yaml', '.yml'] and 
                ('archetype' in path.name.lower() or 'rules' in path.name.lower()))

class FileWatcher:
    """File watcher for monitoring rule changes."""
    
    def __init__(self, callback: Callable[[List[str]], None]):
        """
        Initialize file watcher.
        
        Args:
            callback: Function to call when files change
        """
        self.callback = callback
        self.observer = Observer()
        self.watched_paths = set()
        self.handler = RulesFileHandler(self._handle_changes)
        self.is_running = False
        
    def add_path(self, path: str, recursive: bool = True):
        """
        Add path to watch.
        
        Args:
            path: Path to watch
            recursive: Whether to watch subdirectories
        """
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return
            
        if path not in self.watched_paths:
            self.observer.schedule(self.handler, path, recursive=recursive)
            self.watched_paths.add(path)
            logger.info(f"Added watch path: {path} (recursive={recursive})")
    
    def start(self):
        """Start watching for file changes."""
        if not self.is_running:
            self.observer.start()
            self.is_running = True
            logger.info("File watcher started")
    
    def stop(self):
        """Stop watching for file changes."""
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("File watcher stopped")
    
    def _handle_changes(self, changed_files: List[str]):
        """Handle file changes with error handling."""
        try:
            self.callback(changed_files)
        except Exception as e:
            logger.error(f"Error handling file changes: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

class PollingFileWatcher:
    """Fallback file watcher using polling (for systems without inotify)."""
    
    def __init__(self, callback: Callable[[List[str]], None], poll_interval: float = 5.0):
        """
        Initialize polling file watcher.
        
        Args:
            callback: Function to call when files change
            poll_interval: Polling interval in seconds
        """
        self.callback = callback
        self.poll_interval = poll_interval
        self.watched_files = {}
        self.is_running = False
        self.thread = None
        
    def add_path(self, path: str, recursive: bool = True):
        """Add path to watch."""
        if os.path.isfile(path):
            self._add_file(path)
        elif os.path.isdir(path):
            self._add_directory(path, recursive)
    
    def _add_file(self, file_path: str):
        """Add single file to watch."""
        try:
            stat = os.stat(file_path)
            self.watched_files[file_path] = stat.st_mtime
            logger.debug(f"Added file to watch: {file_path}")
        except OSError as e:
            logger.warning(f"Could not add file to watch: {file_path} - {e}")
    
    def _add_directory(self, dir_path: str, recursive: bool):
        """Add directory to watch."""
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_rules_file(file_path):
                        self._add_file(file_path)
                
                if not recursive:
                    break
        except OSError as e:
            logger.warning(f"Could not add directory to watch: {dir_path} - {e}")
    
    def _is_rules_file(self, file_path: str) -> bool:
        """Check if file is a rules file."""
        path = Path(file_path)
        return (path.suffix.lower() in ['.json', '.yaml', '.yml'] and 
                ('archetype' in path.name.lower() or 'rules' in path.name.lower()))
    
    def start(self):
        """Start polling for file changes."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._poll_files)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Polling file watcher started")
    
    def stop(self):
        """Stop polling for file changes."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Polling file watcher stopped")
    
    def _poll_files(self):
        """Poll files for changes."""
        while self.is_running:
            try:
                changed_files = []
                
                for file_path, last_mtime in list(self.watched_files.items()):
                    try:
                        current_mtime = os.stat(file_path).st_mtime
                        if current_mtime != last_mtime:
                            changed_files.append(file_path)
                            self.watched_files[file_path] = current_mtime
                    except OSError:
                        # File might have been deleted
                        changed_files.append(file_path)
                        del self.watched_files[file_path]
                
                if changed_files:
                    logger.info(f"Detected changes in {len(changed_files)} files")
                    self.callback(changed_files)
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.poll_interval)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

def create_file_watcher(callback: Callable[[List[str]], None], use_polling: bool = False) -> FileWatcher:
    """
    Create appropriate file watcher based on system capabilities.
    
    Args:
        callback: Function to call when files change
        use_polling: Force use of polling watcher
        
    Returns:
        FileWatcher instance
    """
    if use_polling:
        return PollingFileWatcher(callback)
    
    try:
        # Try to use watchdog
        return FileWatcher(callback)
    except ImportError:
        logger.warning("Watchdog not available, falling back to polling")
        return PollingFileWatcher(callback) 