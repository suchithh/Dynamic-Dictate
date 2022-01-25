from PyQt5 import QtWidgets, QtCore
import PyQt5

class PreferencesDialog(QtWidgets.QDialog) :
    
    def __init__(self) :
        super(PreferencesDialog, self).__init__()
        self.resize(508, 350)

        self.buttonbox = QtWidgets.QDialogButtonBox(self)
        self.buttonbox.setGeometry(QtCore.QRect(150, 250, 341, 32))
        self.buttonbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.accepted.connect(self.ok)
        self.buttonbox.rejected.connect(self.cancel)

    def ok() :
        pass

    def cancel() :
        pass