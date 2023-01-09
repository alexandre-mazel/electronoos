import sys
import time
import win32api

def start_timer(nTimeMin, beepOnlyOnce=False):
    timeBegin = time.time()
    print("INF: Starting a timer for %d min" % nTimeMin)
    while (time.time()-timeBegin)/60<nTimeMin:
        print("\rINF: il reste %.2f min   " % (nTimeMin-(time.time()-timeBegin)/60), end="" )
        time.sleep(1)
    print("\ndring")
    while 1:
        for i in range(3):
            win32api.Beep(2000,200)
            time.sleep(0.05)
        if beepOnlyOnce: break
        time.sleep(2)

if __name__ == "__main__":
    nTimeMin  = 10
    beepOnlyOnce = False
    if len(sys.argv)>1:
        nTimeMin = int(sys.argv[1])
    if len(sys.argv)>2:
        beepOnlyOnce = True      
    start_timer(nTimeMin,beepOnlyOnce=beepOnlyOnce)