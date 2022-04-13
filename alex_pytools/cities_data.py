# -*- coding: utf-8 -*-

import datetime
import math
import os
import shutil
import sys
import time

def assert_equal(a,b):
    if a == b:
        print("(%s==%s) => ok" % (a,b))
    else:
        print("(%s==%s) => NOT ok (type:%s and %s)" % (a,b,type(a),type(b)))
        assert(0)

def assert_diff(a,b,diff=0.1):
    if abs(a-b)<diff:
        print("(%s diff %s < %s) => ok" % (a,b,diff))
    else:
        print("(%s diff %s < %s)) => NOT ok (type:%s and %s)" % (a,b,diff, type(a),type(b)))
        assert(0)
        
def getTimeStamp():
    """
    
    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    

def openWithEncoding( filename, mode, encoding, errors = 'strict' ):
    if sys.version_info[0] < 3:
        import io
        return io.open( filename, mode, encoding=encoding, errors=errors )
    return open( filename, mode, encoding=encoding, errors=errors )

        

def floatRepr( v, bReplacePointByComma = True, nNbrDecimalPoint=-1 ):
    """
    convert a value into a string, if the value is a float, then '.' is changed by ',' 
    """
    if not bReplacePointByComma and nNbrDecimalPoint == -1:
        return str(v)
        
    if nNbrDecimalPoint == -1:
        strFloatFormat = "%f"
    else:
        strFloatFormat = "%%.%df" % nNbrDecimalPoint
        
    #~ print(type(v))
    
    if not isinstance(v,float):
        return str(v)
        
    sv = strFloatFormat % v
    sv = sv.replace('.',',')
    return sv

def outputCsv( dictValues, strFilename, aListLabels, key = None, reverse = False ):
    sep = ';'
    bReplacePointByComma = True # for french spreadsheet
    f = open(strFilename, "wt")
    for l in aListLabels:
        f.write(l + sep)
    f.write("\n")
    
    if key == None:
        items = dictValues.items()
    else:
        items = sorted(dictValues.items(),key=key,reverse=reverse)
        
    for k,v in items:
        if not isinstance( v, list ) and not isinstance( v, tuple ): 
            f.write("%s%s%s\n" % (k,sep,floatRepr(v,bReplacePointByComma)) )
        else:
            #~ print(type(v))
            f.write("%s%s" % (k,sep) )
            for i in v:
                f.write("%s%s"%(floatRepr(i,bReplacePointByComma),sep))
            f.write("\n")
    f.close()
    
def arrayToTd( aList ):
    strOut = ""
    for l in aList:
        strOut += '<td>' + l + '</td>'
    return strOut
    
def getAsHtmlTable( dictValues, aListLabels, key = None, reverse = False ):
    """
    output a dict as an html table
    """
    bReplacePointByComma = False
    strOut = "<table>"

    strOut += "<tr>" + arrayToTd(aListLabels) + "</tr>"
    
    if key == None:
        items = dictValues.items()
    else:
        items = sorted(dictValues.items(),key=key,reverse=reverse)
        
    for k,v in items:
        strOut += "<tr>"
        if not isinstance( v, list ) and not isinstance( v, tuple ): 
            strOut += "<td><center>%s</td><td><center>%s</td>\n" % (k,floatRepr(v,bReplacePointByComma,nNbrDecimalPoint=2))
        else:
            #~ print(type(v))
            strOut += "<td><center>%s</td>" % (k)
            for i in v:
                strOut += "<td><center>%s</td>"%(floatRepr(i,bReplacePointByComma,nNbrDecimalPoint=2))
        strOut += "</tr>"
    strOut += "</table>"  
    return strOut
            
        

def listPeoples( cnx ):
    cursor = cnx.cursor()

    query = ("SELECT first_name, last_name FROM xenia_user WHERE first_name like '%%test_alex%%'")

    #~ hire_start = datetime.date(1999, 1, 1)
    #~ hire_end = datetime.date(1999, 12, 31)

    #~ cursor.execute(query, (hire_start, hire_end))

    cursor.execute(query)

    for (first_name, last_name) in cursor:
        print("{}, {}".format(last_name, first_name))

    cursor.close()
    
def isRepresentInt(s):
    try: 
        int(s)
        return True
    except (ValueError,TypeError) as err:
        return False
        
        
def distLongLat( lo1, la1, lo2, la2 ):
    """
    Source: http://villemin.gerard.free.fr/aGeograp/Distance.htm
    Pour de petites distances la methode utilisant le theoreme de Pythagore marche bien.
    
    On calcule x et y des distances exprimees en degres (degres decimaux).
    Puis, z la distance cherchee exprimee en "degres".
    
    Le facteur k retablit l'echelle en kilometre en sachant que 1 minute d'arc = 1 mille marin  = 1852 m; 
    a multiplier par 60 pour passer aux degres.
    """
    #~ print(lo1, la1, lo2, la2)
    x = (lo2-lo1)*math.cos(((la2+la1)/2)*math.pi/180)
    y = (la2-la1)
    z = math.sqrt(x*x+y*y)
    d=1.852*60*z
    return d

        
def loadListUnivercityCity():
    bVerbose = 0
    strFilename = "datas/classement_ville_etudiante.txt"
    enc = 'utf-8'
    file = openWithEncoding(strFilename, "rt", encoding = enc, errors='ignore')
    dictCityNbrStudent = {}
    while 1:
        line = file.readline()
        if len(line)<1:
            break
        if line[0] == '#':
            continue
        if bVerbose: print(line)
        start = ' - '
        end = ' avec'

        idx = line.find(start)
        idx2 = line.find(end)

        if idx2 == -1:
            continue
        strCity = line[idx+len(start):idx2]
        if bVerbose: print("strCity: '%s'" % strCity)

        start = 'avec '
        end = '('

        idx = line.find(start)
        idx2 = line.find(end)
        strNbr = line[idx+len(start):idx2].replace(" ","")
        if bVerbose: print("strNbr: '%s'" % strNbr)
        
        nNbr = int(strNbr)
        if bVerbose: print("nNbr: '%s'" % nNbr)  
        
        dictCityNbrStudent[strCity] = nNbr        
                    
                    
    return dictCityNbrStudent
    
        
def getLongLatParis(zip):
    """
    return None if zip not in paris
    """
    dMairieByArrt = {
    "75001": (48.860229481701275, 2.341144718898233),
    "75002": (48.86691549409705, 2.3405526632345692),
    "75003": (45.760454328146665, 4.849619942213573),
    "75004": (45.77439665631134, 4.827901461166257),
    "75005": (48.84728895451373, 2.3444269031033427),
    "75006": (48.85186486570257, 2.332323906701487),
    "75007": (48.857964521292004, 2.3203047419951717),
    "75008": (48.8778735550223, 2.3175353470467672),
    "75009": (48.87461575312214, 2.340110188782279),
    "75010": (48.872026438530554, 2.3575061446349297),
    "75011": (48.85883038976746, 2.379526708674561),
    "75012": (48.841188747402434, 2.3880029516825205),
    "75013": (48.83400181758377, 2.355797863333225),
    "75014": (48.8333833024, 2.3269441538671694),
    "75015": (48.84156802519426, 2.300377494022698),
    "75016": (48.8639710753748, 2.2765973930774925),
    "75017": (48.884640668829505, 2.3221624511967787),
    "75018": (48.89245470756174, 2.344460607631557),
    "75019": (48.884160133854074, 2.381934739473095),
    "75020": (48.865226484167344, 2.39903486037782),
    }
    
    try:
        return dMairieByArrt[str(zip)][::-1]
    except KeyError:
        pass
    return None
    

def removeAccent( c ):
    try:
        acc="ÉÈÎâàçéêëèîïôûüùŷÿ" # TODO A avec accent
        noacc="EEIaaceeeeiiouuuyy"
        #~ idx=acc.find(c) # in python 2.7: UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 0: ordinal not in range(128) // ord(value) was 233
        #~ if idx != -1:
            #~ return noacc[idx]
        #~ for i in range(len(acc)):
            #~ if c == acc[i]:
                #~ return noacc[i]
        if 0:
            # generate acc_ord code value
            for c in acc:
                print("%s," % ord(c) )
                
        acc_ord = [
            201,
            200,
            206,
            226,
            224,
            231,
            233,
            234,
            235,
            232,
            238,
            239,
            244,
            251,
            252,
            249,
            375,
            255
            ]

        # same chars at ovh (preceded by a 195 or 197 in front of 183)
        acc_ord_ovh = [
            137,
            136,
            142,
            162,
            160,
            167,
            169,
            170,
            171,
            168,
            174,
            175,
            180,
            187,
            188,
            185,
            183,
            191
        ]

        #~ assert_equal( len(acc_ord),len(noacc) )
        for i in range(len(acc_ord)):
            if ord(c) == acc_ord[i]:
                return noacc[i]        

        #~ assert_equal( len(acc_ord),len(acc_ord_ovh) )
        for i in range(len(acc_ord_ovh)):
            if ord(c) == acc_ord_ovh[i]:
                return noacc[i]      
                
        if c == "æ" or ord(c)==230:
            c = "ae"
        if c == "œ" or ord(c)==339:
            c = "oe"
        elif c == "Œ" or ord(c)==338:
            c = "OE"
        elif ord(c) == 231: # c cedile not detected previously
            c = "c"
        elif ord(c) == 156 or ord(c) == 140:
            # second part of oe, don't complain (minuscule then majuscule)
            c = ""
        elif ord(c) == 195 or ord(c) == 197:
            # mark of char on two chars at ovh, don't complain
            c = ""
        elif ord(c) == 8211 or ord(c) == 8212:
            # custom hyphen
            c = "-"
        elif ord(c) == 8216 or ord(c) == 8217:
            # type de '
            c = "'"
        elif ord(c) == 8220:
            # type de 
            c = '"'
        elif ord(c) == 8230:
            c = "..."
        else:
            try:
                print("DBG: removeAccent: not found: %c (%s)" % (c,ord(c) ))
            except BaseException as err:
                print("DBG: removeAccent: catch else: ord: %s, err: %s" % (ord(c),err) )
            c="" # it should remains only invisible char like the square before "oe"
        return c
    except TypeError as err:
        print("DBG: removeAccent:type error: %s, returning '_'" % str(err) )
    return "_"
        
    
def cleanString( s ):
    """
    change a string to lower case without accent
    """
    bPrintResultForDebug = 0
    o = ""
    for c in s:
        if ord(c)>127:
            #~ print("in %s: %c" % (s,c) )
            c = removeAccent(c)
            #~ print("=> %c" % c )
            bPrintResultForDebug = 1
        c=c.lower()
        o += c
    #~ if bPrintResultForDebug: print("=> %s" % o )
    return o
    
def simpleString( s ):
    """
    change a string to lower case without accent and no hypen
    """
    bPrintResultForDebug = 0
    o = ""
    for c in s:
        if ord(c)>127:
            #~ print("in %s: %c" % (s,c) )
            c = removeAccent(c)
            #~ print("=> %c" % c )
            bPrintResultForDebug = 1
        elif c == '-':
            c = ' '
        c = c.lower()
        o += c
    #~ if bPrintResultForDebug: print("=> %s" % o )
    return o
    
    
def appendToDict( d, k, v ):
    """
    assign a value to a list in an element of a dict, if first time, create the list
    """
    try:
        d[k].append(v)
    except KeyError:
        d[k] = [v]
        
class Regions:
    """
    get region by department 
    and departement by region
    """
    def __init__( self ):
        #~ self.dictRegionId = {} # for each region, it's index
        self.dictRegionByDept = {} # dept_number as string (pour 2A => region name
        self.dictDeptByRegion = {} # region name => list of dept_number (as string)
        self.dictDeptByName = {} # dept name => dept_number (as string)
        self.dictDeptByNumber = {} #  dept_number (as string) => dept_name
        
    def load( self ):
        print("INF: Regions.load: loading regions data...")
        bVerbose = 0
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
        if strLocalPath == "": strLocalPath = '.'
        strFilename = strLocalPath + '/datas/region_dept.csv'
        enc = 'utf-8'
        enc = 'cp1252'
        file = openWithEncoding(strFilename, "rt", encoding = enc)
        line = file.readline() # skip first line

        while 1:
            line = file.readline()
            if len(line)<1:
                break
            if bVerbose: print("DBG: Regions.load: line: %s" % str(line) )
            line = line.replace('"','')
            fields = line.split(';')
            if bVerbose: print("DBG: Regions.load: fields: %s" % str(fields) )
            strDeptNumber, strDeptName, strRegionName = fields
            strRegionName = strRegionName.replace("\n", "" )
            #~ nDeptNumber = int(strDeptNumber) # bug 2A
            self.dictRegionByDept[strDeptNumber] = strRegionName
            self.dictDeptByName[strDeptName] = strDeptNumber
            self.dictDeptByNumber[strDeptNumber] = strDeptName
            appendToDict( self.dictDeptByRegion, cleanString(strRegionName),strDeptNumber)
            
                
    def findDept( self, region ):
        region = cleanString(region)
        try:
            return self.dictDeptByRegion[region]
        except KeyError as err:
            print("INF: Regions.findDept: can't find region '%s'" % region )
            return []
            
    def findRegion( self, num_dept ):
        num_dept = str(num_dept)
        try:
            return self.dictRegionByDept[num_dept]
        except KeyError as err:
            if num_dept == "20":
                return self.dictRegionByDept["2A"]
        return "Unknown Region"
        
    def getDeptName( self, num_dept ):
        num_dept = str(num_dept)
        return self.dictDeptByNumber[num_dept]
        
    def getDeptNumber( self, name_dept ):
        return self.dictDeptByName[name_dept]
        
    def getListRegions( self ):
        return self.dictDeptByRegion.keys()
        
# class Regions - end
    
class Cities:
    """
    Uses:
    1: Autocomplete, eg on a website: enter start of city, it completes with "full name (zip)"
        FindByRealName( city, bPartOf = True )
         
    2: Adress detection: give a zip and a city, it will validate it's really an adress, and can correct it.
        isValidAdress( zip, city ), return (zip,city,confidence) confidence of the right correction.
         
    3: Distance between two city: give two zip, it returns the distance
        distTwoZip( zip1, zip2 )
    """
    def __init__(self):
        self.dictCities = {} # city per zip (zip as a string, could start with unsignifiant 00 )=> (strDept,strZip,strCity Slug,strCity Real (including casse),float(strLong),float(strLat))
        self.dupCityPerZip = {} # some cities have same zip, so we store for each overwritten city slug their zip
        self.dupZipPerZip = {} # some zip are for the same cities, we store them here alternateZip => Zip
        self.cacheLastFindByRealName = (None,None,None) # city, partof, result of last research
        
        # refactor
        self.bEnableHash = 1
        #  assume slug is unique, so we have a dict with one element per city 
        # for each slug: (strDept,strZip,strCitySimple,strCityReal,float(strLong),float(strLat))
        self.cityPerSlug = {}
        
        self.zipToSlug = {} # for each zip, a list of associated slugs
        self.realNameToSlug = {} # for each city name in lower case, a list of associated slugs name
        self.simpleNameToSlug = {} # for each city name in lower case unhyphenised without accent, a list of associated slugs name
       
        self.warnMessages = [] # handle warn messages, not overflowing the output

    def load(self):
        print("INF: Cities: loading city data...")
        timeBegin = time.time()
        bVerbose = 0
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
        if strLocalPath == "": strLocalPath = '.'
        strFilename = strLocalPath + '/datas/villes_france.csv'
        enc = 'utf-8'
        file = openWithEncoding(strFilename, "rt", encoding = enc)
        line = file.readline() # skip first line
        self.dictCities = {}
        while 1:
            line = file.readline()
            if len(line)<1:
                break
            if bVerbose: print(line)
            line = line.replace('"','')
            fields = line.split(',')
            strDept = fields[1]
            if strDept == "dept":
                continue
            strZip = fields[8]
            strCitySimple = fields[4]
            strCityReal = fields[5]
            strCitySlug = fields[2]
            strLong = fields[19]
            strLat = fields[20]
            if bVerbose: print("strDept: %s, strZip: %s, strCity: %s, strLong: %s, strLat: %s" % (strDept,strZip,strCitySlug,strLong,strLat) ) 
            
            if self.bEnableHash:
                listZips = []
                if "-" not in strZip:
                    listZips.append(strZip)
                else:
                    listZips = strZip.split('-')
                
            if "-" in strZip:
                strAllZip = strZip.split('-')
                strNewZip = strAllZip[0][:-2]+"01" # prend le premier est kill les 2 derniers zeros
                if bVerbose: print( "strZip: %s changeto: %s" % (strZip,strNewZip) )
                for z in strAllZip:
                    self.dupZipPerZip[z] = strNewZip
                strZip = strNewZip
                
            if strZip in self.dictCities.keys():
                if bVerbose: print("WRN: Cities.load: storing (%s,%s,%s); on: %s" % (strDept,strZip,strCitySlug, str(self.dictCities[strZip])) )
                self.dupCityPerZip[self.dictCities[strZip][2]] = strZip
                pass
            self.dictCities[strZip] = (strDept,strZip,strCitySlug,strCityReal,float(strLong),float(strLat))
            
            if self.bEnableHash:
                self.cityPerSlug[strCitySlug] = (strDept,strZip,strCitySimple,strCityReal,float(strLong),float(strLat))
                for z in listZips:
                    appendToDict(self.zipToSlug, z,strCitySlug)
                appendToDict(self.realNameToSlug, strCityReal,strCitySlug)
                appendToDict(self.simpleNameToSlug, strCitySimple,strCitySlug)
        if bVerbose: 
            print("DBG: self.dupZipPerZip: %s" % str(self.dupZipPerZip))
            print("DBG: self.dupCityPerZip: %s" % str(self.dupCityPerZip))
        print("INF: Cities: loading city data - end duration: %.2fs" % (time.time()-timeBegin) )
        # mstab7: 0.27s
        # rpi4 2.7: 11.8s
        # rpi4 3.7: 1.18s
    # load - end
    
    def warn(self,msg):
        if msg in self.warnMessages:
            return
        self.warnMessages.append(msg)
        print(msg)
    
    @staticmethod
    def getCityRealName( c ):
        """
        take a city description and return the real name
        """
        return c[3]
        
    def findByZip( self, zip, bQuiet = True ):
        """
        return info on a city or None if not nound
        """
        if zip == None:
            print("WRN: findByZip: called with None => returning None" )
            return None
        if isinstance(zip, int):
            zip = "%05d" % zip
            
        if zip == "75000":
            zip = "75001"
        elif zip == "69000":
            zip = "69001"
        elif zip == "31000":
            zip = "31100"
        elif zip == "13000":
            zip = "13001"            
        # ne fonctione pas pour toutes les bigs cities
        #~ elif isBigCityZip(zip):
            #~ newzip = "%05d" % (int(zip)+1)
            #~ print("DBG: findByZip: changing zip %s to %s" % (zip,newzip) )
            #~ zip = newzip
            
        if self.bEnableHash:
            # use hashed dict
            try:
                listSlug = self.zipToSlug[zip]
            except KeyError:
                try:
                    listSlug = self.zipToSlug[zip[:-1]+"0"]
                except KeyError:
                    return None
                
            if len(listSlug)>1:
                self.warn("WRN: findByZip: this zip belongs to different cities: %s" % (listSlug) )
            k = listSlug[0]
            return self.cityPerSlug[k]
            
        try:
            return self.dictCities[zip]
        except KeyError:
            try:
                return self.dictCities[zip[:-2]+"01"]
            except KeyError:
                try:
                    return self.dictCities[self.dupZipPerZip[zip]]
                except KeyError as err:
                    if not bQuiet: print("WRN: findByZip: zip %s not found (err:%s)" % (zip,str(err) ) )
        return None
            
    def findBySlugName( self, strCityName, bPartOf=False ):
        """
        return the zip related to a city slug name
        """
        
        if self.bEnableHash:
            # use hashed dict
            strCityName = strCityName.lower()
            try:
                city = self.cityPerSlug[strCityName]
                return city[1] # 1: get zip
            except KeyError:
                pass
            return None

            
        strNormalisedCityName = strCityName.lower().replace('-', ' ') # WHY ? slugs have hyphens!
        for k,v in self.dictCities.items():
            #~ print(v[2])
            if v[2] == strNormalisedCityName or (bPartOf and strNormalisedCityName in v[2]):
                return k
        #~ print(self.dupCityPerZip)
        for k,v in self.dupCityPerZip.items():
            if k == strNormalisedCityName or (bPartOf and strNormalisedCityName in k):
                print("WRN: Cities.findBySlugName: city '%s' has been overwritten, returning neighbour" % k)
                return v
                    
        print("WRN: Cities.findBySlugName: city '%s' not found" % strCityName)
        return -1

    def findByRealName( self, strCityName, bPartOf=False ):
        """
        return the zip related to a city real name or -1 if not found
        bPartOf, ne fonctionne pas si dans dupCityPerZip
        """
        bVerbose = 0
        
        if strCityName == "":
            return -1
            
        if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            return self.cacheLastFindByRealName[2]
            
        if self.bEnableHash:
            # use hashed dict
            try:
                listSlug = self.realNameToSlug[strCityName]
            except KeyError:
                strSimpleName = simpleString(strCityName)
                try:
                    listSlug = self.simpleNameToSlug[strSimpleName]
                except KeyError:
                    if not bPartOf:
                        return -1
                    for k,v in self.simpleNameToSlug.items():
                        if strSimpleName in k:
                            listSlug = v
                            break
                    else:
                        return -1

            
            if len(listSlug)>1:
                self.warn("WRN: findByRealName: this city has different zip: %s" % (listSlug) )
            k = listSlug[0]
            return self.cityPerSlug[k][1] # 1: get zip
            
        strNormalisedCityName = cleanString(strCityName)
        for k,v in self.dictCities.items():
            #~ if 0: print("%s=>%s to compare with %s=>%s" % (strCityName,strNormalisedCityName,v[3],cleanString(v[3]) ) ) # at ovh: UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 5: ordinal not in range(128)
            if bVerbose: print("DBG: findByRealName: 1: '%s' to compare with '%s'" % (strNormalisedCityName,cleanString(v[3]) ) )
            if cleanString(v[3]) == strNormalisedCityName or (bPartOf and strNormalisedCityName in v[3]):
                if bVerbose: print("DBG: findByRealName: MATCH 1")
                self.cacheLastFindByRealName = (strCityName,bPartOf,k)
                return k
            if 0:
                # cherche dans les villes sans -, mais en fait si c'est dans dupCityPerZip, on les trouve pas. # a refactorer
                nohyp1 = strNormalisedCityName.replace('-',' ')
                nohyp2 = cleanString(v[3]).replace('-',' ')
                if bVerbose: print("DBG: findByRealName: 2: '%s' to compare with '%s'" % (nohyp1,nohyp2) )
                if nohyp1 == nohyp2:
                    if bVerbose: print("WRN: findByRealName: found, but with different '-'" )
                    return k
        #~ print("DBG: findByRealName: self.dupCityPerZip: %s" % self.dupCityPerZip.keys())
        if strNormalisedCityName in self.dupCityPerZip.keys(): # here bug: comparing real name and slug!
            out = self.dupCityPerZip[strNormalisedCityName]
            self.cacheLastFindByRealName = (strCityName,bPartOf,out)
            if bVerbose: print("DBG: findByRealName: MATCH 2: %s" % out)
            return out
        if bVerbose: print("WRN: Cities.findByRealName: city '%s' not found (bPartOf:%d)" % (strCityName,bPartOf))
        self.cacheLastFindByRealName = (strCityName,bPartOf,-1)
        return -1
        
    def isValidAdress( self, zip, strCityName ):
        """
        is this zip correpond roughly to this city.
        return zip, real name, confidence [0..1]
        or None,None,0
        """
        retVal = None,None,0.
        
        if isinstance(zip, int):
            zip = "%05d" % zip
            
        try:
            listSlug = self.zipToSlug[zip]
        except KeyError:
            return retVal
            
        strCityName = simpleString( strCityName )
        for k in listSlug:
            city = self.cityPerSlug[k]
            if strCityName in city[2]: # look in simplename
                sumLen = len(city[2]) + len(strCityName) # or max des 2, ca se discute
                rDiff = abs(len(city[2])-len(strCityName)) / float(sumLen) # on aurait pu faire une distance de Levenstein
                # rDiff can be from 0 to nearly 1
                rConfidence = 1. - rDiff
                
                print("DBG: isValidAdress: %s and %s => %s: %s, rConfidence: %.2f" % (zip, strCityName, zip, city[2], rConfidence) )
                return zip, city[2], rConfidence
        return retVal
        
    def distTwoZip(self,zip1,zip2,bVerbose=False):
        c1 = getLongLatParis(zip1)
        if c1 is None:

            c1 = self.findByZip(zip1)
            if c1 == None:
                print("WRN: distTwoZip: zip1 '%s' not found" % zip1)
                assert(0)
                return 99999
            if bVerbose: print("DBG: distTwoZip: ville 1: %s" % str(c1) )
            if bVerbose: print("DBG: distTwoZip: ville 1: long: %.3f, lat: %.3f" % (c1[4],c1[5]) )
            c1 = c1[4:6]
            
        c2 = getLongLatParis(zip2)
        if c2 is None:
            c2 = self.findByZip(zip2)
            if c2 == None:
                print("WRN: distTwoZip: zip2 '%s' not found" % zip2)
                assert(0)
                return 99999
                
            if bVerbose: print("DBG: distTwoZip: ville 2: %s" % str(c2) )
            if bVerbose: print("DBG: distTwoZip: ville 2: long: %.3f, lat: %.3f" % (c2[4],c2[5]) )
            c2 = c2[4:6]
            
        #~ return distLongLat(c1[4],c1[5],c2[4],c2[5])
        return distLongLat(c1[0],c1[1],c2[0],c2[1])
        
    def getLongLat(self,zip,bDefaultToClermont = False ):
        """
        return the long and lat of a city
        """
        c = self.findByZip(zip)
        if c == None:
            if not bDefaultToClermont:
                return 0,0
            print("WRN: Cities.getLongLat: zip %s is not in the database, returning Clermont" % zip )
            c = self.findByZip(63000) # 63000 is ClermontFerrand
        return c[4],c[5]
        
    def findZipInString(self,strCity):
        """
        receive a string and look for a zip in it
        zip can be sth like : "78170 La Celle-Saint-Cloud" or "78170 La Celle-Saint-Cloud"
        Return -1 if nothing found
        """
        if strCity ==  None:
            return -1
        s = strCity
        s = s.replace("-", "")
        s = s.replace(" ", "")
        if isRepresentInt(s[:5]):
            return int(s[:5])
        if isRepresentInt(s[:4]):
            return int(s[:4])        

        if isRepresentInt(s[:-5]):
            return int(s[:-5])
        if isRepresentInt(s[:-4]):
            return int(s[:-4])
        
        return self.findByRealName( strCity ) # perhaps it's just the city...
        
        
    def getAllRealCitiesName( self, bJoinZip = False, bJoinLatLong = False ):
        """
        return all loaded cities name (including the dupped)
        """
        listAll = []
        for k,v in self.dictCities.items():
            strCityName = v[3]
            if bJoinZip:
                strCityName += " (%s)" % v[0]
            listAll.append(strCityName)
        for k,v in self.dupCityPerZip.items():
            if bJoinZip:
                k += " (%s)" % v
            listAll.append(k)
        return listAll

    def getAllRealCitiesAndDatas( self ):
        """
        return all loaded cities  (including the dupped) as a list of list city,cp,long,lat
        """
        listAll = []
        if self.bEnableHash:
            for k,v in self.cityPerSlug.items():
                listAll.append([ v[3],v[1],v[4],v[5] ])       
            return listAll

        for k,v in self.dictCities.items():
            listAll.append([ v[3],v[0],v[4],v[5] ])
        for k,v in self.dupCityPerZip.items():
            cityAlt = self.findByZip(v)
            listAll.append([ k,v,cityAlt[4],cityAlt[5] ])
        return listAll
        
#class Cities - end

# create Cities static method
#~ # ne semble pas utile...
#~ Cities.getCityRealName = staticmethod(Cities.getCityRealName)



def findNearestUniv( zip_host, cities, dictUniv ):
    """
    take zip of a village, and find the nearest university using long and lat in city.
    Return the name and the distance
    """
    longcity,latcity = cities.getLongLat(zip_host)
    if (longcity,latcity) == (0,0):
        return None
    kMin = ""
    dMin= 9999
    for k,v in dictUniv.items():
        d = distLongLat(longcity,latcity,v[2],v[3])
        if d < dMin:
            dMin = d
            kMin = k
    return kMin,dMin
    

def generateStatHousing( cnx, bOutputHtml ):
    bVerbose = 0 # to debug
    
    bOutputResult = not bOutputHtml
    if not bOutputResult:
        bVerbose = 0
    
    cities = Cities()
    cities.load()
    if 0:
        rDist = cities.distTwoZip("75000","33000")
        rDist2 = cities.distTwoZip("59000","66000")
        print("Dist Paris-Bordeaux: %s" % rDist ) # devrait etre 499,20 km, courament: 544.98
        print("Dist Lille-Perpignan: %s" % rDist2 ) # devrait etre 882,49 km, courament: 883.59
        return
        
    #
    dictCityNbrStudent = loadListUnivercityCity()
    if bOutputResult: print("city by nbr of student: " + str(dictCityNbrStudent) )
    
    
    # add to the dict their zip and long/lat
    dictCityStudZipLongLat = {}
    for k,v in dictCityNbrStudent.items():
        if bOutputResult: print("univ: %s" % k )
        if "Aix-Mar" in k:
            k = "Marseille"
            
        zip = cities.findByRealName(k)
        if zip == -1:
            if bOutputResult: print("ERR: can't find zip for city '%s'" % k )
            zip = 49000
        long,lat = cities.getLongLat(zip)
        dictCityStudZipLongLat[k] = (v,zip,long,lat)
        
    
    rUniv, rDist = findNearestUniv( 63000, cities, dictCityStudZipLongLat )
    if bOutputResult: print("INF: Clermont is related to univ: %s,%5.2fkms" % (rUniv,rDist) )

    
    cursor = cnx.cursor()
    query = ("SELECT zip_code, city, validated, archive FROM housing WHERE validated = 1 and archive != 1 and is_deleted != 1")

    #~ hire_start = datetime.date(1999, 1, 1)
    #~ hire_end = datetime.date(1999, 12, 31)
    
    #~ cursor.execute(query, (hire_start, hire_end))

    cursor.execute(query)
    
    dictCode = dict()

    cptTotal = 0
    cptError = 0
    
    dictByUniv = dict()
    for (zip_code, city, validated, archive) in cursor:
        if bVerbose: print("zip: %7s: city: %12s, validated: %s, archive: %s" % (zip_code, city, validated, archive) )
        if not isRepresentInt(zip_code):
            zipFound = cities.findZipInString( city )
            if zipFound != -1:
                zip_code = zipFound

        if not isRepresentInt(zip_code):
            if bOutputResult: print("ERR: Unknown zip '%s', city '%s':" % (zip_code,city) )
            cptError +=1
        else:
            zip_code = int(zip_code)
            if zip_code not in dictCode.keys():
                dictCode[zip_code] = 0
            dictCode[zip_code] += 1
            
            retVal = findNearestUniv( zip_code, cities, dictCityStudZipLongLat )
            if retVal == None:
                if bOutputResult: print("WRN: unknown zip or cities: zip: %7s: city: '%s', validated: %s, archive: %s" % (zip_code, city, validated, archive) )
                continue
            strUniv, rDist = retVal
            if bVerbose: print("Find Nearest: %s => %s, %s" % ( zip_code, strUniv, rDist ) )
            if strUniv not in dictByUniv.keys():
                dictByUniv[strUniv] = (0,0)
            dictByUniv[strUniv] = (dictByUniv[strUniv][0]+1,dictByUniv[strUniv][1]+rDist)
            
        cptTotal += 1

    cursor.close()
    
    if bOutputResult: print("Nbr Housing: %s" % cptTotal )
    if bOutputResult: print("Nbr Invalid Zip: %s" % cptError )
    
    if bOutputResult: print("dictCode: %s" % dictCode )
    if bOutputResult: print("dictByUniv: %s" % dictByUniv )
    
    # compute average
    for k,v in dictByUniv.items():
        dictByUniv[k]=(v[0],v[1]/v[0])
    
    for k,v in sorted(dictCode.items()):
        if bOutputResult: print("CP: %s, Nbr Logement: %s" % (k,v) )
        
    for k,v in sorted(dictByUniv.items(),key=lambda x: x[1], reverse=True):
        if bOutputResult: print("Univ: %s, Nbr Logement: %s, avg dist: %5.1fkms" % (k,v[0],v[1]) )
        
    strOutputPath = "output/"
    try: os.makedirs(strOutputPath)
    except: pass    
    strNameByCode = "places_by_code.csv"
    strNameByUniv = "places_by_univ.csv"
    strTimeStamp =         "# generated at %s (a 1h ou 2h pres chez ovh)" % getTimeStamp()
    aLabelByCode = ("CP", "logement number",strTimeStamp)
    aLabelByUniv = ("university", "logement number", "average distance to university",strTimeStamp)
    outputCsv(dictCode, strOutputPath+strNameByCode, aLabelByCode ) 
    outputCsv(dictByUniv, strOutputPath+strNameByUniv, aLabelByUniv, key=lambda x: x[1], reverse=True ) 
    
    strWebsitePath = "../public/uploads/generated/"
    strAbsWebsitePath = "/uploads/generated/"
    
    if 1:
        # copy to website:
        try: os.makedirs(strWebsitePath)
        except: pass
        shutil.copyfile(strOutputPath+strNameByCode,strWebsitePath+strNameByCode)
        shutil.copyfile(strOutputPath+strNameByUniv,strWebsitePath+strNameByUniv)
        
    if bOutputHtml:
        strHtml = getAsHtmlTable(dictByUniv, aLabelByUniv[:-1], key=lambda x: x[1], reverse=True ) 
        if 1:
            # direct output
            print(strHtml)
        else:
            # output in a file
            file = open(strWebsitePath+strNameByUniv+".html", "wt")
            file.write(strHtml)
            file.write("<a href='" + strAbsWebsitePath+strNameByUniv + "'>download results</a>")
            file.close()
        
# generateStatHousing - end


bigCityZip = [
                    ("Paris", "75000"),
                    ( "Marseille", "13000"), 
                    ( "Lyon", "69000"), 
                    ( "Toulouse","31000"), 
                    ( "Nice","06000"), 
                    ( "Nantes","44000"), 
                    ( "Montpellier","34000"), 
                    ( "Strasbourg","67000"), 
                    ( "Bordeaux","33000"), 
                    ( "Lille", "59000"), 
                ]
                
def bigCityToZip( strCity ):
    """
    return the generic zip of big cities
    """
    for i in range(len(bigCityZip)):
        if bigCityZip[i][0].lower() == strCity.lower():
            return bigCityZip[i][1]
    print("ERR: cities_data.bigCityToZip: '%s' not found" % strCity )
    assert(1)
    return "-1"
    
def isBigCityZip(zip):
    for city,zipbig in bigCityZip:
        if zip == zipbig:
            return 1
    return 0
    
if 0:
    cities = Cities()
    cities.load()
    rdist=cities.distTwoZip("75001",bigCityToZip("Paris"))
    print(rdist)
    rdist=cities.distTwoZip("75001",bigCityToZip("Marseille"))
    print(rdist)    
    rdist=cities.distTwoZip("75001",bigCityToZip("Nice"))
    print(rdist)    
    
def statByRegion(bOutputHtml=False):
    import xeniadb
    #~ listPeoples(cnx)
    cnx = xeniadb.connect()
    generateStatHousing(cnx,bOutputHtml=bOutputHtml)
    cnx.close()
    
    


def autotest_cities():
    bUseHash = 1 # deactivate some test not working in previous version
    
    cities = Cities()
    cities.load()
    
    assert_equal( cities.findByRealName("Besançon"), "25000" )
    assert_equal( cities.findByRealName("Besancon"), "25000" )
    assert_equal( cities.findByRealName("Saint-etienne"), "42001" )
    assert_equal( cities.findByRealName("Orléans"), "45001" )
    assert_equal( cities.findByRealName("Nancy"), "54100" )
    retVal = cities.findByRealName("beaumont-pied-de-boeuf") # oe
    assert( retVal in ["53290","72500"] ) 
    assert_equal( cities.findByRealName("oeuf-en-ternois"), "62130" ) # oe en premier
    assert_equal( cities.findByRealName("ANCY-sur-moselle"), "57130" ) 
    if bUseHash:
        assert_equal( cities.findByRealName("ANCY sur moselle"), "57130" ) # real name is ANCY-sur-moselle, et c'est dans dupCityPerZip, donc pas trouvé
        assert_equal( cities.findByRealName("nissan lez enserune"),"34440")
        assert_equal( cities.findByRealName("nissan", bPartOf=True),"11220") # Tournissan
        assert_equal( cities.findByRealName("nissan lez", bPartOf=True),"34440") # Tournissan
    

    retVal = cities.findByZip("25000")
    assert_equal( retVal[1], "25000" )

    retVal = cities.findByZip("34400")
    assert_equal( retVal[1], "34400" )
    
    retVal = cities.findByZip("75014")
    assert_equal( retVal[1], "75001" )

    retVal = cities.findByZip("94440")
    assert_equal( retVal[1], "94440" )
    
    
    for city in ["Nissan", "Colombiers","Paris"]:
        retVal = cities.findBySlugName(city,bPartOf=True)
        print("INF: autotest: find Slug '%s', return: %s" % (city,str(retVal) ) )
        if retVal != -1:
            print("INF: autotest: detail: %s" % str(cities.findByZip(retVal)))
        retVal = cities.findByRealName(city,bPartOf=False)
        print("INF: autotest: find Real '%s', return: %s" % (city,str(retVal) ) )
        if retVal != -1:
            print("INF: autotest: detail: %s" % str(cities.findByZip(retVal)))
        print(""), 
        
        
    assert_equal( cities.findBySlugName("Paris"), "75001" )
    assert_equal( cities.findBySlugName("tremblay-sur-mauldre"), "78490" )
        
    # bug dist bondy/velizy2
    zip1 = cities.findByRealName("Bondy")
    assert_equal(zip1,"93140")
    #~ zip2 = cities.findByRealName("Vélizy")
    zip2 = "78140"
    dist = cities.distTwoZip(zip1,zip2,bVerbose=True)
    assert_diff(dist,22,5)
    
    # bug Schiltigheim / parly
    zip1 = cities.findByRealName("Schiltigheim")
    assert_equal(zip1,"67300")
    #~ zip2 = cities.findByRealName("Parly")
    #~ zip2 = cities.findByRealName("Le Chesnay-Rocquencourt")
    #~ assert_equal(zip2,"78150")
    zip2 = "78150"
    dist = cities.distTwoZip(zip1,zip2,bVerbose=True)
    assert_diff(dist,397,20)
    

    dist = cities.distTwoZip("75000","75001",bVerbose=True)
    assert_diff(dist,1,5)  
    
    dist = cities.distTwoZip("75006","34000",bVerbose=True)
    assert_diff(dist,596,20)        

    dist = cities.distTwoZip("33000","67000",bVerbose=True)
    assert_diff(dist,760,20)

    dist = cities.distTwoZip("75000","75001",bVerbose=True)
    
    dist = cities.distTwoZip("75020","75016",bVerbose=True)
    assert_diff(dist,9,4)
    
    dist = cities.distTwoZip("75008","75017",bVerbose=True)
    assert_diff(dist,0.82,0.3)

    
    assert_diff(cities.isValidAdress( "34440","colombier")[2],0.95)
    assert_diff(cities.isValidAdress( "34440","colom")[2],0.67)
    assert_diff(cities.isValidAdress( "34440","nissa")[2],0.42)
    assert_diff(cities.isValidAdress( "34440","a")[2],0.1)
    assert_diff(cities.isValidAdress( "34440","y")[2],0.)    
    
    timeBegin = time.time()
    for i in range(100):
        # en mettre plusieurs différent permet de zapper le cache
        cities.findByRealName("ozan") # le premier
        cities.findByRealName("st-pierre-et-miquelon") # le dernier
        cities.findByRealName("paris")
        cities.findByRealName("marseille")
        cities.findByRealName("zanzibar") # inconnu
    duration = time.time() - timeBegin
    print("INF: 1: 500 tests: %.1fs (%.1fms/recherche)" % (duration,duration/0.5 ) )
    # mstab7: 500 tests: 4.5s (9ms/recherche)
    # mstab7: passage au slugToZip:
    # 500 tests: 0.0s (0.0ms/recherche)
    
    timeBegin = time.time()
    for i in range(100):
        # en mettre plusieurs différent permet de zapper le cache
        cities.findByRealName("oza", bPartOf=1) # le premier
        cities.findByRealName("st-pierre-et-", bPartOf=1) # le dernier
        cities.findByRealName("pari", bPartOf=1)
        cities.findByRealName("marseill", bPartOf=1)
        cities.findByRealName("zanzibar" , bPartOf=1) # inconnu
    duration = time.time() - timeBegin
    print("INF: 2: 500 tests: %.1fs (%.1fms/recherche)" % (duration,duration/0.5 ) )
    # mstab7: 500 tests: 4.9s (9.8ms/recherche)
    # mstab7: passage au slugToZip
    # 500 tests: 0.7s (1.3ms/recherche)
    # mstab7: 500 tests: 0.0s (0.0ms/recherche)
    # RPI4_2.7: 500 tests: 0.0s (0.0ms/recherche)
    # RPI4_3.7: 500 tests: 0.0s (0.0ms/recherche)
    
    retVal = cities.findByZip("06000")
    assert_equal(retVal[1],"06001")

    retVal = cities.findByZip("06000")
    assert_equal(retVal[1],"06001")
    
    retVal = cities.findByZip("56000")
    assert_equal(retVal[1],"56000")

    retVal = cities.findByZip("69000")
    assert_equal(retVal[1],"69001")

    retVal = cities.findByZip("67000")
    assert_equal(retVal[1],"67001")

    retVal = cities.findByZip("63000")
    assert_equal(retVal[1],"63001")

    retVal = cities.findByZip("63001")
    assert_equal(retVal[1],"63001")
    
    
    # test all big city:
    for city,zip in bigCityZip:
        print( "INF: autotest: bigCityZip: testing %s" % zip )
        retVal = cities.findByZip(zip)
        print( "INF: autotest: bigCityZip: returning %s" % str(retVal) )
        if retVal == None or (retVal[1] != zip and retVal[1][:-1] != zip[:-1]):
            assert(0)        
    
    timeBegin = time.time()
    for i in range(100):
        # zip equally repartited
        retVal = cities.findByZip("10000")
        retVal = cities.findByZip("34440")
        retVal = cities.findByZip("54000")
        retVal = cities.findByZip("75014")
        retVal = cities.findByZip("94270")
        
    duration = time.time() - timeBegin
    print("INF: 2: 500 tests: %.1fs (%.1fms/recherche)" % (duration,duration/0.5 ) )
    # mstab7: 500 tests: 0.0s (0.0ms/recherche)
    # mstab7: passage au slugToZip (vaguement moins avantageux car on perd la recherche dans un dico en direct) (indirection)
    # 500 tests: 0.0s (0.0ms/recherche)
    # RPI4_2.7: 500 tests: 23.8s (47.7ms/recherche)
    # RPI4_3.7: 500 tests: 0.0s (0.0ms/recherche)
    
    assert_equal(isBigCityZip("67000"),1)
    assert_equal(isBigCityZip("34440"),0)
    
# autotest_cities - end

def autotest_region():
    r = Regions()
    r.load()
    print( "autotest_region: Regions list: %s" % str(r.getListRegions() ) )
    
    dpt = r.findDept( "Île-de-France" )
    assert_equal( dpt, ["75","77","78","91","92","93","94","95"] )

    region = r.findRegion( 34 )
    assert_equal( region, "Occitanie" )

    region = r.findRegion( 20 )
    assert_equal( region, "Corse" )
    
    region = r.findRegion( 94 )
    assert_equal( region, "Île-de-France" )
    
    val = r.getDeptName( 94 )
    assert_equal( val, "Val-de-Marne" )
    
    val = r.getDeptNumber( "Paris" )
    assert_equal( val, "75" )
    
# autotest_region - end
    
if __name__ == "__main__":
    if 1:
        autotest_cities()
        autotest_region()
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
        statByRegion( bOutputHtml = bOutputHtml )
