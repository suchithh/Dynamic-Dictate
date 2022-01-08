from gtts import gTTS
import pdfplumber
from pygame import mixer, time
from datetime import datetime
import os
import keyboard
pages=1
n=5
def getpages():
    with pdfplumber.open(r'Harry Potter and The Sorcerer’s Stone.pdf') as pdf:
        global pages
        pages=len(pdf.pages)
def pdfparse(pageno):
    text=""
    with pdfplumber.open(r'Harry Potter and The Sorcerer’s Stone.pdf') as pdf:
        data = pdf.pages[pageno]
        text+=data.extract_text()+" "
    return text
def textparse(text):
    words=text.split(" ")
    readlist=[]
    index=0
    text=''
    for word in words:
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
def check_if_writing(checktext):
    return not keyboard.is_pressed('space')
def narrate(current_index,readlist):
    date_string = datetime.now().strftime("%d%m%Y%H%M%S")
    filename = "voice"+date_string+".mp3"
    speech = gTTS(text = readlist[current_index], lang='en', tld='com', slow=True)
    with open (filename,'wb') as file:
        speech.write_to_fp(file)
    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()
    while mixer.music.get_busy(): 
        time.Clock().tick(10)
    mixer.quit()
    os.remove(filename)

getpages()
for page in range(pages):
    readlist=textparse(pdfparse(page))
    for index in range(len(readlist)):
        narrate(index,readlist)
        writing=True
        while writing:
            writing=check_if_writing(readlist[index])