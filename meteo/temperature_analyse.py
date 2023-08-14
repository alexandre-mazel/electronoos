# analyse temperature file

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
        
        self.strPrevDay = ""
        
        self.bLastStatWasBreakfast = False # helper to know if we analyse the last measure as a breakfast
        
        self.bLastStatWasLunch = False
        
        self.bLastStatWasDinner = False

class Stat:
    def __init__( self ):
        self.min = 999
        self.max = -40
        
        self.nbrBreakfast = 0 # nbr breakfast  at 8.30 > 15 and no rain breakfast
        
        self.nbrLunch = 0 # nbr lunch at 13 > 20
        
        self.nbrDinner = 0 # nbr dinner at 19.30 > 20
        
        self.nbrHotNight = 0 # nbr min night >= 20
        self.nbrColdNight = 0 # nbr min night < 13
        self.nbrWetNight = 0 # night with more than 15min of rain
        
    def __str__(self):
        o  = ""
        #~ o += " min: %s, max: %s, hotnight: %s" % (self.min,self.max,self.nbrHotNight)
        o += "  min: %s\n" % self.min
        o += "  max: %s\n" % self.max
        o += "  cold night: %s\n" % self.nbrColdNight
        o += "  hot night: %s\n" % self.nbrHotNight
        return o

def analyse(strFilename):
    bVerbose = 0
    
    f = open(strFilename,"rb")
    occCity = common.OccCounter()
    
    dicoHelper = {} # city => HelperStat
    
    dicoStat = {} # dico per city and month => stat

    
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
        strCity = strCity.decode()
        strMonth = strDate.decode()[5:7]
        strHour = strTime.decode()[0:2]
        nHour = int(strHour)
        if bVerbose: print("nHour: %s" % nHour)
        
        nTemp = int(strTemp)
        
        bNight = nHour >= 22 or nHour <= 7
        
        if bVerbose: print("bNight: %s" % bNight)
            
        bNewDay = 0 # new matinee
        
        key = strCity + "__" + strMonth

        if strCity not in dicoHelper:
            if bVerbose: print("create new helper was not")
            dicoHelper[strCity] = HelperStat()
                
        if nHour >= 8 and dicoHelper[strCity].strPrevDay != strDate:
            if bVerbose: print("new day")
            bNewDay = 1
            

            dicoHelper[strCity].strPrevDay = strDate
            
            # update stat of the night (warning we can start with a hour at 22, and so updating previous night)

            if strCity in dicoHelper and dicoHelper[strCity].minNight < 999:
                if bVerbose: print("minnight: %s" % dicoHelper[strCity].minNight)
                if  dicoHelper[strCity].minNight >= 20:
                    dicoStat[key].nbrHotNight += 1
                if dicoHelper[strCity].minNight < 13:
                    dicoStat[key].nbrColdNight += 1            
            
        
        
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
            
                
        if bNight:
            if bVerbose: print("min night: %s" % dicoHelper[strCity].minNight)
            if dicoHelper[strCity].minNight > nTemp:
                dicoHelper[strCity].minNight = nTemp
            
            
        if dicoStat[key].min > nTemp:
           dicoStat[key].min = nTemp

        if dicoStat[key].max < nTemp:
           dicoStat[key].max = nTemp

            
        nNumLine += 1

        if nNumLine >= 2000 and 0:
            break
    
    occCity.printRes()
    for k,v in dicoStat.items():
        print("%s:\n%s" % (k,str(v)))
    
    f.close()
    
# analyse - end
        
        
    
    
    
    
    
    
strFilename = "data/temperature.txt"
analyse(strFilename)