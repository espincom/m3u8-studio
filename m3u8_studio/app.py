import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from .cache import clean_old_cache
from .config import setup_logging
from .mainwindow import MainWindow
from .theme import STYLE


def main():
    setup_logging()
    clean_old_cache()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setWindowIcon(QIcon())
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
