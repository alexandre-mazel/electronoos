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

def assert_diff(a,b,diff):
    if abs(a-b)<diff:
        print("(%s diff %s < %s) => ok" % (a,b,diff))
    else:
        print("(%s diff %s) => NOT ok (type:%s and %s)" % (a,b,type(a),type(b)))
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
    

def removeAccent( c ):
    acc="ÉÈÎâàçéêëèîïôûüùŷÿ"
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
    else:
        try:
            print("DBG: removeAccent: not found: %c (%s)" % (c,ord(c) ))
        except BaseException as err:
            print("DBG: removeAccent: catch else: ord: %s, err: %s" % (ord(c),err) )
        c="" # it should remains only invisible char like the square before "oe"
    return c
    
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
    
    
class Cities:
    def __init__(self):
        self.dictCities = {} # city per zip (zip as a string, could start with unsignifiant 00 )=> (strDept,strZip,strCity Slug,strCity Real (including casse),float(strLong),float(strLat))
        self.dupCityPerZip = {} # some cities have same zip, so we store for each overwritten city slug their zip
        self.dupZipPerZip = {} # some zip are for the same cities, we store them here alternateZip => Zip
        self.cacheLastFindByRealName = (0,0,0) # city, partof, result of last research
        
    def load(self):
        print("INF: Cities: loading city data...")
        bVerbose = 0
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
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
            strCityReal = fields[5]
            strCitySlug = fields[2]
            strLong = fields[19]
            strLat = fields[20]
            if bVerbose: print("strDept: %s, strZip: %s, strCity: %s, strLong: %s, strLat: %s" % (strDept,strZip,strCitySlug,strLong,strLat) ) 
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
        if bVerbose: 
            print("DBG: self.dupZipPerZip: %s" % str(self.dupZipPerZip))
            print("DBG: self.dupCityPerZip: %s" % str(self.dupCityPerZip))
    # load - end
    
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
        if isinstance(zip, int):
            zip = "%05d" % zip
            
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
        strNormalisedCityName = strCityName.lower().replace('-', ' ')
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
        return the zip related to a city real name
        bPartOf, ne fonctionne pas si dans dupCityPerZip
        """
        bVerbose = 0
        
        if strCityName == "":
            return -1
            
        if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            return self.cacheLastFindByRealName[2]
            
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
        
    def distTwoZip(self,zip1,zip2,bVerbose=False):
        c1 = self.findByZip(zip1)
        c2 = self.findByZip(zip2)
        if bVerbose: print("DBG: distTwoZip: ville 1: %s" % str(c1) )
        if bVerbose: print("DBG: distTwoZip: ville 1: long: %.3f, lat: %.3f" % (c1[4],c1[5]) )
        if bVerbose: print("DBG: distTwoZip: ville 2: %s" % str(c2) )
        if bVerbose: print("DBG: distTwoZip: ville 2: long: %.3f, lat: %.3f" % (c2[4],c2[5]) )
        return distLongLat(c1[4],c1[5],c2[4],c2[5])
        
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



def autotest_cities():
    cities = Cities()
    cities.load()
    
    assert_equal( cities.findByRealName("Besançon"), "25000" )
    assert_equal( cities.findByRealName("Besancon"), "25000" )
    assert_equal( cities.findByRealName("Saint-etienne"), "42001" )
    assert_equal( cities.findByRealName("Orléans"), "45001" )
    assert_equal( cities.findByRealName("Nancy"), "54100" )
    assert_equal( cities.findByRealName("beaumont-pied-de-boeuf"), "72500" ) # oe
    assert_equal( cities.findByRealName("oeuf-en-ternois"), "62130" ) # oe en premier
    assert_equal( cities.findByRealName("ANCY-sur-moselle"), "57130" ) 
    #~ assert_equal( cities.findByRealName("ANCY sur moselle"), "57130" ) # real name is ANCY-sur-moselle, et c'est dans dupCityPerZip, donc pas trouvé
    
    
    
    
    for city in ["Nissan", "Colombiers","Paris"]:
        retVal = cities.findBySlugName(city,bPartOf=True)
        print("INF: find Slug'%s', return: %s" % (city,str(retVal) ) )
        if retVal != -1:
            print("detail: %s" % str(cities.findByZip(retVal)))
        retVal = cities.findByRealName(city,bPartOf=False)
        print("INF: find Real'%s', return: %s" % (city,str(retVal) ) )
        if retVal != -1:
            print("detail: %s" % str(cities.findByZip(retVal)))
        print("")
        
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
    

    dist = cities.distTwoZip("75006","34000",bVerbose=True)
    assert_diff(dist,596,20)        

    dist = cities.distTwoZip("33000","67000",bVerbose=True)
    assert_diff(dist,760,20)      
    
    timeBegin = time.time()
    for i in range(100):
        # en mettre plusieurs différent permet de zapper le cache
        cities.findByRealName("ozan") # le premier
        cities.findByRealName("oeuf-en-ternois")
        cities.findByRealName("paris")
        cities.findByRealName("marseille")
        cities.findByRealName("zanzibar") # inconnu
    duration = time.time() - timeBegin
    print("INF: 500 tests: %.1fs (%.1fms/recherche)" % (duration,duration/0.5 ) )

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


def bigCityToZip( strCity ):
    """
    return the generic zip of big cities
    """
    cityzip = [
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
    for i in range(len(cityzip)):
        if cityzip[i][0].lower() == strCity.lower():
            return cityzip[i][1]
    print("ERR: cities_data.bigCityToZip: '%s' not found" % strCity )
    assert(1)
    return "-1"
    
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
    
if __name__ == "__main__":
    if 1:
        autotest_cities()
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
        statByRegion( bOutputHtml = bOutputHtml )
