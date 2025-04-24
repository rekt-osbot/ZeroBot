"""
Logging configuration for the ZeroBot application
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger():
    """Configure application logging"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Create a unique log file for each run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/zerobot_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                log_file, 
                maxBytes=10485760,  # 10MB
                backupCount=10
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity of third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
