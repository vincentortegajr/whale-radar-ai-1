"""Logging configuration for WhaleRadar.ai"""

import logging
import colorlog
from datetime import datetime
import os
from src.utils.config import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure color logging
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Configure file logging
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def setup_logger(name: str) -> logging.Logger:
    """Set up logger with both console and file handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_filename = f"logs/whaleradar_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Prevent duplicate logging
    logger.propagate = False
    
    return logger

# Create main logger
logger = setup_logger("WhaleRadar")