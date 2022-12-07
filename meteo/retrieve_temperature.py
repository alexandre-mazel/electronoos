# -*- coding: cp1252 -*-

import io
import os
import sys
import time

sys.path.append("../alex_pytools/")
import misctools
import nettools
import stringtools

def store(city,temp,cond):
    timestamp = misctools.getTimeStamp()
    if os.name == "nt":
        dest = "c:/save/temperature.txt"
    else:
        dest = "/home/pi/save/temperature.txt"
    
    f = open(dest,"a")
    f.write("%s: %s: %s: %s\n" % (timestamp,city,temp,cond) )
    f.close()

# from https://weather.com
def retrieveTemp():
    startbase = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--MHmYY">'
    stopbase = "°</span>"
    astrDatas = [
            ["Paris", "https://weather.com/fr-FR/temps/aujour/l/48.86,2.35?par=google",startbase,stopbase],
            ["Beziers", "https://weather.com/fr-FR/temps/aujour/l/48dfaf8b4db3509a7e858c54a0ec35164fa8baccc73b35f6b9e0cd04b7544ea5",startbase,stopbase],
            ["Bort-les-Orgues", "https://weather.com/fr-FR/temps/aujour/l/14e53d3cef725e41222474317acf1d27951992d718300074c36ded62883afdd5",startbase,stopbase],
            ["Annecy", "https://weather.com/fr-FR/temps/aujour/l/dca69ee3f92301838c6a8f09e67796bf14fe8684fb90ed81dc4cbfb732668169",startbase,stopbase],
    ]
    
    start_cond = '<div data-testid="wxPhrase" class="CurrentConditions--phraseValue--mZC_p">'
    stop_cond = '</div><div class="CurrentConditions--tempHiLoValue--3T1DG">'
    
    for city,link,txt_start,txt_end in astrDatas:
        dst = "/tmp/meteo_temp.html"
        nettools.download(link,dst,bForceDownload=1)
        f = io.open(dst,"r",encoding='utf-8')
        buf = f.read()
        f.close()
        temp = stringtools.findSubString(buf,txt_start,txt_end)
        cond = stringtools.findSubString(buf,start_cond,stop_cond)
        # beau: soleil avec un peu de nuage
        # ensoleillé: plein soleil
        print("DBG: retrieveTemp: %s: temp: '%s' cond: '%s'" % (city,temp,cond) )
        if len(temp) < 3:
            temp = int(temp)
            cond = cond.replace("é","e")
            store(city,temp,cond)
        #~ break
            
# retrieveTemp - end

def loop(nTimeLoopMin=15):
    while 1:
        retrieveTemp()
        print("sleeping %d min..." % nTimeLoopMin)
        time.sleep(nTimeLoopMin*60)
        #~ use misctools.isQuarterHour ?

#~ retrieveTemp()
loop()

