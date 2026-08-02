"""
FocusGuard AI - System Configuration Settings
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = "FocusGuard Studio"
APP_VERSION = "1.0.0"

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
SOUNDS_DIR = ASSETS_DIR / "sounds"