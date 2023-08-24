from ctypes import *
import pyaudio

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  return
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')

asound.snd_lib_error_set_handler(c_error_handler)

p = pyaudio.PyAudio()
p.terminate()

asound.snd_lib_error_set_handler(None)
