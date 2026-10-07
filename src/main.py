
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def buildUI():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    buildUI()

