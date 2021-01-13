#~ import panda as pd # pip install panda ; pip install requests # python3-requests

import gzip

def getNbrHourWind( strFile, rThresholdMeterSecond ):
    """
    return a ratio of enough wind/total
    """
    #~ print("INF: getNbrHourWind %s" % strFile )
    #~ df = pd.read_csv(strFile, compression='gzip', header=0, sep=' ', quotechar='"', error_bad_lines=False)
    file = gzip.open(strFile, mode='rb', compresslevel=9, encoding=None, errors=None, newline=None)
    #~ print("INF: getNbrHourWind: loaded..." )
    lines = file.readlines()
    nCptLine = 0
    nIdxWindspeed = 6
    nCount = 0
    nCountTotal = 0
    for l in lines:
        #~ print("nCptLine: %d/%d" % (nCptLine,len(lines)) )
        l = str(l)
        #~ print(l) 
        data = l.split(';')
        #~ print(data)
        rWindSpeed = data[nIdxWindspeed]
        if rWindSpeed == 'mq' or rWindSpeed == 'ff' :
            continue
        rWindSpeed = float(data[nIdxWindspeed]) # en noeud
        rWindSpeed *= 0.514444 # in m/s
        #~ print("rWindSpeed: %f" % rWindSpeed )
        if rWindSpeed >= rThresholdMeterSecond:
            nCount += 1
        nCountTotal += 1
            
            
        nCptLine += 1
        #~ if nCptLine > 5:
            #~ break
    #~ print("INF: getNbrHourWind: analysed..." )
    return nCount/nCountTotal
    
# getNbrHourWind - end
rThresholdMeterSecond = 12
print("rThresholdMeterSecond: %d m/s" % rThresholdMeterSecond )
for m in range(1,13):
    strName = "C:/Users/amazel/perso/docs/creativeV/meteodata/synop.2020%02d.csv.gz" % m
    rRatio = getNbrHourWind(strName, rThresholdMeterSecond = rThresholdMeterSecond)
    print("Month %2s: %5.1f min/day" % (m, rRatio*24*60) )