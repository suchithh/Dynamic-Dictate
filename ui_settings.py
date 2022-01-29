from PyQt5 import QtWidgets, QtCore
import sys

stylesheet = open('style-css.txt', 'r').read()

def read_settings() :
    with open('settings.txt', 'r') as file0 :
        return eval(file0.read())

def write_settings(speed, region, no_of_words, camera_on) :
    file0 = open('settings.txt', 'w')
    d = {
    "Narration": {
        "Speed": f"{speed}",
        "Region": f"{region}",
        "Maximum_Words_Read": f"{no_of_words}"
        },
    "On-Startup": {
        "Camera-on": camera_on
        }
    }
    file0.write(str(d))
    file0.close()

class PreferencesDialog(QtWidgets.QDialog) :
    
    def __init__(self) :
        super(PreferencesDialog, self).__init__()
        self.resize(600, 400)
        self.setWindowTitle('Preferences')
        self.setStyleSheet(stylesheet)

        d = read_settings()

        self.buttonbox = QtWidgets.QDialogButtonBox(self)
        self.buttonbox.setGeometry(20, 340, 560, 28)
        self.buttonbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.accepted.connect(self.ok)
        self.buttonbox.rejected.connect(self.cancel)

        self.groupbox = QtWidgets.QGroupBox(self, title='Narration')
        self.groupbox.setGeometry(20, 20, 560, 200)
        self.formlayout = QtWidgets.QFormLayout()
        self.formlayout.setVerticalSpacing(24)
        self.groupbox.setLayout(self.formlayout)

        self.radiogroup = QtWidgets.QHBoxLayout()
        self.radioslow = QtWidgets.QRadioButton()
        self.radioslow.setText('Slow')
        self.radiogroup.addWidget(self.radioslow)
        self.radionormal = QtWidgets.QRadioButton()
        self.radionormal.setText('Normal')
        if d :
            if (d['Narration']['Speed'] == 'Slow') :
                self.radioslow.setChecked(True)
            else :
                self.radionormal.setChecked(True)
        self.radiogroup.addWidget(self.radionormal)
        self.formlayout.addRow(QtWidgets.QLabel('Speed:'), self.radiogroup)

        self.langbox = QtWidgets.QComboBox()
        self.langbox.addItems(['English (India)', 'English (US)', 'English (UK)'])
        if d :
            if (d['Narration']['Region'] == 'English (US)') :
                self.langbox.setCurrentIndex(1)
            elif (d['Narration']['Region'] == 'English (UK)') :
                self.langbox.setCurrentIndex(2)
        self.formlayout.addRow(QtWidgets.QLabel('Region:'), self.langbox)

        self.numberbox = QtWidgets.QSpinBox()
        self.numberbox.setRange(1, 10)
        if d :
            self.numberbox.setValue(int(d['Narration']['Maximum_Words_Read']))
        self.numberbox.setFixedWidth(100)
        self.formlayout.addRow(QtWidgets.QLabel('Maximum words spoken at once:'), self.numberbox)

        self.groupbox2 = QtWidgets.QGroupBox(self, title='On Startup')
        self.groupbox2.setGeometry(20, 240, 560, 80)
        self.formlayout2 = QtWidgets.QFormLayout()
        self.formlayout2.setVerticalSpacing(24)
        self.groupbox2.setLayout(self.formlayout2)

        self.cameraonbox = QtWidgets.QCheckBox()
        self.cameraonbox.setText('Camera on by default on startup')
        if d :
            self.cameraonbox.setChecked(d['On-Startup']['Camera-on'])
        self.formlayout2.addRow(self.cameraonbox)

    def ok(self) :
        speedbool = self.radioslow.isChecked()
        speed = 'Normal'
        if speedbool :
            speed = 'Slow'
        region = self.langbox.currentText()
        no_of_words = int(self.numberbox.value())
        camera_on = self.cameraonbox.isChecked()
        write_settings(speed, region, no_of_words, camera_on)
        self.close()

    def cancel(self) :
        self.close()