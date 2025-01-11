# analyse temperature file (from real sonde dans la piece)
# elles sont sur REE, le serveur est a l'heure en hiver.

# to retrieve data sent from rpi sonde
# scp -P 11022 na@thenardier.fr:/home/na/save/office_temperature.txt C:/Users/alexa/dev/git/electronoos/meteo/data/

# to retrieve data sent from logged data from various IOT device
# scp -P 50022 na@thenardier.fr:/var/www/save/webdata.txt  C:/Users/alexa/dev/git/electronoos/meteo/data/


import sys

sys.path.append("../../obo/spider/")

import common
import misctools
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
    """
    return a list of dictionnary of values, eg: ("location","name of datas") => list of values = [year,month,day,hour, min, value]
    """
    
    bVerbose = 1
    bVerbose = 0
    
    f = open(strFilename,"rb")

    nNumLine = 0
    
    allDatas = {}
    
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
            
        # office sonde line format: 2023/02/13: 15h54m10s: armoire: 22.375
        # websave line format: 1735662269.80: MisBKit3: humid: 78.73
        
        # duplicates in websave compared to office sonde: 1735662309.73: robot-enhanced-education.org: temp: 19.0
        
        if b"/" in datas[0]:
            # office sonde format
            strDate, strTime, strLocation, strValue = datas[:4]
            
            if bVerbose: print("strDate: '%s'" % strDate)
            if bVerbose: print("strTime: '%s'" % strTime)
            if bVerbose: print("strLocation: '%s'" % strLocation)
            if bVerbose: print("strValue: '%s'" % strValue)
            
            strDate = strDate.decode()
            strTime = strTime.decode()
            strHost  = "rpi"  # for back compat
            strMesureName = "Temperature" # for back compat
            strLocation = strLocation.decode()
            datas_key = (strLocation, "temp")
        else:
            # web save
            strEpoch, strHost, strMesureName, strValue = datas[:4]
            
            if bVerbose: print("strEpoch: '%s'" % strEpoch)
            if bVerbose: print("strHost: '%s'" % strHost)
            if bVerbose: print("strMesureName: '%s'" % strMesureName)
            if bVerbose: print("strValue: '%s'" % strValue)
            
            strEpoch = strEpoch.decode()
            strHost = strHost.decode()
            strMesureName = strMesureName.decode()
            strValue = strValue.decode()
            strValue = strValue.replace("%22", "" ) # at once I've sent  &v="421"  instead of  &v=421
            
            strDateTime = common.epochToTimeStamp(float(strEpoch))
            if bVerbose: print("strDateTime: '%s'" % strDateTime)
            strDate,strTime = strDateTime.split(':')
            strTime = strTime.strip()
            
            datas_key = (strHost, strMesureName)
            

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
        rValue = float(strValue)
        if bVerbose or nNumLine==0: print("DBG: integered: %d/%02d/%02d: %02dh%02d: value: %5.2f" % (nYear, nMonth, nDay, nHour,nMin,rValue))
        
        nNumLine += 1
        #~ if nNumLine > 100:
            #~ break
            
            
        # remove abberations
        if rValue < 1 or rValue > 50000: # max is VOC 1...50000
            continue
            
        # remove test
        if "test" in strMesureName.lower() or "misbb" in strHost.lower():
            continue
            
        if 0:
            # average on two values (works only on sonde) (else we'll need many prevValues)
            rValue = (prevTemp + rValue)/2
            prevTemp = rValue
            
        if datas_key not in allDatas: allDatas[datas_key] = []
        allDatas[datas_key].append([nYear, nMonth, nDay, nHour,nMin,rValue])
    
    f.close()
    
    
    return allDatas
    
# analyse - end


def draw_point(list_x,list_y):
    import matplotlib.pyplot as plt
    plt.plot(list_x,list_y)
    plt.ylabel('temperature')
    plt.show()
    
