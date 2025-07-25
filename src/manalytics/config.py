"""
Centralized configuration for Manalytics
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "output"

# Ensure directories exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/manalytics")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Scraping Configuration
MTGO_BASE_URL = os.getenv("MTGO_BASE_URL", "https://magic.wizards.com")
MELEE_BASE_URL = os.getenv("MELEE_BASE_URL", "https://melee.gg")

# Melee Credentials
MELEE_EMAIL = os.getenv("MELEE_EMAIL")
MELEE_PASSWORD = os.getenv("MELEE_PASSWORD")

# Rate Limits
SCRYFALL_RATE_LIMIT = int(os.getenv("SCRYFALL_RATE_LIMIT", "10"))
MTGO_RATE_LIMIT = int(os.getenv("MTGO_RATE_LIMIT", "2"))
MELEE_RATE_LIMIT = int(os.getenv("MELEE_RATE_LIMIT", "5"))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
API_KEY = os.getenv("API_KEY", "change-me-in-production")

# Features
ENABLED_FORMATS = os.getenv("ENABLED_FORMATS", "standard,modern,legacy,pioneer,pauper,vintage").split(",")
ENABLED_SCRAPERS = os.getenv("ENABLED_SCRAPERS", "mtgo,melee").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"