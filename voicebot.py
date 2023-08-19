import speech_recognition as sr
import subprocess

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

                r.adjust_for_ambient_noise(source, duration=0.2)

                print("I'm listening")

                audio = r.listen(source)

                MyText = r.recognize_google(audio)

                if MyText.startswith(WAKE_WORD):
                    MyText = MyText[len(WAKE_WORD)+1:]
                    return MyText

        except sr.RequestError as e:
            print("Could not request results: {0}".format(e))

        except sr.UnknownValueError:
            print("unknown error occurred")
    return

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

def output_text(text):
    f = open(f"{LOG_PATH}/output.txt", "a")
    f.write(text)
    f.write("\n")
    f.close()
    return

def SpeakText(response):
    output_text(f"AI: {response.capitalize()}.")
    subprocess.run(["espeak", "-v", "mb-en1+f1", "-s", "100" ,response])

messages = [{"role": "user", "content": "Act like Jarvis from IronMan"}]
while(1):
    text = record_text()
    output_text(f"User: {text.capitalize()}.")
    messages.append({"role": "user", "content": text})
    response = send_to_chatGPT(messages)
    SpeakText(response)
    print(response)
