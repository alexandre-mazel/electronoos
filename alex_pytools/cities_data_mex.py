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

"""
~ 13 675 codes postaux
~ 15 639 villes/localités
réparties dans 36 régions administratives
"""

"""
Format officiel:

Juan Pérez
Av. Insurgentes Sur 1234
Colonia Del Valle
03100 Ciudad de México
CDMX
México

eg:

Colonia Campestre
Churubusco, Coyoacán, 
CDMX 
=>
Ciudad de México / Ciudad de México


Nebraska 154 Col. Nápoles Alcaldía Benito Juárez, C.P. 03810
Celular 55 40 84 63 06
=>
Alcaldía Benito Juárez
03810 Ciudad de México
"""

"""
AA BBBB CCCC
AA → indicatif de zone (ville ou région)
BBBB CCCC → numéro local
Total : 10 chiffres

Ville	Indicatif
Ciudad de México	55
Guadalajara	33
Monterrey	81
Cancún	998
Tijuana	664

Les grandes villes ont 2 chiffres, les plus petites 3 chiffres.

Pas de prefixe particulier pour les mobiles. (donc spécifier en mode texte), eg: celular: xxx 

+52 Mexique
"""


import misctools # for levenshtein




# Le Mexique est divisé en estados [États], chaque État est ensuite divisé en municipios [similaires aux comtés aux États-Unis], 
# puis les municipios sont divisés en colonias [similaires aux quartiers aux États-Unis ou aux arrondissements au Royaume-Uni].
# Certains municipios ruraux ou historiquement ruraux peuvent être divisés en villes ou villages, puis chaque village divisé en barrios au lieu de colonias.
# State > County > Community

    
kCityName = 0 # version sans accent
kCityNameAscii = 1
kZip = 2
kStateName = 3
kStateID = 4
kCountyName = 5 # municipios
kCommunityName = 7 # colonia, petit quartier
kLong = 9
kLat = 10


def removeAccentSpecificLang( s, strSpecificLang = "ES" ):
    dic_conv = { 
            "Á": "A",
            "á": "a",
            "à": "a",
            "É": "E",
            "é": "e",
            "è": "e",
            "Í": "I",
            "í": "i",
            "Ñ": "N",
            "ñ": "n",
            "Ó": "O",
            "ó": "o",
            "Ú": "U",
            "ù": "u",
            "ú": "u",
            "Ü": "U",
            "ü": "u",
    }
    out = []
    for c in s:
        try:
            newc = dic_conv[c]
        except KeyError:
            newc = c
        out += newc
    out = "".join(out)
    #~ print( "DBG: removeAccentSpecificLang: '%s' => '%s'" % (s,out) )
    return out
    
# indicatifs_mexique_complet.py

