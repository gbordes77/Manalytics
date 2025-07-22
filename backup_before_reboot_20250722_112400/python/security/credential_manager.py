"""
Secure credential manager with encryption and rotation capabilities.
"""

import base64
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecureCredentialManager:
    """Secure credential manager with encryption and rotation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize secure credential manager.

        Args:
            config: Configuration including encryption settings
        """
        self.config = {
            "credentials_file": "./credentials/encrypted_credentials.json",
            "master_key_file": "./credentials/master.key",
            "rotation_days": 90,
            "backup_old_credentials": True,
            **config,
        }

        # Ensure credentials directory exists
        self.credentials_dir = Path(self.config["credentials_file"]).parent
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption
        self.encryption_key = self._get_or_create_master_key()
        self.cipher = Fernet(self.encryption_key)

        # Load credentials
        self.credentials = self._load_credentials()

    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key."""
        master_key_path = Path(self.config["master_key_file"])

        if master_key_path.exists():
            try:
                with open(master_key_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading master key: {e}")
                raise
        else:
            # Generate new master key
            key = Fernet.generate_key()

            try:
                with open(master_key_path, "wb") as f:
                    f.write(key)

                # Set restrictive permissions
                os.chmod(master_key_path, 0o600)

                logger.info(f"Generated new master key: {master_key_path}")
                return key

            except Exception as e:
                logger.error(f"Error creating master key: {e}")
                raise

    def _load_credentials(self) -> Dict[str, Any]:
        """Load encrypted credentials."""
        credentials_path = Path(self.config["credentials_file"])

        if not credentials_path.exists():
            return {}

        try:
            with open(credentials_path, "r") as f:
                encrypted_data = json.load(f)

            # Decrypt credentials
            decrypted_credentials = {}
            for service, encrypted_cred in encrypted_data.items():
                if service == "_metadata":
                    decrypted_credentials[service] = encrypted_cred
                else:
                    decrypted_data = self.cipher.decrypt(
                        encrypted_cred["data"].encode()
                    )
                    credential_data = json.loads(decrypted_data.decode())

                    decrypted_credentials[service] = {
                        "data": credential_data,
                        "created_at": encrypted_cred["created_at"],
                        "last_rotated": encrypted_cred.get("last_rotated"),
                        "rotation_due": encrypted_cred.get("rotation_due"),
                    }

            return decrypted_credentials

        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {}

    def _save_credentials(self):
        """Save encrypted credentials."""
        credentials_path = Path(self.config["credentials_file"])

        try:
            # Encrypt credentials
            encrypted_data = {}
            for service, credential in self.credentials.items():
                if service == "_metadata":
                    encrypted_data[service] = credential
                else:
                    # Encrypt the credential data
                    data_json = json.dumps(credential["data"])
                    encrypted_bytes = self.cipher.encrypt(data_json.encode())

                    encrypted_data[service] = {
                        "data": encrypted_bytes.decode(),
                        "created_at": credential["created_at"],
                        "last_rotated": credential.get("last_rotated"),
                        "rotation_due": credential.get("rotation_due"),
                    }

            # Add metadata
            encrypted_data["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_credentials": len(self.credentials) - 1,  # Exclude metadata
            }

            # Write to file
            with open(credentials_path, "w") as f:
                json.dump(encrypted_data, f, indent=2)

            # Set restrictive permissions
            os.chmod(credentials_path, 0o600)

        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            raise

    def store_credential(
        self,
        service: str,
        credential_data: Dict[str, Any],
        rotation_days: Optional[int] = None,
    ) -> bool:
        """
        Store encrypted credential for a service.

        Args:
            service: Service name
            credential_data: Credential data to encrypt
            rotation_days: Days until rotation (optional)

        Returns:
            True if successful
        """
        try:
            now = datetime.now()
            rotation_days = rotation_days or self.config["rotation_days"]

            credential_entry = {
                "data": credential_data,
                "created_at": now.isoformat(),
                "last_rotated": now.isoformat(),
                "rotation_due": (now + timedelta(days=rotation_days)).isoformat(),
            }

            self.credentials[service] = credential_entry
            self._save_credentials()

            logger.info(f"Stored credential for service: {service}")
            return True

        except Exception as e:
            logger.error(f"Error storing credential for {service}: {e}")
            return False

    def get_credential(self, service: str) -> Optional[Dict[str, Any]]:
        """
        Get decrypted credential for a service.

        Args:
            service: Service name

        Returns:
            Credential data or None
        """
        try:
            if service not in self.credentials:
                logger.warning(f"No credential found for service: {service}")
                return None

            credential = self.credentials[service]

            # Check if rotation is due
            if self._is_rotation_due(credential):
                logger.warning(f"Credential rotation due for service: {service}")

            return credential["data"].copy()

        except Exception as e:
            logger.error(f"Error retrieving credential for {service}: {e}")
            return None

    def _is_rotation_due(self, credential: Dict[str, Any]) -> bool:
        """Check if credential rotation is due."""
        if not credential.get("rotation_due"):
            return False

        try:
            rotation_due = datetime.fromisoformat(credential["rotation_due"])
            return datetime.now() >= rotation_due
        except Exception:
            return False

    def rotate_credential(
        self, service: str, new_credential_data: Dict[str, Any]
    ) -> bool:
        """
        Rotate credential for a service.

        Args:
            service: Service name
            new_credential_data: New credential data

        Returns:
            True if successful
        """
        try:
            if service not in self.credentials:
                logger.error(f"Cannot rotate non-existent credential: {service}")
                return False

            # Backup old credential if configured
            if self.config["backup_old_credentials"]:
                self._backup_credential(service)

            # Update credential
            now = datetime.now()
            rotation_days = self.config["rotation_days"]

            self.credentials[service].update(
                {
                    "data": new_credential_data,
                    "last_rotated": now.isoformat(),
                    "rotation_due": (now + timedelta(days=rotation_days)).isoformat(),
                }
            )

            self._save_credentials()

            logger.info(f"Rotated credential for service: {service}")
            return True

        except Exception as e:
            logger.error(f"Error rotating credential for {service}: {e}")
            return False

    def _backup_credential(self, service: str):
        """Backup credential before rotation."""
        try:
            backup_dir = self.credentials_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{service}_{timestamp}.json"

            credential = self.credentials[service]

            # Encrypt backup
            backup_data = {
                "service": service,
                "credential": credential,
                "backup_timestamp": datetime.now().isoformat(),
            }

            encrypted_backup = self.cipher.encrypt(json.dumps(backup_data).encode())

            with open(backup_file, "wb") as f:
                f.write(encrypted_backup)

            os.chmod(backup_file, 0o600)

            logger.debug(f"Backed up credential for {service}")

        except Exception as e:
            logger.error(f"Error backing up credential for {service}: {e}")

    def list_credentials(self) -> List[Dict[str, Any]]:
        """List all stored credentials with metadata."""
        credentials_list = []

        for service, credential in self.credentials.items():
            if service == "_metadata":
                continue

            credentials_list.append(
                {
                    "service": service,
                    "created_at": credential["created_at"],
                    "last_rotated": credential.get("last_rotated"),
                    "rotation_due": credential.get("rotation_due"),
                    "rotation_overdue": self._is_rotation_due(credential),
                }
            )

        return credentials_list

    def delete_credential(self, service: str) -> bool:
        """
        Delete credential for a service.

        Args:
            service: Service name

        Returns:
            True if successful
        """
        try:
            if service not in self.credentials:
                logger.warning(f"No credential to delete for service: {service}")
                return False

            # Backup before deletion
            if self.config["backup_old_credentials"]:
                self._backup_credential(service)

            del self.credentials[service]
            self._save_credentials()

            logger.info(f"Deleted credential for service: {service}")
            return True

        except Exception as e:
            logger.error(f"Error deleting credential for {service}: {e}")
            return False

    def check_rotation_status(self) -> Dict[str, Any]:
        """Check rotation status for all credentials."""
        status = {
            "total_credentials": 0,
            "rotation_due": [],
            "rotation_overdue": [],
            "healthy": [],
        }

        for service, credential in self.credentials.items():
            if service == "_metadata":
                continue

            status["total_credentials"] += 1

            if self._is_rotation_due(credential):
                rotation_due_date = datetime.fromisoformat(credential["rotation_due"])
                days_overdue = (datetime.now() - rotation_due_date).days

                if days_overdue > 0:
                    status["rotation_overdue"].append(
                        {
                            "service": service,
                            "days_overdue": days_overdue,
                            "rotation_due": credential["rotation_due"],
                        }
                    )
                else:
                    status["rotation_due"].append(
                        {"service": service, "rotation_due": credential["rotation_due"]}
                    )
            else:
                status["healthy"].append(service)

        return status

    def auto_rotate_credentials(
        self, rotation_handlers: Dict[str, callable]
    ) -> Dict[str, Any]:
        """
        Automatically rotate credentials that are due.

        Args:
            rotation_handlers: Dict mapping service names to rotation functions

        Returns:
            Rotation results
        """
        results = {"rotated": [], "failed": [], "skipped": []}

        rotation_status = self.check_rotation_status()

        for overdue_cred in rotation_status["rotation_overdue"]:
            service = overdue_cred["service"]

            if service in rotation_handlers:
                try:
                    # Call rotation handler
                    new_credential = rotation_handlers[service]()

                    if new_credential:
                        success = self.rotate_credential(service, new_credential)
                        if success:
                            results["rotated"].append(service)
                        else:
                            results["failed"].append(service)
                    else:
                        results["failed"].append(service)

                except Exception as e:
                    logger.error(f"Error in auto-rotation for {service}: {e}")
                    results["failed"].append(service)
            else:
                results["skipped"].append(service)

        return results

    def export_credentials(
        self, services: List[str], export_path: str, include_metadata: bool = True
    ) -> bool:
        """
        Export credentials to encrypted file.

        Args:
            services: List of services to export
            export_path: Path for export file
            include_metadata: Whether to include metadata

        Returns:
            True if successful
        """
        try:
            export_data = {}

            for service in services:
                if service in self.credentials:
                    export_data[service] = self.credentials[service]

            if include_metadata:
                export_data["_export_metadata"] = {
                    "exported_at": datetime.now().isoformat(),
                    "exported_services": services,
                    "total_exported": len(export_data),
                }

            # Encrypt export data
            encrypted_export = self.cipher.encrypt(json.dumps(export_data).encode())

            with open(export_path, "wb") as f:
                f.write(encrypted_export)

            os.chmod(export_path, 0o600)

            logger.info(f"Exported {len(export_data)} credentials to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting credentials: {e}")
            return False

    def import_credentials(
        self, import_path: str, overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import credentials from encrypted file.

        Args:
            import_path: Path to import file
            overwrite: Whether to overwrite existing credentials

        Returns:
            Import results
        """
        results = {"imported": [], "skipped": [], "failed": []}

        try:
            with open(import_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt import data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            import_data = json.loads(decrypted_data.decode())

            for service, credential_data in import_data.items():
                if service.startswith("_"):  # Skip metadata
                    continue

                if service in self.credentials and not overwrite:
                    results["skipped"].append(service)
                    continue

                try:
                    self.credentials[service] = credential_data
                    results["imported"].append(service)
                except Exception as e:
                    logger.error(f"Error importing credential for {service}: {e}")
                    results["failed"].append(service)

            if results["imported"]:
                self._save_credentials()

            logger.info(
                f"Import completed: {len(results['imported'])} imported, "
                f"{len(results['skipped'])} skipped, {len(results['failed'])} failed"
            )

            return results

        except Exception as e:
            logger.error(f"Error importing credentials: {e}")
            return results

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring."""
        metrics = {
            "total_credentials": len(self.credentials) - 1,  # Exclude metadata
            "credentials_due_rotation": 0,
            "credentials_overdue_rotation": 0,
            "average_age_days": 0,
            "oldest_credential_age_days": 0,
            "newest_credential_age_days": 0,
        }

        if not self.credentials:
            return metrics

        ages = []
        now = datetime.now()

        for service, credential in self.credentials.items():
            if service == "_metadata":
                continue

            created_at = datetime.fromisoformat(credential["created_at"])
            age_days = (now - created_at).days
            ages.append(age_days)

            if self._is_rotation_due(credential):
                rotation_due = datetime.fromisoformat(credential["rotation_due"])
                if now > rotation_due:
                    metrics["credentials_overdue_rotation"] += 1
                else:
                    metrics["credentials_due_rotation"] += 1

        if ages:
            metrics["average_age_days"] = sum(ages) / len(ages)
            metrics["oldest_credential_age_days"] = max(ages)
            metrics["newest_credential_age_days"] = min(ages)

        return metrics
