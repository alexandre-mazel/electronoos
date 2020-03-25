import os
import datetime
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
        #~ print( "sock: '%s'" % str( sock ) )
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
            ret = ret[18:24]
            #~ print( "ret: '%s'" % ret );
            strMAC = ':'.join(['%02x' % ord(char) for char in ret])
        except BaseException, err:
            print( "ERR: get_ip_address(2): %s" % str(err) )
    except BaseException, err:
        print( "ERR: get_ip_address: %s" % str(err) )
    return (strIP, strMAC)
    # get_ip_address - end
    
def getHostUp():
    """
    Retrieve a list of all machine on the lan.
    Return ["ip", "mac", "system guess from mac", "system guess from nmap(optionnally)"
    WRN: need to be launched by root, or no mac information
    """
    listUp = []
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
        #~ print("l: %s" % l )
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
            strHostHint = l[idx+len(strMacLine) + len(strMAC):].strip()
        if strIP == strMyIP:
            strMAC = strMyMAC
        if strMAC != "" and strIP != "":
            strDetectedOS = ""
            if 1:
                # probe system (not interesting: take long and so, let's use a map of labelled)
                pass
            print( "strIP: '%s'" % strIP )
            print( "strMAC: '%s'" % strMAC )
            print( "strHostHint: '%s'" % strHostHint )
            listUp.append( (strIP, strMAC, strHostHint, strDetectedOS) )
            strIP = ""
    return listUp
# getHostUp - end
            
            
def getDateStamp():
    datetimeObject = datetime.datetime.now()
    strStamp = datetimeObject.strftime( "%Y_%m_%d")
    return strStamp
    
class Stater:
    
    def __init__( self ):
        self.dStatPerDay = {} # for each day: for each mac: (nUptime,bPresent) the elapsed time and a flag saying present or not
        self.nLastTime = 0
        self.strDate = ""
        self.loadLabels()
        
    def loadLabels( self ):
        """
        load list mac => label
        """
        self.labels = {
            "B8:27:EB:C1:69:F7": "rasp2",
            "D0:F8:8C:A5:9D:82": "?",
            "F4:CA:E5:5F:16:56": "FreeBox",
        }
        
    def getLabels(self, strMAC ):
        try:
            return self.labels[strMAC]
        except: pass
        return "???"
        
    def updateConnected( self ):
        self.strDate = getDateStamp()    
        listUp = getHostUp()
        if not self.strDate in self.dStatPerDay.keys():
            self.dStatPerDay[self.strDate]={}
        statToday = self.dStatPerDay[self.strDate]
        tempUpMacList = []
        for info in listUp:
            ip, mac, d1,d2 = info
            tempUpMacList.append(mac)
            if mac not in statToday.keys():
                statToday[mac] = [0,False]
            if statToday[mac][1]:
                statToday[mac][0] += time.time() - self.nLastTime
            else:
                statToday[mac][1] = True
        
        for k,v in statToday.items():
            if k not in tempUpMacList:
                v[1] = False
        self.nLastTime = time.time()
        
        print(self.dStatPerDay)
    
    def generatePage( self ):
        statToday = self.dStatPerDay[self.strDate]
        strPage = "<html><head></head><body>"
        for k,v in statToday.items():
            strPage += "<tr>"
            strPage += "<td>%s</td>" % self.getLabels(k)
            strPage += "<td>%s sec</td>" % v[0]
            strPage += "<td>Up: %s</td>" % v[1]
            strPage += "</tr>"
        strPage += "</table></body></html>"
        f = open("/var/www/html/stat_up.html", "wt")
        f.write(strPage)
        f.close()
            
            
        
# class Stater - end

def loopUpdate():
    stats = Stater()
    nCnt = 0
    while 1:
            stats.updateConnected()
            stats.generatePage()
            nCnt += 1
            #~ if nCnt>3:
                #~ break
            time.sleep(5)
    
loopUpdate()
    