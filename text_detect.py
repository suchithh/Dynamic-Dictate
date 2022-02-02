import cv2
import pytesseract
from PIL import Image
from autocorrect import Speller
import base64
import requests
import json
import os

API_KEY = None

def get_key():
    global API_KEY
    if API_KEY==None:
        with open("./key/api_key.txt","r") as key_text:
            API_KEY = key_text.readline().rstrip()

def set_tess_path(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path

def img_thresholding(image):
    img = image.copy()
    # Adaptive Thresholding
    # img = cv2.adaptiveThreshold(img,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    # Otsu Thresholding
    blur = cv2.GaussianBlur(img,(5,5),0)
    _, img = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)     # Convert to RGB for tesseract
    #cv2.imwrite('output.jpg', img)                # Write output to file
    return(Image.fromarray(img))

def api_detect(image):
    global API_KEY
    cv2.imwrite("./temp/currframe.jpg", image)
    with open("./temp/currframe.jpg", "rb") as tempimg:
        converted_string = base64.b64encode(tempimg.read())
    data_obj = {"requests": [{
        "image": {"content": converted_string.decode('utf-8')},
        "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
    }]}
    api_return = requests.post("https://vision.googleapis.com/v1/images:annotate?key={}".format(API_KEY), json=data_obj)
    api_return = json.loads(api_return.text)
    complete_text = api_return['responses'][0]['textAnnotations'][0]['description']
    coords_tl = api_return['responses'][0]['textAnnotations'][0]['boundingPoly']['vertices'][0]
    coords_br = api_return['responses'][0]['textAnnotations'][0]['boundingPoly']['vertices'][2]
    cv2.imwrite('output.jpg', image)
    return (coords_tl, coords_br, complete_text)

def detect_text(image):
    spell_check = Speller()
    thr_img = img_thresholding(image)
    ocr_data = pytesseract.image_to_data(thr_img, output_type=pytesseract.Output.DICT)
    if (sum(list(map(int,ocr_data['conf'])))/len(ocr_data))>97:
        return({'x': 0, 'y': 0}, {'x': 0, 'y': 0}, spell_check(pytesseract.image_to_string(thr_img))[:-2])
    else:
        return(api_detect(image))
    #Texblob spelling correction and remove extraneous character
    #return (TextBlob(pytesseract.image_to_string(img_thresholding(img_path))).correct()[:-2])
    #Without spell check
    #return (pytesseract.image_to_string(img_thresholding(img_path)))

def main():
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass
    get_key()
    set_tess_path(r'bin\tesseract-ocr-win64\tesseract.exe')
    print(detect_text(cv2.imread(r'testimg\test2.png',0)))

if __name__=="__main__":
    main()