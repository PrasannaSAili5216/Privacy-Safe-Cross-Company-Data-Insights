import logging
import sys
from typing import Optional

def setup_logger(name: str = "privacy_insights", log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configures and returns a logger instance.

    Args:
        name (str): Name of the logger.
        log_level (int): Logging level (default: logging.INFO).
        log_file (Optional[str]): Path to a log file. If None, logs only to console.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (Optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
