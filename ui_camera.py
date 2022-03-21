from turtle import title
from PyQt5 import QtWidgets, QtCore, QtGui
import cv2, sys
from pynput.keyboard import Key, Controller
import time, platform, os
import text_detect, except_thread as exc
stylesheet = open('style-css.txt', 'r').read()

class PreferencesDialog(QtWidgets.QDialog) :

    prevtext=''
    text=''
    f = None

    def __init__(self) :
        super(PreferencesDialog, self).__init__()
        self.setFixedSize(1280, 720)
        self.setWindowTitle('OCR whatever')
        self.setStyleSheet(stylesheet)
        self.cap = None
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vertical_layout)

        self.horizontal_layout_1 = QtWidgets.QHBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout_1)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(int(0.85*self.width()), int(0.85*self.height()))
        self.horizontal_layout_1.addWidget(self.image_label, alignment=QtCore.Qt.AlignVCenter)

        self.horizontal_layout_2 = QtWidgets.QHBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout_2)

        self.stop_button = QtWidgets.QPushButton(text='Stop')
        self.stop_button.setFixedSize(int(0.2*self.width()), int(0.05*self.height()))
        self.horizontal_layout_2.addWidget(self.stop_button, alignment=QtCore.Qt.AlignVCenter)
        self.stop_button.clicked.connect(self.stop_webcam)
        self.start_webcam()

    @QtCore.pyqtSlot()
    def start_webcam(self) :
        if (self.cap is None) :
            self.cap = cv2.VideoCapture(0)
        self.f = exc.thread_with_exception(target = self.update_frame)
        self.f.start()

    @QtCore.pyqtSlot()
    def stop_webcam(self) :
        if (self.cap is not None) :
            self.cap = None
        if self.f is not None :
            self.f.raise_exception()
            self.f.join()
            self.f = None
        self.close()

    @QtCore.pyqtSlot()
    def update_frame(self) :
        counter = 0
        coords_tl, coords_br, self.text = None, None, None
        while self.cap.isOpened() :
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
        
        qformat = QtGui.QImage.Format_Indexed8
        if len(img.shape) == 3 :
            if img.shape[2] == 4 :
                qformat = QtGui.QImage.Format_RGBA8888
            else :
                qformat = QtGui.QImage.Format_RGB888
        outImage = QtGui.QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        if window :
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(outImage))
    
    def keyboard_type(self):
        keyboard=Controller()
        if not len(self.text) < 2:
            for i in self.prevtext:
                keyboard.press(Key.backspace)
                keyboard.release(Key.backspace)
            for i in self.text:              
                keyboard.press(i)
            self.prevtext=self.text

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
app = QtWidgets.QApplication(sys.argv)
#initializing custom window with random dimensions (can be changed)
win = PreferencesDialog()
win.show()

# exits program when close button is pressed
sys.exit(app.exec_())