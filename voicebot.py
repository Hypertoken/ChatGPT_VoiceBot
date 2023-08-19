import speech_recognition as sr
import subprocess
from language_tool_python import LanguageTool
import os

# Explicitly set PulseAudio environment variables
os.environ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
os.environ["PULSE_COOKIE"] = "/run/user/1000/pulse/cookie"

from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
WAKE_WORD = os.getenv('WAKE_WORD')
LOG_PATH = os.getenv('LOG_PATH')

import openai
openai.api_key = OPENAI_KEY

r = sr.Recognizer()

def record_text():
    while(1):
        try:
            with sr.Microphone() as source:
            #use what_mic.py to find the microphone index of the mic you would like to use, or just use sr.Microphone() for the default mic.
                r.adjust_for_ambient_noise(source, duration=0.2)

                audio = r.listen(source)

                MyText = r.recognize_google(audio)

                if MyText.startswith(WAKE_WORD):
                    MyText = MyText[len(WAKE_WORD)+1:]
                    return MyText

        except sr.RequestError as e:
            print("Could not request results: {0}".format(e))
            output_text("Could not request results: {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occurred")
            output_text("unknown error occurred")

def send_to_chatGPT(messages, model="gpt-3.5-turbo"):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].message.content
    messages.append(response.choices[0].message)
    return message

def correct_text(text):
    tool = LanguageTool('en-US')  # LanguageTool instance with English language rules
    corrected_text = tool.correct(text)
    return corrected_text

def output_text(text):
    f = open(f"{LOG_PATH}/output.txt", "a")
    print(text)
    f.write(text)
    f.write("\n")
    f.close()
    return

def SpeakText(response):
    output_text(f"TARS: {response}")
    subprocess.run(["espeak", "-v", "mb-us1", "-s", "120" ,response])

messages = [{"role": "system", "content": "You are TARS a witty, sarcastic, and humorous robot companion from the Movie Interstellar. Respond only as TARS, including whitty banter."}]
while(1):
    speak = record_text()
    text = correct_text(speak)
    output_text(f"USER: {text}")
    messages.append({"role": "user", "content": text})
    response = send_to_chatGPT(messages)
    SpeakText(response)
