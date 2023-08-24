from datetime import datetime as dt
import sys

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
print("this is a test")
