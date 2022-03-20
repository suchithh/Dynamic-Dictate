from ctypes import alignment
from operator import imod
from tracemalloc import stop
from PyQt5 import QtWidgets as Widgets, QtCore, QtGui, QtWebEngineWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QObject, QThread, pyqtSignal
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication as App, QMainWindow as Window, QFileDialog
import sys, os, qrc_res, zipfile, cv2, text_detect, platform, tts, threading, speech_recognition as speech, except_thread as exc, ui_settings
from difflib import SequenceMatcher
import asyncio
import time
# Qt widgets can be styled in CSS, so this string will work as the parent style sheet for the app
stylesheet = open('style-css.txt', 'r').read()

class MyWindow(Window) :
    text = ''
    page = 0
    b = None
    d = None
    c = None
    e = None
    f = None
    index = 0
    writing = True
    is_file_open = False
    is_started = False
    is_audiobook =  False
    readlist = []
    r = speech.Recognizer()
    settings = ui_settings.read_settings()
    n = int(settings['Narration']['Maximum_Words_Read'])
    # a signal which is triggered when the window resizes
    resized = QtCore.pyqtSignal()

    # full file path, file name, file name shortened to 22 characters
    file, filename, filedisplayname = '', '', ''
    # same as above but only for recently opened files
    rfiles, rfilenames, rfiledisplaynames = [], [], []
    # current working directory path
    file_cwd = os.getcwd().replace('\\', '/')
    with speech.Microphone() as source2:
        r.adjust_for_ambient_noise(source2, duration = 0.2)
    

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

        # path to pdf.js, a tool used to view PDFs
        self.path_pdfjs = f'file:///{self.file_cwd}/pdfjs_copy/web/viewer.html'

        # recents.txt is required for proper functioning of the program
        if (not os.path.isfile('recents.txt')) :
            newfile = open('recents.txt', 'w')
            newfile.write('[]')
            newfile.close()

        if not os.path.exists(f'{self.file_cwd}/pdfjs_copy/') :
            with zipfile.ZipFile(f'{self.file_cwd}/pdfjs_copy.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{self.file_cwd}')

        # read recent files opened
        self.read()
        # make menu bar and menus
        self.make_menu()

        # frame containing tab layout
        self.frame = QWebEngineView(self)
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.frame.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        self.frame.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PdfViewerEnabled, True)

        # text label for webcam image
        self.image_label = Widgets.QLabel(self)
        self.image_label.setGeometry(int(0.8*self.width()), int(0.8*self.height()), int(0.2*self.width()), int(0.2*self.height()))

        # group boxes for holding text pieces, detected and narrated
        self.text_read_group = Widgets.QGroupBox(self, title = 'Text detected:')
        self.text_narrated_group = Widgets.QGroupBox(self, title = 'Text narrated:')
        self.text_read_group.setGeometry(int(0.8*self.width()), int(0.2*self.height()), int(0.2*self.width()), int(0.15*self.height()))
        self.text_narrated_group.setGeometry(int(0.8*self.width()), int(0.4*self.height()), int(0.2*self.width()), int(0.15*self.height()))
        self.text_read_layout = Widgets.QVBoxLayout()
        self.text_narrated_layout = Widgets.QVBoxLayout()
        self.text_read = Widgets.QLabel(self.text_read_group)
        self.text_read_layout.addWidget(self.text_read)
        self.text_narrated = Widgets.QLabel(self.text_narrated_group)
        self.text_narrated_layout.addWidget(self.text_narrated)
        self.text_read_group.setLayout(self.text_read_layout)
        self.text_narrated_group.setLayout(self.text_narrated_layout)

        # group box for text detected by mic and status of mic
        self.mic_group = Widgets.QGroupBox(self, title = 'Mic input:')
        self.mic_group.setGeometry(int(0.8*self.width()), int(0.6*self.height()), int(0.2*self.width()), int(0.15*self.height()))
        self.mic_layout = Widgets.QVBoxLayout()
        self.mic_detected = Widgets.QLabel(self.mic_group)
        self.mic_status = Widgets.QHBoxLayout()
        self.mic_status_icon = Widgets.QToolButton(icon = QIcon(':ic-mic-off.svg'))
        self.mic_status_text = Widgets.QLabel(text = 'Mic off')
        self.mic_status.addWidget(self.mic_status_icon)
        self.mic_status.addWidget(self.mic_status_text)
        self.mic_layout.addWidget(self.mic_detected)
        self.mic_status_widget = Widgets.QWidget()
        self.mic_status_widget.setLayout(self.mic_status)
        self.mic_layout.addWidget(self.mic_status_widget)
        self.mic_group.setLayout(self.mic_layout)

        # capture of the camera
        self.cap = None
        self.camon = self.settings['On-Startup']['Camera-on']
        self._image_counter = 0
        self.start_webcam()

    @QtCore.pyqtSlot()
    def start_webcam(self) :
        if (self.cap is None and self.camon) :
            self.cap = cv2.VideoCapture(0)
            self.f = exc.thread_with_exception(target = self.update_frame)
            self.f.start()

    @QtCore.pyqtSlot()
    def stop_webcam(self) :
        if (self.cap is not None and not self.camon) :
            self.cap = None
        if self.f is not None :
            self.f.raise_exception()
            self.f.join()
            self.f = None

    @QtCore.pyqtSlot()
    def update_frame(self) :
        counter = 0
        coords_tl, coords_br, self.text = None, None, None
        while self.camon and self.cap.isOpened() :
            _, image = self.cap.read()
            if image is not None :
                counter += 1
                if counter == 10 :
                    coords_tl, coords_br, self.text = text_detect.detect_text(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
                    print(self.text)
                    counter = 0
                if coords_br and coords_tl :
                    if ('x' in coords_br and 'x' in coords_tl and 'y' in coords_br and 'y' in coords_tl) :
                        image = cv2.rectangle(image,(coords_tl['x'],coords_tl['y']),(coords_br['x'],coords_br['y']),(0,0,255),2)
                width = self.image_label.width()
                height = self.image_label.height()
                image = cv2.resize(image, (width, height), interpolation = cv2.INTER_CUBIC)
                self.display_image(image, True)
        else :
            self.display_image(None, True)

    def display_image(self, img, window = True) :
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

    def make_menu(self) :
        # menu bar
        self.menubar = self.menuBar()
        # fixed size (size does not change with window)
        self.menubar.setFixedHeight(40)
        toolbar = self.addToolBar('Controls')

        # menus
        self.fileMenu = self.menubar.addMenu('&File')
        contMenu = self.menubar.addMenu('&Controls')

        # actions
        openAction = Widgets.QAction(self, text = 'Open...', icon = QIcon(':ic-open.svg'))
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.open_file)
        saveAction = Widgets.QAction(self, text = 'Save Progress...', icon = QIcon(':ic-save.svg'))
        saveAction.setShortcut('Ctrl+S')

        self.camAction = Widgets.QAction(self, text = 'Toggle Camera')
        if (self.settings['On-Startup']['Camera-on']) :
            self.camAction.setIcon(QIcon(':ic-cam-off.svg'))
        else :
            self.camAction.setIcon(QIcon(':ic-cam-on.svg'))
        self.camAction.setShortcut('Ctrl+Alt+V')
        self.camAction.triggered.connect(self.toggle_cam)

        narrAction = Widgets.QAction(self, text = 'Start Narration', icon = QIcon(':ic-play.svg'))
        narrAction.setShortcut('K')
        narrAction.triggered.connect(self.buttonpress)
        nextAction = Widgets.QAction(self, text = 'Continue Narration', icon = QIcon(':ic-next.svg'))
        nextAction.setShortcut('D')
        nextAction.triggered.connect(self.continue_narrate)
        prevAction = Widgets.QAction(self, text = 'Repeat Narration', icon = QIcon(':ic-prev.svg'))
        prevAction.setShortcut('A')
        prevAction.triggered.connect(self.repeat_narrate)

        stopAction = Widgets.QAction(self, text = 'Stop Narration', icon = QIcon(':ic-stop.svg'))
        stopAction.setShortcut('X')
        stopAction.triggered.connect(self.stop_narrate)

        audioAction = Widgets.QAction(self, text = 'Read as Audiobook', icon = QIcon(':ic-read.svg'))
        audioAction.setShortcut('R')
        audioAction.triggered.connect(self.start_audiobook)

        setAction = Widgets.QAction(self, text = 'Preferences', icon = QIcon(':ic-settings.svg'))
        setAction.setShortcut('Ctrl+Shift+P')
        setAction.triggered.connect(self.open_settings)

        # opening recent menu has its own method
        self.openRMenu = self.fileMenu.addMenu('Open Recent...')
        self.make_recent_menu()
        
        # menus
        self.fileMenu.addActions([openAction, saveAction, setAction])
        contMenu.addActions([self.camAction, narrAction, stopAction, audioAction])
        # menu bar
        self.menubar.setStyleSheet(stylesheet)
        self.menubar.addActions([self.fileMenu.menuAction(), contMenu.menuAction()])
        

        # toolbar
        toolbar.addActions([openAction, saveAction, self.camAction, narrAction, prevAction, nextAction, stopAction, audioAction])

    def toggle_cam(self) :
        self.camon = not self.camon
        if self.camon :
            self.start_webcam()
            self.camAction.setIcon(QIcon(':ic-cam-off.svg'))
        else :
            self.stop_webcam()
            if self.f is not None:
                self.f.raise_exception()
                self.f.join()
                self.f=None
            self.camAction.setIcon(QIcon(':ic-cam-on.svg'))

    def open_settings(self) :
        dialog = ui_settings.PreferencesDialog()
        dialog.exec_()
        dialog.show()
        self.settings = ui_settings.read_settings()

    #recent menu opened here
    def make_recent_menu(self) :
        self.openRMenu.clear()
        if (self.rfiles) :
            lastFileAction = Widgets.QAction(self, text = self.rfiles[-1].split('/')[-1])
            lastFileAction.setShortcut('Ctrl+Shift+O')
            lastFileAction.triggered.connect(lambda: self.open_recent_file(-1))
            self.openRMenu.addAction(lastFileAction)
            self.openRMenu.addSeparator()
        for i in range(len(self.rfiles)-2, -1, -1) :
            fileAction = Widgets.QAction(self, text = self.rfiles[i].split('/')[-1])
            fileAction.triggered.connect(lambda: self.open_recent_file(i))
            self.openRMenu.addAction(fileAction)

    def resizeEvent(self, event) :
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    # resize frame on window resize
    def resize(self) :
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.image_label.setGeometry(int(0.8*self.width()), int(0.8*self.height()), int(0.2*self.width()), int(0.2*self.height()))
        self.text_read_group.setGeometry(int(0.8*self.width()), int(0.2*self.height()), int(0.2*self.width()), int(0.15*self.height()))
        self.text_narrated_group.setGeometry(int(0.8*self.width()), int(0.4*self.height()), int(0.2*self.width()), int(0.15*self.height()))
        self.mic_group.setGeometry(int(0.8*self.width()), int(0.6*self.height()), int(0.2*self.width()), int(0.15*self.height()))

    # open action triggered
    def open_file(self) :
        # a frame that shows web requests
        options = QFileDialog.Options()
        self.file, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName', '', 'PDF files (*.pdf)', options = options)
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
        self.make_recent_menu()

        # a frame that shows web requests
        self.frame.load(QUrl.fromUserInput(f'{self.path_pdfjs}?file={self.file}'))
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.is_file_open = True

    # file opened from 'Open Recent...' menu
    def open_recent_file(self, index) :
        # a frame that shows web requests
        self.frame.load(QUrl.fromUserInput(f'{self.path_pdfjs}?file={self.rfiles[index]}'))
        self.frame.setGeometry(0, int(0.1*self.height()), int(0.8*self.width()), int(0.9*self.height()))
        self.file = self.rfiles[index]

        self.rfiles.append(self.rfiles.pop(index))
        recents = open('recents.txt', 'w')
        recents.write(str(self.rfiles))
        self.read()
        self.make_recent_menu()
        self.is_file_open = True

    def start_narrate(self, path) :
        self.writing = False    
        if self.page >= self.pages :
            return
        if self.index >=  len(self.readlist) :
            self.page += 1
            self.frame.load(QUrl.fromUserInput(f'{self.path_pdfjs}?file={self.file}#page={(self.page+1)}'))
            self.index = 0
            self.readlist = tts.textparse(tts.pdfparse(self.page, self.file))
        self.writing = True
        self.d = exc.thread_with_exception(target = self.start_tts)
        self.d.start()
        self.b = exc.thread_with_exception(target = self.voicecheck)
        self.b.start()
        self.e =  exc.thread_with_exception(target = self.camcheck)
        self.e.start()
    

    def start_tts(self) :
        tts.narrate(self.index, self.readlist)
        self.text_narrated.setText(self.readlist[self.index])
        # self.readlist[self.index] is the string being read out
        if self.d is not None :
                self.d.raise_exception()
                self.d.join()
    
    def buttonpress(self) :      
        self.writing = True
        if self.is_file_open :
            self.is_started = True
            self.pages = tts.getpages(self.file)
            self.readlist = tts.getfirstpage(self.file)
            self.start_narrate(self.file)

    def continue_narrate(self) :
        if self.b is not None :
            self.b.raise_exception()
            self.b.join()
            if self.d is not None :
                self.d.raise_exception()
                self.d.join()
                tts.mixer.quit()
                tts.delete_cache()
            if self.e is not None:
                self.e.raise_exception()
                self.e.join()
        if self.is_file_open :
            if self.is_started :
                self.index += 1
                self.start_narrate(self.file)
    
    def repeat_narrate(self) :   
        if self.b is not None :
            self.b.raise_exception()
            self.b.join()
            if self.d is not None :
                self.d.raise_exception()
                self.d.join()
                tts.mixer.quit()
                tts.delete_cache()
            if self.e is not None:
                self.e.raise_exception()
                self.e.join()
        if self.is_file_open :
            if self.is_started :
                self.start_narrate(self.file)
    
    def voicecheck(self) :
        while self.writing:
            r = speech.Recognizer()    
            with speech.Microphone() as source :
                self.mic_status_icon.setIcon(QIcon(':ic-mic-on.svg'))
                self.mic_status_text.setText('Listening')
                if not any(x in self.mic_detected.text() for x in ['next', 'continue', 'yes', 'yeah', 'yah', 'previous', 'back', 'no', 'repeat']) :
                    self.mic_detected.setText('')
                r.pause_threshold = 1
                audio = r.listen(source)        
            try : 
                self.mic_status_icon.setIcon(QIcon(':ic-mic-recog.svg'))
                self.mic_status_text.setText('Recognizing')
                text = r.recognize_google(audio, language = 'en-in')
                print(text)
                self.mic_detected.setText(text)   
            except Exception as e :
                text = 'bruh'
                print(e)   
                self.mic_detected.setText('Unable to recognize.')
            if any(x in text for x in ['next', 'continue', 'yes', 'yeah', 'yah']) :      
                a = threading.Thread(target = self.continue_narrate).start()
                self.writing = False
                break
            elif any(x in text for x in ['previous', 'back', 'no', 'repeat']) :
                a = threading.Thread(target = self.repeat_narrate).start()
                self.writing = False
                break
    
    def stop_narrate(self) :
        if self.is_file_open :
            if self.is_started and not self.is_audiobook :
                self.is_started = False
                if self.b is not None :
                    self.b.raise_exception()
                    self.b.join()
                    tts.delete_cache()
                if self.e is not None :
                    self.e.raise_exception()
                    self.e.join()
            elif not self.is_started and self.is_audiobook :
                self.is_audiobook = False
                if self.c is not None :
                    self.c.raise_exception()
                    self.c.join()
                    tts.mixer.quit()
                    tts.delete_cache()

    def start_audiobook(self) :
        if self.is_file_open:
            if not self.is_started :
                self.is_audiobook = True
                self.pages = tts.getpages(self.file)
                self.c = exc.thread_with_exception(target = self.read_audiobook)
                self.c.start()
    
    def read_audiobook(self) :    
        for page in range(self.pages) :
            text = [tts.Audiobookparse(page, self.file).replace('\n','')]
            tts.narrate(0,text)
    
    def camcheck(self):
        while self.writing:
            temp = self.readlist[self.index]
            indexer = len(temp.split())
            checktext = ''
            # checktext is the string detected by Google
            words = self.text.split()
            if len(words)>= indexer :
                listwords = words[len(words)-indexer::]
                checktext = ' '.join(listwords)
                if SequenceMatcher(None, checktext.lower(), temp.lower()).ratio()>0.5:
                    print(checktext)
                    self.text_read.setText(checktext)
                    a = threading.Thread(target = self.continue_narrate).start()
                    self.writing = False
                    break
    
if platform.system() == 'Windows' and platform.machine().endswith('64') :
    text_detect.set_tess_path(r'bin\tesseract-ocr-win64\tesseract.exe')
else :
    text_detect.set_tess_path('tesseract')
try:
    os.mkdir('temp')
except FileExistsError:
    pass
text_detect.get_key()

# initializing app with system arguments
app = App(sys.argv)
#initializing custom window with random dimensions (can be changed)
win = MyWindow(1600, 900)
win.show()

# exits program when close button is pressed
sys.exit(app.exec_())