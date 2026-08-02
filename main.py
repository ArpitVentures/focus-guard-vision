import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.logger import logger


def main():
    logger.info("Launching FocusGuard Studio...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
