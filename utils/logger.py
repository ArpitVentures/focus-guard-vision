"""
FocusGuard AI - Logging Engine
"""
import logging
import sys
from config.settings import LOGS_DIR

def setup_logger(name: str = "FocusGuard") -> logging.Logger:
    """Configures and returns a custom logger instance."""
    app_logger = logging.getLogger(name)
    app_logger.setLevel(logging.DEBUG)

    if app_logger.handlers:
        return app_logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)

    return app_logger

logger = setup_logger()