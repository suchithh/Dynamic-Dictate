import platform

import cv2
import pytesseract
from PIL import Image
from textblob import TextBlob


def img_thresholding(path):
    image = cv2.imread(path,0)
    img = image.copy()
    #Global Thresholding (v=140)
    ret,img = cv2.threshold(img,140,255,cv2.THRESH_BINARY)

    #Adaptive Gaussian Thresholding
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    #Convert to RGB for tesseract
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    cv2.imwrite('output.jpg', img)
    return(Image.fromarray(img))

def detect_text(img_path):
    if platform.system()=='Windows' and platform.machine().endswith('64'):
        tesseract_path = r'tesseract-ocr-win64\tesseract.exe'
    else:
        try:
            pytesseract.get_languages(config='')
            tesseract_path = 'tesseract'
        except:
            tesseract_path = input("Enter the absolute path to the tesseract execuatable for your OS : ")
            
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    #print(pytesseract.image_to_string(img_thresholding(img_path)))

    #Texblob spelling correction and remove extraneous character
    return (TextBlob(pytesseract.image_to_string(img_thresholding(img_path))).correct()[:-2])

if __name__=="__main__":
    print(detect_text(r'testimg\test1.jpg'))
