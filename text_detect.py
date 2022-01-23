import platform
import cv2
import pytesseract
from PIL import Image
from autocorrect import Speller

import time

def img_thresholding(image):
    img = image.copy()

    #Adaptive Thresholding
    #img = cv2.adaptiveThreshold(img,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    
    # Otsu Thresholding
    blur = cv2.GaussianBlur(img,(5,5),0)
    dump, img = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #Convert to RGB for tesseract
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #Write output to file
    cv2.imwrite('output.jpg', img)

    return(Image.fromarray(img))

def detect_text(img_path):
    spell_check = Speller(only_replacements=True)
    return(spell_check(pytesseract.image_to_string(img_thresholding(img_path)))[:-2])
    
    #Texblob spelling correction and remove extraneous character
    #return (TextBlob(pytesseract.image_to_string(img_thresholding(img_path))).correct()[:-2])
    #Without spell check
    #return (pytesseract.image_to_string(img_thresholding(img_path)))


def set_tess_path(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def main():
    set_tess_path(r'bin\tesseract-ocr-win64\tesseract.exe')
    print(detect_text(cv2.imread(r'testimg\test1.jpg',0)))

if __name__=="__main__":
    main()


#Test webcam code
# video = cv2.VideoCapture(0)
# video.set(3, 640)
# video.set(4, 480)

# while True:
# 	vidframe = vs.read()
# 	vidframe = imutils.resize(vidframe, width=400)
# 	# grab the frame dimensions and convert it to a blob
# 	# (h, w) = vidframe.shape[:2]
# 	# vidframeblob = cv2.resize(vidframe, (300, 300))
#     print (detect_text(vidframe))