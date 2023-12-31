from gtts import gTTS
import pygame
from io import BytesIO

pygame.init()

def say(text):
    tts = gTTS(text=text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

say('Testing of conversion from text to speach, using the Google Text to Speech API')
