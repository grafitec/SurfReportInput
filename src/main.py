
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.database_service import initiate_database
from services.mail_service import initiate_mail_client
import traceback
from pathlib import Path

# To do
# Add support for mail submission
# Tabeller
# Kunna sortera och filtrera på rubrikerna
# Lägga in en knapp för Columns för att kunna klicka bort vissa
# Annan typsnitt

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

        # Initiate mail
        initiate_mail_client()

        # Build UI
        buildUI()


    except Exception:
        traceback.print_exc()

