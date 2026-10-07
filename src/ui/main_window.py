from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/report.ui", self)

        # main button
        self.btnSendSurfReport.clicked.connect(self.send_surf_report)

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

    def send_surf_report(self):
        # Checking if all fields are valid to continue
        if not self.chkSkip.isChecked():
            valid = self.validate_form()
        else:
            valid = True
        if valid:
            # Query all the data from the form
            self.get_form_data()

    def validate_form(self):
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
        if self.rad1LedLight.isChecked() == False or self.rad2LedLight.isChecked() == False:
            interrupt = True
            self.rad1LedLight.setStyleSheet("border: 2px solid red;")
            self.rad2LedLight.setStyleSheet("border: 2px solid red;")
        if self.rad1Friends.isChecked() == False or self.rad2Friends.isChecked() == False:
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

    def get_form_data(self):
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

    def clear_validation(self, widgetList):
        for widget in widgetList:
            widget.setStyleSheet("")

    def friends_toggled(self, checked):
        self.gboxAddPeople.setVisible(checked)
        print(checked)