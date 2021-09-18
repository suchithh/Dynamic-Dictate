from PyQt5 import QtWidgets as Widgets
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QUrl
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication as App, QMainWindow as Window, QFileDialog
import sys, os, qrc_res, zipfile

# Qt widgets can be styled in CSS, so this string will work as the parent style sheet for the app
stylesheet = open('style-css.txt', 'r').read()

class MyWindow(Window) :

    # a signal which is triggered when the window resizes
    resized = QtCore.pyqtSignal()

    # full file path, file name, file name shortened to 22 characters
    files, filenames, filedisplaynames = [], [], []
    # same as above but only for recently opened files
    rfiles, rfilenames, rfiledisplaynames = [], [], []
    # current working directory path
    file_cwd = os.getcwd().replace('\\', '/')

    def __init__(self, win_width, win_height) :
        # super call
        super(MyWindow, self).__init__()

        # making window
        self.setGeometry(0, 0, win_width, win_height)
        self.setMinimumHeight(600)
        self.setMinimumWidth(1000)
        self.setWindowTitle("Dynamic Dictate")
        self.setStyleSheet(stylesheet)
        self.resized.connect(self.resize)

        # recents.txt is required for proper functioning of the program
        if (not os.path.isfile("recents.txt")) :
            newfile = open("recents.txt", "w")
            newfile.write("[]")
            newfile.close()

        if not os.path.exists(f"{self.file_cwd}/pdfjs_copy/"):
            with zipfile.ZipFile(f"{self.file_cwd}/pdfjs_copy.zip", "r") as zip_ref:
                zip_ref.extractall(f"{self.file_cwd}")

        # read recent files opened
        self.read()
        # make menu bar and menus
        self.makeMenu()

        # frame containing tab layout
        self.frame = Widgets.QFrame(self)
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))

        # build the tab layout
        self.buildtab()

    def read(self) :
        # read recent files from text file
        with open('recents.txt', 'r') as recents :
            s = recents.read()
        if (s) : # returns false if s is a blank string
            self.rfiles = list(eval(s))
        for file in self.rfiles :
            # file.split("/")[-1] gives the name of the file without the path
            self.rfilenames.append(file.split("/")[-1])
            if (len(self.rfilenames) > 22) :
                # name sliced to 19 characters and ... added at the end
                self.rfiledisplaynames.append(self.rfilenames[-1][:20]+"...")
            else :
                self.rfiledisplaynames.append(self.rfilenames[-1])

    def makeMenu(self) :
        # menu bar
        self.menubar = self.menuBar()
        # fixed size (size does not change with window)
        self.menubar.setFixedHeight(60)
        toolbar = self.addToolBar("Controls")

        # menus
        self.fileMenu = self.menubar.addMenu("&File")
        contMenu = self.menubar.addMenu("&Controls")

        # actions
        openAction = Widgets.QAction(self, text="Open...", icon=QIcon(":ic-open.svg"))
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.opentab)
        saveAction = Widgets.QAction(self, text="Save Progress...", icon=QIcon(":ic-save.svg"))
        saveAction.setShortcut("Ctrl+S")
        playAction = Widgets.QAction(self, text="Play/Pause", icon=QIcon(":ic-play.svg"))
        playAction.setShortcut("K")
        stopAction = Widgets.QAction(self, text="Stop", icon=QIcon(":ic-stop.svg"))
        stopAction.setShortcut("Ctrl+K")
        camAction = Widgets.QAction(self, text="Toggle Camera", icon=QIcon(":ic-cam-on.svg"))
        camAction.setShortcut("Ctrl+Alt+V")
        closeAction = Widgets.QAction(self, text="Close Tab", icon=QIcon(":ic-close.svg"))
        closeAction.setShortcut("Ctrl+W")
        closeAction.triggered.connect(self.closetab)

        # opening recent menu has its own method
        self.openRMenu = self.fileMenu.addMenu("Open Recent...")
        self.makeRecentMenu()
        
        # menus
        self.fileMenu.addActions([openAction, saveAction, closeAction])
        contMenu.addActions([playAction, stopAction])
        contMenu.addSeparator()
        contMenu.addActions([camAction])

        # menu bar
        self.menubar.setStyleSheet(stylesheet)
        self.menubar.addActions([self.fileMenu.menuAction(), contMenu.menuAction()])

        # toolbar
        toolbar.addActions([openAction, saveAction, closeAction, playAction, stopAction, camAction])

    #recent menu opened here
    def makeRecentMenu(self) :
        self.openRMenu.clear()
        if (self.rfiles) :
            lastFileAction = Widgets.QAction(self, text=self.rfiles[-1].split("/")[-1])
            lastFileAction.setShortcut("Ctrl+Shift+O")
            lastFileAction.triggered.connect(lambda: self.openrecenttab(-1))
            self.openRMenu.addAction(lastFileAction)
            self.openRMenu.addSeparator()
        for i in range(len(self.rfiles)-2, -1, -1) :
            fileAction = Widgets.QAction(self, text=self.rfiles[i].split("/")[-1])
            fileAction.triggered.connect(lambda: self.openrecenttab(i))
            self.openRMenu.addAction(fileAction)
        
    # add tab bar to frame
    def buildtab(self) :
        self.tabs = Widgets.QTabWidget(self.frame)
        self.tabs.setStyleSheet(stylesheet)
        self.tabs.setMovable(True)

        self.labelNone = Widgets.QLabel('No tabs open')
        self.tabs.addTab(self.labelNone, "Home")

    def resizeEvent(self, event) :
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    # resize frame on window resize
    def resize(self) :
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.tabs.setGeometry(0, 0, int(0.8*self.width()), int(0.9*self.height()))

    # open action triggered
    def opentab(self) :
        # path to pdf.js, a tool used to view PDFs
        path_pdfjs = f"file:///{self.file_cwd}/pdfjs_copy/web/viewer.html"

        # a frame that shows web requests
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames", "", "PDF files (*.pdf)", options=options)
        self.files += files
        for file in files :
            self.filenames.append(file.split("/")[-1])
            if (len(self.filenames[-1]) > 22) :
                self.filedisplaynames.append(self.filenames[-1][:20]+"...")
            else :
                self.filedisplaynames.append(self.filenames[-1])

            if (file in self.rfiles) :
                self.rfiles.remove(file)
            self.rfiles.append(file)
            if (len(self.rfiles) > 10) :
                self.rfiles.pop(0)
            recents = open('recents.txt', 'w')
            recents.write(str(self.rfiles))
            self.read()
            self.makeRecentMenu()

            self.pdf_view = QWebEngineView()
            self.pdf_view.load(QUrl.fromUserInput("%s?file=%s" % (path_pdfjs, file)))
            self.tabs.addTab(self.pdf_view, self.filedisplaynames[-1])
            self.tabs.setTabToolTip(-1, self.filenames[-1])
            if (self.tabs.indexOf(self.labelNone) == 0) :
                self.tabs.removeTab(0)

    # file opened from "Open Recent..." menu
    def openrecenttab(self, index) :
        # path to pdf.js, a tool used to view PDFs
        path_pdfjs = f"file:///{self.file_cwd}/pdfjs_copy/web/viewer.html"

        # a frame that shows web requests
        self.pdf_view = QWebEngineView()
        self.pdf_view.load(QUrl.fromUserInput("%s?file=%s" % (path_pdfjs, self.rfiles[index])))
        self.tabs.addTab(self.pdf_view, self.rfiledisplaynames[index])
        self.tabs.setTabToolTip(-1, self.rfilenames[index])
        if (self.tabs.indexOf(self.labelNone) == 0) :
            self.tabs.removeTab(0)

        self.rfiles.append(self.rfiles.pop(index))
        recents = open('recents.txt', 'w')
        recents.write(str(self.rfiles))
        self.read()
        self.makeRecentMenu()

    # close action triggered
    def closetab(self) :
        self.tabs.removeTab(self.tabs.currentIndex())
        if (self.tabs.count() == 0) :
            self.tabs.addTab(self.labelNone, "Home")

# initializing app with system arguments
app = App(sys.argv)

#initializing custom window with random dimensions (can be changed)
win = MyWindow(1600, 1200)
win.show()

# exits program when close button is pressed
sys.exit(app.exec_())