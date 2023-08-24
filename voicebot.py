from datetime import datetime as dt
import speech_recognition as sr
from dotenv import load_dotenv
from io import BytesIO
from gtts import gTTS
from ctypes import *
import pygame
import openai
import sys
import os


###THIS WILL ADD TIMESTAMPS TO ALL PRINT COMMANDS 

old_out = sys.stdout

class StAmpedOut:
    nl = True
    
    def write(self, x):
        if x == '\n':
            old_out.write(x)
            self.nl = True
        elif self.nl:
            old_out.write('%s> %s' % (str(dt.now()), x))
            self.nl = False
        else:
            old_out.write(x)
    
    def flush(self):
        old_out.flush()

sys.stdout = StAmpedOut()

####THIS WILL REMOVE THE ALSA LIB ERRORS IM GETTING

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  return
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')

pygame.init()

#####THIS WILL GET THE ENV VARIABLES

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')
WAKE_WORD = os.getenv('WAKE_WORD')

######GET OPEN AI KEY FROM https://platform.openai.com/account/api-keys

openai.api_key = OPENAI_KEY

# Initialize Speech Recognition
r = sr.Recognizer()

#Function that listens form speech
def record_text():
    #Part of handling ALSA LIB errors
    asound.snd_lib_error_set_handler(c_error_handler)
    while(1):
        #Exception Handling on Speech Recognition
        try:
            with sr.Microphone() as source:
            #use get_mics.py to find the microphone index of the mic you would like to use, or just use sr.Microphone() for the default mic.
                # The duration parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. 
                # This value should be at least 0.5 in order to get a representative sample of the ambient noise.
                r.adjust_for_ambient_noise(source, duration=0.5)
                printit("listening...")
                # listen for the first phrase and extract it into audio data
                audio = r.listen(source)
                printit("sending to google...")
                MyText = r.recognize_google(audio)

                printit(f"I heard: {MyText}")
                if MyText.startswith(WAKE_WORD):
                    printit("got wake word...")
                    MyText = MyText[len(WAKE_WORD)+1:]
                    return MyText

        except sr.RequestError as e:
            printit("Could not request results: {0}".format(e))
        except sr.UnknownValueError:
            printit("unknown error occurred")
    #Part of handling ALSA LIB errors
    asound.snd_lib_error_set_handler(None)

def send_to_chatGPT(messages, model="gpt-3.5-turbo"):

    printit("waiting for OpenAI to respond...")

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    printit("ChatGPT says...")
    message = response.choices[0].message.content
    printit(f"TARS: {message}")
    messages.append(response.choices[0].message)
    return message

def output_text(text):
    f = open("output.txt", "a")
    f.write(text)
    f.write("\n")
    f.close()
    return

def printit(statement):
    if statement.startswith("TARS: "):
        lines = statement.splitlines()
        for line in lines:
            if line.startswith("TARS: "):
                print(line)
                output_text(line)
            else:
                if line.strip():
                    print("TARS: " +line)
                    output_text("TARS: " +line)
    
    elif statement.startswith("USER: "):
        print(statement)
        output_text(statement)
    else:
        print(statement)

def SpeakText(response):
    tts = gTTS(text=response, lang='en')
    printit("waiting for Google TTS to respond...")
    fp = BytesIO()
    printit("writing respose to memory...")
    tts.write_to_fp(fp)
    fp.seek(0)
    printit("playing respose...")
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


messages = [{"role": "system", "content": "You are TARS a witty, sarcastic, and humorous robot companion from the Movie Interstellar. Respond only as TARS, including whitty banter."}]
printit("Starting...")
while(1):
    text = record_text()
    printit(f"USER: {text}")
    messages.append({"role": "user", "content": text})
    response = send_to_chatGPT(messages)
    SpeakText(response)
