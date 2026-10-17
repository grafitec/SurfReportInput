from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import QTimer, Qt

from pathlib import Path
import traceback

# Only for matplotlib, remove later
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ChartWidget(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

class AnalyticsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/analytics_window.ui", self)

        # Buttons
        self.btnFullscreen.clicked.connect(self.toggle_fullscreen)

        # Skapa bakgrundsbilden
        self.backgroundLabel = QLabel(self.centralwidget_analytic)
        self.backgroundLabel.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.backgroundLabel.setScaledContents(False)

        # Ladda bilden
        image_path = Path(__file__).resolve().parent / \
            "images/surf-background_big.png"
        self.backgroundPixmap = QPixmap(str(image_path))

        if self.backgroundPixmap.isNull():
            print(f"Kunde inte ladda bilden: {image_path}")

        # Placera bakgrunden bakom övrigt innehåll
        self.backgroundLabel.lower()
        self.update_background()

        self.setup_proportional_scaling()
        self.resize(1536, 864)
        QTimer.singleShot(0, self.update_background)

        self.layoutCharts()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "graphics_view"):
            self.scale_design()


    def update_background(self):
        if self.backgroundPixmap.isNull():
            return

        size = self.centralwidget_analytic.size()
        self.backgroundLabel.setGeometry(
            self.centralwidget_analytic.rect()
        )

        scaled = self.backgroundPixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Beskär mitten så att bilden fyller hela ytan
        x = (scaled.width() - size.width()) // 2
        y = (scaled.height() - size.height()) // 2

        cropped = scaled.copy(
            x, y, size.width(), size.height()
        )

        self.backgroundLabel.setPixmap(cropped)
        self.backgroundLabel.lower()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def setup_proportional_scaling(self):
        # Originalstorleken på din design
        self.design_width = 1536
        self.design_height = 864

        # Spara den befintliga designen
        self.design_widget = self.centralwidget_analytic

        # Frigör den från QMainWindow innan den placeras i proxyn
        self.takeCentralWidget()

        self.design_widget.setParent(None)
        self.design_widget.setFixedSize(
            self.design_width,
            self.design_height
        )

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(
            0, 0, self.design_width, self.design_height
        )

        self.proxy = self.scene.addWidget(self.design_widget)

        self.graphics_view = QGraphicsView(self.scene, self)
        self.graphics_view.setFrameShape(
            QGraphicsView.Shape.NoFrame
        )
        self.graphics_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.graphics_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.graphics_view.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.graphics_view.setStyleSheet(
            "QGraphicsView { border: none; background: transparent; }"
        )

        self.setCentralWidget(self.graphics_view)
        QTimer.singleShot(0, self.scale_design)
        self.scale_design()



    def scale_design(self):
        if not hasattr(self, "graphics_view"):
            return

        self.graphics_view.resetTransform()

        self.graphics_view.fitInView(
            self.scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )

    def layoutCharts(self):
        chart = ChartWidget()
        self.verticalLayout_3.addWidget(chart)