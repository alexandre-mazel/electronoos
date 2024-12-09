# analyse temperature file (from real sonde dans la piece)
# elles sont sur REE

# scp -P 11022 na@thenardier.fr:/home/na/save/office_temperature.txt C:/Users/alexa/dev/git/electronoos/meteo/data/

import sys

sys.path.append("../../obo/spider/")

import common
import retrieve_pop3
import datetime

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

def decode_file_sonde(strFilename):
    bVerbose = 1
    bVerbose = 0
    
    f = open(strFilename,"rb")
    occCity = common.OccCounter()
    occWeather = common.OccCounter()
    
    dicoHelper = {} # city => HelperStat
    
    dicoStat = {} # dico per city and month => stat
    
    strStartDate = ""
    strStopDate = ""

    
    nNumLine = 0
    
    allDatas = []
    while 1:
        line = f.readline()
        if bVerbose: print(line)
        if len(line)<2:
            break
        datas = retrieve_pop3.splitBytes(line,ord(":"))
        
        if bVerbose: print(datas)
        
        for i in range(len(datas)):
            datas[i] = datas[i].strip()
        
        strDate, strTime, strCity, strTemp = datas[:4]
        
        if bVerbose: print("strDate: '%s'" % strDate)
        if bVerbose: print("strTime: '%s'" % strTime)
        if bVerbose: print("strCity: '%s'" % strCity)
        if bVerbose: print("strTemp: '%s'" % strTemp)
        
        strDate = strDate.decode()
        strTime = strTime.decode()
        strCity = strCity.decode()
        strYear = strDate[0:4]
        strMonth = strDate[5:7]
        strDay = strDate[8:10]
        strHour = strTime[0:2]
        strMin = strTime[3:5]

        if bVerbose: print("DBG: decoded: %s/%02s/%02s: %sh%s" % (strYear, strMonth, strDay, strHour,strMin))
        
        nYear = int(strYear)
        nMonth = int(strMonth)
        nDay = int(strDay)
        nHour = int(strHour)
        nMin = int(strMin)
        rTemp = float(strTemp)
        if bVerbose: print("DBG: integered: %d/%02d/%02d: %02dh%02d: temp: %5.2f" % (nYear, nMonth, nDay, nHour,nMin,rTemp))
        
        nNumLine += 1
        #~ if nNumLine > 100:
            #~ break
            
            
        allDatas.append([nYear, nMonth, nDay, nHour,nMin,rTemp])
    
    f.close()
    
    
    return allDatas
    
# analyse - end


def draw_point(list_x,list_y):
    import matplotlib.pyplot as plt
    plt.plot(list_x,list_y)
    plt.ylabel('temperature')
    plt.show()
    
def draw_point_series(dictPerDay):
    import matplotlib.pyplot as plt
    
    for k in dictPerDay:
        my_label = k.replace("2024/","" ) 
        plt.plot(dictPerDay[k][0],dictPerDay[k][1],label = my_label)
        if 1:
            # local min & max
            for extremum,offset in [(min,-0.4),(max,+0.1)]:
                idx = dictPerDay[k][1].index(extremum(dictPerDay[k][1]))
                strLabelMin = my_label + '\n' + str(int(dictPerDay[k][0][idx])) + 'h' + "%02d: "%((dictPerDay[k][0][idx]%1)*60) + str(dictPerDay[k][1][idx]) + '' 
                # plt.annotate('local max', xy=(2, 1), xytext=(3, 1.5), arrowprops=dict(facecolor='black', shrink=0.05),)
                plt.annotate( strLabelMin, xy=(dictPerDay[k][0][idx]-0.5, dictPerDay[k][1][idx]+offset))
    plt.ylabel('temperature')
    plt.legend()
    plt.locator_params(axis='both', nbins=24) 
    plt.show()


def analyse_sonde_temp( datas, nYearMin, nMonthMin ):
    """
    Analyse data after nYearMin/nMonthMin (included)
    """
    
    dictPerDay = {}
    xs = []
    ys = []
    for d in datas:
        nYear, nMonth, nDay, nHour,nMin,rTemp = d
        if nYear < nYearMin or ( nYear == nYearMin and nMonth < nMonthMin):
            continue
        #~ print("INF: analyse_sonde_temp: %d/%02d/%02d: %02dh%02d: temp: %5.2f" % (nYear, nMonth, nDay, nHour,nMin,rTemp))
        xs.append(nHour+nMin/60)
        ys.append(rTemp)
        
        my_date = datetime.datetime(nYear, nMonth, nDay) 
        dayname = my_date.strftime("%A")

        k = "%s: %d/%02d/%02d" % (dayname, nYear, nMonth, nDay)
        if not k in dictPerDay:
            dictPerDay[k] = ([],[])
        dictPerDay[k][0].append(nHour+nMin/60)
        dictPerDay[k][1].append(rTemp)
        
    #~ draw_point(xs,ys)
    draw_point_series(dictPerDay)
        
        
        
"""
start: 2022/12/06
stop: 2023/08/14

"""
    
# a faire: par equipe de 2: quel est la meilleur combinaison par mois
    
    
    
    
strFilename = "data/office_temperature.txt"
datas = decode_file_sonde(strFilename)
analyse_sonde_temp(datas, 2024,12)