import sys
import time

sys.path.append( "../alex_pytools/")
import misctools

def playSounds():
    print("INF: playSounds...")
    for i in range(10):
        misctools.tic(bWaitEnd=False)    
    misctools.beep(220,500)
    misctools.beep(440,500)
    misctools.beep(880,500)
    

while 1:
    playSounds()
    print("sleeping...")
    time.sleep(3)

