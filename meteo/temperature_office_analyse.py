# analyse temperature file (from real sonde dans la piece)
# elles sont sur REE, le serveur est a l'heure en hiver.

# scp -P 11022 na@thenardier.fr:/home/na/save/office_temperature.txt C:/Users/alexa/dev/git/electronoos/meteo/data/

import sys

sys.path.append("../../obo/spider/")

import common
import retrieve_pop3
import datetime

        
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
    prevTemp = 0
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
        if bVerbose or nNumLine==0: print("DBG: integered: %d/%02d/%02d: %02dh%02d: temp: %5.2f" % (nYear, nMonth, nDay, nHour,nMin,rTemp))
        
        nNumLine += 1
        #~ if nNumLine > 100:
            #~ break
            
            
        # remove abberations
        if rTemp < 1:
            continue
            
        if 0:
            # average on two values
            rTemp = (prevTemp + rTemp)/2
            prevTemp = rTemp
        allDatas.append([nYear, nMonth, nDay, nHour,nMin,rTemp])
    
    f.close()
    
    
    return allDatas
    
# analyse - end


def draw_point(list_x,list_y):
    import matplotlib.pyplot as plt
    plt.plot(list_x,list_y)
    plt.ylabel('temperature')
    plt.show()
    
def draw_point_series(dictPerDay, bRender=True):
    import matplotlib.pyplot as plt
    
    for k in dictPerDay:
        my_label = k.replace("2024/","" ).replace("2023/","" )
        # invert day et month
        my_label = my_label[:-5] + my_label[-2:] + "/" + my_label[-5:-3]
        plt.plot(dictPerDay[k][0],dictPerDay[k][1],label = my_label)
        if 1:
            # local min & max
            for extremum,offset in [(min,-0.4),(max,+0.1)]:
                idx = dictPerDay[k][1].index(extremum(dictPerDay[k][1]))
                strLabelMin = my_label + '\n' + str(int(dictPerDay[k][0][idx])) + 'h' + "%02d: "%((dictPerDay[k][0][idx]%1)*60) + "%.1f"%   (dictPerDay[k][1][idx]) + '' 
                # plt.annotate('local max', xy=(2, 1), xytext=(3, 1.5), arrowprops=dict(facecolor='black', shrink=0.05),)
                plt.annotate( strLabelMin, xy=(dictPerDay[k][0][idx]-0.5, dictPerDay[k][1][idx]+offset))
                
    first_year = list(dictPerDay.keys())[0].split(":")[1].strip()[:4]
    first_month = list(dictPerDay.keys())[0].split(":")[1].strip()[5:7]
    print(first_month)
    plt.ylabel('Temperature' + ' ' + first_year)
    plt.legend()
    plt.locator_params(axis='both', nbins=24) 
    plt.tight_layout(pad=0) # fonctionne pas sur le premier?
    plt.gcf().set_size_inches(32, 18) # pour le rendu dans le fichier
    fn = 'output/month_'+first_year+'_'+first_month+".jpg"
    print("INF: draw_point_series: writing to '%s'" % fn )
    plt.savefig(fn, dpi=100)
    if bRender: plt.show()
    plt.clf()
    plt.cla()


def analyse_sonde_temp( datas, nYearMin, nMonthMin, nYearMax = 2094, nMonthMax = 13, bRender=True ):
    """
    Analyse data after nYearMin/nMonthMin (included)
    and before nYearMax/nMonthMax (included)
    """
    
    dictPerDay = {}
    xs = []
    ys = []
    for d in datas:
        nYear, nMonth, nDay, nHour,nMin,rTemp = d
        if nYear < nYearMin or ( nYear == nYearMin and nMonth < nMonthMin):
            continue
        if nYear > nYearMax or ( nYear == nYearMax and nMonth > nMonthMax):
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
    if len(dictPerDay) > 0:
        draw_point_series(dictPerDay, bRender=bRender)
        
        
        
"""
"""

    
    
    
strFilename = "data/office_temperature.txt"
datas = decode_file_sonde(strFilename)
if 1:
    for d in datas[-40:]:
        print(d)

datas = datas[-24*12*7:] # a peu pres la derniere semaine

analyse_sonde_temp(datas, 2024,12)
#~ analyse_sonde_temp(datas, 2024,11,2024,11)
#~ analyse_sonde_temp(datas, 2024,7,2024,7)
#~ analyse_sonde_temp(datas, 2024,8,2024,8)
#~ analyse_sonde_temp(datas, 2023,12,2023,12)
#~ analyse_sonde_temp(datas, 2023,2,2023,2)

if 0:
    # sort toutes les stats par mois
    for y in [2023,2024]:
        for m in range(1,13):
            analyse_sonde_temp(datas,y,m,y,m,bRender=False)
        