# src/logger.py
import logging
import os

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

def get_logger(name: str = __name__, log_file: str = "logs/run.log") -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name: Logger name
        log_file: Path to the log file
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if logger is called multiple times
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handlers
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
