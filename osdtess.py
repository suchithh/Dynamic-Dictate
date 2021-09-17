from PIL import Image
import numpy as np
import cv2
import pytesseract
from textblob import TextBlob

def img_thresholding(path):
    image = cv2.imread(path,0)
    img = image.copy()
    ret1,img = cv2.threshold(img,140,255,cv2.THRESH_BINARY)
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite('output.jpg', img)
    return(Image.fromarray(img))

def detect_text(img_path):
    tesseract_path = r'tesseract-ocr-win64\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    #print(pytesseract.image_to_string(img_thresholding(img_path)))
    return (TextBlob(pytesseract.image_to_string(img_thresholding(img_path))).correct()[:-2])

if __name__=="__main__":
    print(detect_text(r'testimg\test1.jpg'))
