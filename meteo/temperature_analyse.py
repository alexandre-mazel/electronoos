# analyse temperature file (from meteo website)

# scp -P 14092 na@thenardier.fr:/home/na/save/temperature.txt C:/Users/alexa/dev/git/electronoos/meteo/data/

import sys

sys.path.append("../../obo/spider/")

import common
import retrieve_pop3

class HelperStat:
    """
    class to help computing stat
    """
    def __init__( self ):
        self.minNight = 999 # min of the night of the current analysed day
        self.maxDay = -999
        
        self.strPrevDay = ""
        
        self.bStatBreakfastDone = False # helper to know if we analyse the measure as been made for breakfast
        
        self.bStatLunchDone = False
        
        self.bStatDinnerDone = False
        
        self.bStatWetDayDone = False
        self.bStatWetNightDone = False

class Stat:
    def __init__( self ):
        self.nbrMeasures = 0
        self.sumTemperature = 0
        
        self.nbrDay = 0
        self.min = 999
        self.max = -40
        
        self.nbrBreakfast = 0 # nbr breakfast  at 8.30 >= 15 and no rain breakfast
        
        self.nbrLunch = 0 # nbr lunch at 13 >= 20
        
        self.nbrDinner = 0 # nbr dinner at 19.30 >= 20
        
        self.nbrHotDay = 0 # nbr max > 33, 32 is unconfortable, if it raise to 34 it means a lot of hour are > 32
        
        self.nbrHotNight = 0 # nbr min night >= 20
        self.nbrColdNight = 0 # nbr min night < 13
        self.nbrWetDay = 0 # day with more than 15min of rain # day is >= 8 and < 22
        self.nbrWetNight = 0 # night with more than 15min of rain
        
        self.score = 0 # nbr points for this location
        self.score_bonus = 0 # detail of bonus
        self.score_malus = 0 # detail of malus
        
    def __str__(self):
        o  = ""
        #~ o += " min: %s, max: %s, hotnight: %s" % (self.min,self.max,self.nbrHotNight)
        o += "  nbr measures: %s\n" % self.nbrMeasures
        o += "  nbr day: %s\n" % self.nbrDay
        o += "  min: %s\n" % self.min
        o += "  med: %.1f\n" % (self.sumTemperature/self.nbrMeasures)
        o += "  max: %s\n" % self.max
        o += "  breakfast: %s\n" % self.nbrBreakfast
        o += "  lunch: %s\n" % self.nbrLunch
        o += "  dinner: %s\n" % self.nbrDinner
        o += "  hot day: %s\n" % self.nbrHotDay
        o += "  hot night: %s\n" % self.nbrHotNight
        o += "  cold night: %s\n" % self.nbrColdNight
        o += "  wet day: %s\n" % self.nbrWetDay
        o += "  wet night: %s\n" % self.nbrWetNight
        o += "  score: %s (%s,%s)\n" % (self.score,self.score_bonus,self.score_malus)
        return o
        
def isListIn(word,list):
    """
    is a member of list in word
    """
    for w in list:
        if w in word:
            return True
    return False

