
import os 
import subprocess
import sys
import time

sys.path.append( "../alex_pytools/")
import misctools
from stringtools import timeToStr, sizeToStr

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
    bVerbose = True
    bVerbose = False
    
    import psutil
    ret = psutil.net_io_counters(pernic=True)
    if bVerbose: print("\nDBG: getNetworkStat_psutil: io_counters: %s" % str(ret) )
    
    retInterestingInterface = None
    
    for k in ["Wi-Fi","eth0","wlan0"]:
        if k in ret.keys():
            if bVerbose:
                print("\nDBG: getNetworkStat_psutil: key: %s" % k )
            retInterestingInterface = ret[k]
            break
    if bVerbose: print("\nDBG: getNetworkStat_psutil: interface: %s" % str(retInterestingInterface) )
        
    if retInterestingInterface == None:
        print("ERR: getNetworkStat_psutil: io_counters: %s (len:%s)" % (str(ret),len(ret)) )
        return 0,0,0

    r = retInterestingInterface.bytes_recv
    s = retInterestingInterface.bytes_sent
    t = r+s
    return r, s, t
    
def getNetworkStat():
    return getNetworkStat_psutil()

def analyseBandwith():
    # un scp de 3 fichiers de 168M copie en local genere 1014M de donnees mesurees !?! 
    r_init, s_init, t_init = getNetworkStat()
    ar_1, as_1, at_1 = [],[],[] # store stat during last minute
    ar_h, as_h, at_h = [],[],[] # store stat during last hour
    r_t, s_t, t_t = 0,0,0 # store stat today (non glissant)
    r_p,s_p,t_p = r_init, s_init, t_init # since last call
    nPeriodSec = 5
    timeBegin = time.time()
    cptLoop = 0
    nPrevDay = -1
    nPrevHour = -1
    while 1:
        r,s,t = getNetworkStat()
        # compute difference
        rd = r-r_init
        sd = s-s_init
        td = t-t_init
        ar_1.append(r-r_p)
        as_1.append(s-s_p)
        at_1.append(t-t_p)
        
        ar_h.append(r-r_p)
        as_h.append(s-s_p)
        at_h.append(t-t_p)
        
        r_t += r-r_p
        s_t += s-s_p
        t_t += t-t_p
        
        if len(ar_1) > (5*60/nPeriodSec):
            del ar_1[0]
            del as_1[0]
            del at_1[0]
        if len(ar_h) > (60*60/nPeriodSec):
            del ar_h[0]
            del as_h[0]
            del at_h[0]

        dummy1,dummy2,d = misctools.getDay()
        if nPrevDay != d:
            nPrevDay = d
            r_t = 0
            s_t = 0
            t_t = 0
            
        h,dummy1,dummy2 = misctools.getTime()
        if nPrevHour != h:
            nPrevHour = h
            print("%2dh" % h )
            
        if 1:
            # render bargraph in ascii
            nMB = (t-t_p)/(1024*1024)
            nMB = int(nMB+0.5)
            if 1:
                #~ nMB = 3 # to test
                # sound fx
                if nMB > 0:
                    for i in range(nMB):
                        misctools.tic(rSoundVolume=0.20,bWaitEnd=False)
                        time.sleep(0.04)
            if 0:
                # total:
                strLine = "%4dMB " % nMB + "*"*nMB
            else:
                # diff up & down
                nr = int(round((r-r_p)/(1024*1024)))
                ns = int(round((s-s_p)/(1024*1024)))
                strLine = "%4dMB " % nMB + "r"*nr + "s"*ns
            nLenLineToEraseAboveStat = 175
            if len(strLine) < nLenLineToEraseAboveStat:
                strLine += " " * (nLenLineToEraseAboveStat-len(strLine))
            print(  strLine )
            
        print("%s/%s Received: %s, Send: %s, Total: %s   Day: %s  %s  %s   Hour: %s  %s  %s   Last5Min: %s  %s  %s      \r" % (
                                            timeToStr(cptLoop*nPeriodSec), timeToStr(time.time()-timeBegin), sizeToStr(rd),sizeToStr(sd),sizeToStr(td),
                                            sizeToStr(r_t),sizeToStr(s_t),sizeToStr(t_t),
                                            sizeToStr(sum(ar_h)),sizeToStr(sum(as_h)),sizeToStr(sum(at_h)), # WRN: generate huge computation ! should sum by minutes!
                                            sizeToStr(sum(ar_1)),sizeToStr(sum(as_1)),sizeToStr(sum(at_1))
                                            ),
                                            end="" )
        r_p,s_p,t_p = r,s,t
        time.sleep(nPeriodSec)
        cptLoop += 1
        
print("")
analyseBandwith()