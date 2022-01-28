from PyQt5 import QtWidgets as Widgets, QtCore, QtGui, QtWebEngineWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QObject, QThread, pyqtSignal
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication as App, QMainWindow as Window, QFileDialog
import sys, os, qrc_res, zipfile, cv2, text_detect, platform, tts, threading
import speech_recognition as speech
import except_thread as exc

# Qt widgets can be styled in CSS, so this string will work as the parent style sheet for the app
stylesheet = open('style-css.txt', 'r').read()

class MyWindow(Window) :
    page=0
    b=None
    index=0
    writing=True
    is_file_open=False
    is_started=False
    readlist=[]
    r = speech.Recognizer()
    # a signal which is triggered when the window resizes
    resized = QtCore.pyqtSignal()

    # full file path, file name, file name shortened to 22 characters
    file, filename, filedisplayname = '', '', ''
    # same as above but only for recently opened files
    rfiles, rfilenames, rfiledisplaynames = [], [], []
    # current working directory path
    file_cwd = os.getcwd().replace('\\', '/')
    with speech.Microphone() as source2:
        r.adjust_for_ambient_noise(source2, duration=0.2)
    

    def __init__(self, win_width, win_height) :
        # super call
        super(MyWindow, self).__init__()

        # making window
        self.setGeometry(0, 0, win_width, win_height)
        self.setMinimumHeight(450)
        self.setMinimumWidth(800)
        self.setWindowTitle('Dynamic Dictate')
        self.setStyleSheet(stylesheet)
        self.resized.connect(self.resize)

        # recents.txt is required for proper functioning of the program
        if (not os.path.isfile('recents.txt')) :
            newfile = open('recents.txt', 'w')
            newfile.write('[]')
            newfile.close()

        if not os.path.exists(f'{self.file_cwd}/pdfjs_copy/'):
            with zipfile.ZipFile(f'{self.file_cwd}/pdfjs_copy.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{self.file_cwd}')

        # read recent files opened
        self.read()
        # make menu bar and menus
        self.makeMenu()

        # frame containing tab layout
        self.frame = QWebEngineView(self)
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.frame.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        self.frame.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PdfViewerEnabled, True)

        # text label for webcam image
        self.image_label = Widgets.QLabel(self)
        self.image_label.setGeometry(int(0.8*self.width()), int(0.8*self.height()), int(0.2*self.width()), int(0.2*self.height()))

        # capture of the camera
        self.cap = None
        self.camon = True

        self.timer = QtCore.QTimer(self, interval=500)
        self.timer.timeout.connect(self.update_frame)
        self._image_counter = 0
        self.start_webcam()

    @QtCore.pyqtSlot()
    def start_webcam(self) :
        if (self.cap is None and self.camon) :
            self.cap = cv2.VideoCapture(0)
        self.timer.start()

    @QtCore.pyqtSlot()
    def stop_webcam(self) :
        if (self.cap is not None and  not self.camon) :
            self.cap = None

    @QtCore.pyqtSlot()
    def update_frame(self) :
        if self.camon and self.cap.isOpened() :
            _, image = self.cap.read()
            if image is not None :
                print(text_detect.detect_text(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
                cv2.resize(image, (1280, 720), interpolation=cv2.INTER_CUBIC)
                self.displayImage(image, True)
        else :
            self.displayImage(None, True)

    def displayImage(self, img, window=True) :
        outImage = None
        if self.camon :
            qformat = QtGui.QImage.Format_Indexed8
            if len(img.shape) == 3 :
                if img.shape[2] == 4 :
                    qformat = QtGui.QImage.Format_RGBA8888
                else :
                    qformat = QtGui.QImage.Format_RGB888
            outImage = QtGui.QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
            outImage = outImage.rgbSwapped()
        else :
            outImage = QtGui.QImage('res/white.png')
        if window :
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(outImage))

    def read(self) :
        # read recent files from text file
        with open('recents.txt', 'r') as recents :
            s = recents.read()
        if (s) : # returns false if s is a blank string
            self.rfiles = list(eval(s))
        for file in self.rfiles :
            # file.split('/')[-1] gives the name of the file without the path
            self.rfilenames.append(file.split('/')[-1])
            if (len(self.rfilenames) > 22) :
                # name sliced to 19 characters and ... added at the end
                self.rfiledisplaynames.append(self.rfilenames[-1][:20]+'...')
            else :
                self.rfiledisplaynames.append(self.rfilenames[-1])

    def makeMenu(self) :
        # menu bar
        self.menubar = self.menuBar()
        # fixed size (size does not change with window)
        self.menubar.setFixedHeight(40)
        toolbar = self.addToolBar('Controls')

        # menus
        self.fileMenu = self.menubar.addMenu('&File')
        contMenu = self.menubar.addMenu('&Controls')

        # actions
        openAction = Widgets.QAction(self, text='Open...', icon=QIcon(':ic-open.svg'))
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openfile)
        saveAction = Widgets.QAction(self, text='Save Progress...', icon=QIcon(':ic-save.svg'))
        saveAction.setShortcut('Ctrl+S')
        camAction = Widgets.QAction(self, text='Toggle Camera', icon=QIcon(':ic-cam-on.svg'))
        camAction.setShortcut('Ctrl+Alt+V')
        camAction.triggered.connect(self.toggleCam)

        narrAction = Widgets.QAction(self, text='Start Narration', icon=QIcon(':ic-cam-on.svg'))
        narrAction.setShortcut('K')
        narrAction.triggered.connect(self.buttonpress)

        NextAction = Widgets.QAction(self, text='Continue Narration', icon=QIcon(':ic-cam-on.svg'))
        NextAction.setShortcut('D')
        NextAction.triggered.connect(self.continue_narrate)

        PrevAction = Widgets.QAction(self, text='Repeat Narration', icon=QIcon(':ic-cam-on.svg'))
        PrevAction.setShortcut('A')
        PrevAction.triggered.connect(self.repeat_narrate)
        # opening recent menu has its own method
        self.openRMenu = self.fileMenu.addMenu('Open Recent...')
        self.makeRecentMenu()
        
        # menus
        self.fileMenu.addActions([openAction, saveAction])
        contMenu.addActions([camAction])
        contMenu.addActions([narrAction])
        # menu bar
        self.menubar.setStyleSheet(stylesheet)
        self.menubar.addActions([self.fileMenu.menuAction(), contMenu.menuAction()])
        

        # toolbar
        toolbar.addActions([openAction, saveAction, camAction, NextAction, PrevAction])

    def toggleCam(self) :
        self.camon = not self.camon
        if self.camon :
            self.start_webcam()
        else :
            self.stop_webcam()

    #recent menu opened here
    def makeRecentMenu(self) :
        self.openRMenu.clear()
        if (self.rfiles) :
            lastFileAction = Widgets.QAction(self, text=self.rfiles[-1].split('/')[-1])
            lastFileAction.setShortcut('Ctrl+Shift+O')
            lastFileAction.triggered.connect(lambda: self.openrecentfile(-1))
            self.openRMenu.addAction(lastFileAction)
            self.openRMenu.addSeparator()
        for i in range(len(self.rfiles)-2, -1, -1) :
            fileAction = Widgets.QAction(self, text=self.rfiles[i].split('/')[-1])
            fileAction.triggered.connect(lambda: self.openrecentfile(i))
            self.openRMenu.addAction(fileAction)

    def resizeEvent(self, event) :
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    # resize frame on window resize
    def resize(self) :
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.image_label.setGeometry(int(0.8*self.width()), int(0.8*self.height()), int(0.2*self.width()), int(0.2*self.height()))

    # open action triggered
    def openfile(self) :
        
        # path to pdf.js, a tool used to view PDFs
        path_pdfjs = f'file:///{self.file_cwd}/pdfjs_copy/web/viewer.html'

        # a frame that shows web requests
        options = QFileDialog.Options()
        self.file, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName', '', 'PDF files (*.pdf)', options=options)
        filename = self.file.split('/')[-1]
        if (len(filename) > 22) :
            self.filedisplayname = self.filename[:20]+'...'
        else :
            self.filedisplayname = self.filename

        if (self.file in self.rfiles) :
            self.rfiles.remove(self.file)
        self.rfiles.append(self.file)
        if (len(self.rfiles) > 10) :
            self.rfiles.pop(0)
        recents = open('recents.txt', 'w')
        recents.write(str(self.rfiles))
        self.read()
        self.makeRecentMenu()

        self.frame.load(QUrl.fromUserInput(self.file))
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.is_file_open=True

    # file opened from 'Open Recent...' menu
    def openrecentfile(self, index) :
        
        # path to pdf.js, a tool used to view PDFs
        path_pdfjs = f'file:///{self.file_cwd}/pdfjs_copy/web/viewer.html'

        # a frame that shows web requests
        self.frame.load(QUrl.fromUserInput(self.rfiles[index]))
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))

        self.rfiles.append(self.rfiles.pop(index))
        recents = open('recents.txt', 'w')
        recents.write(str(self.rfiles))
        self.read()
        self.makeRecentMenu()
        self.is_file_open=True
        self.file=self.rfiles[index]

    def start_narrate(self, path):
        self.writing=False    
        if self.page>=self.pages:
            return
        if self.index>=len(self.readlist):
            self.page+=1
            self.index=0
            self.readlist=tts.textparse(tts.pdfparse(self.page, self.file))
        self.writing=True
        a=threading.Thread(target=tts.narrate,args=(self.index,self.readlist)).start()
        self.b=exc.thread_with_exception(target=self.voicecheck)
        self.b.start()

    def buttonpress(self):      
        self.writing=True
        print('k pressed')
        if self.is_file_open:
            self.is_started=True
            self.pages=tts.getpages(self.file)
            self.readlist=tts.getfirstpage(self.file)
            self.start_narrate(self.file)

    def continue_narrate(self):
        if self.b is not None:
            self.b.raise_exception()
            self.b.join()
        print('d pressed')
        if self.is_file_open:
            if self.is_started==True:
                self.index+=1
                self.start_narrate(self.file)
    
    def repeat_narrate(self):   
        if self.b is not None:
            self.b.raise_exception()
            self.b.join()
        print('a pressed')
        if self.is_file_open:
            if self.is_started==True:
                self.start_narrate(self.file)
    
    def voicecheck(self):
        while self.writing:
            print('started')
            r = speech.Recognizer()    
            with speech.Microphone() as source:            
                print("Listening...")
                r.pause_threshold = 1
                audio = r.listen(source)        
            try:
                print("Recognizing...")   
                text = r.recognize_google(audio, language ='en-in')
                print(text)       
            except Exception as e:
                text='bruh'
                print(e)   
                print("Unable to Recognize your voice.") 
            if any(x in text for x in ['next', 'continue', 'yes', 'yeah', 'yah']):      
                a=threading.Thread(target=self.continue_narrate).start()
                self.writing=False
                break
            elif any(x in text for x in ['previous', 'back', 'no']):
                a=threading.Thread(target=self.repeat_narrate).start()
                self.writing=False
                break

if platform.system() == 'Windows' and platform.machine().endswith('64') :
    text_detect.set_tess_path(r'bin\tesseract-ocr-win64\tesseract.exe')
else :
    text_detect.set_tess_path('tesseract')

# initializing app with system arguments
app = App(sys.argv)
#initializing custom window with random dimensions (can be changed)
win = MyWindow(1600, 900)
win.show()

# exits program when close button is pressed
sys.exit(app.exec_())