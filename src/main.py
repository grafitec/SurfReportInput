
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database_service import initiate_database
import traceback
from pathlib import Path

# To do
# Tabeller
# Kunna filtrera på rubrikerna
# Annan typsnitt
# en process för instagram länkar
# Ta emot epost från TCX och lägga in den
# Windows när man bara importerar TCX
# Lägg till json track path i databasen

# Test to run n8n for mail trigger and run a code that process the TCX files
# When TCX process also make route picture as strava stile
# When TCX process also make a video when the route writes out
# transfer data from this year
# Test out panda and some graphic element
# Make pages
# Test maps, folium or plotly maps
# Option to export the data to Excel
# Option to export the analyst to pdf
# Send report mail for this month with analytics



def buildUI():
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
        # Build database
        initiate_database()

        # Build UI
        buildUI()


    except Exception:
        traceback.print_exc()