phone_indicatif_mexique = {
    "55": ["Ciudad de México", "Ciudad de México"],       # capitale 🇲🇽 :contentReference[oaicite:1]{index=1}
    "56": ["Ciudad de México", "Ciudad de México"],       # overlay pour Mexico City :contentReference[oaicite:2]{index=2}
    "33": ["Guadalajara", "Jalisco"],                     # :contentReference[oaicite:3]{index=3}
    "81": ["Monterrey", "Nuevo León"],                    # :contentReference[oaicite:4]{index=4}
    "222": ["Puebla", "Puebla"],                          # :contentReference[oaicite:5]{index=5}
    "664": ["Tijuana", "Baja California"],                # :contentReference[oaicite:6]{index=6}
    "998": ["Cancún", "Quintana Roo"],                    # :contentReference[oaicite:7]{index=7}
    "999": ["Mérida", "Yucatán"],                         # :contentReference[oaicite:8]{index=8}
    "449": ["Aguascalientes", "Aguascalientes"],           # :contentReference[oaicite:9]{index=9}
    "477": ["León", "Guanajuato"],                        # :contentReference[oaicite:10]{index=10}
    "442": ["Querétaro", "Querétaro"],                    # :contentReference[oaicite:11]{index=11}
    "744": ["Acapulco", "Guerrero"],                      # :contentReference[oaicite:12]{index=12}
    "614": ["Chihuahua", "Chihuahua"],                    # :contentReference[oaicite:13]{index=13}
    "656": ["Ciudad Juárez", "Chihuahua"],                # :contentReference[oaicite:14]{index=14}
    "662": ["Hermosillo", "Sonora"],                      # :contentReference[oaicite:15]{index=15}
    "686": ["Mexicali", "Baja California"],               # :contentReference[oaicite:16]{index=16}
    "229": ["Veracruz", "Veracruz"],                      # :contentReference[oaicite:17]{index=17}
    "322": ["Puerto Vallarta", "Jalisco"],                # :contentReference[oaicite:18]{index=18}
    "444": ["San Luis Potosí", "San Luis Potosí"],        # :contentReference[oaicite:19]{index=19}
    "844": ["Saltillo", "Coahuila"],                      # :contentReference[oaicite:20]{index=20}
    "899": ["Reynosa", "Tamaulipas"],                     # :contentReference[oaicite:21]{index=21}
    "433": ["Morelia", "Michoacán"],                      # :contentReference[oaicite:22]{index=22}
    "624": ["Cabo San Lucas", "Baja California Sur"],     # :contentReference[oaicite:23]{index=23}
    "951": ["Oaxaca de Juárez", "Oaxaca"],                # :contentReference[oaicite:24]{index=24}
    "961": ["Tuxtla Gutiérrez", "Chiapas"],               # :contentReference[oaicite:25]{index=25}
    "871": ["Torreón", "Coahuila"],                       # :contentReference[oaicite:26]{index=26}
    "861": ["Progreso", "Yucatán"],
    "646": ["Ensenada","Baja California"],
    "667": ["Culiacán","Sinaloa"],
    "462": ["Irapuato","Guanajuato"],
    "443": ["Morelia","Michoacán"],
    "833": ["Tampico","Tamaulipas"],
    "993": ["Villahermosa","Tabasco"],
    "984": ["Playa del Carmen","Quintana Roo"],
    "815": ["Toluca","Estado de México"],
    "932": ["Jalapa","Veracruz"],
    "777": ["Cuernavaca","Morelos"],
    "938": ["Ciudad del Carmen","Campeche"],
}

if 0:
    # fusion de 2 dicos
    for k,v in indicatifs_mexique.items():
        if not k in phone_indicatif_mexique:
            print('"%s":["%s","%s"]' % (k,v[0],v[1]) )
        else:
            assert(v == phone_indicatif_mexique[k] )
    exit(1)
    
def getCityAndStateFromPhoneIndicatif( indi ):
    indi = str(indi)
    try:
        return phone_indicatif_mexique[indi]
    except KeyError as err:
        pass
    return None

