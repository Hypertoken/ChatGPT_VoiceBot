from datetime import datetime as dt
import speech_recognition as sr
from dotenv import load_dotenv
from io import BytesIO
from gtts import gTTS
from ctypes import *
import platform
import pygame
import openai
import sys
import os

#Setup the Identitiy of the Voice Bot.
identity="You are TARS a witty, sarcastic, and humorous robot companion from the Movie Interstellar. Respond only as TARS, including witty banter."
Chat_Name = "TARS"

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

##### Initalize pygame for playing audio

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
                r.adjust_for_ambient_noise(source, duration=5)
                printit("listening...")
                # listen for the first phrase and extract it into audio data
                audio = r.listen(source)
                printit("sending to google...")
                # Performs speech recognition on audio_data using the Google Speech Recognition API.
                MyText = r.recognize_google(audio)

                printit(f"I heard: {MyText}")
                # Check for Wake Word
                if MyText.startswith(WAKE_WORD):
                    # Play ding if wake word was heard
                    if platform.system() == "Windows":
                        os.system("cmdmp3 ding.mp3")
                    elif platform.system() == "Linux":
                        os.system("mpg123 ding.mp3")
                    printit("got wake word...")
                    # Remove the Wake word from the phrase
                    MyText = MyText[len(WAKE_WORD)+1:]
                    return MyText
        # Handle Errors from speech_recognition
        except sr.RequestError as e:
            printit("Could not request results: {0}".format(e))
        except sr.UnknownValueError:
            printit("speech is unintelligible")
    #Part of handling ALSA LIB errors
    asound.snd_lib_error_set_handler(None)

#Function that sends text to ChatGPT
def send_to_chatGPT(messages, model="gpt-3.5-turbo"):

    printit("waiting for OpenAI to respond...")
    # Creates a new chat completion for the provided messages and parameters.
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    printit("ChatGPT says...")
    # Get ChatGPT text response into variable
    message = response.choices[0].message.content
    printit(f"{Chat_Name}: {message}")
    # Append response to ChatGPT history
    messages.append(response.choices[0].message)
    return message

# Function to write the Chat log.
def output_text(text):
    f = open("output.txt", "a")
    f.write(text)
    f.write("\n")
    f.close()
    return

# modified print function
def printit(statement):
    # Checks if {Chat_Name}: for response could be in multiple lines
    if statement.startswith(f"{Chat_Name}: "):
        # split lines incase there are multiple
        lines = statement.splitlines()
        # loop through each line
        for line in lines:
            if line.startswith(f"{Chat_Name}: "):
                print(line)
                output_text(line)
            # print other lines that don't have {Chat_Name}: and add {Chat_Name}: in.
            else:
                # if the line is not blank
                if line.strip():
                    print(f"{Chat_Name}: {line}")
                    # write to output log
                    output_text(f"{Chat_Name}: {line}")
    # if the statement is from USER: just print it, its not in multiple lines 
    elif statement.startswith("USER: "):
        print(statement)
        # write to output log
        output_text(statement)
    # this is for only print and not output statements, so not {Chat_Name}: OR USER: 
    else:
        # dont write to output log just print
        print(statement)

# Function to speak the ChatGPT response text aloud
def SpeakText(response):
    printit("waiting for Google TTS to respond...")
    # send response text to google 
    tts = gTTS(text=response, lang='en')
    # Initialize reading TTS into memory
    fp = BytesIO()
    printit("writing respose to memory...")
    # Write TTS to memory 
    tts.write_to_fp(fp)
    # Seek to beginning of TTS data
    fp.seek(0)
    printit("playing respose...")
    # Initialize pygame mixer for playing audio
    pygame.mixer.init()
    # Load TTS from memory
    pygame.mixer.music.load(fp)
    # Play the TTS
    pygame.mixer.music.play()
    # wait while TTS plays
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
# Initialize ChatGPT with its identity
messages = [{"role": "system", "content": identity}]
printit("Starting...")
while(1):
    text = record_text()
    printit(f"USER: {text}")
    messages.append({"role": "user", "content": text})
    response = send_to_chatGPT(messages)
    SpeakText(response)
