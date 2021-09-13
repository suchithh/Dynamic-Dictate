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
    files, filenames, filedisplaynames = [], [], []
    recentfiles, recentfilenames, recentfilednames = [], [], []

    def __init__(self, win_width, win_height):
        super(MyWindow, self).__init__()
        self.setGeometry(0, 0, win_width, win_height)
        self.setMinimumHeight(600)
        self.setMinimumWidth(1000)
        self.setWindowTitle("Dynamic Dictate")
        self.setStyleSheet(stylesheet)
        self.resized.connect(self.resize)

        self.read()
        self.makeMenu()

        self.frame = Widgets.QFrame(self)
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.7*self.width()), int(0.8*self.height()))
        self.buildtab()

    def read(self) :  
        with open('recents.txt', 'r') as recents :
            s = recents.read()
        if (s) :
            self.recentfiles = list(eval(s))
        for file in self.recentfiles :
            self.recentfilenames.append(file.split("/")[-1])
            if (len(self.recentfilenames) > 22) :
                self.recentfilednames.append(self.recentfilenames[-1][:20]+"...")
            else :
                self.recentfilednames.append(self.recentfilenames[-1])

    def makeMenu(self) :
        # menu bar
        self.menubar = self.menuBar()
        # fixed size (size does not change with window)
        self.menubar.setFixedHeight(60)
        toolbar = self.addToolBar("Controls")

        self.fileMenu = self.menubar.addMenu("&File")
        viewMenu = self.menubar.addMenu("&View")
        contMenu = self.menubar.addMenu("&Controls")

        # actions
        openAction = Widgets.QAction(self, text="Open...", icon=QIcon(":ic-open.svg"))
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.opentab)
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
        closeAction = Widgets.QAction(self, text="Close Tab", icon=QIcon(":ic-close.svg"))
        closeAction.setShortcut("Ctrl+W")
        closeAction.triggered.connect(self.closetab)

        # spin box for zoom
        zoomSpinBox = Widgets.QSpinBox(self)
        # fixed size (size does not change with window)
        zoomSpinBox.setFixedSize(QSize(176, 60))
        zoomSpinBox.setRange(25, 400)
        zoomSpinBox.setSingleStep(25)

        self.openRMenu = self.fileMenu.addMenu("Open Recent...")
        self.makeRecentMenu()
        
        # menus
        self.fileMenu.addActions([openAction, saveAction, closeAction])
        zoomMenu = viewMenu.addMenu("Zoom")
        zoomMenu.addActions([zoomIAction, zoomOAction])
        navMenu = viewMenu.addMenu("Navigate")
        navMenu.addActions([nextAction, prevAction])
        contMenu.addActions([playAction, stopAction])
        contMenu.addSeparator()
        contMenu.addActions([camAction])

        # menu bar
        self.menubar.setStyleSheet(stylesheet)
        self.menubar.addActions([self.fileMenu.menuAction(), viewMenu.menuAction(), contMenu.menuAction()])

        # toolbar
        toolbar.addActions([openAction, saveAction, closeAction, zoomIAction, zoomOAction])
        toolbar.addWidget(zoomSpinBox)
        toolbar.addActions([nextAction, prevAction, playAction, stopAction, camAction])

    def makeRecentMenu(self) :
        self.openRMenu.clear()
        if (self.recentfiles) :
            lastFileAction = Widgets.QAction(self, text=self.recentfiles[-1].split("/")[-1])
            lastFileAction.setShortcut("Ctrl+Shift+O")
            lastFileAction.triggered.connect(lambda: self.openrecenttab(-1))
            self.openRMenu.addAction(lastFileAction)
        for i in range(len(self.recentfiles)-2, -1, -1) :
            fileAction = Widgets.QAction(self, text=self.recentfiles[i].split("/")[-1])
            fileAction.triggered.connect(lambda: self.openrecenttab(i))
            self.openRMenu.addAction(fileAction)
        

    def buildtab(self) :
        self.tabs = Widgets.QTabWidget(self.frame)
        self.tabs.setStyleSheet(stylesheet)
        self.tabs.setMovable(True)

        self.labelNone = Widgets.QLabel('No tabs open')
        self.tabs.addTab(self.labelNone, "Home")

    def resizeEvent(self, event) :
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def resize(self) :
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.7*self.width()), int(0.8*self.height()))
        self.tabs.setGeometry(0, 0, int(0.7*self.width()), int(0.8*self.height()))

    # open action triggered
    def opentab(self) :
        cwd = os.getcwd().replace('\\', '/')
        path_pdfjs = f"file:///{cwd}/pdfjs_copy/web/viewer.html"

        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames", "", "PDF files (*.pdf)", options=options)
        self.files += files
        for file in files :
            self.filenames.append(file.split("/")[-1])
            if (len(self.filenames[-1]) > 22) :
                self.filedisplaynames.append(self.filenames[-1][:20]+"...")
            else :
                self.filedisplaynames.append(self.filenames[-1])

            if (file in self.recentfiles) :
                self.recentfiles.remove(file)
            self.recentfiles.append(file)
            if (len(self.recentfiles) > 10) :
                self.recentfiles.pop(0)
            recents = open('recents.txt', 'w')
            recents.write(str(self.recentfiles))
            self.read()
            self.makeRecentMenu()

            self.pdf_view = QWebEngineView()
            self.pdf_view.setGeometry(0, 0, int(0.7*self.width()), int(0.8*self.height()))
            self.pdf_view.load(QUrl.fromUserInput("%s?file=%s" % (path_pdfjs, file)))
            self.tabs.addTab(self.pdf_view, self.filedisplaynames[-1])
            self.tabs.setTabToolTip(-1, self.filenames[-1])
            if (self.tabs.indexOf(self.labelNone) == 0) :
                self.tabs.removeTab(0)

    def openrecenttab(self, index) :
        cwd = os.getcwd().replace('\\', '/')
        path_pdfjs = f"file:///{cwd}/pdfjs_copy/web/viewer.html"

        self.pdf_view = QWebEngineView()
        self.pdf_view.setGeometry(0, 0, int(0.7*self.width()), int(0.8*self.height()))
        self.pdf_view.load(QUrl.fromUserInput("%s?file=%s" % (path_pdfjs, self.recentfiles[index])))
        self.tabs.addTab(self.pdf_view, self.recentfilednames[index])
        self.tabs.setTabToolTip(-1, self.recentfilenames[index])
        if (self.tabs.indexOf(self.labelNone) == 0) :
            self.tabs.removeTab(0)

        self.recentfiles.append(self.recentfiles.pop(index))
        recents = open('recents.txt', 'w')
        recents.write(str(self.recentfiles))
        self.read()
        self.makeRecentMenu()

    def closetab(self) :
        self.tabs.removeTab(self.tabs.currentIndex())
        if (self.tabs.count() == 0) :
            self.tabs.addTab(self.labelNone, "Home")

app = App(sys.argv)
win = MyWindow(1600, 1200)
win.show()
print()
sys.exit(app.exec_())