class CitiesMex:
    """
    Uses:
    1: Autocomplete, eg on a website: enter start of city, it completes with "full name (zip)"
        findByRealName( city, bPartOf = True )
         
    2: Adress detection: give a zip and a city, it will validate it's really an adress, and can correct it.
        isValidAddress( zip, city ), return (zip,city,confidence) confidence of the right correction.
         
    3: Distance between two city: give two zip, it returns the distance
        distTwoZips( zip1, zip2 )
        
    NB: Cities are sorted by population, so all research with many answers will return the biggest city
    """
    
    def __init__(self):
        self.dictCities = {} # id => (city_ascii (sans accent), city avec accent, state_id, state_name,county_fips, county_name,float(strLong),float(strLat),population, density, ranking?,list_of_zips)
        self.dictIdsPerZip = {} # zip as a string => (id1, id2, ...)
        self.dictIdsPerCityName = {} # cityname without accent as a string => (id1, id2, ...)
        #~ self.dupCityPerZip = {} # some cities have same zip, so we store for each overwritten city slug their zip
        #~ self.dupZipPerZip = {} # some zip are for the same cities, we store them here alternateZip => Zip
        #~ self.cacheLastFindByRealName = (None,None,None) # city, partof, result of last research
       
        self.warnMessages = [] # handle warn messages, not overflowing the output

    def load(self):
        bVerbose = 1
        bVerbose = 0
        
        print("INF: CitiesMex: loading city data...")
        timeBegin = time.time()
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
        if strLocalPath == "": strLocalPath = '.'
        
        #     sep="\t",  header=None,  names=[  "country_code",  "postal_code",  "city", "state", "state_code", "province", "province_code", "community",  "community_code", "latitude", "longitude", "accuracy"
        strFilename = strLocalPath + '/datas/mexican_cities.csv'
        enc = 'utf-8'
        file = cities_data.openWithEncoding(strFilename, "rt", encoding = enc)
        line = file.readline() # skip first line
        self.dictCities = {}
        nDuplicateZip = 0
        nDuplicateCityName = 0
        #~ nTotalPopulation = 0
        #~ nNbrCityMore100k = 0
        #~ nNbrCityMore100kCalifornia = 0
        id = 1
        while 1:
            line = file.readline()
            if len(line)<1:
                break
            if bVerbose: print(line)
            line = line.replace('"','')
            fields = line.split('\t')
            if bVerbose: print("fields (%d): %s" % (len(fields), str(fields)) )
            strCountryCode, strZip, strCity, strCommunity, strCommunityID, strCountyName, strCountyID, strStateName, strStateId,  strLat, strLong, strAccuracy = fields
            
            if bVerbose  or "Cavario" in strCity or "52213" in strZip: print("%d: strCity: %s, strStateId: %s, strStateName: %s, strCountyName: %s, strCommunity: %s" % (id, strCity,strStateId,strStateName,strCountyName, strCommunity) ) 
                
            strAccuracy = strAccuracy.strip() # remove EOL
            
            if strStateName == "" and strStateId == "":
                # qd pas de community (ou de county) ca décale tout.
                    strStateName = strCommunity
                    strStateId = strCommunityID
                    
                    # 2 choix a décider selon les locaux!
                    if 0:
                        strCountyName = strCommunity
                        strCountyID = strCommunityID
                        strCommunity = ""
                        strCommunityID = -1
                    elif 0:
                        strCommunity = strCountyName
                        strCommunityID = strCountyID    
                        strCountyName = ""
                        strCountyID = -1
                    else:
                        strCommunity = ""
                        strCommunityID = -1
                        
                        
                        
            strCityAscii = removeAccentSpecificLang( strCity )
            self.dictCities[id] = ( strCity, strCityAscii, strZip, strStateName, strStateId, strCountyName, strCountyID, strCommunity, strCommunityID, float(strLong), float(strLat) )

            if not strZip in self.dictIdsPerZip:
                self.dictIdsPerZip[strZip] = []
            else:
                if bVerbose: print( "WRN: Duplicate id for the same zips: id %s and %s" % (id, self.dictIdsPerZip[strZip][0]) )
                nDuplicateZip += 1
            self.dictIdsPerZip[strZip].append( id )
                
            if not strCityAscii in self.dictIdsPerCityName:
                    self.dictIdsPerCityName[strCityAscii] = []
            else:
                first_id = self.dictIdsPerCityName[strCityAscii][0]
                if bVerbose: print( "WRN: %s/%s have same cityname than %s/%s" % (strCity,strStateName,self.dictCities[first_id][kCityName],self.dictCities[first_id][kCountyName]) )
                nDuplicateCityName += 1

            self.dictIdsPerCityName[strCityAscii].append( id )
            
            id += 1

            if id > 10 and 0:
                break
            
        # while each line - end
        
        # official stats: Over xx cities and towns from all xx states
        
        print( "" )
        print( "INF: %d loaded cities" % len(self.dictCities)  ) # should be 144654
        print( "WRN: %d duplicated zip found" % nDuplicateZip ) # 112207 !
        print( "WRN: %d duplicated cityname found" % nDuplicateCityName ) # 64914! (la moitié !?!)
        
        assert( len(self.dictCities) == 144654 )

        
        # manual addings:
        print( "INF: Manual Addings..." )
        
        listCitiesToAdd = [
            # zip, cityname, State,  County,  Community, strLong, strLat
            # officiellement c'est 01000, mais d'apres wikipedia, c'est 00–16 !!!
            ["01000", self.getCapitalName(), "Ciudad de México", "Ciudad de México", "Ciudad de México","-99.133208","19.432608"]
        ]
        
        for c in listCitiesToAdd:
            strZip, strCity,  strStateName, strCountyName, strCommunityName, strLong, strLat = c
            strCityAscii = removeAccentSpecificLang(strCity)
            strStateId = -1
            strCountyID = -1
            strCommunityId = -1
            self.dictCities[id] = ( strCity, strCityAscii, strZip, strStateName, strStateId, strCountyName, strCountyID, strCommunity, strCommunityID, float(strLong), float(strLat) )

            if not strZip in self.dictIdsPerZip:
                self.dictIdsPerZip[strZip] = []
            else:
                print( "WRN: Duplicate id for the same zips: id %s and %s" % (id, self.dictIdsPerZip[strZip][0]) )
                nDuplicateZip += 1
            self.dictIdsPerZip[strZip].insert( 0, id ) # CDMX a la prio
                
            if not strCityAscii in self.dictIdsPerCityName:
                    self.dictIdsPerCityName[strCityAscii] = []
            else:
                first_id = self.dictIdsPerCityName[strCityAscii][0]
                if bVerbose: print( "WRN: %s/%s have same cityname than %s/%s" % (strCity,strStateName,self.dictCities[first_id][kCityName],self.dictCities[first_id][kCountyName]) )
                nDuplicateCityName += 1

            self.dictIdsPerCityName[strCityAscii].append( id )
            id += 1
          
                
        print("INF: CitiesUs: loading city data - end duration: %.2fs" % (time.time()-timeBegin) )
        
        #~ self.computeStats()
    # load - end
    
    def getCapitalName( self ):
        return "Mexico City (CDMX)"
    
    def computeStats( self ):
        lenCity = 0
        nbrCity = 0
        lenState = 0
        nbrState = 0
        for k,v in self.dictCities.items():
            c = v[kCityName]
            if c != "":
                lenCity += len(c.split( " " ))
                nbrCity += 1
            c = v[kStateName]
            if c != "":
                lenState += len(c.split( " " ))
                nbrState += 1      

        print( "nbr city: %d" % len( self.dictCities ) )
        print( "nbr city not empty: %d" % nbrCity )
        print( "avg city not empty: %.2f" % (lenCity/nbrCity) ) # 2.41
        print( "nbr state not empty: %d" % nbrState )
        print( "avg state not empty: %.2f" % (lenState/nbrState) ) # 1.81
        
    
    def warn(self,msg):
        if msg in self.warnMessages:
            return
        self.warnMessages.append(msg)
        print(msg)
        
    def getCityById( self, id ):
        try:
            return self.dictCities[id]
        except KeyError:
            print("WRN: CitiesMex.getCityById: city with id: '%s' not found..." % id )
            pass
        return None
        
    def getCityAndStateNameById( self, id ):
        try:
            return self.dictCities[id][kCityName] + "/" + self.dictCities[id][kStateName]
        except KeyError:
            print("WRN: CitiesMex.getCityAndStateNameById: city with id: '%s' not found..." % id )
            pass
        return "/"

    def getCityAndStatePairById( self, id ):
        try:
            return self.dictCities[id][kCityName], self.dictCities[id][kStateName]
        except KeyError:
            print("WRN: CitiesMex.getCityAndStatePairById: city with id: '%s' not found..." % id )
            pass
        return ("","")
        
    def getCityAndCountyNameById( self, id ):
        try:
            return self.dictCities[id][kCityName] + "/" + self.dictCities[id][kCountyName]
        except KeyError:
            print("WRN: CitiesMex.getCityAndCountyNameById: city with id: '%s' not found..." % id )
            pass
        return "/"

    def getIdByZip( self, zip ):
        """
        return if of a city or -1 if not nound
        """
        if zip == None:
            print("WRN: CitiesMex.getIdByZip: called with None => returning -1" )
            return -1
            
        if isinstance(zip, int):
            zip = "%05d" % zip
            
        try:
            id = self.dictIdsPerZip[zip][0]
        except KeyError:
            return -1
            
        return id
        
    def findByZip( self, zip, bQuiet = True ):
        """
        return info on a city or None if not nound
        """
        id = self.getIdByZip( zip )
        if id == -1:
            print("WRN: CitiesMex.findByZip: zip '%s' not found" % zip )
            return None
            
        return self.dictCities[id]
            

    def findByName( self, strCityName, strStateName = None, bPartOf=False, bVerbose = 0 ):
        """
        return id related to a cityname. (cityname with or without accent) or -1 if not found
        WRN: If strStateName is bad and bPartOf is False, it will return -1 even if city exists
        """
        
        if strCityName == "":
            return -1
           
    
        strCityNameCapital = "Mexico City (CDMX)"
        if strCityName in ["Mexico City", "CDMX", "Mexico"]:
            strCityName = strCityNameCapital
            
            
        #~ if self.cacheLastFindByRealName[0] == strCityName and self.cacheLastFindByRealName[1] == bPartOf:
            #~ return self.cacheLastFindByRealName[2]
            
            
        strCityName = removeAccentSpecificLang( strCityName )
        if strStateName != None:
            strStateName = removeAccentSpecificLang( strStateName )
            
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
                self.warn("WRN: CitiesMex.findByName: this city name has different ids: %s" % (listIds) )
                id = listIds[0]
            else:
                for id in listIds:
                    if bVerbose: print( "DBG: CitiesMex.findByName try to match state '%s' and '%s'" % (strStateName,self.dictCities[id][kStateName]) ) 
                    if removeAccentSpecificLang(self.dictCities[id][kStateName]) == strStateName or self.dictCities[id][kStateID]== strStateName:
                        return id
                self.warn("WRN: CitiesMex.findByName: this city name '%s', exist but not with this statename/stateid: '%s' (1)" % (strCityName,strStateName) )
                return -1
        else:
            id = listIds[0]
            if not bPartOf and strStateName != None and removeAccentSpecificLang(self.dictCities[id][kStateName]) != strStateName and self.dictCities[id][kStateID] != strStateName:
                self.warn("WRN: CitiesMex.findByName: this city name '%s' exist but not with this statename/stateid: '%s' (2)" % (strCityName,strStateName) )
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
            
        
    def findByCityStateOrCommunity( self, name ):
        """
        return city id and number of field matching the name
        or if not found -1, -1
        """
        if name == "":
            return -1,-1
            
        name = removeAccentSpecificLang(name).lower()
        for id,data in self.dictCities.items():
            for num_field in [kCityName, kStateName, kCountyName, kCommunityName]:
                if name == removeAccentSpecificLang(data[num_field]).lower():
                    return id, num_field
        return -1, -1
        
        
    def isValidAddress( self, zip, strCityName, strStateName = None ):
        """
        is this zip correspond roughly to this city.
        return zip, real name, state name, confidence [0..1]
        or None,None, None, 0
        
        Work on unaccentuated string
        """
        retValNone = None,None,None, 0.
        
        if isinstance(zip, int):
            zip = "%05d" % zip
            
        try:
            ids = self.dictIdsPerZip[zip]
        except KeyError:
            return retValNone
            
        # patch cdmx
        if zip == "01000":
            if( strCityName == "CDMX" or strCityName == "Mexico City" ):
                strCityName = self.getCapitalName()
            
        strCityName = removeAccentSpecificLang( strCityName )
        if strStateName != None:
            strStateName = removeAccentSpecificLang( strStateName )
        
        for id in ids:
            city = self.dictCities[id]
            if strCityName == city[kCityNameAscii] and ( strStateName == None or strStateName == removeAccentSpecificLang(city[kStateName]) or strStateName == city[kStateID] ):
                return zip, city[kCityName], city[kStateName], 1
                
        # else recherche approximative, au plus proche
        dist_min = 999999
        id_min = -1
        for id in ids:
            city = self.dictCities[id]
            print( "DBG: isValidAddress: comparing '%s' and '%s'" % (strCityName,city[kCityNameAscii]) )
            dist = misctools.levenshtein( strCityName, city[kCityNameAscii] )
            if strStateName != None:
                dist += misctools.levenshtein( strStateName, removeAccentSpecificLang(city[kStateName]) )
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
        
        
    def distTwoCities( self, city1, county1, city2, county2 = None, bApproxSearch=True, bVerbose=False ):
        id1 = self.findByName( city1, county1 )
        id2 = self.findByName( city2, county2 )
        return self.distTwoIds( id1, id2 )
        
    def distTwoZips( self, zip1, zip2, bApproxSearch=True, bVerbose=False ):
        id1 = self.getIdByZip( zip1 )
        id2 = self.getIdByZip( zip2 )
        #~ print("id1: '%s'" % id1 )
        #~ print("id2: '%s'" % id2 )
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
        
        
    def extractAddress( self, txt ):
        print( "DBG: extractAddress: extracting from text: " + txt )
        for li in txt.split("\n"):
            splitted = li.split(",")
            city =splitted[0].strip()
            state = None
            if len(splitted) > 1:
                splitted = splitted[1].split( " " )
                idx = 0
                if len(splitted[0]) < 2 and len(splitted) > 1:
                    idx = 1
                state = splitted[idx].strip()
            id = self.findByName( city, state )
            if id != -1:
                return id
        return -1
        
        
    def getFormatedCity( self, city, bLeaveAccent = True ):
        if bLeaveAccent: 
            txt = city[kZip] + " " + city[kCityName] + ", " + city[kStateName]
            return txt
        txt = city[kZip] + " " + city[kCityNameAscii] + ", " + removeAccentSpecificLang( city[kStateName] )
        return txt       
        
        
    def zipToHumanised( self, zip ):
        city = self.findByZip( zip )
        if city == None:
            print("WRN: zipToHumanised city is None for zip '%s'" % zip )
            return ""
        strCity = city[3]
        
        strOut = "en " + city[kCityName]
        return strOut
        
    def idToZip( self, id ):
        """
        take the id of a city and return the first zip
        """
        return self.getCityById( id )[kZip]
        
