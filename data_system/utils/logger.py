import logging
import sys
from pathlib import Path

# Cấu hình logger cho data_system
def setup_logger(name: str = "data_system", level: int = logging.CRITICAL, log_file: str = None) -> logging.Logger:
    """
    Setup a logger with console and optional file handler.
    Note: Level is set to CRITICAL to suppress most logging (Windows encoding issues)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent propagation to root logger

    # Only add handlers if file is specified (for debugging)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use UTF-8 encoding for file handler to avoid encoding issues
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Global logger instance - disable all logging to avoid Windows encoding issues
logger = setup_logger()

