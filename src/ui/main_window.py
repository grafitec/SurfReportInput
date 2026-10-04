from PyQt6.QtWidgets import QMainWindow, QLabel
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surf Report Input")
        label = QLabel("Hej Mikael!")
        self.setCentralWidget(label)