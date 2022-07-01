

import os 
import subprocess
import time

def getNetworkStat():
    """
    return received,send,total in Bytes
    """
    p = subprocess.Popen(['C:\\Windows\\System32\\netstat.exe', '-e'], encoding="cp1252",errors="ignore",stdout = subprocess.PIPE)
    #~ print(dir(p))
    a = p.wait(5)
    a = p.stdout.read() 
    a = a.split('\n')
    if 0:
        for n,l in enumerate(a):
            print("%d: '%s'" % (n,l))
        
    info = a[4].split()
    r = int(info[1]) / 6
    s = int(info[2]) / 6
    t = r+s
    return r, s, t
        
        
def printSmart(v):
    listUnit = ['B','KB', 'MB', 'GB', 'TB']
    idxUnit = 0
    while v > 1024:
        v /= 1024
        idxUnit += 1
    return "%.2f%s" % (v,listUnit[idxUnit])
        

def analyseBandwith():
    # un scp de 3 fichiers de 168M copie en local genere 1014M de donnees mesurees !?! 
    r_init, s_init, t_init = getNetworkStat()
    ar_1, as_1, at_1 = [],[],[] # store stat during last minute
    r_p,s_p,t_p = r_init, s_init, t_init # since last call
    nPeriodSec = 5
    while 1:
        r,s,t = getNetworkStat()
        # compute difference
        rd = r-r_init
        sd = s-s_init
        td = t-t_init
        ar_1.append(r-r_p)
        as_1.append(s-s_p)
        at_1.append(t-t_p)
        if len(ar_1) > (60/nPeriodSec):
            del ar_1[0]
            del as_1[0]
            del at_1[0]
            
        print("Total: Received: %s, Send: %s, Total: %s; LastMin: %s\r" % (printSmart(rd),printSmart(sd),printSmart(td),printSmart(sum(ar_1))), end="" )
        r_p,s_p,t_p = r,s,t
        time.sleep(nPeriodSec)
        
print("")
analyseBandwith()