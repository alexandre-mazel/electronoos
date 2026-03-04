# -*- coding: utf-8 -*-

import datetime
import math
import os
import shutil
import sys
import time

import stringtools
import cities_data
from cities_data import assert_equal, assert_not_equal


    
kCityName = 0
kStateID = 2
kStateName = 3
kCountyName = 5
kLong = 6
kLat = 7
kZips = 15

class CitiesUs:
    """
    Uses:
    1: Autocomplete, eg on a website: enter start of city, it completes with "full name (zip)"
        findByRealName( city, bPartOf = True )
         
    2: Adress detection: give a zip and a city, it will validate it's really an adress, and can correct it.
        isValidAdress( zip, city ), return (zip,city,confidence) confidence of the right correction.
         
    3: Distance between two city: give two zip, it returns the distance
        distTwoZip( zip1, zip2 )
    """
    
    def __init__(self):
        self.dictCities = {} # id => (city, city_ascii?, state_id, state_name,county_fips, county_name,float(strLong),float(strLat),population, density, ranking?,list_of_zips)
        self.dictIdsPerZip = {} # zip as a string => (id1, id2, ...)
        self.dictIdsPerCityName = {} # zip as a string => (id1, id2, ...)
        #~ self.dupCityPerZip = {} # some cities have same zip, so we store for each overwritten city slug their zip
        #~ self.dupZipPerZip = {} # some zip are for the same cities, we store them here alternateZip => Zip
        #~ self.cacheLastFindByRealName = (None,None,None) # city, partof, result of last research
       
        self.warnMessages = [] # handle warn messages, not overflowing the output

    def load(self):
        bVerbose = 1
        bVerbose = 0
        
        print("INF: CitiesUS: loading city data...")
        timeBegin = time.time()
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
        if strLocalPath == "": strLocalPath = '.'
        strFilename = strLocalPath + '/datas/us_cities.csv'
        enc = 'utf-8'
        file = cities_data.openWithEncoding(strFilename, "rt", encoding = enc)
        line = file.readline() # skip first line
        self.dictCities = {}
        nDuplicateZip = 0
        nDuplicateCityName = 0
        while 1:
            line = file.readline()
            if len(line)<1:
                break
            if bVerbose: print(line)
            line = line.replace('"','')
            fields = line.split(',')
            if bVerbose: print("fields (%d): %s" % (len(fields), str(fields)) )
            strCity, strCityAscii, strStateId, strStateName, strCountyFips, strCountyName, strLat, strLong, strPopulation, \
                    strDensity, strSource, strMilitary, strIncorporated, strTimeZone, strRanking, strZips, strId = fields
            
            if bVerbose: print("strCity: %s,strCityAscii: %s,strStateId: %s,strStateName: %s,strCountyName: %s" % (strCity,strCityAscii,strStateId,strStateName,strCountyName) ) 
            
            if strId in self.dictCities:
                assert(0)
                
            listZips = strZips.split(" ")
            if bVerbose: print("listZips (%d): %s" % (len(listZips), str(listZips)) )
            self.dictCities[strId] = (strCity, strCityAscii, strStateId, strStateName, strCountyFips, strCountyName, float(strLong), float(strLat), strPopulation, \
                        strDensity, strSource, strMilitary, strIncorporated, strTimeZone, strRanking,listZips)
                        
            
            for z in listZips:
                if not z in self.dictIdsPerZip:
                    self.dictIdsPerZip[z] = []
                else:
                    first_id = self.dictIdsPerZip[z][0]
                    if bVerbose: print( "WRN: %s have same zip than %s: %s" % (strCity,self.dictCities[first_id][kCityName],z) )
                    nDuplicateZip += 1

                self.dictIdsPerZip[z].append( strId )
                
            if not strCity in self.dictIdsPerCityName:
                    self.dictIdsPerCityName[strCity] = []
            else:
                first_id = self.dictIdsPerCityName[strCity][0]
                if bVerbose: print( "WRN: %s/%s have same cityname than %s/%s" % (strCity,strCountyName,self.dictCities[first_id][kCityName],self.dictCities[first_id][kCountyName]) )
                nDuplicateCityName += 1

            self.dictIdsPerCityName[strCity].append( strId )
            
                
            #~ break
            
            
        # while each line
        
        print( "INF: %d loaded cities" % len(self.dictCities)  ) # should be 31257
        assert( len(self.dictCities) == 31257 )
        print( "WRN: %d duplicated zip found" % nDuplicateZip )
        print( "WRN: %d duplicated cityname found" % nDuplicateCityName )
        
        # manual addings:
                
        print("INF: Cities: loading city data - end duration: %.2fs" % (time.time()-timeBegin) )
    # load - end
    
    def warn(self,msg):
        if msg in self.warnMessages:
            return
        self.warnMessages.append(msg)
        print(msg)
    
        
    def findByZip( self, zip, bQuiet = True ):
        """
        return info on a city or None if not nound
        """
        if zip == None:
            print("WRN: CitiesUs.findByZip: called with None => returning None" )
            return None
            
        if isinstance(zip, int):
            zip = "%05d" % zip

            
        try:
            id = self.dictIdsPerZip[zip][0]
        except KeyError:
            return None
            
        return self.dictCities[id]

            
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
        return id related to a cityname
        """
        bVerbose = 0
        
        if strCityName == "":
            return -1
            
        #~ if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            #~ return self.cacheLastFindByRealName[2]
            
        
            
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
        if strNormalisedCityName in self.dupCityPerZip: # here bug: comparing real name and slug!
            out = self.dupCityPerZip[strNormalisedCityName]
            self.cacheLastFindByRealName = (strCityName,bPartOf,out)
            if bVerbose: print("DBG: findByRealName: MATCH 2: %s" % out)
            return out
        if bVerbose: print("WRN: Cities.findByRealName: city '%s' not found (bPartOf:%d)" % (strCityName,bPartOf))
        self.cacheLastFindByRealName = (strCityName,bPartOf,-1)
        return -1
        
    def findByLongLat( self, rLong, rLat ):
        """
        find nearest city of a gps point.
        return slug name
        """
        # for each slug: (strDept,strZip,strCitySimple,strCityReal,float(strLong),float(strLat))
        strMinSlug = ""
        rMinDist = 999
        for slug,data in self.cityPerSlug.items():
            citylong,citylat = data[4:6]
            diff = (citylong-rLong)*(citylong-rLong)+(citylat-rLat)*(citylat-rLat)
            if diff < rMinDist:
                rMinDist = diff
                strMinSlug = slug
                #~ print("DBG: findByLongLat: diff: %.3f, slug: %s" % (diff,slug))
        
        city = self.cityPerSlug[strMinSlug]
        dist = distLongLat(rLong, rLat,city[4],city[5])
        print("DBG: findByLongLat: exiting with: diff: %.3f, slug: %s (dist: %.3f)" % (rMinDist,strMinSlug,dist))
        return strMinSlug,dist
            
        
        
        
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
        
    def distTwoZip( self, zip1, zip2, bApproxSearch=True, bVerbose=False ):
        """
        - bApproxSearch: set to one to accept city name as zipcode, eg Saint-Tropez instead of 83990
        """
        c1 = getLongLatParis(zip1)
        if c1 is None:

            c1 = self.findByZip(zip1,bQuiet=not bVerbose)
            if c1 == None:
                print("WRN: distTwoZip: zip1 '%s' not found" % zip1)
                if not bApproxSearch:
                    assert(0)
                    return 99999
                zip1 = self.findByRealName(zip1)
                print("WRN: distTwoZip: zip1 changed to '%s'" % zip1)
                c1 = self.findByZip(zip1,bQuiet=not bVerbose)
                if c1 == None:
                    print("WRN: distTwoZip: zip1 '%s' not found" % zip1)
                    if not bApproxSearch:
                        assert(0)
                        return 99999                    
                
            if bVerbose: print("DBG: distTwoZip: ville 1: %s" % str(c1) )
            if bVerbose: print("DBG: distTwoZip: ville 1: long: %.3f, lat: %.3f" % (c1[4],c1[5]) )
            c1 = c1[4:6]
            
        c2 = getLongLatParis(zip2)
        if c2 is None:
            c2 = self.findByZip(zip2,bQuiet=not bVerbose)
            if c2 == None:
                print("WRN: distTwoZip: zip2 '%s' not found" % zip2)
                if not bApproxSearch:
                    assert(0)
                    return 99999
                zip2 = self.findByRealName(zip2)
                print("WRN: distTwoZip: zip2 changed to '%s'" % zip2)
                c2 = self.findByZip(zip2,bQuiet=not bVerbose)
                if c2 == None:
                    print("WRN: distTwoZip: zip2 '%s' not found" % zip1)
                    if not bApproxSearch:
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
            # add paris 2 to 20
            for i in range(2,21):
                zip = "750"+("%02d"%i)
                ret = getLongLatParis(zip)
                #~ print(ret)
                long,lat = ret
                listAll.append( ["Paris", zip, long, lat ] )
            return listAll

        for k,v in self.dictCities.items():
            listAll.append([ v[3],v[0],v[4],v[5] ])
        for k,v in self.dupCityPerZip.items():
            cityAlt = self.findByZip(v)
            listAll.append([ k,v,cityAlt[4],cityAlt[5] ])
        return listAll
        
    def zipToHumanised( self, zip ):
        city = self.findByZip( zip )
        if city == None:
            print("WRN: zipToHumanised city is None for zip '%s'" % zip )
            return ""
        strCity = city[3]
        
        #~ if isBigCityZip(zip): #c'est debile de dire dans le premier arrt de Nice!
        if zip[:2] in ['75','13','69'] and isBigCityZip(zip):
            arrt = ordinalToStr(zip[-2:])
            if sys.version_info[0]<3 and isinstance(arrt,unicode):
                arrt = arrt.encode("utf-8", 'replace')
            if sys.version_info[0]<3 and isinstance(strCity,unicode):
                strCity = strCity.encode("utf-8", 'replace')
            strOut = "dans le " + arrt + " arrondissement de " + strCity
        else:
            if sys.version_info[0]<3:
                if isinstance(strCity,unicode):
                    strCity = strCity.encode("utf-8", 'replace')
                strOut = u"à ".encode("utf-8", 'replace') + strCity
            else:
                strOut = "à " + strCity
        return strOut
        
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
            if zip_code not in dictCode:
                dictCode[zip_code] = 0
            dictCode[zip_code] += 1
            
            retVal = findNearestUniv( zip_code, cities, dictCityStudZipLongLat )
            if retVal == None:
                if bOutputResult: print("WRN: unknown zip or cities: zip: %7s: city: '%s', validated: %s, archive: %s" % (zip_code, city, validated, archive) )
                continue
            strUniv, rDist = retVal
            if bVerbose: print("Find Nearest: %s => %s, %s" % ( zip_code, strUniv, rDist ) )
            if strUniv not in dictByUniv:
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
    zip = zip[:-2]+"00" # change 75008 to 75000
    for city,zipbig in bigCityZip:
        if zip == zipbig:
            return 1
    return 0
    
def getTop50():
    """
    src: https://www.linternaute.com/ville/classement/villes/population on 9 aout 2022
    """
    return [
                "Paris",
                "Marseille",
                "Lyon",
                "Toulouse",
                "Nice",
                "Nantes",
                "Montpellier",
                "Strasbourg",
                "Bordeaux",
                "Lille",
                "Rennes",
                "Reims",
                "Toulon",
                "Saint-Étienne",
                "Le Havre",
                "Grenoble",
                "Dijon",
                "Angers",
                "Villeurbanne",
                "Saint-Denis",
                "Nîmes",
                "Clermont-Ferrand",
                "Le Mans",
                "Aix-en-Provence",
                "Brest",
                "Tours",
                "Amiens",
                "Limoges",
                "Annecy",
                "Boulogne-Billancourt",
                "Perpignan",
                "Besançon",
                "Metz",
                "Orléans",
                "Saint-Denis",
                "Rouen",
                "Argenteuil",
                "Montreuil",
                "Mulhouse",
                "Caen",
                "Nancy",
                "Saint-Paul",
                "Roubaix",
                "Tourcoing",
                "Nanterre",
                "Vitry-sur-Seine",
                "Créteil",
                "Avignon",
                "Poitiers",
                "Aubervilliers",
        ]

# getTop50 - end


def autotest_cities():
    cities = CitiesUs()
    cities.load()
    #  mstab7_2.7 : 
    #  mstab7_3.9 : 0.18
    # RPI4_2.7      : 
    # RPI4_3.7      : 
    
    assert_equal( cities.findByZip("666"), None )
    assert_not_equal( cities.findByZip("11220"), None )
    assert_equal( cities.findByZip("11220")[0], "New York" )
    
    
    
    
    
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

    retVal = cities.findByZip("35001")
    assert_equal( retVal[1], "35001" )    
    
    
    
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

    # bug Saint-Tropez
    zipFoireux = "Saint-Tropez"
    dist = cities.distTwoZip(zipFoireux,"34000",bVerbose=True)
    assert_diff(dist,225,5)
    dist = cities.distTwoZip("75006",zipFoireux,bVerbose=True)
    assert_diff(dist,703,5)
    dist = cities.distTwoZip("75006","Saint+Tropez",bVerbose=True)
    assert_diff(dist,703,5)
    
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
    
    dist = cities.distTwoZip("69001","75001",bVerbose=True)
    assert_diff(dist,400,20)

    dist = cities.distTwoZip("69001","75004",bVerbose=True)
    assert_diff(dist,400,20)
    
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
    
    if 1:
        # this test takes time in python2.7
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
        # mstab7: passage au slugToZip:
        #  mstab7_2.7: 500 tests: 4.9s (9.8ms/recherche)
        #  mstab7_3.9: 500 tests: 0.7s (1.5ms/recherche)
        # RPI4_2.7: 500 tests: 23.7s (47.3ms/recherche)
        # RPI4_3.7: 500 tests: 1.8s (3.6ms/recherche)
    
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
    print("INF: 3: 500 tests: %.1fs (%.1fms/recherche)" % (duration,duration/0.5 ) )
    # mstab7: 500 tests: 0.0s (0.0ms/recherche)
    # mstab7: passage au slugToZip (vaguement moins avantageux car on perd la recherche dans un dico en direct) (indirection)
    #  mstab7_2.7: 500 tests: 0.0s (0.0ms/recherche)
    #  mstab7_3.9: 500 tests: 0.0s (0.0ms/recherche)
    # RPI4_2.7: 500 tests:  0.0s (0.0ms/recherche)
    # RPI4_3.7: 500 tests: 0.0s (0.0ms/recherche)
    
    assert_equal(isBigCityZip("67000"),1)
    assert_equal(isBigCityZip("34440"),0)
    
    assert_equal(cities.zipToHumanised("94270"),"à Le Kremlin-Bicêtre")
    assert_equal(cities.zipToHumanised("34440"),"à Nissan-lez-Enserune")
    assert_equal(cities.zipToHumanised("75008"),"dans le 8ème arrondissement de Paris")
    assert_equal(cities.zipToHumanised("06001"),"à Nice")

    retVal = cities.findByZip("75001")
    print("DBG: autotest: get paris: %s" % str(retVal) )
    
    retVal = cities.findByZip("34440")
    print("DBG: autotest: get nissan: %s" % str(retVal) )
    
    retVal = cities.findByZip("98000")
    print("DBG: autotest: get monaco: %s" % str(retVal) )
    assert_equal(retVal[1],"98000")
    
    dist = cities.distTwoZip("98000","06500",bVerbose=True) # Menton et Monaco
    assert_diff(dist,11,4)
    
    val,dist = cities.findByLongLat(2.345418299722222,48.80381479972222) # ma maison
    assert_equal( val, "arcueil" )
    assert_diff( dist, 0.9, 10.2 )
    
    val,dist = cities.findByLongLat(6.163830555555556,45.897038888888886) # les chaises longues prés d'annecy
    assert_equal( val, "veyrier-du-lac" )
    assert_diff( dist, 1.5, 0.2 )
    
    val,dist = cities.findByLongLat(6.163830555555556,45.897038888888886) # les chaises longues prés d'annecy
    assert_equal( val, "veyrier-du-lac" )
    assert_diff( dist, 1.5, 0.2 )

    val,dist = cities.findByLongLat(2.324166835348288,48.84538969379644) # rue littre
    assert_equal( val, "paris" )
    assert_diff( dist, 2.2, 0.2 )
    
# autotest_cities - end
    
if __name__ == "__main__":
    if 1:
        autotest_cities()
        #~ autotest_region()
        print("INF: autotest passed [GOOD]")
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
        statByRegion( bOutputHtml = bOutputHtml )
