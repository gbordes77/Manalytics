"""Configuration settings for Manalytics."""

SETTINGS = {
    "scraping": {
        "timeout": 30,
        "max_retries": 3,
        "delay_between_requests": 1.0,
        "user_agent": "Manalytics/1.0"
    },
    "classification": {
        "min_cards_for_archetype": 10,
        "confidence_threshold": 0.8
    },
    "analysis": {
        "min_matches_for_stats": 20,
        "confidence_level": 0.95
    },
    "visualization": {
        "theme": "plotly_dark",
        "figure_height": 600,
        "figure_width": 1000
    }
}

# Cache settings
CACHE_SETTINGS = {
    "dir": "/tmp/manalytics_cache",
    "ttl": 3600,  # 1 hour
    "max_size": 1000
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 