from PyQt5 import QtWidgets as Widgets
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QUrl
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication as App, QMainWindow as Window, QFileDialog
import sys, os
import qrc_res

stylesheet = open('style-css.txt', 'r').read()

class MyWindow(Window) :

    resized = QtCore.pyqtSignal()
    files, filenames = [], []

    def __init__(self, win_width, win_height):
        super(MyWindow, self).__init__()
        self.setGeometry(0, 0, win_width, win_height)
        self.setMinimumHeight(600)
        self.setMinimumWidth(1000)
        self.setWindowTitle("Dynamic Dictate")
        self.setStyleSheet(stylesheet)
        self.resized.connect(self.resize)

        menuBar = self.menuBar()
        menuBar.setFixedHeight(60)
        toolbar = self.addToolBar("Controls")

        fileMenu = menuBar.addMenu("&File")
        viewMenu = menuBar.addMenu("&View")
        contMenu = menuBar.addMenu("&Controls")

        openAction = Widgets.QAction(self, text="Open...", icon=QIcon(":ic-open.svg"))
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.opentab)
        openRAction = Widgets.QAction(self, text="Open Recent...")
        openRAction.setShortcut("Ctrl+Shift+O")
        saveAction = Widgets.QAction(self, text="Save Progress...", icon=QIcon(":ic-save.svg"))
        saveAction.setShortcut("Ctrl+S")
        zoomIAction = Widgets.QAction(self, text="Zoom in...", icon=QIcon(":ic-zoom-in.svg"))
        zoomIAction.setShortcut("Ctrl+=")
        zoomOAction = Widgets.QAction(self, text="Zoom out...", icon=QIcon(":ic-zoom-out.svg"))
        zoomOAction.setShortcut("Ctrl+-")
        nextAction = Widgets.QAction(self, text="Next Page", icon=QIcon(":ic-down.svg"))
        nextAction.setShortcut("Right")
        prevAction = Widgets.QAction(self, text="Previous Page", icon=QIcon(":ic-up.svg"))
        prevAction.setShortcut("Left")
        playAction = Widgets.QAction(self, text="Play/Pause", icon=QIcon(":ic-play.svg"))
        playAction.setShortcut("K")
        stopAction = Widgets.QAction(self, text="Stop", icon=QIcon(":ic-stop.svg"))
        stopAction.setShortcut("Ctrl+K")
        camAction = Widgets.QAction(self, text="Toggle Camera", icon=QIcon(":ic-cam-on.svg"))
        camAction.setShortcut("Ctrl+Alt+V")
        zoomSpinBox = Widgets.QSpinBox(self)
        # fixed size (size does not change with window)
        zoomSpinBox.setFixedSize(QSize(176, 60))
        zoomSpinBox.setRange(25, 400)
        zoomSpinBox.setSingleStep(25)

        fileMenu.addActions([openAction, openRAction, saveAction])
        zoomMenu = viewMenu.addMenu("Zoom")
        zoomMenu.addActions([zoomIAction, zoomOAction])
        navMenu = viewMenu.addMenu("Navigate")
        navMenu.addActions([nextAction, prevAction])
        contMenu.addActions([playAction, stopAction])
        contMenu.addSeparator()
        contMenu.addActions([camAction])

        menuBar.setStyleSheet(stylesheet)
        menuBar.addMenu(fileMenu)
        menuBar.addActions([fileMenu.menuAction(), viewMenu.menuAction(), contMenu.menuAction()])

        toolbar.addActions([openAction, saveAction, zoomIAction, zoomOAction])
        toolbar.addWidget(zoomSpinBox)
        toolbar.addActions([nextAction, prevAction, playAction, stopAction, camAction])

        self.frame = Widgets.QFrame(self)
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.7*self.width()), int(0.8*self.height()))

        self.tabs = Widgets.QTabWidget(self.frame)
        self.labelNone = Widgets.QLabel('No tabs open')

        self.tabs.addTab(self.labelNone, "Tab 1")

    def resizeEvent(self, event) :
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def resize(self) :
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.7*self.width()), int(0.8*self.height()))
        self.tabs.setGeometry(0, 0, int(0.7*self.width()), int(0.8*self.height()))

    def opentab(self) :
        cwd = os.getcwd().replace('\\', '/')
        path_pdfjs = f"file:///{cwd}/pdfjs_copy/web/viewer.html"
        path_pdf = f"file:///{cwd}/Checklist_Scientifica.pdf"

        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames", "", "PDF files (*.pdf)", options=options)
        if (files) :
            print(files)
        self.files += files
        for file in files :
            self.filenames.append(file.split("/")[-1])

            self.pdf_view = QWebEngineView()
            self.pdf_view.setGeometry(0, 0, int(0.7*self.width()), int(0.8*self.height()))
            self.pdf_view.load(QUrl.fromUserInput("%s?file=%s" % (path_pdfjs, file)))
            self.tabs.addTab(self.pdf_view, self.filenames[-1])
            if (self.tabs.indexOf(self.labelNone) == 0) :
                self.tabs.removeTab(0)

app = App(sys.argv)
win = MyWindow(1600, 1200)
win.show()
print()
sys.exit(app.exec_())