def analyse(strFilename):
    """
    Compute best place to live AND
    return a list of dictionnary of values, eg: ("location","temperature") => list of values = [year, month,day, hour, min, value]
    """
    bVerbose = 1
    #~ bVerbose = 0
    
    f = open(strFilename,"rb")
    occCity = common.OccCounter()
    occWeather = common.OccCounter()
    
    dicoHelper = {} # city => HelperStat
    
    dicoStat = {} # dico per city and month => stat
    
    strStartDate = ""
    strStopDate = ""
    
    dict_out = {} # the dict to return

    
    nNumLine = 0
    while 1:
        line = f.readline()
        if len(line)<2:
            break
        datas = retrieve_pop3.splitBytes(line,ord(":"))
        
        if bVerbose: print(datas)
        
        for i in range(len(datas)):
            datas[i] = datas[i].strip()
        
        strDate, strTime, strCity, strTemp = datas[:4]
        strDate = strDate.decode()
        strTime = strTime.decode()
        strCity = strCity.decode()
        strYear = strDate[0:4]
        strMonth = strDate[5:7]
        strDay = strDate[8:10]
        strHour = strTime[0:2]
        nHour = int(strHour)
        strMin =  strTime[3:4]
        nMin = int(strMin)
        
        if strYear == "\x00\x00\x00\x00'":
            print("ERR: year is zeroed")
            continue

        if bVerbose: print("nHour: %s" % nHour)
        
        nTemp = int(strTemp)
        
        bNight = nHour >= 22 or nHour <= 7
        bDay = not bNight
        
        if strStartDate == "":
            strStartDate = strDate
        strStopDate = strDate
        
        # analyse conditions
        strWeather = "?"
        bRain = 0
        bSnow = 0
        bSun = 0
        nCondition = -1 # etat du plus au moins sympa, -1: unknown, 1: pluie, 2: neige, 3: nuage, 4: soleil
        if len(datas)>4:
            strWeather = datas[4].decode()
            strWeatherLo = strWeather.lower()
            
            if bVerbose: print( "DBG: strWeatherLo: '%s'" % strWeatherLo )
            
            nCondition = 3
            
            if isListIn(strWeatherLo, ["pluie", "averse", "bruine", "orage", "cipitation"] ):
                bRain = True
                nCondition = 1
            if isListIn(strWeatherLo, ["neige"] ):
                bSnow = True
                nCondition = 2
            if isListIn(strWeatherLo, ["soleil","beau","ciel degage"] ):
                bSun = True
                nCondition = 4
                
            if bVerbose: 
                if not bRain and not bSnow and not bSun:
                    print( "DBG: check it is nuage: '%s'" % strWeatherLo )

        bRainOrSnow = bRain or bSnow
        occWeather.add(strWeather)


                
        if "Beziers" in strCity:
            if bVerbose: print(datas)
        
        
        if bVerbose: print("bNight: %s" % bNight)
        
        # prepare data to be outtputed
        dataToPost = ( int(strYear), int(strMonth), int( strDay) , nHour, nMin)
        for namevalue,value in ( ("temp",nTemp), ("condition", nCondition) ):
            key = (strCity,namevalue)
            if not key in dict_out:
                dict_out[key] = []
            dict_out[key].append( dataToPost + (value,) )

            
            
        bNewDay = 0 # new matinee
        
        key = strCity + "__" + strYear + "/" + strMonth

        if strCity not in dicoHelper:
            if bVerbose: print("create new helper was not")
            dicoHelper[strCity] = HelperStat()
                
        if nHour >= 8 and dicoHelper[strCity].strPrevDay != strDate:
            if bVerbose: print("new day")
            bNewDay = 1
            
            # affiche les infos sur une ville particuliere
                                 
            if "Beziers" in strCity and 0:
                # ne fontionne pas!
                if strCity in dicoHelper and dicoHelper[strCity].minNight < 999:
                    print("Beziers %s: %s" % (dicoHelper[strCity].strPrevDay, dicoStat[key]) )
            

            dicoHelper[strCity].strPrevDay = strDate
            
            # update stat of the night (warning we can start with a hour at 22, and so updating previous night)

            if strCity in dicoHelper and dicoHelper[strCity].minNight < 999:
                if bVerbose: print("minnight: %s" % dicoHelper[strCity].minNight)
                if  dicoHelper[strCity].minNight >= 20:
                    dicoStat[key].nbrHotNight += 1
                if dicoHelper[strCity].minNight < 13:
                    dicoStat[key].nbrColdNight += 1

            if strCity in dicoHelper and dicoHelper[strCity].maxDay > -999:
                if bVerbose: print("maxday: %s" % dicoHelper[strCity].maxDay)
                if  dicoHelper[strCity].maxDay > 33:
                    if bVerbose: print("hot day!")
                    dicoStat[key].nbrHotDay+= 1
        
        
        occCity.add(strCity)
        
        strDetail = ""
        if len(datas)>4:
            strDetail = datas[4]
            
        if not strCity in dicoHelper or bNewDay:
            if bVerbose: print("create new helper")
            dicoHelper[strCity] = HelperStat()
            dicoHelper[strCity].strPrevDay = strDate
            
            
        #~ print(key)
        if not key in dicoStat:
            dicoStat[key] = Stat()
            
            
        if bNewDay:
            dicoStat[key].nbrDay += 1
            
                
        if bNight:
            if bVerbose: print("min night: %s" % dicoHelper[strCity].minNight)
            if dicoHelper[strCity].minNight > nTemp:
                dicoHelper[strCity].minNight = nTemp
                
        if bDay:
            if dicoHelper[strCity].maxDay < nTemp:
                dicoHelper[strCity].maxDay = nTemp
            
            
        dicoStat[key].nbrMeasures += 1
        dicoStat[key].sumTemperature += nTemp
        
        if dicoStat[key].min > nTemp:
           dicoStat[key].min = nTemp

        if dicoStat[key].max < nTemp:
           dicoStat[key].max = nTemp
           
           
        if not dicoHelper[strCity].bStatBreakfastDone:
            if nHour >= 8 and nHour < 9 and nTemp >= 15 and not bRainOrSnow:
                dicoHelper[strCity].bStatBreakfastDone = 1
                dicoStat[key].nbrBreakfast += 1
                
        if not dicoHelper[strCity].bStatLunchDone:
            if nHour >= 13 and nHour < 14 and nTemp >= 20 and not bRainOrSnow:
                dicoHelper[strCity].bStatLunchDone = 1
                dicoStat[key].nbrLunch += 1
                
        if not dicoHelper[strCity].bStatDinnerDone:
            if nHour >= 19 and nHour < 20 and nTemp >= 20 and not bRainOrSnow:
                dicoHelper[strCity].bStatDinnerDone = 1
                dicoStat[key].nbrDinner += 1
                
        if bDay and not dicoHelper[strCity].bStatWetDayDone:
            if bRainOrSnow:
                dicoHelper[strCity].bStatWetDayDone = 1
                dicoStat[key].nbrWetDay += 1

        if bNight and not dicoHelper[strCity].bStatWetNightDone:
            if bRainOrSnow:
                dicoHelper[strCity].bStatWetNightDone = 1
                dicoStat[key].nbrWetNight += 1
                

            
        nNumLine += 1

        if nNumLine >= 2000 and 0:
            break
    
    occCity.printRes()
    occWeather.printRes()

    # compute score
    for k,v in dicoStat.items():
        b = 0
        m = 0
        b = v.nbrBreakfast + v.nbrLunch + v.nbrDinner
        m += v.nbrHotDay + v.nbrHotNight + v.nbrColdNight
        m += v.nbrWetDay + v.nbrWetNight
        
        dicoStat[k].score = b-m
        dicoStat[k].score_bonus = b
        dicoStat[k].score_malus = m
    
        
    
    scorePerCity = {} # score, bonus, malus
    scorePerMonth = {} # (ville, score)
    
    for k,v in dicoStat.items():
        strCity = k.split("__")[0]
        strMonth = k.split("__")[1]
        if strCity not in scorePerCity:
            scorePerCity[strCity] = [0,0,0]
        scorePerCity[strCity][0] += dicoStat[k].score
        scorePerCity[strCity][1] += dicoStat[k].score_bonus
        scorePerCity[strCity][2] += dicoStat[k].score_malus
        if strMonth not in scorePerMonth:
            scorePerMonth[strMonth] = []
        scorePerMonth[strMonth].append( (strCity,dicoStat[k].score) )
    
    for k,v in dicoStat.items():
        print("%s:\n%s" % (k,str(v)))
        
    print("palmares par mois:")
    for k,v in sorted(scorePerMonth.items()):
        v = sorted(v,key=lambda a:a[1], reverse=True)
        print("%s:\n%s" % (k,str(v)))
    
        
    print("start: %s" % strStartDate)
    print("stop: %s" % strStopDate)
    print("")
        
    for k,v in sorted(scorePerCity.items(),key=lambda a:a[1][0], reverse=True):
        print("%s:\n%s" % (k,str(v)))
    
    f.close()
    
    return dict_out
    
# analyse - end
        
        
"""
start: 2022/12/06
stop: 2023/08/14

Las Palmas:
[379, 455, 76]
Tavira:
[151, 368, 217]
Bonifacio:
[79, 251, 172]
VN Gaia:
[52, 267, 215]
Catanzaro:
[41, 234, 193]
Beziers:
[-52, 282, 334]
Bordeaux:
[-70, 255, 325]
Biarritz:
[-82, 251, 333]
Vacheres:
[-143, 193, 336]
Le Kremlin-Bicetre:
[-180, 183, 363]
Paris:
[-190, 182, 372]
Annecy:
[-206, 205, 411]
Bort-les-Orgues:
[-239, 169, 408]
Saint-bonnet-pret-bort:
[-282, 140, 422]
St Malo:
[-283, 101, 384]
"""
    
# a faire: par equipe de 2: quel est la meilleur combinaison par mois
    
    
    
if __name__ == "__main__":
    strFilename = "data/temperature.txt"
    datas = analyse(strFilename)
    if 1:
        print("")
        print("render_all_datas bloc begin")
        import temperature_office_analyse
        temperature_office_analyse.render_all_datas(datas)