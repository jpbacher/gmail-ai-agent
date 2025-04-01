import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LEVEL = getattr(logging, LOG_LEVEL, logging.INFO)

LOG_DIR = "logs"
LOG_FILE = "app.log"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str = "gmail_ai_agent") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LEVEL)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)

        # File handler (DEBUG+)
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, LOG_FILE),
            maxBytes=1_000_000,
            backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger