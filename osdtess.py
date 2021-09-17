from PIL import Image
import numpy as np
import cv2
import pytesseract
from textblob import TextBlob

def clear_image(path):
    image = cv2.imread(path)
    img = image.copy()
    alpha =2.7
    beta = -160.0
    denoised = alpha * img + beta
    denoised = np.clip(denoised, 0, 255).astype(np.uint8)
    img = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    h = img.shape[0]
    w = img.shape[1]
    for y in range(0, h):
        for x in range(0, w):
            if img[y, x] >= 220:
                img[y, x] = 255
            else:
                img[y, x] = 0
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite('output.jpg', img)
    return(Image.fromarray(img))

tesseract_fp = r'tesseract-ocr-win64\tesseract.exe'
im_path = r'testimg\test1.jpg'

pytesseract.pytesseract.tesseract_cmd = tesseract_fp
print(pytesseract.image_to_string(clear_image(im_path)))
print(TextBlob(pytesseract.image_to_string(clear_image(im_path))).correct())
