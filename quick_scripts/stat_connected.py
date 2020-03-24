import os
import time

def runCommandGetResults( strCommand ):
    strFilename = "/tmp/" + str(time.time())
    os.system(strCommand + " > " + strFilename )
    f = open(strFilename, "rt")
    buf = f.read()
    f.close()
    os.remove(strFilename)
    return buf
    
def getHostUp():
    strFirstIP = "192.168.0.1" # TODO: auto detect
    buf = runCommandGetResults( "nmap -sP %s-10 -v" % strFirstIP )
    lines = buf.split("\n")
    bInConnected = False
    strIP = ""
    for l in lines:
        print("l: %s" % l )
        if "Nmap scan report" in l and not "[host down]" in l:
            bInConnected = True
            idx = l.find( "for " )
            strIP = l[idx:]
            print( "strIP: %s" % strIP )
            
    
    """
Nmap scan report for 192.168.0.5
Host is up (0.00092s latency).
MAC Address: B8:27:EB:C1:69:F7 (Raspberry Pi Foundation)
"""

    print(buf)
    
    
def updateConnected():
    getHostUp()
    
    
updateConnected()
    