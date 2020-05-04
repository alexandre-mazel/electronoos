#!/usr/bin/python

def logDebug(txt):
    pass
    #file = open("/home/pi/pi_error.log", "at" )
    #file.write(txt + "\n")
    #file.close()
    
logDebug("Started")
import os
import datetime
import time

import sys


strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
logDebug("strLocalPath: " + strLocalPath)
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools


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
            strMAC = ':'.join(['%02X' % ord(char) for char in ret])
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
            

    
class Stater:
    
    def __init__( self ):
        self.dStatPerDay = {} # for each day: for each mac: (ip, nUptime,bPresent, d1, d2) the elapsed time and a flag saying present or not
        self.nLastTime = 0
        self.strDate = ""
        self.loadLabels()
        
    def loadLabels( self ):
        """
        load list mac => label
        """
        self.labels = {
            "B8:27:EB:C1:69:F7": "rasp2",
            "D0:F8:8C:A5:9D:82": "TabletCorto",
            "F4:CA:E5:5F:16:56": "FreeBox",
            "B8:27:EB:41:86:24": "RaspRee",
            "BC:83:85:00:24:35": "TabPro4",
            "B8:8A:EC:C7:73:14": "SwitchCorto",
            "48:4B:AA:68:E4:41": "IphoneAlex",
            "90:21:81:27:D5:58": "TabletGaia",
            "64:27:37:D3:31:67": "OrdiCorto", #E4:9E:12:26:39:E1
            "E4:9E:12:26:39:E1": "FreeBoxTV",
            #:60: elsaphone
        }
        
    def getLabels(self, strMAC ):
        try:
            return self.labels[strMAC]
        except: pass
        return "?"
        
    def updateConnected( self ):
        self.strDate = misctools.getDateStamp()    
        listUp = getHostUp()
        if not self.strDate in self.dStatPerDay.keys():
            self.dStatPerDay[self.strDate]={}
        statToday = self.dStatPerDay[self.strDate]
        tempUpMacList = []
        for info in listUp:
            ip, mac, strHostHint,strDetectedOS = info
            tempUpMacList.append(mac)
            if mac not in statToday.keys():
                statToday[mac] = [ip, 0,False, "", ""]
            if statToday[mac][2]:
                statToday[mac][0] = ip
                statToday[mac][1] += time.time() - self.nLastTime
            else:
                statToday[mac][2] = True
                statToday[mac][3] = strHostHint
                statToday[mac][4] = strDetectedOS
        
        for k,v in statToday.items():
            if k not in tempUpMacList:
                statToday[k][2] = False
        self.nLastTime = time.time()
        
        print(self.dStatPerDay)
    
    def generatePage( self ):
        statToday = self.dStatPerDay[self.strDate]
        strPage = "<html><head></head><body><table>"
        for k,v in statToday.items():
            strUp = "Down"
            if v[2]: strUp = "Up"
            strPage += "<tr>"
            strPage += "<td>%s</td>" % k
            if v[2]: strPage += "<td><b>%s</b></td>" % self.getLabels(k)
            else: strPage += "<td>%s</td>" % self.getLabels(k)
            strPage += "<td><font size=-2>%s</font></td>" % v[3]
            strPage += "<td>%s</td>" % v[0]
            strPage += "<td>%s</td>" % misctools.timeToString(v[1])
            strPage += "<td>%s</td>" % strUp
            strPage += "</tr>"
        strPage += "</table>"
        strPage += "<font size=-10>last computed: %s</font>" % misctools.getTimeStamp()
        strPage += "</body></html>"
        f = open("/var/www/html/stat_up.html", "wt")
        f.write(strPage)
        f.close()
        
# class Stater - end

def loopUpdate():
    logDebug("loopUpdate: begin")
    stats = Stater()
    nCnt = 0
    nTimeSleep = 1 # at start, we sleep less for debug purpose, and it will become higher during time pass
    while 1:
            try:
                logDebug("loopUpdate: avant update connected")
                stats.updateConnected()
                logDebug("loopUpdate: avant generatePage")
                stats.generatePage()
            except BaseException as err:
                strErr = "ERR: loopUpdate: err: %s" % str(err)
                print(strErr)
                logDebug(strErr)
            nCnt += 1
            #~ if nCnt>3:
                #~ break
            time.sleep( nTimeSleep )
            if nTimeSleep < 300:
                nTimeSleep += 1
loopUpdate()
    
