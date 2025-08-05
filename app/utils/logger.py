"""
Logging configuration for the application
"""
import logging
import sys
from pathlib import Path
import structlog
from pythonjsonlogger import jsonlogger

from app.config import settings

def setup_logging(name: str) -> logging.Logger:
    """Setup structured logging"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(settings.log_file)
    file_handler.setLevel(logging.INFO)
    
    # JSON formatter for structured logs
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Apply formatters
    console_handler.setFormatter(json_formatter)
    file_handler.setFormatter(json_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
