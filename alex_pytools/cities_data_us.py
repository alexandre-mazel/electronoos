# -*- coding: utf-8 -*-

import datetime
import math
import os
import shutil
import sys
import time

import stringtools
import cities_data
from cities_data import assert_equal, assert_not_equal, assert_diff, distLongLat


    
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
            
            strId = strId.strip() # remove EOL
            
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
        
    def getCityById( self, id ):
        try:
            return self.dictCities[id]
        except KeyError:
            print("WRN: CitiesUs.getCityById: city with id: '%s' not found..." % id )
            pass
        return None
        
    def getCityAndCountyNameById( self, id ):
        try:
            return self.dictCities[id][kCityName] + "/" + self.dictCities[id][kCountyName]
        except KeyError:
            print("WRN: CitiesUs.getCityById: city with id: '%s' not found..." % id )
            pass
        return "/"
    
        
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

            

    def findByName( self, strCityName, strCountyName = None, bPartOf=False ):
        """
        return id related to a cityname.
        WRN: If countyname is bad and bPartOf is False, it will return -1 even if city exists
        """
        bVerbose = 0
        
        if strCityName == "":
            return -1
            
        #~ if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            #~ return self.cacheLastFindByRealName[2]
            
        try:
            listIds = self.dictIdsPerCityName[strCityName]
        except KeyError:
            return -1

            
        if len(listIds) > 1:
            if strCountyName == None:
                self.warn("WRN: CitiesUs.findByName: this city name has different cities: %s" % (listIds) )
                id = listIds[0]
            else:
                for id in listIds:
                    print( "DBG: CitiesUs.findByName try to match '%s' and '%s'" % (strCountyName,dictCities[id][kCountyName]) ) 
                    if self.dictCities[id][kCountyName]== strCountyName:
                        return id
                self.warn("WRN: CitiesUs.findByName: this city name '%s', exist but not with this countyname: '%s' (1)" % (strCityName,strCountyName) )
                return -1
        else:
            id = listIds[0]
            if strCountyName != None and self.dictCities[id][kCountyName] != strCountyName:
                self.warn("WRN: CitiesUs.findByName: this city name '%s' exist but not with this countyname: '%s' (2)" % (strCityName,strCountyName) )
                return -1
        return id

        
    def findByLongLat( self, rLong, rLat ):
        """
        find nearest city of a gps point
        return id
        """
        strMinId = ""
        rMinDist = 99999999999
        for id,data in self.dictCities.items():
            citylong,citylat = data[kLong:kLat+1]
            #~ diff = (citylong-rLong)*(citylong-rLong)+(citylat-rLat)*(citylat-rLat) # approx to gain time
            diff = distLongLat(rLong, rLat,citylong,citylat)
            if diff < rMinDist:
                rMinDist = diff
                strMinId = id
                #~ print("DBG: findByLongLat: diff: %.3f, slug: %s" % (diff,slug))
        
        city = self.dictCities[strMinId]
        dist = distLongLat(rLong, rLat,city[kLong],city[kLat])
        print("DBG: findByLongLat: exiting with: %s/%s diff: %.3fkm, id: %s (dist: %.3f)" % (city[kCityName],city[kCountyName], rMinDist,strMinId,dist))
        return strMinId,dist
            
        
        
        
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
        
    def distTwoCity( self, city1, county1, city2, county2, bApproxSearch=True, bVerbose=False ):
        id1 = self.findByName( city1, county1 )
        id2 = self.findByName( city2, county2 )
        return self.distTwoIds( id1, id2 )

    def distTwoIds( self, id1, id2 ):
        lo1, la1 = self.dictCities[id1][kLong:kLat+1]
        lo2, la2 = self.dictCities[id2][kLong:kLat+1]
        
        return distLongLat( lo1, la1, lo2, la2 )
        
#class Cities - end




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
    
    assert_not_equal( cities.findByName("New York"), -1 )
    assert_equal( cities.getCityById( cities.findByName("New York") )[0], "New York" )
    assert_equal( cities.getCityById( cities.findByName("New York") )[0], "New York" )
    
    print("Test: findByName adding CountyName")
    assert_equal( cities.findByName("New York","bad countyname"), -1 )
    assert_equal( cities.findByName("New York","San Francisco"), -1 ) # another bad county name
    assert_equal( cities.getCityAndCountyNameById( cities.findByName("New York","Queens") ), "New York/Queens" )
    assert_equal( cities.getCityAndCountyNameById( cities.findByName("San Francisco","San Francisco") ), "San Francisco/San Francisco" )
    assert_equal( cities.findByName("San Francisco","Caca"), -1 )
    
    #~ assert_equal( cities.getCityById(cities.findByLongLat(-74.01380,40.70879)[0])[0], "New York" )
    assert_equal( cities.getCityById(cities.findByLongLat(-74.01380,40.70879)[0])[0], "Hoboken" ) # Un quartier précis de New York
    assert_equal( cities.getCityAndCountyNameById(cities.findByLongLat(-74.01380,40.70879)[0]), "Hoboken/Hudson" ) # Paris
    assert_equal( cities.getCityAndCountyNameById(cities.findByLongLat(-122.41903,37.77500)[0]), "San Francisco/San Francisco" ) # Paris
    
    assert_diff( cities.distTwoCity( "New York","Queens", "San Francisco","San Francisco" ), 4189.4 ) #~ 4768km a pied
    

# autotest_cities - end
    
if __name__ == "__main__":
    if 1:
        autotest_cities()
        #~ autotest_region()
        print("INF: CitiesUs.autotest passed [GOOD]")
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
        statByRegion( bOutputHtml = bOutputHtml )
