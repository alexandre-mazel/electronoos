# coding: cp1252

#~ import xml.etree.ElementTree as ET

#~ from lxml import etree
#~ root = etree.parse('data.xml').getroot()
#~ instruments = root.find('Instruments')
#~ instrument = instruments.findall('Instrument')
#~ for grandchild in instrument:
    #~ code, source = grandchild.find('Code'), grandchild.find('Source')
    #~ print (code.text), (source.text)
    
import datetime
import os
import unicodedata
import time
    

    
def scrap_cours_crypto( strFileContent ):
    bVerbose = 1
    buf = strFileContent
    
    if 1:
        # get all list of currency:
        strBeforeCurrency = 'e="display:flex" class="jsx-1338272632"><div style="height:20px" class="lazyload-placeholder"></div>'
        start = 0
        listCurrency = []
        while 1:
            idx = buf[start:].find(strBeforeCurrency)
            if idx == -1:
                break
            start += idx+len(strBeforeCurrency)
            end = buf[start:].find(')')
            strCurrency = buf[start:start+end+1]
            if bVerbose: print("currency: '%s'" % strCurrency)
            listCurrency.append(strCurrency)
    else:            
        listCurrency = [
                                    "Bitcoin (BTC)",
                                    "Ethereum (ETH)",
                                    "Binance Coin (BNB)",
                                    "Ripple (XRP)",
                                    "Tether (USDT)",
                                    "Bitcoin Cash (BCH)",
                                    "Litecoin (LTC)",
                                ]
                            
    dictOut = {} # for each name, its value
    
                                
    for strCurrency in listCurrency:
        idxStart = buf.find(strCurrency)
        if bVerbose: print("%d: %s" % (idxStart, buf[idxStart:idxStart+300]))
        idxPreTest = idxStart-100
        if bVerbose: print("idxPreTest: %d: %s" % (idxPreTest, buf[idxPreTest:idxPreTest+105]))
        
        strJustBefore = '<td data-title="Cours" class="jsx-1338272632"><span class="">'
        idx2 = buf[idxStart:].find(strJustBefore)
        idx2 += idxStart+len(strJustBefore)
        if bVerbose: print("%s" % (buf[idx2:idx2+30]))
        
        strEnd =  unicodedata.lookup("EURO SIGN") # u"€" 
        idxEnd = buf[idx2:].find(strEnd)
        if bVerbose: print("idxEnd: %s" % idxEnd)
        
        strValue = buf[idx2:idx2+idxEnd]
        strValue = strValue.replace("&#x27;","")
        if bVerbose: print("strValue: %s" % strValue )
        
        rValue = float(strValue)
        if bVerbose: print("rValue: %s" % rValue )
        dictOut[strCurrency] = rValue
        
    if bVerbose: print( "INF: %d value(s) found" % len(dictOut) )
    if bVerbose: print( dictOut )
    return dictOut
        

def scrapFromFile_cours_crypto( strFile ):
    enc = 'utf-8'
    f = open(strFile, "rt", encoding = enc)
    buf = f.read()
    f.close()
    return scrap_cours_crypto(buf)
    
def scrapFromWeb_cours_crypto():
    #~ import urllib.request
    from six.moves import urllib
    fp = urllib.request.urlopen("https://courscryptomonnaies.com/")
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    return scrap_cours_crypto( mystr )
    
def computeDiffDict(d1,d2):
    """
    compute difference of each value in a dictionnary and in another.
    """
    dOut = {}
    for k,v in d1.items():
        diff = d2[k] - v
        dOut[k] = [diff,100*diff/v]
    return dOut
        
