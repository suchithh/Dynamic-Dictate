from PIL import Image
import numpy as np
import cv2
import pytesseract
from textblob import TextBlob

def clear_image(path):
    img = cv2.imread(path,0)
    # img = image.copy()
    # alpha =2.7
    # beta = -160.0
    # denoised = alpha * img + beta
    # denoised = np.clip(denoised, 0, 255).astype(np.uint8)
    # img = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    # h = img.shape[0]
    # w = img.shape[1]
    # for y in range(0, h):
    #     for x in range(0, w):
    #         if img[y, x] >= 220:
    #             img[y, x] = 255
    #         else:
    #             img[y, x] = 0
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # cv2.imwrite('output.jpg', img)
    # return(Image.fromarray(img))
    img = cv2.medianBlur(img,5)
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite('output.jpg', img)
    return(Image.fromarray(img))
tesseract_fp = r'..\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = tesseract_fp
im_path = 'test3.jpg'
print(pytesseract.image_to_string(clear_image(im_path)))
print(TextBlob(pytesseract.image_to_string(clear_image(im_path))).correct())
