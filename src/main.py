
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database_service import initiate_database
import traceback
from pathlib import Path

# To do
# Add support for mail submission

# fråga ai om att sammanfatta ihop read me
# transfer data from this year
# Test out panda and some graphic element
# Make an Anayze button or Analyze tab
# Make pages
# Test maps, folium or plotly maps


def buildUI():
    # Build database
    initiate_database()

    # Build UI
    app = QApplication(sys.argv)
    style_path = (
            Path(__file__).parent
            / "ui"
            / "theme.qss"
    )
    app.setStyleSheet(style_path.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    app.exec()



if __name__ == '__main__':
    try:
        buildUI()
    except Exception:
        traceback.print_exc()

