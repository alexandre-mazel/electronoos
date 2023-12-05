import sys
sys.path.insert(0,"../alex_pytools")
import os
import nettools
    
import json

# en fait, impossible de trouver une base de donnees ou service ip => name (car ca permettrait de faire un mega spammer)
# donc on peut generer un cache en partant des sites les plus visitees => ip

class ReverseDnsCache:
    def __init__(self):
        self.dictRDNS = {} # ip => set(name1,name2,...)
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        self.strSaveFilename = strLocalPath + '/' + "rdns.json"
        
    def isInCache(self,strIP):
        return strIP in self.dictRDNS

    def getIP( self, strSite ):
        """
        return first ip found for site.
        return "" if not found
        """
        strSitelow = strSite.lower()
        for k,v in self.dictRDNS.items():
            if strSitelow in v:
                return k
        return ""
        
    def isKnownSite( self, strSite ):
        return self.getIP(strSite) != ""
        
    def getNames(self,strIP,bVerbose=0):
        """
        retrieve names related to an ip
        """
        try:
            return self.dictRDNS[strIP]
        except KeyError:
            if bVerbose: print("WRN: ReverseDns.getNames: ip '%s' not found" % strIP)
        return []
        
    def getName(self,strIP,bVerbose=0):
        """
        return first name associated to ip or ip if not found
        """
        names = self.getNames(strIP,bVerbose=bVerbose)
        if len(names)>0:
            return nettools.reduceDomainToMasterDomain(list(names)[0])
        return strIP
        
    def addSite(self,strIP,strName):
        strNamelo = strName.lower()
        print("DBG: ReverseDns.addSite: %s => %s" % (strIP,strNamelo) )
        if strIP not in self.dictRDNS:
            self.dictRDNS[strIP] = set()
        self.dictRDNS[strIP].add(strNamelo)
        
    def save( self ):
        print("DBG: ReverseDnsCache.save: saving %d record(s) to '%s'" % (len(self.dictRDNS),str(self.strSaveFilename)))
        import misctools
        misctools.backupFile(self.strSaveFilename)
        f = open(self.strSaveFilename,"wt")
        # can't save dict of set, so converting before saving
        dictOfList = {}
        for k,v in self.dictRDNS.items():
            dictOfList[k] = list(v)
        ret = json.dump((dictOfList),f,indent=2,ensure_ascii =False)
        f.close()
        
    def load(self):
        try:
            f = open(self.strSaveFilename,"rt")
        except FileNotFoundError:
            print("WRN: ReverseDnsCache.load: file not found: '%s'" % self.strSaveFilename)
            return 0
        try:
            dictOfList = json.load(f)
            self.dictRDNS = {}
            for k,v in dictOfList.items():
                self.dictRDNS[k] = set(v)
        except BaseException as err:
            print("INF: ReverseDnsCache.load: potential error (or file empty): %s" % str(err) )
        
        print("INF: ReverseDnsCache.load: loaded: %d rdns(s)" % ( len(self.dictRDNS) ) )
        f.close()
        
# class ReverseDnsCache - end

reverseDnsCache = ReverseDnsCache()
reverseDnsCache.load()
        

def generateCacheReverseDns(filename):
    import csv_loader

    datas = csv_loader.load_csv(filename,sepa=',')
    bSkipAlreadyIn = True
    nNbrProcessed = 0
    for record in datas:
        n,site,rank = record
        if bSkipAlreadyIn:
            if reverseDnsCache.isKnownSite(site):
                continue
        #site = "signal.org"
        print("\n"+site)
        ips = nettools.getIPx(site)
        print(ips)
        ipv6s = nettools.getIPV6x(site)
        print(ipv6s)
        ipv6sub = nettools.getIPV6Sub(site)
        print(ipv6sub)
            
        if ips != False:
            for ip in ips:
                reverseDnsCache.addSite(ip,site)
            
        nNbrProcessed += 1

        if n > 20:
            break
            
        #~ if nNbrProcessed > 20:
            #~ break
            
        if (nNbrProcessed % 50) == 0:
            reverseDnsCache.save()
            
    hardTable = [
        ["20.44.229.112","microsoft(windows).com"],
        ["170.114.15.95","zoom(daemon).us"]
    ]
    for ip,site in hardTable:
        reverseDnsCache.addSite(ip,site)
        
            
    reverseDnsCache.save()
    

def getIP(strName):
    return reverseDnsCache.getIP(strName)

def getName(strIP,bVerbose=0):
    return reverseDnsCache.getName(strIP,bVerbose)
    
def getNames(strIP,bVerbose=0):
    return reverseDnsCache.getNames(strIP,bVerbose)
    


def createRDNS_DB():
    filename = "websites_1000.csv"
    generateCacheReverseDns(filename)
    
def autotest():
    # some test:
    for ip in ["127.0.0.1","13.107.42.14","142.250.179.78","216.58.214.170","162.159.128.61"]:
        print("RDNS: %s: %s" % (ip,reverseDnsCache.getNames(ip)))
        print("RDNS: %s: %s" % (ip,reverseDnsCache.getName(ip)))
        
    for site in ["vimeo.com"]:
        print("DNS: %s: %s" % (site,reverseDnsCache.getIP(site)))
        
if __name__ == "__main__":
    createRDNS_DB()
    autotest()