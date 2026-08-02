"""
FocusGuard AI - System Configuration Settings
"""
from pathlib import Path

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Settings
APP_NAME = "FocusGuard Studio"
APP_VERSION = "1.0.0"

# Camera Hardware Defaults
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Storage Directories
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
