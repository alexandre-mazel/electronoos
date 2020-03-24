import os
import time

def runCommandGetResults( strCommand ):
    strFilename = "/tmp/" + str(time.time())
    os.system(strCommand + " > " + strCommand )
    f = open(strFilename, "rt")
    buf = f.read()
    f.close()
    os.remove(strFilename)
    return buf

def getHostUp():
    strFirstIP = "192.168.0.1" # TODO: auto detect
    buf = runCommandGetResults( "sudo nmap -sP %s/24 nmap" % strFirstIP )
    """
Nmap scan report for 192.168.0.5
Host is up (0.00092s latency).
MAC Address: B8:27:EB:C1:69:F7 (Raspberry Pi Foundation)"""

    print(buf)
    
    
def updateConnected()
    