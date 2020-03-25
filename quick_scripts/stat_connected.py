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

    strIP = ""
    strMAC = ""
    try:
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        print( "sock: '%s'" % str( sock ) )
        #~ print( "strInterfaceName: " + str( strInterfaceName ) )
        strInterfaceName = strInterfaceName[:15]
        #~ print( "strInterfaceName: " + str( strInterfaceName ) )
        packedInterfaceName = struct.pack( '256s', strInterfaceName )
        #~ print( "packedInterfaceName: " + str( packedInterfaceName ) )
        
        try:                
            ret = fcntl.ioctl( sock.fileno(),  0x8915,  packedInterfaceName  )
            #~ print( "ret: '%s'" % ret );
            ret = ret[20:24]
            #~ print( "ret: '%s'" % ret );
            strIP = socket.inet_ntoa( ret )
        except BaseException, err:
            print( "ERR: get_ip_address(1): %s" % str(err) )
        
        try:                
            ret = fcntl.ioctl( sock.fileno(),  0x8927,  packedInterfaceName  )
            #~ print( "ret: '%s'" % ret );
            ret = ret[20:24]
            #~ print( "ret: '%s'" % ret );
            strMAC = ':'.join(['%02x' % ord(char) for char in info[18:24]])
        except BaseException, err:
            print( "ERR: get_ip_address(2): %s" % str(err) )
    except BaseException, err:
        print( "ERR: get_ip_address: %s" % str(err) )
    return (strIP, strMAC)
    # get_ip_address - end
    
def getHostUp():
    strMyIP, strMyMAC = get_ip_and_mac_address("eth0")
    print( "strMyIP: '%s'" % strMyIP )
    print( "strMyMAC: '%s'" % strMyMAC )
    strFirstIP = strMyIP.split('.')[:-1]
    strFirstIP.append('1')
    strFirstIP = '.'.join(strFirstIP)
    print( "strFirstIP: '%s'" % strFirstIP )
    
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
    strMAC = ""
    strHostHint = ""
    for l in lines:
        print("l: %s" % l )
        strIpLine = "Nmap scan report for "
        if strIpLine in l and not "[host down]" in l:
            idx = l.find( strIpLine )
            strIP = l[idx+len(strIpLine):]
            print( "New Found: strIP: '%s'" % strIP )
            # new found
            strMAC = ""
            strHostHint = ""
        strMacLine = "MAC Address: "
        strHostHint = ""
        if strMacLine in l:
            idx = l.find( strMacLine )
            strMAC = l[idx+len(strMacLine):].split(" ")[0]
            strHostHint = l[idx+len(strMacLine) + len(strMac):].strip()
        if strIP == strMyIP:
            strMAC = strMyMAC
        if strMAC != "" and strIP != "":
            print( "strIP: '%s'" % strIP )
            print( "strMAC: '%s'" % strMAC )
            print( "strHostHint: '%s'" % strHostHint )
            strIP = ""
            
            
    

    
    
def updateConnected():
    getHostUp()
    
    
updateConnected()
    