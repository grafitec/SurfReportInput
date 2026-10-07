
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database_service import initiate_database
import traceback

def buildUI():
    # Build database
    initiate_database()

    # Build UI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()



if __name__ == '__main__':
    try:
        buildUI()
    except Exception:
        traceback.print_exc()

