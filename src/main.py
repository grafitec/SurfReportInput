
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database_service import initiate_database
import traceback

# To do
# Make StartPoint working


# Populate friends table
# fixa browse knappen
# Put the gas table into the tab
# Make a total price of the gas and total times i bought
# Add support for mail submission
# Add support for CTX files
# Test out panda and some graphic element
# Make an Anayze button or Analyze tab
# Make pages
# Test maps, folium or plotly maps


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

