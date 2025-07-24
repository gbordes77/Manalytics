from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='allow')

    # Application
    APP_NAME: str = "Manalytics"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str
    API_KEY: str

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: Optional[str] = None

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    RULES_DIR: Path = BASE_DIR / "database" / "seed_data" / "rules"

    # Scraping
    MTGO_BASE_URL: str = "https://magic.wizards.com"
    MELEE_BASE_URL: str = "https://melee.gg"
    MELEE_EMAIL: str
    MELEE_PASSWORD: str

    # Rate Limiting
    SCRYFALL_RATE_LIMIT: int = 10
    MTGO_RATE_LIMIT: int = 2
    MELEE_RATE_LIMIT: int = 5

    # Enabled Features
    ENABLED_FORMATS: List[str] = ["standard", "modern", "legacy", "pioneer", "pauper", "vintage"]
    ENABLED_SCRAPERS: List[str] = ["mtgo", "melee"]

    def ensure_directories(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        (self.DATA_DIR / "raw").mkdir(exist_ok=True)
        (self.DATA_DIR / "processed").mkdir(exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.RULES_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()