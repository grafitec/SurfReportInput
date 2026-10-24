from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDialog, QFileDialog, QGraphicsOpacityEffect, QLabel, QMenu, QWidgetAction, QCheckBox, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDate, QSize, QPropertyAnimation, QTimer, Qt, pyqtSignal, QObject, QEvent


from services.database_service import save_surf_report
from services.database_service import save_gas_report
from services.database_service import get_surf_report
from services.database_service import get_gas_report
from services.database_service import get_next_id
from services.database_service import load_database_ride_from_id
from services.database_service import save_location_into_database
from services.database_service import get_location_from_database

from services.mail_service import get_new_mails
from services.mail_service import move_mail


from services.analytics_service import runAnalytics

from ui.analytics_window import AnalyticsWindow

import json
from pathlib import Path
import xml.etree.ElementTree as ET
import traceback
import os


class FileDropFilter(QObject):
    def __init__(self, drop_zone, line_edit):
        super().__init__(drop_zone)
        self.drop_zone = drop_zone
        self.line_edit = line_edit

        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.DragEnter:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True

        elif event.type() == QEvent.Type.DragMove:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True

        elif event.type() == QEvent.Type.Drop:
            for url in event.mimeData().urls():
                path = url.toLocalFile()

                if (
                    Path(path).is_file()
                    and Path(path).suffix.lower() == ".tcx"
                ):
                    self.line_edit.setText(path)
                    self.line_edit.setToolTip(path)
                    event.acceptProposedAction()
                    return True

        return False

class LocationDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/dialog_surf_launch.ui", self)
        self.btnOkay.clicked.connect(self.accept)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/report.ui", self)
        self.fileDropFilter = FileDropFilter(
            self.uploadDropZone,
            self.txtCtxPath
        )
        #self.setFixedSize(self.size())
        self.setWindowIcon(QIcon("ui/icons/diagram.png"))
        self.labUploadIcon = QLabel(self.uploadDropZone)
        pixmap = QPixmap("ui/icons/upload.png")
        self.labUploadIcon.setPixmap(
            pixmap.scaled(
                60, 60,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.labUploadIcon.setFixedSize(40, 40)
        self.labUploadIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uploadDropZone.layout().insertWidget(0, self.labUploadIcon)



        self.tabMain.setTabIcon(0, QIcon("ui/icons/document2.png"))
        self.tabMain.setTabIcon(1, QIcon("ui/icons/gas-station2.png"))
        self.tabMain.setTabIcon(2, QIcon("ui/icons/diagram.png"))
        self.tabMain.setIconSize(QSize(16, 16))

        self.labNewEntryIcon.setPixmap(
            QPixmap("ui/icons/clipboard.svg").scaled(
                25, 25,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        # Animations
        #self.tabMain.currentChanged.connect(self.on_tab_changed)

        # main buttons
        self.btnSendSurfReport.clicked.connect(self.send_surf_report)
        self.btnSendGasReport.clicked.connect(self.send_gas_report)
        self.btnReset.clicked.connect(self.resetUI)
        self.btnBrowseCtx.clicked.connect(self.browse_file)
        self.btnAnalytics.clicked.connect(self.openAnalytics)

        self.cmbStartPoint.currentTextChanged.connect(lambda: self.addStartLocationPopUp([self.cmbStartPoint]))



        # variables
        self.currentID = 0
        self.dataFromMail = []
        self.friendsFields = [self.txtFriend1, self.txtFriend2, self.txtFriend3, self.txtFriend4, self.txtFriend5, self.txtFriend6]

        # clear validation
        self.clearVal()

        # Adding people
        self.rad2Friends.toggled.connect(self.friends_toggled)
        self.gboxAddPeople.setVisible(False)

        # Add Surf launch spot
        self.populateStartLocation()

        # Load existing tables
        self.tabletRides.setAlternatingRowColors(True)
        self.tabletRides.horizontalHeader().setSortIndicatorShown(True)
        self.tabletRides.horizontalHeader().setSectionsClickable(True)
        self.load_surf_report_into_tables()
        nextId = get_next_id()
        self.labHeader.setText('New Entry · Record #'+str(nextId))
        self.setup_column_menu()

        # Initiate mail
        QTimer.singleShot(0, self.checkMails)


    def checkMails(self):
        self.dataFromMail = get_new_mails()
        if not self.dataFromMail == []:
            msg = str(len(self.dataFromMail))+' new mail reports'
            self.labMail.setText(str(len(self.dataFromMail))+' new mail on queue')
            QMessageBox.information(
                self,
                "Newly arrived mails",
                msg
            )
            self.proceed_mail()

    def proceed_mail(self):
        nextId = get_next_id()
        self.labHeader.setText('New Entry from mail · Record #' + str(nextId))
        if len(self.dataFromMail) > 1:
            self.labMail.setText(str(len(self.dataFromMail)-1)+' new mail on queue')
        else:
            self.labMail.setText('No new mail on queue')

        # Popuplate form
        self.load_report(self.dataFromMail[0])
        self.btnReset.setEnabled(False)


    def send_surf_report(self):
        # Checking if all fields are valid to continue
        if self.chkSkip.isChecked():
            valid = True
        else:
            valid = self.validate_surf_form()

        if valid:
            # Query all the data from the form
            self.process_surf_data()

    def send_gas_report(self):
        self.process_gas_data()

    def clear_validation(self, widgetList):
        for widget in widgetList:
            widget.setStyleSheet("")

    def addStartLocationPopUp(self, widget):
        if self.cmbStartPoint.currentText() == 'Add location':
            dialog = LocationDialog()
            if dialog.exec():
                location = dialog.txtLocation.text()
                gpsCor = dialog.txtGpsCor.text()
                save_location_into_database(location, gpsCor)
                self.cmbStartPoint.addItem(location)
                self.cmbStartPoint.setCurrentText(location)

    def populateStartLocation(self):
        locations = get_location_from_database()
        locationList = []
        for location in reversed(locations):
            locationList.append(location[1])
        self.cmbStartPoint.addItems(locationList)

    def openAnalytics(self):
        try:
            self.analyticsWindow = AnalyticsWindow()
            self.analyticsWindow.show()


        except Exception:
            traceback.print_exc()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TCX File",
            "",
            "TCX Files (*.tcx);;All Files (*)"
        )

        if file_path:
            self.txtCtxPath.setText(file_path)
            self.btnBrowseCtx.hide()


    def validate_surf_form(self):
        interrupt = False
        if self.txtComment.text() == '':
            interrupt = True
            self.txtComment.setStyleSheet("border: 2px solid red;")
        if self.spnTimeOnWater.value() == 0.0:
            interrupt = True
            self.spnTimeOnWater.setStyleSheet("border: 2px solid red;")
        if self.spnDistance.value() == 0.0:
            interrupt = True
            self.spnDistance.setStyleSheet("border: 2px solid red;")
        if self.cmbWeather.currentText() == '':
            interrupt = True
            self.cmbWeather.setStyleSheet("border: 2px solid red;")
        if self.cmbSurfType.currentText() == '':
            interrupt = True
            self.cmbSurfType.setStyleSheet("border: 2px solid red;")
        if self.rad1LedLight.isChecked() == False and self.rad2LedLight.isChecked() == False:
            interrupt = True
            self.rad1LedLight.setStyleSheet("border: 2px solid red;")
            self.rad2LedLight.setStyleSheet("border: 2px solid red;")
        if self.rad1Friends.isChecked() == False and self.rad2Friends.isChecked() == False:
            interrupt = True
            self.rad1Friends.setStyleSheet("border: 2px solid red;")
            self.rad2Friends.setStyleSheet("border: 2px solid red;")
        if self.cmbAnyInjuries.currentText() == '':
            interrupt = True
            self.cmbAnyInjuries.setStyleSheet("border: 2px solid red;")
        if self.cmbTemperature.currentText() == '':
            interrupt = True
            self.cmbTemperature.setStyleSheet("border: 2px solid red;")
        if self.cmbStartPoint.currentText() == '':
            interrupt = True
            self.cmbStartPoint.setStyleSheet("border: 2px solid red;")
        if self.dateSurfRide.date().toString("yyyy-MM-dd") == '2027-01-01':
            interrupt = True
            self.dateSurfRide.setStyleSheet("border: 2px solid red;")

        if interrupt:
            return False
        else:
            return True

    def friends_toggled(self, checked):
        self.gboxAddPeople.setVisible(checked)

    def clearVal(self):
        self.txtComment.textChanged.connect(lambda: self.clear_validation([self.txtComment]))
        self.spnTimeOnWater.textChanged.connect(lambda: self.clear_validation([self.spnTimeOnWater]))
        self.spnDistance.textChanged.connect(lambda: self.clear_validation([self.spnDistance]))
        self.cmbWeather.currentTextChanged.connect(lambda: self.clear_validation([self.cmbWeather]))
        self.cmbSurfType.currentTextChanged.connect(lambda: self.clear_validation([self.cmbSurfType]))
        self.cmbAnyInjuries.currentTextChanged.connect(lambda: self.clear_validation([self.cmbAnyInjuries]))
        self.cmbTemperature.currentTextChanged.connect(lambda: self.clear_validation([self.cmbTemperature]))
        self.cmbStartPoint.currentTextChanged.connect(lambda: self.clear_validation([self.cmbStartPoint]))
        self.dateSurfRide.dateChanged.connect(lambda: self.clear_validation([self.dateSurfRide]))
        self.rad2LedLight.toggled.connect(lambda: self.clear_validation([self.rad2LedLight, self.rad1LedLight]))
        self.rad1LedLight.toggled.connect(lambda: self.clear_validation([self.rad1LedLight, self.rad2LedLight]))
        self.rad1Friends.toggled.connect(lambda: self.clear_validation([self.rad1Friends, self.rad2Friends]))
        self.rad2Friends.toggled.connect(lambda: self.clear_validation([self.rad2Friends, self.rad1Friends]))


    def process_surf_data(self):
        date = self.dateSurfRide.date().toString("yyyy-MM-dd")
        comments = self.txtComment.text()
        timeOnWater = self.spnTimeOnWater.value()
        distance = self.spnDistance.value()
        instaLink = self.txtInstaLink.text()
        ctxPath = self.txtCtxPath.text()
        weather = self.cmbWeather.currentText()
        surfType = self.cmbSurfType.currentText()
        temperature = self.cmbTemperature.currentText()
        startPoint = self.cmbStartPoint.currentText()
        injuries = self.cmbAnyInjuries.currentText()
        ledLights = self.rad2LedLight.isChecked()
        friends = self.rad2Friends.isChecked()

        if friends:
            friendsName = []
            for field in self.friendsFields:
                if not field.text() == '':
                    friendsName.append(field.text())
        else:
            friendsName = []


        rideData = {
            'date': date,
            'comments': comments,
            'timeOnWater': timeOnWater,
            'distance': distance,
            'instaLink': instaLink,
            'ctxPath': ctxPath,
            'weather': weather,
            'surfType': surfType,
            'ledLights': ledLights,
            'friends': friends,
            'injuries': injuries,
            'temperature': temperature,
            'startPoint': startPoint,
            'friendsName': friendsName,
        }
        json_string = json.dumps(rideData, indent=4)
        try:
            # Send to database
            ride_id = save_surf_report(rideData, self.currentID)

            # Process TCX data
            if not 'Drop TCX file' in ctxPath:
                json_file = self.tcx_to_json(ctxPath, ride_id)
                rideData['ctxPath'] = json_file
                ride_id = save_surf_report(rideData, ride_id)

            # Update database UI
            self.load_surf_report_into_tables()


            if self.currentID == 0:
                msg = f'Surf report rideID #{ride_id} saved successfully. \nCheck it out under the "Current records" tab'
            else:
                msg = f'Surf report rideID #{ride_id} updated successfully. \nCheck it out under the "Current records" tab'

            QMessageBox.information(
                self,
                "Success",
                msg
            )
        except Exception:
            traceback.print_exc()

        # After submission
        prepear_for_new_sub = False
        if self.dataFromMail:
            mailId = self.dataFromMail[0]['mailId']
            move_mail(mailId)
            if len(self.dataFromMail) > 1:
                self.dataFromMail.pop(0)
            else:
                self.dataFromMail = []

            if self.dataFromMail:
                self.proceed_mail()
            else:
                prepear_for_new_sub = True
        else:
            prepear_for_new_sub = True

        if prepear_for_new_sub:
            # Reset the form
            self.resetUI()
            self.btnReset.setEnabled(True)
            self.labMail.setText('')



    def process_gas_data(self):
        date = self.dateGas.date().toString("yyyy-MM-dd")
        liter = self.spnLiter.value()
        cost = self.spnCost.value()

        gasData = {
            'date': date,
            'liter': liter,
            'cost': cost,
        }
        gas_id = save_gas_report(gasData)

        self.load_surf_report_into_tables()

        QMessageBox.information(
            self,
            "Success",
            f'Gas report gasID #{gas_id} saved successfully'
        )

    def load_surf_report_into_tables(self):
        # Populate surf report into tables
        reports = get_surf_report()
        self.tabletRides.setSortingEnabled(False)
        self.tabletRides.setRowCount(len(reports))
        self.tabletRides.setColumnCount(14)
        for row_index, row_data in enumerate(reports):
            for column_index, value in enumerate(row_data):
                self.tabletRides.setItem(row_index, column_index, QTableWidgetItem(str(value)))
        self.tabletRides.setHorizontalHeaderLabels([
            "ID",
            "Date",
            "Weather",
            "Friends",
            "Injuries",
            "Temperature",
            "Time",
            "Comments",
            "Distance",
            "Instagram",
            "CTX",
            "Surf Type",
            "LED",
            "Start Point"
        ])
        for row_index, row_data in enumerate(reports):
            self.tabletRides.setItem(row_index, 0, NumericTableWidgetItem(str(row_data[0])))
            self.tabletRides.setItem(row_index, 8, NumericTableWidgetItem(str(row_data[8])))
        self.tabletRides.resizeColumnsToContents()
        self.tabletRides.verticalHeader().setVisible(False)
        self.tabletRides.cellDoubleClicked.connect(self.load_report_from_edited)
        self.tabletRides.setSortingEnabled(True)

        # Populate Gas report into tables
        reports = get_gas_report()
        self.tabletGas_2.setRowCount(len(reports))
        self.tabletGas_2.setColumnCount(4)
        for row_index, row_data in enumerate(reports):
            for column_index, value in enumerate(row_data):
                self.tabletGas_2.setItem(row_index, column_index, QTableWidgetItem(str(value)))
        self.tabletGas_2.setHorizontalHeaderLabels([
            "ID",
            "Date",
            "liters",
            "cost",
        ])
        self.tabletGas_2.resizeColumnsToContents()
        self.tabletGas_2.verticalHeader().setVisible(False)

        # Count cost and liters
        total_liters = 0
        total_cost = 0
        for row in reports:
            total_liters += row[2]
            total_cost += row[3]
        self.labLiters.setText(str(total_liters) + ' liters')
        self.labCost.setText(str(total_cost) + ' kr')

        # Populate friends report into tables
        reports = get_gas_report()
        self.tabletGas_2.setRowCount(len(reports))
        self.tabletGas_2.setColumnCount(4)
        for row_index, row_data in enumerate(reports):
            for column_index, value in enumerate(row_data):
                self.tabletGas_2.setItem(row_index, column_index, QTableWidgetItem(str(value)))
        self.tabletGas_2.setHorizontalHeaderLabels([
            "ID",
            "Date",
            "liters",
            "cost",
        ])
        self.tabletGas_2.resizeColumnsToContents()
        self.tabletGas_2.verticalHeader().setVisible(False)

    def setup_column_menu(self):
        hidden_columns = {
            "Instagram",
            "Injuries",
            "Temperature",
            "CTX",
        }

        self.column_menu = QMenu(self)

        for col in range(self.tabletRides.columnCount()):
            header = self.tabletRides.horizontalHeaderItem(col)

            if header is None:
                continue
            name = header.text()
            checkbox = QCheckBox(header.text(), self.column_menu)
            checkbox.setChecked(not self.tabletRides.isColumnHidden(col))

            checked = name not in hidden_columns
            checkbox.setChecked(checked)
            self.tabletRides.setColumnHidden(col, not checked)

            checkbox.toggled.connect(
                lambda checked, c=col:
                self.tabletRides.setColumnHidden(c, not checked)
            )

            action = QWidgetAction(self.column_menu)
            action.setDefaultWidget(checkbox)
            self.column_menu.addAction(action)

        self.btnColumns.clicked.connect(self.show_column_menu)

    def show_column_menu(self):
        self.column_menu.exec(
            self.btnColumns.mapToGlobal(
                self.btnColumns.rect().bottomLeft()
            )
        )



    def load_report_from_edited(self, row, column):
        self.currentID = self.tabletRides.item(row, 0).text()
        self.tabMain.setCurrentIndex(0)
        self.labHeader.setText('Update Entry · Record #' + str(self.currentID))
        self.btnSendSurfReport.setText('Update row #' + str(self.currentID))
        rideData = load_database_ride_from_id(self.currentID)
        self.load_report(rideData)


    def load_report(self, data):
        date = QDate.fromString(data['date'], "yyyy-MM-dd")
        self.dateSurfRide.setDate(date)
        self.cmbWeather.setCurrentText(data['weather'])
        self.cmbAnyInjuries.setCurrentText(data['injuries'])
        self.cmbTemperature.setCurrentText(data['temperature'])
        self.spnTimeOnWater.setValue(data['timeOnWater'])
        self.txtComment.setText(data['comments'])
        self.spnDistance.setValue(data['distance'])
        if 'instaLink' in data:
            self.txtInstaLink.setText(data['instaLink'])
        if 'ctxPath' in data:
            self.txtCtxPath.setText(data['ctxPath'])
        self.cmbSurfType.setCurrentText(data['surfType'])
        self.cmbStartPoint.setCurrentText(data['startPoint'])
        if data['friends'] == 1:
            self.rad2Friends.setChecked(True)

            for field in self.friendsFields:
                field.setText('')
            for name in data['friendsName']:
                for field in self.friendsFields:
                    if field.text() == '':
                        field.setText(name)
                        break
                continue
            self.friends_toggled(True)

        else:
            self.rad1Friends.setChecked(True)
        if data['ledLights'] == 1:
            self.rad2LedLight.setChecked(True)
        else:
            self.rad1LedLight.setChecked(True)


    def resetUI(self):
        nextId = get_next_id()
        self.currentID = 0

        self.labHeader.setText('New Entry · Record #'+str(nextId))
        self.btnSendSurfReport.setText('Add surf report')

        data = {
            'date': '2027-01-01',
            'weather': '',
            'injuries': '',
            'temperature': '',
            'timeOnWater': 0,
            'comments': '',
            'distance': 0,
            'instaLink': '',
            'ctxPath': 'Drop TCX file here or',
            'surfType': '',
            'startPoint': '',
            'friends': False,
            'friendsName': [],
            'ledLights': False
        }

        self.load_report(data)


    def tcx_to_json(self, tcx_path, rideId):
        TCX_NS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        NS = {"tcx": TCX_NS}
        tcx_file = Path(tcx_path)
        if os.path.exists(tcx_file):
            root = ET.parse(tcx_file).getroot()

            points = []
            index = 0
            for point in root.findall(".//tcx:Trackpoint", NS):
                time_el = point.find("tcx:Time", NS)
                lat_el = point.find("tcx:Position/tcx:LatitudeDegrees", NS)
                lon_el = point.find("tcx:Position/tcx:LongitudeDegrees", NS)

                if time_el is None or time_el.text is None:
                    continue
                if lat_el is None or lon_el is None:
                    continue

                points.append({
                    "id": float(1),
                    "index": int(index),
                    "time": time_el.text,
                    "latitude": float(lat_el.text),
                    "longitude": float(lon_el.text),

                })
                index = index + 1
            json_path = (
                    Path(__file__).parent.parent.parent
                    / "data"
                    / "tcx"
                    / f"appleWatchRideData_rideId_{rideId}.json"
            )
            json_file = Path(json_path)
            with json_file.open("w", encoding="utf-8") as f:
                json.dump(points, f, indent=2, ensure_ascii=False)
            path = str(json_file).replace('\\','/')
            return path
        else:
            return None

    def on_tab_changed(self, index):
        widget = self.tabMain.widget(index)
        self.fade_in(widget)

    def fade_in(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(250)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)

        self._fade_animation = animation
        animation.start()

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)