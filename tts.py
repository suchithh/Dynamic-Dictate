from gtts import gTTS
import pdfplumber
from pygame import mixer, time
from datetime import datetime
import os
import keyboard
from difflib import SequenceMatcher
pages=1 
n=5 #setting for number of words to be read at once at max
repeat=False 
slow=False #setting for slow/normal speed reading
def getpages():
    with pdfplumber.open(r'Harry Potter and The Sorcerer’s Stone.pdf') as pdf:
        global pages 
        pages=len(pdf.pages) #procures number of pages
def pdfparse(pageno): 
    text=""
    with pdfplumber.open(r'Harry Potter and The Sorcerer’s Stone.pdf') as pdf:
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
def check_if_writing(checktext): #checks for user input/ when user is done writing   
    global repeat    
    if keyboard.is_pressed('space') or keyboard.is_pressed('right'):
        repeat=False
        return False
    elif keyboard.is_pressed('left'):
        repeat=True
        return False
    elif image_check(checktext)>0.2:
        repeat=False
        return False    
    return True

def image_check(checktext): #compares text to ocr to determine wheter the user has finished writing
    temp=''
    return SequenceMatcher(None, checktext, temp).ratio()


def narrate(current_index,readlist):
    date_string = datetime.now().strftime("%d%m%Y%H%M%S") #generates an mp3 file with a unique name
    filename = "voice"+date_string+".mp3"
    speech = gTTS(text = readlist[current_index], lang='en', tld='us', slow=slow) #initiates gtts with en-us could give user option to choose
    with open (filename,'wb') as file:
        speech.write_to_fp(file)
    mixer.init()
    mixer.music.load(filename) #plays mp3 using pygame mixer
    mixer.music.play()
    while mixer.music.get_busy(): 
        time.Clock().tick(10)
    mixer.quit()
    os.remove(filename) #deletes temp file

getpages()
#driver code
for page in range(pages):
    readlist=textparse(pdfparse(page))
    index=0
    while True:
        if repeat:
            index-=1
            narrate(index,readlist)
        else:
            narrate(index,readlist)
        writing=True
        while writing:
            writing=check_if_writing(readlist[index])
        index+=1