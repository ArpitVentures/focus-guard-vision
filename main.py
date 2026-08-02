"""
FocusGuard AI - Desktop Application Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.logger import logger


def main():
    logger.info("Launching FocusGuard AI Desktop Studio Application...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
