# config/logging_config.py - Enhanced logging configuration

import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import settings

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    COLORS = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.grey)
        record.levelname = f"{log_color}{record.levelname}{self.reset}"
        return super().format(record)

def setup_logging():
    """Configures the root logger with enhanced features."""
    
    # Create logs directory if it doesn't exist
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Remove all existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Set base log level
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
    
    if sys.stdout.isatty():  # Use colors only in terminal
        console_handler.setFormatter(ColoredFormatter(console_format))
    else:
        console_handler.setFormatter(logging.Formatter(console_format))
    
    root_logger.addHandler(console_handler)
    
    # File handler for persistent logs
    if not settings.DEBUG:
        file_handler = logging.FileHandler(
            log_dir / f"manalytics_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_format = "%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    
    # Special handling for database logs
    db_logger = logging.getLogger("database")
    if settings.DEBUG:
        db_logger.setLevel(logging.DEBUG)
    else:
        db_logger.setLevel(logging.INFO)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    
    return root_logger

# Performance logging decorator
def log_performance(func):
    """Decorator to log function execution time."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if elapsed > 1.0:  # Log only slow operations
                logger.warning(
                    f"{func.__name__} took {elapsed:.2f}s to execute"
                )
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}"
            )
            raise
    
    return wrapper

# Async version of the performance decorator
def log_async_performance(func):
    """Decorator to log async function execution time."""
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if elapsed > 1.0:  # Log only slow operations
                logger.warning(
                    f"{func.__name__} took {elapsed:.2f}s to execute"
                )
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}"
            )
            raise
    
    return wrapper

# Initialize logging on module import
setup_logging()