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
    
def get_ip_and_mac_address( strInterfaceName ):
    """
    get the ip associated to a linux network interface
    WARNING: it assumes that device are eth0 and wlan0 (known bugs on some 1.12.xx)
    return (ip,mac) - or '' if no ip
    """
    import fcntl
    import socket
    import struct

    try:
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        print( "sock: '%s'" % str( sock ) )
        #~ print( "strInterfaceName: " + str( strInterfaceName ) )
        strInterfaceName = strInterfaceName[:15]
        #~ print( "strInterfaceName: " + str( strInterfaceName ) )
        packedInterfaceName = struct.pack( '256s', strInterfaceName )
        #~ print( "packedInterfaceName: " + str( packedInterfaceName ) )
        ret = fcntl.ioctl( sock.fileno(),  0x8915,  packedInterfaceName        )
        #~ print( "ret: '%s'" % ret );
        ret = ret[20:24]
        #~ print( "ret: '%s'" % ret );
        return socket.inet_ntoa( ret )
    except BaseException, err:
        print( "ERR: get_ip_address: %s" % str(err) )
        return ''
    # get_ip_address - end
    
def getHostUp():
    strMyIP = get_ip_address("eth0")
    print( "strMyIP: '%s'" % strMyIP )
    strFirstIP = "192.168.0.1" # TODO: auto detect
    strRange = "/24"
    #~ strRange = "-10" # to debug
    buf = runCommandGetResults( "nmap -sP %s%s -v" % (strFirstIP,strRange) )
    """
Nmap scan report for 192.168.0.5
Host is up (0.00092s latency).
MAC Address: B8:27:EB:C1:69:F7 (Raspberry Pi Foundation)
"""
    lines = buf.split("\n")
    strIP = ""
    for l in lines:
        print("l: %s" % l )
        strIpLine = "Nmap scan report for "
        if strIpLine in l and not "[host down]" in l:
            idx = l.find( strIpLine )
            strIP = l[idx+len(strIpLine):]
            print( "strIP: '%s'" % strIP )
        strMacLine = "MAC Address: "
        strHostHint = ""
        if strMacLine in l:
            idx = l.find( strMacLine )
            strMac = l[idx+len(strMacLine):].split(" ")[0]
            print( "strMac: '%s'" % strMac )
            strHostHint = l[idx+len(strMacLine) + len(strMac):].strip()
            print( "strHostHint: '%s'" % strHostHint )
            
            
    

    
    
def updateConnected():
    getHostUp()
    
    
updateConnected()
    