class DataSaver:
    """
    take a dict of nammed value, save it smartly on disk with timestamp...
    csvs...
    """
    def __init__( self, strPathToSave = "/tmp/", nAutoSaveSec = 5*60 ):
        self.reset()
        self.changeSavePath(strPathToSave)
        self.nAutoSaveSec = nAutoSaveSec
        
    def changeSavePath( self, strNewPathToSave ):
        self.strPath = os.path.abspath(strNewPathToSave)
        
    def reset(self):
        self.aIdxLabels = {} # for each label its idx
        self.aLabels = [] # a list of labels
        self.aDatas = [] # a list of list of data related to each label
        self.aTime = [] # for each list of data, its time
        self.lastTimeSave = time.time()
        
    def save( self ):
        if time.time() - self.lastTimeSave < self.nAutoSaveSec:
            return
        self.lastTimeSave = time.time()
        datetimeObject = datetime.datetime.now()
        fn = datetimeObject.strftime( "%Y_%m_%d.csv" );
        afn = self.strPath+os.sep+fn
        try:
            os.makedirs(self.strPath)
        except BaseException as err:
            #~ print("WRN: while creating folder: %s" % str(err) )
            pass
        print("before file")
        try:
            nSize = os.path.getsize(afn)
            bNewFile = nSize < 1
        except BaseException as err:
            bNewFile = True
        print("after file")
            
        print("INF: saving to '%s'..." % afn )
        if os.path.exists( afn ) or 1:
            f = open(afn,"at") # seems to work on windows in python3 but not in python2 on RPI
        else:
            f = open(afn,"wt")
        if bNewFile:
            # write headers
            f.write("time_stamp;")
            for s in self.aLabels:
                f.write( "%s;"% s)
            f.write("\n")
        for i,datas in enumerate(self.aDatas):
            f.write("%s;" % self.aTime[i])
            for data in datas:
                f.write("%f;" % data)
            f.write("\n")
        f.close()
        
        
    def update( self, dictData ):
        """
        receive a dict with name => value
        """
        
        if len(self.aLabels)<1:
            self.aLabels = sorted(dictData.keys())
            for i,k in enumerate(self.aLabels):
                self.aIdxLabels[k]=i
                
        #~ t = time.time()    
        datetimeObject = datetime.datetime.now()
        t = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
        if os.name != "nt": t = t.replace( "000ms", "ms" ); 
        
        self.aTime.append(t)
        
        self.aDatas.append([0]*len(self.aLabels))
        print("DBG: self.aLabels (%3d): %s" % (len(self.aLabels),self.aLabels))
        print("DBG: self.aIdxLabels (%3d): %s" % (len(self.aIdxLabels),self.aIdxLabels))
        print("DBG: self.aDatas (%3d): %s" % (len(self.aDatas),self.aDatas))
        print("DBG: self.aTime (%3d): %s" % (len(self.aTime),self.aTime))
        for k,v in dictData.items():
            try:
                idx = self.aIdxLabels[k]
            except KeyError as err:
                print("WRN: new value appears, skipping it: '%s'" % k)
                # dans le cas ou des valeurs disparaissent, on aura des 0
                continue
            self.aDatas[-1][idx]=v
        print("DBG: self.aDatas (%3d): %s" % (len(self.aDatas),self.aDatas))
        self.save()


# class DataSaver - end
dataSaver = DataSaver()

def scrapAndSaveCryptoCurrency(strSavePath):
    dataSaver.changeSavePath(strSavePath)
    dataSaver.nAutoSaveSec = 5
    d1 = scrapFromWeb_cours_crypto()
    print("INF: scrapAndSaveCryptoCurrency: (%d): %s" % (len(d1),d1) )
    dataSaver.update(d1)
    

if __name__ == "__main__":
    strFilename = "courscryptomonnaies.html"
    strFilename2 = "courscryptomonnaies2.html"
    if 0:
        scrapFromFile_cours_crypto( strFilename )
        exit(0)
    if 0:
        if 0:
            d1 = scrapFromWeb_cours_crypto()
            time.sleep(10)
            d2 = scrapFromWeb_cours_crypto()
        else:
            d1 = scrapFromFile_cours_crypto( strFilename )
            d2 = scrapFromFile_cours_crypto( strFilename2 )
            
        dictDiff = computeDiffDict(d1,d2)
        print( "Diff: len: %d, %s" % (len(dictDiff), dictDiff ))
        for k,v in dictDiff.items():
            print("%s: %5.2f, %5.2f%%" % (k,v[0],v[1]) )
    
    if 0:
        dataSaver = DataSaver("/tmp2/", 2.0)
        for i in range(3):
            d = scrapFromFile_cours_crypto( strFilename )
            dataSaver.update(d)
            time.sleep(1)
            d=scrapFromFile_cours_crypto( strFilename2 )
            time.sleep(1)    
            dataSaver.update(d)
    
    if 1:
        dataSaver.nAutoSaveSec = 90
        for i in range(10):
            scrapAndSaveCryptoCurrency(os.path.expanduser("~/")+"/records/")
            time.sleep(30)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
