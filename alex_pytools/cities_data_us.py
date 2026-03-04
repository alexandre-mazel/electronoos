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


import misctools # for levenshtein
    
kCityName = 0 # version sans accent
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
        
    NB: Cities are sorted by population, so all research with many answers will return the biggest city
    """
    
    def __init__(self):
        self.dictCities = {} # id => (city_ascii (sans accent), city avec accent, state_id, state_name,county_fips, county_name,float(strLong),float(strLat),population, density, ranking?,list_of_zips)
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
        nTotalPopulation = 0
        nNbrCityMore100k = 0
        nNbrCityMore100kCalifornia = 0
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
            self.dictCities[strId] = (strCityAscii, strCity, strStateId, strStateName, strCountyFips, strCountyName, float(strLong), float(strLat), strPopulation, \
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
                if bVerbose: print( "WRN: %s/%s have same cityname than %s/%s" % (strCity,strStateName,self.dictCities[first_id][kCityName],self.dictCities[first_id][kCountyName]) )
                nDuplicateCityName += 1

            self.dictIdsPerCityName[strCity].append( strId )
            
            nPop = int( strPopulation )
            nTotalPopulation += nPop
            if nPop >= 100000:
                nNbrCityMore100k += 1
                if strStateName == "California":
                    nNbrCityMore100kCalifornia += 1
            
            # un peu de debug/exploration
            if 0:
                if strCity != strCityAscii:
                    print( "INF: ascii: %s != %s" % (strCityAscii, strCity) ) # eg Bayamon avec un accent aigu sur le 0 ou San German avec un accent aigu sur le a
                
            #~ break
            
        # while each line - end
        
        # official stats: Over 109,000 cities and towns from all 50 states
        # 346 over 100k as of July 1, 2024, as estimated by the U.S. Census Bureau
        # 76 in california
        # 348,503,802 inhabitants as of March 2 2026, ref worldometer
        
        print( "INF: %d loaded cities" % len(self.dictCities)  ) # should be 31257
        print( "INF: %d inhabitants" % nTotalPopulation  ) # should be 406,992,621 (too much)
        print( "INF: nNbrCityMore100k: %d" % nNbrCityMore100k  ) # Currently 472 instead of 346
        print( "INF: nNbrCityMore100kCalifornia: %d" % nNbrCityMore100kCalifornia ) # Currently 86 instead of 76
        assert( len(self.dictCities) == 31257 )
        assert( nTotalPopulation == 406992621 )
        assert( nNbrCityMore100k == 472 )
        assert( nNbrCityMore100kCalifornia == 86 )
        
        print( "WRN: %d duplicated zip found" % nDuplicateZip )
        print( "WRN: %d duplicated cityname found" % nDuplicateCityName )
        
        # manual addings:
                
        print("INF: CitiesUs: loading city data - end duration: %.2fs" % (time.time()-timeBegin) )
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
        
    def getCityAndStateNameById( self, id ):
        try:
            return self.dictCities[id][kCityName] + "/" + self.dictCities[id][kStateName]
        except KeyError:
            print("WRN: CitiesUs.getCityAndStateNameById: city with id: '%s' not found..." % id )
            pass
        return "/"

    def getCityAndStatePairById( self, id ):
        try:
            return self.dictCities[id][kCityName], self.dictCities[id][kStateName]
        except KeyError:
            print("WRN: CitiesUs.getCityAndStatePairById: city with id: '%s' not found..." % id )
            pass
        return ("","")
        
    def getCityAndCountyNameById( self, id ):
        try:
            return self.dictCities[id][kCityName] + "/" + self.dictCities[id][kCountyName]
        except KeyError:
            print("WRN: CitiesUs.getCityAndCountyNameById: city with id: '%s' not found..." % id )
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
            

    def findByName( self, strCityName, strStateName = None, bPartOf=False ):
        """
        return id related to a cityname.
        WRN: If strStateName is bad and bPartOf is False, it will return -1 even if city exists
        """
        bVerbose = 0
        
        if strCityName == "":
            return -1
            
        #~ if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            #~ return self.cacheLastFindByRealName[2]
            
        try:
            listIds = self.dictIdsPerCityName[strCityName]
        except KeyError:
            if bPartOf: 
                for id,c in self.dictCities.items():
                    if strCityName in c[kCityName]:
                        return id
            return -1

            
        if len(listIds) > 1:
            if strStateName == None:
                self.warn("WRN: CitiesUs.findByName: this city name has different cities: %s" % (listIds) )
                id = listIds[0]
            else:
                for id in listIds:
                    print( "DBG: CitiesUs.findByName try to match '%s' and '%s'" % (strStateName,self.dictCities[id][kStateName]) ) 
                    if self.dictCities[id][kStateName]== strStateName:
                        return id
                self.warn("WRN: CitiesUs.findByName: this city name '%s', exist but not with this statename: '%s' (1)" % (strCityName,strStateName) )
                return -1
        else:
            id = listIds[0]
            if not bPartOf and strStateName != None and self.dictCities[id][kStateName] != strStateName:
                self.warn("WRN: CitiesUs.findByName: this city name '%s' exist but not with this statename: '%s' (2)" % (strCityName,strStateName) )
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
        print("DBG: findByLongLat: exiting with: %s/%s diff: %.3fkm, id: %s (dist: %.3f)" % (city[kCityName],city[kStateName], rMinDist,strMinId,dist))
        return strMinId,dist
            
        
        
        
    def isValidAdress( self, zip, strCityName, strStateName = None ):
        """
        is this zip correpond roughly to this city.
        return zip, real name, state name, confidence [0..1]
        or None,None, None, 0
        """
        retValNone = None,None,None, 0.
        
        if isinstance(zip, int):
            zip = "%05d" % zip
            
        ids = self.dictIdsPerZip[zip]
        
        for id in ids:
            city = self.dictCities[id]
            if strCityName == city[kCityName] and ( strStateName == None or strStateName == city[kStateName] ):
                return zip, city[kCityName], city[kStateName], 1
                
        # else recherche approximative, au plus proche
        dist_min = 999999
        id_min = -1
        for id in ids:
            city = self.dictCities[id]
            dist = misctools.levenshtein( strCityName, city[kCityName] )
            if strStateName != None:
                dist += misctools.levenshtein( strStateName, city[kStateName] )
            if dist < dist_min:
                dist_min = dist
                id_min = id
        if dist_min < 6:
            length = len(strCityName)
            if strStateName != None:
                length += len(strStateName)
            city = self.dictCities[id_min]
            return zip, city[kCityName], city[kStateName], 1 - (dist_min/length)
        
        
        return retValNone
        
        
    def distTwoCity( self, city1, county1, city2, county2 = None, bApproxSearch=True, bVerbose=False ):
        id1 = self.findByName( city1, county1 )
        id2 = self.findByName( city2, county2 )
        return self.distTwoIds( id1, id2 )

    def distTwoIds( self, id1, id2 ):
        if id1 == -1:
            print( "WRN: distTwoIds: id1 is -1, returning 999999")
            return 999999
        if id2 == -1:
            print( "WRN: distTwoIds: id2 is -1, returning 999999")
            return 999999
        lo1, la1 = self.dictCities[id1][kLong:kLat+1]
        lo2, la2 = self.dictCities[id2][kLong:kLat+1]
        
        return distLongLat( lo1, la1, lo2, la2 )
        
#class CitiesUS - end




def autotest_cities():
    cities = CitiesUs()
    cities.load()
    #  mstab7_2.7 : 
    #  mstab7_3.9 : 0.19
    # RPI4_2.7      : 
    # RPI4_3.7      : 
    
    assert_equal( cities.findByZip("666"), None )
    assert_not_equal( cities.findByZip("11220"), None )
    assert_equal( cities.findByZip("11220")[0], "New York" )
    assert_equal( cities.findByZip("35816")[0], "Huntsville" )
    assert_equal( cities.findByZip("90210")[0], "Los Angeles" )
    
    assert_equal( cities.findByName(""), -1 )
    assert_not_equal( cities.findByName("New York"), -1 )
    assert_equal( cities.getCityById( cities.findByName("New York") )[0], "New York" )
    assert_equal( cities.getCityById( cities.findByName("New York") )[0], "New York" )
    
    print( "DBG: findByName ret:", cities.findByName("New Yor", bPartOf = 1) )
    
    # find by name bPartOf return city sorted by habitants (pratique)
    assert_equal( cities.getCityAndStateNameById(cities.findByName("New Yor", bPartOf = 1)), "New York/New York" )
    assert_equal( cities.getCityAndStateNameById(cities.findByName("New", bPartOf = 1)), "New York/New York" )
    assert_equal( cities.getCityAndStateNameById(cities.findByName("N", bPartOf = 1)), "New York/New York" )
    assert_equal( cities.getCityAndStateNameById(cities.findByName("Qu", bPartOf = 1)), "Queens/New York" )
    assert_equal( cities.getCityAndStateNameById(cities.findByName("", bPartOf = 1)), "/" )
    
    print("Test: findByName adding CountyName")
    assert_equal( cities.findByName("New York","bad statename"), -1 )
    assert_equal( cities.findByName("New York","San Francisco"), -1 ) # another bad county name
    assert_equal( cities.getCityAndStateNameById( cities.findByName("New York","New York") ), "New York/New York" )
    assert_equal( cities.getCityAndCountyNameById( cities.findByName("New York","New York") ), "New York/Queens" )
    assert_equal( cities.getCityAndStateNameById( cities.findByName("San Francisco","California") ), "San Francisco/California" )
    assert_equal( cities.getCityAndCountyNameById( cities.findByName("San Francisco","California") ), "San Francisco/San Francisco" )
    assert_equal( cities.getCityAndStatePairById( cities.findByName("San Francisco","California") ), ("San Francisco","California") )
    assert_equal( cities.findByName("San Francisco","Caca"), -1 )
    assert_equal( cities.getCityAndStateNameById(cities.findByName("Huntsville")), "Huntsville/Alabama" )
    
    assert_equal( cities.getCityAndStatePairById(cities.findByName("Springfield")), ("Springfield","Massachusetts") ) # 439199 habitants (le plus grand)
    assert_equal( cities.getCityAndStatePairById(cities.findByName("Springfield", "Ohio")), ("Springfield","Ohio") ) # un plus petit
    assert_equal( cities.getCityAndStatePairById(cities.findByName("Springfield", "Wisconsin")), ("Springfield","Wisconsin") ) # le plus petit: 100h
    
    #~ assert_equal( cities.getCityById(cities.findByLongLat(-74.01380,40.70879)[0])[0], "New York" )
    assert_equal( cities.getCityById(cities.findByLongLat(-74.01380,40.70879)[0])[0], "Hoboken" ) # Un quartier précis de New York
    assert_equal( cities.getCityAndStateNameById(cities.findByLongLat(-74.01380,40.70879)[0]), "Hoboken/New Jersey" ) # Paris
    assert_equal( cities.getCityAndCountyNameById(cities.findByLongLat(-74.01380,40.70879)[0]), "Hoboken/Hudson" ) # Paris
    assert_equal( cities.getCityAndCountyNameById(cities.findByLongLat(-73.9,40.6943)[0]), "New York/Queens" ) # Paris
    assert_equal( cities.getCityAndCountyNameById(cities.findByLongLat(-122.41903,37.77500)[0]), "San Francisco/San Francisco" ) # Paris
    
    assert_diff( cities.distTwoCity( "New York","New York", "San Francisco","California" ), 4189.4 ) #~ 4768km a pied
    assert_diff( cities.distTwoCity( "New York","New York", "Hoboken","Caca" ), 999999 )
    assert_diff( cities.distTwoCity( "New York","New York", "Pipi" ), 999999 )
    assert_diff( cities.distTwoCity( "New York","New York", "Hoboken" ), 10.36 )
    assert_diff( cities.distTwoCity( "New York","New York", "Hoboken", "New Jersey" ), 10.36 )
    
    assert_equal( cities.isValidAdress( "10168", "New York" )[3], 1 )
    assert_equal( cities.isValidAdress( 10168, "New York" )[3], 1 )
    
    assert_equal( cities.isValidAdress( "75006", "New York" )[3], 0 )
    assert_equal( cities.isValidAdress( 75006, "New York" )[3], 0 )
    
    assert_equal( cities.isValidAdress( 90210, "Beverly Hills" )[3], 1 )
    assert_equal( cities.isValidAdress( 90210, "Beverly Hills", "Caca" )[3], 0 )
    assert_equal( cities.isValidAdress( 90210, "Beverly Hills", "California" )[3], 1 )
    
    assert_equal( cities.isValidAdress( 10168, "New York", "Queens" )[3], 0 )
    assert_equal( cities.isValidAdress( 10168, "New York", "Caca" )[3], 0 )
    
    print("Test: isValidAdress adding approximation")
    assert_diff( cities.isValidAdress( "10168", "Mew York" )[3], 0.875 )
    assert_diff( cities.isValidAdress( "10168", "Meu York" )[3], 0.75 )
    assert_diff( cities.isValidAdress( "10168", "Meu Yor" )[3], 0.571 )
    
    assert_diff( cities.isValidAdress( "10168", "Mew York", "New York" )[3], 0.9375 )
    assert_diff( cities.isValidAdress( "10168", "New York", "Mew York" )[3], 0.9375 )
    assert_diff( cities.isValidAdress( "10168", "Meu York", "Meu York" )[3], 0.75 )
    assert_diff( cities.isValidAdress( "10168", "Meu York", "Meu Yor" )[3], 0.666 )
    assert_diff( cities.isValidAdress( "10168", "New York", "Meu Y" )[3], 0.615 )
    assert_diff( cities.isValidAdress( "75006", "New York" )[3], 0 )

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