def draw_temp_series(dictPerDay, bRender=True, bCloseAtEnd = True, strTitle = None ):
    """
    Receive a dict of curvename => [x],[y] render all curves on the same graph
    """
    import matplotlib.pyplot as plt
    
    strTitleGenerated = ""
    
    listBestLabelX = [] # the goal is to take the labels of the curve going from the widest range
    
    for k in dictPerDay:
        if k.count('/') > 2: # it's a date
            my_label = k.replace("2024/","" ).replace("2023/","" ).replace("2022/","" )
            # invert day et month
            my_label = my_label[:-5] + my_label[-2:] + "/" + my_label[-5:-3]
        else:
            my_label = str(k)
            if len(strTitleGenerated) > 0:
                strTitleGenerated += ", "
            strTitleGenerated += my_label
            
        if 1:
            # change x labels
            labelx_pos = []
            labelx_txt = []
            #~ labelx_txt: list[str] = [f'Val{v:0.2f}' for v in dictPerDay[k][0]]
            prevxval = - 100
            for xval in dictPerDay[k][0]:
                if int(xval) > prevxval:
                    prevxval = xval
                    pos = int(xval)
                    txt = str(int(xval)% 24)
                    labelx_pos.append(pos)
                    labelx_txt.append(txt)
                #~ else:
                    #~ labelx_pos.append(xval)
                    #~ labelx_txt.append("")
            if len(listBestLabelX) < len(labelx_pos):
                listBestLabelX = labelx_pos
                plt.xticks(labelx_pos, labelx_txt)
            
        plt.plot(dictPerDay[k][0],dictPerDay[k][1],label = my_label)

        if 1:
            # local min & max
            for extremum,offset in [(min,-0.4),(max,+0.1)]:
                idx = dictPerDay[k][1].index(extremum(dictPerDay[k][1]))
                # x is hour with decimal since start or hour in absolute
                nNumJour = int(dictPerDay[k][0][idx]/24)
                rHour = dictPerDay[k][0][idx] - ( nNumJour * 24 )
                nMin = int(rHour * 60) % 60
                nHour = int(rHour)
                nNumJour += 1
                strMoment = ""
                if nNumJour > 1:
                    strMoment = "Jour %d " % nNumJour
                strMoment += "%dh%02d: " % ( nHour, nMin)                
                try:
                    strLabelToDraw = my_label + '\n' + strMoment + "%.1f" % (dictPerDay[k][1][idx])
                except ValueError as err:
                    # value name is not a date
                    # usefull code part ? working ?
                    strLabelToDraw = "Jour %d, Hour: %dh%02d: %.1f" % (nNumJour,nHour,nMin, dictPerDay[k][1][idx])
                # plt.annotate('local max', xy=(2, 1), xytext=(3, 1.5), arrowprops=dict(facecolor='black', shrink=0.05),)
                print(dictPerDay[k][0][idx])
                plt.annotate( strLabelToDraw, xy=(dictPerDay[k][0][idx]-0.5, dictPerDay[k][1][idx]+offset))
                
    try:
        first_year = list(dictPerDay.keys())[0].split(":")[1].strip()[:4]
        first_month = list(dictPerDay.keys())[0].split(":")[1].strip()[5:7]
        filenamepostfix = "month_" + first_year + '_' + first_month
        print(first_month)
    except (IndexError,AttributeError) as err:
        # keys are not year and month
        strTitle = strTitleGenerated
        filenamepostfix = "series" # title is already in prefix
    
    if strTitle == None:
        strTitle = 'Temperature' + ' ' + first_year
        strPrefix = "temp"
    else:
        strPrefix = strTitle.replace("(","").replace(")","").replace(",","_").replace(" ", "").replace("'", "").replace("-", "").replace(".", "").lower()
    plt.ylabel(strTitle)
    plt.legend()
    plt.locator_params(axis='both', nbins=24) 
    plt.tight_layout(pad=0) # fonctionne pas sur le premier?
    plt.gcf().set_size_inches(32, 18) # pour le rendu dans le fichier
    fn = ('output/%s_'% strPrefix) +filenamepostfix+".jpg"
    print("INF: draw_temp_series: writing to '%s'" % fn )
    plt.savefig(fn, dpi=100)
    if bRender: plt.show()
    
    if bCloseAtEnd:
        plt.clf()
        plt.cla()


def analyse_sonde_temp( alldatas, nYearMin, nMonthMin, nYearMax = 2094, nMonthMax = 13, bRender=True ):
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
        draw_temp_series(dictPerDay, bRender=bRender)
        
        
        
