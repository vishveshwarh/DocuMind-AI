# Centralised logging setup
# Logs to both console and file simultaneously
# Every module imports get_logger(__name__) to get its own named logger

import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import settings

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

    # Log format — timestamp | level | module | message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — shows logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler — writes logs to logs/app.log
    # RotatingFileHandler: creates new file when size exceeds 5MB, keeps last 3 files
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    log_path = os.path.join(settings.LOG_DIR, settings.LOG_FILE)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,   # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger