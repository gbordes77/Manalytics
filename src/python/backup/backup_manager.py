"""
Backup manager for incremental backups and point-in-time recovery.
"""

import os
import hashlib
import json
import shutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import logging
import tarfile
import gzip

logger = logging.getLogger(__name__)

class BackupManager:
    """Manager for incremental backups with point-in-time recovery."""
    
    def __init__(self, backup_config: Dict[str, Any]):
        """
        Initialize backup manager.
        
        Args:
            backup_config: Backup configuration
        """
        self.config = {
            'backup_root': './backups',
            'retention_days': 30,
            'compression': True,
            'incremental': True,
            'max_backup_size': 10 * 1024 * 1024 * 1024,  # 10GB
            'exclude_patterns': ['*.tmp', '*.log', '__pycache__'],
            **backup_config
        }
        
        self.backup_root = Path(self.config['backup_root'])
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Storage backend
        self.storage_backend = self._initialize_storage_backend()
        
        # Backup metadata
        self.metadata_file = self.backup_root / 'backup_metadata.json'
        self.metadata = self._load_metadata()
        
        # Thread safety
        self._lock = threading.RLock()
        
    def _initialize_storage_backend(self):
        """Initialize storage backend based on configuration."""
        backend_type = self.config.get('storage_backend', 'local')
        
        if backend_type == 'local':
            from .storage_backends import LocalStorageBackend
            return LocalStorageBackend(self.config)
        elif backend_type == 's3':
            from .storage_backends import S3StorageBackend
            return S3StorageBackend(self.config)
        else:
            raise ValueError(f"Unknown storage backend: {backend_type}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading backup metadata: {e}")
        
        return {
            'backups': [],
            'last_full_backup': None,
            'file_checksums': {}
        }
    
    def _save_metadata(self):
        """Save backup metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving backup metadata: {e}")
    
    def create_incremental_backup(self, source_paths: List[str], 
                                 backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create incremental backup of specified paths.
        
        Args:
            source_paths: List of paths to backup
            backup_name: Optional backup name
            
        Returns:
            Backup information
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                backup_name = backup_name or f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
                
                logger.info(f"Starting incremental backup: {backup_name}")
                
                # Find files that need backup
                files_to_backup = self._find_files_to_backup(source_paths)
                
                if not files_to_backup:
                    logger.info("No files need backup")
                    return {'status': 'no_changes', 'backup_name': backup_name}
                
                # Create backup
                backup_info = self._create_backup(files_to_backup, backup_name, timestamp)
                
                # Update metadata
                self.metadata['backups'].append(backup_info)
                self._save_metadata()
                
                # Cleanup old backups
                self._cleanup_old_backups()
                
                logger.info(f"Backup completed: {backup_name} ({len(files_to_backup)} files)")
                return backup_info
                
            except Exception as e:
                logger.error(f"Error creating backup: {e}")
                raise
    
    def _find_files_to_backup(self, source_paths: List[str]) -> List[Dict[str, Any]]:
        """Find files that need to be backed up."""
        files_to_backup = []
        
        for source_path in source_paths:
            source = Path(source_path)
            
            if not source.exists():
                logger.warning(f"Source path does not exist: {source_path}")
                continue
            
            if source.is_file():
                file_info = self._get_file_info(source)
                if self._needs_backup(file_info):
                    files_to_backup.append(file_info)
            else:
                # Directory - walk recursively
                for root, dirs, files in os.walk(source):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs if not self._is_excluded(d)]
                    
                    for file in files:
                        if self._is_excluded(file):
                            continue
                        
                        file_path = Path(root) / file
                        file_info = self._get_file_info(file_path)
                        
                        if self._needs_backup(file_info):
                            files_to_backup.append(file_info)
        
        return files_to_backup
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information including checksum."""
        try:
            stat = file_path.stat()
            
            # Calculate checksum
            checksum = self._calculate_checksum(file_path)
            
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(Path.cwd())),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'checksum': checksum
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def _needs_backup(self, file_info: Dict[str, Any]) -> bool:
        """Check if file needs backup."""
        if not file_info:
            return False
        
        file_path = file_info['path']
        current_checksum = file_info['checksum']
        
        # Check if file has changed
        stored_checksum = self.metadata['file_checksums'].get(file_path)
        
        if stored_checksum != current_checksum:
            return True
        
        return False
    
    def _is_excluded(self, name: str) -> bool:
        """Check if file/directory should be excluded."""
        import fnmatch
        
        for pattern in self.config['exclude_patterns']:
            if fnmatch.fnmatch(name, pattern):
                return True
        
        return False
    
    def _create_backup(self, files_to_backup: List[Dict[str, Any]], 
                      backup_name: str, timestamp: datetime) -> Dict[str, Any]:
        """Create backup archive."""
        backup_file = self.backup_root / f"{backup_name}.tar.gz"
        
        backup_info = {
            'name': backup_name,
            'timestamp': timestamp.isoformat(),
            'type': 'incremental',
            'file_count': len(files_to_backup),
            'total_size': sum(f['size'] for f in files_to_backup),
            'backup_file': str(backup_file),
            'files': files_to_backup
        }
        
        # Create compressed archive
        with tarfile.open(backup_file, 'w:gz') as tar:
            for file_info in files_to_backup:
                file_path = Path(file_info['path'])
                arcname = file_info['relative_path']
                
                try:
                    tar.add(file_path, arcname=arcname)
                    
                    # Update checksum metadata
                    self.metadata['file_checksums'][file_info['path']] = file_info['checksum']
                    
                except Exception as e:
                    logger.error(f"Error adding file to backup: {file_path} - {e}")
        
        # Upload to storage backend if configured
        if self.storage_backend:
            try:
                remote_path = self.storage_backend.upload_backup(backup_file, backup_name)
                backup_info['remote_path'] = remote_path
                
                # Optionally remove local file after upload
                if self.config.get('remove_local_after_upload', False):
                    backup_file.unlink()
                    backup_info['local_file_removed'] = True
                    
            except Exception as e:
                logger.error(f"Error uploading backup: {e}")
        
        return backup_info
    
    def create_full_backup(self, source_paths: List[str], 
                          backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create full backup (not incremental).
        
        Args:
            source_paths: List of paths to backup
            backup_name: Optional backup name
            
        Returns:
            Backup information
        """
        with self._lock:
            # Clear file checksums to force full backup
            old_checksums = self.metadata['file_checksums'].copy()
            self.metadata['file_checksums'] = {}
            
            try:
                backup_info = self.create_incremental_backup(source_paths, backup_name)
                backup_info['type'] = 'full'
                
                # Update last full backup timestamp
                self.metadata['last_full_backup'] = backup_info['timestamp']
                self._save_metadata()
                
                return backup_info
                
            except Exception as e:
                # Restore checksums on error
                self.metadata['file_checksums'] = old_checksums
                raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        return self.metadata['backups'].copy()
    
    def get_backup_info(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup."""
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                return backup.copy()
        return None
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a specific backup."""
        with self._lock:
            backup_info = self.get_backup_info(backup_name)
            if not backup_info:
                return False
            
            try:
                # Delete local file
                backup_file = Path(backup_info['backup_file'])
                if backup_file.exists():
                    backup_file.unlink()
                
                # Delete from remote storage
                if self.storage_backend and 'remote_path' in backup_info:
                    self.storage_backend.delete_backup(backup_info['remote_path'])
                
                # Remove from metadata
                self.metadata['backups'] = [
                    b for b in self.metadata['backups'] 
                    if b['name'] != backup_name
                ]
                self._save_metadata()
                
                logger.info(f"Deleted backup: {backup_name}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting backup {backup_name}: {e}")
                return False
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        if not self.config.get('retention_days'):
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        backups_to_delete = []
        for backup in self.metadata['backups']:
            backup_date = datetime.fromisoformat(backup['timestamp'])
            if backup_date < cutoff_date:
                backups_to_delete.append(backup['name'])
        
        for backup_name in backups_to_delete:
            self.delete_backup(backup_name)
        
        if backups_to_delete:
            logger.info(f"Cleaned up {len(backups_to_delete)} old backups")
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        backups = self.metadata['backups']
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size': 0,
                'oldest_backup': None,
                'newest_backup': None,
                'storage_usage': 0
            }
        
        total_size = sum(backup.get('total_size', 0) for backup in backups)
        
        backup_dates = [datetime.fromisoformat(b['timestamp']) for b in backups]
        oldest_backup = min(backup_dates)
        newest_backup = max(backup_dates)
        
        return {
            'total_backups': len(backups),
            'total_size': total_size,
            'oldest_backup': oldest_backup.isoformat(),
            'newest_backup': newest_backup.isoformat(),
            'storage_usage': self._calculate_storage_usage(),
            'retention_days': self.config['retention_days']
        }
    
    def _calculate_storage_usage(self) -> int:
        """Calculate total storage usage."""
        total_size = 0
        
        for backup in self.metadata['backups']:
            backup_file = Path(backup['backup_file'])
            if backup_file.exists():
                total_size += backup_file.stat().st_size
        
        return total_size
    
    def verify_backup(self, backup_name: str) -> Dict[str, Any]:
        """Verify backup integrity."""
        backup_info = self.get_backup_info(backup_name)
        if not backup_info:
            return {'status': 'not_found'}
        
        backup_file = Path(backup_info['backup_file'])
        
        # Check if backup file exists
        if not backup_file.exists():
            # Try to download from remote storage
            if self.storage_backend and 'remote_path' in backup_info:
                try:
                    self.storage_backend.download_backup(backup_info['remote_path'], backup_file)
                except Exception as e:
                    return {'status': 'error', 'message': f"Could not download backup: {e}"}
            else:
                return {'status': 'missing'}
        
        # Verify archive integrity
        try:
            with tarfile.open(backup_file, 'r:gz') as tar:
                # Check if all files are present
                members = tar.getmembers()
                expected_files = len(backup_info.get('files', []))
                actual_files = len(members)
                
                if expected_files != actual_files:
                    return {
                        'status': 'corrupt',
                        'message': f"File count mismatch: expected {expected_files}, found {actual_files}"
                    }
                
                # Try to extract a few files to verify
                for member in members[:5]:  # Check first 5 files
                    try:
                        tar.extractfile(member)
                    except Exception as e:
                        return {
                            'status': 'corrupt',
                            'message': f"Could not extract {member.name}: {e}"
                        }
                
                return {'status': 'valid', 'file_count': actual_files}
                
        except Exception as e:
            return {'status': 'error', 'message': f"Archive verification failed: {e}"}
    
    def schedule_backup(self, source_paths: List[str], 
                       schedule_type: str = 'daily',
                       backup_name_prefix: str = 'scheduled') -> Dict[str, Any]:
        """
        Schedule automatic backups.
        
        Args:
            source_paths: Paths to backup
            schedule_type: 'daily', 'weekly', 'monthly'
            backup_name_prefix: Prefix for backup names
            
        Returns:
            Schedule information
        """
        # This would integrate with a job scheduler like cron or celery
        # For now, just return the configuration
        
        schedule_config = {
            'source_paths': source_paths,
            'schedule_type': schedule_type,
            'backup_name_prefix': backup_name_prefix,
            'next_backup': self._calculate_next_backup_time(schedule_type)
        }
        
        return schedule_config
    
    def _calculate_next_backup_time(self, schedule_type: str) -> datetime:
        """Calculate next backup time based on schedule type."""
        now = datetime.now()
        
        if schedule_type == 'daily':
            return now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif schedule_type == 'weekly':
            days_ahead = 6 - now.weekday()  # Sunday
            return now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        elif schedule_type == 'monthly':
            next_month = now.replace(day=1, hour=2, minute=0, second=0, microsecond=0)
            if next_month.month == 12:
                next_month = next_month.replace(year=next_month.year + 1, month=1)
            else:
                next_month = next_month.replace(month=next_month.month + 1)
            return next_month
        
        return now + timedelta(days=1) 