from gtts import gTTS
import pdfplumber
from pygame import mixer, time
from datetime import datetime
import os
import keyboard
from difflib import SequenceMatcher
import speech_recognition as sr
import threading
pages=1 
n=5 #setting for number of words to be read at once at max
repeat=False 
slow=False #setting for slow/normal speed reading
writing=False
r = sr.Recognizer()
with sr.Microphone() as source2:
    r.adjust_for_ambient_noise(source2, duration=0.2)
def getpages():
    with pdfplumber.open(r"E:\MATH PRACTICAL NOTES TO BE WRITTEN IN RECORD CLASS 12.pdf") as pdf:
        global pages 
        pages=len(pdf.pages) #procures number of pages
def pdfparse(pageno): 
    text=""
    with pdfplumber.open(r"E:\MATH PRACTICAL NOTES TO BE WRITTEN IN RECORD CLASS 12.pdf") as pdf:
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
def keypress():
    global writing
    global repeat    
    if keyboard.is_pressed('space') or keyboard.is_pressed('right'):
        repeat=False
        writing=False
        return None
    elif keyboard.is_pressed('left'):
        repeat=True
        writing=False
        return None

def imagechecker(checktext):
    global writing
    if image_check(checktext)>0.2:
        writing=False
        repeat=False
        return None

def voicecheck():
    print('started')
    global writing
    global repeat
    while writing:
        try:
            with sr.Microphone() as source2:                        
                audio2 = r.listen(source2)
                MyText = r.recognize_google(audio2)
                text = MyText.lower()  
                print(text)
                if text != None:
                    if any(text in x for x in ['next', 'continue', 'yes', 'yeah', 'yah']):                        
                        repeat=False
                        writing= False
                        break
                    elif any(text in x for x in ['previous', 'back', 'no']):
                        repeat=True
                        writing= False
                        break
        except sr.RequestError as e:
            print('error')
            pass                    
        except sr.UnknownValueError:
            print('error')
            pass
    else:
        print('stopped')
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
        if index>=len(readlist):
            break
        if repeat:
            index-=1
            narrate(index,readlist)
        else:
            narrate(index,readlist)
        writing=True
        c=threading.Thread(target=voicecheck).start()
        while writing:
            a=threading.Thread(target=keypress).start()           
            b=threading.Thread(target=image_check(readlist[index])).start()
        index+=1