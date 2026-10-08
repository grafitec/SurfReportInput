from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
import json
from services.database_service import save_surf_report
from services.database_service import save_gas_report
from services.database_service import get_surf_report


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/report.ui", self)

        # main button
        self.btnSendSurfReport.clicked.connect(self.send_surf_report)
        self.btnSendGasReport.clicked.connect(self.send_gas_report)

        # clear validation
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

        # Adding people
        self.rad2Friends.toggled.connect(self.friends_toggled)
        self.gboxAddPeople.setVisible(False)

        # Load existing tables
        self.load_surf_report()

    def send_surf_report(self):
        # Checking if all fields are valid to continue
        if self.chkSkip.isChecked():
            valid = True
        else:
            valid = self.validate_surf_form()

        if valid:
            # Query all the data from the form
            self.get_surf_form_data()

    def send_gas_report(self):
        self.get_gas_form_data()

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
            print('Run popup window')
            return False
        else:
            return True

    def clear_validation(self, widgetList):
        for widget in widgetList:
            widget.setStyleSheet("")

    def friends_toggled(self, checked):
        self.gboxAddPeople.setVisible(checked)

    def get_surf_form_data(self):
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
            if not self.txtFriend1.text() == '':
                friendsName.append(self.txtFriend1.text())
            if not self.txtFriend2.text() == '':
                friendsName.append(self.txtFriend2.text())
            if not self.txtFriend3.text() == '':
                friendsName.append(self.txtFriend3.text())
            if not self.txtFriend4.text() == '':
                friendsName.append(self.txtFriend4.text())
            if not self.txtFriend5.text() == '':
                friendsName.append(self.txtFriend5.text())
            if not self.txtFriend6.text() == '':
                friendsName.append(self.txtFriend6.text())
            if not self.txtFriend7.text() == '':
                friendsName.append(self.txtFriend7.text())
            if not self.txtFriend8.text() == '':
                friendsName.append(self.txtFriend8.text())
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
        rideDataDumped = json.dumps(rideData, indent=4)
        print(rideDataDumped)
        ride_id = save_surf_report(rideData)
        self.load_surf_report()

        QMessageBox.information(
            self,
            "Success",
            f'Surf report rideID #{ride_id} saved successfully. \nCheck it out under the "Current Records" tab'
        )


    def get_gas_form_data(self):
        date = self.dateGas.date().toString("yyyy-MM-dd")
        liter = self.spnLiter.value()
        cost = self.spnCost.value()

        gasData = {
            'date': date,
            'liter': liter,
            'cost': cost,
        }
        gas_id = save_gas_report(gasData)

        QMessageBox.information(
            self,
            "Success",
            f'Gas report gasID #{gas_id} saved successfully'
        )

    def load_surf_report(self):

        reports = get_surf_report()
        self.tabletRides.setRowCount(len(reports))
        self.tabletRides.setColumnCount(14)

        for row_index, row_data in enumerate(reports):
            for column_index, value in enumerate(row_data):
                print(value)
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

        self.tabletRides.resizeColumnsToContents()
        self.tabletRides.verticalHeader().setVisible(False)

        self.tabletRides.cellDoubleClicked.connect(
            self.load_report
        )

    def load_report(self, row, column):

        ride_id = self.tabletRides.item(row, 0).text()
        print(ride_id)

        #self.load_ride(ride_id)

        """
        SELECT *
        FROM surfReport
        WHERE rideId = ?
        
        self.txtTemperature.setText(...)
        self.cmbWeather.setCurrentText(...)
        self.chkLedLights.setChecked(...)
        """