"""
Constants and configuration values for the Manalytics application.
This file centralizes hardcoded values that were scattered throughout the codebase.
"""

from typing import Dict

# API URLs and Endpoints
URLS = {
    "MELEE_BASE": "https://melee.gg",
    "MELEE_API": "https://api.melee.gg",
    "MELEE_API_V1": "https://melee.gg/api/v1",
    "MTGO_BASE": "https://www.mtgo.com",
    "SCRYFALL_API": "https://api.scryfall.com",
    "SELENIUM_HUB": "http://chrome:3000/wd/hub",
}

# Network Configuration
NETWORK = {
    "DEFAULT_HOST": "0.0.0.0",
    "DEFAULT_PORT": 8000,
    "SELENIUM_PORT": 3000,
    "DEFAULT_TIMEOUT": 30.0,
    "SCRYFALL_TIMEOUT": 10.0,
    "WEBDRIVER_WAIT_TIMEOUT": 15,
}

# Authentication & Security
AUTH = {
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 60 * 24,  # 24 hours
    "API_KEY_HEADER": "X-API-KEY",
    "TOKEN_URL": "/api/auth/token",
}

# Rate Limits and Pagination
LIMITS = {
    "DEFAULT_PAGE_SIZE": 50,
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_LIMIT": 10,
    "MAX_LIMIT": 50,
    "TOURNAMENT_LIMIT": 10,
    "TOP_STANDINGS": 32,
    "MELEE_PAGE_SIZE": 50,
    "MAX_MELEE_PAGES": 5,
    "VISUALIZATION_LIMIT": 100,
}

# MTG Game Rules
MTG_RULES = {
    "MIN_MAINBOARD_CARDS": 60,
    "MAX_SIDEBOARD_CARDS": 15,
}

# Cache Configuration (in seconds)
CACHE_TTL = {
    "DEFAULT": 3600,  # 1 hour
    "SCRAPER_DEFAULT": 24 * 3600,  # 24 hours
    "MTGO_CACHE": 48 * 3600,  # 48 hours
    "SCRYFALL_CACHE": 7 * 24 * 3600,  # 7 days
}

# Visualization Settings
VISUALIZATION = {
    "DEFAULT_DAYS": 30,
    "MIN_MATCHES": 5,
    "HEATMAP_FIGURE_SIZE": (12, 10),
    "TREND_FIGURE_SIZE": (14, 8),
    "MIRROR_MATCHUP_VALUE": 50.0,
    "HEATMAP_CENTER": 50,
}

# Date Formats
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%m/%d/%Y",
]

# Format Mappings
MTG_FORMATS: Dict[str, str] = {
    "standard": "Standard",
    "modern": "Modern",
    "legacy": "Legacy",
    "vintage": "Vintage",
    "pioneer": "Pioneer",
    "pauper": "Pauper",
    "commander": "Commander",
    "historic": "Historic",
    "explorer": "Explorer",
    "alchemy": "Alchemy",
}

# Melee Format IDs
MELEE_FORMAT_IDS: Dict[str, int] = {
    "standard": 1,
    "modern": 3,
    "legacy": 4,
    "vintage": 5,
    "pioneer": 7,
    "pauper": 8,
}

# CORS Settings (should be restricted in production)
CORS_ALLOW_ORIGINS = ["*"]  # TODO: Restrict this in production