"""
FocusGuard AI - Centralized Settings and Configurations
"""
from pathlib import Path

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Camera Hardware Configs
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS_TARGET = 30

# Product & UI Metadata
APP_NAME = "FocusGuard AI - Distraction Tracker Studio"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800