#class CitiesMex - end

def generate_js_cities_list(destination_filename):
    """
    will generate a big js list, like that with each city, zip, long, lat
    to the given filename
    citiesAndDatas=[['Ozan', '01190', 4.91667, 46.3833],['Cormoranche-sur-Sa&ocirc;ne', '01290', 4.83333, 46.2333]
    """
    print( "INF: generate_js_cities_list to filename '%s'" % destination_filename )
    out = ""
    out += "// automatically generated using script '%s'\n" % ( sys.modules[__name__].__file__ )
    
    cities = CitiesMex()
    cities.load()
    
    out += "// it contains %d cities\n" % len(cities.dictCities)
    
    out += "citiesAndDatas_MEX=["
    for k,data in cities.dictCities.items():
        cityname = data[kCityName]
        #~ if "\"" in cityname:
            #~ print("outch")
        out += '["%s","%s",%.4f,%.4f],' % (cityname,data[kZip],data[kLong],data[kLat])
    out = out[:-1] # remove last comma
    out += "];"
    
    f = open(destination_filename,"wt", encoding = "utf-8")
    f.write(out)
    f.close()
    
    print( "INF: generate_js_cities_list to filename '%s' - done" % destination_filename )
# generate_js_cities_list - end
    




def autotest_cities():
    cities = CitiesMex()
    cities.load()
    #  mstab7_2.7 : 
    #  mstab7_3.9 : 1.22
    # RPI4_2.7      : 
    # RPI4_3.7      : 
    # Azure             : 1.21
    
    assert_equal( cities.findByZip("666"), None )
    assert_not_equal( cities.findByZip("11220"), None )
    assert_not_equal( cities.findByZip("06700"), None )
    
    assert_equal( cities.getFormatedCity( cities.findByZip("06700") ), "06700 Roma Norte, Ciudad de México" )
    assert_equal( cities.getFormatedCity( cities.findByZip("06700"), False ), "06700 Roma Norte, Ciudad de Mexico" )
    
    assert_equal( cities.findByZip("06700")[kCityName], "Roma Norte" )
    assert_equal( cities.findByZip("06700")[kStateName], "Ciudad de México" )
    assert_equal( cities.findByZip("06700")[kCountyName], "Cuauhtémoc" )
    assert_equal( cities.findByZip("06700")[kCommunityName], "Distrito Federal" )
    
    assert_equal( cities.findByZip("01000")[kCityName], "Mexico City (CDMX)" )
    
    # San Diego la Huerta es una localidad del Estado de México, México. Es parte del municipio de Calimaya. # https://es.wikipedia.org/wiki/San_Diego_la_Huerta
    assert_equal( cities.findByZip("52213")[kCityName], "El Calvario" )  # or San Diego la Huerta
    assert_equal( cities.findByZip("52213")[kStateName], "México" )
    assert_equal( cities.findByZip("52213")[kCountyName], "Calimaya" )
    assert_equal( cities.findByZip("52213")[kCommunityName], "" )
    
    assert_equal( cities.findByZip("35816")[kCityName], "Providencia" )
    assert_equal( cities.findByZip("35816")[kStateName], "Durango" )
    assert_equal( cities.findByZip("35816")[kCountyName], "Cuencamé" )
    assert_equal( cities.findByZip("35816")[kCommunityName], "" )

    
    assert_equal( cities.findByName(""), -1 )
    assert_equal( cities.findByName("New York"), -1 )
    assert_equal( cities.getCityById( cities.findByName("Delegación Política Cuauhtémoc"))[kCityName], "Delegación Política Cuauhtémoc" )
    assert_equal( cities.getCityById( cities.findByName("Delegacion Politica Cuauhtemoc"))[kCityName], "Delegación Política Cuauhtémoc" )
    assert_equal( cities.getCityById( cities.findByName("Mexico City"))[kCityName], "Mexico City (CDMX)" )
    assert_equal( cities.getCityById( cities.findByName("CDMX"))[kCityName], "Mexico City (CDMX)" )
    assert_equal( cities.getCityById( cities.findByName("Mexico City (CDMX)"))[kCityName], "Mexico City (CDMX)" )
    assert_equal( cities.getCityById( cities.findByName("Mexico City", "Ciudad de México"))[kCityName], "Mexico City (CDMX)" )
    assert_equal( cities.getCityById( cities.findByName("Mexico City (CDMX)", "Ciudad de México"))[kCityName], "Mexico City (CDMX)" )
    
    assert_equal( cities.getCityById( cities.findByName("El Calvario") )[kCityName], "El Calvario" )
    
    assert_equal( cities.getCityAndStateNameById( cities.findByName("El Calvario", "Durango") ), "El Calvario/Durango" )
    
    print( "DBG: findByName ret:", cities.findByName("New Yor", bPartOf = 1) )
    
    # find by name bPartOf return city sorted by habitants (pratique)
    assert_equal( cities.getCityAndStateNameById(cities.findByName("El Calvari", bPartOf = 1)), "El Calvario/Jesús María" )
    
    print("Test: findByName adding CountyName")
    assert_equal( cities.findByName("El Calvari","bad statename"), -1 )

    #~ assert_equal( cities.getCityById(cities.findByLongLat(-74.01380,40.70879)[0])[0], "New York" )
    assert_equal( cities.getCityAndStateNameById(cities.findByLongLat(-108.0114,25.5775)[0]), "Alhueycito/Sinaloa" )
    assert_diff( cities.distTwoCities( "Alhueycito","Sinaloa", "Roma Norte", "Ciudad de México" ), 1137.35 )#~ 1572km a pied
    assert_diff( cities.distTwoCities( "Alhueycito","Sinaloa", "Roma Norte" ), 1137.35 )#~ 1572km a pied
    assert_diff( cities.distTwoCities( "CDMX", "Ciudad de México", "Roma Norte" ), 3.55 ) # c'est a coté
    
    assert_diff( cities.distTwoCities( "New York","New York", "Hoboken","Caca" ), 999999 )
    
    assert_diff( cities.distTwoZips( "06700", "06357" ), 3.33 ) # Roma Norte & Delegación Política Cuauhtémoc, theoric: 3.44km (distance calculator)
    
    print("Test: isValidAddress block")
    assert_equal( cities.isValidAddress( "06700", "Roma Norte" )[3], 1 )
    assert_equal( cities.isValidAddress( "06700", "Mora Norte" )[3], 0.8 )
    assert_equal( cities.isValidAddress( "06701", "Roma Norte" )[3], 0 )
    assert_equal( cities.isValidAddress( "01000", "CDMX" )[3], 1 )
    assert_equal( cities.isValidAddress( "01000", "Mexico City" )[3], 1 )
    assert_equal( cities.isValidAddress( "01000", "Mexico City (CDMX)" )[3], 1 )
    
    assert_equal( cities.isValidAddress( "06357", "Delegación Política Cuauhtémoc" )[3], 1 )
    assert_diff( cities.isValidAddress( "06357", "Delegacion Politica Cuauhtemoc" )[3], 1 )
    assert_diff( cities.isValidAddress( "06357", "Delegación Política Cuauhtémo" )[3], 0.965 )
    assert_diff( cities.isValidAddress( "06357", "Delegación Política Cuauht" )[3], 0.846 )
    
    assert_equal( getCityAndStateFromPhoneIndicatif( "421" ), None )
    assert_equal( getCityAndStateFromPhoneIndicatif( "646" ), ['Ensenada', 'Baja California'] )
    assert_equal( getCityAndStateFromPhoneIndicatif( 646 ), ['Ensenada', 'Baja California'] )
    
    assert_equal( cities.findByCityStateOrCommunity( "Baja California" )[1], kStateName )
    assert_equal( cities.findByCityStateOrCommunity( "Ensenada" )[1], kCountyName ) # c'est aussi une county
    assert_equal( cities.findByCityStateOrCommunity( "Roma Norte" )[1], kCityName )
    assert_equal( cities.findByCityStateOrCommunity( "Baja California Sur" )[1], kCommunityName )
    # cherche d'une communauté qui fonctionne:
    #~ for k,v in cities.dictCities.items():
        #~ if cities.findByCityStateOrCommunity( v[kCommunityName] )[1] == kCommunityName:
            #~ print("kCommunityName: '%s'" % v[kCommunityName] )
            #~ exit(1)
    
# autotest_cities - end
    
if __name__ == "__main__":
    if 1:
        autotest_cities()
        #~ autotest_region()
        print("INF: CitiesMex.autotest passed [GOOD]")
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
        statByRegion( bOutputHtml = bOutputHtml )

        
    if 1:
        generate_js_cities_list( "datas/eng_city_mex_datas.js")