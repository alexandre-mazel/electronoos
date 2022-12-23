# -*- coding: cp1252 -*-


import io
import os
import random
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
        dest = os.path.expanduser("~/save/temperature.txt")
    
    f = open(dest,"a")
    f.write("%s: %s: %s: %s\n" % (timestamp,city,temp,cond) )
    f.close()

# from https://weather.com
def retrieveTemp():
    startbase = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--MHmYY">'
    stopbase = "°</span>"
    # beau: soleil avec des nuages, ensolleile: plein soleil
    astrDatas = [
            ["Paris", "https://weather.com/fr-FR/temps/aujour/l/48.86,2.35?par=google",startbase,stopbase],
            ["Le Kremlin-Bicetre", "https://weather.com/fr-FR/temps/aujour/l/ccb7b6dc48e255339753562e6a8ea1b48b796d68cc275ef58b3d8fe4c9b75fa7",startbase,stopbase],
            ["Beziers", "https://weather.com/fr-FR/temps/aujour/l/48dfaf8b4db3509a7e858c54a0ec35164fa8baccc73b35f6b9e0cd04b7544ea5",startbase,stopbase],
            ["Bort-les-Orgues", "https://weather.com/fr-FR/temps/aujour/l/14e53d3cef725e41222474317acf1d27951992d718300074c36ded62883afdd5",startbase,stopbase],
            ["Saint-bonnet-pret-bort", "https://weather.com/fr-FR/temps/aujour/l/356a10c392837b0bd6f3e7ddd33acb4d385701ddf07ebae91c8ed2fa8b7c803c",startbase,stopbase],
            ["Annecy", "https://weather.com/fr-FR/temps/aujour/l/dca69ee3f92301838c6a8f09e67796bf14fe8684fb90ed81dc4cbfb732668169",startbase,stopbase],
            ["Biarritz", "https://weather.com/fr-FR/temps/aujour/l/ad456d1b2d0a43d1e8940f2f0f6956ff227ebe4f5faf3f0af67e22f17242a9a2",startbase,stopbase],
            ["Vacheres", "https://weather.com/fr-FR/temps/aujour/l/0e75f3a11bcabc16a92fe0d2e9924db5630544cf77e2aa76c11cfe7069313825",startbase,stopbase],
            ["St Malo", "https://weather.com/fr-FR/temps/aujour/l/a1baaf192d861ad1bed879b83a55048b51283588728dfbcf6dc28281d5ce8f4f",startbase,stopbase],
            ["Bordeaux", "https://weather.com/fr-FR/temps/aujour/l/12fae739549c2bb1e6693bdb14c062671c7c87d40051273a05a4eaf5848064fe",startbase,stopbase],
            ["Tavira", "https://weather.com/fr-FR/temps/aujour/l/efa3db97660e2aaaa3efc076350dd00386e0453da1547361cd68e78a412f2fb8",startbase,stopbase],
            ["VN Gaia", "https://weather.com/fr-FR/temps/aujour/l/7291c492bc9efb63e5a06ee49112469d08890e36e59bc3df64648f4c681440d5",startbase,stopbase],
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
        time.sleep(random.random()*10)
        time.sleep(8)
        #~ break
            
# retrieveTemp - end

def loop(nTimeLoopMin=14):
    while 1:
        retrieveTemp()
        print("sleeping %d min..." % nTimeLoopMin)
        time.sleep(nTimeLoopMin*60)
        #~ use misctools.isQuarterHour ?

#~ retrieveTemp()
loop()

