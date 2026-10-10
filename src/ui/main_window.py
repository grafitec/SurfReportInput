from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog, QFileDialog
from PyQt6.QtCore import QDate
from services.database_service import save_surf_report
from services.database_service import save_gas_report
from services.database_service import get_surf_report
from services.database_service import get_gas_report
from services.database_service import get_next_id
from services.database_service import load_ride_from_id
from services.database_service import save_location_into_database
from services.database_service import get_location_from_database
from services.database_service import process_TCX_into_database

class LocationDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/dialog_surf_launch.ui", self)
        self.btnOkay.clicked.connect(self.accept)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/report.ui", self)

        # main buttons
        self.btnSendSurfReport.clicked.connect(self.send_surf_report)
        self.btnSendGasReport.clicked.connect(self.send_gas_report)
        self.btnReset.clicked.connect(self.resetUI)
        self.btnBrowseCtx.clicked.connect(self.browse_file)

        self.cmbStartPoint.currentTextChanged.connect(lambda: self.addStartLocationPopUp([self.cmbStartPoint]))


        # variables
        self.currentID = 0
        self.friendsFields = [self.txtFriend1, self.txtFriend2, self.txtFriend3, self.txtFriend4, self.txtFriend5, self.txtFriend6, self.txtFriend7, self.txtFriend8]

        # clear validation
        self.clearVal()

        # Adding people
        self.rad2Friends.toggled.connect(self.friends_toggled)
        self.gboxAddPeople.setVisible(False)

        # Add Surf launch spot
        self.populateStartLocation()

        # Load existing tables
        self.load_surf_report_into_tables()
        nextId = get_next_id()
        self.labHeader.setText('Will add new row into database, rideID #'+str(nextId))

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
            print('Add location')
            dialog = LocationDialog()
            if dialog.exec():
                location = dialog.txtLocation.text()
                gpsCor = dialog.txtGpsCor.text()
                save_location_into_database(location, gpsCor)
                self.cmbStartPoint.addItem(location)
                self.cmbStartPoint.setCurrentText(location)

    def populateStartLocation(self):
        locations = get_location_from_database()
        print(locations)
        locationList = []
        for location in reversed(locations):
            locationList.append(location[1])
        self.cmbStartPoint.addItems(locationList)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TCX File",
            "",
            "TCX Files (*.tcx);;All Files (*)"
        )

        if file_path:
            self.txtCtxPath.setText(file_path)

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
        # Send to database
        ride_id = save_surf_report(rideData, self.currentID)

        # Update database UI
        self.load_surf_report_into_tables()

        # Process TCX data
        process_TCX_into_database(ctxPath)


        if self.currentID == 0:
            msg = f'Surf report rideID #{ride_id} saved successfully. \nCheck it out under the "Current records" tab'
        else:
            msg = f'Surf report rideID #{ride_id} updated successfully. \nCheck it out under the "Current records" tab'

        QMessageBox.information(
            self,
            "Success",
            msg
        )

        # Reset the form
        self.resetUI()


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
        self.tabletRides.resizeColumnsToContents()
        self.tabletRides.verticalHeader().setVisible(False)
        self.tabletRides.cellDoubleClicked.connect(self.load_report)

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



    def load_report(self, row, column):

        self.currentID = self.tabletRides.item(row, 0).text()
        self.tabMain.setCurrentIndex(0)
        self.labHeader.setText('Will update row in database, rideID #' + str(self.currentID))
        self.btnSendSurfReport.setText('Update row #' + str(self.currentID))
        rideData = load_ride_from_id(self.currentID)
        print(rideData)
        date = QDate.fromString(rideData[1], "yyyy-MM-dd")
        self.dateSurfRide.setDate(date)
        self.cmbWeather.setCurrentText(rideData[2])
        self.cmbAnyInjuries.setCurrentText(rideData[4])
        self.cmbTemperature.setCurrentText(rideData[5])
        self.spnTimeOnWater.setValue(rideData[6])
        self.txtComment.setText(rideData[7])
        self.spnDistance.setValue(rideData[8])
        self.txtInstaLink.setText(rideData[9])
        self.txtCtxPath.setText(rideData[10])
        self.cmbSurfType.setCurrentText(rideData[11])
        self.cmbStartPoint.setCurrentText(rideData[13])
        if rideData[3] == 1:
            self.rad2Friends.setChecked(True)

            for field in self.friendsFields:
                field.setText('')

            for name in rideData[14]:
                for field in self.friendsFields:
                    if field.text() == '':
                        field.setText(name)
                        break
                continue
            self.friends_toggled(True)

        else:
            self.rad1Friends.setChecked(True)
        if rideData[12] == 1:
            self.rad2LedLight.setChecked(True)
        else:
            self.rad1LedLight.setChecked(True)




    def resetUI(self):
        nextId = get_next_id()
        self.currentID = 0

        self.labHeader.setText('Will add new row into database, rideID #'+str(nextId))
        self.btnSendSurfReport.setText('Add surf report')
        date = QDate.fromString('2027-01-01', "yyyy-MM-dd")
        self.dateSurfRide.setDate(date)
        self.txtComment.setText('')
        self.spnTimeOnWater.setValue(0)
        self.spnDistance.setValue(0)
        self.txtInstaLink.setText('')
        self.txtCtxPath.setText('')
        self.cmbWeather.setCurrentText('')
        self.cmbSurfType.setCurrentText('')
        self.cmbTemperature.setCurrentText('')
        self.cmbStartPoint.setCurrentText('')
        self.cmbAnyInjuries.setCurrentText('')
        self.rad2LedLight.setChecked(False)
        self.rad2Friends.setChecked(False)
        self.rad1Friends.setChecked(False)
        self.rad1LedLight.setChecked(False)
        for field in self.friendsFields:
            field.setText('')