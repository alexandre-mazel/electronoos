#!/usr/bin/python

def logDebug(txt):
    pass
    #file = open("/home/na/pi_error.log", "at" )
    #file.write(txt + "\n")
    #file.close()
    
logDebug("Started")
import os
import datetime
import time

import sys


strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
logDebug("strLocalPath: " + strLocalPath)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import nettools


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
        self.nCptRestartToday = 0
        self.nLastTime = 0
        self.strDate = ""
        self.loadLabels()
        self.strSaveFileName = os.path.expanduser("~/") + "stater.sav"
        self.load()
        
    def save(self):
        f=open(self.strSaveFileName, "wt")
        f.write(repr((self.dStatPerDay,self.nCptRestartToday)))
        f.close()
        
    def load(self):
        try:
            f=open(self.strSaveFileName, "rt")
            data = f.read()
            reconstructed = eval(data) # harsh unsafe!
            #print("DBG: Stater.load: loading: '%s'" % str(reconstructed) )
            self.dStatPerDay, self.nCptRestartToday  = reconstructed
            self.nCptRestartToday += 1
            f.close()  
        except BaseException as err:
            print("WRN: Stater.load: %s" % str(err) )
            return
        
    def loadLabels( self ):
        """
        load list mac => label and hint => label
        """
        self.labels = {
            "B8:27:EB:C1:69:F7": "rasp2",
            "D0:F8:8C:A5:9D:82": "TabletCorto",
            "F4:CA:E5:5F:16:56": "FreeBox",
            "B8:27:EB:41:86:24": "RaspRee",
            "DC:A6:32:A7:FE:E1": "RPi4",
            "BC:83:85:00:24:35": "TabPro4",
            "E0:2B:E9:D7:DE:8A": "TabPro7",
            "B8:8A:EC:C7:73:14": "SwitchCorto",
            "1C:45:86:94:FB:6F": "SwitchGaia",
            "48:4B:AA:68:E4:41": "IphoneAlex",
            "B8:FF:61:54:81:FA": "IpadAlex",
            "90:21:81:27:D5:58": "TabletGaia",
            "64:27:37:D3:31:67": "OrdiCorto", #E4:9E:12:26:39:E1
            "AC:36:13:13:E2:60": "MobileCorto",
            "5C:C3:07:8E:68:1F": "P10_Corto",
            "E4:9E:12:26:39:E1": "FreeBoxTV",
            "E4:9E:12:26:39:E0": "FreeBoxTV Eth",
            #:60: elsaphone
            "00:13:95:1C:0E:C6": "PepperAlex9 Eth",
            "48:A9:D2:8C:75:F8": "PepperAlex9 Wifi",
            "00:08:22:66:0C:FC": "PepperAlex9 Tab",
            
            "48:B0:2D:05:B6:9D": "Jetson AGX",
            "DC:A6:32:48:A4:0C": "Rasp4Therm",
            "18:03:73:17:D3:6C": "BigA",
            "2C:F0:5D:9F:BF:DE": "XeniaDev",
            "A0:32:99:D1:52:CA": "LenovoYoga",
            "8A:E2:56:9A:7D:6A": "IphoneXAlex",
            "3A:E6:D8:43:04:B5": "Iphone14",
            "72:1C:0D:52:39:39": "A52_Alex",
            "20:C1:9B:F3:F2:0A": "Kakashi",
            
            "84:CF:BF:95:4A:88": "FairCorto",
            "9E:DF:71:E1:AE:0E": "FairCorto2",

            "74:DA:38:F6:D8:DB": "Edimax_meteo",
            
            
            
            
        }

        self.hostLabels = {
            "Speed Dragon": "Adapt Usb => Eth",
            "Wistron Neweb": "Pepper/NAO6 Wifi",
            "congatec": "Pepper Eth",
        }
            
    def getLabels(self, strMAC, strHostHint = "" ):
        try:
            return self.labels[strMAC]
        except: pass
        if strHostHint != "":
            # search in host hint table
            for k,v in self.hostLabels.items():
                if k in strHostHint:
                    return v
        return "?"
        
    def updateConnected( self ):
        """
        return True if a new day has started
        """
        bNewDay = False
        self.strDate = misctools.getDateStamp()    
        print("self.strDate: %s" % self.strDate )
        if 0:
            # debug to simulate many days
            if self.nLastTime == 0:
                self.nCpt = 0
            else:
                self.nCpt += 1
                if self.nCpt == 1:
                    self.strDate = "2020_05_09"
                if self.nCpt == 2:
                    self.strDate = "2020_05_10"
        if self.nLastTime == 0:
            self.nLastTime = time.time() # was generating a bug when loading from save

        listUp = getHostUp()
        if not self.strDate in self.dStatPerDay.keys():
            bNewDay = True
            self.dStatPerDay[self.strDate]={}
            self.nCptRestartToday = 0
            self.save() # clean current day backup
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
        
        #print(self.dStatPerDay)

        return bNewDay
    
    def generatePage( self, strDate, strOutputFileName ):
        statToday = self.dStatPerDay[strDate]
        strPage = "<html><head></head><body><table>"
        #for k,v in statToday.items():
        for k,v in sorted(statToday.items(), key=lambda v: v[1][1], reverse=True ):
            strUp = "Down"
            if v[2]: strUp = "Up"
            strPage += "<tr>"
            strPage += "<td>%s</td>" % k
            if v[2]: strPage += "<td><b>%s</b></td>" % self.getLabels(k, v[3])
            else: strPage += "<td>%s</td>" % self.getLabels(k, v[3])
            strPage += "<td><font size=-2>%s</font></td>" % v[3]
            strPage += "<td>%s</td>" % v[0]
            strPage += "<td>%s</td>" % misctools.timeToString(v[1])
            strPage += "<td>%s</td>" % strUp
            strPage += "</tr>"
        strPage += "</table>"
        strPage += "<font size=-10>restart today: %d<br>last computed: %s</font>" % (self.nCptRestartToday, misctools.getTimeStamp() )
        strPage += "</body></html>"
        f = open( strOutputFileName, "wt" )
        f.write(strPage)
        f.close()
        
