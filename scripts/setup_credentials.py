#!/usr/bin/env python3
"""
🔐 Manalytics Credentials Setup Helper

This script helps you configure your credentials securely for Manalytics.
It guides you through creating a .env file with all necessary secrets.
"""

import os
import sys
import getpass
import secrets
from pathlib import Path
from typing import Optional
import json
import shutil

class CredentialsSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.env_file = self.root_dir / '.env'
        self.env_example = self.root_dir / '.env.example'
        self.old_credentials_dir = self.root_dir / 'api_credentials'
        
    def run(self):
        """Main setup flow"""
        print("🔐 Manalytics Credentials Setup")
        print("=" * 50)
        
        # Check if .env already exists
        if self.env_file.exists():
            print("⚠️  .env file already exists!")
            overwrite = input("Do you want to overwrite it? (y/N): ").lower()
            if overwrite != 'y':
                print("❌ Setup cancelled.")
                return
                
        # Start setup
        print("\n📋 Let's configure your credentials...")
        print("Press Enter to use default values (shown in brackets)\n")
        
        config = {}
        
        # Application Settings
        print("=== Application Settings ===")
        config['APP_NAME'] = self._prompt("App Name", "Manalytics")
        config['VERSION'] = self._prompt("Version", "1.0.0")
        config['DEBUG'] = self._prompt("Debug Mode (true/false)", "false")
        config['LOG_LEVEL'] = self._prompt("Log Level", "INFO")
        
        # Security Keys
        print("\n=== Security Keys ===")
        print("🔑 Generating secure keys...")
        config['SECRET_KEY'] = secrets.token_urlsafe(32)
        config['API_KEY'] = secrets.token_urlsafe(32)
        print("✅ Secure keys generated!")
        
        # Database
        print("\n=== Database Configuration ===")
        config['DATABASE_URL'] = self._prompt(
            "PostgreSQL URL",
            "postgresql://manalytics:changeme@localhost:5432/manalytics"
        )
        
        # Redis
        print("\n=== Redis Cache (Optional) ===")
        config['REDIS_URL'] = self._prompt("Redis URL (leave empty to skip)", "")
        
        # MTGO Settings
        print("\n=== MTGO Scraping ===")
        config['MTGO_BASE_URL'] = self._prompt("MTGO Base URL", "https://magic.wizards.com")
        config['MTGO_RATE_LIMIT'] = self._prompt("MTGO Rate Limit", "2")
        
        # Melee Settings
        print("\n=== Melee.gg Credentials ===")
        
        # Try to import from old files
        imported = self._try_import_melee_credentials()
        if imported:
            print("✅ Found existing Melee credentials!")
            use_existing = input("Use existing credentials? (Y/n): ").lower()
            if use_existing != 'n':
                config['MELEE_EMAIL'] = imported['email']
                config['MELEE_PASSWORD'] = imported['password']
            else:
                config['MELEE_EMAIL'] = input("Melee Email: ")
                config['MELEE_PASSWORD'] = getpass.getpass("Melee Password: ")
        else:
            config['MELEE_EMAIL'] = input("Melee Email: ")
            config['MELEE_PASSWORD'] = getpass.getpass("Melee Password: ")
            
        config['MELEE_BASE_URL'] = self._prompt("Melee Base URL", "https://melee.gg")
        config['MELEE_RATE_LIMIT'] = self._prompt("Melee Rate Limit", "5")
        
        # Other Settings
        print("\n=== Other Settings ===")
        config['SCRYFALL_RATE_LIMIT'] = self._prompt("Scryfall Rate Limit", "10")
        config['ENABLED_FORMATS'] = self._prompt(
            "Enabled Formats", 
            "standard,modern,legacy,pioneer,pauper,vintage"
        )
        config['ENABLED_SCRAPERS'] = self._prompt("Enabled Scrapers", "mtgo,melee")
        
        # JWT Settings
        config['ACCESS_TOKEN_EXPIRE_MINUTES'] = self._prompt("JWT Access Token Expiry (minutes)", "30")
        config['REFRESH_TOKEN_EXPIRE_DAYS'] = self._prompt("JWT Refresh Token Expiry (days)", "7")
        
        # CORS
        config['CORS_ORIGINS'] = self._prompt(
            "CORS Origins",
            "http://localhost:3000,http://localhost:8000"
        )
        
        # Write .env file
        print("\n📝 Writing .env file...")
        self._write_env_file(config)
        
        # Secure permissions
        print("🔒 Setting secure permissions...")
        os.chmod(self.env_file, 0o600)
        
        # Clean up old credentials
        if self.old_credentials_dir.exists():
            print("\n🧹 Cleaning up old credentials...")
            cleanup = input("Remove old api_credentials directory? (y/N): ").lower()
            if cleanup == 'y':
                self._secure_delete_directory(self.old_credentials_dir)
                print("✅ Old credentials removed securely")
        
        print("\n✨ Setup complete!")
        print(f"✅ Created: {self.env_file}")
        print("\n⚠️  IMPORTANT:")
        print("  - NEVER commit .env to version control")
        print("  - Keep your .env file secure")
        print("  - Backup your credentials safely")
        
        # Offer to test connection
        print("\n🧪 Would you like to test your credentials?")
        test = input("Test Melee connection? (y/N): ").lower()
        if test == 'y':
            self._test_melee_connection(config['MELEE_EMAIL'], config['MELEE_PASSWORD'])
            
    def _prompt(self, message: str, default: str = "") -> str:
        """Prompt user for input with default value"""
        if default:
            value = input(f"{message} [{default}]: ").strip()
            return value or default
        else:
            return input(f"{message}: ").strip()
            
    def _try_import_melee_credentials(self) -> Optional[dict]:
        """Try to import existing Melee credentials"""
        possible_paths = [
            self.old_credentials_dir / 'melee_login.json',
            self.root_dir / 'Api_token_and_login' / 'melee_login.json',
            self.root_dir / 'melee_login.json'
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        return {
                            'email': data.get('login', data.get('email', '')),
                            'password': data.get('mdp', data.get('password', ''))
                        }
                except Exception:
                    continue
                    
        return None
        
    def _write_env_file(self, config: dict):
        """Write configuration to .env file"""
        lines = []
        
        # Read template from .env.example
        if self.env_example.exists():
            with open(self.env_example, 'r') as f:
                template = f.read()
                
            # Replace placeholders with actual values
            for key, value in config.items():
                if value:  # Only write non-empty values
                    # Find the key in template and replace its value
                    import re
                    pattern = f"^{key}=.*$"
                    replacement = f"{key}={value}"
                    template = re.sub(pattern, replacement, template, flags=re.MULTILINE)
                    
            with open(self.env_file, 'w') as f:
                f.write(template)
        else:
            # Fallback: write simple format
            with open(self.env_file, 'w') as f:
                f.write("# Manalytics Environment Configuration\n")
                f.write("# Generated by setup_credentials.py\n\n")
                
                for key, value in config.items():
                    if value:
                        f.write(f"{key}={value}\n")
                        
    def _secure_delete_directory(self, directory: Path):
        """Securely delete a directory and its contents"""
        try:
            # First, overwrite all files with random data
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    # Overwrite with random data
                    size = file_path.stat().st_size
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(size))
                        
            # Then remove the directory
            shutil.rmtree(directory)
        except Exception as e:
            print(f"⚠️  Warning: Could not fully secure delete: {e}")
            
    def _test_melee_connection(self, email: str, password: str):
        """Test Melee credentials"""
        print("\n🧪 Testing Melee connection...")
        try:
            import requests
            
            session = requests.Session()
            login_url = "https://melee.gg/Account/Login"
            
            # Get login page for CSRF token
            response = session.get(login_url)
            if response.status_code == 200:
                print("✅ Connected to Melee.gg")
                print("⚠️  Full authentication test requires CSRF token extraction")
                print("   Run scrapers to fully test credentials")
            else:
                print("❌ Could not connect to Melee.gg")
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            

if __name__ == "__main__":
    setup = CredentialsSetup()
    setup.run()