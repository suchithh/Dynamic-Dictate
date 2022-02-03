from gtts import gTTS
import pdfplumber
from pygame import mixer, time
from datetime import datetime
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import keyboard
from difflib import SequenceMatcher
import speech_recognition as speech
import threading
import ui_settings



pages=1 
n=5 #setting for number of words to be read at once at max
repeat=False 
slow=False #setting for slow/normal speed reading
writing=True
path="Harry_Potter_and_The_Sorcerers_Stone.pdf" #give path here
tld='us' #accent setting

def delete_cache():
    for file in os.listdir():
        if '.mp3' in file:
            os.remove(file)


def getpages(path):
    global n
    global slow
    global tld
    settings=ui_settings.read_settings()
    if settings['Narration']['Speed']=='Normal':
        slow=False
    else:
        slow=True
    if settings['Narration']['Region']=='English (India)':
        tld='co.in'
    elif settings['Narration']['Region']=='English (UK)':
        tld='co.uk'
    else:
        tld='us'
    n=int(settings['Narration']['Maximum_Words_Read'])
    with pdfplumber.open(path) as pdf:
        pages=len(pdf.pages)
        return pages #procures number of pages

def pdfparse(pageno, path): 
    text=""
    with pdfplumber.open(path) as pdf:
        data = pdf.pages[pageno]
        text+=data.extract_text()+" " #parses a page in the pdf as a string
    return text

def textparse(text):
    words=text.split(" ")
    readlist=[]
    index=0
    text=''
    for word in words: #converts the string into a list of strings of max length n words each, divided by '.'
        if word !='':
            if word!='\n':
                text+=word+' '
            if word[-1]=='.':
                if text!='':
                    readlist.append(text)
                index=0
                text=''
            elif word=='\n':
                if text!='':
                    readlist.append(text)
                index=0
                text=''
            elif index==n:
                if text!='':
                    readlist.append(text)
                text=''
                index=0
            index+=1
    return readlist

def Audiobookparse(pageno, path): 
    text=""
    with pdfplumber.open(path) as pdf:
        data = pdf.pages[pageno]
        text+=data.extract_text()+" " #parses a page in the pdf as a string
    return text
# def imagechecker(checktext, path, pages, page, index, writing):
#     if image_check(checktext)>0.2:
#         writing=False
#         repeat=False
#         pagereader(path, pages, page, index, writing, repeat)


# def image_check(checktext): #compares text to ocr to determine wheter the user has finished writing
#     temp=''
#     return SequenceMatcher(None, checktext, temp).ratio()

def narrate(current_index,readlist):
    print('narrating')
    date_string = datetime.now().strftime("%d%m%Y%H%M%S") #generates an mp3 file with a unique name
    filename = "voice"+date_string+".mp3"
    speech = gTTS(text = readlist[current_index], lang='en', tld=tld, slow=slow) #initiates gtts with en-us could give user option to choose
    with open (filename,'wb') as file:
        speech.write_to_fp(file)
    mixer.init()
    mixer.music.load(filename) #plays mp3 using pygame mixer
    mixer.music.play()
    while mixer.music.get_busy(): 
        time.Clock().tick(10)
    mixer.quit()
    os.remove(filename) #deletes temp file

def getfirstpage(path):
    return textparse(pdfparse(0, path))



