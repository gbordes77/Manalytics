from pydantic import BaseSettings, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import os
from pathlib import Path

class Environment(str, Enum):
    """Environnements supportés"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Niveaux de log supportés"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseConfig(BaseSettings):
    """Configuration base de données et cache"""
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(0, env="REDIS_DB")
    redis_max_connections: int = Field(10, env="REDIS_MAX_CONNECTIONS")
    
    # Configuration connexion
    socket_timeout: float = Field(5.0, env="DB_SOCKET_TIMEOUT")
    socket_connect_timeout: float = Field(5.0, env="DB_SOCKET_CONNECT_TIMEOUT")
    retry_on_timeout: bool = Field(True, env="DB_RETRY_ON_TIMEOUT")
    
    # Health check
    health_check_interval: int = Field(30, env="DB_HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_prefix = "DB_"

class APIConfig(BaseSettings):
    """Configuration API FastAPI"""
    
    # Métadonnées
    title: str = Field("Manalytics API", env="API_TITLE")
    version: str = Field("2.0.0", env="API_VERSION")
    description: str = Field("MTG Metagame Analysis Platform", env="API_DESCRIPTION")
    
    # Sécurité
    cors_origins: List[str] = Field(
        default_factory=lambda: ["https://manalytics.app"],
        env="API_CORS_ORIGINS"
    )
    
    # JWT
    jwt_secret: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(30, env="JWT_EXPIRE_MINUTES")
    
    # Rate limiting
    rate_limit_requests: int = Field(100, env="API_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="API_RATE_LIMIT_WINDOW")
    
    # Server
    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    workers: int = Field(1, env="API_WORKERS")
    
    # Timeouts
    request_timeout: int = Field(30, env="API_REQUEST_TIMEOUT")
    max_request_size: int = Field(1024 * 1024, env="API_MAX_REQUEST_SIZE")  # 1MB
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(',')]
        return v
    
    class Config:
        env_prefix = "API_"

class CacheConfig(BaseSettings):
    """Configuration cache intelligent"""
    
    # TTL par défaut
    default_ttl: int = Field(3600, env="CACHE_DEFAULT_TTL")
    
    # L1 Cache (mémoire)
    l1_max_memory_mb: int = Field(100, env="CACHE_L1_MAX_MEMORY_MB")
    l1_enabled: bool = Field(True, env="CACHE_L1_ENABLED")
    
    # L2 Cache (Redis)
    l2_enabled: bool = Field(True, env="CACHE_L2_ENABLED")
    
    # Compression
    enable_compression: bool = Field(True, env="CACHE_COMPRESSION_ENABLED")
    compression_threshold: int = Field(1024, env="CACHE_COMPRESSION_THRESHOLD")
    compression_min_ratio: float = Field(0.9, env="CACHE_COMPRESSION_MIN_RATIO")
    
    # Prefetch
    enable_prefetch: bool = Field(True, env="CACHE_PREFETCH_ENABLED")
    prefetch_queue_size: int = Field(100, env="CACHE_PREFETCH_QUEUE_SIZE")
    
    # Métriques
    enable_metrics: bool = Field(True, env="CACHE_METRICS_ENABLED")
    metrics_interval: int = Field(60, env="CACHE_METRICS_INTERVAL")
    
    class Config:
        env_prefix = "CACHE_"

class PerformanceConfig(BaseSettings):
    """Configuration performance et parallélisation"""
    
    # Workers
    max_workers: int = Field(4, env="PERF_MAX_WORKERS")
    
    # Timeouts
    request_timeout: int = Field(30, env="PERF_REQUEST_TIMEOUT")
    pipeline_timeout: int = Field(120, env="PERF_PIPELINE_TIMEOUT")
    
    # Retry
    max_retries: int = Field(3, env="PERF_MAX_RETRIES")
    retry_delay: float = Field(1.0, env="PERF_RETRY_DELAY")
    
    # Batch processing
    batch_size: int = Field(100, env="PERF_BATCH_SIZE")
    chunk_size: int = Field(50, env="PERF_CHUNK_SIZE")
    
    # Parallélisation
    parallel_enabled: bool = Field(True, env="PERF_PARALLEL_ENABLED")
    parallel_data_loading: bool = Field(True, env="PERF_PARALLEL_DATA_LOADING")
    parallel_classification: bool = Field(True, env="PERF_PARALLEL_CLASSIFICATION")
    parallel_visualization: bool = Field(True, env="PERF_PARALLEL_VISUALIZATION")
    
    # Objectifs performance
    target_pipeline_time: float = Field(1.0, env="PERF_TARGET_PIPELINE_TIME")
    target_cache_hit_rate: float = Field(0.8, env="PERF_TARGET_CACHE_HIT_RATE")
    
    class Config:
        env_prefix = "PERF_"

class MTGConfig(BaseSettings):
    """Configuration spécifique MTG"""
    
    # Formats supportés
    supported_formats: List[str] = Field(
        default_factory=lambda: ["Standard", "Modern", "Legacy", "Pioneer", "Pauper"],
        env="MTG_FORMATS"
    )
    
    # Règles deck
    min_deck_size: int = Field(60, env="MTG_MIN_DECK_SIZE")
    max_deck_size: int = Field(75, env="MTG_MAX_DECK_SIZE")
    max_sideboard_size: int = Field(15, env="MTG_MAX_SIDEBOARD")
    
    # Classification
    archetype_confidence_threshold: float = Field(0.7, env="MTG_ARCHETYPE_THRESHOLD")
    max_archetypes_display: int = Field(12, env="MTG_MAX_ARCHETYPES_DISPLAY")
    
    # Couleurs
    color_system_enabled: bool = Field(True, env="MTG_COLOR_SYSTEM_ENABLED")
    color_accessibility: bool = Field(True, env="MTG_COLOR_ACCESSIBILITY")
    
    # Données
    min_sample_size: int = Field(10, env="MTG_MIN_SAMPLE_SIZE")
    max_tournaments_per_analysis: int = Field(1000, env="MTG_MAX_TOURNAMENTS")
    
    @validator('supported_formats', pre=True)
    def parse_formats(cls, v):
        if isinstance(v, str):
            return [f.strip() for f in v.split(',')]
        return v
    
    @validator('archetype_confidence_threshold')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence threshold must be between 0 and 1')
        return v
    
    class Config:
        env_prefix = "MTG_"

class SecurityConfig(BaseSettings):
    """Configuration sécurité"""
    
    # Monitoring
    enable_monitoring: bool = Field(True, env="SECURITY_MONITORING_ENABLED")
    
    # Blocage IP
    failed_attempts_threshold: int = Field(5, env="SECURITY_FAILED_ATTEMPTS_THRESHOLD")
    block_duration_minutes: int = Field(60, env="SECURITY_BLOCK_DURATION_MINUTES")
    monitoring_window_seconds: int = Field(300, env="SECURITY_MONITORING_WINDOW")
    
    # Rate limiting
    requests_per_minute: int = Field(60, env="SECURITY_REQUESTS_PER_MINUTE")
    
    # Patterns suspects
    enable_content_analysis: bool = Field(True, env="SECURITY_CONTENT_ANALYSIS")
    
    # Persistance
    enable_persistence: bool = Field(True, env="SECURITY_PERSISTENCE_ENABLED")
    
    class Config:
        env_prefix = "SECURITY_"

class LoggingConfig(BaseSettings):
    """Configuration logging"""
    
    # Niveau global
    log_level: LogLevel = Field(LogLevel.INFO, env="LOG_LEVEL")
    
    # Fichiers
    log_dir: str = Field("logs", env="LOG_DIR")
    enable_file_logging: bool = Field(True, env="LOG_FILE_ENABLED")
    enable_console_logging: bool = Field(True, env="LOG_CONSOLE_ENABLED")
    
    # Format
    enable_json: bool = Field(False, env="LOG_JSON_ENABLED")
    enable_colors: bool = Field(True, env="LOG_COLORS_ENABLED")
    
    # Rotation
    max_file_size_mb: int = Field(10, env="LOG_MAX_FILE_SIZE_MB")
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT")
    
    # Loggers spécialisés
    performance_logging: bool = Field(True, env="LOG_PERFORMANCE_ENABLED")
    security_logging: bool = Field(True, env="LOG_SECURITY_ENABLED")
    
    class Config:
        env_prefix = "LOG_"

class Settings(BaseSettings):
    """Configuration principale Manalytics"""
    
    # Environment
    environment: Environment = Field(Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    testing: bool = Field(False, env="TESTING")
    
    # Version
    version: str = Field("2.0.0", env="VERSION")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Optional[Path] = Field(None, env="DATA_DIR")
    output_dir: Optional[Path] = Field(None, env="OUTPUT_DIR")
    log_dir: Optional[Path] = Field(None, env="LOG_DIR")
    mtgo_data_path: Optional[Path] = Field(None, env="MTGO_DATA_PATH")
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    api: APIConfig = APIConfig()
    cache: CacheConfig = CacheConfig()
    performance: PerformanceConfig = PerformanceConfig()
    mtg: MTGConfig = MTGConfig()
    security: SecurityConfig = SecurityConfig()
    logging: LoggingConfig = LoggingConfig()
    
    # Feature flags
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "advanced_analytics": True,
        "realtime_updates": False,
        "experimental_classifiers": False,
        "api_v2": True,
        "parallel_processing": True,
        "smart_cache": True,
        "security_monitoring": True,
        "structured_logging": True
    })
    
    # Monitoring
    enable_monitoring: bool = Field(True, env="MONITORING_ENABLED")
    metrics_collection: bool = Field(True, env="METRICS_COLLECTION_ENABLED")
    
    @validator('environment', pre=True)
    def parse_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator('data_dir', 'output_dir', 'log_dir', 'mtgo_data_path', pre=True)
    def parse_paths(cls, v, values):
        if v is None:
            return None
        if isinstance(v, str):
            # Relative au base_dir si pas absolu
            path = Path(v)
            if not path.is_absolute():
                base_dir = values.get('base_dir', Path.cwd())
                return base_dir / path
            return path
        return v
    
    @validator('features', pre=True)
    def parse_features(cls, v):
        if isinstance(v, str):
            # Support format "feature1=true,feature2=false"
            features = {}
            for item in v.split(','):
                if '=' in item:
                    key, value = item.split('=', 1)
                    features[key.strip()] = value.strip().lower() in ('true', '1', 'yes', 'on')
            return features
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Valeurs par défaut si non spécifiées
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.output_dir is None:
            self.output_dir = self.base_dir / "Analyses"
        if self.log_dir is None:
            self.log_dir = self.base_dir / "logs"
        if self.mtgo_data_path is None:
            self.mtgo_data_path = self.base_dir / "MTGOFormatData"
        
        # Créer les répertoires nécessaires
        for dir_path in [self.data_dir, self.output_dir, self.log_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Ajuster config logging selon environnement
        if self.environment == Environment.PRODUCTION:
            self.logging.enable_json = True
            self.logging.enable_colors = False
            self.logging.log_level = LogLevel.INFO
        elif self.environment == Environment.DEVELOPMENT:
            self.logging.enable_json = False
            self.logging.enable_colors = True
            self.logging.log_level = LogLevel.DEBUG if self.debug else LogLevel.INFO
    
    # Propriétés utilitaires
    
    @property
    def is_production(self) -> bool:
        """Vérifier si en production"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Vérifier si en développement"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Vérifier si en test"""
        return self.testing
    
    def get_redis_url(self) -> str:
        """URL Redis complète avec authentification"""
        if self.database.redis_password:
            parts = self.database.redis_url.split('://')
            if len(parts) == 2:
                return f"{parts[0]}://:{self.database.redis_password}@{parts[1]}"
        return self.database.redis_url
    
    def get_log_config(self) -> Dict[str, Any]:
        """Configuration logging complète"""
        return {
            "level": self.logging.log_level.value,
            "dir": str(self.log_dir),
            "json": self.logging.enable_json,
            "colors": self.logging.enable_colors,
            "file_enabled": self.logging.enable_file_logging,
            "console_enabled": self.logging.enable_console_logging,
            "max_size_mb": self.logging.max_file_size_mb,
            "backup_count": self.logging.backup_count
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Configuration performance complète"""
        return {
            "max_workers": self.performance.max_workers,
            "parallel_enabled": self.performance.parallel_enabled,
            "target_pipeline_time": self.performance.target_pipeline_time,
            "target_cache_hit_rate": self.performance.target_cache_hit_rate,
            "batch_size": self.performance.batch_size,
            "chunk_size": self.performance.chunk_size
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Configuration sécurité complète"""
        return {
            "monitoring_enabled": self.security.enable_monitoring,
            "failed_attempts_threshold": self.security.failed_attempts_threshold,
            "block_duration_minutes": self.security.block_duration_minutes,
            "requests_per_minute": self.security.requests_per_minute,
            "content_analysis": self.security.enable_content_analysis
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Vérifier si une feature est activée"""
        return self.features.get(feature_name, False)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Informations d'environnement"""
        return {
            "environment": self.environment.value,
            "version": self.version,
            "debug": self.debug,
            "testing": self.testing,
            "base_dir": str(self.base_dir),
            "data_dir": str(self.data_dir),
            "output_dir": str(self.output_dir),
            "log_dir": str(self.log_dir)
        }
    
    def validate_configuration(self) -> List[str]:
        """Valider la configuration et retourner les erreurs"""
        errors = []
        
        # Vérifier JWT secret en production
        if self.is_production and len(self.api.jwt_secret) < 32:
            errors.append("JWT secret too short for production")
        
        # Vérifier paths
        if not self.mtgo_data_path.exists():
            errors.append(f"MTGO data path does not exist: {self.mtgo_data_path}")
        
        # Vérifier cohérence performance
        if self.performance.target_pipeline_time < 0.1:
            errors.append("Target pipeline time too low")
        
        if self.performance.target_cache_hit_rate < 0.1 or self.performance.target_cache_hit_rate > 1.0:
            errors.append("Invalid cache hit rate target")
        
        # Vérifier sécurité
        if self.security.failed_attempts_threshold < 1:
            errors.append("Failed attempts threshold too low")
        
        return errors
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        validate_assignment = True

# Singleton
_settings: Optional[Settings] = None

def get_settings(reload: bool = False) -> Settings:
    """Obtenir instance settings (singleton)"""
    global _settings
    if _settings is None or reload:
        _settings = Settings()
    return _settings

def reload_settings():
    """Recharger la configuration"""
    global _settings
    _settings = None
    return get_settings()

# Alias pour import facile
settings = get_settings() 