def render_all_datas( alldatas, nYearMin = 2024, nMonthMin = 1, nDayMin = 1, nYearMax = 2094, nMonthMax = 13, nDayMax = 32, sameGraphList = [], bRender=True ):
    """
    for each datas, for each week we want all days in one graph. (nXxxMin and nXxxMax are included)
    if sameGraphList != []: will render datas listed on only one graph for the whole period nYearMin, nMonthMin, nDayMin to nYearMax, nMonthMax, nDayMax.
        eg: [("MisBKit3","temp"),("MisBKit3","humid")])
    """
    import matplotlib.pyplot as plt
    
    dictPerDay = {}
    xs = []
    ys = []
    
    nInitMin = misctools.convertYmdHmsToEpoch( nYearMin, nMonthMin, nDayMin )//60
    
    bAllOnSameGraph = sameGraphList != []
    for key, datas in alldatas.items():
        print(key)
        
        if sameGraphList == []  and not ("MisB" in key[0] or "Kremlin" in key[0]): # un peu temp
            continue

        if sameGraphList != [] and not key in sameGraphList:
            continue
            
        for d in datas:
            try:
                nYear, nMonth, nDay, nHour,nMin,rValue = d
            except ValueError:
                print( "ERR: render_all_datas: Value error on key: %s, d:%s" % (key,d) )
                assert(0)

            if nYear < nYearMin or ( nYear == nYearMin and nMonth < nMonthMin) or ( nYear == nYearMin and nMonth == nMonthMin and nDay < nDayMin):
                continue
            if nYear > nYearMax or ( nYear == nYearMax and nMonth > nMonthMax) or ( nYear == nYearMax and nMonth == nMonthMax and nDay > nDayMax ):
                continue
            print("INF: render_all_datas: key: %s, %d/%02d/%02d: %02dh%02d: value: %5.2f" % (str(key),nYear, nMonth, nDay, nHour,nMin,rValue))
            xs.append(nHour+nMin/60)
            ys.append(rValue)
            
            my_date = datetime.datetime(nYear, nMonth, nDay) 
            dayname = my_date.strftime("%A")

            if not bAllOnSameGraph:
                k = "%s: %d/%02d/%02d" % (dayname, nYear, nMonth, nDay)
                if not k in dictPerDay:
                    dictPerDay[k] = ([],[])
                dictPerDay[k][0].append(nHour+nMin/60)
                dictPerDay[k][1].append(rValue)
            else:
                k = key
                if not k in dictPerDay:
                    dictPerDay[k] = ([],[])
                nTimeHour = (misctools.convertYmdHmsToEpoch( nYear, nMonth, nDay, nHour,nMin )//60 - nInitMin)/60.
                dictPerDay[k][0].append(nTimeHour)
                dictPerDay[k][1].append(rValue)
                
                
            
        #~ for k in dictPerDay:
        #~ import matplotlib.pyplot as plt
        #~ plt.plot(xs,ys)
        #~ plt.ylabel( str(key) )
        #~ plt.show()
        if len(dictPerDay) > 0 and not bAllOnSameGraph:
            draw_temp_series(dictPerDay, bRender=bRender, strTitle = str(key))
            dictPerDay = {}
            
    if bAllOnSameGraph:
        draw_temp_series(dictPerDay, bRender=bRender, strTitle = str(key))

    
    
if __name__ == "__main__":
        
    strFilename = "data/office_temperature.txt"
    strFilename = "data/webdata.txt"
    datas = decode_file_sonde(strFilename)

    if 1:
        # draw some datas:
        #~ print(datas.keys())
        print("Last datas of each type:")
        for k, v in datas.items():
            print("key: %s" % str(k) )
            for d in v[-40:]:
                print(d)
                
    if 0:
        # just render temperature
                
        key = list(datas.keys())[0]
        
        print("Rendering data for %s" % str(key) )
        datas = datas[key] # render first type

        datas = datas[-24*12*7:] # a peu pres la derniere semaine

        analyse_sonde_temp(datas, 2025,1)
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
                    
    else:
        # render multi variable
        render_all_datas(datas,2025,1)
            