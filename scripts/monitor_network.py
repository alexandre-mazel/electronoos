

import os 
import subprocess
import time

def getNetworkStat_netstat():
    """
    return received,send,total in Bytes
    # works badly, sometimes it' resetted !
    """
    p = subprocess.Popen(['C:\\Windows\\System32\\netstat.exe', '-e', '-p', 'IP'], encoding="cp1252",errors="ignore",stdout = subprocess.PIPE)
    #~ print(dir(p))
    a = p.wait(5)
    a = p.stdout.read() 
    a = a.split('\n')
    if 1:
        print("")
        for n,l in enumerate(a):
            print("%d: '%s'" % (n,l))
        
        
    info = a[4].split()
    rRatioError = 1
    #~ rRatioError = 6
    r = int(info[1]) / rRatioError
    s = int(info[2]) / rRatioError
    t = r+s
    return r, s, t
    
def getNetworkStat_psutil():
    """
    return received,send,total in Bytes in wifi interface
    # works fine !!!
    """
    import psutil
    ret = psutil.net_io_counters(pernic=True)
    
    retWifi = ret["Wi-Fi"]
    if 0:
        print("")
        print(retWifi )

    r = retWifi.bytes_recv
    s = retWifi.bytes_sent
    t = r+s
    return r, s, t
    
def getNetworkStat():
    return getNetworkStat_psutil()
        
        
def printSmart(v):
    listUnit = ['B','KB', 'MB', 'GB', 'TB']
    idxUnit = 0
    while v > 1024:
        v /= 1024
        idxUnit += 1
    return "%.2f%s" % (v,listUnit[idxUnit])
    
def printSmartTime(ts):
    """
    take a time in sec and print it as it's best
    """
    if ts < 60:
        return "%2ds" % ts
    ts /= 60
    if ts < 60:
        return "%2dm" % ts     
    ts /= 60
    if ts < 24:
        return "%.1fh" % ts      
    ts /= 24
    return "%.1fd" % ts

def analyseBandwith():
    # un scp de 3 fichiers de 168M copie en local genere 1014M de donnees mesurees !?! 
    r_init, s_init, t_init = getNetworkStat()
    ar_1, as_1, at_1 = [],[],[] # store stat during last minute
    r_p,s_p,t_p = r_init, s_init, t_init # since last call
    nPeriodSec = 5
    timeBegin = time.time()
    cptLoop = 0
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
            
        if 1:
            # render bargraph in ascii
            nMB = (t-t_p)/(1024*1024)
            nMB = int(nMB+0.5)
            if 0:
                # total:
                strLine = "%4dMB " % nMB + "*"*nMB
            else:
                # diff up & down
                nr = int(round((r-r_p)/(1024*1024)))
                ns = int(round((s-s_p)/(1024*1024)))
                strLine = "%4dMB " % nMB + "r"*nr + "s"*ns
            nLenLineToEraseAboveStat = 110
            if len(strLine) < nLenLineToEraseAboveStat:
                strLine += " " * (nLenLineToEraseAboveStat-len(strLine))
            print(  strLine )
            
        print("%s/%s Received: %s, Send: %s, Total: %s    LastMin: r: %s, s:%s, t:%s      \r" % (printSmartTime(cptLoop*nPeriodSec), printSmartTime(time.time()-timeBegin), printSmart(rd),printSmart(sd),printSmart(td),printSmart(sum(ar_1)),printSmart(sum(as_1)),printSmart(sum(at_1)) ), end="" )
        r_p,s_p,t_p = r,s,t
        time.sleep(nPeriodSec)
        cptLoop += 1
        
print("")
analyseBandwith()