# class Stater - end

sys.path.append(strLocalPath+"/../crypto_prono/")
import scrap
def updateScrap():
    strPath = os.path.expanduser("~/")+"/records/"
    strPath = "/home/na/records/"
    scrap.scrapAndSaveCryptoCurrency(strPath)
    
def getTemperatureFrom1wire(strDeviceID):
    """
    open w1 devices and extract temperature, return it in degree Celsius
    find /sys/bus/w1/devices/ -name "28-*" -exec cat {}/w1_slave \; | grep "t=" | awk -F "t=" '{print $2/1000}'

    """
    f = open("/sys/bus/w1/devices/%s/w1_slave" % strDeviceID,"rt")
    lines = f.readlines()
    if len(lines)>0:
        t = lines[-1].split("t=")[-1]
        t = int(t)/1000.
        #~ t -= 1.5 # overheat
    else:
        t = -127
    return t
    
def updateTemperature():
    strDeviceID = "28-3cb1f649c835"
    t = getTemperatureFrom1wire(strDeviceID)
    if t <= -127:
        return
        
    if 1:
         # on va moyenner 2 lectures a 15s d'intervalles
        time.sleep(15)
        t2 = getTemperatureFrom1wire(strDeviceID)
        if t2 > -127:
            t = (t + t2) / 2
    
    #~ print("INF: updateTemperature: %.1f" % t )
    
    timestamp = misctools.getTimeStamp()
    if os.name == "nt":
        dest = "c:/save/office_temperature.txt"
    else:
        #~ dest = os.path.expanduser("~/save/office_temperature.txt")
        dest = "/home/na/save/office_temperature.txt" # here we want to save there, even if running as root
    
    f = open(dest,"a+")
    f.write("%s: %s: %.1f\n" % (timestamp,"armoire",t) )
    f.close()
    
    nettools. sendDataToEngServer("temp", t)
    
#~ updateTemperature()
#~ exit(1)

def loopUpdate():
    logDebug("loopUpdate: begin")
    stats = Stater()
    nCnt = 0
    nTimeSleep = 1 # at start, we sleep less for debug purpose, and it will become higher during time pass
    while 1:
            try:
                logDebug("loopUpdate: avant update connected")
                bNewDay = stats.updateConnected()
                if bNewDay and len(stats.dStatPerDay) > 1:
                    strDatePrev = sorted(stats.dStatPerDay.keys())[-2]
                    stats.generatePage(strDatePrev, "/var/www/html/stat_up_%s.html" % strDatePrev )
                logDebug("loopUpdate: avant generatePage")
                stats.generatePage(stats.strDate, "/var/www/html/stat_up.html")                                
                if misctools.isEvery10min() or 0:
                    stats.save()
                updateScrap()

            except BaseException as err:
                strErr = "ERR: loopUpdate: err: %s" % str(err)
                print(strErr)
                logDebug(strErr)
                
            try:
                updateTemperature()
            except BaseException as err:
                strErr = "ERR: loopUpdate2: err: %s" % str(err)
                print(strErr)
                logDebug(strErr)
                
            nCnt += 1
            #~ if nCnt>3:
                #~ break
            time.sleep( nTimeSleep )
            if nTimeSleep < 300:
                nTimeSleep += 1
loopUpdate()
    
